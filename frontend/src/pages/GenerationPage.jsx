import { motion } from 'framer-motion'
import { getPageVariants } from '../animations/variants.js'
import AgentGrid from '../components/AgentGrid/AgentGrid.jsx'
import HandshakeLoader from '../components/ui/HandshakeLoader.jsx'
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

  const displayMessage = stageMessage || (
    contextReady
      ? 'Context intelligence active — 6 agents stress-testing your market fit...'
      : 'Harvesting real-world market, regulatory & cultural context...'
  )

  return (
    <motion.main
      className="min-h-screen bg-void p-4 sm:p-8 font-body text-content-primary max-w-5xl mx-auto"
      variants={getPageVariants()}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      <header className="mb-6 text-center sm:text-left">
        <h1 className="font-display text-h1 font-bold text-content-primary">
          Phase 2: Swarm Generation
        </h1>
        <p className="font-body text-content-secondary mt-1">
          Six competing expert personas are independently analyzing, stress-testing, and drafting your BRD.
        </p>
      </header>

      {status === SESSION_STATUS.FAILED && error && (
        <div role="alert" className="mb-6 p-4 rounded-md border border-error bg-surface text-error font-body text-small">
          {error}
        </div>
      )}

      {/* Handshake Deal Loading Animation Hero */}
      <div className="mb-6">
        <HandshakeLoader
          stageMessage={displayMessage}
          progressPct={progressPct}
          stepNumber="5"
          tagText={progressPct >= 100 ? 'SWARM COMPLETE' : 'SWIPE <<<'}
        />
      </div>

      {/* 6-Agent Live Progress Grid */}
      <section aria-labelledby="agent-grid-heading">
        <div className="flex items-center justify-between mb-4">
          <h2 id="agent-grid-heading" className="font-display text-h3 text-content-primary font-bold">
            Live Agent Deliberation
          </h2>
          <span className="font-tertiary text-xs text-content-secondary uppercase tracking-wider">
            {agents.filter((a) => a.status === 'complete').length} / 6 Complete
          </span>
        </div>
        <AgentGrid agents={agents} />
      </section>
    </motion.main>
  )
}
