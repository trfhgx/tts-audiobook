#!/usr/bin/env python3
"""
Audiobook Studio Python Backend
FastAPI server for text annotation and TTS generation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
import torch
import torchaudio
import numpy as np
import requests
import io
import logging
from typing import Optional
import uvicorn
import os
import sys
from pathlib import Path

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
annotation_model = None
tts_model = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
OLLAMA_URL = "http://localhost:11434"

class TextRequest(BaseModel):
    text: str
    settings: dict

class AnnotationSettings(BaseModel):
    addEmotions: bool = True
    emotionIntensity: float = 0.7
    addPauses: bool = True
    speakerVariation: bool = True

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global annotation_model, tts_model
    
    logger.info("Loading models...")
    
    # Load annotation model from environment
    annotation_model_name = os.getenv("ANNOTATION_MODEL", "")
    
    if annotation_model_name:
        try:
            # Test Ollama connection
            response = requests.get(f"{OLLAMA_URL}/api/version", timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ Ollama connected, using model: {annotation_model_name}")
                annotation_model = annotation_model_name
            else:
                logger.warning("Ollama not available, using rule-based annotation")
                annotation_model = None
        except Exception as e:
            logger.warning(f"Failed to connect to Ollama: {e}")
            annotation_model = None
    else:
        logger.warning("No annotation model configured in .env")
        annotation_model = None
    
    # Load Dia TTS model
    try:
        # Add the dia directory to Python path
        dia_path = Path.cwd() / "dia"
        if dia_path.exists():
            sys.path.insert(0, str(dia_path))
            
            # Try to import and load Dia TTS
            try:
                from transformers import AutoModel, AutoTokenizer
                
                model_name = "nari-labs/Dia-1.6B-0626"
                logger.info(f"Loading Dia TTS model: {model_name}")
                
                tts_model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
                tts_tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
                
                tts_model = tts_model.to(device)
                tts_model.eval()
                
                globals()['tts_tokenizer'] = tts_tokenizer
                logger.info(f"✅ Dia TTS loaded successfully on {device}")
                
            except Exception as e:
                logger.error(f"Failed to load Dia TTS from HuggingFace: {e}")
                logger.error("TTS service will be unavailable")
                tts_model = None
        else:
            logger.error("Dia directory not found, run setup.py first")
            logger.error("TTS service will be unavailable")
            tts_model = None
            
    except Exception as e:
        logger.error(f"Failed to setup Dia TTS: {e}")
        logger.error("TTS service will be unavailable")
        tts_model = None

@app.get("/")
async def root():
    return {"message": "Audiobook Studio API", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "models": {
            "annotation": annotation_model is not None,
            "annotation_model": annotation_model if annotation_model else "rule-based",
            "tts": tts_model is not None and tts_model != "placeholder",
            "tts_model_type": "Dia-1.6B-0626" if tts_model not in [None, "placeholder"] else "placeholder"
        },
        "device": str(device),
        "cuda_available": torch.cuda.is_available(),
        "ollama_connected": annotation_model is not None
    }

@app.post("/annotate-text")
async def annotate_text(request: TextRequest):
    """Add emotional annotations to text using local AI model"""
    try:
        text = request.text
        settings = request.settings
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        annotated_text = text
        
        if settings.get('addEmotions', True):
            annotated_text = await add_emotional_annotations(
                text, 
                settings.get('emotionIntensity', 0.7)
            )
        
        if settings.get('addPauses', True):
            annotated_text = add_natural_pauses(annotated_text)
        
        return {
            "original": text,
            "annotated": annotated_text,
            "settings": settings
        }
        
    except Exception as e:
        logger.error(f"Annotation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to annotate text: {str(e)}")

@app.post("/generate-audio")
async def generate_audio(request: TextRequest):
    """Generate audio from text using TTS"""
    try:
        text = request.text
        settings = request.settings
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # First annotate the text if needed
        if settings.get('addEmotions', True) or settings.get('addPauses', True):
            annotation_response = await annotate_text(request)
            processed_text = annotation_response["annotated"]
        else:
            processed_text = text
        
        # Generate audio
        audio_bytes = await generate_tts_audio(processed_text, settings)
        
        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=audiobook.wav"
            }
        )
        
    except Exception as e:
        logger.error(f"Audio generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate audio: {str(e)}")

async def add_emotional_annotations(text: str, intensity: float) -> str:
    """Add emotional annotations using Ollama model"""
    try:
        if annotation_model is None:
            logger.warning("Annotation model not available, using rule-based approach")
            return add_rule_based_annotations(text, intensity)
        
        intensity_level = "subtle" if intensity < 0.3 else "moderate" if intensity < 0.7 else "expressive"
        
        prompt = f"""Add emotional cues to this text for audiobook narration. Use {intensity_level} emotions.
Add annotations like (laughs), (sighs), (whispers), (pauses) where appropriate.
Keep the original text intact, only ADD emotions in parentheses.

Text: {text}

Enhanced text:"""
        
        # Call Ollama API
        response = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": annotation_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 200
            }
        }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            enhanced_text = result.get("response", "").strip()
            
            # Clean up the response to extract just the enhanced text
            if "Enhanced text:" in enhanced_text:
                enhanced_text = enhanced_text.split("Enhanced text:")[-1].strip()
            
            # Validate the result
            if enhanced_text and len(enhanced_text) >= len(text) * 0.8:
                return enhanced_text
        
        # Fallback to rule-based if AI response is poor
        return add_rule_based_annotations(text, intensity)
        
    except Exception as e:
        logger.warning(f"Ollama annotation failed: {e}, using rule-based approach")
        return add_rule_based_annotations(text, intensity)

def add_rule_based_annotations(text: str, intensity: float) -> str:
    """Fallback rule-based annotation system"""
    import re
    
    annotated = text
    
    # Simple rules based on intensity
    if intensity > 0.3:
        # Add basic emotions
        annotated = re.sub(r'\b(ha ha|haha|funny|joke)\b', r'\1 (laughs)', annotated, flags=re.IGNORECASE)
        annotated = re.sub(r'\b(oh dear|oh no|unfortunately)\b', r'\1 (sighs)', annotated, flags=re.IGNORECASE)
        annotated = re.sub(r'\b(wow|amazing|incredible)\b', r'\1 (gasps)', annotated, flags=re.IGNORECASE)
        annotated = re.sub(r'\b(whisper|quietly|softly)\b', r'\1 (whispers)', annotated, flags=re.IGNORECASE)
    
    if intensity > 0.7:
        # Add more dramatic emotions
        annotated = re.sub(r'([.!?])\s+', r'\1 (pauses) ', annotated)
        annotated = re.sub(r'([,;:])\s+', r'\1 (brief pause) ', annotated)
    
    return annotated

def add_natural_pauses(text: str) -> str:
    """Add natural pauses at punctuation"""
    import re
    text = re.sub(r'([.!?])\s+', r'\1 (pauses) ', text)
    text = re.sub(r'([,;:])\s+', r'\1 (brief pause) ', text)
    return text

async def generate_tts_audio(text: str, settings: dict) -> bytes:
    """Generate audio using Dia TTS"""
    if tts_model is None:
        raise HTTPException(status_code=503, detail="TTS model not available. Please ensure Dia TTS is properly installed.")
        
    logger.info(f"Generating audio for text: {text[:50]}...")
    
    # Preprocess text for Dia TTS
    processed_text = preprocess_text_for_dia(text)
    
    # Get tokenizer from globals
    tokenizer = globals().get('tts_tokenizer')
    if tokenizer is None:
        raise HTTPException(status_code=503, detail="TTS tokenizer not available")
    
    try:
        # Tokenize input
        inputs = tokenizer(processed_text, return_tensors="pt", padding=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate audio with Dia TTS
        with torch.no_grad():
            audio_tokens = tts_model.generate(
                **inputs,
                max_length=min(2048, len(inputs['input_ids'][0]) + 1024),
                do_sample=True,
                temperature=0.7,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        
        # Decode audio tokens to waveform
        if hasattr(tts_model, 'decode_audio'):
            audio_waveform = tts_model.decode_audio(audio_tokens)
        elif hasattr(tts_model, 'decode'):
            audio_waveform = tts_model.decode(audio_tokens)
        else:
            raise HTTPException(status_code=503, detail="Dia TTS model does not support audio decoding")
        
        # Ensure audio is in the right format
        if audio_waveform.dim() == 1:
            audio_waveform = audio_waveform.unsqueeze(0)
        
        # Convert to WAV bytes
        sample_rate = 24000
        buffer = io.BytesIO()
        torchaudio.save(buffer, audio_waveform.cpu(), sample_rate, format="wav")
        buffer.seek(0)
        
        logger.info("✅ Audio generated successfully")
        return buffer.getvalue()
        
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate audio: {str(e)}")

def preprocess_text_for_dia(text: str) -> str:
    """Preprocess text for optimal Dia TTS generation"""
    
    # Ensure proper speaker tags
    if not text.strip().startswith('[S1]') and not text.strip().startswith('[S2]'):
        text = f"[S1] {text}"
    
    # Clean up formatting
    text = text.replace('\n\n', ' ')
    text = text.replace('\n', ' ')
    
    # Ensure text ends with a speaker tag for better quality
    if not text.strip().endswith('[S1]') and not text.strip().endswith('[S2]'):
        # Determine the last speaker and add it
        last_speaker = '[S2]' if '[S2]' in text else '[S1]'
        text = f"{text} {last_speaker}"
    
    return text

def generate_placeholder_audio(text: str) -> torch.Tensor:
    """Generate placeholder audio when the real model fails"""
    
    sample_rate = 24000
    duration = min(len(text) / 10, 30)  # Rough estimate
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Generate a more interesting tone that varies based on text
    frequency = 440 + (hash(text) % 200)
    audio = 0.3 * np.sin(2 * np.pi * frequency * t)
    
    # Add some variation to make it more speech-like
    audio = audio * (1 + 0.3 * np.sin(2 * np.pi * 2 * t))
    
    # Add some envelope to make it more natural
    envelope = np.exp(-t / (duration * 0.8))  # Fade out
    audio = audio * envelope
    
    return text

# Endpoint handlers

if __name__ == "__main__":
    uvicorn.run(
        "backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
