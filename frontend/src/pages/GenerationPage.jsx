import { motion } from 'framer-motion'
import { getPageVariants } from '../animations/variants.js'
import AgentGrid from '../components/AgentGrid/AgentGrid.jsx'
import { useSSE } from '../hooks/useSSE.js'
import { SESSION_STATUS, useSession } from '../hooks/useSession.js'

const AGENT_CONFIGS = [
  { name: 'vc', title: 'VC Optimist' },
  { name: 'lean', title: 'Lean Founder' },
  { name: 'cto', title: 'CTO Pragmatist' },
  { name: 'ux', title: 'UX Advocate' },
  { name: 'regulator', title: 'Regulator' },
  { name: 'adversarial', title: 'Adversarial Critic' },
]

export default function GenerationPage() {
  const { sessionId, status, agentStatuses, error } = useSession()
  const { contextReady, progressPct, stageMessage } = useSSE(sessionId)

  const agents = AGENT_CONFIGS.map((agent) => ({
    ...agent,
    status: agentStatuses[agent.name] || 'pending',
  }))

  return (
    <motion.main
      className="min-h-screen bg-void p-8 font-body text-content-primary max-w-5xl mx-auto"
      variants={getPageVariants()}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      <header className="mb-8">
        <h1 className="font-display text-h1 font-bold text-content-primary">
          Phase 2: Swarm Generation
        </h1>
        <p className="font-body text-content-secondary mt-1">
          Six personas are independently developing and stress-testing the BRD.
        </p>

        {/* Live Pipeline Status line */}
        <div className="mt-4 flex items-center gap-3 p-3 bg-surface rounded-md border border-border">
          <span
            className={`w-3 h-3 rounded-full flex-shrink-0 ${
              progressPct >= 100
                ? 'bg-success'
                : contextReady
                ? 'bg-accent-signal animate-pulse'
                : 'bg-warning animate-pulse'
            }`}
          />
          <span className="font-tertiary text-small text-content-secondary">
            {stageMessage || (contextReady
              ? 'Context harvester complete (NewsAPI, Crunchbase, World Bank)'
              : 'Harvesting real-world context data...')}
          </span>
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex justify-between text-micro font-tertiary text-content-secondary mb-1">
            <span>Swarm Execution</span>
            <span>{progressPct}%</span>
          </div>
          <div className="w-full h-2 bg-surface-raised rounded-full overflow-hidden border border-border-subtle">
            <div
              className="h-full bg-accent-signal transition-all duration-300 ease-out"
              style={{ width: `${progressPct}%` }}
            />
          </div>
        </div>
      </header>

      {status === SESSION_STATUS.FAILED && error && (
        <div role="alert" className="mb-6 p-4 rounded-md border border-error bg-surface text-error font-body text-small">
          {error}
        </div>
      )}

      <AgentGrid agents={agents} />
    </motion.main>
  )
}
