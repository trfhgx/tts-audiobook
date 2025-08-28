'use client'

import { motion } from 'framer-motion'
import { Settings, Sparkles, Clock, Users } from 'lucide-react'

interface AnnotationSettingsProps {
  settings: {
    addEmotions: boolean
    emotionIntensity: number
    addPauses: boolean
    speakerVariation: boolean
  }
  onChange: (settings: any) => void
}

export default function AnnotationSettings({ settings, onChange }: AnnotationSettingsProps) {
  const updateSetting = (key: string, value: any) => {
    onChange({
      ...settings,
      [key]: value
    })
  }

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      className="border border-gray-200 rounded-lg p-4 bg-gray-50"
    >
      <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <Settings className="w-5 h-5 text-primary-500" />
        Audio Settings
      </h3>

      <div className="space-y-4">
        {/* Add Emotions Toggle */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Sparkles className="w-5 h-5 text-accent-500" />
            <div>
              <label className="font-medium text-gray-700">Smart Emotions</label>
              <p className="text-sm text-gray-600">Add (laughs), (sighs), etc. automatically</p>
            </div>
          </div>
          <motion.button
            onClick={() => updateSetting('addEmotions', !settings.addEmotions)}
            className={`relative w-12 h-6 rounded-full transition-colors duration-200 ${
              settings.addEmotions ? 'bg-primary-500' : 'bg-gray-300'
            }`}
            whileTap={{ scale: 0.95 }}
          >
            <motion.div
              className="absolute top-1 w-4 h-4 bg-white rounded-full shadow-sm"
              animate={{ x: settings.addEmotions ? 24 : 2 }}
              transition={{ duration: 0.2 }}
            />
          </motion.button>
        </div>

        {/* Emotion Intensity Slider */}
        {settings.addEmotions && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="ml-8 space-y-2"
          >
            <label className="text-sm font-medium text-gray-700">
              Emotion Intensity: {Math.round(settings.emotionIntensity * 100)}%
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={settings.emotionIntensity}
              onChange={(e) => updateSetting('emotionIntensity', parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>Subtle</span>
              <span>Dramatic</span>
            </div>
          </motion.div>
        )}

        {/* Add Pauses Toggle */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Clock className="w-5 h-5 text-blue-500" />
            <div>
              <label className="font-medium text-gray-700">Natural Pauses</label>
              <p className="text-sm text-gray-600">Add pauses at punctuation marks</p>
            </div>
          </div>
          <motion.button
            onClick={() => updateSetting('addPauses', !settings.addPauses)}
            className={`relative w-12 h-6 rounded-full transition-colors duration-200 ${
              settings.addPauses ? 'bg-primary-500' : 'bg-gray-300'
            }`}
            whileTap={{ scale: 0.95 }}
          >
            <motion.div
              className="absolute top-1 w-4 h-4 bg-white rounded-full shadow-sm"
              animate={{ x: settings.addPauses ? 24 : 2 }}
              transition={{ duration: 0.2 }}
            />
          </motion.button>
        </div>

        {/* Speaker Variation Toggle */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Users className="w-5 h-5 text-green-500" />
            <div>
              <label className="font-medium text-gray-700">Speaker Variation</label>
              <p className="text-sm text-gray-600">Different voices for [S1] and [S2]</p>
            </div>
          </div>
          <motion.button
            onClick={() => updateSetting('speakerVariation', !settings.speakerVariation)}
            className={`relative w-12 h-6 rounded-full transition-colors duration-200 ${
              settings.speakerVariation ? 'bg-primary-500' : 'bg-gray-300'
            }`}
            whileTap={{ scale: 0.95 }}
          >
            <motion.div
              className="absolute top-1 w-4 h-4 bg-white rounded-full shadow-sm"
              animate={{ x: settings.speakerVariation ? 24 : 2 }}
              transition={{ duration: 0.2 }}
            />
          </motion.button>
        </div>
      </div>

      {/* Preview of supported emotions */}
      <div className="mt-6 p-3 bg-white rounded-lg border border-gray-200">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Supported Emotions</h4>
        <div className="flex flex-wrap gap-2 text-xs">
          {[
            '(laughs)', '(sighs)', '(whispers)', '(gasps)', '(coughs)', 
            '(clears throat)', '(chuckles)', '(groans)', '(inhales)', '(exhales)'
          ].map((emotion, index) => (
            <span
              key={index}
              className="px-2 py-1 bg-gray-100 text-gray-600 rounded-full"
            >
              {emotion}
            </span>
          ))}
        </div>
      </div>
    </motion.div>
  )
}
