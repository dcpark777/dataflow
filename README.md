# DataFlow MVP

DataFlow is a Python application for natural language data transformations using pyspark-ai. The MVP allows users to represent their datasets in JSON, YAML, or Python dataclass format and define transformations between datasets using natural language.

## 🚀 MVP Features

- **Dataset Definition**: Define datasets using JSON, YAML, or Python dataclass formats
- **Natural Language Transformations**: Define transformations using natural language queries
- **SQL/PySpark Generation**: Automatically converts natural language to SQL and PySpark code
- **Job/Operator System**: Create and execute transformation jobs
- **Web UI**: User-friendly interface for dataset management and transformations
- **REST API**: Complete API for programmatic access
- **Data Validation**: Validate data against defined schemas
- **Export/Import**: Export and import dataset definitions

## Installation

### Prerequisites

- Python 3.9 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- OpenAI API key

### Quick Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd dataflow
```

2. Run the setup script:
```bash
python setup.py
```

3. Edit the `.env` file and set your OpenAI API key:
```bash
# Edit .env file
OPENAI_API_KEY=your-actual-openai-api-key-here
```

4. Install dependencies:
```bash
# Option A (Recommended): Using uv
uv sync

# Option B: Using pip
pip install -e .
```

### Manual Setup

#### Using uv (Recommended)

1. Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository:
```bash
git clone <repository-url>
cd dataflow
```

3. Install dependencies:
```bash
uv sync
```

4. Copy environment template:
```bash
cp env.example .env
```

5. Edit `.env` file and set your OpenAI API key:
```bash
OPENAI_API_KEY=your-actual-openai-api-key-here
```

#### Using pip

1. Clone the repository:
```bash
git clone <repository-url>
cd dataflow
```

2. Install dependencies:
```bash
pip install -e .
```

3. Copy environment template:
```bash
cp env.example .env
```

4. Edit `.env` file and set your OpenAI API key:
```bash
OPENAI_API_KEY=your-actual-openai-api-key-here
```

## 🎯 Quick Start

### **Option 1: Using Taskfile (Recommended)**

Install Task runner:
```bash
# macOS with Homebrew
brew install go-task/tap/go-task

# Or download from: https://taskfile.dev/installation/
```

```bash
# Initial setup
task setup
# Edit .env file and set OPENAI_API_KEY=your-actual-api-key
task install

# Run the application
task example    # MVP example (recommended first run)
task ui         # Web UI (http://localhost:8501)
task api        # API server (http://localhost:8000/docs)
task help       # Show all available commands
```

### **Option 2: Using Shell Script**

```bash
# Initial setup
./dataflow.sh setup
# Edit .env file and set OPENAI_API_KEY=your-actual-api-key
./dataflow.sh install

# Run the application
./dataflow.sh example    # MVP example (recommended first run)
./dataflow.sh ui         # Web UI (http://localhost:8501)
./dataflow.sh api        # API server (http://localhost:8000/docs)
./dataflow.sh help       # Show all available commands
```

### **Option 3: Manual Commands**

```bash
# Setup Java environment
export JAVA_HOME="/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"

# Run the application
uv run python mvp_example.py
uv run python start.py ui
uv run python start.py api
uv run dataflow --help
```

## 📋 **Available Commands**

### **Taskfile Commands** (`task <command>`)
```bash
# Setup
task setup      # Initial setup (creates .env file)
task install    # Install dependencies
task check-java # Check/install Java 17

# Main Commands
task example    # Run MVP example (recommended first run)
task ui         # Start web UI (http://localhost:8501)
task api        # Start API server (http://localhost:8000/docs)

# CLI Commands
task cli-help      # Show CLI help
task dataset-list  # List datasets
task dataset-show  # Show dataset details
task job-list      # List transformation jobs
task transform     # Transform data

# Development
task test      # Run tests
task lint      # Run linting
task format    # Format code

# Utilities
task clean     # Clean temporary files
task status    # Check DataFlow status
task help      # Show all commands
```

### **Shell Script Commands** (`./dataflow.sh <command>`)
```bash
# Same commands as Taskfile, but using ./dataflow.sh instead of task
./dataflow.sh example
./dataflow.sh ui
./dataflow.sh api
./dataflow.sh help
```

## 🐳 **Container Deployment**

DataFlow runs exclusively with Podman for secure, rootless container deployment.

### **Quick Start**

```bash
# 1. Install Podman (if not installed)
# macOS: brew install podman
# Ubuntu: sudo apt install podman
# RHEL/CentOS: sudo dnf install podman

# 2. Set up environment
cp env.container .env
# Edit .env and set your OPENAI_API_KEY

# 3. Start DataFlow
task up

# 4. Access the services
# API: http://localhost:8000/docs
# UI: http://localhost:8501
```

### **Container Commands**

```bash
# Build and start all services
task up

# View logs
task logs

# Stop services
task down

# Rebuild and restart
task build && task up

# Clean up resources
task clean
```

### **Direct Podman Commands**

```bash
# Build and start all services
podman-compose up -d

# View logs
podman-compose logs -f

# Stop services
podman-compose down

# Rebuild and restart
podman-compose up -d --build

# Start only API server
podman-compose up -d dataflow-api

# Start only UI
podman-compose up -d dataflow-ui
```

### **Individual Container Images**

```bash
# Build API server image
podman build -f Containerfile.api -t dataflow-api .

# Build UI image
podman build -f Containerfile.ui -t dataflow-ui .

# Run API server
podman run -p 8000:8000 --env-file .env dataflow-api

# Run UI
podman run -p 8501:8501 --env-file .env dataflow-ui
```

### **Podman Features**

- ✅ **Java 17 included** - No need to install Java separately
- ✅ **Health checks** - Automatic service monitoring
- ✅ **Volume mounting** - Persistent data storage
- ✅ **Network isolation** - Secure service communication
- ✅ **Auto-restart** - Services restart automatically on failure
- ✅ **Environment configuration** - Easy configuration management
- 🔒 **Rootless containers** - Run without root privileges
- 🛡️ **Better security** - No daemon required
- 🔄 **Docker compatibility** - Same commands and images
- 📦 **Pod support** - Native Kubernetes pod support
- 🚀 **Systemd integration** - Better system integration
- 🔧 **No daemon** - No background service required

### **Container Configuration**

DataFlow uses Podman with these configuration files:
- **Containerfiles**: `Containerfile.api` and `Containerfile.ui`
- **Compose file**: `compose.yml`
- **Environment**: `env.container` template
- **API Server**: FastAPI with uvicorn on port 8000
- **UI Server**: Streamlit on port 8501
- **Shared Network**: Services communicate internally
- **Volume Mounts**: Data persistence in `./data` and `./logs`
- **Health Checks**: Automatic service monitoring
- **Rootless**: Runs without root privileges
- **No Daemon**: No background service required

## 🔧 Configuration

### Environment Variables

DataFlow uses a `.env` file for configuration. Copy `env.example` to `.env` and customize:

#### Required Variables
- `OPENAI_API_KEY`: Required for natural language processing

#### Optional Variables
- `DATAFLOW_API_URL`: API base URL for web UI (default: http://localhost:8000)
- `DATAFLOW_API_HOST`: API server host (default: 0.0.0.0)
- `DATAFLOW_API_PORT`: API server port (default: 8000)
- `DATAFLOW_UI_PORT`: Web UI port (default: 8501)
- `DATAFLOW_UI_HOST`: Web UI host (default: 0.0.0.0)
- `SPARK_MASTER`: Spark master URL (default: local[*])
- `SPARK_APP_NAME`: Spark application name (default: DataFlow)
- `SPARK_DRIVER_MEMORY`: Spark driver memory (default: 2g)
- `SPARK_EXECUTOR_MEMORY`: Spark executor memory (default: 2g)
- `DATAFLOW_DATASET_STORAGE_PATH`: Dataset storage path (default: ./dataflow_datasets)
- `DATAFLOW_LOG_LEVEL`: Logging level (default: INFO)
- `DATAFLOW_LOG_FILE`: Log file path (default: ./dataflow.log)

### Configuration Management

The configuration is managed by the `DataFlowConfig` class:

```python
from dataflow.config import get_config

config = get_config()
print(f"API URL: {config.api_url}")
print(f"OpenAI API Key: {'✓ Set' if config.openai_api_key else '✗ Not set'}")

# Validate configuration
if not config.is_valid():
    for error in config.validate():
        print(f"Error: {error}")
```

### Spark Configuration

DataFlow uses PySpark with optimized default configurations:
- Adaptive query execution enabled
- Coalesce partitions enabled
- Kryo serializer
- Configurable memory settings

You can customize Spark configuration by modifying the `.env` file or passing `spark_config` to the DataFlow constructor.

## 🛠️ Troubleshooting

### Common Issues

#### 1. `uv sync` Dependency Conflicts
If you encounter dependency resolution errors with `uv sync`:

```bash
# Check for dependency conflicts
uv sync --verbose

# If pydantic conflicts occur, the issue is already fixed in pyproject.toml
# pyspark-ai requires pydantic<2.0.0, which is now properly specified
```

#### 2. OpenAI API Key Not Set
```bash
# Check if API key is set
uv run python -c "from dataflow.config import get_config; print('API Key:', '✓ Set' if get_config().openai_api_key else '✗ Not set')"

# If not set, edit .env file
echo "OPENAI_API_KEY=your-actual-api-key-here" >> .env
```

#### 3. Import Errors
```bash
# Test imports
uv run python -c "from dataflow import DataFlow; print('✓ DataFlow imported successfully')"

# If errors occur, reinstall
uv sync --reinstall
```

#### 4. Java Version Issues
If you get Java-related errors:
```
java.lang.UnsupportedClassVersionError: org/apache/spark/launcher/Main has been compiled by a more recent version of the Java Runtime
```

**Solution**: Install Java 17+ (PySpark 3.4+ requires Java 17+)

```bash
# Install Java 17 (macOS with Homebrew)
brew install openjdk@17

# Set environment variables
export JAVA_HOME="/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"

# Verify Java version
java -version  # Should show Java 17+

# Run DataFlow with Java 17
uv run python mvp_example.py
```

**Easy Setup**: Use the provided Java setup script:
```bash
python java_setup.py "uv run python mvp_example.py"
```

#### 5. LangChain Deprecation Warnings
These warnings are normal and don't affect functionality:
```
LangChainDeprecationWarning: Importing GoogleSearchAPIWrapper from langchain.utilities is deprecated
```
The warnings come from `pyspark-ai` dependencies and can be safely ignored.

### Alternative Installation Methods

If `uv sync` continues to have issues:

```bash
# Method 1: Use pip with virtual environment
python -m venv dataflow-env
source dataflow-env/bin/activate  # On Windows: dataflow-env\Scripts\activate
pip install -e .

# Method 2: Use pip without virtual environment
pip install -e . --user
```

## 📖 MVP Components

### Dataset Management
- **DatasetDefinition**: Define schemas with fields, types, and validation rules
- **DatasetRegistry**: Store and manage dataset definitions
- **Multiple Formats**: Support for JSON, YAML, and Python dataclass definitions
- **Data Validation**: Validate data against defined schemas

### Transformation Engine
- **NaturalLanguageProcessor**: Convert natural language to SQL/PySpark
- **TransformationJob**: Manage multi-step transformation pipelines
- **TransformationStep**: Individual transformation operations
- **Job Execution**: Execute complete transformation workflows

### Web Interface
- **Streamlit UI**: User-friendly web interface for dataset and job management
- **REST API**: Complete API for programmatic access
- **Real-time Execution**: Execute transformations and view results

### Examples

Run the included examples to see DataFlow in action:

```bash
# Run the comprehensive MVP example
python mvp_example.py

# Run additional examples
python examples.py
```

## Command Line Interface

DataFlow includes a command-line interface for quick data transformations:

```bash
# Show help
dataflow --help

# Load data and show sample
dataflow data.csv --show-sample 10

# Apply transformation and save result
dataflow data.csv --query "Filter rows where age > 30" --output filtered_data.csv

# Show data schema
dataflow data.csv --show-schema

# Get natural language description
dataflow data.csv --describe
```

The examples demonstrate:
- Basic transformations (filtering, grouping, sorting)
- Sales data analysis
- Data cleaning operations
- Advanced analytics and customer segmentation

## API Reference

### DataFlow Class

#### `__init__(openai_api_key=None, spark_config=None)`
Initialize DataFlow with optional OpenAI API key and Spark configuration.

#### `load_data(source, format="auto", **kwargs)`
Load data from various sources:
- File paths (CSV, JSON, Parquet)
- pandas DataFrames
- Python lists of dictionaries

#### `transform(df, natural_language_query)`
Apply natural language transformations to a DataFrame.

#### `show_schema(df)`
Display the schema of a DataFrame.

#### `show_sample(df, n=20)`
Display a sample of the DataFrame.

#### `describe_data(df)`
Provide a natural language description of the data.

#### `save_data(df, output_path, format="csv", **kwargs)`
Save DataFrame to various formats.

#### `stop()`
Stop the Spark session.

## Natural Language Queries

DataFlow supports a wide variety of natural language queries for data transformations:

### Filtering
- "Filter rows where age is greater than 30"
- "Keep only records where city equals 'New York'"
- "Remove rows where salary is null"

### Grouping and Aggregation
- "Group by department and calculate average salary"
- "Group by city and count the number of records"
- "Group by category and sum the total revenue"

### Column Operations
- "Add a new column called 'age_group' that categorizes age as 'young' for age < 30, 'middle' for age 30-35, and 'senior' for age > 35"
- "Create a column 'full_name' that concatenates first_name and last_name"
- "Calculate a new column 'total_cost' as price * quantity"

### Sorting and Selection
- "Sort by salary in descending order"
- "Select only name, department, and salary columns"
- "Order by date ascending"

### Data Cleaning
- "Remove duplicate rows"
- "Fill null values in the age column with the average age"
- "Convert the date column to proper date format"

## Development

### Setting up development environment

```bash
# Install with development dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run linting
uv run hatch run lint

# Format code
uv run hatch run format

# Run all checks
uv run hatch run check
```

### Project structure

```
dataflow/
├── dataflow/           # Main package
│   ├── __init__.py     # Main DataFlow class
│   └── cli.py          # Command-line interface
├── examples.py         # Example usage
├── pyproject.toml      # Project configuration
├── uv.lock            # Dependency lock file
└── README.md          # This file
```

## Requirements

- Python 3.9+
- PySpark 4.0.1+
- pyspark-ai 0.1.21+
- OpenAI API key

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
