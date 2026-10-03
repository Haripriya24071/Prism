import { motion } from 'framer-motion'
import { getAgentCardVariants } from '../../animations/variants.js'
import './AgentGrid.css'

const STATUS_LABELS = Object.freeze({
  pending: 'Waiting',
  running: 'Thinking...',
  complete: 'Done',
  failed: 'Failed',
})

export function AgentCard({ name, title, status }) {
  const safeStatus = Object.hasOwn(STATUS_LABELS, status) ? status : 'pending'

  return (
    <motion.article
      className="agent-card"
      data-agent={name}
      data-status={safeStatus}
      variants={getAgentCardVariants()}
      initial={false}
      animate={safeStatus}
    >
      <h3 className="agent-card__title">{title}</h3>
      <span className="agent-card__chip" data-status={safeStatus}>
        <span className="agent-card__chip-dot" aria-hidden="true" />
        {STATUS_LABELS[safeStatus]}
      </span>
    </motion.article>
  )
}
