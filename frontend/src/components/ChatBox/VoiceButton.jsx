import { useVoiceInput } from '../../hooks/useVoiceInput.js'
import './ChatBox.css'

export function VoiceButton({ onTranscript, disabled = false }) {
  const { supported, isRecording, startRecording, stopRecording } = useVoiceInput({
    onTranscript,
  })

  if (!supported) {
    return null
  }

  return (
    <button
      type="button"
      className={`chatbox__icon-btn chatbox__voice${isRecording ? ' chatbox__voice--recording' : ''}`}
      aria-label={isRecording ? 'Stop recording' : 'Start voice input'}
      aria-pressed={isRecording}
      disabled={disabled}
      onClick={isRecording ? stopRecording : startRecording}
    >
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <rect x="9" y="3" width="6" height="12" rx="3" />
        <path d="M5 11a7 7 0 0 0 14 0" />
        <path d="M12 18v3" />
      </svg>
    </button>
  )
}
