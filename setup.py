#!/usr/bin/env python3
"""
DataFlow Setup Script - Helps users set up their environment
"""

import os
import shutil
from pathlib import Path


def setup_environment():
    """Set up the DataFlow environment"""
    print("🔄 DataFlow Environment Setup")
    print("=" * 40)
    
    # Check if .env file exists
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("📝 Creating .env file from template...")
            shutil.copy(env_example, env_file)
            print("✅ Created .env file")
            print("\n⚠️  IMPORTANT: Please edit .env file and set your OpenAI API key:")
            print("   OPENAI_API_KEY=your-actual-api-key-here")
        else:
            print("❌ env.example file not found. Creating basic .env file...")
            create_basic_env_file()
    else:
        print("✅ .env file already exists")
    
    # Check if .gitignore exists
    gitignore_file = Path(".gitignore")
    if not gitignore_file.exists():
        print("📝 Creating .gitignore file...")
        create_gitignore_file()
        print("✅ Created .gitignore file")
    else:
        print("✅ .gitignore file already exists")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file and set your OpenAI API key")
    print("2. Install dependencies:")
    print("   Option A (Recommended): uv sync")
    print("   Option B: pip install -e .")
    print("3. Run the example:")
    print("   Option A: uv run python mvp_example.py")
    print("   Option B: python mvp_example.py")


def create_basic_env_file():
    """Create a basic .env file"""
    env_content = """# DataFlow Environment Configuration
# Copy this file to .env and fill in your actual values

# OpenAI API Key (required for natural language processing)
OPENAI_API_KEY=your-openai-api-key-here

# DataFlow API Configuration
DATAFLOW_API_URL=http://localhost:8000
DATAFLOW_API_HOST=0.0.0.0
DATAFLOW_API_PORT=8000

# Web UI Configuration
DATAFLOW_UI_PORT=8501
DATAFLOW_UI_HOST=0.0.0.0

# Spark Configuration (optional)
SPARK_MASTER=local[*]
SPARK_APP_NAME=DataFlow
SPARK_DRIVER_MEMORY=2g
SPARK_EXECUTOR_MEMORY=2g

# Dataset Storage (optional)
DATAFLOW_DATASET_STORAGE_PATH=./dataflow_datasets

# Logging Configuration (optional)
DATAFLOW_LOG_LEVEL=INFO
DATAFLOW_LOG_FILE=./dataflow.log
"""
    
    with open(".env", "w") as f:
        f.write(env_content)


def create_gitignore_file():
    """Create a .gitignore file"""
    gitignore_content = """# Environment variables
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# DataFlow specific
dataflow_datasets/
*.log
dataflow.log
exported_datasets.json
temp_data/
output/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Spark
spark-warehouse/
metastore_db/
derby.log

# Temporary files
*.tmp
*.temp
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)


def main():
    """Main setup function"""
    setup_environment()


if __name__ == "__main__":
    main()
