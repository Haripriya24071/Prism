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

export default function PeekingMascot({ currentView = 'showcase', onNavigate, onSelectSample }) {
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
      className="hidden lg:block fixed left-0 bottom-0 z-40 select-none pointer-events-none"
    >
      <div className="relative flex items-end pointer-events-auto">
        {/* Mascot Peeking Button */}
        <motion.button
          type="button"
          onClick={() => setIsOpen((prev) => !prev)}
          whileHover={{ x: 6 }}
          whileTap={{ scale: 0.98 }}
          className="relative flex items-end cursor-pointer group focus:outline-none"
          title="Click PRISM Observer for quick swarm insights and navigation"
          aria-expanded={isOpen}
        >
          {/* Scaled-up mascot image */}
          <img
            src={mascotPng}
            alt="PRISM Swarm Observer peeking from corner"
            style={{ width: '165px', maxWidth: '165px' }}
            className="h-auto drop-shadow-xl transition-transform duration-200"
            draggable="false"
          />

          {/* Clean vertical tab along his edge */}
          <div className="absolute left-[142px] bottom-[110px] -rotate-90 origin-bottom-left px-3 py-1 bg-border text-surface rounded-t-md font-tertiary text-micro font-bold tracking-wider uppercase shadow-[2px_2px_0px_var(--color-border)] group-hover:bg-accent-signal transition-colors pointer-events-none whitespace-nowrap flex items-center gap-1.5">
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
              className="absolute left-[175px] bottom-10 w-[340px] sketch-card p-4 sm:p-5 bg-surface border-2 border-border shadow-[6px_6px_0px_var(--color-border)] rounded-xl font-body text-content-primary z-50"
            >
              {/* Card Header */}
              <div className="flex items-center justify-between pb-3 mb-3 border-b border-border-subtle">
                <div className="flex items-center gap-2">
                  <span className="font-display font-bold text-body text-content-primary">
                    PRISM Observer
                  </span>
                  <span className="px-2 py-0.5 bg-accent-tint text-accent-signal border border-border-subtle text-[10px] font-tertiary font-bold rounded-full">
                    {currentView === 'pitch' ? 'Pitch Mode Active' : 'Swarm Standby'}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => setIsOpen(false)}
                  className="w-6 h-6 rounded-md hover:bg-surface-raised flex items-center justify-center text-content-muted hover:text-content-primary font-bold text-small transition-colors cursor-pointer"
                  aria-label="Close observer"
                >
                  ✕
                </button>
              </div>

              {/* Agent Whisper / Rotating Tip */}
              <div className="p-3 bg-surface-raised border border-border-subtle rounded-lg mb-3">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-tertiary text-micro font-bold text-content-primary flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-accent-signal"></span>
                    <span>{activeWhisper.agent}</span>
                  </span>
                  <button
                    type="button"
                    onClick={cycleWhisper}
                    className="text-accent-signal hover:underline text-micro font-semibold cursor-pointer"
                  >
                    Next tip →
                  </button>
                </div>
                <p className="font-body text-small text-content-secondary italic leading-relaxed">
                  &ldquo;{activeWhisper.quote}&rdquo;
                </p>
              </div>

              {/* Quick Useful Actions tailored by current view */}
              <div className="space-y-2">
                {currentView === 'pitch' ? (
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

