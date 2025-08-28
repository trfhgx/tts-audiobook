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
annotation_model = None
tts_model = None
tts_processor = None

# Device selection with proper GPU support
if torch.cuda.is_available():
    device = torch.device("cuda")
    print("🚀 Using CUDA GPU")
elif torch.backends.mps.is_available():
    device = torch.device("mps") 
    print("🚀 Using Apple Metal GPU")
else:
    device = torch.device("cpu")
    print("⚠️  Using CPU (slow)")

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
    global annotation_model, tts_model, tts_processor
    
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
        # Add the dia directory to Python path (dia is in parent directory)
        dia_path = Path.cwd().parent / "dia"
        models_path = Path.cwd().parent / "models" / "dia-tts"
        
        if dia_path.exists():
            sys.path.insert(0, str(dia_path))
            
            # Try to import and load Dia TTS (only if locally available)
            try:
                from transformers import AutoProcessor, DiaForConditionalGeneration
                
                # Check if model is available locally first
                if models_path.exists():
                    # Find the actual model path in the cache structure
                    model_cache_path = models_path / "models--nari-labs--Dia-1.6B-0626" / "snapshots"
                    if model_cache_path.exists():
                        # Get the latest snapshot directory
                        snapshot_dirs = [d for d in model_cache_path.iterdir() if d.is_dir()]
                        if snapshot_dirs:
                            actual_model_path = snapshot_dirs[0]  # Use the first (should be only) snapshot
                            logger.info(f"Loading local Dia TTS model from: {actual_model_path}")
                            
                            # Load processor and model separately
                            tts_processor = AutoProcessor.from_pretrained(
                                str(actual_model_path),
                                local_files_only=True
                            )
                            tts_model = DiaForConditionalGeneration.from_pretrained(
                                str(actual_model_path),
                                local_files_only=True
                            )
                            
                            tts_model = tts_model.to(device)
                            tts_model.eval()
                            
                            # Set global variables
                            globals()['tts_processor'] = tts_processor
                            logger.info(f"✅ Dia TTS loaded successfully on {device}")
                            
                else:
                    logger.info("Dia TTS model not found in ./models/dia-tts/")
                    logger.info("Run setup.py to download the TTS model")
                    tts_model = None
                
            except Exception as e:
                logger.error(f"Failed to setup Dia TTS: {e}")
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
        
        prompt = f"""You are an audiobook narrator editor. Add ONLY emotional cues in parentheses to the following text. Do NOT change, rephrase, or add any other words. Only insert emotion annotations like (laughs), (sighs), (whispers), (pauses), (excited), (sad) where appropriate.

Original text: "{text}"

Return ONLY the original text with added emotion annotations in parentheses:"""
        
        # Call Ollama API
        response = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": annotation_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": min(len(text) + 50, 150),  # Limit output length
                "stop": ["\n", "Text:", "Original:", "Note:"]  # Stop tokens
            }
        }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            enhanced_text = result.get("response", "").strip()
            
            # Clean up common AI response artifacts
            enhanced_text = enhanced_text.replace('"', '').strip()
            if enhanced_text.startswith(text):
                enhanced_text = enhanced_text[len(text):].strip()
                if enhanced_text:
                    return text + " " + enhanced_text
            
            # Validate that the response contains the original text
            if text.lower() in enhanced_text.lower() and len(enhanced_text) <= len(text) * 1.5:
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
    global tts_model, tts_processor
    
    if tts_model is None:
        raise HTTPException(status_code=503, detail="TTS model not available. Please ensure Dia TTS is properly installed.")
        
    if tts_processor is None:
        raise HTTPException(status_code=503, detail="TTS processor not available")
        
    import time
    start_time = time.time()
    logger.info(f"🎵 Generating audio for text: {text[:50]}...")
    logger.info(f"📊 Text length: {len(text)} characters")
    
    # Preprocess text for Dia TTS
    processed_text = preprocess_text_for_dia(text)
    
    try:
        # Process input text
        prep_start = time.time()
        logger.info("🔄 Processing input text...")
        inputs = tts_processor(text=[processed_text], padding=True, return_tensors="pt").to(device)
        prep_time = time.time() - prep_start
        logger.info(f"✅ Input processed in {prep_time:.2f}s")
        
        # Generate audio with Dia TTS
        gen_start = time.time()
        logger.info("🎶 Generating audio tokens...")
        
        # Calculate adaptive max_tokens based on text length
        # Audio models need substantial tokens for proper speech generation
        char_count = len(processed_text)
        base_tokens = char_count * 25  # Increased to 25 tokens per character
        max_tokens = max(1536, min(base_tokens, 3072))  # Min 1536 for proper speech, max 3072
        
        logger.info(f"📊 Text: {char_count} chars → Using {max_tokens} tokens (ratio: {max_tokens/char_count:.1f}:1)")
        logger.info(f"📝 Processed text: '{processed_text}'")
        
        generated_tokens = 0
        
        # Override the model's forward pass to track progress
        original_forward = tts_model.forward
        
        def forward_with_progress(*args, **kwargs):
            nonlocal generated_tokens
            generated_tokens += 1
            
            # Log progress every 50 tokens
            if generated_tokens % 50 == 0:
                elapsed = time.time() - gen_start
                progress_pct = (generated_tokens / max_tokens) * 100
                speed = generated_tokens / elapsed if elapsed > 0 else 0
                eta = (max_tokens - generated_tokens) / speed if speed > 0 else 0
                logger.info(f"🔄 Progress: {generated_tokens}/{max_tokens} ({progress_pct:.1f}%) | Speed: {speed:.1f} tok/s | ETA: {eta:.1f}s")
            
            return original_forward(*args, **kwargs)
        
        # Patch the forward method temporarily
        tts_model.forward = forward_with_progress
        
        try:
            with torch.no_grad():
                outputs = tts_model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    guidance_scale=3.0,
                    temperature=1.8,
                    top_p=0.90,
                    top_k=45
                )
        finally:
            # Restore original forward method
            tts_model.forward = original_forward
        
        gen_time = time.time() - gen_start
        logger.info(f"✅ Audio tokens generated in {gen_time:.2f}s")
        
        # Decode the outputs
        decode_start = time.time()
        logger.info("🔊 Decoding audio...")
        audio_outputs = tts_processor.batch_decode(outputs)
        decode_time = time.time() - decode_start
        logger.info(f"✅ Audio decoded in {decode_time:.2f}s")
        
        # Save to temporary buffer
        save_start = time.time()
        logger.info("💾 Saving audio file...")
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            tts_processor.save_audio(audio_outputs, temp_file.name)
            
            # Read the audio file
            with open(temp_file.name, 'rb') as audio_file:
                audio_bytes = audio_file.read()
            
            # Clean up temp file
            import os
            os.unlink(temp_file.name)
        
        save_time = time.time() - save_start
        total_time = time.time() - start_time
        
        logger.info(f"✅ Audio saved in {save_time:.2f}s")
        logger.info(f"🎉 Total generation time: {total_time:.2f}s")
        logger.info(f"⚡ Speed: {len(text)/total_time:.1f} chars/sec")
        return audio_bytes
        
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate audio: {str(e)}")

def preprocess_text_for_dia(text: str) -> str:
    """Preprocess text for optimal Dia TTS generation based on working pattern"""
    
    # Clean up formatting first
    text = text.replace('\n\n', ' ').replace('\n', ' ').strip()
    
    # If text is very short, pad it with conversational context
    if len(text) < 20:
        # Create a conversation pattern like the working example
        return f"[S2] Here is what you wanted to hear. [S1] {text}. Amazing! [S2] That was perfect."
    
    # For longer text, create natural speaker alternation
    sentences = [s.strip() for s in text.replace('.', '.|').replace('!', '!|').replace('?', '?|').split('|') if s.strip()]
    
    if len(sentences) == 1:
        # Single sentence - wrap in conversation like working example
        return f"[S2] Let me read this for you. [S1] {sentences[0]}. That's great! [S2] Hope you enjoyed that."
    
    # Multiple sentences - alternate speakers naturally
    result = "[S2] "
    current_speaker = "S2"
    
    for i, sentence in enumerate(sentences):
        if i > 0:
            # Switch speaker every 1-2 sentences
            if i % 2 == 1:
                current_speaker = "S1" if current_speaker == "S2" else "S2"
                result += f" [{current_speaker}] "
        
        result += sentence
        
        # Add occasional emotional cues like in working example
        if i == len(sentences) // 2:
            result += ". Amazing!"
    
    # Ensure it ends with speaker alternation like working example
    final_speaker = "S1" if current_speaker == "S2" else "S2"
    result += f" [{final_speaker}] That was excellent."
    
    return result

# Endpoint handlers

if __name__ == "__main__":
    uvicorn.run(
        "backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
