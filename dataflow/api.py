"""
REST API endpoints for DataFlow dataset management and transformations
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pyspark.sql import SparkSession

from .dataset import DatasetDefinition, DatasetRegistry, create_sample_datasets
from .transformation import TransformationEngine, TransformationJob, TransformationStep
from .config import get_config


# Pydantic models for API requests/responses
class DatasetCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    fields: List[Dict[str, Any]]
    source_type: str = "manual"
    source_config: Dict[str, Any] = {}
    tags: List[str] = []


class DatasetUpdateRequest(BaseModel):
    description: Optional[str] = None
    fields: List[Dict[str, Any]]
    source_type: Optional[str] = None
    source_config: Dict[str, Any] = {}
    tags: List[str] = []


class TransformationRequest(BaseModel):
    job_name: str
    job_description: Optional[str] = None
    steps: List[Dict[str, Any]]


class TransformationStepRequest(BaseModel):
    step_name: str
    natural_language_query: str
    input_datasets: List[str]
    output_dataset: Optional[str] = None


class DataUploadRequest(BaseModel):
    dataset_name: str
    data: List[Dict[str, Any]]


# Initialize FastAPI app
app = FastAPI(
    title="DataFlow API",
    description="REST API for DataFlow dataset management and transformations",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
dataset_registry: Optional[DatasetRegistry] = None
transformation_engine: Optional[TransformationEngine] = None
spark_session: Optional[SparkSession] = None
config = get_config()


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global dataset_registry, transformation_engine, spark_session
    
    # Initialize Spark session with configuration
    spark_builder = SparkSession.builder.appName(config.spark_app_name)
    
    # Apply Spark configuration
    spark_config = config.get_spark_config()
    for key, value in spark_config.items():
        spark_builder = spark_builder.config(key, value)
    
    spark_session = spark_builder.getOrCreate()
    
    # Initialize dataset registry
    dataset_registry = DatasetRegistry()
    
    # Add sample datasets
    sample_datasets = create_sample_datasets()
    for dataset in sample_datasets:
        dataset_registry.add_dataset(dataset)
    
    # Initialize transformation engine
    transformation_engine = TransformationEngine(spark_session, dataset_registry)
    
    print("DataFlow API started successfully!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global spark_session
    if spark_session:
        spark_session.stop()


# Dataset Management Endpoints

@app.get("/api/datasets")
async def list_datasets():
    """List all datasets"""
    if not dataset_registry:
        raise HTTPException(status_code=500, detail="Dataset registry not initialized")
    
    datasets = []
    for name in dataset_registry.list_datasets():
        dataset = dataset_registry.get_dataset(name)
        if dataset:
            datasets.append({
                "name": dataset.name,
                "description": dataset.description,
                "fields": [{"name": f.name, "type": f.type, "nullable": f.nullable, "description": f.description} for f in dataset.fields],
                "source_type": dataset.source_type,
                "tags": dataset.tags,
                "created_at": datetime.now().isoformat()
            })
    
    return {"datasets": datasets}


@app.get("/api/datasets/{dataset_name}")
async def get_dataset(dataset_name: str):
    """Get a specific dataset definition"""
    if not dataset_registry:
        raise HTTPException(status_code=500, detail="Dataset registry not initialized")
    
    dataset = dataset_registry.get_dataset(dataset_name)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_name}' not found")
    
    return {
        "name": dataset.name,
        "description": dataset.description,
        "fields": [{"name": f.name, "type": f.type, "nullable": f.nullable, "description": f.description} for f in dataset.fields],
        "source_type": dataset.source_type,
        "source_config": dataset.source_config,
        "tags": dataset.tags
    }


@app.post("/api/datasets")
async def create_dataset(request: DatasetCreateRequest):
    """Create a new dataset definition"""
    if not dataset_registry:
        raise HTTPException(status_code=500, detail="Dataset registry not initialized")
    
    # Check if dataset already exists
    if dataset_registry.get_dataset(request.name):
        raise HTTPException(status_code=400, detail=f"Dataset '{request.name}' already exists")
    
    # Create field definitions
    fields = []
    for field_data in request.fields:
        field = DatasetDefinition.FieldDefinition(
            name=field_data["name"],
            type=field_data["type"],
            nullable=field_data.get("nullable", True),
            description=field_data.get("description")
        )
        fields.append(field)
    
    # Create dataset definition
    dataset = DatasetDefinition(
        name=request.name,
        description=request.description,
        fields=fields,
        source_type=request.source_type,
        source_config=request.source_config,
        tags=request.tags
    )
    
    dataset_registry.add_dataset(dataset)
    
    return {"message": f"Dataset '{request.name}' created successfully", "dataset": dataset.to_dict()}


@app.put("/api/datasets/{dataset_name}")
async def update_dataset(dataset_name: str, request: DatasetUpdateRequest):
    """Update an existing dataset definition"""
    if not dataset_registry:
        raise HTTPException(status_code=500, detail="Dataset registry not initialized")
    
    dataset = dataset_registry.get_dataset(dataset_name)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_name}' not found")
    
    # Update fields
    fields = []
    for field_data in request.fields:
        field = DatasetDefinition.FieldDefinition(
            name=field_data["name"],
            type=field_data["type"],
            nullable=field_data.get("nullable", True),
            description=field_data.get("description")
        )
        fields.append(field)
    
    # Update dataset
    dataset.fields = fields
    if request.description is not None:
        dataset.description = request.description
    if request.source_type is not None:
        dataset.source_type = request.source_type
    dataset.source_config = request.source_config
    dataset.tags = request.tags
    
    dataset_registry.update_dataset(dataset)
    
    return {"message": f"Dataset '{dataset_name}' updated successfully", "dataset": dataset.to_dict()}


@app.delete("/api/datasets/{dataset_name}")
async def delete_dataset(dataset_name: str):
    """Delete a dataset definition"""
    if not dataset_registry:
        raise HTTPException(status_code=500, detail="Dataset registry not initialized")
    
    if not dataset_registry.remove_dataset(dataset_name):
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_name}' not found")
    
    return {"message": f"Dataset '{dataset_name}' deleted successfully"}


@app.post("/api/datasets/{dataset_name}/validate")
async def validate_dataset_data(dataset_name: str, request: DataUploadRequest):
    """Validate data against a dataset schema"""
    if not dataset_registry:
        raise HTTPException(status_code=500, detail="Dataset registry not initialized")
    
    dataset = dataset_registry.get_dataset(dataset_name)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_name}' not found")
    
    errors = dataset.validate_data(request.data)
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "row_count": len(request.data)
    }


# Transformation Management Endpoints

@app.get("/api/transformations")
async def list_transformations():
    """List all transformation jobs"""
    if not transformation_engine:
        raise HTTPException(status_code=500, detail="Transformation engine not initialized")
    
    jobs = transformation_engine.list_jobs()
    return {"jobs": [job.to_dict() for job in jobs]}


@app.get("/api/transformations/{job_id}")
async def get_transformation(job_id: str):
    """Get a specific transformation job"""
    if not transformation_engine:
        raise HTTPException(status_code=500, detail="Transformation engine not initialized")
    
    job = transformation_engine.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Transformation job '{job_id}' not found")
    
    return job.to_dict()


@app.post("/api/transformations")
async def create_transformation(request: TransformationRequest):
    """Create a new transformation job"""
    if not transformation_engine:
        raise HTTPException(status_code=500, detail="Transformation engine not initialized")
    
    # Create job
    job = transformation_engine.create_job(request.job_name, request.job_description)
    
    # Add steps
    for step_data in request.steps:
        transformation_engine.add_transformation_step(
            job.job_id,
            step_data["step_name"],
            step_data["natural_language_query"],
            step_data["input_datasets"],
            step_data.get("output_dataset")
        )
    
    return {"message": "Transformation job created successfully", "job": job.to_dict()}


@app.post("/api/transformations/{job_id}/steps")
async def add_transformation_step(job_id: str, request: TransformationStepRequest):
    """Add a step to an existing transformation job"""
    if not transformation_engine:
        raise HTTPException(status_code=500, detail="Transformation engine not initialized")
    
    step = transformation_engine.add_transformation_step(
        job_id,
        request.step_name,
        request.natural_language_query,
        request.input_datasets,
        request.output_dataset
    )
    
    return {"message": "Transformation step added successfully", "step": {
        "step_id": step.step_id,
        "name": step.name,
        "description": step.description,
        "transformation_type": step.transformation_type.value,
        "natural_language_query": step.natural_language_query,
        "sql_query": step.sql_query,
        "pyspark_code": step.pyspark_code,
        "parameters": step.parameters,
        "input_datasets": step.input_datasets,
        "output_dataset": step.output_dataset
    }}


@app.post("/api/transformations/{job_id}/execute")
async def execute_transformation(job_id: str, input_data: Dict[str, List[Dict[str, Any]]]):
    """Execute a transformation job with input data"""
    if not transformation_engine or not spark_session:
        raise HTTPException(status_code=500, detail="Transformation engine not initialized")
    
    # Convert input data to Spark DataFrames
    spark_dataframes = {}
    for dataset_name, data in input_data.items():
        df = spark_session.createDataFrame(data)
        spark_dataframes[dataset_name] = df
    
    try:
        # Execute the job
        result_dataframes = transformation_engine.execute_job(job_id, spark_dataframes)
        
        # Convert results back to JSON-serializable format
        results = {}
        for dataset_name, df in result_dataframes.items():
            # Collect data and convert to list of dictionaries
            data = [row.asDict() for row in df.collect()]
            results[dataset_name] = data
        
        return {
            "message": "Transformation executed successfully",
            "results": results,
            "job_status": transformation_engine.get_job(job_id).status.value
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transformation execution failed: {str(e)}")


# Utility Endpoints

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "spark_available": spark_session is not None,
        "dataset_registry_available": dataset_registry is not None,
        "transformation_engine_available": transformation_engine is not None
    }


@app.get("/api/schema/{dataset_name}")
async def get_dataset_schema(dataset_name: str):
    """Get Spark schema for a dataset"""
    if not dataset_registry:
        raise HTTPException(status_code=500, detail="Dataset registry not initialized")
    
    dataset = dataset_registry.get_dataset(dataset_name)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_name}' not found")
    
    schema = dataset.get_spark_schema()
    return {
        "dataset_name": dataset_name,
        "schema": schema.json(),
        "fields": [{"name": f.name, "type": f.dataType.typeName(), "nullable": f.nullable} for f in schema.fields]
    }


@app.post("/api/export/datasets")
async def export_datasets(format: str = "json"):
    """Export all datasets in specified format"""
    if not dataset_registry:
        raise HTTPException(status_code=500, detail="Dataset registry not initialized")
    
    try:
        exported_data = dataset_registry.export_datasets(format)
        return {"format": format, "data": exported_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@app.post("/api/import/datasets")
async def import_datasets(data: str, format: str = "json"):
    """Import datasets from specified format"""
    if not dataset_registry:
        raise HTTPException(status_code=500, detail="Dataset registry not initialized")
    
    try:
        dataset_registry.import_datasets(data, format)
        return {"message": "Datasets imported successfully", "count": len(dataset_registry.list_datasets())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
