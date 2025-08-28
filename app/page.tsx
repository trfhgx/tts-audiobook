'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  BookOpen, 
  Upload, 
  Wand2, 
  Play, 
  Download,
  Sparkles,
  Volume2,
  FileText,
  Settings,
  Star
} from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import TextInput from '@/components/TextInput'
import AudioPreview from '@/components/AudioPreview'
import AnnotationSettings from '@/components/AnnotationSettings'
import toast from 'react-hot-toast'

interface ProcessingStep {
  id: string
  title: string
  description: string
  icon: any
  completed: boolean
  processing: boolean
}

export default function Home() {
  const [text, setText] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [currentStep, setCurrentStep] = useState(0)
  const [annotationSettings, setAnnotationSettings] = useState({
    addEmotions: true,
    emotionIntensity: 0.7,
    addPauses: true,
    speakerVariation: true
  })

  const processingSteps: ProcessingStep[] = [
    {
      id: 'analyze',
      title: 'Analyzing Text',
      description: 'Understanding context and structure',
      icon: FileText,
      completed: false,
      processing: false
    },
    {
      id: 'annotate',
      title: 'Adding Emotions',
      description: 'Inserting (laughs), (sighs), and pauses',
      icon: Sparkles,
      completed: false,
      processing: false
    },
    {
      id: 'synthesize',
      title: 'Generating Audio',
      description: 'Creating high-quality speech with Dia TTS',
      icon: Volume2,
      completed: false,
      processing: false
    },
    {
      id: 'finalize',
      title: 'Finalizing',
      description: 'Preparing your audiobook',
      icon: Star,
      completed: false,
      processing: false
    }
  ]

  const handleGenerateAudio = async () => {
    if (!text.trim()) {
      toast.error('Please enter some text first!')
      return
    }

    setIsProcessing(true)
    setCurrentStep(0)

    try {
      // Simulate processing steps
      for (let i = 0; i < processingSteps.length; i++) {
        setCurrentStep(i)
        
        // Simulate processing time
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        if (i === processingSteps.length - 1) {
          // Final step - call the actual API
          const response = await fetch('/api/generate-audio', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              text,
              settings: annotationSettings
            }),
          })

          if (!response.ok) {
            throw new Error('Failed to generate audio')
          }

          const audioBlob = await response.blob()
          const audioUrl = URL.createObjectURL(audioBlob)
          setAudioUrl(audioUrl)
          
          toast.success('🎉 Your audiobook is ready!')
        }
      }
    } catch (error) {
      console.error('Error generating audio:', error)
      toast.error('Something went wrong. Please try again!')
    } finally {
      setIsProcessing(false)
      setCurrentStep(0)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8 relative z-10">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-12"
      >
        <div className="inline-flex items-center gap-3 mb-6">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          >
            <BookOpen className="w-12 h-12 text-primary-500" />
          </motion.div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent">
            Audiobook Studio
          </h1>
        </div>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Transform your text into engaging audiobooks with AI-powered emotional annotations and ultra-realistic voice synthesis
        </p>
      </motion.div>

      <div className="max-w-6xl mx-auto grid lg:grid-cols-2 gap-8">
        {/* Left Panel - Input */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Wand2 className="w-6 h-6 text-primary" />
                Create Your Audiobook
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">

            <TextInput 
              value={text}
              onChange={setText}
              placeholder="Paste your text here or upload a file..."
            />

            <AnnotationSettings 
              settings={annotationSettings}
              onChange={setAnnotationSettings}
            />

            <Button
              onClick={handleGenerateAudio}
              disabled={isProcessing || !text.trim()}
              className="w-full"
              size="lg"
            >
              <div className="flex items-center justify-center gap-2">
                {isProcessing ? (
                  <>
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    >
                      <Sparkles className="w-5 h-5" />
                    </motion.div>
                    Processing...
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5" />
                    Generate Audiobook
                  </>
                )}
              </div>
            </Button>
            </CardContent>
          </Card>
        </motion.div>

        {/* Right Panel - Output */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
        >
          {isProcessing ? (
            <div className="card">
              <h3 className="text-xl font-bold text-gray-800 mb-6">Processing Your Audiobook</h3>
              <div className="space-y-4">
                {processingSteps.map((step, index) => (
                  <motion.div
                    key={step.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`flex items-center gap-4 p-4 rounded-lg transition-all duration-300 ${
                      index === currentStep 
                        ? 'bg-primary-50 border-2 border-primary-200' 
                        : index < currentStep 
                          ? 'bg-green-50 border-2 border-green-200'
                          : 'bg-gray-50 border border-gray-200'
                    }`}
                  >
                    <div className={`p-2 rounded-full ${
                      index === currentStep 
                        ? 'bg-primary-500 text-white' 
                        : index < currentStep 
                          ? 'bg-green-500 text-white'
                          : 'bg-gray-300 text-gray-600'
                    }`}>
                      <step.icon className="w-5 h-5" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-800">{step.title}</h4>
                      <p className="text-sm text-gray-600">{step.description}</p>
                    </div>
                    {index === currentStep && (
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="w-5 h-5 border-2 border-primary-500 border-t-transparent rounded-full"
                      />
                    )}
                  </motion.div>
                ))}
              </div>
            </div>
          ) : audioUrl ? (
            <AudioPreview audioUrl={audioUrl} />
          ) : (
            <div className="card text-center">
              <div className="py-12">
                <motion.div
                  animate={{ y: [0, -10, 0] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <Upload className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                </motion.div>
                <h3 className="text-xl font-semibold text-gray-600 mb-2">Ready to Create</h3>
                <p className="text-gray-500">Enter your text and click generate to create your audiobook</p>
              </div>
            </div>
          )}
        </motion.div>
      </div>

      {/* Features Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="mt-16"
      >
        <h2 className="text-3xl font-bold text-center text-gray-800 mb-12">
          Why Choose Audiobook Studio?
        </h2>
        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          {[
            {
              icon: Sparkles,
              title: "Smart Annotations",
              description: "AI automatically adds emotional cues like (laughs), (sighs), and natural pauses"
            },
            {
              icon: Volume2,
              title: "Ultra-Realistic Voice",
              description: "Powered by Dia TTS for natural, engaging speech synthesis"
            },
            {
              icon: Settings,
              title: "Full Customization",
              description: "Control emotion intensity, speaker variation, and audio settings"
            }
          ].map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 + index * 0.1 }}
              className="text-center"
            >
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-primary-500 to-purple-500 rounded-full mb-4">
                <feature.icon className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}
