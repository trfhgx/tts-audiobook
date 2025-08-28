#!/usr/bin/env python3
"""
Audiobook Studio Runner
Starts both backend and frontend servers
"""

import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def run_backend():
    """Start the Python backend"""
    print("Starting Python backend...")
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    backend_dir = script_dir / "backend"
    venv_activate = backend_dir / "venv" / "bin" / "activate"
    
    # Require virtual environment
    if not venv_activate.exists():
        print("❌ Virtual environment not found!")
        print("Please run 'python3 setup.py' first to create the virtual environment.")
        sys.exit(1)
    
    print("Using virtual environment")
    # Create command that activates venv and runs the backend
    cmd = f"source {venv_activate} && python backend.py"
    return subprocess.Popen(cmd, shell=True, cwd=str(backend_dir))

def run_frontend():
    """Start the Next.js frontend"""
    print("Starting Next.js frontend...")
    return subprocess.Popen(["npm", "run", "dev"])

def main():
    """Main runner function"""
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Check if .env.local exists and has a model configured
    env_file = Path(".env.local")
    if not env_file.exists():
        print("Please run setup.py first!")
        return
    
    content = env_file.read_text()
    if "ANNOTATION_MODEL=" not in content or content.split("ANNOTATION_MODEL=")[1].split()[0] == "":
        print("Please run setup.py first to configure the annotation model!")
        return
    
    print("Starting Audiobook Studio...")
    print("Press Ctrl+C to stop both servers")
    
    # Start both processes
    backend_process = run_backend()
    time.sleep(2)  # Give backend time to start
    frontend_process = run_frontend()
    
    def signal_handler(sig, frame):
        print("\nStopping servers...")
        backend_process.terminate()
        frontend_process.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Wait for both processes
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
