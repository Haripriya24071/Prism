import { useCallback, useEffect, useRef, useState } from 'react'

export function useVoiceInput({ onTranscript, onError } = {}) {
  const [isRecording, setIsRecording] = useState(false)
  const recognitionRef = useRef(null)
  const shouldBeRecordingRef = useRef(false)
  const restartTimerRef = useRef(null)
  const initAndStartRef = useRef(null)

  const isSupported =
    typeof window !== 'undefined' &&
    ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)

  // Clean up on unmount
  useEffect(() => {
    return () => {
      shouldBeRecordingRef.current = false
      if (restartTimerRef.current) {
        clearTimeout(restartTimerRef.current)
        restartTimerRef.current = null
      }
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort()
        } catch {
          // ignore
        }
        recognitionRef.current = null
      }
    }
  }, [])

  const stopRecording = useCallback(() => {
    shouldBeRecordingRef.current = false
    setIsRecording(false)
    if (restartTimerRef.current) {
      clearTimeout(restartTimerRef.current)
      restartTimerRef.current = null
    }
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop()
      } catch {
        // ignore
      }
    }
  }, [])

  const initAndStart = useCallback(() => {
    if (!isSupported) return

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition

    // Clean up prior instance if any
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort()
      } catch {
        // ignore
      }
    }

    const recognition = new SpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = false
    recognition.lang = 'en-US'

    recognition.onstart = () => {
      if (shouldBeRecordingRef.current) {
        setIsRecording(true)
      }
    }

    recognition.onresult = (event) => {
      if (!shouldBeRecordingRef.current) return

      let newTranscript = ''
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          const piece = event.results[i][0].transcript.trim()
          if (piece) {
            newTranscript = newTranscript ? `${newTranscript} ${piece}` : piece
          }
        }
      }

      if (newTranscript && onTranscript) {
        onTranscript(newTranscript)
      }
    }

    recognition.onerror = (event) => {
      // Chrome emits 'no-speech' when the user pauses for ~5-6 seconds.
      // Claude / modern voice chat ignores 'no-speech' and keeps listening!
      if (event.error === 'no-speech' || event.error === 'aborted') {
        return
      }

      // Hard error: permission denied or no audio capture hardware
      if (event.error === 'not-allowed' || event.error === 'audio-capture') {
        shouldBeRecordingRef.current = false
        setIsRecording(false)
        if (onError) {
          onError(event.error)
        }
      }
    }

    recognition.onend = () => {
      // If the user did NOT click to turn it off, automatically keep listening!
      if (shouldBeRecordingRef.current) {
        if (restartTimerRef.current) {
          clearTimeout(restartTimerRef.current)
        }
        restartTimerRef.current = setTimeout(() => {
          if (shouldBeRecordingRef.current) {
            try {
              recognition.start()
            } catch {
              // If start throws (e.g. invalid state), re-init fresh instance
              try {
                initAndStartRef.current?.()
              } catch {
                setIsRecording(false)
              }
            }
          }
        }, 120)
      } else {
        setIsRecording(false)
      }
    }

    recognitionRef.current = recognition

    try {
      recognition.start()
      setIsRecording(true)
    } catch (err) {
      if (onError && err.name !== 'InvalidStateError') {
        onError(err)
      }
    }
  }, [isSupported, onTranscript, onError])

  useEffect(() => {
    initAndStartRef.current = initAndStart
  }, [initAndStart])

  const startRecording = useCallback(() => {
    if (!isSupported) return
    shouldBeRecordingRef.current = true
    initAndStart()
  }, [isSupported, initAndStart])

  const toggleRecording = useCallback(() => {
    if (isRecording || shouldBeRecordingRef.current) {
      stopRecording()
    } else {
      startRecording()
    }
  }, [isRecording, startRecording, stopRecording])

  if (!isSupported) {
    return {
      supported: false,
      isRecording: false,
      startRecording: () => {},
      stopRecording: () => {},
      toggleRecording: () => {},
    }
  }

  return {
    supported: true,
    isRecording,
    startRecording,
    stopRecording,
    toggleRecording,
  }
}
