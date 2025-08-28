#!/usr/bin/env python3
"""
Test script for local annotation
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from local_annotator import LocalAnnotator

def test_annotation():
    print("🧪 Testing Local Annotation System\n")
    
    # Test text
    test_text = "[S1] Hello there! This is a test of our local annotation system. [S2] That sounds amazing! I can't wait to see how it works. [S1] Well, let me tell you all about it..."
    
    # Test different models
    models_to_test = ['rule-based', 'tiny-llama', 'ollama']
    
    settings = {
        'addEmotions': True,
        'addPauses': True,
        'emotionIntensity': 0.7
    }
    
    for model_type in models_to_test:
        print(f"Testing {model_type} model:")
        print("-" * 40)
        
        try:
            annotator = LocalAnnotator(model_type=model_type)
            result = annotator.annotate(test_text, settings)
            
            print(f"Original: {test_text[:80]}...")
            print(f"Result: {result[:80]}...")
            print(f"Status: ✅ Working")
            
        except Exception as e:
            print(f"Status: ❌ Error - {e}")
        
        print()

if __name__ == "__main__":
    test_annotation()
