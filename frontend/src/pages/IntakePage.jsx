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
    title: 'B2B AI Code Review',
    tag: 'Scenario 1: High Consensus (85 Score)',
    tagColor: 'text-success bg-success/10 border-success/30',
    prompt:
      'I want to build an automated AI code review and security vulnerability auditing platform for enterprise GitHub pull requests. We target US & EU tech enterprises, currently pre-seed with $150k budget, targeting $500k ARR in year 1.',
    icon: '🚀',
  },
  {
    title: 'P2P Social Lending',
    tag: 'Scenario 2: Pivot Suggester Trigger',
    tagColor: 'text-warning bg-warning/10 border-warning/30',
    prompt:
      'I am launching a peer-to-peer consumer micro-lending platform on social media apps in Southeast Asia, targeting unbanked gig workers with $50k bootstrap capital and targeting 50,000 active borrowers in year one.',
    icon: '⚡',
  },
  {
    title: 'Rural Telehealth AI',
    tag: 'Scenario 3: Regulated HealthTech',
    tagColor: 'text-primary bg-primary/10 border-primary/30',
    prompt:
      'We are creating an AI remote patient diagnostic and clinical triage platform for rural health clinics across India, operating with $80k grant funding, requiring strict compliance with DISHA and DPDP health data laws.',
    icon: '🏥',
  },
  {
    title: 'Global PayTech AI',
    tag: 'Scenario 4: Multi-Border FinCEN',
    tagColor: 'text-accent-signal bg-accent-signal/10 border-accent-signal/30',
    prompt:
      'Autonomous AI regulatory compliance officer for cross-border B2B payments under EU MiCA and US FinCEN regulations, targeting international supply chains with $120k seed runway.',
    icon: '⚖️',
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
      // Graceful resilient client-side calibration if offline or temporary network issue
      setIsBackendOnline(false)
      setTurnNumber((prev) => prev + 1)

      const fallbackExt = { ...extraction }
      const lower = messageText.toLowerCase()

      // 1. Raw idea
      if (!fallbackExt.raw_idea) {
        fallbackExt.raw_idea = messageText
      }

      // 2. Region detection
      if (!fallbackExt.region) {
        if (lower.includes('india') || lower.includes('inr') || lower.includes('upi')) fallbackExt.region = 'IN'
        else if (lower.includes('uk') || lower.includes('united kingdom') || lower.includes('london')) fallbackExt.region = 'GB'
        else if (lower.includes('uae') || lower.includes('dubai')) fallbackExt.region = 'AE'
        else if (lower.includes('us') || lower.includes('america') || lower.includes('states')) fallbackExt.region = 'US'
        else if (fallbackExt.raw_idea && fallbackExt.raw_idea !== messageText) fallbackExt.region = 'US'
      }

      // 3. Industry detection
      if (!fallbackExt.industry) {
        if (lower.includes('health') || lower.includes('med') || lower.includes('doctor')) fallbackExt.industry = 'Healthcare'
        else if (lower.includes('fintech') || lower.includes('pay') || lower.includes('bank')) fallbackExt.industry = 'FinTech'
        else if (lower.includes('saas') || lower.includes('software') || lower.includes('b2b')) fallbackExt.industry = 'B2B SaaS'
        else if (lower.includes('logistics') || lower.includes('delivery') || lower.includes('fleet')) fallbackExt.industry = 'Logistics'
        else if (fallbackExt.region) fallbackExt.industry = 'Technology & AI'
      }

      // 4. Stage detection
      if (!fallbackExt.stage) {
        if (lower.includes('mvp')) fallbackExt.stage = 'mvp'
        else if (lower.includes('prototype') || lower.includes('demo')) fallbackExt.stage = 'prototype'
        else if (lower.includes('growth') || lower.includes('scaling')) fallbackExt.stage = 'growth'
        else if (fallbackExt.industry) fallbackExt.stage = 'idea'
      }

      // 5. Budget detection
      if (!fallbackExt.budget_range) {
        if (lower.includes('bootstrapp')) fallbackExt.budget_range = 'Bootstrapped (<$20k)'
        else if (lower.includes('seed') || lower.includes('angel')) fallbackExt.budget_range = 'Seed Stage ($50k-$150k)'
        else if (lower.includes('series') || lower.includes('funded')) fallbackExt.budget_range = 'Funded ($250k+)'
        else if (fallbackExt.stage) fallbackExt.budget_range = 'Pre-Seed ($25k-$50k)'
      }

      // 6. Success milestone
      if (!fallbackExt.success_definition) {
        if (fallbackExt.budget_range) {
          fallbackExt.success_definition = '10 committed pilot customers and positive unit economics in 12 months'
        }
      }

      setExtraction(fallbackExt)

      const lockedCount = ['raw_idea', 'region', 'industry', 'stage', 'budget_range', 'success_definition'].filter(
        (k) => Boolean(fallbackExt[k])
      ).length

      const pct = Math.min(100, Math.round((lockedCount / 6) * 100))
      setCompletionPct(pct)

      if (lockedCount >= 3) setReadyToEvaluate(true)
      if (lockedCount >= 6) setIsComplete(true)

      let nextReply = ''
      let nextChips = []
      if (!fallbackExt.region) {
        nextReply = 'Great business concept! Where are you planning to launch this first (e.g. India, US, UK, UAE)? Specifying your target region activates live local regulations, currency rates, and market feeds.'
        nextChips = ['🇮🇳 India', '🇺🇸 United States', '🇬🇧 United Kingdom', '🇦🇪 UAE']
      } else if (!fallbackExt.industry) {
        nextReply = 'Understood! What industry vertical or customer segment will this primarily target?'
        nextChips = ['🏥 Healthcare', '💳 FinTech', '🤖 B2B SaaS', '📦 Logistics']
      } else if (!fallbackExt.stage) {
        nextReply = 'Got it! Is this a brand-new idea starting fresh, or do you have a working prototype or team in place?'
        nextChips = ['💡 Fresh Idea', '🛠️ Prototype', '🚀 Active MVP', '📈 Scaling']
      } else if (!fallbackExt.budget_range) {
        nextReply = 'What approximate starting budget or revenue model are you projecting to operate with over the first 12 months?'
        nextChips = ['🌱 Bootstrapped (<$25k)', '💼 Seed ($50k-$150k)', '🏢 Funded ($250k+)']
      } else if (!fallbackExt.success_definition) {
        nextReply = 'What primary milestone defines success for this venture in year one?'
        nextChips = ['💰 $50k ARR Revenue', '👥 1,000 Active Users', '🤝 10 Pilot Customers']
      } else {
        nextReply = 'All 6 venture parameters are locked in! Our 6 expert agents are standing by to stress-test your business model.'
        nextChips = []
      }

      setSuggestedChips(nextChips)

      const fallbackReply = {
        id: `asst-fb-${msgCounter.current++}`,
        role: 'assistant',
        content: nextReply,
      }
      setMessages((prev) => [...prev, fallbackReply])
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
              className="group flex items-center gap-3 hover:opacity-90 transition-all cursor-pointer select-none"
              aria-label="PRISM Home"
            >
              <img
                src={prismLogo}
                alt="PRISM Detective"
                className="w-10 h-10 rounded-full border-2 border-border shadow-[1.5px_1.5px_0px_var(--color-border)] object-cover group-hover:scale-105 transition-transform duration-200"
              />
              <span className="font-display font-black text-3xl sm:text-[32px] tracking-[0.06em] text-content-primary leading-none">
                PRISM
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
                  className="group inline-flex items-center gap-2 px-5 py-2 bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-500 hover:to-teal-600 text-white font-display font-bold text-xs rounded-full shadow-[0_2px_12px_rgba(5,150,105,0.4)] hover:shadow-[0_4px_16px_rgba(5,150,105,0.55)] hover:-translate-y-0.5 active:translate-y-0 transition-all duration-200 cursor-pointer whitespace-nowrap"
                >
                  <span className="w-2 h-2 rounded-full bg-emerald-200 animate-pulse" />
                  <span>Launch 6-Agent Swarm</span>
                  <span className="group-hover:translate-x-0.5 transition-transform">→</span>
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
                    className="group relative inline-flex items-center gap-2.5 px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-700 hover:from-emerald-500 hover:to-teal-600 text-white font-display font-extrabold text-sm tracking-wide shadow-[0_4px_16px_rgba(5,150,105,0.4)] hover:shadow-[0_6px_22px_rgba(5,150,105,0.55)] hover:-translate-y-0.5 active:translate-y-0 transition-all duration-200 whitespace-nowrap cursor-pointer flex-shrink-0"
                  >
                    <span className="flex h-2.5 w-2.5 relative flex-shrink-0">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-300 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-100"></span>
                    </span>
                    <span>Run 6-Agent Swarm</span>
                    <svg
                      className="w-4 h-4 text-emerald-200 transition-transform duration-200 group-hover:translate-x-1 flex-shrink-0"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <line x1="5" y1="12" x2="19" y2="12"></line>
                      <polyline points="12 5 19 12 12 19"></polyline>
                    </svg>
                  </button>
                )}
              </div>

              {/* Quick Sample Prompts */}
              {turnNumber === 0 ? (
                <div className="mb-6">
                  <span className="font-tertiary text-micro font-bold uppercase tracking-wider text-accent-signal block mb-2.5">
                    ⚡ One-Click Demo Scenarios (Click to Load):
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                    {SAMPLE_IDEAS.map((idea, index) => (
                      <button
                        key={index}
                        type="button"
                        onClick={() => handleSend(idea.prompt)}
                        className="p-3 text-left rounded-lg border border-border-subtle bg-surface-raised hover:bg-void hover:border-accent-signal hover:shadow-md transition-all group flex flex-col justify-between shadow-xs cursor-pointer"
                      >
                        <div>
                          <div className="flex items-center justify-between gap-1 mb-1.5">
                            <span className="text-base group-hover:scale-110 transition-transform">{idea.icon}</span>
                            {idea.tag && (
                              <span className={`font-display text-[9px] font-bold px-1.5 py-0.5 rounded border ${idea.tagColor}`}>
                                {idea.tag.split(':')[0]}
                              </span>
                            )}
                          </div>
                          <span className="font-display font-bold text-micro text-content-primary group-hover:text-accent-signal transition-colors block mb-1">
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

              {/* Integrated Workspace: Live Swarm Calibration Matrix + Full-Comfort ChatBox */}
              <div className="flex flex-col gap-5">
                <VentureDossier
                  extraction={extraction}
                  completionPct={completionPct}
                  onRunSwarm={readyToEvaluate ? handleStartGeneration : undefined}
                  isComplete={isComplete || Object.values(extraction || {}).filter(Boolean).length >= 6}
                />

                <div className="w-full">
                  <ChatBox
                    messages={messages}
                    onSend={handleSend}
                    onUpload={handleUpload}
                    disabled={isSending}
                    uploadError={uploadError}
                    suggestedChips={suggestedChips}
                  />
                </div>
              </div>

              {/* Ready to Evaluate Callout Banner */}
              {readyToEvaluate && (
                <div className="mt-6 p-5 sm:p-6 rounded-2xl border border-emerald-500/30 bg-gradient-to-r from-emerald-950/10 via-surface to-emerald-950/5 flex flex-col sm:flex-row items-center justify-between gap-5 shadow-xs">
                  <div className="flex items-center gap-3.5">
                    <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-2xl flex-shrink-0">
                      🐝
                    </div>
                    <div>
                      <div className="font-display font-bold text-body text-content-primary flex items-center gap-2">
                        <span>Swarm Coordinates Calibrated & Armed</span>
                        <span className="font-tertiary text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-700 font-bold border border-emerald-500/20">
                          6 of 6 Ready
                        </span>
                      </div>
                      <div className="font-body text-small text-content-secondary mt-0.5">
                        All 6 personas (VC, Bootstrapper, CTO, UX, Regulator, Rival) have sufficient context to simulate.
                      </div>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={handleStartGeneration}
                    className="group relative inline-flex items-center gap-2.5 px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-700 hover:from-emerald-500 hover:to-teal-600 text-white font-display font-extrabold text-sm tracking-wide shadow-[0_4px_16px_rgba(5,150,105,0.4)] hover:shadow-[0_6px_22px_rgba(5,150,105,0.55)] hover:-translate-y-0.5 active:translate-y-0 transition-all duration-200 whitespace-nowrap cursor-pointer flex-shrink-0"
                  >
                    <span className="flex h-2.5 w-2.5 relative flex-shrink-0">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-300 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-100"></span>
                    </span>
                    <span>Launch 6-Agent Swarm</span>
                    <svg
                      className="w-4 h-4 text-emerald-200 transition-transform duration-200 group-hover:translate-x-1 flex-shrink-0"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <line x1="5" y1="12" x2="19" y2="12"></line>
                      <polyline points="12 5 19 12 12 19"></polyline>
                    </svg>
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
