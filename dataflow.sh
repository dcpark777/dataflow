#!/bin/bash
# DataFlow Simple Commands Script
# Usage: ./dataflow.sh <command>

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Java setup
JAVA_HOME="/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
JAVA_BIN="/opt/homebrew/opt/openjdk@17/bin"

# Function to setup Java environment
setup_java() {
    if [ ! -d "$JAVA_HOME" ]; then
        echo -e "${YELLOW}Installing Java 17...${NC}"
        brew install openjdk@17
    fi
    
    export JAVA_HOME="$JAVA_HOME"
    export PATH="$JAVA_BIN:$PATH"
    
    echo -e "${GREEN}✅ Java 17 is ready!${NC}"
}

# Function to show help
show_help() {
    echo -e "${BLUE}🔄 DataFlow Commands${NC}"
    echo "=================="
    echo ""
    echo -e "${YELLOW}Setup Commands:${NC}"
    echo "  $0 setup      - Initial setup (creates .env file)"
    echo "  $0 install    - Install dependencies"
    echo "  $0 check-java - Check/install Java 17"
    echo ""
    echo -e "${YELLOW}Main Commands:${NC}"
    echo "  $0 example    - Run MVP example (recommended first run)"
    echo "  $0 ui         - Start web UI (http://localhost:8501)"
    echo "  $0 api        - Start API server (http://localhost:8000/docs)"
    echo ""
    echo -e "${YELLOW}CLI Commands:${NC}"
    echo "  $0 cli-help      - Show CLI help"
    echo "  $0 dataset-list  - List datasets"
    echo "  $0 dataset-show <name>  - Show dataset details"
    echo "  $0 job-list      - List transformation jobs"
    echo "  $0 transform <file> <query>  - Transform data"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 example"
    echo "  $0 ui"
    echo "  $0 transform data.csv 'filter age > 30'"
    echo "  $0 dataset-show employees"
}

# Function to run uv command with Java setup
run_dataflow() {
    setup_java
    uv run "$@"
}

# Main command handling
case "${1:-help}" in
    "setup")
        echo -e "${BLUE}🔄 Setting up DataFlow...${NC}"
        python setup.py
        echo -e "${GREEN}✅ Setup complete! Edit .env file and set your OPENAI_API_KEY${NC}"
        echo "Then run: $0 install"
        ;;
    
    "install")
        echo -e "${BLUE}📦 Installing dependencies...${NC}"
        uv sync
        echo -e "${GREEN}✅ Dependencies installed!${NC}"
        ;;
    
    "check-java")
        setup_java
        java -version
        ;;
    
    "example")
        echo -e "${BLUE}🚀 Running DataFlow MVP Example...${NC}"
        run_dataflow python mvp_example.py
        ;;
    
    "ui")
        echo -e "${BLUE}🚀 Starting DataFlow Web UI...${NC}"
        echo -e "${GREEN}🌐 Open http://localhost:8501 in your browser${NC}"
        run_dataflow python start.py ui
        ;;
    
    "api")
        echo -e "${BLUE}🚀 Starting DataFlow API Server...${NC}"
        echo -e "${GREEN}📖 API docs: http://localhost:8000/docs${NC}"
        run_dataflow python start.py api
        ;;
    
    "cli-help")
        run_dataflow dataflow --help
        ;;
    
    "dataset-list")
        run_dataflow dataflow dataset list
        ;;
    
    "dataset-show")
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Please provide dataset name${NC}"
            echo "Usage: $0 dataset-show <dataset_name>"
            exit 1
        fi
        run_dataflow dataflow dataset show "$2"
        ;;
    
    "job-list")
        run_dataflow dataflow job list
        ;;
    
    "transform")
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo -e "${RED}❌ Please provide file and query${NC}"
            echo "Usage: $0 transform <file> <query>"
            exit 1
        fi
        run_dataflow dataflow transform "$2" --query "$3"
        ;;
    
    "test")
        echo -e "${BLUE}🧪 Running tests...${NC}"
        uv run pytest
        ;;
    
    "lint")
        echo -e "${BLUE}🔍 Running linting...${NC}"
        uv run hatch run lint
        ;;
    
    "format")
        echo -e "${BLUE}✨ Formatting code...${NC}"
        uv run hatch run format
        ;;
    
    "clean")
        echo -e "${BLUE}🧹 Cleaning up...${NC}"
        rm -rf __pycache__/ .pytest_cache/ *.log dataflow_datasets/ exported_datasets.json
        echo -e "${GREEN}✅ Cleaned up temporary files${NC}"
        ;;
    
    "status")
        echo -e "${BLUE}🔍 Checking DataFlow status...${NC}"
        if [ -f ".env" ]; then
            echo -e "${GREEN}✅ .env file exists${NC}"
        else
            echo -e "${RED}❌ .env file missing - run '$0 setup'${NC}"
        fi
        
        if [ -d ".venv" ] || command -v uv >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Dependencies installed${NC}"
        else
            echo -e "${RED}❌ Dependencies not installed - run '$0 install'${NC}"
        fi
        
        if [ -d "$JAVA_HOME" ]; then
            echo -e "${GREEN}✅ Java 17 installed${NC}"
        else
            echo -e "${RED}❌ Java 17 not installed - run '$0 check-java'${NC}"
        fi
        ;;
    
    "help"|*)
        show_help
        ;;
esac
