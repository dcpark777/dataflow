#!/usr/bin/env python3
"""
DataFlow Environment Setup Script - Sets up Java 17 environment
"""

import os
import subprocess
import sys
from pathlib import Path


def setup_java_environment():
    """Set up Java 17 environment for DataFlow"""
    print("☕ Setting up Java 17 environment for DataFlow...")
    
    # Check if Java 17 is installed
    java_home = "/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
    java_bin = "/opt/homebrew/opt/openjdk@17/bin"
    
    if not Path(java_home).exists():
        print("❌ Java 17 not found. Installing...")
        try:
            subprocess.run(["brew", "install", "openjdk@17"], check=True)
            print("✅ Java 17 installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Java 17. Please install manually:")
            print("   brew install openjdk@17")
            return False
    else:
        print("✅ Java 17 found!")
    
    # Set environment variables
    os.environ["JAVA_HOME"] = java_home
    os.environ["PATH"] = f"{java_bin}:{os.environ.get('PATH', '')}"
    
    # Verify Java version
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True)
        if "17.0" in result.stderr:
            print("✅ Java 17 is active!")
            return True
        else:
            print("❌ Java 17 is not active. Current version:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error checking Java version: {e}")
        return False


def run_dataflow_command(command):
    """Run a DataFlow command with proper Java environment"""
    if not setup_java_environment():
        print("❌ Failed to set up Java environment")
        return False
    
    print(f"🚀 Running: {command}")
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        return False


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python java_setup.py <command>")
        print("Examples:")
        print("  python java_setup.py 'uv run python mvp_example.py'")
        print("  python java_setup.py 'uv run python start.py ui'")
        print("  python java_setup.py 'uv run dataflow --help'")
        return
    
    command = " ".join(sys.argv[1:])
    success = run_dataflow_command(command)
    
    if success:
        print("✅ Command completed successfully!")
    else:
        print("❌ Command failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
