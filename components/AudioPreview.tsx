'use client'

import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Play, 
  Pause, 
  Download, 
  Volume2, 
  SkipBack, 
  SkipForward,
  RotateCcw
} from 'lucide-react'
import toast from 'react-hot-toast'

interface AudioPreviewProps {
  audioUrl: string
}

export default function AudioPreview({ audioUrl }: AudioPreviewProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(1)
  const audioRef = useRef<HTMLAudioElement>(null)

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const updateTime = () => setCurrentTime(audio.currentTime)
    const updateDuration = () => setDuration(audio.duration)
    const handleEnded = () => setIsPlaying(false)

    audio.addEventListener('timeupdate', updateTime)
    audio.addEventListener('loadedmetadata', updateDuration)
    audio.addEventListener('ended', handleEnded)

    return () => {
      audio.removeEventListener('timeupdate', updateTime)
      audio.removeEventListener('loadedmetadata', updateDuration)
      audio.removeEventListener('ended', handleEnded)
    }
  }, [audioUrl])

  const togglePlayPause = () => {
    const audio = audioRef.current
    if (!audio) return

    if (isPlaying) {
      audio.pause()
    } else {
      audio.play()
    }
    setIsPlaying(!isPlaying)
  }

  const seek = (time: number) => {
    const audio = audioRef.current
    if (!audio) return
    
    audio.currentTime = time
    setCurrentTime(time)
  }

  const skipBackward = () => {
    seek(Math.max(0, currentTime - 10))
  }

  const skipForward = () => {
    seek(Math.min(duration, currentTime + 10))
  }

  const restart = () => {
    seek(0)
    if (!isPlaying) {
      togglePlayPause()
    }
  }

  const handleVolumeChange = (newVolume: number) => {
    const audio = audioRef.current
    if (!audio) return
    
    audio.volume = newVolume
    setVolume(newVolume)
  }

  const downloadAudio = () => {
    const link = document.createElement('a')
    link.href = audioUrl
    link.download = `audiobook-${Date.now()}.wav`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    toast.success('Download started!')
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
    >
      <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
        <Volume2 className="w-6 h-6 text-green-500" />
        Your Audiobook is Ready! 🎉
      </h3>

      <audio ref={audioRef} src={audioUrl} preload="metadata" />

      {/* Waveform Visualization Placeholder */}
      <div className="bg-gradient-to-r from-primary-100 to-purple-100 rounded-lg p-6 mb-6">
        <div className="flex items-center justify-center h-32">
          <motion.div
            className="flex items-end gap-1"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {Array.from({ length: 40 }, (_, i) => (
              <motion.div
                key={i}
                className="bg-primary-500 rounded-full"
                style={{
                  width: '3px',
                  height: `${20 + Math.random() * 60}px`,
                }}
                animate={{
                  height: isPlaying 
                    ? [`${20 + Math.random() * 60}px`, `${30 + Math.random() * 40}px`]
                    : `${20 + Math.random() * 60}px`
                }}
                transition={{
                  duration: 0.5,
                  repeat: isPlaying ? Infinity : 0,
                  repeatType: 'reverse',
                  delay: i * 0.05
                }}
              />
            ))}
          </motion.div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div 
          className="w-full bg-gray-200 rounded-full h-2 cursor-pointer"
          onClick={(e) => {
            const rect = e.currentTarget.getBoundingClientRect()
            const percent = (e.clientX - rect.left) / rect.width
            seek(percent * duration)
          }}
        >
          <motion.div
            className="bg-gradient-to-r from-primary-500 to-purple-500 h-2 rounded-full"
            style={{ width: `${(currentTime / duration) * 100}%` }}
            initial={{ width: 0 }}
            animate={{ width: `${(currentTime / duration) * 100}%` }}
          />
        </div>
        <div className="flex justify-between text-sm text-gray-600 mt-1">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-center gap-4 mb-6">
        <motion.button
          onClick={restart}
          className="p-2 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors duration-200"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          title="Restart"
        >
          <RotateCcw className="w-5 h-5 text-gray-600" />
        </motion.button>

        <motion.button
          onClick={skipBackward}
          className="p-2 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors duration-200"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          title="Skip back 10s"
        >
          <SkipBack className="w-5 h-5 text-gray-600" />
        </motion.button>

        <motion.button
          onClick={togglePlayPause}
          className="p-4 bg-gradient-to-r from-primary-500 to-purple-500 hover:from-primary-600 hover:to-purple-600 rounded-full shadow-lg"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          {isPlaying ? (
            <Pause className="w-6 h-6 text-white" />
          ) : (
            <Play className="w-6 h-6 text-white ml-1" />
          )}
        </motion.button>

        <motion.button
          onClick={skipForward}
          className="p-2 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors duration-200"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          title="Skip forward 10s"
        >
          <SkipForward className="w-5 h-5 text-gray-600" />
        </motion.button>

        {/* Volume Control */}
        <div className="flex items-center gap-2 ml-4">
          <Volume2 className="w-4 h-4 text-gray-600" />
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={volume}
            onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
            className="w-20 h-1 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
        </div>
      </div>

      {/* Download Button */}
      <motion.button
        onClick={downloadAudio}
        className="btn-secondary w-full flex items-center justify-center gap-2"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <Download className="w-5 h-5" />
        Download Audiobook
      </motion.button>

      {/* Audio Info */}
      <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
        <h4 className="font-medium text-green-800 mb-1">Audio Details</h4>
        <div className="text-sm text-green-700 space-y-1">
          <div>Duration: {formatTime(duration)}</div>
          <div>Format: WAV (High Quality)</div>
          <div>Sample Rate: 24kHz</div>
        </div>
      </div>
    </motion.div>
  )
}
