import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import mascotPng from '../../assets/landing/mascot_peeking_left_edge.png'

const AGENT_WHISPERS = [
  { agent: 'VC', quote: 'Make sure your market TAM is >$1B with a 12-month Series A trajectory.' },
  { agent: 'Lean Founder', quote: 'Cut the fluff. Ship the core loop in 4 weeks on $5K.' },
  { agent: 'Enterprise CTO', quote: 'Design for SOC-2 Type II and 10M concurrent scale from day 1.' },
  { agent: 'UX Researcher', quote: 'If onboarding takes more than 3 steps, 80% of users will abandon.' },
  { agent: 'Regulator', quote: 'Verify regional data residency and GDPR/DPDP obligations early.' },
  { agent: 'Adversary', quote: 'A $10M rival will clone your frontend in 48 hours unless you have deep moat.' },
]

export default function PeekingMascot({ onSelectSample }) {
  const [isOpen, setIsOpen] = useState(false)
  const [whisperIdx, setWhisperIdx] = useState(0)
  const isInteracting = useRef(false)

  const cycleWhisper = (e) => {
    e.stopPropagation()
    setWhisperIdx((prev) => (prev + 1) % AGENT_WHISPERS.length)
  }

  const scrollToSection = (id) => {
    const el = document.getElementById(id)
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' })
      setIsOpen(false)
    }
  }

  return (
    <aside
      aria-label="PRISM Observer companion"
      className="hidden lg:block fixed left-0 bottom-0 z-40 select-none"
    >
      <div className="relative flex items-end">
        {/* The Clinging Mascot Image */}
        <motion.button
          type="button"
          onClick={() => setIsOpen((prev) => !prev)}
          onMouseEnter={() => {
            if (!isOpen) isInteracting.current = true
          }}
          whileHover={{ x: 6 }}
          whileTap={{ scale: 0.97 }}
          className="relative flex items-end cursor-pointer group focus:outline-none"
          title="Click PRISM Observer for quick navigation and tips"
        >
          {/* Edge image flush against left screen border & bottom corner — prominent and clearly visible */}
          <img
            src={mascotPng}
            alt="PRISM Swarm Observer peeking from corner"
            style={{ width: '135px', maxWidth: '135px' }}
            className="h-auto drop-shadow-lg transition-transform duration-200"
            draggable="false"
          />

          {/* Vertical badge tab along the edge */}
          <div className="absolute left-24 bottom-28 -rotate-90 origin-left px-2.5 py-0.5 bg-border text-surface rounded-t-md font-tertiary text-[10px] font-bold tracking-wider uppercase shadow-[2px_2px_0px_var(--color-border)] group-hover:bg-accent-signal transition-colors pointer-events-none whitespace-nowrap">
            {isOpen ? 'Close' : '✦ Observer'}
          </div>
        </motion.button>

        {/* Flyout Useful Drawer / Quick Actions Card */}
        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, x: -16, y: 10, scale: 0.95 }}
              animate={{ opacity: 1, x: 0, y: 0, scale: 1 }}
              exit={{ opacity: 0, x: -16, y: 10, scale: 0.95 }}
              transition={{ type: 'spring', stiffness: 350, damping: 25 }}
              className="absolute left-36 bottom-6 w-80 sketch-card p-4 bg-surface border-2 border-border shadow-[5px_5px_0px_var(--color-border)] rounded-xl font-body text-content-primary z-50"
            >
              {/* Card Header */}
              <div className="flex items-center justify-between pb-2 mb-3 border-b border-border-subtle">
                <div className="flex items-center gap-2">
                  <span className="font-display font-bold text-small text-content-primary">
                    PRISM Observer
                  </span>
                  <span className="px-1.5 py-0.2 bg-accent-tint text-accent-signal border border-border-subtle text-[10px] font-tertiary font-bold rounded">
                    Active
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => setIsOpen(false)}
                  className="text-content-muted hover:text-content-primary font-bold text-micro p-1"
                  aria-label="Close observer"
                >
                  ✕
                </button>
              </div>

              {/* Agent Whisper / Rotating Tip */}
              <div className="p-2.5 bg-surface-raised border border-border-subtle rounded-lg mb-3">
                <div className="flex items-center justify-between text-micro font-tertiary font-bold text-content-secondary mb-1">
                  <span>{AGENT_WHISPERS[whisperIdx].agent} Insight</span>
                  <button
                    type="button"
                    onClick={cycleWhisper}
                    className="text-accent-signal hover:underline text-[10px] font-semibold"
                  >
                    Next tip →
                  </button>
                </div>
                <p className="font-body text-micro text-content-primary italic leading-snug">
                  &ldquo;{AGENT_WHISPERS[whisperIdx].quote}&rdquo;
                </p>
              </div>

              {/* Quick Useful Actions */}
              <div className="space-y-1.5">
                <button
                  type="button"
                  onClick={() => scrollToSection('pitch-terminal')}
                  className="w-full text-left px-3 py-2 rounded-md bg-void hover:bg-accent-tint/40 border border-border-subtle hover:border-border font-display font-semibold text-micro text-content-primary flex items-center justify-between transition-colors group"
                >
                  <span>🚀 Jump to Idea Intake</span>
                  <span className="text-accent-signal font-bold group-hover:translate-x-0.5 transition-transform">→</span>
                </button>

                <button
                  type="button"
                  onClick={() => scrollToSection('swarm-heading')}
                  className="w-full text-left px-3 py-2 rounded-md bg-void hover:bg-accent-tint/40 border border-border-subtle hover:border-border font-display font-semibold text-micro text-content-primary flex items-center justify-between transition-colors group"
                >
                  <span>👥 Inspect 6 Agents</span>
                  <span className="text-accent-signal font-bold group-hover:translate-x-0.5 transition-transform">→</span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    onSelectSample?.()
                    scrollToSection('pitch-terminal')
                  }}
                  className="w-full text-left px-3 py-2 rounded-md bg-void hover:bg-accent-tint/40 border border-border-subtle hover:border-border font-display font-semibold text-micro text-content-primary flex items-center justify-between transition-colors group"
                >
                  <span>💡 Try a Sample Pitch</span>
                  <span className="text-accent-signal font-bold group-hover:translate-x-0.5 transition-transform">→</span>
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </aside>
  )
}
