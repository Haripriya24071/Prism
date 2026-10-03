import { useCallback, useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { createSession, sendChat, triggerGeneration, uploadFile } from '../api.js'
import { getPageVariants } from '../animations/variants.js'
import ChatBox from '../components/ChatBox/ChatBox.jsx'
import { SESSION_STATUS, useSession } from '../hooks/useSession.js'

export default function IntakePage() {
  const { sessionId, setSessionId, status, setStatus, error, failSession } = useSession()
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Welcome to PRISM. Describe your startup or business idea to begin.',
    },
  ])
  const [turnNumber, setTurnNumber] = useState(0)
  const [uploadError, setUploadError] = useState(null)
  const [isSending, setIsSending] = useState(false)

  const initSession = useCallback(async () => {
    try {
      const data = await createSession()
      if (data?.session_id) {
        setSessionId(data.session_id)
      }
      setStatus(SESSION_STATUS.INTAKE)
    } catch (err) {
      failSession(err?.message || 'Failed to initialize session.')
    }
  }, [setSessionId, setStatus, failSession])

  useEffect(() => {
    if (!sessionId) {
      initSession()
    }
  }, [sessionId, initSession])

  const handleSend = async (messageText) => {
    if (!sessionId) return

    const userMsg = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: messageText,
    }
    setMessages((prev) => [...prev, userMsg])
    setIsSending(true)
    setUploadError(null)

    try {
      const res = await sendChat(sessionId, messageText, turnNumber)
      setTurnNumber((prev) => prev + 1)

      if (res?.reply) {
        const assistantMsg = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: res.reply,
        }
        setMessages((prev) => [...prev, assistantMsg])
      }

      if (res?.extraction_complete) {
        setStatus(SESSION_STATUS.HARVESTING)
        await triggerGeneration(sessionId)
      }
    } catch (err) {
      failSession(err?.message || 'Error communicating with assistant.')
    } finally {
      setIsSending(false)
    }
  }

  const handleUpload = async (file) => {
    if (!sessionId) return
    setUploadError(null)
    try {
      const res = await uploadFile(sessionId, file)
      const uploadNotice = {
        id: `upload-${Date.now()}`,
        role: 'assistant',
        content: `Uploaded ${file.name} (${res?.file_type || 'document'}). Summary: ${res?.summary || 'Parsed successfully.'}`,
      }
      setMessages((prev) => [...prev, uploadNotice])
    } catch (err) {
      setUploadError(err?.message || 'File upload rejected.')
    }
  }

  return (
    <motion.main
      className="min-h-screen bg-void p-8 font-body text-content-primary max-w-4xl mx-auto flex flex-col justify-between"
      variants={getPageVariants()}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      <div>
        <header className="mb-6">
          <h1 className="font-display text-h1 font-bold text-content-primary">PRISM Intake</h1>
          <p className="font-body text-content-secondary mt-1">
            Ground your idea across 6 competing AI perspectives.
          </p>
        </header>

        {status === SESSION_STATUS.FAILED && error && (
          <div role="alert" className="mb-6 p-4 rounded-md border border-error bg-surface flex items-center justify-between">
            <span className="text-error font-body text-small">{error}</span>
            <button
              type="button"
              onClick={initSession}
              className="px-3 py-1 bg-accent-signal text-void rounded-md font-body text-small hover:opacity-90"
            >
              Retry
            </button>
          </div>
        )}

        <ChatBox
          messages={messages}
          onSend={handleSend}
          onUpload={handleUpload}
          disabled={isSending || status === SESSION_STATUS.FAILED}
          uploadError={uploadError}
        />
      </div>
    </motion.main>
  )
}
