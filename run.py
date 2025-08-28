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
    return subprocess.Popen([sys.executable, "backend.py"])

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
