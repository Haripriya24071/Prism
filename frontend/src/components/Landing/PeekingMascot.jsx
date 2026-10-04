import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import mascotPng from '../../assets/landing/mascot_peeking_left_edge.png'

const AGENT_WHISPERS = [
  {
    agent: 'Silicon Valley VC',
    quote: 'Make sure your market TAM is >$1B with a defensible moat and 12-month Series A trajectory.',
  },
  {
    agent: 'Bootstrapped Founder',
    quote: 'Cut the fluff. Ship the core loop in 4 weeks on $5K. Validate paying demand first.',
  },
  {
    agent: 'Enterprise CTO',
    quote: 'Design for zero vendor lock-in, SOC-2 Type II audit, and 10M concurrent transactions.',
  },
  {
    agent: 'UX Researcher',
    quote: 'If onboarding takes more than 3 steps, 80% of users will abandon before experiencing value.',
  },
  {
    agent: 'Government Regulator',
    quote: 'Verify regional data residency, DPDP Act, and sector licensing before cross-border launch.',
  },
  {
    agent: 'Well-Funded Rival',
    quote: 'I will clone your frontend in 48 hours unless you have proprietary data or strong network moats.',
  },
]

export default function PeekingMascot({
  currentView = 'showcase',
  onNavigate,
  onSelectSample,
  activeTab = 'overview',
  onNavigateTab,
  onDownloadPdf,
}) {
  const [isOpen, setIsOpen] = useState(false)
  const [whisperIdx, setWhisperIdx] = useState(0)
  const mascotRef = useRef(null)

  // Listen for global observer toggle events (e.g. from top navbar)
  useEffect(() => {
    const handleToggle = () => setIsOpen((prev) => !prev)
    window.addEventListener('prism-toggle-observer', handleToggle)
    return () => window.removeEventListener('prism-toggle-observer', handleToggle)
  }, [])

  // Close console on click outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (mascotRef.current && !mascotRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const cycleWhisper = (e) => {
    e.stopPropagation()
    setWhisperIdx((prev) => (prev + 1) % AGENT_WHISPERS.length)
  }

  const handleNavAndScroll = (view, sectionId) => {
    setIsOpen(false)
    if (onNavigate && currentView !== view) {
      onNavigate(view)
      if (sectionId) {
        setTimeout(() => {
          const el = document.getElementById(sectionId)
          if (el) el.scrollIntoView({ behavior: 'smooth' })
        }, 150)
      }
    } else if (sectionId) {
      const el = document.getElementById(sectionId)
      if (el) el.scrollIntoView({ behavior: 'smooth' })
    }
  }

  const activeWhisper = AGENT_WHISPERS[whisperIdx]

  return (
    <aside
      ref={mascotRef}
      aria-label="PRISM Observer companion"
      className="fixed left-0 bottom-0 z-40 select-none pointer-events-none"
    >
      <div className="relative flex items-end pointer-events-auto">
        {/* Mascot Peeking Button */}
        <motion.button
          type="button"
          onClick={() => setIsOpen((prev) => !prev)}
          whileHover={{ x: 8 }}
          whileTap={{ scale: 0.98 }}
          className="relative flex items-end cursor-pointer group focus:outline-none"
          title="Click PRISM Observer for quick swarm insights and navigation"
          aria-expanded={isOpen}
        >
          {/* Scaled mascot image */}
          <img
            src={mascotPng}
            alt="PRISM Swarm Observer peeking from corner"
            style={{ width: '155px', maxWidth: '155px' }}
            className="h-auto drop-shadow-xl transition-transform duration-200"
            draggable="false"
          />

          {/* Clean vertical comic tab along his edge */}
          <div className="absolute left-[135px] bottom-[95px] -rotate-90 origin-bottom-left px-3 py-1 bg-border text-surface rounded-t-md font-tertiary text-micro font-bold tracking-wider uppercase shadow-[2px_2px_0px_var(--color-border)] group-hover:bg-accent-signal transition-colors pointer-events-none whitespace-nowrap flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-accent-glow animate-pulse"></span>
            <span>{isOpen ? 'Close ✕' : '✦ Observer'}</span>
          </div>
        </motion.button>

        {/* Flyout Observer Console Drawer */}
        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, x: -16, y: 8, scale: 0.96 }}
              animate={{ opacity: 1, x: 0, y: 0, scale: 1 }}
              exit={{ opacity: 0, x: -16, y: 8, scale: 0.96 }}
              transition={{ type: 'spring', stiffness: 350, damping: 25 }}
              className="absolute left-[165px] bottom-6 w-[330px] sketch-card p-4 sm:p-5 bg-surface border-2 border-border shadow-[5px_5px_0px_var(--color-border)] rounded-xl font-body text-content-primary z-50"
            >
              {/* Card Header */}
              <div className="flex items-center justify-between pb-2.5 mb-2.5 border-b border-border-subtle">
                <div className="flex items-center gap-2">
                  <span className="font-display font-bold text-sm text-content-primary">
                    PRISM Observer
                  </span>
                  <span className="px-2 py-0.5 bg-accent-tint text-accent-signal border border-border-subtle text-[10px] font-tertiary font-bold rounded-full">
                    {currentView === 'workspace' ? 'Swarm Synthesized ✓' : currentView === 'pitch' ? 'Pitch Mode Active' : 'Swarm Standby'}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => setIsOpen(false)}
                  className="w-6 h-6 rounded hover:bg-surface-raised flex items-center justify-center text-content-muted hover:text-content-primary font-bold text-xs transition-colors cursor-pointer"
                  aria-label="Close observer"
                >
                  ✕
                </button>
              </div>

              {/* Agent Whisper / Rotating Tip */}
              <div className="p-2.5 bg-surface-raised border border-border-subtle rounded-lg mb-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-tertiary text-[11px] font-bold text-content-primary flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-accent-signal"></span>
                    <span>{activeWhisper.agent}</span>
                  </span>
                  <button
                    type="button"
                    onClick={cycleWhisper}
                    className="text-accent-signal hover:underline text-[10px] font-semibold cursor-pointer"
                  >
                    Next tip →
                  </button>
                </div>
                <p className="font-body text-xs text-content-secondary italic leading-relaxed">
                  &ldquo;{activeWhisper.quote}&rdquo;
                </p>
              </div>

              {/* Quick Actions tailored by current view */}
              <div className="space-y-1.5">
                {currentView === 'workspace' ? (
                  <>
                    <div className="text-[10px] font-mono font-bold text-content-muted uppercase tracking-wider mb-1">
                      Quick Workspace Jump
                    </div>

                    {[
                      { id: 'overview', label: '01. Overview & Verdict', icon: '📊' },
                      { id: 'swarm', label: '02. 6-Agent Swarm', icon: '🐝' },
                      { id: 'deliberation', label: '03. Contested Battles', icon: '⚔️' },
                      { id: 'final_brd', label: '04. Final BRD Spec', icon: '📑' },
                      { id: 'risks', label: '05. Risks & Traps', icon: '⚠️' },
                      { id: 'export', label: '06. Export Center', icon: '📥' },
                    ].map((item) => (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() => {
                          setIsOpen(false)
                          onNavigateTab?.(item.id)
                        }}
                        className={`w-full text-left px-2.5 py-1.5 rounded border font-display text-xs flex items-center justify-between transition-all cursor-pointer ${
                          activeTab === item.id
                            ? 'bg-accent-tint border-border font-bold text-content-primary shadow-xs'
                            : 'bg-surface hover:bg-surface-raised border-border-subtle hover:border-border text-content-secondary'
                        }`}
                      >
                        <span className="flex items-center gap-2">
                          <span>{item.icon}</span>
                          <span>{item.label}</span>
                        </span>
                        <span className="text-[10px] text-content-muted">→</span>
                      </button>
                    ))}

                    {onDownloadPdf && (
                      <button
                        type="button"
                        onClick={() => {
                          setIsOpen(false)
                          onDownloadPdf('final')
                        }}
                        className="w-full mt-2 px-3 py-2 rounded-lg bg-accent-signal text-void font-display font-bold text-xs flex items-center justify-center gap-1.5 shadow-xs hover:opacity-90 transition-opacity cursor-pointer"
                      >
                        <span>📥 Download Master BRD (PDF)</span>
                      </button>
                    )}
                  </>
                ) : currentView === 'pitch' ? (
                  <>
                    <button
                      type="button"
                      onClick={() => {
                        setIsOpen(false)
                        onSelectSample?.()
                      }}
                      className="w-full text-left px-3.5 py-2.5 rounded-lg bg-surface hover:bg-surface-raised border border-border-subtle hover:border-border font-display font-semibold text-small text-content-primary flex items-center justify-between transition-all group shadow-sm cursor-pointer"
                    >
                      <span className="flex items-center gap-2.5">
                        <span>💡</span>
                        <span>Load Sample Pitch Idea</span>
                      </span>
                      <span className="text-content-muted group-hover:text-accent-signal group-hover:translate-x-1 transition-all">→</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => handleNavAndScroll('showcase', 'swarm-heading')}
                      className="w-full text-left px-3.5 py-2.5 rounded-lg bg-surface hover:bg-surface-raised border border-border-subtle hover:border-border font-display font-semibold text-small text-content-primary flex items-center justify-between transition-all group shadow-sm cursor-pointer"
                    >
                      <span className="flex items-center gap-2.5">
                        <span>👥</span>
                        <span>Review 6 Competing Minds</span>
                      </span>
                      <span className="text-content-muted group-hover:text-accent-signal group-hover:translate-x-1 transition-all">→</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => handleNavAndScroll('showcase', 'how-it-works')}
                      className="w-full text-left px-3.5 py-2.5 rounded-lg bg-surface hover:bg-surface-raised border border-border-subtle hover:border-border font-display font-semibold text-small text-content-primary flex items-center justify-between transition-all group shadow-sm cursor-pointer"
                    >
                      <span className="flex items-center gap-2.5">
                        <span>⚙️</span>
                        <span>How The Swarm Operates</span>
                      </span>
                      <span className="text-content-muted group-hover:text-accent-signal group-hover:translate-x-1 transition-all">→</span>
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      type="button"
                      onClick={() => handleNavAndScroll('pitch', 'pitch-terminal')}
                      className="w-full text-left px-3.5 py-2.5 rounded-lg bg-surface hover:bg-surface-raised border border-border-subtle hover:border-border font-display font-semibold text-small text-content-primary flex items-center justify-between transition-all group shadow-sm cursor-pointer"
                    >
                      <span className="flex items-center gap-2.5">
                        <span>⚡</span>
                        <span>Jump to Pitch Launchpad</span>
                      </span>
                      <span className="text-content-muted group-hover:text-accent-signal group-hover:translate-x-1 transition-all">→</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => handleNavAndScroll('showcase', 'swarm-heading')}
                      className="w-full text-left px-3.5 py-2.5 rounded-lg bg-surface hover:bg-surface-raised border border-border-subtle hover:border-border font-display font-semibold text-small text-content-primary flex items-center justify-between transition-all group shadow-sm cursor-pointer"
                    >
                      <span className="flex items-center gap-2.5">
                        <span>👥</span>
                        <span>Inspect 6 Competing Minds</span>
                      </span>
                      <span className="text-content-muted group-hover:text-accent-signal group-hover:translate-x-1 transition-all">→</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => {
                        setIsOpen(false)
                        onSelectSample?.()
                      }}
                      className="w-full text-left px-3.5 py-2.5 rounded-lg bg-surface hover:bg-surface-raised border border-border-subtle hover:border-border font-display font-semibold text-small text-content-primary flex items-center justify-between transition-all group shadow-sm cursor-pointer"
                    >
                      <span className="flex items-center gap-2.5">
                        <span>💡</span>
                        <span>Try a Sample Pitch</span>
                      </span>
                      <span className="text-content-muted group-hover:text-accent-signal group-hover:translate-x-1 transition-all">→</span>
                    </button>
                  </>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </aside>
  )
}

