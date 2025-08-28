# Audiobook Studio

A fun web application for creating audiobooks using AI-powered text-to-speech with Dia TTS and emotional annotations.

## Features

- 🎭 **Smart AI Annotations** - Local models add emotions like (laughs), (sighs), (whispers)
- 🎵 **High-Quality TTS** - Dia TTS model for natural speech generation
- 🎛️ **Customizable Settings** - Control emotion intensity and pauses
- 📁 **File Upload Support** - Import text files directly
- 🎧 **Built-in Player** - Preview and download your audiobooks
- 🔒 **Fully Local** - No data sent to external services

## Quick Setup

1. **Prerequisites**
   - Node.js 18+
   - Python 3.8+
   - Ollama (for text annotation models)

2. **Interactive Setup**
   ```bash
   git clone <your-repo-url>
   cd audiobook-studio
   python3 setup.py
   ```
   
   The setup will guide you through:
   - Creating virtual environment
   - Selecting annotation models (Ollama)
   - Downloading Dia TTS model (~6GB)
   - Installing all dependencies

3. **Start the Application**
   
   **Terminal 1 (Backend):**
   ```bash
   cd backend
   source venv/bin/activate
   python backend.py
   ```
   
   **Terminal 2 (Frontend):**
   ```bash
   npm run dev
   ```
   
   Open http://localhost:3000

## Text Formatting Tips

- Use `[S1]` and `[S2]` for different speakers
- Add emotions manually: `(laughs)`, `(sighs)`, `(whispers)`, `(pauses)`
- Or let AI add them automatically with configurable intensity
- Keep individual sections under 500 characters for best results

## Configuration



You can change the annotation model to any Ollama model you have installed.

## Architecture

- **Frontend:** Next.js 14 + TypeScript + Tailwind CSS
- **Backend:** FastAPI + PyTorch + Transformers
- **TTS:** Dia TTS (nari-labs/Dia-1.6B-0626)
- **Annotation:** Local Ollama models (no external API calls)

## Troubleshooting

- **"TTS model not available"** - Run setup.py and download the Dia TTS model
- **"No annotation model"** - Install Ollama and run setup.py to select a model
- **Backend won't start** - Ensure virtual environment exists: `python3 setup.py`

## License

MIT License. Dia TTS is licensed under Apache 2.0.
