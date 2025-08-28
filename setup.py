#!/usr/bin/env python3
"""
Audiobook Studio Setup Script
Interactive setup with user confirmation for each step
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
            print(f"❌ Error running command: {cmd}")
            print(f"Error: {e.stderr}")
        return None

def ask_yes_no(question, default="y"):
    """Ask a yes/no question with default"""
    choices = "[Y/n]" if default.lower() == "y" else "[y/N]"
    while True:
        answer = input(f"{question} {choices}: ").strip().lower()
        if not answer:
            return default.lower() == "y"
        if answer in ['y', 'yes']:
            return True
        if answer in ['n', 'no']:
            return False
        print("Please answer 'y' or 'n'")

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
    """Install an Ollama model with confirmation"""
    print(f"\n📦 About to install Ollama model: {model_name}")
    print(f"This will download and install the model (may take several minutes)")
    
    if not ask_yes_no("Do you want to proceed with installation?"):
        return False
        
    print(f"Installing {model_name}...")
    try:
        # Run ollama pull command
        result = subprocess.run(f"ollama pull {model_name}", shell=True, check=True)
        print(f"✅ Successfully installed {model_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {model_name}")
        print(f"Error: {e}")
        return False

def select_annotation_model():
    """Interactive model selection for text annotation"""
    print("\n🤖 TEXT ANNOTATION MODEL SETUP")
    print("=" * 50)
    
    if not check_ollama():
        print("❌ Ollama is not installed.")
        print("Ollama is required for local AI text annotation.")
        print("Install from: https://ollama.ai")
        
        if ask_yes_no("Do you want to continue without text annotation?"):
            return "none"
        else:
            return None
    
    print("✅ Ollama is installed")
    models = get_ollama_models()
    
    print(f"\n📋 Currently installed models: {len(models)}")
    if models:
        for i, model in enumerate(models, 1):
            print(f"  {i}. {model}")
    else:
        print("  No models found")
    
    # Recommended models for text annotation
    recommended = [
        ("llama3.2:1b", "Very small and fast (1.3GB)"),
        ("llama3.2:3b", "Small with good quality (2GB)"),
        ("phi3:mini", "Microsoft's efficient model (2.3GB)"),
        ("qwen2:1.5b", "Alibaba's compact model (934MB)"),
        ("tinyllama:1.1b", "Tiny model for basic tasks (637MB)")
    ]
    
    print(f"\n🎯 Recommended models for text annotation:")
    for i, (model, desc) in enumerate(recommended, 1):
        installed = "✅" if model in models else "📦"
        print(f"  {i}. {installed} {model} - {desc}")
    
    print("\nOptions:")
    if models:
        print("  A. Use an existing installed model")
    print("  B. Install a new recommended model")
    print("  C. Skip text annotation (manual mode)")
    
    while True:
        choice = input("\nSelect option (A/B/C): ").strip().upper()
        
        if choice == "A" and models:
            print(f"\nInstalled models:")
            for i, model in enumerate(models, 1):
                print(f"  {i}. {model}")
            
            try:
                model_choice = int(input("Select model number: ")) - 1
                if 0 <= model_choice < len(models):
                    selected = models[model_choice]
                    print(f"Selected: {selected}")
                    return selected
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Invalid input")
                
        elif choice == "B":
            print(f"\nRecommended models:")
            for i, (model, desc) in enumerate(recommended, 1):
                print(f"  {i}. {model} - {desc}")
            
            try:
                model_choice = int(input("Select model to install (number): ")) - 1
                if 0 <= model_choice < len(recommended):
                    model_name = recommended[model_choice][0]
                    if install_ollama_model(model_name):
                        return model_name
                    else:
                        print("Installation failed. Try another model or skip.")
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Invalid input")
                
        elif choice == "C":
            print("⚠️  Skipping text annotation setup")
            return "none"
        else:
            print("❌ Invalid option. Please choose A, B, or C")

def setup_dia_tts():
    """Setup Dia TTS from the GitHub repo with confirmation"""
    print("\n🎵 DIA TTS SETUP")
    print("=" * 30)
    
    # Step 1: Clone/update repository
    if Path("dia").exists():
        print("✅ Dia TTS repository already exists")
        if ask_yes_no("Do you want to update it?"):
            print("Updating Dia TTS repository...")
            os.chdir("dia")
            try:
                result = subprocess.run(["git", "pull"], capture_output=True, text=True, check=True)
                os.chdir("..")
                if "Already up to date" in result.stdout or "Fast-forward" in result.stdout:
                    print("✅ Dia TTS repository updated")
                else:
                    print("✅ Dia TTS repository updated")
            except subprocess.CalledProcessError as e:
                os.chdir("..")
                print(f"❌ Failed to update Dia TTS: {e}")
                return False
    else:
        print("📦 Dia TTS repository not found")
        print("This will clone the Dia TTS repository from GitHub")
        print("Repository: https://github.com/nari-labs/dia.git")
        print("Note: This contains the Dia TTS code and interface")
        
        if ask_yes_no("Do you want to clone Dia TTS repository?"):
            print("Cloning Dia TTS repository...")
            try:
                subprocess.run(["git", "clone", "https://github.com/nari-labs/dia.git"], check=True)
                print("✅ Successfully cloned Dia TTS repository")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to clone Dia repository: {e}")
                return False
        else:
            print("⚠️  Skipping Dia TTS setup")
            return False
    
    # Step 2: Download TTS model weights
    print("\n📥 DIA TTS MODEL DOWNLOAD")
    print("=" * 40)
    print("The Dia TTS model weights need to be downloaded from HuggingFace")
    print("Model: nari-labs/Dia-1.6B-0626")
    print("Size: ~6.4GB (this will take time depending on your internet)")
    print("This enables high-quality text-to-speech generation")
    print("")
    print("The model will be saved to ./models/dia-tts/ in this project")
    
    if ask_yes_no("Do you want to download the Dia TTS model?"):
        print("Downloading Dia TTS model... (this may take 10-30 minutes)")
        
        # Use Python to download the model
        download_script = '''
import sys
import os
from pathlib import Path
try:
    from transformers import DiaForConditionalGeneration, AutoProcessor
    
    # Create models directory
    models_dir = Path("models/dia-tts")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print("🔄 Downloading Dia TTS model and processor...")
    print(f"📁 Saving to: {models_dir.absolute()}")
    model_name = "nari-labs/Dia-1.6B-0626"
    
    # Download processor first (includes tokenizer and audio configs)
    print("📝 Downloading processor (tokenizer + audio configs)...")
    processor = AutoProcessor.from_pretrained(
        model_name, 
        cache_dir=str(models_dir)
    )
    print("✅ Processor downloaded")
    
    # Download model to local directory
    print("🎵 Downloading Dia TTS model (this will take a while)...")
    print("Progress will be shown below:")
    model = DiaForConditionalGeneration.from_pretrained(
        model_name, 
        cache_dir=str(models_dir)
    )
    print("✅ Model downloaded successfully")
    print(f"📁 Model saved to: {models_dir.absolute()}")
    print("🎉 Dia TTS is ready to use!")
    
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Please ensure transformers is installed")
    sys.exit(1)
except Exception as e:
    print(f"❌ Failed to download model: {e}")
    sys.exit(1)
'''
        
        try:
            # Run the download in the virtual environment
            venv_python = Path("backend/venv/bin/python")
            if venv_python.exists():
                with open("temp_download.py", "w") as f:
                    f.write(download_script)
                
                subprocess.run([str(venv_python), "temp_download.py"], check=True)
                os.remove("temp_download.py")
                print("✅ Dia TTS model downloaded successfully")
                return True
            else:
                print("❌ Virtual environment not found. Please run virtual environment setup first.")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to download Dia TTS model: {e}")
            if os.path.exists("temp_download.py"):
                os.remove("temp_download.py")
            return False
    else:
        print("⚠️  Skipping Dia TTS model download")
        print("Note: TTS will not work without the model")
        return True  # Repository setup still succeeded

def create_virtual_environment():
    """Create and setup virtual environment"""
    print("\n🐍 PYTHON VIRTUAL ENVIRONMENT")
    print("=" * 45)
    
    venv_path = Path("backend/venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        if ask_yes_no("Do you want to recreate it?"):
            print("Removing existing virtual environment...")
            import shutil
            shutil.rmtree(venv_path)
        else:
            return True
    
    print("Creating Python virtual environment...")
    print(f"Location: {venv_path}")
    
    if ask_yes_no("Do you want to create a virtual environment?"):
        try:
            result = subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
            print("✅ Successfully created virtual environment")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    else:
        print("⚠️  Skipping virtual environment creation")
        return False

def install_dependencies():
    """Install Python dependencies with virtual environment"""
    print("\n📚 PYTHON DEPENDENCIES")
    print("=" * 35)
    
    venv_path = Path("backend/venv")
    
    if not venv_path.exists():
        print("❌ Virtual environment not found")
        if ask_yes_no("Do you want to create it now?"):
            if not create_virtual_environment():
                return False
        else:
            return False
    
    # Determine pip path based on OS
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip"
        python_path = venv_path / "Scripts" / "python"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    print("Required Python packages:")
    print("  - fastapi (web framework)")
    print("  - torch (PyTorch for AI)")
    print("  - torchaudio (audio processing)")
    print("  - transformers (AI models)")
    print("  - requests (HTTP client)")
    print("  - uvicorn (web server)")
    print(f"\nUsing virtual environment: {venv_path}")
    
    if ask_yes_no("Do you want to install Python dependencies?"):
        print("Installing Python dependencies in virtual environment...")
        try:
            # Upgrade pip first
            subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
            print("✅ Upgraded pip")
            
            # Install requirements
            subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
            print("✅ Successfully installed Python dependencies")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    else:
        print("⚠️  Skipping Python dependencies")
        return False

def install_node_dependencies():
    """Install Node.js dependencies with confirmation"""
    print("\n📦 NODE.JS DEPENDENCIES")
    print("=" * 35)
    
    if not Path("package.json").exists():
        print("❌ package.json not found")
        return False
        
    print("Required Node.js packages:")
    print("  - Next.js (React framework)")
    print("  - TypeScript (type safety)")
    print("  - Tailwind CSS (styling)")
    print("  - Framer Motion (animations)")
    
    if ask_yes_no("Do you want to install Node.js dependencies?"):
        print("Installing Node.js dependencies...")
        try:
            subprocess.run(["npm", "install"], check=True)
            print("✅ Successfully installed Node.js dependencies")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Node.js dependencies: {e}")
            return False
    else:
        print("⚠️  Skipping Node.js dependencies")
        return False

def update_env_file(model_name):
    """Update .env.local with selected model"""
    print("\n⚙️  CONFIGURATION")
    print("=" * 25)
    
    env_file = Path(".env.local")
    
    config_info = f"""
Configuration to be written to .env.local:
  ANNOTATION_MODEL={model_name}
  PYTHON_BACKEND_URL=http://localhost:8000
"""
    print(config_info)
    
    if ask_yes_no("Do you want to create/update the configuration file?"):
        if env_file.exists():
            content = env_file.read_text()
            lines = content.split('\n')
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('ANNOTATION_MODEL='):
                    lines[i] = f'ANNOTATION_MODEL={model_name}'
                    updated = True
                    break
            if not updated:
                lines.append(f'ANNOTATION_MODEL={model_name}')
            env_file.write_text('\n'.join(lines))
        else:
            env_file.write_text(f'ANNOTATION_MODEL={model_name}\nPYTHON_BACKEND_URL=http://localhost:8000\n')
        
        print("✅ Configuration updated")
        return True
    else:
        print("⚠️  Skipping configuration")
        return False

def main():
    """Main setup function with step-by-step confirmation"""
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    print("🚀 AUDIOBOOK STUDIO SETUP")
    print("=" * 50)
    print("This interactive setup will guide you through configuring your audiobook studio.")
    print("You can choose what to install and configure at each step.\n")
    
    # Step 1: Text annotation model selection
    print("STEP 1/6: Text Annotation Model")
    model = select_annotation_model()
    if model is None:
        print("❌ Setup cancelled")
        return
    
    # Step 2: Update configuration
    print("\nSTEP 2/6: Configuration")
    config_updated = update_env_file(model)
    
    # Step 3: Virtual environment
    print("\nSTEP 3/6: Python Virtual Environment")
    venv_created = create_virtual_environment()
    
    # Step 4: Python dependencies
    print("\nSTEP 4/6: Python Dependencies")
    python_deps = install_dependencies() if venv_created else False
    
    # Step 5: Dia TTS setup
    print("\nSTEP 5/6: Dia TTS Setup")
    dia_setup = setup_dia_tts()
    
    # Step 6: Node.js dependencies
    print("\nSTEP 6/6: Node.js Dependencies")
    node_deps = install_node_dependencies()
    
    # Summary
    print("\n🎉 SETUP SUMMARY")
    print("=" * 30)
    print(f"✅ Text annotation model: {model}")
    print(f"{'✅' if config_updated else '⚠️ '} Configuration: {'Updated' if config_updated else 'Skipped'}")
    print(f"{'✅' if venv_created else '⚠️ '} Virtual environment: {'Created' if venv_created else 'Skipped'}")
    print(f"{'✅' if python_deps else '⚠️ '} Python deps: {'Installed' if python_deps else 'Skipped'}")
    print(f"{'✅' if dia_setup else '⚠️ '} Dia TTS: {'Ready' if dia_setup else 'Skipped'}")
    print(f"{'✅' if node_deps else '⚠️ '} Node.js deps: {'Installed' if node_deps else 'Skipped'}")
    
    print(f"\n🎯 NEXT STEPS")
    print("=" * 20)
    
    if python_deps and node_deps:
        print("✅ Setup complete! You can now start the application:")
        print("\n  Terminal 1 (Backend):")
        print("    cd backend && source venv/bin/activate && python3 backend.py")
        print("\n  Terminal 2 (Frontend):")
        print("    npm run dev")
        print("\n  Then open http://localhost:3000")
    else:
        print("⚠️  Some components were skipped. You may need to:")
        if not venv_created:
            print("  - Create virtual environment: python3 -m venv backend/venv")
        if not python_deps:
            print("  - Install Python dependencies: backend/venv/bin/pip install -r requirements.txt")
        if not node_deps:
            print("  - Install Node.js dependencies: npm install")
        print("  - Then start backend and frontend in separate terminals")
    
    if model == "none":
        print("\n⚠️  Note: Text annotation is disabled. You'll need to manually add emotions to your text.")
    
    if not dia_setup:
        print("\n⚠️  Note: Dia TTS is not set up. Audio generation may not work.")

if __name__ == "__main__":
    main()
