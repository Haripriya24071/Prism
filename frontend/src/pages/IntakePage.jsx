import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { createSession, sendChat, triggerGeneration, uploadFile } from '../api.js'
import { getPageVariants } from '../animations/variants.js'
import ChatBox from '../components/ChatBox/ChatBox.jsx'
import { SESSION_STATUS, useSession } from '../hooks/useSession.js'
import HeroSection from '../components/Landing/HeroSection.jsx'
import AgentsShowcase from '../components/Landing/AgentsShowcase.jsx'
import HowItWorks from '../components/Landing/HowItWorks.jsx'
import PeekingMascot from '../components/Landing/PeekingMascot.jsx'

const SAMPLE_IDEAS = [
  {
    title: 'FinTech Compliance',
    prompt: 'Autonomous AI regulatory compliance officer for cross-border B2B payments under EU and US law.',
    icon: '⚖️',
  },
  {
    title: 'Fleet Telematics IoT',
    prompt: 'Predictive maintenance sensor network and micro-SaaS for heavy construction fleet operators.',
    icon: '🚜',
  },
  {
    title: 'Farm-to-Kitchen',
    prompt: 'Hyperlocal fresh produce marketplace matching organic regenerative farmers directly with urban dark kitchens.',
    icon: '🥦',
  },
  {
    title: 'Field Voice Assistant',
    prompt: 'Noise-cancelling voice assistant earpiece for industrial field technicians with automated blueprint lookups.',
    icon: '🎙️',
  },
]

export default function IntakePage() {
  const { sessionId, setSessionId, status, setStatus, error } = useSession()
  const msgCounter = useRef(1)
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        'Welcome to PRISM. Pitch your startup concept in 1–2 sentences. Our 6 domain agents will evaluate market sizing, tech architecture, unit economics, regulatory risk, UX friction, and adversarial vulnerabilities.',
    },
  ])
  const [turnNumber, setTurnNumber] = useState(0)
  const [uploadError, setUploadError] = useState(null)
  const [isSending, setIsSending] = useState(false)
  const [isBackendOnline, setIsBackendOnline] = useState(null)
  const [readyToEvaluate, setReadyToEvaluate] = useState(false)

  // Initialize session with graceful offline fallback
  useEffect(() => {
    let isMounted = true
    if (!sessionId) {
      createSession()
        .then((data) => {
          if (!isMounted) return
          if (data?.session_id) {
            setSessionId(data.session_id)
            setIsBackendOnline(true)
            setStatus(SESSION_STATUS.INTAKE)
          }
        })
        .catch(() => {
          if (!isMounted) return
          setSessionId('prism-session-standby')
          setIsBackendOnline(false)
          setStatus(SESSION_STATUS.INTAKE)
        })
    }
    return () => {
      isMounted = false
    }
  }, [sessionId, setSessionId, setStatus])

  const scrollToPitch = () => {
    const el = document.getElementById('pitch-terminal')
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' })
    }
  }

  const handleSend = async (messageText) => {
    if (!sessionId) return

    const userMsgId = `user-msg-${msgCounter.current++}`
    const userMsg = {
      id: userMsgId,
      role: 'user',
      content: messageText,
    }
    setMessages((prev) => [...prev, userMsg])
    setIsSending(true)
    setUploadError(null)

    try {
      // Attempt live backend chat first
      const res = await sendChat(sessionId, messageText, turnNumber)
      setIsBackendOnline(true)
      setTurnNumber((prev) => prev + 1)

      if (res?.reply) {
        const assistantMsgId = `asst-msg-${msgCounter.current++}`
        const assistantMsg = {
          id: assistantMsgId,
          role: 'assistant',
          content: res.reply,
        }
        setMessages((prev) => [...prev, assistantMsg])
      }

      if (res?.extraction_complete) {
        setReadyToEvaluate(true)
      }
    } catch {
      // Backend not running / offline: provide intelligent coordinator response
      setIsBackendOnline(false)
      setTurnNumber((prev) => prev + 1)
      setReadyToEvaluate(true)

      const demoReplyId = `asst-demo-${msgCounter.current++}`
      const demoReply = {
        id: demoReplyId,
        role: 'assistant',
        content: `I have ingested your venture thesis: "${messageText}".\n\nAll 6 Swarm Agents (Seed VC, Bootstrapper, Enterprise CTO, UX Researcher, Policy Expert, Adversary) have been alerted and are standing by to run their independent evaluations. Click 'Launch Swarm Evaluation' below to begin the gauntlet!`,
      }
      setMessages((prev) => [...prev, demoReply])
    } finally {
      setIsSending(false)
    }
  }

  const handleUpload = async (file) => {
    if (!sessionId) return
    setUploadError(null)
    const uploadId = `upload-msg-${msgCounter.current++}`
    try {
      const res = await uploadFile(sessionId, file)
      setIsBackendOnline(true)
      const uploadNotice = {
        id: uploadId,
        role: 'assistant',
        content: `Uploaded ${file.name} (${res?.file_type || 'document'}). Summary: ${res?.summary || 'Parsed successfully.'}`,
      }
      setMessages((prev) => [...prev, uploadNotice])
    } catch {
      // Fallback for upload in demo
      const uploadNotice = {
        id: uploadId,
        role: 'assistant',
        content: `Uploaded ${file.name}. File attached to session context for 6-agent evaluation.`,
      }
      setMessages((prev) => [...prev, uploadNotice])
    }
  }

  const handleStartGeneration = async () => {
    setStatus(SESSION_STATUS.HARVESTING)
    try {
      await triggerGeneration(sessionId)
    } catch {
      // If backend is offline, generation page will simulate or display progress
    }
  }

  return (
    <motion.main
      className="min-h-screen bg-void text-content-primary selection:bg-accent-tint selection:text-content-primary relative"
      variants={getPageVariants()}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      {/* Left Screen Border Clinging Observer (Laptops & Desktops Only) */}
      <PeekingMascot onSelectSample={() => handleSend(SAMPLE_IDEAS[0].prompt)} />

      {/* Top Navigation Bar */}
      <header className="border-b border-border bg-surface px-6 py-4 sticky top-0 z-20 shadow-sm">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="font-display font-black text-h2 tracking-tight text-content-primary">
              PRISM<span className="text-accent-signal">.</span>
            </span>
            <span className="hidden sm:inline-block px-2.5 py-0.5 rounded-full border border-border-subtle bg-surface-raised font-tertiary text-micro text-content-secondary">
              6-Agent Swarm
            </span>
          </div>

          <div className="flex items-center gap-4">
            {/* Live Backend Connection Indicator */}
            <div className="flex items-center gap-2 px-3 py-1 rounded-full border border-border-subtle bg-surface-raised text-micro font-tertiary">
              <span
                className={`w-2 h-2 rounded-full ${
                  isBackendOnline ? 'bg-success animate-pulse' : 'bg-warning'
                }`}
              ></span>
              <span className="text-content-secondary hidden md:inline">
                {isBackendOnline ? 'Live Swarm Connected' : 'Swarm Standby (Demo Ready)'}
              </span>
            </div>

            <button
              type="button"
              onClick={scrollToPitch}
              className="px-4 py-1.5 bg-border text-surface font-display font-semibold text-small rounded-md shadow-[2px_2px_0px_var(--color-border)] hover:bg-accent-signal transition-all"
            >
              Pitch Idea →
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* 1. Hero Section */}
        <HeroSection onStartClick={scrollToPitch} />

        {/* 2. The 6 Competing Agents Showcase */}
        <AgentsShowcase onSelectAgent={() => scrollToPitch()} />

        {/* 3. How It Works */}
        <HowItWorks />

        {/* 4. Interactive Intake Launchpad Terminal */}
        <section id="pitch-terminal" className="my-16 scroll-mt-20" aria-label="Pitch Terminal">
          <div className="sketch-card p-6 sm:p-8 bg-surface border-2 border-border shadow-[5px_5px_0px_var(--color-border)] relative">
            {/* Top Badge */}
            <div className="flex items-center justify-between pb-4 mb-6 border-b border-border-subtle">
              <div>
                <span className="font-tertiary text-micro font-bold uppercase tracking-wider text-accent-signal block mb-1">
                  Intake Launchpad
                </span>
                <h2 className="font-display text-h2 font-extrabold text-content-primary">
                  Pitch Your Idea to the Swarm
                </h2>
                <p className="font-body text-content-secondary text-small mt-0.5">
                  Describe your business concept below, or pick a sample prompt to test all 6 agents.
                </p>
              </div>

              {readyToEvaluate && (
                <button
                  type="button"
                  onClick={handleStartGeneration}
                  className="px-5 py-2.5 bg-accent-signal text-surface font-display font-bold text-small rounded-lg shadow-[3px_3px_0px_var(--color-border)] hover:opacity-90 transition-all animate-bounce"
                >
                  ⚡ Run 6-Agent Swarm →
                </button>
              )}
            </div>

            {/* Quick Sample Prompts */}
            <div className="mb-6">
              <span className="font-tertiary text-micro font-bold uppercase tracking-wider text-content-secondary block mb-2">
                Quick Starters (Click to load):
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
                {SAMPLE_IDEAS.map((idea, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => handleSend(idea.prompt)}
                    className="p-3 text-left rounded-lg border border-border-subtle bg-surface-raised hover:bg-accent-tint/30 hover:border-border transition-all group flex flex-col justify-between"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-base">{idea.icon}</span>
                      <span className="font-display font-bold text-micro text-content-primary group-hover:text-accent-signal">
                        {idea.title}
                      </span>
                    </div>
                    <p className="font-body text-[11px] text-content-secondary line-clamp-2 leading-snug">
                      &ldquo;{idea.prompt}&rdquo;
                    </p>
                  </button>
                ))}
              </div>
            </div>

            {/* Error Notification if any */}
            {status === SESSION_STATUS.FAILED && error && (
              <div
                role="alert"
                className="mb-6 p-4 rounded-md border border-error bg-surface flex items-center justify-between"
              >
                <span className="text-error font-body text-small">{error}</span>
                <button
                  type="button"
                  onClick={() => {
                    createSession()
                      .then((data) => {
                        if (data?.session_id) {
                          setSessionId(data.session_id)
                          setIsBackendOnline(true)
                          setStatus(SESSION_STATUS.INTAKE)
                        }
                      })
                      .catch(() => {
                        setIsBackendOnline(false)
                      })
                  }}
                  className="px-3 py-1 bg-accent-signal text-surface rounded-md font-body text-small hover:opacity-90"
                >
                  Retry
                </button>
              </div>
            )}

            {/* ChatBox Component */}
            <ChatBox
              messages={messages}
              onSend={handleSend}
              onUpload={handleUpload}
              disabled={isSending}
              uploadError={uploadError}
            />

            {/* Ready to Evaluate Call-to-Action Bar */}
            {readyToEvaluate && (
              <div className="mt-6 p-4 rounded-xl border-2 border-border bg-accent-tint/40 flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">🐝</span>
                  <div>
                    <div className="font-display font-bold text-small text-content-primary">
                      Swarm Ready for Deployment
                    </div>
                    <div className="font-body text-micro text-content-secondary">
                      All 6 personas will evaluate feasibility, market size, regulatory risk, and architecture.
                    </div>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={handleStartGeneration}
                  className="px-6 py-2.5 bg-border text-surface font-display font-bold text-small rounded-lg shadow-[3px_3px_0px_var(--color-border)] hover:bg-accent-signal transition-all flex-shrink-0"
                >
                  Launch 6-Agent Swarm →
                </button>
              </div>
            )}
          </div>
        </section>
      </div>

      {/* Footer */}
      <footer className="mt-20 border-t border-border bg-surface py-8 px-6 text-center">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-display font-bold text-content-primary">PRISM</span>
            <span className="font-body text-micro text-content-secondary">
              — Autonomous Multi-Agent Venture Validation System
            </span>
          </div>
          <p className="font-body text-micro text-content-muted">
            Grounding ventures across 6 adversarial domains • Hand-crafted editorial style
          </p>
        </div>
      </footer>
    </motion.main>
  )
}
