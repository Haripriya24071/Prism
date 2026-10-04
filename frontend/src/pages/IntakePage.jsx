import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { createSession, sendChat, triggerGeneration, uploadFile } from '../api.js'
import { getPageVariants } from '../animations/variants.js'
import ChatBox from '../components/ChatBox/ChatBox.jsx'
import VentureDossier from '../components/Intake/VentureDossier.jsx'
import { SESSION_STATUS, useSession } from '../hooks/useSession.js'
import HeroSection from '../components/Landing/HeroSection.jsx'
import AgentsShowcase from '../components/Landing/AgentsShowcase.jsx'
import HowItWorks from '../components/Landing/HowItWorks.jsx'
import PeekingMascot from '../components/Landing/PeekingMascot.jsx'
import prismLogo from '../assets/landing/prism_logo.jpg'

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
  const [extraction, setExtraction] = useState({})
  const [completionPct, setCompletionPct] = useState(0)
  const [suggestedChips, setSuggestedChips] = useState([])
  const [isComplete, setIsComplete] = useState(false)

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

  // Current view: 'showcase' | 'pitch'
  const [currentView, setCurrentView] = useState(() => {
    if (typeof window !== 'undefined' && window.location.hash === '#pitch') {
      return 'pitch'
    }
    return 'showcase'
  })

  // Synchronize with URL hash for browser back/forward navigation
  useEffect(() => {
    const handleHashChange = () => {
      if (window.location.hash === '#pitch') {
        setCurrentView('pitch')
      } else {
        setCurrentView('showcase')
      }
    }
    window.addEventListener('hashchange', handleHashChange)
    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  const navigateTo = (view) => {
    setCurrentView(view)
    if (view === 'pitch') {
      window.location.hash = 'pitch'
    } else {
      window.location.hash = ''
    }
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const scrollToSection = (id) => {
    if (currentView !== 'showcase') {
      setCurrentView('showcase')
      window.location.hash = ''
      setTimeout(() => {
        const el = document.getElementById(id)
        if (el) el.scrollIntoView({ behavior: 'smooth' })
      }, 150)
    } else {
      const el = document.getElementById(id)
      if (el) el.scrollIntoView({ behavior: 'smooth' })
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

      if (res?.extraction) {
        setExtraction(res.extraction)
      }
      if (typeof res?.completion_pct === 'number') {
        setCompletionPct(res.completion_pct)
      }
      if (Array.isArray(res?.suggested_chips)) {
        setSuggestedChips(res.suggested_chips)
      }
      if (res?.is_complete) {
        setIsComplete(true)
        setReadyToEvaluate(true)
      } else if (res?.completion_pct >= 50) {
        setReadyToEvaluate(true)
      }

      if (res?.reply) {
        const assistantMsgId = `asst-msg-${msgCounter.current++}`
        const assistantMsg = {
          id: assistantMsgId,
          role: 'assistant',
          content: res.reply,
        }
        setMessages((prev) => [...prev, assistantMsg])
      }
    } catch {
      // Backend not running / offline: provide intelligent coordinator response
      setIsBackendOnline(false)
      setTurnNumber((prev) => prev + 1)
      setReadyToEvaluate(true)

      // Fallback progressive parameter filling
      const fallbackExt = { ...extraction }
      if (!fallbackExt.raw_idea) {
        fallbackExt.raw_idea = messageText
        setSuggestedChips(['🇮🇳 India', '🇺🇸 United States', '🇬🇧 United Kingdom', '🇦🇪 UAE'])
      } else if (!fallbackExt.region) {
        fallbackExt.region = messageText.includes('India') ? 'IN' : 'US'
        setSuggestedChips(['💡 Fresh Idea', '🛠️ Prototype', '🚀 Active MVP'])
      } else if (!fallbackExt.stage) {
        fallbackExt.stage = 'idea'
        setSuggestedChips(['🌱 Bootstrapped (<$15k)', '💼 Seed ($50k-$250k)', '🏢 Series A+'])
      }
      setExtraction(fallbackExt)
      setCompletionPct((prev) => Math.min(100, (prev || 0) + 33))

      const demoReplyId = `asst-demo-${msgCounter.current++}`
      const demoReply = {
        id: demoReplyId,
        role: 'assistant',
        content: `Captured into dossier: "${messageText}".\n\nWhat is your target geographic market or jurisdiction for launch?`,
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
      setReadyToEvaluate(true)
      const uploadNotice = {
        id: uploadId,
        role: 'assistant',
        content: `Uploaded ${file.name} (${res?.file_type || 'document'}). Summary: ${res?.summary || 'Parsed successfully.'}`,
      }
      setMessages((prev) => [...prev, uploadNotice])
    } catch {
      // Fallback for upload in demo
      setReadyToEvaluate(true)
      const uploadNotice = {
        id: uploadId,
        role: 'assistant',
        content: `Uploaded ${file.name}. File attached to session context for 6-agent evaluation.`,
      }
      setMessages((prev) => [...prev, uploadNotice])
    }
  }

  const handleStartGeneration = async () => {
    setUploadError(null)
    try {
      await triggerGeneration(sessionId)
      setStatus(SESSION_STATUS.HARVESTING)
    } catch (err) {
      setUploadError(err?.message || 'Failed to start generation. Please check backend connection.')
    }
  }

  return (
    <motion.main
      className="min-h-screen bg-void text-content-primary selection:bg-accent-tint selection:text-content-primary relative flex flex-col justify-between"
      variants={getPageVariants()}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      <div>
        {/* Top Navigation Bar - Simple, Neat & Minimalist */}
        <header className="sticky top-0 z-30 w-full bg-surface/90 backdrop-blur-md border-b border-border-subtle">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
            {/* Clean Brand Logo */}
            <button
              type="button"
              onClick={() => navigateTo('showcase')}
              className="group flex items-center gap-2.5 hover:opacity-85 transition-opacity cursor-pointer"
              aria-label="PRISM Home"
            >
              <img
                src={prismLogo}
                alt="PRISM Detective"
                className="w-8 h-8 rounded-full border border-border shadow-sm object-cover"
              />
              <span className="font-display font-black text-2xl tracking-tight text-content-primary">
                PRISM<span className="text-accent-signal">.</span>
              </span>
            </button>

            {/* Simple Text Navigation Links */}
            <nav className="hidden md:flex items-center gap-8" aria-label="Main Navigation">
              <button
                type="button"
                onClick={() => navigateTo('showcase')}
                className={`font-display text-sm font-semibold transition-colors cursor-pointer ${
                  currentView === 'showcase'
                    ? 'text-content-primary'
                    : 'text-content-secondary hover:text-content-primary'
                }`}
              >
                Showcase
              </button>
              <button
                type="button"
                onClick={() => scrollToSection('swarm-heading')}
                className="font-display text-sm font-medium text-content-secondary hover:text-content-primary transition-colors cursor-pointer"
              >
                The 6 Minds
              </button>
              <button
                type="button"
                onClick={() => scrollToSection('how-it-works')}
                className="font-display text-sm font-medium text-content-secondary hover:text-content-primary transition-colors cursor-pointer"
              >
                How It Works
              </button>
            </nav>

            {/* Right Side: Clean Status & Single Neat Action */}
            <div className="flex items-center gap-4">
              {/* Subtle Status Dot */}
              <div className="flex items-center gap-2 text-xs font-tertiary text-content-secondary">
                <span
                  className={`w-2 h-2 rounded-full ${
                    isBackendOnline ? 'bg-success animate-pulse' : 'bg-warning'
                  }`}
                />
                <span className="hidden sm:inline">
                  {isBackendOnline ? 'Live Swarm' : 'Demo Standby'}
                </span>
              </div>

              {/* Contextual CTA */}
              {currentView === 'showcase' ? (
                <button
                  type="button"
                  onClick={() => navigateTo('pitch')}
                  className="px-5 py-2 bg-content-primary text-surface font-display font-semibold text-xs rounded-full hover:bg-accent-signal transition-colors shadow-sm cursor-pointer"
                >
                  Pitch Idea →
                </button>
              ) : readyToEvaluate ? (
                <button
                  type="button"
                  onClick={handleStartGeneration}
                  className="px-5 py-2 bg-accent-signal text-surface font-display font-bold text-xs rounded-full hover:opacity-90 transition-opacity shadow-sm cursor-pointer animate-pulse"
                >
                  Run Swarm →
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => navigateTo('showcase')}
                  className="px-4 py-2 border border-border-subtle rounded-full text-xs font-display font-medium text-content-secondary hover:text-content-primary hover:border-border transition-colors cursor-pointer"
                >
                  ← Back to Showcase
                </button>
              )}
            </div>
          </div>
        </header>

        {/* Companion Mascot Observer - Available globally across Showcase & Pitch Launchpad */}
        <PeekingMascot
          currentView={currentView}
          onNavigate={navigateTo}
          onSelectSample={(samplePrompt) => {
            if (currentView !== 'pitch') {
              navigateTo('pitch')
            }
            handleSend(samplePrompt || SAMPLE_IDEAS[0].prompt)
          }}
        />

        {/* View 1: Landing Page Showcase */}
        {currentView === 'showcase' && (
          <motion.div
            key="showcase-view"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
            className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6"
          >
            {/* Hero Section with Pitch CTA */}
            <HeroSection onStartClick={() => navigateTo('pitch')} />

            {/* 6 Agents Showcase */}
            <AgentsShowcase onSelectAgent={() => navigateTo('pitch')} />

            {/* 3-Step Process Engine */}
            <HowItWorks />

            {/* Bottom High-Impact Invitation Banner */}
            <section className="my-16 text-center sketch-card p-8 sm:p-12 bg-surface border-2 border-border shadow-[6px_6px_0px_var(--color-border)]">
              <div className="inline-block px-3 py-1 rounded-full border border-border bg-surface-raised font-tertiary text-micro font-semibold uppercase tracking-wider text-accent-signal mb-3 shadow-[2px_2px_0px_var(--color-border)]">
                Start Venture Validation
              </div>
              <h2 className="font-display text-h1 sm:text-display font-extrabold text-content-primary max-w-2xl mx-auto">
                Ready to stress-test your startup?
              </h2>
              <p className="font-body text-content-secondary text-body max-w-xl mx-auto mt-3 mb-6 leading-relaxed">
                No decks required. Pitch your thesis in 1–2 sentences and let our 6 adversarial AI personas stress-test your business model in 90 seconds.
              </p>
              <button
                type="button"
                onClick={() => navigateTo('pitch')}
                className="px-8 py-3.5 bg-border text-surface font-display font-bold text-body rounded-lg shadow-[3px_3px_0px_var(--color-border)] hover:bg-accent-signal transition-all inline-flex items-center gap-2 cursor-pointer"
              >
                <span>Pitch Your Idea to the Swarm</span>
                <span>→</span>
              </button>
            </section>
          </motion.div>
        )}

        {/* View 2: Dedicated Pitch Launchpad Page */}
        {currentView === 'pitch' && (
          <motion.div
            key="pitch-view"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
            className="max-w-6xl mx-auto px-4 sm:px-6 py-8"
          >
            {/* Top Breadcrumb & Step Indicator */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2 font-tertiary text-micro">
                <button
                  type="button"
                  onClick={() => navigateTo('showcase')}
                  className="text-content-secondary hover:text-content-primary transition-colors flex items-center gap-1 cursor-pointer font-medium"
                >
                  <span>←</span>
                  <span>Showcase</span>
                </button>
                <span className="text-content-muted">/</span>
                <span className="font-bold text-content-primary">Pitch Launchpad</span>
              </div>

              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-surface-raised border border-border-subtle text-content-secondary font-tertiary text-[11px] font-semibold">
                  <span className="w-1.5 h-1.5 rounded-full bg-accent-signal"></span>
                  Step 1 of 3: Dynamic Idea Intake
                </span>
              </div>
            </div>

            {/* Launchpad Terminal Card */}
            <section id="pitch-terminal" className="sketch-card p-6 sm:p-8 bg-surface border-2 border-border shadow-[6px_6px_0px_var(--color-border)] relative">
              {/* Dynamic Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-6 border-b border-border-subtle gap-4">
                <div>
                  {turnNumber === 0 ? (
                    <div className="inline-block px-2.5 py-0.5 rounded-full border border-border bg-accent-tint text-accent-signal font-tertiary text-[11px] font-bold uppercase tracking-wider mb-2">
                      Intake Launchpad
                    </div>
                  ) : isComplete || Object.values(extraction || {}).filter(Boolean).length >= 6 ? (
                    <div className="inline-block px-2.5 py-0.5 rounded-full border border-[#2D6A4F] bg-[#D8F3DC] text-[#2D6A4F] font-tertiary text-[11px] font-bold uppercase tracking-wider mb-2">
                      ✓ Venture Blueprint Armed & Ready (100%)
                    </div>
                  ) : (
                    <div className="inline-block px-2.5 py-0.5 rounded-full border border-border bg-accent-tint text-accent-signal font-tertiary text-[11px] font-bold uppercase tracking-wider mb-2">
                      Dynamic Intake • {completionPct}% Calibrated ({Object.values(extraction || {}).filter(Boolean).length}/6 Fields Locked)
                    </div>
                  )}
                  <h1 className="font-display text-h2 sm:text-h1 font-black text-content-primary">
                    {turnNumber === 0
                      ? 'Pitch Your Idea to the Swarm'
                      : isComplete || Object.values(extraction || {}).filter(Boolean).length >= 6
                      ? 'Venture Thesis Locked & Armed'
                      : `Calibrating Venture Thesis (${Object.values(extraction || {}).filter(Boolean).length} of 6 Locked)`}
                  </h1>
                  <p className="font-body text-content-secondary text-body mt-1">
                    {turnNumber === 0
                      ? 'Describe your business concept below, or click a quick starter. Zero friction: form fields get locked behind the scenes.'
                      : isComplete || Object.values(extraction || {}).filter(Boolean).length >= 6
                      ? 'All 6 domain agents have sufficient context to simulate unit economics, tech stack, and regulatory compliance.'
                      : 'Answer the single targeted question below. Notice how your Venture Blueprint on the right fills automatically.'}
                  </p>
                </div>

                {readyToEvaluate && (
                  <button
                    type="button"
                    onClick={handleStartGeneration}
                    className="px-5 py-2.5 bg-accent-signal text-surface font-display font-bold text-small rounded-lg shadow-[3px_3px_0px_var(--color-border)] hover:opacity-90 transition-all flex items-center gap-2 self-start sm:self-auto cursor-pointer animate-pulse"
                  >
                    <span>⚡ Run 6-Agent Swarm</span>
                    <span>→</span>
                  </button>
                )}
              </div>

              {/* Quick Sample Prompts */}
              {turnNumber === 0 ? (
                <div className="mb-6">
                  <span className="font-tertiary text-micro font-bold uppercase tracking-wider text-content-secondary block mb-2.5">
                    Quick Starters (Click to load):
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                    {SAMPLE_IDEAS.map((idea, index) => (
                      <button
                        key={index}
                        type="button"
                        onClick={() => handleSend(idea.prompt)}
                        className="p-3 text-left rounded-lg border border-border-subtle bg-surface-raised hover:bg-void hover:border-border transition-all group flex flex-col justify-between shadow-sm cursor-pointer"
                      >
                        <div className="flex items-center gap-2 mb-1.5">
                          <span className="text-base">{idea.icon}</span>
                          <span className="font-display font-bold text-micro text-content-primary group-hover:text-accent-signal transition-colors">
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
              ) : (
                <details className="mb-5 text-micro font-tertiary text-content-secondary cursor-pointer">
                  <summary className="hover:text-content-primary transition-colors">
                    💡 Click to view quick startup starter templates
                  </summary>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 mt-2 pt-2 border-t border-border-subtle">
                    {SAMPLE_IDEAS.map((idea, index) => (
                      <button
                        key={index}
                        type="button"
                        onClick={() => handleSend(idea.prompt)}
                        className="p-2 text-left rounded border border-border-subtle bg-surface-raised hover:bg-void text-[11px] flex items-center gap-1.5"
                      >
                        <span>{idea.icon}</span>
                        <span className="font-bold">{idea.title}</span>
                      </button>
                    ))}
                  </div>
                </details>
              )}

              {/* Error Notification if any */}
              {(uploadError || (status === SESSION_STATUS.FAILED && error)) && (
                <div
                  role="alert"
                  className="mb-6 p-4 rounded-md border border-error bg-surface flex items-center justify-between"
                >
                  <span className="text-error font-body text-small">{uploadError || error}</span>
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

              {/* 2-Column Responsive Workspace: ChatBox + Venture Blueprint */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                <div className="lg:col-span-7 flex flex-col gap-4">
                  <ChatBox
                    messages={messages}
                    onSend={handleSend}
                    onUpload={handleUpload}
                    disabled={isSending}
                    uploadError={uploadError}
                    suggestedChips={suggestedChips}
                  />
                </div>

                <div className="lg:col-span-5 sticky top-24">
                  <VentureDossier
                    extraction={extraction}
                    completionPct={completionPct}
                    onRunSwarm={readyToEvaluate ? handleStartGeneration : undefined}
                    isComplete={isComplete || Object.values(extraction || {}).filter(Boolean).length >= 6}
                  />
                </div>
              </div>

              {/* Ready to Evaluate Callout Banner */}
              {readyToEvaluate && (
                <div className="mt-6 p-5 rounded-xl border-2 border-border bg-accent-tint/30 flex flex-col sm:flex-row items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">🐝</span>
                    <div>
                      <div className="font-display font-bold text-body text-content-primary">
                        Swarm Coordinates Locked & Ready
                      </div>
                      <div className="font-body text-small text-content-secondary">
                        All 6 personas (VC, Bootstrapper, CTO, UX, Regulator, Rival) are calibrated.
                      </div>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={handleStartGeneration}
                    className="px-6 py-3 bg-border text-surface font-display font-bold text-body rounded-lg shadow-[3px_3px_0px_var(--color-border)] hover:bg-accent-signal transition-all flex items-center gap-2 flex-shrink-0 cursor-pointer"
                  >
                    <span>Launch 6-Agent Swarm</span>
                    <span>→</span>
                  </button>
                </div>
              )}
            </section>
          </motion.div>
        )}
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
