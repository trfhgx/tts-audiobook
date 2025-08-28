// This annotation API is no longer needed with Chatterbox TTS
// Chatterbox handles emotions and naturalness automatically from plain text
// This file can be removed in the future

import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  return NextResponse.json(
    { 
      message: "Text annotation is no longer needed with Chatterbox TTS",
      info: "Chatterbox automatically handles emotions and natural speech patterns"
    },
    { status: 200 }
  )
}
