import { motion } from 'framer-motion'
import { getAgentCardVariants } from '../../animations/variants.js'
import './AgentGrid.css'

import agentVcImg from '../../assets/landing/agents/agent_vc.jpg'
import agentLeanImg from '../../assets/landing/agents/agent_lean.jpg'
import agentCtoImg from '../../assets/landing/agents/agent_cto.jpg'
import agentUxImg from '../../assets/landing/agents/agent_ux.jpg'
import agentRegulatorImg from '../../assets/landing/agents/agent_regulator.jpg'
import agentAdversarialImg from '../../assets/landing/agents/agent_adversarial.jpg'

const PERSONA_CONFIG = Object.freeze({
  vc: {
    avatar: agentVcImg,
    badge: '10x Return & Moats',
    mandate: 'Unit economics, venture scale & defensible moat.',
    statusThoughts: {
      pending: 'Standing by to evaluate TAM and enterprise scalability...',
      running: 'Simulating unit economics, TAM expansion & defensibility...',
      complete: '10x market viability & venture critique synthesized.',
      failed: 'Analysis interrupted. Ready for re-evaluation.',
    },
    colorVar: 'var(--color-agent-vc)',
  },
  lean: {
    avatar: agentLeanImg,
    badge: '4-Week MVP Validation',
    mandate: 'Scope discipline, rapid PMF cycles & cheap validation.',
    statusThoughts: {
      pending: 'Standing by to challenge feature bloat and validate PMF...',
      running: 'Pruning non-core scope. Stress-testing 30-day proof of value...',
      complete: 'Lean MVP scope & customer validation criteria finalized.',
      failed: 'Validation sequence paused. Ready to re-run.',
    },
    colorVar: 'var(--color-agent-lean)',
  },
  cto: {
    avatar: agentCtoImg,
    badge: 'Tech Feasibility & Stack',
    mandate: 'Architecture, DB bottlenecks, API latency & tech debt.',
    statusThoughts: {
      pending: 'Standing by to benchmark architectural scale limits...',
      running: 'Auditing microservices, latency bottlenecks & DB tier...',
      complete: 'Technical feasibility & infrastructure blueprint verified.',
      failed: 'Architecture audit paused. Ready to re-run.',
    },
    colorVar: 'var(--color-agent-cto)',
  },
  ux: {
    avatar: agentUxImg,
    badge: 'Friction & Delight',
    mandate: 'Cognitive load, zero-friction onboarding & customer retention.',
    statusThoughts: {
      pending: 'Standing by to audit end-to-end user journeys...',
      running: 'Evaluating customer cognitive friction & time-to-value...',
      complete: 'User journey maps & cognitive ergonomics synthesized.',
      failed: 'UX audit interrupted. Ready to re-run.',
    },
    colorVar: 'var(--color-agent-ux)',
  },
  regulator: {
    avatar: agentRegulatorImg,
    badge: 'Compliance & Legal Shield',
    mandate: 'SOC2, GDPR/DPDP privacy boundaries & legal risk.',
    statusThoughts: {
      pending: 'Standing by to review data governance and legal exposure...',
      running: 'Scanning GDPR/SOC2 compliance, PII flows & liabilities...',
      complete: 'Compliance guardrails & legal risk shield verified.',
      failed: 'Compliance check paused. Ready to re-run.',
    },
    colorVar: 'var(--color-agent-regulator)',
  },
  adversarial: {
    avatar: agentAdversarialImg,
    badge: 'Stress-Testing & Flaws',
    mandate: 'Exposing hidden catastrophic failure modes & fatal assumptions.',
    statusThoughts: {
      pending: 'Standing by to attack product assumptions and unit flaws...',
      running: 'Ruthlessly hunting fatal assumptions & customer churn traps...',
      complete: 'Vulnerability matrix & counter-measures documented.',
      failed: 'Stress-test interrupted. Ready to re-run.',
    },
    colorVar: 'var(--color-agent-adversarial)',
  },
})

const STATUS_LABELS = Object.freeze({
  pending: 'Waiting',
  running: 'Deliberating...',
  complete: 'Complete',
  failed: 'Failed',
})

export function AgentCard({ name, title, status, onRetry }) {
  const safeStatus = Object.hasOwn(STATUS_LABELS, status) ? status : 'pending'
  const persona = PERSONA_CONFIG[name] || {
    avatar: agentVcImg,
    badge: 'Specialist Agent',
    mandate: 'Domain analysis & synthesis.',
    statusThoughts: {
      pending: 'Awaiting intake signals...',
      running: 'Analyzing requirements...',
      complete: 'Critique completed.',
      failed: 'Failed.',
    },
    colorVar: 'var(--color-agent-vc)',
  }

  const currentThought = persona.statusThoughts[safeStatus] || persona.statusThoughts.pending

  return (
    <motion.article
      className="agent-card"
      data-agent={name}
      data-status={safeStatus}
      variants={getAgentCardVariants()}
      initial={false}
      animate={safeStatus}
    >
      {/* Top Profile Row: Avatar + Title + Status Chip */}
      <div className="agent-card__header">
        <div className="agent-card__avatar-frame" style={{ borderColor: persona.colorVar }}>
          <img
            src={persona.avatar}
            alt={`${title} Persona Avatar`}
            className="agent-card__avatar-img"
            loading="lazy"
          />
          {/* Avatar status badge */}
          {safeStatus === 'running' && (
            <span className="agent-card__avatar-beacon" aria-hidden="true">
              <span className="agent-card__beacon-ring" />
              <span className="agent-card__beacon-dot" />
            </span>
          )}
          {safeStatus === 'complete' && (
            <span className="agent-card__avatar-check" aria-label="Completed">
              ✓
            </span>
          )}
        </div>

        <div className="agent-card__identity">
          <div className="agent-card__title-row">
            <h3 className="agent-card__title">{title}</h3>
            <span className="agent-card__chip" data-status={safeStatus}>
              <span className="agent-card__chip-dot" aria-hidden="true" />
              {STATUS_LABELS[safeStatus]}
            </span>
          </div>
          <span className="agent-card__badge" style={{ borderColor: persona.colorVar }}>
            {persona.badge}
          </span>
        </div>
      </div>

      {/* Live Deliberation Thought Bubble */}
      <div className="agent-card__thought-box" data-status={safeStatus}>
        <div className="agent-card__thought-content">
          {safeStatus === 'pending' && (
            <p className="agent-card__thought-text agent-card__thought-text--pending">
              <span className="agent-card__thought-icon">✦</span>
              {currentThought}
            </p>
          )}

          {safeStatus === 'running' && (
            <div className="agent-card__thought-running">
              <p className="agent-card__thought-text agent-card__thought-text--running">
                <span className="agent-card__thought-spinner">⚙</span>
                {currentThought}
              </p>
              <div className="agent-card__pulse-bar">
                <motion.div
                  className="agent-card__pulse-bar-fill"
                  animate={{ x: ['-100%', '100%'] }}
                  transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
                />
              </div>
            </div>
          )}

          {safeStatus === 'complete' && (
            <p className="agent-card__thought-text agent-card__thought-text--complete">
              <span className="agent-card__thought-icon">✓</span>
              {currentThought}
            </p>
          )}

          {safeStatus === 'failed' && (
            <p className="agent-card__thought-text agent-card__thought-text--failed">
              <span className="agent-card__thought-icon">⚠</span>
              {currentThought}
            </p>
          )}
        </div>
      </div>

      {/* Mandate & Retry Footer */}
      <div className="agent-card__footer">
        <span className="agent-card__mandate-label">Focus</span>
        <span className="agent-card__mandate-text">{persona.mandate}</span>
      </div>

      {safeStatus === 'failed' && onRetry && (
        <button
          type="button"
          onClick={() => onRetry(name)}
          className="agent-card__retry-btn"
          aria-label={`Retry ${title}`}
        >
          Retry Deliberation
        </button>
      )}
    </motion.article>
  )
}
export default AgentCard
