# DataFlow MVP

DataFlow is a containerized Python application for natural language data transformations using pyspark-ai. The MVP allows users to represent their datasets in JSON, YAML, or Python dataclass format and define transformations between datasets using natural language.

## 🚀 MVP Features

- **Dataset Definition**: Define datasets using JSON, YAML, or Python dataclass formats
- **Natural Language Transformations**: Define transformations using natural language queries
- **SQL/PySpark Generation**: Automatically converts natural language to SQL and PySpark code
- **Job/Operator System**: Create and execute transformation jobs
- **Web UI**: User-friendly interface for dataset management and transformations
- **REST API**: Complete API for programmatic access
- **Containerized Deployment**: Runs exclusively with Podman for secure, rootless containers

## 🐳 Quick Start

DataFlow runs exclusively with Podman for secure, rootless container deployment.

### Prerequisites

- [Podman](https://podman.io/) installed
- OpenAI API key

### Installation

1. **Install Podman** (if not installed):
   ```bash
   # macOS
   brew install podman
   
   # Ubuntu/Debian
   sudo apt install podman
   
   # RHEL/CentOS
   sudo dnf install podman
   ```

2. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd dataflow
   cp env.example .env
   ```

3. **Configure environment**:
   ```bash
   # Edit .env and set your OpenAI API key
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Start DataFlow**:
   ```bash
   task up
   ```

5. **Access the services**:
   - **API**: http://localhost:8000/docs
   - **UI**: http://localhost:8501

## 🎯 Available Commands

```bash
# Container Commands
task up          # Start DataFlow services
task down        # Stop DataFlow services
task logs        # View service logs
task restart     # Restart services
task clean       # Clean container resources
task kill-local  # Kill local DataFlow processes

# Utilities
task help        # Show available commands
```

## 🔧 Configuration

### Environment Variables

Copy `env.example` to `.env` and customize:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# API Configuration
DATAFLOW_API_HOST=0.0.0.0
DATAFLOW_API_PORT=8000
DATAFLOW_API_URL=http://localhost:8000

# UI Configuration
DATAFLOW_UI_HOST=0.0.0.0
DATAFLOW_UI_PORT=8501
DATAFLOW_UI_URL=http://localhost:8501

# Spark Configuration
SPARK_APP_NAME=DataFlow
SPARK_MASTER=local[*]
SPARK_DRIVER_MEMORY=2g
SPARK_EXECUTOR_MEMORY=2g
```

## 🏗️ Architecture

### Components

- **API Server**: FastAPI-based REST API (port 8000)
- **Web UI**: Streamlit-based user interface (port 8501)
- **Transformation Engine**: Natural language to SQL/PySpark conversion
- **Dataset Registry**: Dataset definition and management
- **Job System**: Transformation job execution

### Container Structure

```
dataflow/
├── Containerfile.api    # API server container
├── Containerfile.ui     # UI container
├── compose.yml          # Podman compose configuration
├── dataflow/            # Core application code
│   ├── api.py          # FastAPI server
│   ├── ui.py           # Streamlit UI
│   ├── dataset.py      # Dataset definitions
│   ├── transformation.py # Transformation engine
│   └── config.py       # Configuration management
└── Taskfile.yml        # Task runner commands
```

## 💾 Dataset Storage

When you create datasets in the UI, they are stored persistently in the `./data/datasets/` directory on your host machine. This directory is mounted into the container, so your datasets will persist even when containers are restarted.

### Storage Structure

```
data/
├── datasets/           # Dataset definitions (JSON files)
├── exports/            # Exported datasets
└── imports/            # Imported datasets
```

### Dataset Persistence

- ✅ **Datasets persist** across container restarts
- ✅ **Automatic saving** when datasets are created/modified
- ✅ **JSON format** for easy backup and version control
- ✅ **Host-mounted** storage for easy access

## 🛡️ Podman Features

- ✅ **Java 21 included** - No need to install Java separately
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

## 🚨 Troubleshooting

### Common Issues

1. **Podman machine not initialized**:
   ```bash
   podman machine init
   podman machine start
   ```

2. **Port conflicts**:
   ```bash
   task kill-local  # Kill any local processes
   task down        # Stop containers
   task up          # Restart
   ```

3. **Missing OpenAI API key**:
   - Ensure `.env` file exists with `OPENAI_API_KEY` set
   - Restart services: `task restart`

4. **Container build failures**:
   ```bash
   task clean       # Clean up resources
   task build       # Rebuild images
   task up          # Start services
   ```

## 📝 Development

### Project Structure

```
dataflow/
├── dataflow/           # Core application
│   ├── __init__.py    # Main DataFlow class
│   ├── api.py         # FastAPI server
│   ├── ui.py          # Streamlit UI
│   ├── dataset.py     # Dataset definitions
│   ├── transformation.py # Transformation engine
│   ├── config.py      # Configuration
│   └── cli.py         # CLI interface
├── Containerfile.api  # API container definition
├── Containerfile.ui   # UI container definition
├── compose.yml        # Podman compose
├── Taskfile.yml       # Task runner
├── pyproject.toml     # Python dependencies
└── README.md          # This file
```

### Adding Features

1. **Modify core logic** in `dataflow/` directory
2. **Update containers** if dependencies change
3. **Test with containers**: `task restart`
4. **Update documentation** as needed

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.