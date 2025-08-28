import { NextRequest, NextResponse } from 'next/server'

const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://localhost:8000'

interface AnnotationSettings {
  addEmotions: boolean
  emotionIntensity: number
  addPauses: boolean
  speakerVariation: boolean
}

export async function POST(request: NextRequest) {
  try {
    const { text, settings }: { text: string; settings: AnnotationSettings } = await request.json()

    if (!text) {
      return NextResponse.json({ error: 'Text is required' }, { status: 400 })
    }

    // Call Python backend
    const response = await fetch(`${PYTHON_BACKEND_URL}/annotate-text`, {
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

    const result = await response.json()
    return NextResponse.json(result)

  } catch (error) {
    console.error('Annotation error:', error)
    return NextResponse.json(
      { error: 'Failed to annotate text' },
      { status: 500 }
    )
  }
}
