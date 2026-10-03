import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import vcImg from '../../assets/landing/agents/agent_vc.jpg'
import leanImg from '../../assets/landing/agents/agent_lean.jpg'
import ctoImg from '../../assets/landing/agents/agent_cto.jpg'
import uxImg from '../../assets/landing/agents/agent_ux.jpg'
import regImg from '../../assets/landing/agents/agent_regulator.jpg'
import advImg from '../../assets/landing/agents/agent_adversarial.jpg'

const AGENTS = [
  {
    id: 'vc',
    name: 'Silicon Valley Seed VC',
    title: 'Silicon Valley Seed VC',
    archetype: 'The Scaler',
    avatar: vcImg,
    badgeColor: 'border-agent-vc text-agent-vc',
    bgTint: 'bg-[#6D28D9]/10',
    mandate: 'Maximise fundability, TAM, and defensible moats. Ignore initial cost constraints.',
    fatalQuestion: 'Is this an explosive $1B+ venture opportunity, or just a small lifestyle tool?',
    axes: ['Market size >$1B TAM', '12-mo path to Series A', 'Defensible network effect'],
    quote: 'Show me the defensible moat and viral expansion loop, or this is just a feature.',
  },
  {
    id: 'lean_founder',
    name: 'Bootstrapped Founder',
    title: 'Bootstrapped Founder',
    archetype: 'The Pragmatist',
    avatar: leanImg,
    badgeColor: 'border-agent-lean text-agent-lean',
    bgTint: 'bg-[#0284C7]/10',
    mandate: 'Ship MVP in 4 weeks on $5K. Cut every feature that is not the absolute core loop.',
    fatalQuestion: 'Can one developer build this in 30 days and collect real customer revenue by week 5?',
    axes: ['Zero paid marketing', 'Single developer execution', 'Revenue by week 5 or pivot'],
    quote: 'If we cannot collect paying dollars from 10 customers next month, shut it down.',
  },
  {
    id: 'enterprise_cto',
    name: 'Enterprise CTO',
    title: 'Enterprise CTO',
    archetype: 'The Architect',
    avatar: ctoImg,
    badgeColor: 'border-agent-cto text-agent-cto',
    bgTint: 'bg-[#15803D]/10',
    mandate: 'Scalability, zero vendor lock-in, and security-first architecture at all times.',
    fatalQuestion: 'Will your system survive 10M concurrent transactions and pass SOC2 Type II audit?',
    axes: ['Scale to 10M concurrent users', 'SOC2 Type II from day 1', 'Zero single-vendor lock-in'],
    quote: 'A fragile architecture with single points of failure will crash on day one.',
  },
  {
    id: 'ux_researcher',
    name: 'UX Researcher',
    title: 'UX Researcher',
    archetype: 'The Humanist',
    avatar: uxImg,
    badgeColor: 'border-agent-ux text-agent-ux',
    bgTint: 'bg-[#D97706]/10',
    mandate: 'Surface real user pain, adoption barriers, and accessibility failures.',
    fatalQuestion: 'Does this solve excruciating human pain, or are users merely being polite in surveys?',
    axes: ['WCAG 2.1 AA minimum', 'Ethnographic validation', 'Zero deceptive dark patterns'],
    quote: 'Your onboarding friction has 6 drop-off points. Nobody will finish this flow.',
  },
  {
    id: 'regulator',
    name: 'Government Policy Expert',
    title: 'Government Policy Expert',
    archetype: 'The Guardian',
    avatar: regImg,
    badgeColor: 'border-agent-regulator text-agent-regulator',
    bgTint: 'bg-[#4F46E5]/10',
    mandate: 'Identify every legal landmine, compliance liability, and licensing obligation.',
    fatalQuestion: 'What are the GDPR, DPDP Act, and regional liabilities that could bankrupt your venture?',
    axes: ['GDPR and DPDP compliance', 'Regional data residency', 'Sector-specific licensing'],
    quote: 'Operating across borders without sovereign data residency invites fatal regulatory fines.',
  },
  {
    id: 'adversarial',
    name: 'Well-Funded Rival',
    title: 'Well-Funded Rival',
    archetype: 'The Assassin',
    avatar: advImg,
    badgeColor: 'border-agent-adversarial text-agent-adversarial',
    bgTint: 'bg-[#BE123C]/10',
    mandate: 'Find every weakness, gap, and exploit. Formulate 3 fatal kill-shots to crush this idea.',
    fatalQuestion: 'If I deploy $10M and clone your features in 48 hours, why do you still exist?',
    axes: ['$10M budget to compete directly', '18 months to reach parity', 'Identify 3 fastest kill-shots'],
    quote: 'I will commoditize your core feature, bundle it for free, and starve your distribution.',
  },
]

export default function AgentsShowcase({ onSelectAgent }) {
  const [selectedAgent, setSelectedAgent] = useState(AGENTS[0])

  return (
    <section className="my-16" aria-labelledby="swarm-heading">
      {/* Section Header */}
      <div className="text-center max-w-2xl mx-auto mb-10">
        <div className="inline-block px-3 py-1 rounded-full border border-border bg-surface-raised font-tertiary text-micro font-semibold uppercase tracking-widest text-content-secondary mb-3 shadow-[2px_2px_0px_var(--color-border)]">
          The 6 Competing Minds
        </div>
        <h2 id="swarm-heading" className="font-display text-h1 sm:text-display font-extrabold text-content-primary">
          Meet Your Adversaries
        </h2>
        <p className="font-body text-content-secondary text-body mt-3 leading-relaxed">
          Not polite AI cheerleaders. Six specialized personas with diametrically opposed incentives
          who argue, diverge, and stress-test every angle of your venture before the market does.
        </p>
      </div>

      {/* 6 Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {AGENTS.map((agent) => {
          const isSelected = selectedAgent.id === agent.id

          return (
            <motion.div
              key={agent.id}
              onClick={() => {
                setSelectedAgent(agent)
                onSelectAgent?.(agent)
              }}
              whileHover={{ y: -4, transition: { duration: 0.15 } }}
              className={`sketch-card p-5 cursor-pointer relative overflow-hidden transition-all flex flex-col justify-between ${
                isSelected ? 'ring-2 ring-border shadow-[5px_5px_0px_var(--color-border)]' : 'shadow-[3px_3px_0px_var(--color-border)]'
              }`}
            >
              <div>
                {/* Header row: Archetype Tag + Indicator */}
                <div className="flex items-center justify-between mb-3">
                  <span className={`inline-flex items-center justify-center px-3.5 py-1 rounded-full border text-micro font-tertiary font-bold uppercase tracking-wider leading-none ${agent.badgeColor} ${agent.bgTint}`}>
                    {agent.archetype}
                  </span>
                  <span className="font-tertiary text-micro text-content-muted">0{AGENTS.indexOf(agent) + 1}</span>
                </div>

                {/* Portrait + Name */}
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-16 h-16 rounded-xl border-2 border-border overflow-hidden bg-surface-raised flex-shrink-0 shadow-[2px_2px_0px_var(--color-border)]">
                    <img
                      src={agent.avatar}
                      alt={agent.title || agent.name}
                      className="w-full h-full object-cover"
                      loading="lazy"
                    />
                  </div>
                  <div>
                    <h3 className="font-display text-h3 font-bold text-content-primary leading-tight">
                      {agent.name}
                    </h3>
                    <p className="font-body text-micro text-content-secondary mt-0.5">
                      {agent.mandate}
                    </p>
                  </div>
                </div>

                {/* Fatal Question */}
                <div className="p-3 bg-surface-raised border border-border-subtle rounded-lg mb-3">
                  <span className="font-tertiary text-micro font-bold text-content-primary uppercase tracking-wide block mb-1">
                    The Fatal Question:
                  </span>
                  <p className="font-body text-small text-content-primary italic leading-snug">
                    &ldquo;{agent.fatalQuestion}&rdquo;
                  </p>
                </div>
              </div>

              {/* Constraint Axes Tags */}
              <div className="pt-2 border-t border-border-subtle">
                <div className="flex flex-wrap gap-1.5">
                  {agent.axes.map((axis, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 rounded-md bg-void border border-border-subtle text-[11px] font-body text-content-secondary"
                    >
                      {axis}
                    </span>
                  ))}
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Interactive Stance Preview Banner */}
      <AnimatePresence mode="wait">
        {selectedAgent && (
          <motion.div
            key={selectedAgent.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mt-8 p-6 sketch-card bg-surface border-2 border-border shadow-[4px_4px_0px_var(--color-border)] flex flex-col md:flex-row items-center gap-6"
          >
            <div className="w-20 h-20 rounded-xl border-2 border-border overflow-hidden bg-surface-raised flex-shrink-0 shadow-[3px_3px_0px_var(--color-border)]">
              <img
                src={selectedAgent.avatar}
                alt={selectedAgent.title || selectedAgent.name}
                className="w-full h-full object-cover"
              />
            </div>
            <div className="flex-1 text-center md:text-left">
              <div className="flex items-center justify-center md:justify-start gap-2 mb-1">
                <span className="font-display font-bold text-h3 text-content-primary">
                  {selectedAgent.name}
                </span>
                <span className={`inline-flex items-center justify-center text-micro px-3 py-1 rounded-full border font-tertiary font-semibold uppercase tracking-wider leading-none ${selectedAgent.badgeColor} ${selectedAgent.bgTint}`}>
                  {selectedAgent.archetype}
                </span>
              </div>
              <p className="font-body text-body text-content-primary italic">
                &ldquo;{selectedAgent.quote}&rdquo;
              </p>
            </div>
            <a
              href="#pitch-terminal"
              className="px-5 py-2.5 bg-border text-surface font-display font-semibold text-small rounded-lg shadow-[2px_2px_0px_var(--color-border)] hover:bg-accent-signal transition-colors flex-shrink-0"
            >
              Test Against {selectedAgent.archetype} ↓
            </a>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  )
}
