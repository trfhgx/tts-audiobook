'use client'

import { motion } from 'framer-motion'
import { Settings, Volume2, Gauge, Mic, Upload, X } from 'lucide-react'
import { useState } from 'react'

interface TTSSettingsProps {
  settings: {
    voice: string
    exaggeration: number
    cfg_weight: number
    quality: string
  }
  onChange: (settings: any) => void
}

export default function TTSSettings({ settings, onChange }: TTSSettingsProps) {
  const [uploadedVoice, setUploadedVoice] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [showUpload, setShowUpload] = useState(false)

  const updateSetting = (key: string, value: any) => {
    onChange({
      ...settings,
      [key]: value
    })
  }

  const voices = [
    { 
      id: 'default', 
      name: 'Default Voice', 
      description: 'Built-in Chatterbox voice - high quality' 
    },
    { 
      id: 'female_sample', 
      name: 'Female Voice Clone', 
      description: 'Clone from female voice sample',
      audioFile: 'female_sample.wav'
    },
    { 
      id: 'male_sample', 
      name: 'Male Voice Clone', 
      description: 'Clone from male voice sample',
      audioFile: 'male_sample.wav'
    },
    { 
      id: 'upload', 
      name: 'Upload Custom Voice', 
      description: 'Upload your own voice sample to clone (3-10 seconds)' 
    }
  ]

  const qualities = [
    { id: 'high', name: 'High Quality', description: 'Best audio quality (slower)' },
    { id: 'medium', name: 'Medium Quality', description: 'Balanced quality and speed' },
    { id: 'fast', name: 'Fast', description: 'Lower quality but faster' }
  ]

  const handleVoiceUpload = async (file: File) => {
    if (!file) return
    
    // Validate file type
    if (!file.type.startsWith('audio/')) {
      alert('Please upload an audio file (WAV, MP3, etc.)')
      return
    }
    
    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('File too large. Please upload an audio file under 10MB.')
      return
    }

    setIsUploading(true)
    
    try {
      const formData = new FormData()
      formData.append('voice_file', file)
      
      const response = await fetch('http://localhost:8000/upload_voice', {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) {
        throw new Error('Failed to upload voice sample')
      }
      
      const result = await response.json()
      setUploadedVoice(result.voice_id)
      updateSetting('voice', result.voice_id)
      setShowUpload(false)
      alert('Voice sample uploaded successfully!')
      
    } catch (error) {
      console.error('Upload error:', error)
      alert('Failed to upload voice sample. Please try again.')
    } finally {
      setIsUploading(false)
    }
  }

  const handleVoiceSelection = (voiceId: string) => {
    if (voiceId === 'upload') {
      setShowUpload(true)
    } else {
      updateSetting('voice', voiceId)
      setShowUpload(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      className="border border-gray-200 rounded-lg p-4 bg-gray-50"
    >
      <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <Settings className="w-5 h-5 text-primary-500" />
        Chatterbox TTS Settings
      </h3>

      <div className="space-y-6">
        {/* Voice Selection */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Mic className="w-5 h-5 text-primary-500" />
            <label className="font-medium text-gray-700">Voice Options</label>
          </div>
          <div className="grid grid-cols-1 gap-2">
            {voices.map((voice) => (
              <motion.button
                key={voice.id}
                onClick={() => handleVoiceSelection(voice.id)}
                className={`p-3 rounded-lg border-2 transition-all text-left ${
                  settings.voice === voice.id
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="font-medium text-gray-800">{voice.name}</div>
                <div className="text-sm text-gray-600">{voice.description}</div>
                {voice.id === 'upload' && uploadedVoice && (
                  <div className="text-xs text-green-600 mt-1">
                    ✓ Custom voice uploaded: {uploadedVoice}
                  </div>
                )}
              </motion.button>
            ))}
          </div>

          {/* File Upload Modal */}
          {showUpload && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mt-4 p-4 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50"
            >
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-gray-800 flex items-center gap-2">
                  <Upload className="w-4 h-4" />
                  Upload Voice Sample
                </h4>
                <button
                  onClick={() => setShowUpload(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              
              <div className="space-y-3">
                <div className="text-sm text-gray-600">
                  <div>📋 <strong>Requirements:</strong></div>
                  <ul className="ml-4 mt-1 space-y-1">
                    <li>• 5-10 seconds of clear speech</li>
                    <li>• WAV or MP3 format</li>
                    <li>• No background noise</li>
                    <li>• Natural speaking pace</li>
                  </ul>
                </div>
                
                <input
                  type="file"
                  accept="audio/*"
                  onChange={(e) => {
                    const file = e.target.files?.[0]
                    if (file) handleVoiceUpload(file)
                  }}
                  disabled={isUploading}
                  className="w-full p-2 border border-gray-300 rounded-lg file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                />
                
                {isUploading && (
                  <div className="flex items-center gap-2 text-primary-600">
                    <div className="animate-spin w-4 h-4 border-2 border-primary-600 border-t-transparent rounded-full"></div>
                    <span className="text-sm">Uploading voice sample...</span>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </div>

        {/* Exaggeration Slider */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Gauge className="w-5 h-5 text-blue-500" />
            <label className="font-medium text-gray-700">
              Exaggeration Level: {settings.exaggeration}
            </label>
          </div>
          <input
            type="range"
            min="0.0"
            max="1.0"
            step="0.1"
            value={settings.exaggeration}
            onChange={(e) => updateSetting('exaggeration', parseFloat(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
          />
          <div className="flex justify-between text-xs text-gray-500">
            <span>0.0 (Neutral)</span>
            <span>0.5 (Balanced)</span>
            <span>1.0 (Very Expressive)</span>
          </div>
        </div>

        {/* CFG Weight Slider */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Volume2 className="w-5 h-5 text-green-500" />
            <label className="font-medium text-gray-700">
              CFG Weight: {settings.cfg_weight}
            </label>
          </div>
          <input
            type="range"
            min="0.1"
            max="1.0"
            step="0.1"
            value={settings.cfg_weight}
            onChange={(e) => updateSetting('cfg_weight', parseFloat(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
          />
          <div className="flex justify-between text-xs text-gray-500">
            <span>0.1 (Fast, Natural)</span>
            <span>0.5 (Balanced)</span>
            <span>1.0 (Slower, Controlled)</span>
          </div>
        </div>

        {/* Quality Selection */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Volume2 className="w-5 h-5 text-green-500" />
            <label className="font-medium text-gray-700">Quality</label>
          </div>
          <div className="grid grid-cols-1 gap-2">
            {qualities.map((quality) => (
              <motion.button
                key={quality.id}
                onClick={() => updateSetting('quality', quality.id)}
                className={`p-3 rounded-lg border-2 transition-all text-left ${
                  settings.quality === quality.id
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="font-medium text-gray-800">{quality.name}</div>
                <div className="text-sm text-gray-600">{quality.description}</div>
              </motion.button>
            ))}
          </div>
        </div>
      </div>

      {/* Chatterbox Info */}
      <div className="mt-6 p-3 bg-white rounded-lg border border-gray-200">
        <h4 className="text-sm font-medium text-gray-700 mb-2">✨ Chatterbox TTS Features</h4>
        <div className="text-sm text-gray-600 space-y-1">
          <div>• No complex formatting needed - just plain text!</div>
          <div>• State-of-the-art voice quality with natural prosody</div>
          <div>• Automatic emotion detection from context</div>
          <div>• Voice cloning capabilities (coming soon)</div>
        </div>
      </div>
    </motion.div>
  )
}
