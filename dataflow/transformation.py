"""
Transformation engine and job/operator system for DataFlow
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, when, lit, sum as spark_sum, avg as spark_avg, count as spark_count

from .dataset import DatasetDefinition, DatasetRegistry


class TransformationStatus(Enum):
    """Status of a transformation job"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TransformationType(Enum):
    """Type of transformation"""
    FILTER = "filter"
    SELECT = "select"
    GROUP_BY = "group_by"
    JOIN = "join"
    AGGREGATE = "aggregate"
    SORT = "sort"
    ADD_COLUMN = "add_column"
    CUSTOM = "custom"


@dataclass
class TransformationStep:
    """A single step in a transformation pipeline"""
    step_id: str
    name: str
    description: str
    transformation_type: TransformationType
    natural_language_query: str
    sql_query: Optional[str] = None
    pyspark_code: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    input_datasets: List[str] = field(default_factory=list)
    output_dataset: Optional[str] = None


@dataclass
class TransformationJob:
    """A complete transformation job"""
    job_id: str
    name: str
    description: Optional[str] = None
    steps: List[TransformationStep] = field(default_factory=list)
    status: TransformationStatus = TransformationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result_datasets: Dict[str, str] = field(default_factory=dict)  # dataset_name -> file_path
    
    def add_step(self, step: TransformationStep) -> None:
        """Add a transformation step to the job"""
        self.steps.append(step)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'job_id': self.job_id,
            'name': self.name,
            'description': self.description,
            'steps': [
                {
                    'step_id': step.step_id,
                    'name': step.name,
                    'description': step.description,
                    'transformation_type': step.transformation_type.value,
                    'natural_language_query': step.natural_language_query,
                    'sql_query': step.sql_query,
                    'pyspark_code': step.pyspark_code,
                    'parameters': step.parameters,
                    'input_datasets': step.input_datasets,
                    'output_dataset': step.output_dataset
                }
                for step in self.steps
            ],
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'result_datasets': self.result_datasets
        }


class NaturalLanguageProcessor:
    """Processes natural language queries and converts them to SQL/PySpark"""
    
    def __init__(self, spark_session: SparkSession):
        self.spark = spark_session
        self.transformation_patterns = self._build_transformation_patterns()
    
    def _build_transformation_patterns(self) -> Dict[str, Callable]:
        """Build pattern matching functions for common transformations"""
        return {
            "filter": self._parse_filter_query,
            "select": self._parse_select_query,
            "group_by": self._parse_group_by_query,
            "join": self._parse_join_query,
            "sort": self._parse_sort_query,
            "add_column": self._parse_add_column_query
        }
    
    def parse_query(self, query: str, input_schema: Dict[str, str]) -> Dict[str, Any]:
        """
        Parse natural language query and return transformation details
        
        Args:
            query: Natural language query
            input_schema: Schema of input dataset (field_name -> field_type)
            
        Returns:
            Dictionary with transformation details
        """
        query_lower = query.lower()
        
        # Determine transformation type and parse accordingly
        if any(word in query_lower for word in ["filter", "where", "remove", "exclude"]):
            return self._parse_filter_query(query, input_schema)
        elif any(word in query_lower for word in ["select", "choose", "pick"]):
            return self._parse_select_query(query, input_schema)
        elif any(word in query_lower for word in ["group", "group by", "aggregate"]):
            return self._parse_group_by_query(query, input_schema)
        elif any(word in query_lower for word in ["join", "merge", "combine"]):
            return self._parse_join_query(query, input_schema)
        elif any(word in query_lower for word in ["sort", "order by", "arrange"]):
            return self._parse_sort_query(query, input_schema)
        elif any(word in query_lower for word in ["add", "create", "new column"]):
            return self._parse_add_column_query(query, input_schema)
        else:
            return self._parse_custom_query(query, input_schema)
    
    def _parse_filter_query(self, query: str, schema: Dict[str, str]) -> Dict[str, Any]:
        """Parse filter/where clause queries"""
        # Simple pattern matching for common filter operations
        conditions = []
        
        # Look for comparison operators
        if "greater than" in query.lower() or ">" in query:
            # Extract field and value
            parts = query.lower().split("greater than")
            if len(parts) == 2:
                field_part = parts[0].strip()
                value_part = parts[1].strip()
                # Find field name in schema
                for field_name in schema.keys():
                    if field_name.lower() in field_part:
                        try:
                            value = float(value_part) if schema[field_name] in ['double', 'integer'] else value_part.strip('"\'')
                            conditions.append(f"{field_name} > {value}")
                        except ValueError:
                            conditions.append(f"{field_name} > '{value_part}'")
                        break
        
        elif "less than" in query.lower() or "<" in query:
            parts = query.lower().split("less than")
            if len(parts) == 2:
                field_part = parts[0].strip()
                value_part = parts[1].strip()
                for field_name in schema.keys():
                    if field_name.lower() in field_part:
                        try:
                            value = float(value_part) if schema[field_name] in ['double', 'integer'] else value_part.strip('"\'')
                            conditions.append(f"{field_name} < {value}")
                        except ValueError:
                            conditions.append(f"{field_name} < '{value_part}'")
                        break
        
        elif "equals" in query.lower() or "=" in query:
            parts = query.lower().split("equals")
            if len(parts) == 2:
                field_part = parts[0].strip()
                value_part = parts[1].strip()
                for field_name in schema.keys():
                    if field_name.lower() in field_part:
                        try:
                            value = float(value_part) if schema[field_name] in ['double', 'integer'] else value_part.strip('"\'')
                            conditions.append(f"{field_name} = {value}")
                        except ValueError:
                            conditions.append(f"{field_name} = '{value_part}'")
                        break
        
        sql_condition = " AND ".join(conditions) if conditions else "1=1"
        
        return {
            "type": "filter",
            "sql_query": f"SELECT * FROM input_table WHERE {sql_condition}",
            "pyspark_code": f"df.filter({sql_condition})",
            "parameters": {"condition": sql_condition}
        }
    
    def _parse_select_query(self, query: str, schema: Dict[str, str]) -> Dict[str, Any]:
        """Parse select/choose column queries"""
        # Extract column names from query
        columns = []
        query_lower = query.lower()
        
        for field_name in schema.keys():
            if field_name.lower() in query_lower:
                columns.append(field_name)
        
        if not columns:
            columns = list(schema.keys())  # Select all if no specific columns mentioned
        
        columns_str = ", ".join(columns)
        
        return {
            "type": "select",
            "sql_query": f"SELECT {columns_str} FROM input_table",
            "pyspark_code": f"df.select({', '.join([f'col(\"{col}\")' for col in columns])})",
            "parameters": {"columns": columns}
        }
    
    def _parse_group_by_query(self, query: str, schema: Dict[str, str]) -> Dict[str, Any]:
        """Parse group by and aggregation queries"""
        group_columns = []
        aggregations = []
        
        query_lower = query.lower()
        
        # Find group by columns
        for field_name in schema.keys():
            if field_name.lower() in query_lower and "group" in query_lower:
                group_columns.append(field_name)
        
        # Find aggregation functions
        if "average" in query_lower or "avg" in query_lower:
            for field_name in schema.keys():
                if field_name.lower() in query_lower and schema[field_name] in ['double', 'integer']:
                    aggregations.append(f"AVG({field_name}) as avg_{field_name}")
        elif "sum" in query_lower:
            for field_name in schema.keys():
                if field_name.lower() in query_lower and schema[field_name] in ['double', 'integer']:
                    aggregations.append(f"SUM({field_name}) as sum_{field_name}")
        elif "count" in query_lower:
            aggregations.append("COUNT(*) as count")
        
        if not group_columns:
            group_columns = list(schema.keys())[:1]  # Use first column as default
        
        if not aggregations:
            aggregations = ["COUNT(*) as count"]  # Default aggregation
        
        group_str = ", ".join(group_columns)
        agg_str = ", ".join(aggregations)
        
        return {
            "type": "group_by",
            "sql_query": f"SELECT {group_str}, {agg_str} FROM input_table GROUP BY {group_str}",
            "pyspark_code": f"df.groupBy({', '.join([f'col(\"{col}\")' for col in group_columns])}).agg({', '.join(aggregations)})",
            "parameters": {"group_columns": group_columns, "aggregations": aggregations}
        }
    
    def _parse_join_query(self, query: str, schema: Dict[str, str]) -> Dict[str, Any]:
        """Parse join queries"""
        # This is a simplified implementation
        return {
            "type": "join",
            "sql_query": "SELECT * FROM input_table1 JOIN input_table2 ON input_table1.id = input_table2.id",
            "pyspark_code": "df1.join(df2, df1.id == df2.id)",
            "parameters": {"join_type": "inner", "join_condition": "id"}
        }
    
    def _parse_sort_query(self, query: str, schema: Dict[str, str]) -> Dict[str, Any]:
        """Parse sort/order by queries"""
        sort_columns = []
        query_lower = query.lower()
        
        # Find sort columns
        for field_name in schema.keys():
            if field_name.lower() in query_lower:
                sort_columns.append(field_name)
        
        if not sort_columns:
            sort_columns = list(schema.keys())[:1]
        
        order = "DESC" if "descending" in query_lower or "desc" in query_lower else "ASC"
        columns_str = ", ".join([f"{col} {order}" for col in sort_columns])
        
        return {
            "type": "sort",
            "sql_query": f"SELECT * FROM input_table ORDER BY {columns_str}",
            "pyspark_code": f"df.orderBy({', '.join([f'col(\"{col}\").{order.lower()}()' for col in sort_columns])})",
            "parameters": {"sort_columns": sort_columns, "order": order}
        }
    
    def _parse_add_column_query(self, query: str, schema: Dict[str, str]) -> Dict[str, Any]:
        """Parse add column queries"""
        # Extract new column name and logic
        new_column = "new_column"
        logic = "lit('default_value')"
        
        if "called" in query.lower():
            parts = query.lower().split("called")
            if len(parts) == 2:
                new_column = parts[1].strip().split()[0].strip('"\'')
        
        return {
            "type": "add_column",
            "sql_query": f"SELECT *, 'default_value' as {new_column} FROM input_table",
            "pyspark_code": f"df.withColumn(\"{new_column}\", {logic})",
            "parameters": {"new_column": new_column, "logic": logic}
        }
    
    def _parse_custom_query(self, query: str, schema: Dict[str, str]) -> Dict[str, Any]:
        """Parse custom queries that don't match common patterns"""
        return {
            "type": "custom",
            "sql_query": f"-- Custom query: {query}",
            "pyspark_code": f"# Custom transformation: {query}",
            "parameters": {"query": query}
        }


class TransformationEngine:
    """Engine for executing transformations"""
    
    def __init__(self, spark_session: SparkSession, dataset_registry: DatasetRegistry):
        self.spark = spark_session
        self.dataset_registry = dataset_registry
        self.nlp_processor = NaturalLanguageProcessor(spark_session)
        self.jobs: Dict[str, TransformationJob] = {}
    
    def create_job(self, name: str, description: Optional[str] = None) -> TransformationJob:
        """Create a new transformation job"""
        job_id = str(uuid.uuid4())
        job = TransformationJob(
            job_id=job_id,
            name=name,
            description=description
        )
        self.jobs[job_id] = job
        return job
    
    def add_transformation_step(self, job_id: str, step_name: str, 
                              natural_language_query: str, 
                              input_datasets: List[str],
                              output_dataset: Optional[str] = None) -> TransformationStep:
        """Add a transformation step to a job"""
        if job_id not in self.jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.jobs[job_id]
        
        # Get schema from input datasets
        input_schema = {}
        for dataset_name in input_datasets:
            dataset_def = self.dataset_registry.get_dataset(dataset_name)
            if dataset_def:
                for field in dataset_def.fields:
                    input_schema[field.name] = field.type
        
        # Parse the natural language query
        transformation_details = self.nlp_processor.parse_query(natural_language_query, input_schema)
        
        # Create transformation step
        step_id = str(uuid.uuid4())
        step = TransformationStep(
            step_id=step_id,
            name=step_name,
            description=f"Transform: {natural_language_query}",
            transformation_type=TransformationType(transformation_details["type"]),
            natural_language_query=natural_language_query,
            sql_query=transformation_details["sql_query"],
            pyspark_code=transformation_details["pyspark_code"],
            parameters=transformation_details["parameters"],
            input_datasets=input_datasets,
            output_dataset=output_dataset
        )
        
        job.add_step(step)
        return step
    
    def execute_job(self, job_id: str, input_data: Dict[str, DataFrame]) -> Dict[str, DataFrame]:
        """Execute a transformation job"""
        if job_id not in self.jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.jobs[job_id]
        job.status = TransformationStatus.RUNNING
        job.started_at = datetime.now()
        
        try:
            current_data = input_data.copy()
            
            for step in job.steps:
                # Execute each step
                step_result = self._execute_step(step, current_data)
                
                # Update current data with step result
                if step.output_dataset:
                    current_data[step.output_dataset] = step_result
                else:
                    # Use step name as output dataset name
                    current_data[step.name] = step_result
            
            job.status = TransformationStatus.COMPLETED
            job.completed_at = datetime.now()
            
            return current_data
            
        except Exception as e:
            job.status = TransformationStatus.FAILED
            job.error_message = str(e)
            raise
    
    def _execute_step(self, step: TransformationStep, input_data: Dict[str, DataFrame]) -> DataFrame:
        """Execute a single transformation step"""
        # Get input DataFrame (assuming single input for now)
        if not step.input_datasets:
            raise ValueError("No input datasets specified")
        
        input_df = input_data.get(step.input_datasets[0])
        if input_df is None:
            raise ValueError(f"Input dataset {step.input_datasets[0]} not found")
        
        # Execute based on transformation type
        if step.transformation_type == TransformationType.FILTER:
            return self._execute_filter(input_df, step.parameters)
        elif step.transformation_type == TransformationType.SELECT:
            return self._execute_select(input_df, step.parameters)
        elif step.transformation_type == TransformationType.GROUP_BY:
            return self._execute_group_by(input_df, step.parameters)
        elif step.transformation_type == TransformationType.SORT:
            return self._execute_sort(input_df, step.parameters)
        elif step.transformation_type == TransformationType.ADD_COLUMN:
            return self._execute_add_column(input_df, step.parameters)
        else:
            # For custom transformations, return the input DataFrame
            return input_df
    
    def _execute_filter(self, df: DataFrame, parameters: Dict[str, Any]) -> DataFrame:
        """Execute filter transformation"""
        condition = parameters.get("condition", "1=1")
        return df.filter(condition)
    
    def _execute_select(self, df: DataFrame, parameters: Dict[str, Any]) -> DataFrame:
        """Execute select transformation"""
        columns = parameters.get("columns", [])
        if columns:
            return df.select(*[col(c) for c in columns])
        return df
    
    def _execute_group_by(self, df: DataFrame, parameters: Dict[str, Any]) -> DataFrame:
        """Execute group by transformation"""
        group_columns = parameters.get("group_columns", [])
        aggregations = parameters.get("aggregations", ["count(*)"])
        
        if group_columns:
            return df.groupBy(*[col(c) for c in group_columns]).agg(*aggregations)
        return df
    
    def _execute_sort(self, df: DataFrame, parameters: Dict[str, Any]) -> DataFrame:
        """Execute sort transformation"""
        sort_columns = parameters.get("sort_columns", [])
        order = parameters.get("order", "ASC")
        
        if sort_columns:
            if order.upper() == "DESC":
                return df.orderBy(*[col(c).desc() for c in sort_columns])
            else:
                return df.orderBy(*[col(c).asc() for c in sort_columns])
        return df
    
    def _execute_add_column(self, df: DataFrame, parameters: Dict[str, Any]) -> DataFrame:
        """Execute add column transformation"""
        new_column = parameters.get("new_column", "new_column")
        logic = parameters.get("logic", "lit('default_value')")
        
        # This is a simplified implementation
        return df.withColumn(new_column, lit("default_value"))
    
    def get_job(self, job_id: str) -> Optional[TransformationJob]:
        """Get a transformation job by ID"""
        return self.jobs.get(job_id)
    
    def list_jobs(self) -> List[TransformationJob]:
        """List all transformation jobs"""
        return list(self.jobs.values())
    
    def save_job(self, job: TransformationJob, file_path: str) -> None:
        """Save a job to file"""
        with open(file_path, 'w') as f:
            json.dump(job.to_dict(), f, indent=2)
    
    def load_job(self, file_path: str) -> TransformationJob:
        """Load a job from file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Reconstruct job from dictionary
        job = TransformationJob(
            job_id=data['job_id'],
            name=data['name'],
            description=data['description'],
            status=TransformationStatus(data['status']),
            created_at=datetime.fromisoformat(data['created_at']),
            started_at=datetime.fromisoformat(data['started_at']) if data['started_at'] else None,
            completed_at=datetime.fromisoformat(data['completed_at']) if data['completed_at'] else None,
            error_message=data['error_message'],
            result_datasets=data['result_datasets']
        )
        
        # Reconstruct steps
        for step_data in data['steps']:
            step = TransformationStep(
                step_id=step_data['step_id'],
                name=step_data['name'],
                description=step_data['description'],
                transformation_type=TransformationType(step_data['transformation_type']),
                natural_language_query=step_data['natural_language_query'],
                sql_query=step_data['sql_query'],
                pyspark_code=step_data['pyspark_code'],
                parameters=step_data['parameters'],
                input_datasets=step_data['input_datasets'],
                output_dataset=step_data['output_dataset']
            )
            job.add_step(step)
        
        self.jobs[job.job_id] = job
        return job
