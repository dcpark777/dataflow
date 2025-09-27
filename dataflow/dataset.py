"""
Dataset definition and management module for DataFlow
"""

import json
import yaml
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Any, Optional, Union, Type
from pathlib import Path
import pandas as pd
from pyspark.sql import DataFrame
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, BooleanType, DateType, TimestampType


@dataclass
class FieldDefinition:
    """Definition of a single field in a dataset"""
    name: str
    type: str  # 'string', 'integer', 'double', 'boolean', 'date', 'timestamp'
    nullable: bool = True
    description: Optional[str] = None


@dataclass
class DatasetDefinition:
    """Definition of a dataset with schema and metadata"""
    name: str
    description: Optional[str] = None
    fields: List[FieldDefinition] = field(default_factory=list)
    source_type: str = "manual"  # 'manual', 'file', 'database', 'api'
    source_config: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatasetDefinition':
        """Create from dictionary representation"""
        fields_data = data.get('fields', [])
        fields = [FieldDefinition(**field) for field in fields_data]
        
        return cls(
            name=data['name'],
            description=data.get('description'),
            fields=fields,
            source_type=data.get('source_type', 'manual'),
            source_config=data.get('source_config', {}),
            tags=data.get('tags', [])
        )
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'DatasetDefinition':
        """Create from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def to_yaml(self) -> str:
        """Convert to YAML string"""
        return yaml.dump(self.to_dict(), default_flow_style=False)
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'DatasetDefinition':
        """Create from YAML string"""
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)
    
    def get_spark_schema(self) -> StructType:
        """Convert field definitions to Spark schema"""
        spark_fields = []
        
        type_mapping = {
            'string': StringType(),
            'integer': IntegerType(),
            'double': DoubleType(),
            'boolean': BooleanType(),
            'date': DateType(),
            'timestamp': TimestampType()
        }
        
        for field in self.fields:
            spark_type = type_mapping.get(field.type, StringType())
            spark_field = StructField(field.name, spark_type, field.nullable)
            spark_fields.append(spark_field)
        
        return StructType(spark_fields)
    
    def validate_data(self, data: List[Dict[str, Any]]) -> List[str]:
        """Validate data against schema and return list of errors"""
        errors = []
        
        if not data:
            return ["No data provided"]
        
        # Get field names from schema
        schema_fields = {field.name for field in self.fields}
        
        # Check first row to get data fields
        if data:
            data_fields = set(data[0].keys())
            
            # Check for missing required fields
            for field in self.fields:
                if not field.nullable and field.name not in data_fields:
                    errors.append(f"Required field '{field.name}' is missing")
            
            # Check for extra fields
            extra_fields = data_fields - schema_fields
            if extra_fields:
                errors.append(f"Unexpected fields found: {', '.join(extra_fields)}")
        
        return errors


class DatasetRegistry:
    """Registry for managing dataset definitions"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize dataset registry
        
        Args:
            storage_path: Path to store dataset definitions (default: in-memory)
        """
        self.storage_path = Path(storage_path) if storage_path else None
        self.datasets: Dict[str, DatasetDefinition] = {}
        
        if self.storage_path and self.storage_path.exists():
            self.load_from_storage()
    
    def add_dataset(self, dataset: DatasetDefinition) -> None:
        """Add a dataset definition to the registry"""
        self.datasets[dataset.name] = dataset
        if self.storage_path:
            self.save_to_storage()
    
    def get_dataset(self, name: str) -> Optional[DatasetDefinition]:
        """Get a dataset definition by name"""
        return self.datasets.get(name)
    
    def list_datasets(self) -> List[str]:
        """List all dataset names"""
        return list(self.datasets.keys())
    
    def remove_dataset(self, name: str) -> bool:
        """Remove a dataset definition"""
        if name in self.datasets:
            del self.datasets[name]
            if self.storage_path:
                self.save_to_storage()
            return True
        return False
    
    def update_dataset(self, dataset: DatasetDefinition) -> None:
        """Update an existing dataset definition"""
        self.add_dataset(dataset)
    
    def save_to_storage(self) -> None:
        """Save all datasets to storage"""
        if not self.storage_path:
            return
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Save each dataset as a separate JSON file
        for name, dataset in self.datasets.items():
            file_path = self.storage_path / f"{name}.json"
            with open(file_path, 'w') as f:
                f.write(dataset.to_json())
    
    def load_from_storage(self) -> None:
        """Load datasets from storage"""
        if not self.storage_path or not self.storage_path.exists():
            return
        
        for file_path in self.storage_path.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    json_str = f.read()
                dataset = DatasetDefinition.from_json(json_str)
                self.datasets[dataset.name] = dataset
            except Exception as e:
                print(f"Error loading dataset from {file_path}: {e}")
    
    def export_datasets(self, format: str = "json") -> str:
        """Export all datasets in specified format"""
        datasets_dict = {name: dataset.to_dict() for name, dataset in self.datasets.items()}
        
        if format.lower() == "json":
            return json.dumps(datasets_dict, indent=2)
        elif format.lower() == "yaml":
            return yaml.dump(datasets_dict, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def import_datasets(self, data: str, format: str = "json") -> None:
        """Import datasets from specified format"""
        if format.lower() == "json":
            datasets_dict = json.loads(data)
        elif format.lower() == "yaml":
            datasets_dict = yaml.safe_load(data)
        else:
            raise ValueError(f"Unsupported import format: {format}")
        
        for name, dataset_data in datasets_dict.items():
            dataset = DatasetDefinition.from_dict(dataset_data)
            self.add_dataset(dataset)


# Example dataset definitions
def create_sample_datasets() -> List[DatasetDefinition]:
    """Create sample dataset definitions for demonstration"""
    
    # Employee dataset
    employee_dataset = DatasetDefinition(
        name="employees",
        description="Employee information dataset",
        fields=[
            FieldDefinition("employee_id", "integer", False, "Unique employee identifier"),
            FieldDefinition("name", "string", False, "Employee full name"),
            FieldDefinition("department", "string", False, "Department name"),
            FieldDefinition("salary", "double", False, "Annual salary"),
            FieldDefinition("hire_date", "date", False, "Date of hire"),
            FieldDefinition("is_active", "boolean", False, "Whether employee is active")
        ],
        source_type="manual",
        tags=["hr", "employees", "personnel"]
    )
    
    # Sales dataset
    sales_dataset = DatasetDefinition(
        name="sales",
        description="Sales transaction dataset",
        fields=[
            FieldDefinition("transaction_id", "integer", False, "Unique transaction identifier"),
            FieldDefinition("product_id", "integer", False, "Product identifier"),
            FieldDefinition("customer_id", "integer", False, "Customer identifier"),
            FieldDefinition("amount", "double", False, "Transaction amount"),
            FieldDefinition("quantity", "integer", False, "Quantity sold"),
            FieldDefinition("sale_date", "timestamp", False, "Date and time of sale"),
            FieldDefinition("region", "string", True, "Sales region")
        ],
        source_type="manual",
        tags=["sales", "transactions", "revenue"]
    )
    
    # Customer dataset
    customer_dataset = DatasetDefinition(
        name="customers",
        description="Customer information dataset",
        fields=[
            FieldDefinition("customer_id", "integer", False, "Unique customer identifier"),
            FieldDefinition("name", "string", False, "Customer name"),
            FieldDefinition("email", "string", True, "Customer email address"),
            FieldDefinition("phone", "string", True, "Customer phone number"),
            FieldDefinition("address", "string", True, "Customer address"),
            FieldDefinition("registration_date", "date", False, "Date of registration"),
            FieldDefinition("customer_tier", "string", False, "Customer tier (bronze, silver, gold)")
        ],
        source_type="manual",
        tags=["customers", "contacts", "demographics"]
    )
    
    return [employee_dataset, sales_dataset, customer_dataset]
