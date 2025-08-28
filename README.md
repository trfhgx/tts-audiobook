# Audiobook Studio

A web application for creating audiobooks using AI-powered text-to-speech with Dia TTS and emotional annotations.

## Features

- Smart text input with file upload support
- AI-powered emotion annotations using local models
- High-quality text-to-speech with Dia TTS
- Customizable audio settings
- Built-in audio player with controls
- Download audiobooks as WAV files

## Quick Start

1. **Prerequisites**
   - Node.js 18+
   - Python 3.8+
   - Ollama (for text annotation models)

2. **Setup**
   ```bash
   git clone <your-repo>
   cd audiobook-studio
   python3 setup.py
   ```

3. **Run**
   ```bash
   python3 run.py
   ```
   Then open http://localhost:3000

## Manual Setup

If you prefer to run components separately:

1. Install dependencies:
   ```bash
   npm install
   pip install -r requirements.txt
   ```

2. Install Ollama and a small model:
   ```bash
   ollama pull llama3.2:1b
   ```

3. Update .env.local:
   ```
   ANNOTATION_MODEL=llama3.2:1b
   PYTHON_BACKEND_URL=http://localhost:8000
   ```

4. Run backend and frontend:
   ```bash
   # Terminal 1
   python3 backend.py
   
   # Terminal 2
   npm run dev
   ```

## Text Formatting

- Use `[S1]` and `[S2]` for different speakers
- Add emotions like `(laughs)`, `(sighs)`, `(whispers)` manually or let AI add them
- Keep sections under 20 seconds for best results

## License

MIT License. Dia TTS is licensed under Apache 2.0.
