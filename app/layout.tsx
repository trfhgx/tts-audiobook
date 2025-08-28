import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Toaster } from 'react-hot-toast'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Audiobook Studio',
  description: 'Create engaging audiobooks with AI-powered text-to-speech',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {/* Beautiful animated gradient background */}
        <div className="fixed inset-0 -z-10">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-400/20 via-teal-300/10 to-cyan-400/20"></div>
          <div className="absolute inset-0 bg-gradient-to-tl from-cyan-300/10 via-transparent to-yellow-200/15"></div>
          
          {/* Floating orbs for extra magic */}
          <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-blue-300/20 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute top-3/4 right-1/4 w-96 h-96 bg-teal-300/15 rounded-full blur-3xl animate-pulse delay-1000"></div>
          <div className="absolute bottom-1/4 left-1/3 w-80 h-80 bg-pink-300/10 rounded-full blur-3xl animate-pulse delay-2000"></div>
        </div>
        
        {/* Main content with glass effect backdrop */}
        <div className="relative min-h-screen backdrop-blur-[0.5px]">
          {children}
        </div>
        
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'rgba(255, 255, 255, 0.1)',
              color: '#333',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '12px',
            },
          }}
        />
      </body>
    </html>
  )
}