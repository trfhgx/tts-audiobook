#!/bin/bash

echo "🎙️ Setting up Audiobook Studio..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

echo "✅ Python and Node.js found"

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Set up Python environment for Dia TTS
echo "🐍 Setting up Python environment for Dia TTS..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip

# Install from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing from requirements.txt..."
    pip install -r requirements.txt
else
    echo "⚠️ requirements.txt not found, installing core packages manually..."
    pip install torch torchaudio transformers
    pip install soundfile librosa numpy
    pip install requests accelerate
fi

# Install small local models for annotation
echo "🤖 Setting up local AI models for text annotation..."
echo "Downloading TinyLlama model (this may take a few minutes)..."
python3 -c "
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    print('Pre-downloading TinyLlama model...')
    model_name = 'TinyLlama/TinyLlama-1.1B-Chat-v1.0'
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    print('✅ TinyLlama model downloaded successfully!')
except Exception as e:
    print(f'⚠️ Could not download TinyLlama: {e}')
    print('Will use rule-based annotation as fallback')
"

# Try to install Dia TTS from the repository
echo "🎵 Installing Dia TTS..."
if [ ! -d "dia" ]; then
    echo "Cloning Dia TTS repository..."
    git clone https://github.com/nari-labs/dia.git
    cd dia
    pip install -r requirements.txt || echo "⚠️ Could not install from requirements.txt, continuing..."
    cd ..
else
    echo "Dia TTS repository already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "🤖 Local AI Model Options:"
echo "1. TinyLlama (1.1B) - Automatically downloaded"
echo "2. Ollama - Install manually for better performance:"
echo "   - Download from: https://ollama.ai"
echo "   - Run: ollama pull llama3.2:1b"
echo "   - Run: ollama pull phi3:3.8b"
echo ""
echo "To start the development server:"
echo "1. Run: npm run dev"
echo "2. Open: http://localhost:3000"
echo ""
echo "📝 Notes:"
echo "- Local AI models will add emotional annotations automatically"
echo "- First run may be slower as models initialize"
echo "- GPU recommended but not required"
echo ""
