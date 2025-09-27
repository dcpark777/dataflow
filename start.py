#!/usr/bin/env python3
"""
DataFlow Startup Script - Easy way to start different DataFlow components
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path

# Import DataFlow configuration
from dataflow.config import get_config


def start_api_server(host=None, port=None):
    """Start the FastAPI server"""
    config = get_config()
    host = host or config.api_host
    port = port or config.api_port
    
    print(f"🚀 Starting DataFlow API server on {host}:{port}")
    print(f"📖 API documentation available at: http://localhost:{port}/docs")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "dataflow.api:app", 
            "--host", host, 
            "--port", str(port),
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 API server stopped")


def start_web_ui(port=None):
    """Start the Streamlit web UI"""
    config = get_config()
    port = port or config.ui_port
    
    print(f"🚀 Starting DataFlow Web UI on port {port}")
    print(f"🌐 Web UI available at: http://localhost:{port}")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "dataflow/ui.py", 
            "--server.port", str(port),
            "--server.address", config.ui_host
        ])
    except KeyboardInterrupt:
        print("\n🛑 Web UI stopped")


def run_example():
    """Run the MVP example"""
    print("🚀 Running DataFlow MVP Example")
    
    try:
        subprocess.run([sys.executable, "mvp_example.py"])
    except KeyboardInterrupt:
        print("\n🛑 Example stopped")


def check_requirements():
    """Check if all requirements are installed"""
    print("🔍 Checking requirements...")
    
    required_packages = [
        "pyspark", "pyspark-ai", "pandas", "numpy", 
        "pyyaml", "fastapi", "uvicorn", "streamlit", "pydantic"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            # Handle special cases for package names
            import_name = package.replace("-", "_")
            if package == "pyyaml":
                import_name = "yaml"
            __import__(import_name)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All requirements satisfied!")
    return True


def check_api_key():
    """Check if OpenAI API key is set"""
    config = get_config()
    
    if not config.openai_api_key:
        print("❌ OPENAI_API_KEY is not set")
        print("Please set your OpenAI API key in .env file:")
        print("OPENAI_API_KEY=your-api-key-here")
        return False
    
    if config.openai_api_key == "your-openai-api-key-here":
        print("❌ Please set a valid OPENAI_API_KEY in your .env file")
        return False
    
    print("✅ OpenAI API key is set")
    return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="DataFlow Startup Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start.py api                    # Start API server
  python start.py ui                     # Start web UI
  python start.py example                # Run MVP example
  python start.py check                  # Check requirements
  python start.py api --port 8080        # Start API on custom port
  python start.py ui --port 8502         # Start UI on custom port
        """
    )
    
    parser.add_argument(
        "command",
        choices=["api", "ui", "example", "check"],
        help="Command to run"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        help="Port to bind to (default: 8000 for API, 8501 for UI)"
    )
    
    args = parser.parse_args()
    
    print("🔄 DataFlow Startup Script")
    print("=" * 40)
    
    # Check requirements for all commands except check
    if args.command != "check":
        if not check_requirements():
            sys.exit(1)
        
        # Check API key for commands that need it
        if args.command in ["api", "ui", "example"]:
            if not check_api_key():
                sys.exit(1)
    
    # Execute command
    if args.command == "api":
        port = args.port or 8000
        start_api_server(args.host, port)
    
    elif args.command == "ui":
        port = args.port or 8501
        start_web_ui(port)
    
    elif args.command == "example":
        run_example()
    
    elif args.command == "check":
        check_requirements()
        check_api_key()


if __name__ == "__main__":
    main()
