# Voice Cloning Guide

## Overview

Chatterbox TTS supports voice cloning from audio samples. Instead of pre-made voice options, you can clone any voice by providing a short audio sample.

## Voice Sample Directory

Voice samples are stored in: `voice_samples/`

## Adding Voice Samples

### 1. Prepare Audio Samples
- **Length**: 3-10 seconds of clean speech
- **Format**: WAV files recommended (MP3 also supported)
- **Quality**: Clear audio without background noise
- **Content**: Natural speech at normal pace

### 2. Add Sample Files
Place your audio files in the `voice_samples/` directory:

```
voice_samples/
├── female_sample.wav    # For female voice option
├── male_sample.wav      # For male voice option
└── custom_voice.wav     # Add more as needed
```

### 3. Built-in Sample Names
The frontend currently recognizes:
- `female_sample.wav` - Female voice clone
- `male_sample.wav` - Male voice clone

## API Endpoints

### Get Available Voices
```bash
GET /voices
```
Returns list of available voices and their status.

### Upload Custom Voice
```bash
POST /upload_voice
```
Upload a custom voice sample for cloning.

### Example Response
```json
{
  "voices": [
    {
      "id": "default",
      "name": "Default Voice", 
      "available": true,
      "type": "built-in"
    },
    {
      "id": "female_sample",
      "name": "Female Voice Clone",
      "available": true,
      "type": "sample",
      "path": "/path/to/voice_samples/female_sample.wav"
    }
  ]
}
```

## Usage Examples

### Default Voice
```json
{
  "voice": "default",
  "exaggeration": 0.5,
  "cfg_weight": 0.5
}
```

### Female Voice Clone
```json
{
  "voice": "female_sample", 
  "exaggeration": 0.7,
  "cfg_weight": 0.3
}
```

## Best Practices

1. **Sample Quality**: Use high-quality, clear recordings
2. **Speaking Style**: Natural conversational speech works best
3. **Length**: 5-8 seconds is optimal
4. **Consistency**: Same speaker throughout the sample
5. **Exaggeration**: Try values 0.3-0.7 for different styles
6. **CFG Weight**: Lower values (0.3) for more natural pacing

## Obtaining Voice Samples

### Option 1: Record Your Own
- Use any recording application
- Speak naturally for 5-10 seconds
- Save as WAV file

### Option 2: Extract from Existing Audio
- Use tools like Audacity
- Extract clean speech segments
- Export as WAV format

### Option 3: Use AI-Generated Samples
- Generate with other TTS systems
- Use as voice cloning source
- Ensure high quality output

## Updating Voice Samples

1. Add new files to `voice_samples/` directory
2. Restart the backend server
3. Check `/voices` endpoint to confirm availability
4. Test with new voice settings

## Technical Specifications

- Voice samples remain local to your server
- Chatterbox respects original speaker characteristics
- Clone quality depends on sample quality
- Experiment with different `exaggeration` and `cfg_weight` values for optimal results
