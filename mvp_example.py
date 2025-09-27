#!/usr/bin/env python3
"""
DataFlow MVP Example - Demonstrates the complete MVP functionality
"""

import os
import json
from datetime import datetime
from dataflow import (
    DataFlow, 
    DatasetDefinition, 
    DatasetRegistry, 
    FieldDefinition,
    TransformationEngine,
    TransformationJob,
    create_sample_datasets
)
from dataflow.config import get_config


def main():
    """Demonstrate DataFlow MVP functionality"""
    
    print("🔄 DataFlow MVP Example")
    print("=" * 50)
    
    # Check configuration
    config = get_config()
    if not config.is_valid():
        print("❌ Configuration validation failed:")
        for error in config.validate():
            print(f"   • {error}")
        print("\nPlease check your .env file and ensure all required settings are configured.")
        return
    
    try:
        # Initialize DataFlow
        print("\n1. Initializing DataFlow...")
        df_app = DataFlow()
        
        # Initialize dataset registry
        print("\n2. Setting up Dataset Registry...")
        dataset_registry = DatasetRegistry()
        
        # Add sample datasets
        print("\n3. Creating Sample Datasets...")
        sample_datasets = create_sample_datasets()
        for dataset in sample_datasets:
            dataset_registry.add_dataset(dataset)
            print(f"   ✅ Created dataset: {dataset.name}")
        
        # Initialize transformation engine
        print("\n4. Setting up Transformation Engine...")
        transformation_engine = TransformationEngine(df_app.spark, dataset_registry)
        
        # Demonstrate dataset definition formats
        print("\n5. Demonstrating Dataset Definition Formats...")
        
        # JSON format
        employee_dataset = dataset_registry.get_dataset("employees")
        json_format = employee_dataset.to_json()
        print(f"   📄 JSON Format (first 200 chars):")
        print(f"   {json_format[:200]}...")
        
        # YAML format
        yaml_format = employee_dataset.to_yaml()
        print(f"   📄 YAML Format (first 200 chars):")
        print(f"   {yaml_format[:200]}...")
        
        # Python dataclass format
        print(f"   📄 Python Dataclass Format:")
        print(f"   DatasetDefinition(name='{employee_dataset.name}', description='{employee_dataset.description}', ...)")
        
        # Create sample data
        print("\n6. Creating Sample Data...")
        employee_data = [
            {"employee_id": 1, "name": "Alice Johnson", "department": "Engineering", "salary": 75000.0, "hire_date": "2020-01-15", "is_active": True},
            {"employee_id": 2, "name": "Bob Smith", "department": "Marketing", "salary": 65000.0, "hire_date": "2021-03-20", "is_active": True},
            {"employee_id": 3, "name": "Charlie Brown", "department": "Engineering", "salary": 85000.0, "hire_date": "2019-06-10", "is_active": True},
            {"employee_id": 4, "name": "Diana Prince", "department": "Sales", "salary": 70000.0, "hire_date": "2022-02-14", "is_active": True},
            {"employee_id": 5, "name": "Eve Wilson", "department": "Engineering", "salary": 90000.0, "hire_date": "2018-09-05", "is_active": False},
        ]
        
        sales_data = [
            {"transaction_id": 1, "product_id": 101, "customer_id": 1001, "amount": 299.99, "quantity": 1, "sale_date": "2024-01-15 10:30:00", "region": "North"},
            {"transaction_id": 2, "product_id": 102, "customer_id": 1002, "amount": 149.99, "quantity": 2, "sale_date": "2024-01-15 14:20:00", "region": "South"},
            {"transaction_id": 3, "product_id": 103, "customer_id": 1001, "amount": 199.99, "quantity": 1, "sale_date": "2024-01-16 09:15:00", "region": "North"},
            {"transaction_id": 4, "product_id": 101, "customer_id": 1003, "amount": 299.99, "quantity": 1, "sale_date": "2024-01-16 16:45:00", "region": "East"},
            {"transaction_id": 5, "product_id": 104, "customer_id": 1002, "amount": 399.99, "quantity": 1, "sale_date": "2024-01-17 11:30:00", "region": "South"},
        ]
        
        # Load data into Spark DataFrames
        employee_df = df_app.load_data(employee_data)
        sales_df = df_app.load_data(sales_data)
        
        print(f"   ✅ Loaded {employee_df.count()} employee records")
        print(f"   ✅ Loaded {sales_df.count()} sales records")
        
        # Demonstrate natural language transformations
        print("\n7. Demonstrating Natural Language Transformations...")
        
        # Create a transformation job
        job = transformation_engine.create_job("Employee Analysis", "Analyze employee data using natural language")
        
        # Add transformation steps
        steps = [
            ("Filter Active Employees", "Filter employees where is_active equals true", ["employees"]),
            ("Group by Department", "Group by department and calculate average salary", ["employees"]),
            ("High Salary Filter", "Filter employees with salary greater than 70000", ["employees"]),
            ("Sort by Salary", "Sort by salary in descending order", ["employees"])
        ]
        
        for step_name, query, input_datasets in steps:
            step = transformation_engine.add_transformation_step(
                job.job_id, step_name, query, input_datasets
            )
            print(f"   ✅ Added step: {step_name}")
            print(f"      Query: {query}")
            print(f"      Generated SQL: {step.sql_query}")
            print(f"      Generated PySpark: {step.pyspark_code}")
        
        # Execute the transformation job
        print("\n8. Executing Transformation Job...")
        input_data = {"employees": employee_df}
        
        try:
            results = transformation_engine.execute_job(job.job_id, input_data)
            print(f"   ✅ Job executed successfully!")
            print(f"   📊 Generated {len(results)} result datasets")
            
            # Show results
            for dataset_name, result_df in results.items():
                print(f"\n   📈 Results for '{dataset_name}':")
                result_df.show(10, truncate=False)
                
        except Exception as e:
            print(f"   ❌ Job execution failed: {e}")
        
        # Demonstrate data validation
        print("\n9. Demonstrating Data Validation...")
        
        # Test valid data
        valid_data = [
            {"employee_id": 6, "name": "Frank Miller", "department": "HR", "salary": 60000.0, "hire_date": "2023-01-01", "is_active": True}
        ]
        
        errors = employee_dataset.validate_data(valid_data)
        if not errors:
            print("   ✅ Valid data passed validation")
        else:
            print(f"   ❌ Validation errors: {errors}")
        
        # Test invalid data
        invalid_data = [
            {"employee_id": 7, "name": "", "department": "IT", "salary": 50000.0, "hire_date": "2023-01-01", "is_active": True}  # Empty name
        ]
        
        errors = employee_dataset.validate_data(invalid_data)
        if errors:
            print(f"   ❌ Invalid data caught: {errors}")
        
        # Export/Import demonstration
        print("\n10. Demonstrating Export/Import...")
        
        # Export datasets
        exported_json = dataset_registry.export_datasets("json")
        print(f"   ✅ Exported {len(dataset_registry.list_datasets())} datasets to JSON")
        
        # Save to file
        with open("exported_datasets.json", "w") as f:
            f.write(exported_json)
        print("   💾 Saved exported datasets to 'exported_datasets.json'")
        
        # Job management
        print("\n11. Job Management...")
        all_jobs = transformation_engine.list_jobs()
        print(f"   📋 Total jobs created: {len(all_jobs)}")
        
        for job in all_jobs:
            print(f"   📝 Job: {job.name} (ID: {job.job_id[:8]}...)")
            print(f"      Status: {job.status.value}")
            print(f"      Steps: {len(job.steps)}")
            print(f"      Created: {job.created_at}")
        
        print("\n" + "=" * 50)
        print("🎉 DataFlow MVP Example Completed Successfully!")
        print("\nKey Features Demonstrated:")
        print("✅ Dataset definition in JSON, YAML, and Python dataclass formats")
        print("✅ Dataset registry for managing datasets")
        print("✅ Natural language to SQL/PySpark translation")
        print("✅ Job/operator system for transformations")
        print("✅ Data validation against schemas")
        print("✅ Export/import functionality")
        print("✅ Complete transformation pipeline execution")
        
        print("\n🚀 Next Steps:")
        print("1. Start the API server: python -m dataflow.api")
        print("2. Launch the web UI: streamlit run dataflow/ui.py")
        print("3. Access the web interface at http://localhost:8501")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        if 'df_app' in locals():
            df_app.stop()
            print("\n🧹 Cleaned up Spark session")


if __name__ == "__main__":
    main()
