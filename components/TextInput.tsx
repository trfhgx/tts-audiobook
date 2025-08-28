'use client'

import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { Upload, FileText, X } from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'

interface TextInputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
}

export default function TextInput({ value, onChange, placeholder }: TextInputProps) {
  const [dragActive, setDragActive] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const onDrop = (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      if (file.type.startsWith('text/') || file.name.endsWith('.txt') || file.name.endsWith('.md')) {
        const reader = new FileReader()
        reader.onload = (e) => {
          const text = e.target?.result as string
          onChange(text)
          toast.success(`Loaded ${file.name}`)
        }
        reader.readAsText(file)
      } else {
        toast.error('Please upload a text file (.txt, .md)')
      }
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'text/*': []
    },
    multiple: false,
    noClick: true
  })

  const handleClear = () => {
    onChange('')
    toast.success('Text cleared')
  }

  const sampleTexts = [
    {
      title: "Short Story",
      content: `[S1] Once upon a time, in a small village nestled between rolling hills, there lived a young baker named Elena. (sighs) She had always dreamed of creating the perfect loaf of bread. [S2] "Elena, your bread is already wonderful!" her grandmother would say with a warm smile. (chuckles) [S1] But Elena knew she could do better. She spent countless hours experimenting with different ingredients and techniques...`
    },
    {
      title: "Educational Content",
      content: `[S1] Today we're going to explore the fascinating world of artificial intelligence. (clears throat) AI has revolutionized the way we interact with technology. [S2] But what exactly is artificial intelligence? [S1] Well, (pauses) artificial intelligence refers to the simulation of human intelligence in machines that are programmed to think and learn like humans...`
    },
    {
      title: "Dialogue Example",
      content: `[S1] "Are you ready for the big presentation tomorrow?" Sarah asked nervously. (sighs) [S2] "I think so," replied Mark, (chuckles) "though I have to admit I'm a bit nervous too." [S1] "We've prepared so well for this. (inhales) I'm sure we'll do great!" [S2] "You're right. (laughs) Let's get some rest and show them what we've got!"`
    }
  ]

  return (
    <div className="space-y-4">
      {/* File Drop Zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-6 transition-all duration-300 cursor-pointer ${
          isDragActive 
            ? 'border-primary-500 bg-primary-50' 
            : 'border-gray-300 bg-gray-50 hover:border-primary-400 hover:bg-primary-25'
        }`}
      >
        <input {...getInputProps()} />
        <div className="text-center">
          <Upload className={`w-8 h-8 mx-auto mb-2 ${isDragActive ? 'text-primary-500' : 'text-gray-400'}`} />
          <p className={`text-sm ${isDragActive ? 'text-primary-600' : 'text-gray-600'}`}>
            {isDragActive ? 'Drop your text file here' : 'Drag & drop a text file here, or click to select'}
          </p>
          <p className="text-xs text-gray-500 mt-1">Supports .txt and .md files</p>
        </div>
      </div>

      {/* Text Area */}
      <div className="relative">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder || "Enter your text here..."}
          className="w-full h-64 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
        />
        
        {value && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            onClick={handleClear}
            className="absolute top-3 right-3 p-1 bg-gray-200 hover:bg-red-100 rounded-full transition-colors duration-200 group"
            title="Clear text"
          >
            <X className="w-4 h-4 text-gray-600 group-hover:text-red-600" />
          </motion.button>
        )}
        
        <div className="absolute bottom-3 right-3 text-xs text-gray-500">
          {value.length} characters
        </div>
      </div>

      {/* Sample Texts */}
      <div className="space-y-3">
        <h3 className="text-sm font-medium text-gray-700 flex items-center gap-2">
          <FileText className="w-4 h-4" />
          Quick Start Examples
        </h3>
        <div className="grid gap-2">
          {sampleTexts.map((sample, index) => (
            <motion.button
              key={index}
              onClick={() => onChange(sample.content)}
              className="text-left p-3 bg-gray-50 hover:bg-primary-50 border border-gray-200 hover:border-primary-300 rounded-lg transition-all duration-200"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="font-medium text-sm text-gray-800">{sample.title}</div>
              <div className="text-xs text-gray-600 mt-1 line-clamp-2">
                {sample.content.substring(0, 100)}...
              </div>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Format Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-800 mb-2">💡 Formatting Tips</h4>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Use <code className="bg-blue-100 px-1 rounded">[S1]</code> and <code className="bg-blue-100 px-1 rounded">[S2]</code> for different speakers</li>
          <li>• Add emotions like <code className="bg-blue-100 px-1 rounded">(laughs)</code>, <code className="bg-blue-100 px-1 rounded">(sighs)</code>, <code className="bg-blue-100 px-1 rounded">(whispers)</code></li>
          <li>• Keep sections under 20 seconds of speech for best results</li>
        </ul>
      </div>
    </div>
  )
}
