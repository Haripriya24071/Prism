import { useEffect, useRef, useState } from 'react'
import { VoiceButton } from './VoiceButton.jsx'
import './ChatBox.css'

export { VoiceButton }

const ACCEPTED_FILES = '.pdf,.png,.jpg,.jpeg,.webp,.docx'

export default function ChatBox({
  messages = [],
  onSend,
  onUpload,
  disabled = false,
  uploadError = null,
}) {
  const [draft, setDraft] = useState('')
  const fileInputRef = useRef(null)
  const logEndRef = useRef(null)
  const textareaId = 'chatbox-input'
  const canSend = draft.trim() !== '' && !disabled

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ block: 'end' })
  }, [messages])

  function send() {
    if (!canSend) {
      return
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

  function appendTranscript(text) {
    setDraft((current) => (current === '' ? text : `${current} ${text}`))
  }

  return (
    <section className="chatbox" aria-label="Intake chat">
      <div className="chatbox__log" role="log" aria-live="polite">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`chatbox__bubble chatbox__bubble--${message.role}`}
          >
            {message.content}
          </div>
        ))}
        <div ref={logEndRef} />
      </div>

      <div className="chatbox__input-container">
        <div className="chatbox__input-row">
          <label htmlFor={textareaId} className="sr-only">
            Describe your business idea
          </label>
          <textarea
            id={textareaId}
            className="chatbox__textarea"
            rows={2}
            value={draft}
            disabled={disabled}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe your business idea"
          />

          <VoiceButton onTranscript={appendTranscript} disabled={disabled} />

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
