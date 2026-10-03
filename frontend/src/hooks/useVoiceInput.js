import { useCallback, useEffect, useRef, useState } from 'react'

export function useVoiceInput({ onTranscript, onError } = {}) {
  const [isRecording, setIsRecording] = useState(false)
  const recognitionRef = useRef(null)
  const isSupported = typeof window !== 'undefined' && 'webkitSpeechRecognition' in window

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort()
        recognitionRef.current = null
      }
    }
  }, [])

  const stopRecording = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
    }
  }, [])

  const startRecording = useCallback(() => {
    if (!isSupported) {
      return
    }

    if (recognitionRef.current) {
      recognitionRef.current.abort()
    }

    const recognition = new window.webkitSpeechRecognition()
    recognition.continuous = false
    recognition.interimResults = false
    recognition.lang = 'en-US'

    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0].transcript)
        .join(' ')
        .trim()

      if (transcript && onTranscript) {
        onTranscript(transcript)
      }
    }

    recognition.onerror = (event) => {
      setIsRecording(false)
      if (onError) {
        onError(event.error)
      }
    }

    recognition.onend = () => {
      setIsRecording(false)
    }

    recognitionRef.current = recognition

    try {
      recognition.start()
      setIsRecording(true)
    } catch (err) {
      setIsRecording(false)
      if (onError) {
        onError(err)
      }
    }
  }, [isSupported, onTranscript, onError])

  if (!isSupported) {
    return {
      supported: false,
      isRecording: false,
      startRecording: () => {},
      stopRecording: () => {},
    }
  }

  return {
    supported: true,
    isRecording,
    startRecording,
    stopRecording,
  }
}
