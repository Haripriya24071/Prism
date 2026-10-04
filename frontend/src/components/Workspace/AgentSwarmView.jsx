import './Workspace.css'

import agentVcImg from '../../assets/landing/agents/agent_vc.jpg'
import agentLeanImg from '../../assets/landing/agents/agent_lean.jpg'
import agentCtoImg from '../../assets/landing/agents/agent_cto.jpg'
import agentUxImg from '../../assets/landing/agents/agent_ux.jpg'
import agentRegulatorImg from '../../assets/landing/agents/agent_regulator.jpg'
import agentAdversarialImg from '../../assets/landing/agents/agent_adversarial.jpg'

const AGENT_PERSONAS = [
  {
    id: 'vc',
    name: 'The VC',
    role: 'Venture Capitalist & Market Strategist',
    badge: '10x Return & Moats',
    avatar: agentVcImg,
    color: '#6D28D9',
    tagline: 'Ruthlessly hunts for defensible market moats, pricing power, and scalable venture economics.',
    mandate: 'Unit economics, venture scale & defensible moat.',
  },
  {
    id: 'lean',
    name: 'Lean Founder',
    role: 'Startup Operator & Growth Architect',
    badge: '4-Week MVP Validation',
    avatar: agentLeanImg,
    color: '#059669',
    tagline: 'Cuts scope bloat. Advocates rapid 30-day proof of value before burning venture capital.',
    mandate: 'Scope discipline, rapid PMF cycles & cheap validation.',
  },
  {
    id: 'cto',
    name: 'Enterprise CTO',
    role: 'Chief Technology Officer & Architect',
    badge: 'Tech Feasibility & Stack',
    avatar: agentCtoImg,
    color: '#0284C7',
    tagline: 'Enforces container isolation, zero-trust RBAC, low latency boundaries, and 99.9% SLAs.',
    mandate: 'Architecture, DB bottlenecks, API latency & tech debt.',
  },
  {
    id: 'ux',
    name: 'UX Researcher',
    role: 'Principal Product Designer & Ergonomics',
    badge: 'Friction & Delight',
    avatar: agentUxImg,
    color: '#D97706',
    tagline: 'Fights cognitive overload and onboarding drop-offs with progressive disclosure and instant value.',
    mandate: 'Cognitive load, zero-friction onboarding & customer retention.',
  },
  {
    id: 'regulator',
    name: 'The Regulator',
    role: 'Statutory & Compliance Officer',
    badge: 'Compliance & Legal Shield',
    avatar: agentRegulatorImg,
    color: '#DC2626',
    tagline: 'Guards against legal liabilities, privacy regulations, PII leaks, and SOC2 audit traps.',
    mandate: 'SOC2, GDPR/DPDP privacy boundaries & legal risk.',
  },
  {
    id: 'adversarial',
    name: 'The Adversary',
    role: 'Red Team & Stress-Testing Lead',
    badge: 'Stress-Testing & Flaws',
    avatar: agentAdversarialImg,
    color: '#475569',
    tagline: 'Simulates competitor feature cloning, customer churn traps, and catastrophic edge failures.',
    mandate: 'Exposing hidden catastrophic failure modes & fatal assumptions.',
  },
]

export default function AgentSwarmView({
  agentOutputs = [],
  brdData,
  onSelectAgent,
}) {
  const rawBrd = brdData?.brd ?? brdData
  const sections = Array.isArray(rawBrd?.sections) ? rawBrd.sections : []

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="workspace-card p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs px-2 py-0.5 rounded bg-surface-raised border border-border-subtle text-content-secondary">
              Autonomous Boardroom Swarm
            </span>
            <span className="font-mono text-xs text-content-muted">
              6 Specialized Agents
            </span>
          </div>
          <h2 className="font-display font-bold text-xl text-content-primary mt-1">
            Meet the 6 Deliberating Personas
          </h2>
          <p className="font-body text-xs text-content-secondary max-w-2xl mt-1">
            Click any agent to inspect their full autonomous position, internal debate excerpts, and empirical grounding citations.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono text-content-secondary">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>All 6 Personas Completed Consensus</span>
        </div>
      </div>

      {/* Simplified, Clean, Artistic 6-Agent Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {AGENT_PERSONAS.map((agent) => {
          const rawOutput = (agentOutputs || []).find((ao) => ao.agent === agent.id)
          const winningSections = sections
            .filter((s) => (s.lineage?.sourceAgent || '').toLowerCase().includes(agent.id))
            .map((s) => s.title)

          const fullAgentData = {
            ...agent,
            confidence: '92%',
            recommendation: rawOutput?.brd_json?.executive_summary || agent.tagline,
            keyConcern: rawOutput?.brd_json?.failure_modes?.[0]?.description || 'Unvalidated unit margins under aggressive bidding competition.',
            isWinnerIn: winningSections,
            sections: rawOutput?.brd_json || {},
            citations: ['World Bank National GDP Data', 'NewsAPI Developer Sentiment', 'Statutory Compliance Database'],
          }

          return (
            <div
              key={agent.id}
              onClick={() => onSelectAgent(fullAgentData)}
              className="agent-simple-card"
            >
              <div>
                {/* Avatar & Title Row */}
                <div className="flex items-center gap-3 pb-3 border-b border-border-subtle">
                  <img
                    src={agent.avatar}
                    alt={agent.name}
                    className="agent-avatar-frame shrink-0"
                    style={{ borderColor: agent.color }}
                  />
                  <div className="min-w-0">
                    <h3 className="font-display font-bold text-base text-content-primary truncate">
                      {agent.name}
                    </h3>
                    <p className="font-body text-xs text-content-secondary truncate">
                      {agent.role}
                    </p>
                    <span
                      className="inline-block mt-1 font-mono text-[10px] font-semibold px-2 py-0.5 rounded border border-border-subtle"
                      style={{ backgroundColor: `${agent.color}15`, color: agent.color }}
                    >
                      {agent.badge}
                    </span>
                  </div>
                </div>

                {/* Persona Attitude / Tagline */}
                <p className="font-body text-xs text-content-secondary leading-relaxed mt-3">
                  {agent.tagline}
                </p>
              </div>

              {/* Bottom Inspect Action */}
              <div className="pt-3 mt-4 border-t border-border-subtle flex items-center justify-between text-xs">
                <span className="font-mono text-[11px] text-content-muted">
                  {winningSections.length > 0 ? `Won ${winningSections.length} BRD section` : 'Deliberation complete'}
                </span>
                <span className="font-display font-semibold text-accent-signal flex items-center gap-1">
                  Inspect Reasoning →
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
