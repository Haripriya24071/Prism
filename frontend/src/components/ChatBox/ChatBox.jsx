import { useCallback, useEffect, useRef, useState } from 'react'
import { VoiceButton } from './VoiceButton.jsx'
import { useVoiceInput } from '../../hooks/useVoiceInput.js'
import './ChatBox.css'

export { VoiceButton }

const ACCEPTED_FILES = '.pdf,.png,.jpg,.jpeg,.webp,.docx'

function FormattedBubble({ content, role }) {
  if (!content) return null

  if (role === 'assistant') {
    const paragraphs = content.split('\n\n').filter(Boolean)
    return (
      <div className="chatbox__formatted-content">
        {paragraphs.map((p, idx) => {
          const parts = p.split(/(\*\*[^*]+\*\*)/g)
          return (
            <p key={idx} className="chatbox__para">
              {parts.map((part, pIdx) => {
                if (part.startsWith('**') && part.endsWith('**')) {
                  return (
                    <strong key={pIdx} className="font-bold text-content-primary">
                      {part.slice(2, -2)}
                    </strong>
                  )
                }
                return part
              })}
            </p>
          )
        })}
      </div>
    )
  }

  return <span>{content}</span>
}

export default function ChatBox({
  messages = [],
  onSend,
  onUpload,
  disabled = false,
  uploadError = null,
  suggestedChips = [],
}) {
  const [draft, setDraft] = useState('')
  const fileInputRef = useRef(null)
  const logEndRef = useRef(null)
  const textareaId = 'chatbox-input'
  const canSend = draft.trim() !== '' && !disabled

  const appendTranscript = useCallback((text) => {
    setDraft((current) => {
      const trimmed = current.trim()
      return trimmed === '' ? text : `${trimmed} ${text}`
    })
  }, [])

  const {
    supported: voiceSupported,
    isRecording,
    toggleRecording,
    stopRecording,
  } = useVoiceInput({
    onTranscript: appendTranscript,
  })

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ block: 'end' })
  }, [messages, disabled])

  useEffect(() => {
    if (disabled && isRecording) {
      stopRecording()
    }
  }, [disabled, isRecording, stopRecording])

  function send() {
    if (!canSend) {
      return
    }
    if (isRecording) {
      stopRecording()
    }
    onSend(draft.trim())
    setDraft('')
  }

  function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      send()
    }
  }

  function handleFileChange(event) {
    const file = event.target.files?.[0]
    if (file) {
      onUpload(file)
    }
    event.target.value = ''
  }

  return (
    <section className="chatbox" aria-label="Intake chat">
      <div className="chatbox__log" role="log" aria-live="polite">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`chatbox__bubble chatbox__bubble--${message.role}`}
          >
            <FormattedBubble content={message.content} role={message.role} />
          </div>
        ))}

        {disabled && (
          <div className="chatbox__bubble chatbox__bubble--assistant chatbox__bubble--typing">
            <span className="chatbox__dot" />
            <span className="chatbox__dot" />
            <span className="chatbox__dot" />
            <span className="font-tertiary text-micro text-content-secondary ml-1">
              Calibrating venture parameters...
            </span>
          </div>
        )}

        <div ref={logEndRef} />
      </div>

      {/* Suggested Quick Reply Chips */}
      {suggestedChips && suggestedChips.length > 0 && !disabled && (
        <div className="chatbox__chips-row">
          <span className="chatbox__chips-label">Quick reply suggestions:</span>
          <div className="chatbox__chips-list">
            {suggestedChips.map((chip, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => onSend(chip)}
                className="chatbox__chip"
              >
                {chip}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Active Voice Chat Continuous Banner */}
      {isRecording && (
        <div className="chatbox__voice-active-banner">
          <div className="flex items-center gap-2">
            <span className="chatbox__voice-live-dot" />
            <span className="font-tertiary text-micro font-bold text-accent-signal uppercase tracking-wider">
              Voice Chat Active — Listening Continuously
            </span>
          </div>
          <span className="font-body text-micro text-content-secondary hidden sm:inline">
            Speak freely (no timeout) • Click mic or Send to finish
          </span>
        </div>
      )}

      <div className="chatbox__input-container">
        <div className="chatbox__input-row">
          <label htmlFor={textareaId} className="sr-only">
            Describe your business idea or answer follow-up
          </label>
          <textarea
            id={textareaId}
            className="chatbox__textarea"
            rows={2}
            value={draft}
            disabled={disabled}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              messages.length > 1
                ? 'Answer the question above, or speak freely...'
                : 'Describe your business idea (1–2 sentences)...'
            }
          />

          <VoiceButton
            supported={voiceSupported}
            isRecording={isRecording}
            onToggle={toggleRecording}
            disabled={disabled}
          />

          <button
            type="button"
            className="chatbox__icon-btn"
            aria-label="Attach a file"
            disabled={disabled}
            onClick={() => fileInputRef.current?.click()}
          >
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M21 11.5 12.5 20a5 5 0 0 1-7-7L14 4.5a3.5 3.5 0 0 1 5 5l-8.5 8.5a2 2 0 0 1-3-3L15 7.5" />
            </svg>
          </button>
          <input
            ref={fileInputRef}
            type="file"
            className="chatbox__file-input"
            accept={ACCEPTED_FILES}
            tabIndex={-1}
            aria-hidden="true"
            onChange={handleFileChange}
          />

          <button
            type="button"
            className="chatbox__send"
            aria-label="Send message"
            disabled={!canSend}
            onClick={send}
          >
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="m22 2-7 20-4-9-9-4z" />
              <path d="M22 2 11 13" />
            </svg>
          </button>
        </div>
        {uploadError && (
          <p role="alert" className="chatbox__upload-error font-body text-micro text-error mt-1 px-3">
            {uploadError}
          </p>
        )}
      </div>
    </section>
  )
}
