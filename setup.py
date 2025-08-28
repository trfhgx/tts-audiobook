#!/usr/bin/env python3
"""
Audiobook Studio Setup Script
Handles Ollama model selection and Dia TTS setup
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def run_command(cmd, capture_output=True, check=True):
    """Run a shell command"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True, check=check)
        return result.stdout.strip() if capture_output else None
    except subprocess.CalledProcessError as e:
        if capture_output:
            print(f"Error running command: {cmd}")
            print(f"Error: {e.stderr}")
        return None

def check_ollama():
    """Check if Ollama is installed"""
    return run_command("which ollama", check=False) is not None

def get_ollama_models():
    """Get list of installed Ollama models"""
    if not check_ollama():
        return []
    
    result = run_command("ollama list", check=False)
    if not result:
        return []
    
    models = []
    lines = result.split('\n')[1:]  # Skip header
    for line in lines:
        if line.strip():
            model_name = line.split()[0]
            if model_name != "NAME":
                models.append(model_name)
    
    return models

def install_ollama_model(model_name):
    """Install an Ollama model"""
    print(f"Installing {model_name}...")
    result = run_command(f"ollama pull {model_name}", capture_output=False, check=False)
    return result is not None

def select_model():
    """Interactive model selection"""
    print("\n=== Audiobook Studio Setup ===\n")
    
    if not check_ollama():
        print("Ollama is not installed. Please install it first:")
        print("https://ollama.ai")
        return None
    
    models = get_ollama_models()
    
    print("Available local models:")
    if models:
        for i, model in enumerate(models, 1):
            print(f"  {i}. {model}")
        print(f"  {len(models) + 1}. Install a new model")
    else:
        print("  No models found")
        print("  1. Install a new model")
    
    print()
    
    # Recommended models for text annotation
    recommended = [
        "llama3.2:1b",      # Very small and fast
        "llama3.2:3b",      # Small and good quality
        "phi3:mini",        # Microsoft's small model
        "qwen2:1.5b",       # Alibaba's small model
        "tinyllama:1.1b"    # Tiny model for basic tasks
    ]
    
    if not models or input("Select option (number): ").strip() == str(len(models) + 1 if models else 1):
        print("\nRecommended models for text annotation:")
        for i, model in enumerate(recommended, 1):
            print(f"  {i}. {model}")
        
        try:
            choice = int(input("Select model to install (number): ")) - 1
            if 0 <= choice < len(recommended):
                model_name = recommended[choice]
                if install_ollama_model(model_name):
                    return model_name
                else:
                    print("Failed to install model")
                    return None
            else:
                print("Invalid selection")
                return None
        except ValueError:
            print("Invalid input")
            return None
    else:
        try:
            choice = int(input("Select model (number): ")) - 1
            if 0 <= choice < len(models):
                return models[choice]
            else:
                print("Invalid selection")
                return None
        except ValueError:
            print("Invalid input")
            return None

def update_env_file(model_name):
    """Update .env.local with selected model"""
    env_file = Path(".env.local")
    
    if env_file.exists():
        content = env_file.read_text()
        # Update the ANNOTATION_MODEL line
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('ANNOTATION_MODEL='):
                lines[i] = f'ANNOTATION_MODEL={model_name}'
                break
        else:
            lines.append(f'ANNOTATION_MODEL={model_name}')
        
        env_file.write_text('\n'.join(lines))
    else:
        env_file.write_text(f'ANNOTATION_MODEL={model_name}\nPYTHON_BACKEND_URL=http://localhost:8000\n')

def setup_dia_tts():
    """Setup Dia TTS from the GitHub repo"""
    print("\nSetting up Dia TTS...")
    
    if not Path("dia").exists():
        print("Cloning Dia TTS repository...")
        if run_command("git clone https://github.com/nari-labs/dia.git", capture_output=False, check=False) is None:
            print("Failed to clone Dia repository")
            return False
    
    print("Dia TTS repository ready")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling Python dependencies...")
    if run_command("pip install -r requirements.txt", capture_output=False, check=False) is None:
        print("Failed to install dependencies")
        return False
    return True

def main():
    """Main setup function"""
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Select annotation model
    model = select_model()
    if not model:
        print("Setup cancelled")
        return
    
    print(f"\nSelected model: {model}")
    update_env_file(model)
    
    # Setup Dia TTS
    if not setup_dia_tts():
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    print("\n✅ Setup complete!")
    print("\nTo start the application:")
    print("  python3 run.py")
    print("\nOr separately:")
    print("  Terminal 1: python3 backend.py")
    print("  Terminal 2: npm run dev")

if __name__ == "__main__":
    main()
