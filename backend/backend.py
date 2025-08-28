#!/usr/bin/env python3
"""
Audiobook Studio Python Backend
FastAPI server for text-to-speech generation using Chatterbox TTS
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
import torch
import torchaudio
import numpy as np
import io
import logging
from typing import Optional
import uvicorn
import os
import sys
from pathlib import Path
from datetime import datetime

# Load environment variables from parent directory
env_file = Path(__file__).parent.parent / ".env.local"
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Audiobook Studio API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
tts_model = None

# Create output directory for generated audio
OUTPUT_DIR = Path("generated_audio")
OUTPUT_DIR.mkdir(exist_ok=True)

# Create voice samples directory
VOICE_SAMPLES_DIR = Path("voice_samples")
VOICE_SAMPLES_DIR.mkdir(exist_ok=True)

def generate_filename(text: str) -> str:
    """Generate a unique filename based on timestamp and text snippet"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Create a safe filename from first 30 chars of text
    text_snippet = "".join(c for c in text[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
    text_snippet = text_snippet.replace(' ', '_')
    if not text_snippet:
        text_snippet = "audiobook"
    return f"{timestamp}_{text_snippet}.wav"

# Device selection with proper GPU support
if torch.cuda.is_available():
    device = torch.device("cuda")
    print("🚀 Using CUDA GPU")
elif torch.backends.mps.is_available():
    device = torch.device("mps") 
    print("🚀 Using Apple Metal GPU")
else:
    device = torch.device("cpu")
    print("⚠️  Using CPU")

class TextRequest(BaseModel):
    text: str
    settings: dict = {}

class TTSSettings(BaseModel):
    voice: str = "default"
    exaggeration: float = 0.5
    cfg_weight: float = 0.5
    quality: str = "high"

@app.on_event("startup")
async def startup_event():
    """Initialize Chatterbox TTS model on startup"""
    global tts_model
    
    # Ensure output directories exist
    OUTPUT_DIR.mkdir(exist_ok=True)
    VOICE_SAMPLES_DIR.mkdir(exist_ok=True)
    logger.info(f"📁 Audio output directory: {OUTPUT_DIR.absolute()}")
    logger.info(f"🎤 Voice samples directory: {VOICE_SAMPLES_DIR.absolute()}")
    
    logger.info("Loading Chatterbox TTS model...")
    
    try:
        # Import and initialize Chatterbox TTS
        from chatterbox.tts import ChatterboxTTS
        
        logger.info("🔄 Initializing Chatterbox TTS...")
        logger.info(f"🖥️  Target device: {device}")
        
        # Correct Chatterbox API usage
        tts_model = ChatterboxTTS.from_pretrained(device=str(device))
        
        # Log which device the model is actually running on
        if hasattr(tts_model, 'device'):
            actual_device = tts_model.device
            logger.info(f"🚀 Chatterbox TTS loaded on device: {actual_device}")
        else:
            logger.info(f"📍 Chatterbox TTS initialized for device: {device}")
        
        # The model will be downloaded automatically on first use if not present
        logger.info("✅ Chatterbox TTS initialized successfully!")
        logger.info("💡 Model will download automatically on first use if needed (~2GB)")
        
    except ImportError as e:
        logger.error(f"❌ Failed to import Chatterbox TTS: {e}")
        logger.error("Please ensure chatterbox-tts is installed: pip install chatterbox-tts")
        tts_model = None
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Chatterbox TTS: {e}")
        tts_model = None

@app.get("/")
async def root():
    return {"message": "Audiobook Studio API", "status": "running"}

@app.get("/files")
async def list_generated_files():
    """List all generated audio files"""
    try:
        files = []
        if OUTPUT_DIR.exists():
            for file_path in OUTPUT_DIR.glob("*.wav"):
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "size_kb": round(stat.st_size / 1024, 1),
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # Sort by creation time, newest first
        files.sort(key=lambda x: x["created"], reverse=True)
        
        return {
            "total_files": len(files),
            "output_directory": str(OUTPUT_DIR.absolute()),
            "files": files
        }
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return {"error": str(e)}

@app.get("/voices")
async def list_available_voices():
    """List available voice samples and their status"""
    try:
        voices = [
            {
                "id": "default",
                "name": "Default Voice",
                "description": "Built-in Chatterbox voice",
                "available": True,
                "type": "built-in"
            }
        ]
        
        # Check for voice samples
        female_sample = VOICE_SAMPLES_DIR / "female_sample.wav"
        male_sample = VOICE_SAMPLES_DIR / "male_sample.wav"
        
        voices.append({
            "id": "female_sample",
            "name": "Female Voice Clone",
            "description": "Female voice sample",
            "available": female_sample.exists(),
            "type": "sample",
            "path": str(female_sample) if female_sample.exists() else None
        })
        
        voices.append({
            "id": "male_sample", 
            "name": "Male Voice Clone",
            "description": "Male voice sample",
            "available": male_sample.exists(),
            "type": "sample",
            "path": str(male_sample) if male_sample.exists() else None
        })
        
        # Scan for custom uploaded voices
        for voice_file in VOICE_SAMPLES_DIR.glob("custom_*"):
            if voice_file.is_file() and voice_file.suffix.lower() in ['.wav', '.mp3', '.ogg', '.flac']:
                voice_id = voice_file.stem  # filename without extension
                voices.append({
                    "id": voice_id,
                    "name": f"Custom Voice ({voice_id})",
                    "description": f"Uploaded custom voice sample",
                    "available": True,
                    "type": "custom",
                    "path": str(voice_file),
                    "uploaded": True
                })
        
        return {
            "voices": voices,
            "voice_samples_directory": str(VOICE_SAMPLES_DIR.absolute()),
            "instructions": "To add voice samples, place 3-10 second audio files in the voice_samples directory or use the upload endpoint"
        }
    except Exception as e:
        logger.error(f"Error listing voices: {e}")
        return {"error": str(e)}

@app.get("/files/{filename}")
async def download_file(filename: str):
    """Download a specific generated audio file"""
    try:
        file_path = OUTPUT_DIR / filename
        
        if not file_path.exists() or not file_path.suffix == '.wav':
            raise HTTPException(status_code=404, detail="File not found")
        
        # Read file and return as response
        with open(file_path, 'rb') as f:
            audio_bytes = f.read()
        
        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint with device information"""
    device_info = {
        "current_device": str(device),
        "cuda_available": torch.cuda.is_available(),
        "mps_available": torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False
    }
    
    # Add model device info if available
    if tts_model and hasattr(tts_model, 'device'):
        device_info["model_device"] = str(tts_model.device)
    
    logger.info(f"🔍 Health check - Device info: {device_info}")
    
    return {
        "status": "healthy",
        "models": {
            "tts": tts_model is not None,
            "tts_model_type": "Chatterbox TTS" if tts_model is not None else "none"
        },
        "device_info": device_info
    }

@app.post("/generate-audio")
async def generate_audio(request: TextRequest):
    """Generate audio from text using Chatterbox TTS"""
    try:
        text = request.text
        settings = request.settings
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Generate audio directly - no preprocessing needed with Chatterbox!
        audio_bytes, filename, file_info = await generate_tts_audio(text, settings)
        
        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "X-Generated-File": file_info["path"],
                "X-File-Size": str(file_info["size"])
            }
        )
        
    except Exception as e:
        logger.error(f"Audio generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate audio: {str(e)}")

async def generate_tts_audio(text: str, settings: dict) -> tuple[bytes, str, dict]:
    """Generate audio using Chatterbox TTS - returns audio_bytes, filename, and file_info"""
    global tts_model
    
    if tts_model is None:
        raise HTTPException(status_code=503, detail="Chatterbox TTS model not available. Please ensure it's properly installed.")
    
    import time
    start_time = time.time()
    logger.info(f"🎵 Generating audio with Chatterbox TTS...")
    logger.info(f"📊 Text length: {len(text)} characters")
    logger.info(f"📝 Text: '{text[:100]}{'...' if len(text) > 100 else ''}'")
    logger.info(f"🖥️  Using device: {device}")
    
    # Log model device if available
    if hasattr(tts_model, 'device'):
        logger.info(f"🚀 Model running on: {tts_model.device}")
    
    try:
        # Generate audio with Chatterbox - correct API usage!
        logger.info("🔄 Generating audio...")
        gen_start = time.time()
        
        # Chatterbox TTS correct API - returns tensor directly
        # Parameters based on documentation: text, audio_prompt_path (optional), exaggeration, cfg_weight
        
        # Handle voice selection
        voice_setting = settings.get('voice', 'default')
        audio_prompt_path = None
        
        if voice_setting == 'female_sample':
            # Use female voice sample if available
            female_sample_path = VOICE_SAMPLES_DIR / "female_sample.wav"
            if female_sample_path.exists():
                audio_prompt_path = str(female_sample_path)
                logger.info(f"🎤 Using female voice sample: {audio_prompt_path}")
            else:
                logger.warning(f"🎤 Female voice sample not found at {female_sample_path}")
        elif voice_setting == 'male_sample':
            # Use male voice sample if available
            male_sample_path = VOICE_SAMPLES_DIR / "male_sample.wav"
            if male_sample_path.exists():
                audio_prompt_path = str(male_sample_path)
                logger.info(f"🎤 Using male voice sample: {audio_prompt_path}")
            else:
                logger.warning(f"🎤 Male voice sample not found at {male_sample_path}")
        elif voice_setting.startswith('custom_'):
            # Handle uploaded custom voices
            # Look for the custom voice file (could be .wav, .mp3, etc.)
            custom_files = list(VOICE_SAMPLES_DIR.glob(f"{voice_setting}.*"))
            if custom_files:
                audio_prompt_path = str(custom_files[0])  # Use the first matching file
                logger.info(f"🎤 Using custom voice sample: {audio_prompt_path}")
            else:
                logger.warning(f"🎤 Custom voice '{voice_setting}' not found in {VOICE_SAMPLES_DIR}")
        elif voice_setting == 'default':
            logger.info("🎤 Using default Chatterbox voice")
        else:
            logger.warning(f"🎤 Unknown voice setting '{voice_setting}', using default")
        
        # Generate with appropriate voice
        if audio_prompt_path:
            audio_tensor = tts_model.generate(
                text,
                audio_prompt_path=audio_prompt_path,
                exaggeration=settings.get('exaggeration', 0.5),
                cfg_weight=settings.get('cfg_weight', 0.5)
            )
        else:
            audio_tensor = tts_model.generate(
                text,
                exaggeration=settings.get('exaggeration', 0.5),
                cfg_weight=settings.get('cfg_weight', 0.5)
            )
        
        gen_time = time.time() - gen_start
        logger.info(f"✅ Audio generated in {gen_time:.2f}s")
        
        # Log tensor device info
        if hasattr(audio_tensor, 'device'):
            logger.info(f"🎯 Generated tensor device: {audio_tensor.device}")
        
        # Convert tensor to WAV bytes for response
        logger.info("💾 Converting audio tensor to WAV bytes...")
        
        # Generate unique filename
        filename = generate_filename(text)
        output_path = OUTPUT_DIR / filename
        
        # Use torchaudio to save the tensor to both file and bytes
        import torchaudio
        import tempfile
        import os
        
        # Save to the permanent output directory
        logger.info(f"📁 Saving audio to: {output_path}")
        torchaudio.save(str(output_path), audio_tensor.cpu(), tts_model.sr)
        
        # Also create bytes for HTTP response using temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            # Save tensor to temporary WAV file
            torchaudio.save(temp_file.name, audio_tensor.cpu(), tts_model.sr)
            
            # Read the WAV file as bytes
            with open(temp_file.name, 'rb') as f:
                audio_bytes = f.read()
            
            # Clean up temp file
            os.unlink(temp_file.name)
        
        total_time = time.time() - start_time
        
        # Get file size for logging
        file_size = output_path.stat().st_size if output_path.exists() else 0
        
        logger.info(f"✅ Audio saved to: {output_path}")
        logger.info(f"📊 File size: {file_size / 1024:.1f} KB")
        logger.info(f"🎉 Total generation time: {total_time:.2f}s")
        logger.info(f"⚡ Speed: {len(text)/total_time:.1f} chars/sec")
        
        file_info = {
            "path": str(output_path),
            "size": file_size
        }
        
        return audio_bytes, filename, file_info
        
    except Exception as e:
        logger.error(f"Chatterbox TTS generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate audio: {str(e)}")

@app.post("/upload_voice")
async def upload_voice(voice_file: UploadFile = File(...)):
    """Upload a custom voice sample for voice cloning"""
    try:
        # Validate file type
        if not voice_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Validate file size (max 10MB)
        if voice_file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
        
        # Create a unique filename for the uploaded voice
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(voice_file.filename)[1] or '.wav'
        voice_id = f"custom_{timestamp}"
        filename = f"{voice_id}{file_extension}"
        
        # Save the uploaded file
        voice_path = VOICE_SAMPLES_DIR / filename
        
        logger.info(f"📤 Uploading voice sample: {voice_file.filename}")
        logger.info(f"💾 Saving to: {voice_path}")
        
        # Write the uploaded file
        with open(voice_path, "wb") as f:
            content = await voice_file.read()
            f.write(content)
        
        logger.info(f"✅ Voice sample uploaded successfully: {voice_id}")
        
        return {
            "message": "Voice sample uploaded successfully",
            "voice_id": voice_id,
            "filename": filename,
            "path": str(voice_path),
            "size": len(content)
        }
        
    except Exception as e:
        logger.error(f"Voice upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload voice sample: {str(e)}")

# Endpoint handlers

if __name__ == "__main__":
    uvicorn.run(
        "backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
