# Audiobook Studio 🎙️

A fun and interactive web application for creating audiobooks using AI-powered text-to-speech with the amazing **Dia TTS** model!

## ✨ Features

- 📝 **Smart Text Input**: Paste text or upload files with drag & drop
- 🤖 **Local AI Annotations**: Uses small local models (TinyLlama, Ollama) to add emotional cues
- 🎭 **Emotion Annotations**: Automatically adds (laughs), (sighs), and other emotional cues
- 🎵 **High-Quality TTS**: Powered by Dia TTS for ultra-realistic voice synthesis
- 🎚️ **Customizable Settings**: Control emotion intensity, pauses, and speaker variation
- 🎧 **Built-in Audio Player**: Preview your audiobook with beautiful controls
- 💾 **Easy Download**: Get your audiobook as a high-quality WAV file
- 🔒 **Privacy First**: All AI processing happens locally on your machine

## 🚀 Quick Start

1. **Clone and setup:**
   ```bash
   git clone <your-repo>
   cd audiobook-studio
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

## 🛠️ Setup Details

### Prerequisites
- Node.js 18+ 
- Python 3.8+
- Git

### Environment Variables
Copy `.env.local` and update if needed:
```bash
# Dia TTS configuration  
DIA_MODEL_PATH=/path/to/dia/model

# Local AI Model preference (optional)
AI_MODEL_TYPE=tiny-llama  # Options: tiny-llama, ollama, rule-based
```

### Local AI Models
The setup script will automatically download TinyLlama (1.1B parameters) for local text annotation.

**Alternative Options:**
- **Ollama**: For better performance, install Ollama and run:
  ```bash
  ollama pull llama3.2:1b
  ollama pull phi3:3.8b
  ```
- **Rule-based**: Fast fallback that uses pattern matching

### Dia TTS Installation
The setup script will automatically:
1. Clone the Dia TTS repository
2. Install Python dependencies
3. Set up the virtual environment

For manual installation:
```bash
git clone https://github.com/nari-labs/dia.git
cd dia
pip install -r requirements.txt
```

## 🎯 How to Use

1. **Enter Your Text**: 
   - Paste text directly or drag & drop a `.txt` file
   - Use `[S1]` and `[S2]` tags for different speakers
   - Try the sample texts to get started

2. **Configure Settings**:
   - Enable smart emotions for automatic annotation
   - Adjust emotion intensity (subtle to dramatic)
   - Toggle natural pauses at punctuation
   - Enable speaker variation for dialogue

3. **Generate Audio**:
   - Click "Generate Audiobook" 
   - Watch the real-time processing steps
   - Preview your audiobook in the player

4. **Download & Enjoy**:
   - Download as high-quality WAV
   - Share your audiobook!

## 🎨 Text Formatting Tips

- **Speakers**: Use `[S1]` and `[S2]` for different voices
- **Emotions**: Add `(laughs)`, `(sighs)`, `(whispers)` manually or let AI do it
- **Length**: Keep sections under 20 seconds for best results
- **Punctuation**: Use proper punctuation for natural pauses

### Example:
```
[S1] Once upon a time, there was a magical library. (sighs wistfully) 
[S2] "Tell me more!" she exclaimed with excitement. (laughs)
[S1] Well, (clears throat) it all started on a dark and stormy night...
```

## 🎵 Supported Emotions

The AI can add these emotional annotations:
- `(laughs)` `(chuckles)` `(giggles)`
- `(sighs)` `(gasps)` `(inhales)` `(exhales)`
- `(whispers)` `(clears throat)` `(coughs)`
- `(groans)` `(pauses)` `(mumbles)`

## 🏗️ Architecture

```
📁 audiobook-studio/
├── 🎨 app/                 # Next.js App Router
│   ├── api/               # API endpoints
│   │   ├── annotate-text/ # AI emotion annotation
│   │   └── generate-audio/ # Dia TTS integration
│   ├── globals.css        # Tailwind styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Main app page
├── 🧩 components/         # React components
│   ├── TextInput.tsx      # File upload & text editor
│   ├── AnnotationSettings.tsx # Audio settings
│   └── AudioPreview.tsx   # Audio player
├── 🐍 dia/               # Dia TTS model (auto-cloned)
├── 🔧 setup.sh           # Setup script
└── 📦 package.json       # Dependencies
```

## 🚧 Development

### Adding New Features
1. **New Emotions**: Update the annotation API in `app/api/annotate-text/route.ts`
2. **Audio Effects**: Modify the Dia TTS integration in `app/api/generate-audio/route.ts`
3. **UI Components**: Add new components in the `components/` folder

### Customizing Dia TTS
- Update model parameters in `generate-audio/route.ts`
- Modify voice cloning features
- Add speaker selection options

## 🐛 Troubleshooting

### Audio Generation Issues
- Ensure Dia TTS is properly installed
- Check Python virtual environment is activated
- Verify GPU/CUDA setup for better performance

### API Errors
- Check server logs for detailed error messages
- Verify environment variables are set
- Ensure OpenAI API key is valid (if using AI annotation)

### Performance
- Use shorter text segments for faster generation
- Consider running on GPU for better speed
- Adjust model precision (fp16/fp32) based on hardware

## 📄 License

This project is licensed under the MIT License. See LICENSE for details.

The Dia TTS model is licensed under Apache 2.0 - see the [Dia repository](https://github.com/nari-labs/dia) for details.

## 🙏 Acknowledgments

- **Nari Labs** for the amazing Dia TTS model
- **Hugging Face** for model hosting and transformers library
- **Next.js** team for the fantastic framework
- **Framer Motion** for beautiful animations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Made with ❤️ for the audiobook community
