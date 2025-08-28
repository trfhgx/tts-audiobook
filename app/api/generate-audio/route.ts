import { NextRequest, NextResponse } from 'next/server'

const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://localhost:8000'

interface TTSSettings {
  voice: string
  exaggeration: number
  cfg_weight: number
  quality: string
}

export async function POST(request: NextRequest) {
  try {
    const { text, settings }: { text: string; settings: TTSSettings } = await request.json()

    if (!text) {
      return NextResponse.json({ error: 'Text is required' }, { status: 400 })
    }

    // Call Python backend
    const response = await fetch(`${PYTHON_BACKEND_URL}/generate-audio`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text, settings }),
    })

    if (!response.ok) {
      const error = await response.text()
      throw new Error(`Backend error: ${error}`)
    }

    // Get the audio data
    const audioBuffer = await response.arrayBuffer()

    // Return the audio file
    return new NextResponse(audioBuffer, {
      headers: {
        'Content-Type': 'audio/wav',
        'Content-Disposition': 'attachment; filename="audiobook.wav"',
      },
    })

  } catch (error) {
    console.error('Audio generation error:', error)
    return NextResponse.json(
      { error: 'Failed to generate audio' },
      { status: 500 }
    )
  }
}
