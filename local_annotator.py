#!/usr/bin/env python3
"""
Local AI Annotation Service for Audiobook Studio
Uses small local models to add emotional annotations
"""

import sys
import json
import re
import random
from typing import List, Dict, Tuple
import argparse
from pathlib import Path

# Try to import transformers for local model
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    import torch
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("Transformers not available, using rule-based fallback")

class LocalAnnotator:
    def __init__(self, model_type="rule-based"):
        self.model_type = model_type
        self.model = None
        self.tokenizer = None
        
        if model_type == "phi-2" and HF_AVAILABLE:
            self.load_phi2_model()
        elif model_type == "tiny-llama" and HF_AVAILABLE:
            self.load_tiny_llama()
        elif model_type == "ollama":
            self.setup_ollama()
        else:
            print(f"Using rule-based annotation (model_type: {model_type})")
    
    def load_phi2_model(self):
        """Load Microsoft's Phi-2 model (2.7B params, good for local use)"""
        try:
            model_name = "microsoft/phi-2"
            print(f"Loading {model_name}...")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                trust_remote_code=True,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            print("Phi-2 model loaded successfully!")
            
        except Exception as e:
            print(f"Failed to load Phi-2: {e}")
            self.model_type = "rule-based"
    
    def load_tiny_llama(self):
        """Load TinyLlama model (1.1B params, very lightweight)"""
        try:
            model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
            print(f"Loading {model_name}...")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            print("TinyLlama model loaded successfully!")
            
        except Exception as e:
            print(f"Failed to load TinyLlama: {e}")
            self.model_type = "rule-based"
    
    def setup_ollama(self):
        """Setup Ollama connection for local models"""
        try:
            import requests
            
            # Test if Ollama is running
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                
                # Look for small models
                preferred_models = ["llama3.2:1b", "phi3:3.8b", "gemma2:2b", "qwen2:1.5b"]
                available_model = None
                
                for model in preferred_models:
                    if any(m["name"].startswith(model) for m in models):
                        available_model = model
                        break
                
                if available_model:
                    self.ollama_model = available_model
                    print(f"Using Ollama model: {available_model}")
                else:
                    print("No suitable Ollama models found, using rule-based")
                    self.model_type = "rule-based"
            else:
                print("Ollama not available, using rule-based")
                self.model_type = "rule-based"
                
        except Exception as e:
            print(f"Ollama setup failed: {e}")
            self.model_type = "rule-based"
    
    def annotate_with_model(self, text: str, intensity: float) -> str:
        """Use AI model to add emotional annotations"""
        
        if self.model_type == "ollama":
            return self.annotate_with_ollama(text, intensity)
        elif self.model and self.tokenizer:
            return self.annotate_with_hf_model(text, intensity)
        else:
            return self.annotate_with_rules(text, intensity)
    
    def annotate_with_hf_model(self, text: str, intensity: float) -> str:
        """Use HuggingFace model for annotation"""
        try:
            intensity_desc = "subtle" if intensity < 0.4 else "moderate" if intensity < 0.7 else "expressive"
            
            prompt = f"""Add emotional annotations to make this text more engaging for audiobook narration.
Rules:
- Add emotions like (laughs), (sighs), (whispers), (gasps), etc.
- Use {intensity_desc} emotions
- Keep original text unchanged, only add annotations in parentheses
- Don't overuse - be strategic

Text: {text}

Annotated version:"""

            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
            
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=min(len(text) + 100, 300),
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract the annotated version
            if "Annotated version:" in result:
                annotated = result.split("Annotated version:")[-1].strip()
                return annotated if annotated else self.annotate_with_rules(text, intensity)
            else:
                return self.annotate_with_rules(text, intensity)
                
        except Exception as e:
            print(f"Model annotation failed: {e}")
            return self.annotate_with_rules(text, intensity)
    
    def annotate_with_ollama(self, text: str, intensity: float) -> str:
        """Use Ollama for annotation"""
        try:
            import requests
            
            intensity_desc = "subtle" if intensity < 0.4 else "moderate" if intensity < 0.7 else "expressive"
            
            prompt = f"""Add {intensity_desc} emotional annotations to this text for audiobook narration. Only add emotions in parentheses like (laughs), (sighs), (whispers). Keep the original text exactly the same.

Text: {text}

Annotated:"""

            data = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": min(len(text) + 50, 200)
                }
            }
            
            response = requests.post("http://localhost:11434/api/generate", json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json().get("response", "").strip()
                return result if result else self.annotate_with_rules(text, intensity)
            else:
                return self.annotate_with_rules(text, intensity)
                
        except Exception as e:
            print(f"Ollama annotation failed: {e}")
            return self.annotate_with_rules(text, intensity)
    
    def annotate_with_rules(self, text: str, intensity: float) -> str:
        """Rule-based annotation as fallback"""
        print("Using rule-based annotation")
        
        annotated = text
        
        # Define emotion patterns and their probabilities based on intensity
        emotion_rules = [
            # Pattern, replacement, min_intensity
            (r'\b(ha ha|haha|funny|joke|humor)\b', r'\1 (laughs)', 0.2),
            (r'\b(oh dear|oh no|unfortunately|sadly)\b', r'\1 (sighs)', 0.3),
            (r'\b(wow|amazing|incredible|unbelievable)\b', r'\1 (gasps)', 0.4),
            (r'\b(whisper|quietly|softly)\b', r'\1 (whispers)', 0.1),
            (r'\b(ahem|um|well)\b', r'\1 (clears throat)', 0.3),
            (r'\b(tired|exhausted|weary)\b', r'\1 (sighs)', 0.2),
            (r'\b(surprise|shocked|startled)\b', r'\1 (gasps)', 0.4),
            (r'\b(cough|cold|sick)\b', r'\1 (coughs)', 0.3),
        ]
        
        # Apply rules based on intensity
        for pattern, replacement, min_intensity in emotion_rules:
            if intensity >= min_intensity and random.random() < intensity:
                annotated = re.sub(pattern, replacement, annotated, flags=re.IGNORECASE)
        
        # Add pauses at sentence endings
        if intensity > 0.3:
            annotated = re.sub(r'([.!?])\s+', r'\1 (pauses) ', annotated)
        
        # Add breathing at paragraph breaks
        if intensity > 0.5:
            annotated = re.sub(r'\n\n+', r' (inhales) ', annotated)
        
        return annotated
    
    def annotate(self, text: str, settings: Dict) -> str:
        """Main annotation method"""
        if not settings.get('addEmotions', False):
            return text
        
        intensity = settings.get('emotionIntensity', 0.5)
        
        # Process text in chunks to avoid overwhelming small models
        chunks = self.split_text_into_chunks(text, max_length=200)
        annotated_chunks = []
        
        for chunk in chunks:
            annotated_chunk = self.annotate_with_model(chunk, intensity)
            annotated_chunks.append(annotated_chunk)
        
        result = ' '.join(annotated_chunks)
        
        # Add natural pauses if enabled
        if settings.get('addPauses', False):
            result = self.add_natural_pauses(result)
        
        return result
    
    def split_text_into_chunks(self, text: str, max_length: int = 200) -> List[str]:
        """Split text into manageable chunks"""
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) < max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text]
    
    def add_natural_pauses(self, text: str) -> str:
        """Add natural pauses at punctuation"""
        # Add brief pauses at commas
        text = re.sub(r',(\s+)', r', (brief pause)\1', text)
        
        # Add pauses at sentence endings (if not already added)
        text = re.sub(r'([.!?])(\s+)(?!\()', r'\1 (pauses)\2', text)
        
        return text

def main():
    parser = argparse.ArgumentParser(description='Local AI annotation for audiobook studio')
    parser.add_argument('--text', required=True, help='Text to annotate')
    parser.add_argument('--intensity', type=float, default=0.5, help='Emotion intensity (0-1)')
    parser.add_argument('--add-emotions', action='store_true', help='Add emotional annotations')
    parser.add_argument('--add-pauses', action='store_true', help='Add natural pauses')
    parser.add_argument('--model', choices=['rule-based', 'phi-2', 'tiny-llama', 'ollama'], 
                        default='tiny-llama', help='Model to use for annotation')
    
    args = parser.parse_args()
    
    # Create settings dict
    settings = {
        'addEmotions': args.add_emotions,
        'addPauses': args.add_pauses,
        'emotionIntensity': args.intensity
    }
    
    # Initialize annotator
    annotator = LocalAnnotator(model_type=args.model)
    
    # Annotate text
    result = annotator.annotate(args.text, settings)
    
    # Output as JSON
    output = {
        'original': args.text,
        'annotated': result,
        'model_used': annotator.model_type,
        'settings': settings
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
