# Audiobook Studio

A professional web application for text-to-speech conversion using Chatterbox TTS with advanced voice cloning capabilities.

## Features

- **Advanced Voice Cloning** - Upload custom voice samples for personalized speech synthesis
- **High-Quality TTS** - Chatterbox TTS model for natural speech generation
- **Customizable Settings** - Control exaggeration levels and CFG weight for optimal output
- **File Management** - Automatic saving of generated audio with timestamp organization
- **Real-time Monitoring** - Device detection and performance logging (GPU/CPU)
- **Voice Library** - Built-in male/female voice samples plus custom upload support
- **Professional Audio** - WAV format output with configurable quality settings

## Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- GPU support recommended (CUDA or Apple Metal)

### Backend Setup

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone https://github.com/trfhgx/tts-audiobook
   cd /tts-audiobook
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```


### Frontend Setup

1. Install Node.js dependencies:
   ```bash
   npm install
   ```

2. Build the frontend:
   ```bash
   npm run build
   ```

## Running the Application

### Start Backend Server

```bash
cd backend
python backend.py
```

The backend will start on `http://localhost:8000`

### Start Frontend

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Text-to-Speech Generation
- `POST /generate-audio` - Convert text to speech with voice settings
- `GET /health` - Check system status and device information

### Voice Management
- `GET /voices` - List available voice samples
- `POST /upload_voice` - Upload custom voice samples for cloning

### File Operations
- `GET /files` - List generated audio files
- `GET /files/{filename}` - Download specific audio file

## Voice Cloning

### Adding Voice Samples

1. **Manual Upload**: Place audio files in the `voice_samples/` directory:
   - `female_sample.wav` - Female voice option
   - `male_sample.wav` - Male voice option

2. **Web Upload**: Use the frontend interface to upload custom voice samples

### Voice Sample Requirements

- **Duration**: 5-10 seconds of clear speech
- **Format**: WAV, MP3, or other common audio formats
- **Quality**: Clean recording without background noise
- **Content**: Natural conversational speech

## Configuration

### TTS Parameters

- **Exaggeration**: Controls speech expressiveness (0.0-1.0)
- **CFG Weight**: Balances generation speed and quality (0.1-1.0)
- **Voice**: Select from default, samples, or uploaded custom voices

### System Settings

The application automatically detects and uses available hardware:
- CUDA GPU (NVIDIA)
- Apple Metal (M1/M2 Macs)
- CPU fallback

## File Management

Generated audio files are automatically saved to `generated_audio/` with timestamps:
- Format: `YYYYMMDD_HHMMSS_text_snippet.wav`
- Automatic directory creation
- File size and generation time logging

## Development

### Project Structure

```
audiobook-studio/
├── backend/
│   └── backend.py          # FastAPI server
├── components/
│   └── TTSSettings.tsx     # Voice configuration UI
├── voice_samples/          # Voice cloning samples
├── generated_audio/        # Output audio files
└── requirements.txt        # Python dependencies
```

### Technology Stack

- **Backend**: FastAPI, PyTorch, Chatterbox TTS
- **Frontend**: Next.js, TypeScript, Tailwind CSS
- **Audio Processing**: torchaudio, librosa
- **Voice Cloning**: Chatterbox neural voice synthesis

## Troubleshooting

### Common Issues

1. **Model Loading Errors**
   - Ensure Chatterbox TTS is properly installed
   - Check CUDA/Metal availability for GPU acceleration

2. **Voice Upload Failures**
   - Verify audio file format and size (max 10MB)
   - Check file permissions in voice_samples directory

3. **Generation Timeouts**
   - Reduce text length for faster processing
   - Lower CFG weight for speed optimization

### Performance Optimization

- Use GPU acceleration when available
- Optimize voice sample quality for better cloning results
- Adjust exaggeration and CFG weight based on use case

## License

MIT License
