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
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import io
import logging
from typing import Optional
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Audiobook Studio API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for models
annotation_model = None
tts_model = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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
    
    # Load annotation model (small local model)
    try:
        annotation_model = pipeline(
            "text-generation",
            model="microsoft/DialoGPT-small",  # Small, fast model for annotations
            tokenizer="microsoft/DialoGPT-small",
            device=0 if torch.cuda.is_available() else -1
        )
        logger.info("✅ Annotation model loaded successfully")
    except Exception as e:
        logger.warning(f"Failed to load annotation model: {e}")
        annotation_model = None
    
    # Load TTS model (Dia TTS)
    try:
        # For now, we'll use a mock TTS - replace with actual Dia TTS
        logger.info("✅ TTS model ready (using mock for now)")
        tts_model = "mock"  # Replace with actual Dia TTS loading
    except Exception as e:
        logger.warning(f"Failed to load TTS model: {e}")
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
            "tts": tts_model is not None
        },
        "device": str(device)
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
    """Add emotional annotations using local AI model"""
    try:
        if annotation_model is None:
            logger.warning("Annotation model not available, using rule-based approach")
            return add_rule_based_annotations(text, intensity)
        
        # Create a prompt for the model
        intensity_level = "subtle" if intensity < 0.3 else "moderate" if intensity < 0.7 else "expressive"
        
        prompt = f"""Add emotional cues to this text for audiobook narration. Use {intensity_level} emotions.
Add annotations like (laughs), (sighs), (whispers), (pauses) where appropriate.
Keep the original text intact, only ADD emotions in parentheses.

Text: {text}

Enhanced text:"""
        
        # Generate with the model
        result = annotation_model(
            prompt,
            max_length=len(prompt.split()) + 100,
            temperature=0.7,
            do_sample=True,
            pad_token_id=annotation_model.tokenizer.eos_token_id
        )
        
        # Extract the generated text
        generated = result[0]['generated_text']
        enhanced_text = generated.split("Enhanced text:")[-1].strip()
        
        # Fallback to original if generation failed
        if not enhanced_text or len(enhanced_text) < len(text) * 0.8:
            return add_rule_based_annotations(text, intensity)
        
        return enhanced_text
        
    except Exception as e:
        logger.warning(f"AI annotation failed: {e}, using rule-based approach")
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
    """Generate audio using TTS (mock implementation for now)"""
    try:
        # For now, generate mock audio
        # TODO: Replace with actual Dia TTS integration
        
        logger.info(f"Generating audio for text: {text[:50]}...")
        
        # Mock audio generation
        sample_rate = 24000
        duration = min(len(text) / 10, 30)  # Rough estimate
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Generate a more interesting tone that varies based on text
        frequency = 440 + (hash(text) % 200)
        audio = 0.3 * np.sin(2 * np.pi * frequency * t)
        
        # Add some variation
        audio = audio * (1 + 0.3 * np.sin(2 * np.pi * 2 * t))
        
        # Convert to WAV bytes
        audio_tensor = torch.FloatTensor(audio).unsqueeze(0)
        
        # Save to bytes buffer
        buffer = io.BytesIO()
        torchaudio.save(buffer, audio_tensor, sample_rate, format="wav")
        buffer.seek(0)
        
        return buffer.getvalue()
        
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise

if __name__ == "__main__":
    uvicorn.run(
        "backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
