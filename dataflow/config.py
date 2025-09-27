"""
Configuration management for DataFlow
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class DataFlowConfig:
    """Configuration class for DataFlow application"""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration
        
        Args:
            env_file: Path to .env file (default: .env in project root)
        """
        # Load environment variables from .env file
        if env_file:
            load_dotenv(env_file)
        else:
            # Try to load from project root
            project_root = Path(__file__).parent.parent
            env_path = project_root / ".env"
            if env_path.exists():
                load_dotenv(env_path)
            else:
                # Load from current directory
                load_dotenv()
        
        # OpenAI Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # API Configuration
        self.api_url = os.getenv("DATAFLOW_API_URL", "http://localhost:8000")
        self.api_host = os.getenv("DATAFLOW_API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("DATAFLOW_API_PORT", "8000"))
        
        # Web UI Configuration
        self.ui_port = int(os.getenv("DATAFLOW_UI_PORT", "8501"))
        self.ui_host = os.getenv("DATAFLOW_UI_HOST", "0.0.0.0")
        
        # Spark Configuration
        self.spark_master = os.getenv("SPARK_MASTER", "local[*]")
        self.spark_app_name = os.getenv("SPARK_APP_NAME", "DataFlow")
        self.spark_driver_memory = os.getenv("SPARK_DRIVER_MEMORY", "2g")
        self.spark_executor_memory = os.getenv("SPARK_EXECUTOR_MEMORY", "2g")
        
        # Dataset Storage
        self.dataset_storage_path = os.getenv("DATAFLOW_DATASET_STORAGE_PATH", "./dataflow_datasets")
        
        # Logging Configuration
        self.log_level = os.getenv("DATAFLOW_LOG_LEVEL", "INFO")
        self.log_file = os.getenv("DATAFLOW_LOG_FILE", "./dataflow.log")
    
    def get_spark_config(self) -> dict:
        """Get Spark configuration dictionary"""
        return {
            "spark.master": self.spark_master,
            "spark.app.name": self.spark_app_name,
            "spark.driver.memory": self.spark_driver_memory,
            "spark.executor.memory": self.spark_executor_memory,
            "spark.sql.adaptive.enabled": "true",
            "spark.sql.adaptive.coalescePartitions.enabled": "true",
            "spark.serializer": "org.apache.spark.serializer.KryoSerializer"
        }
    
    def validate(self) -> list:
        """
        Validate configuration and return list of errors
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY is required but not set")
        
        if not self.openai_api_key or self.openai_api_key == "your-openai-api-key-here":
            errors.append("Please set a valid OPENAI_API_KEY in your .env file")
        
        # Validate ports
        if not (1 <= self.api_port <= 65535):
            errors.append(f"Invalid API port: {self.api_port}")
        
        if not (1 <= self.ui_port <= 65535):
            errors.append(f"Invalid UI port: {self.ui_port}")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        return len(self.validate()) == 0
    
    def print_config(self) -> None:
        """Print current configuration (excluding sensitive data)"""
        print("DataFlow Configuration:")
        print(f"  API URL: {self.api_url}")
        print(f"  API Host: {self.api_host}")
        print(f"  API Port: {self.api_port}")
        print(f"  UI Host: {self.ui_host}")
        print(f"  UI Port: {self.ui_port}")
        print(f"  Spark Master: {self.spark_master}")
        print(f"  Spark App Name: {self.spark_app_name}")
        print(f"  Dataset Storage: {self.dataset_storage_path}")
        print(f"  Log Level: {self.log_level}")
        print(f"  OpenAI API Key: {'✓ Set' if self.openai_api_key else '✗ Not set'}")


# Global configuration instance
config = DataFlowConfig()


def get_config() -> DataFlowConfig:
    """Get the global configuration instance"""
    return config


def reload_config(env_file: Optional[str] = None) -> DataFlowConfig:
    """Reload configuration from environment file"""
    global config
    config = DataFlowConfig(env_file)
    return config
