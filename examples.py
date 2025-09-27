#!/usr/bin/env python3
"""
DataFlow Examples - Various examples demonstrating natural language data transformations
"""

import os
import pandas as pd
from dataflow import DataFlow


def example_basic_transformations():
    """Example of basic data transformations using natural language."""
    print("=== Basic Transformations Example ===")
    
    # Initialize DataFlow
    df_app = DataFlow()
    
    # Create sample employee data
    employee_data = [
        {"employee_id": 1, "name": "Alice Johnson", "department": "Engineering", "salary": 75000, "years_experience": 5},
        {"employee_id": 2, "name": "Bob Smith", "department": "Marketing", "salary": 65000, "years_experience": 3},
        {"employee_id": 3, "name": "Charlie Brown", "department": "Engineering", "salary": 85000, "years_experience": 7},
        {"employee_id": 4, "name": "Diana Prince", "department": "Sales", "salary": 70000, "years_experience": 4},
        {"employee_id": 5, "name": "Eve Wilson", "department": "Engineering", "salary": 90000, "years_experience": 8},
        {"employee_id": 6, "name": "Frank Miller", "department": "Marketing", "salary": 60000, "years_experience": 2},
    ]
    
    # Load data
    df = df_app.load_data(employee_data)
    
    print("Original data:")
    df_app.show_sample(df)
    
    # Natural language transformations
    transformations = [
        "Filter employees with salary greater than 70000",
        "Group by department and calculate average salary",
        "Add a column called 'seniority' that categorizes years_experience as 'junior' (< 4), 'mid' (4-6), 'senior' (> 6)",
        "Sort by salary in descending order",
        "Select only name, department, and salary columns"
    ]
    
    current_df = df
    for i, transformation in enumerate(transformations, 1):
        print(f"\n--- Transformation {i}: {transformation} ---")
        current_df = df_app.transform(current_df, transformation)
        current_df.show()
    
    df_app.stop()


def example_sales_data_analysis():
    """Example of sales data analysis using natural language."""
    print("\n=== Sales Data Analysis Example ===")
    
    # Initialize DataFlow
    df_app = DataFlow()
    
    # Create sample sales data
    sales_data = [
        {"product": "Laptop", "category": "Electronics", "price": 999.99, "quantity": 10, "date": "2024-01-15"},
        {"product": "Mouse", "category": "Electronics", "price": 29.99, "quantity": 50, "date": "2024-01-15"},
        {"product": "Desk Chair", "category": "Furniture", "price": 199.99, "quantity": 5, "date": "2024-01-16"},
        {"product": "Monitor", "category": "Electronics", "price": 299.99, "quantity": 15, "date": "2024-01-16"},
        {"product": "Bookshelf", "category": "Furniture", "price": 149.99, "quantity": 8, "date": "2024-01-17"},
        {"product": "Keyboard", "category": "Electronics", "price": 79.99, "quantity": 25, "date": "2024-01-17"},
    ]
    
    # Load data
    df = df_app.load_data(sales_data)
    
    print("Original sales data:")
    df_app.show_sample(df)
    
    # Sales analysis transformations
    analysis_queries = [
        "Add a new column called 'total_revenue' that calculates price * quantity",
        "Group by category and calculate total revenue and average price",
        "Filter products with quantity sold greater than 20",
        "Sort by total revenue in descending order"
    ]
    
    current_df = df
    for i, query in enumerate(analysis_queries, 1):
        print(f"\n--- Analysis {i}: {query} ---")
        current_df = df_app.transform(current_df, query)
        current_df.show()
    
    df_app.stop()


def example_data_cleaning():
    """Example of data cleaning operations using natural language."""
    print("\n=== Data Cleaning Example ===")
    
    # Initialize DataFlow
    df_app = DataFlow()
    
    # Create sample data with some issues
    messy_data = [
        {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 25, "city": "New York"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": None, "city": "Los Angeles"},
        {"id": 3, "name": "", "email": "bob@example.com", "age": 30, "city": "Chicago"},
        {"id": 4, "name": "Alice Johnson", "email": "invalid-email", "age": 28, "city": "Boston"},
        {"id": 5, "name": "Charlie Brown", "email": "charlie@example.com", "age": 35, "city": ""},
        {"id": 6, "name": "Diana Prince", "email": "diana@example.com", "age": 22, "city": "Seattle"},
    ]
    
    # Load data
    df = df_app.load_data(messy_data)
    
    print("Original messy data:")
    df_app.show_sample(df)
    
    # Data cleaning transformations
    cleaning_queries = [
        "Remove rows where name is empty or null",
        "Remove rows where age is null",
        "Remove rows where city is empty or null",
        "Add a new column called 'email_valid' that checks if email contains '@' and ends with '.com'",
        "Filter to keep only rows with valid emails"
    ]
    
    current_df = df
    for i, query in enumerate(cleaning_queries, 1):
        print(f"\n--- Cleaning Step {i}: {query} ---")
        current_df = df_app.transform(current_df, query)
        current_df.show()
    
    print("\nFinal cleaned data:")
    current_df.show()
    
    df_app.stop()


def example_advanced_analytics():
    """Example of advanced analytics using natural language."""
    print("\n=== Advanced Analytics Example ===")
    
    # Initialize DataFlow
    df_app = DataFlow()
    
    # Create sample customer data
    customer_data = [
        {"customer_id": 1, "name": "Alice", "age": 25, "income": 50000, "purchases": 5, "total_spent": 1200},
        {"customer_id": 2, "name": "Bob", "age": 35, "income": 75000, "purchases": 8, "total_spent": 2100},
        {"customer_id": 3, "name": "Charlie", "age": 28, "income": 60000, "purchases": 3, "total_spent": 800},
        {"customer_id": 4, "name": "Diana", "age": 42, "income": 90000, "purchases": 12, "total_spent": 3500},
        {"customer_id": 5, "name": "Eve", "age": 31, "income": 65000, "purchases": 6, "total_spent": 1500},
        {"customer_id": 6, "name": "Frank", "age": 29, "income": 55000, "purchases": 4, "total_spent": 900},
    ]
    
    # Load data
    df = df_app.load_data(customer_data)
    
    print("Original customer data:")
    df_app.show_sample(df)
    
    # Advanced analytics transformations
    analytics_queries = [
        "Add a new column called 'avg_purchase_value' that calculates total_spent / purchases",
        "Add a new column called 'customer_segment' that categorizes customers as 'high_value' if total_spent > 2000, 'medium_value' if total_spent between 1000-2000, and 'low_value' if total_spent < 1000",
        "Group by customer_segment and calculate average income, average purchases, and count of customers",
        "Add a new column called 'age_group' that categorizes age as 'young' (< 30), 'middle' (30-40), 'senior' (> 40)",
        "Create a summary showing average total_spent by age_group and customer_segment"
    ]
    
    current_df = df
    for i, query in enumerate(analytics_queries, 1):
        print(f"\n--- Analytics Step {i}: {query} ---")
        current_df = df_app.transform(current_df, query)
        current_df.show()
    
    df_app.stop()


def main():
    """Run all examples."""
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please set your OpenAI API key before running examples:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return
    
    try:
        # Run examples
        example_basic_transformations()
        example_sales_data_analysis()
        example_data_cleaning()
        example_advanced_analytics()
        
        print("\n=== All Examples Completed Successfully! ===")
        
    except Exception as e:
        print(f"Error running examples: {e}")


if __name__ == "__main__":
    main()
