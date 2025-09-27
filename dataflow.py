#!/usr/bin/env python3
"""
DataFlow - A Python application for natural language data transformations using pyspark-ai
"""

import os
import sys
from typing import Optional, Union, List, Dict, Any
from pathlib import Path

try:
    from pyspark.sql import SparkSession
    from pyspark_ai import SparkAI
    from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType
    import pandas as pd
except ImportError as e:
    print(f"Error importing required packages: {e}")
    print("Please install the required packages using: pip install -r requirements.txt")
    sys.exit(1)


class DataFlow:
    """
    Main DataFlow class that provides natural language interface for data transformations
    using pyspark-ai.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, spark_config: Optional[Dict[str, str]] = None):
        """
        Initialize DataFlow with optional OpenAI API key and Spark configuration.
        
        Args:
            openai_api_key: OpenAI API key for pyspark-ai. If not provided, will try to get from environment.
            spark_config: Additional Spark configuration options.
        """
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it directly.")
        
        # Initialize Spark session
        spark_builder = SparkSession.builder.appName("DataFlow")
        
        # Add default configurations
        default_config = {
            "spark.sql.adaptive.enabled": "true",
            "spark.sql.adaptive.coalescePartitions.enabled": "true",
            "spark.serializer": "org.apache.spark.serializer.KryoSerializer"
        }
        
        if spark_config:
            default_config.update(spark_config)
            
        for key, value in default_config.items():
            spark_builder = spark_builder.config(key, value)
        
        self.spark = spark_builder.getOrCreate()
        
        # Initialize SparkAI
        self.spark_ai = SparkAI(
            spark_session=self.spark,
            openai_api_key=self.openai_api_key
        )
        
        print("DataFlow initialized successfully!")
        print(f"Spark version: {self.spark.version}")
        print(f"Spark UI: {self.spark.sparkContext.uiWebUrl}")
    
    def load_data(self, source: Union[str, pd.DataFrame, List[Dict]], 
                  format: str = "auto", **kwargs) -> 'DataFrame':
        """
        Load data from various sources into a Spark DataFrame.
        
        Args:
            source: Data source - can be file path, pandas DataFrame, or list of dictionaries
            format: Data format (csv, json, parquet, etc.) or 'auto' for auto-detection
            **kwargs: Additional arguments for the specific data source
            
        Returns:
            Spark DataFrame
        """
        if isinstance(source, pd.DataFrame):
            # Convert pandas DataFrame to Spark DataFrame
            return self.spark.createDataFrame(source)
        
        elif isinstance(source, list):
            # Convert list of dictionaries to Spark DataFrame
            return self.spark.createDataFrame(source)
        
        elif isinstance(source, str):
            # Load from file
            if format == "auto":
                format = Path(source).suffix[1:].lower()  # Remove the dot
            
            if format == "csv":
                return self.spark.read.csv(source, header=True, inferSchema=True, **kwargs)
            elif format == "json":
                return self.spark.read.json(source, **kwargs)
            elif format == "parquet":
                return self.spark.read.parquet(source, **kwargs)
            else:
                raise ValueError(f"Unsupported format: {format}")
        
        else:
            raise ValueError(f"Unsupported data source type: {type(source)}")
    
    def transform(self, df: 'DataFrame', natural_language_query: str) -> 'DataFrame':
        """
        Apply natural language transformations to a DataFrame.
        
        Args:
            df: Input Spark DataFrame
            natural_language_query: Natural language description of the transformation
            
        Returns:
            Transformed Spark DataFrame
        """
        print(f"Applying transformation: {natural_language_query}")
        
        # Use pyspark-ai to apply the transformation
        result_df = self.spark_ai.transform(df, natural_language_query)
        
        print("Transformation completed successfully!")
        return result_df
    
    def show_schema(self, df: 'DataFrame') -> None:
        """Display the schema of a DataFrame."""
        print("DataFrame Schema:")
        df.printSchema()
    
    def show_sample(self, df: 'DataFrame', n: int = 20) -> None:
        """Display a sample of the DataFrame."""
        print(f"Sample data (first {n} rows):")
        df.show(n, truncate=False)
    
    def describe_data(self, df: 'DataFrame') -> None:
        """Provide a natural language description of the data."""
        print("Data Description:")
        description = self.spark_ai.explain(df)
        print(description)
    
    def save_data(self, df: 'DataFrame', output_path: str, format: str = "csv", **kwargs) -> None:
        """
        Save DataFrame to various formats.
        
        Args:
            df: Spark DataFrame to save
            output_path: Output file path
            format: Output format (csv, json, parquet)
            **kwargs: Additional arguments for the specific format
        """
        print(f"Saving data to {output_path} in {format} format...")
        
        if format == "csv":
            df.write.mode("overwrite").option("header", "true").csv(output_path, **kwargs)
        elif format == "json":
            df.write.mode("overwrite").json(output_path, **kwargs)
        elif format == "parquet":
            df.write.mode("overwrite").parquet(output_path, **kwargs)
        else:
            raise ValueError(f"Unsupported output format: {format}")
        
        print("Data saved successfully!")
    
    def stop(self) -> None:
        """Stop the Spark session."""
        if self.spark:
            self.spark.stop()
            print("Spark session stopped.")


def main():
    """Example usage of DataFlow."""
    try:
        # Initialize DataFlow
        df_app = DataFlow()
        
        # Example: Create sample data
        sample_data = [
            {"name": "Alice", "age": 25, "city": "New York", "salary": 50000},
            {"name": "Bob", "age": 30, "city": "San Francisco", "salary": 60000},
            {"name": "Charlie", "age": 35, "city": "New York", "salary": 70000},
            {"name": "Diana", "age": 28, "city": "Chicago", "salary": 55000},
            {"name": "Eve", "age": 32, "city": "San Francisco", "salary": 65000}
        ]
        
        # Load data
        df = df_app.load_data(sample_data)
        
        # Show initial data
        print("\n=== Initial Data ===")
        df_app.show_schema(df)
        df_app.show_sample(df)
        
        # Apply transformations using natural language
        print("\n=== Applying Transformations ===")
        
        # Filter data
        filtered_df = df_app.transform(df, "Filter rows where age is greater than 30")
        print("\nFiltered data (age > 30):")
        filtered_df.show()
        
        # Group and aggregate
        grouped_df = df_app.transform(df, "Group by city and calculate average salary")
        print("\nAverage salary by city:")
        grouped_df.show()
        
        # Add new column
        enhanced_df = df_app.transform(df, "Add a new column called 'age_group' that categorizes age as 'young' for age < 30, 'middle' for age 30-35, and 'senior' for age > 35")
        print("\nData with age groups:")
        enhanced_df.show()
        
        # Get data description
        print("\n=== Data Description ===")
        df_app.describe_data(df)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have set the OPENAI_API_KEY environment variable.")
    
    finally:
        # Clean up
        if 'df_app' in locals():
            df_app.stop()


if __name__ == "__main__":
    main()
