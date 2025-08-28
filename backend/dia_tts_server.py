#!/usr/bin/env python3
"""
Dia TTS Integration Script for Audiobook Studio
"""

import sys
import os
import json
import torch
import torchaudio
from pathlib import Path
import argparse

def setup_dia_model():
    """Initialize and return the Dia TTS model"""
    try:
        # Try importing from local dia installation
        sys.path.append(str(Path.cwd() / 'dia'))
        
        # For HuggingFace Transformers integration
        from transformers import AutoModel, AutoTokenizer
        
        model_name = "nari-labs/Dia-1.6B-0626"
        print(f"Loading Dia TTS model: {model_name}")
        
        # Load model and tokenizer
        model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        
        # Move to GPU if available
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)
        model.eval()
        
        print(f"Model loaded successfully on {device}")
        return model, tokenizer, device
        
    except Exception as e:
        print(f"Error loading Dia model: {e}")
        print("Please ensure Dia TTS is properly installed")
        return None, None, None

def generate_audio(text: str, output_path: str, model=None, tokenizer=None, device=None):
    """Generate audio from text using Dia TTS"""
    
    if model is None or tokenizer is None:
        print("Model not loaded, generating mock audio...")
        generate_mock_audio(text, output_path)
        return
    
    try:
        print(f"Generating audio for text: {text[:100]}...")
        
        # Preprocess text for Dia TTS
        processed_text = preprocess_text(text)
        
        # Tokenize input
        inputs = tokenizer(processed_text, return_tensors="pt", padding=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate audio tokens
        with torch.no_grad():
            audio_tokens = model.generate(
                **inputs,
                max_length=2048,  # Adjust based on text length
                do_sample=True,
                temperature=0.7,
                pad_token_id=tokenizer.pad_token_id
            )
        
        # Decode audio tokens to waveform
        # Note: This is a simplified version - check Dia docs for exact decoding
        audio_waveform = model.decode_audio(audio_tokens)
        
        # Save audio file
        sample_rate = 24000  # Dia TTS sample rate
        torchaudio.save(output_path, audio_waveform.cpu(), sample_rate)
        
        print(f"Audio saved to: {output_path}")
        
    except Exception as e:
        print(f"Error generating audio: {e}")
        print("Falling back to mock audio generation...")
        generate_mock_audio(text, output_path)

def preprocess_text(text: str) -> str:
    """Preprocess text for optimal Dia TTS generation"""
    
    # Ensure proper speaker tags
    if not text.strip().startswith('[S1]') and not text.strip().startswith('[S2]'):
        text = f"[S1] {text}"
    
    # Clean up formatting
    text = text.replace('\n\n', ' [S1] ')
    text = text.replace('\n', ' ')
    
    # Ensure alternating speakers if dialogue is detected
    # This is a simplified approach - you might want more sophisticated detection
    if '[S2]' in text and not text.count('[S1]') == text.count('[S2]'):
        # Balance speaker tags for better audio quality
        pass
    
    return text

def generate_mock_audio(text: str, output_path: str):
    """Generate mock audio for testing purposes"""
    import numpy as np
    
    print("Generating mock audio (replace with actual Dia TTS)")
    
    # Simple sine wave generation
    sample_rate = 24000
    duration = min(len(text) / 10, 30)  # Rough estimate
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Generate a simple tone that varies based on text
    frequency = 440 + (hash(text) % 200)  # Vary frequency based on text
    audio = 0.3 * np.sin(2 * np.pi * frequency * t)
    
    # Add some variation to make it more interesting
    audio = audio * (1 + 0.3 * np.sin(2 * np.pi * 2 * t))
    
    # Convert to tensor and save
    audio_tensor = torch.FloatTensor(audio).unsqueeze(0)
    torchaudio.save(output_path, audio_tensor, sample_rate)

def main():
    parser = argparse.ArgumentParser(description='Generate audio using Dia TTS')
    parser.add_argument('--text', required=True, help='Text to convert to speech')
    parser.add_argument('--output', required=True, help='Output audio file path')
    parser.add_argument('--mock', action='store_true', help='Use mock audio generation')
    
    args = parser.parse_args()
    
    if args.mock:
        generate_mock_audio(args.text, args.output)
    else:
        # Load model
        model, tokenizer, device = setup_dia_model()
        
        # Generate audio
        generate_audio(args.text, args.output, model, tokenizer, device)

if __name__ == "__main__":
    main()
