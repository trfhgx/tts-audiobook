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

# Ollama and annotation functions are no longer needed with Chatterbox
# since it doesn't require text annotations or speaker tags

def setup_chatterbox_tts():
    """Setup Chatterbox TTS - much simpler than Dia!"""
    print("\n🎵 CHATTERBOX TTS SETUP")
    print("=" * 35)
    print("✨ Chatterbox is a state-of-the-art open-source TTS model")
    print("✅ No complex setup needed - installs directly via pip")
    print("✅ No manual model downloads required")
    print("✅ No speaker tags or annotations needed")
    print("✅ Just plain text → high-quality speech!")
    print("")
    
    if ask_yes_no("Do you want to install Chatterbox TTS?"):
        print("📦 Installing Chatterbox TTS...")
        
        try:
            # Install chatterbox-tts in the virtual environment
            venv_python = Path("backend/venv/bin/python")
            if venv_python.exists():
                print("🔧 Installing chatterbox-tts in virtual environment...")
                subprocess.run([str(venv_python), "-m", "pip", "install", "chatterbox-tts"], check=True)
                print("✅ Chatterbox TTS installed successfully!")
                
                # Test the installation
                print("🧪 Testing Chatterbox installation...")
                test_script = '''
try:
    from chatterbox.tts import ChatterboxTTS
    print("✅ Chatterbox import successful!")
    print("ℹ️  Model will be downloaded automatically on first use")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    exit(1)
'''
                with open("test_chatterbox.py", "w") as f:
                    f.write(test_script)
                
                subprocess.run([str(venv_python), "test_chatterbox.py"], check=True)
                os.remove("test_chatterbox.py")
                
                print("🎉 Chatterbox TTS is ready!")
                print("💡 The model will download automatically on first use (~2GB)")
                return True
            else:
                print("❌ Virtual environment not found. Please run virtual environment setup first.")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Chatterbox TTS: {e}")
            if os.path.exists("test_chatterbox.py"):
                os.remove("test_chatterbox.py")
            return False
    else:
        print("⚠️  Skipping Chatterbox TTS setup")
        return False

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

def update_env_file():
    """Update .env.local with backend URL"""
    print("\n⚙️  CONFIGURATION")
    print("=" * 25)
    
    env_file = Path(".env.local")
    
    config_info = """
Configuration to be written to .env.local:
  PYTHON_BACKEND_URL=http://localhost:8000
  TTS_ENGINE=chatterbox
"""
    print(config_info)
    
    if ask_yes_no("Do you want to create/update the configuration file?"):
        env_content = "PYTHON_BACKEND_URL=http://localhost:8000\nTTS_ENGINE=chatterbox\n"
        env_file.write_text(env_content)
        
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
    
    # Step 1: Configuration
    print("STEP 1/5: Configuration")
    config_updated = update_env_file()
    
    # Step 2: Virtual environment
    print("\nSTEP 2/5: Python Virtual Environment")
    venv_created = create_virtual_environment()
    
    # Step 3: Python dependencies
    print("\nSTEP 3/5: Python Dependencies")
    python_deps = install_dependencies() if venv_created else False
    
    # Step 4: Chatterbox TTS setup
    print("\nSTEP 4/5: Chatterbox TTS Setup")
    chatterbox_setup = setup_chatterbox_tts()
    
    # Step 5: Node.js dependencies
    print("\nSTEP 5/5: Node.js Dependencies")
    node_deps = install_node_dependencies()
    
    # Summary
    print("\n🎉 SETUP SUMMARY")
    print("=" * 30)
    print(f"{'✅' if config_updated else '⚠️ '} Configuration: {'Updated' if config_updated else 'Skipped'}")
    print(f"{'✅' if venv_created else '⚠️ '} Virtual environment: {'Created' if venv_created else 'Skipped'}")
    print(f"{'✅' if python_deps else '⚠️ '} Python deps: {'Installed' if python_deps else 'Skipped'}")
    print(f"{'✅' if chatterbox_setup else '⚠️ '} Chatterbox TTS: {'Ready' if chatterbox_setup else 'Skipped'}")
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
    
    if not chatterbox_setup:
        print("\n⚠️  Note: Chatterbox TTS is not set up. Audio generation may not work.")

if __name__ == "__main__":
    main()
