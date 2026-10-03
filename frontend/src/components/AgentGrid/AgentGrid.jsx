import { AgentCard } from './AgentCard.jsx'
import './AgentGrid.css'

export default function AgentGrid({ agents, onRetry }) {
  return (
    <section className="agent-grid" aria-live="polite" aria-label="Agent progress">
      {agents.map((agent) => (
        <AgentCard
          key={agent.name}
          name={agent.name}
          title={agent.title}
          status={agent.status}
          onRetry={agent.onRetry || onRetry}
        />
      ))}
    </section>
  )
}
