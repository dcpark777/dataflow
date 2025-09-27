#!/usr/bin/env python3
"""
Command-line interface for DataFlow
"""

import argparse
import sys
import os
from pathlib import Path

from . import DataFlow, DatasetRegistry, TransformationEngine, create_sample_datasets
from .config import get_config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="DataFlow - Natural language data transformations using pyspark-ai"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Version
    parser.add_argument(
        "--version",
        action="version",
        version="DataFlow 0.1.0"
    )
    
    # Transform command (original functionality)
    transform_parser = subparsers.add_parser("transform", help="Transform data using natural language")
    transform_parser.add_argument(
        "input_file",
        nargs="?",
        help="Input data file (CSV, JSON, or Parquet)"
    )
    transform_parser.add_argument(
        "--query",
        "-q",
        help="Natural language query for data transformation"
    )
    transform_parser.add_argument(
        "--output",
        "-o",
        help="Output file path"
    )
    transform_parser.add_argument(
        "--format",
        "-f",
        choices=["csv", "json", "parquet"],
        default="csv",
        help="Output format (default: csv)"
    )
    transform_parser.add_argument(
        "--show-schema",
        action="store_true",
        help="Show data schema"
    )
    transform_parser.add_argument(
        "--show-sample",
        type=int,
        metavar="N",
        help="Show sample of N rows"
    )
    transform_parser.add_argument(
        "--describe",
        action="store_true",
        help="Provide natural language description of the data"
    )
    
    # Dataset management commands
    dataset_parser = subparsers.add_parser("dataset", help="Manage datasets")
    dataset_subparsers = dataset_parser.add_subparsers(dest="dataset_command", help="Dataset commands")
    
    # List datasets
    dataset_subparsers.add_parser("list", help="List all datasets")
    
    # Create dataset
    create_parser = dataset_subparsers.add_parser("create", help="Create a new dataset")
    create_parser.add_argument("name", help="Dataset name")
    create_parser.add_argument("--description", help="Dataset description")
    create_parser.add_argument("--fields", help="JSON string defining fields")
    
    # Show dataset
    show_parser = dataset_subparsers.add_parser("show", help="Show dataset details")
    show_parser.add_argument("name", help="Dataset name")
    
    # Export datasets
    export_parser = dataset_subparsers.add_parser("export", help="Export datasets")
    export_parser.add_argument("--format", choices=["json", "yaml"], default="json", help="Export format")
    export_parser.add_argument("--output", "-o", help="Output file")
    
    # Job management commands
    job_parser = subparsers.add_parser("job", help="Manage transformation jobs")
    job_subparsers = job_parser.add_subparsers(dest="job_command", help="Job commands")
    
    # List jobs
    job_subparsers.add_parser("list", help="List all jobs")
    
    # Create job
    create_job_parser = job_subparsers.add_parser("create", help="Create a new job")
    create_job_parser.add_argument("name", help="Job name")
    create_job_parser.add_argument("--description", help="Job description")
    
    # Show job
    show_job_parser = job_subparsers.add_parser("show", help="Show job details")
    show_job_parser.add_argument("job_id", help="Job ID")
    
    # Server commands
    server_parser = subparsers.add_parser("server", help="Start servers")
    server_subparsers = server_parser.add_subparsers(dest="server_command", help="Server commands")
    
    # Start API server
    server_subparsers.add_parser("api", help="Start API server")
    
    # Start web UI
    server_subparsers.add_parser("ui", help="Start web UI")
    
    args = parser.parse_args()
    
    # Handle commands that don't need OpenAI API key
    if args.command == "server":
        if args.server_command == "api":
            print("Starting API server...")
            os.system("python -m uvicorn dataflow.api:app --host 0.0.0.0 --port 8000 --reload")
        elif args.server_command == "ui":
            print("Starting web UI...")
            os.system("python -m streamlit run dataflow/ui.py --server.port 8501")
        return
    
    # Check for OpenAI API key for other commands
    config = get_config()
    if not config.openai_api_key or config.openai_api_key == "your-openai-api-key-here":
        print("Error: OPENAI_API_KEY is not set or invalid.")
        print("Please set your OpenAI API key in .env file:")
        print("OPENAI_API_KEY=your-actual-api-key-here")
        sys.exit(1)
    
    try:
        # Initialize DataFlow
        df_app = DataFlow()
        
        # Handle different commands
        if args.command == "transform":
            handle_transform_command(df_app, args)
        elif args.command == "dataset":
            handle_dataset_command(df_app, args)
        elif args.command == "job":
            handle_job_command(df_app, args)
        else:
            print("No command specified. Use --help for available options.")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    finally:
        # Clean up
        if 'df_app' in locals():
            df_app.stop()


def handle_transform_command(df_app, args):
    """Handle transform command (original functionality)"""
    if args.input_file:
        # Load data from file
        input_path = Path(args.input_file)
        if not input_path.exists():
            print(f"Error: Input file '{args.input_file}' does not exist.")
            sys.exit(1)
        
        df = df_app.load_data(str(input_path))
    else:
        # Interactive mode - create sample data
        print("No input file provided. Using sample data...")
        sample_data = [
            {"name": "Alice", "age": 25, "city": "New York", "salary": 50000},
            {"name": "Bob", "age": 30, "city": "San Francisco", "salary": 60000},
            {"name": "Charlie", "age": 35, "city": "New York", "salary": 70000},
            {"name": "Diana", "age": 28, "city": "Chicago", "salary": 55000},
            {"name": "Eve", "age": 32, "city": "San Francisco", "salary": 65000}
        ]
        df = df_app.load_data(sample_data)
    
    # Show schema if requested
    if args.show_schema:
        df_app.show_schema(df)
    
    # Show sample if requested
    if args.show_sample:
        df_app.show_sample(df, args.show_sample)
    
    # Describe data if requested
    if args.describe:
        df_app.describe_data(df)
    
    # Apply transformation if query provided
    if args.query:
        print(f"Applying transformation: {args.query}")
        df = df_app.transform(df, args.query)
        df.show()
    
    # Save output if specified
    if args.output:
        df_app.save_data(df, args.output, args.format)
        print(f"Data saved to {args.output}")
    
    # If no specific action requested, show sample
    if not any([args.show_schema, args.show_sample, args.describe, args.query, args.output]):
        print("Data loaded successfully. Use --help for available options.")
        df_app.show_sample(df, 10)


def handle_dataset_command(df_app, args):
    """Handle dataset management commands"""
    dataset_registry = DatasetRegistry()
    
    # Add sample datasets
    sample_datasets = create_sample_datasets()
    for dataset in sample_datasets:
        dataset_registry.add_dataset(dataset)
    
    if args.dataset_command == "list":
        datasets = dataset_registry.list_datasets()
        print("Available datasets:")
        for name in datasets:
            dataset = dataset_registry.get_dataset(name)
            print(f"  - {name}: {dataset.description}")
    
    elif args.dataset_command == "show":
        dataset = dataset_registry.get_dataset(args.name)
        if dataset:
            print(f"Dataset: {dataset.name}")
            print(f"Description: {dataset.description}")
            print("Fields:")
            for field in dataset.fields:
                print(f"  - {field.name} ({field.type}): {field.description}")
        else:
            print(f"Dataset '{args.name}' not found")
    
    elif args.dataset_command == "export":
        exported_data = dataset_registry.export_datasets(args.format)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(exported_data)
            print(f"Datasets exported to {args.output}")
        else:
            print(exported_data)


def handle_job_command(df_app, args):
    """Handle job management commands"""
    dataset_registry = DatasetRegistry()
    transformation_engine = TransformationEngine(df_app.spark, dataset_registry)
    
    if args.job_command == "list":
        jobs = transformation_engine.list_jobs()
        print("Available jobs:")
        for job in jobs:
            print(f"  - {job.name} (ID: {job.job_id[:8]}...): {job.status.value}")
    
    elif args.job_command == "show":
        job = transformation_engine.get_job(args.job_id)
        if job:
            print(f"Job: {job.name}")
            print(f"Status: {job.status.value}")
            print(f"Description: {job.description}")
            print("Steps:")
            for step in job.steps:
                print(f"  - {step.name}: {step.natural_language_query}")
        else:
            print(f"Job '{args.job_id}' not found")


if __name__ == "__main__":
    main()
