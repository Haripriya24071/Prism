import { motion } from 'framer-motion'
import { ScoreRing } from './ScoreRing.jsx'
import './ScoreCard.css'

export { ScoreRing }

export default function ScoreCard(props) {
  const {
    score,
    confidenceBand,
    gapFlags = [],
  } = props

  return (
    <section className="score-card" aria-label="Investor readiness">
      <ScoreRing score={score} />
      {confidenceBand && <p className="score-card__band">{confidenceBand}</p>}

      {gapFlags.length > 0 && (
        <ul className="score-card__gaps">
          {gapFlags.map((flag) => (
            <li key={flag.criterion} className="score-card__gap">
              <span className="score-card__gap-head">
                {flag.criterion}
                <span className="score-card__gap-score">{flag.score}</span>
              </span>
              <span className="score-card__gap-action">{flag.actionItem}</span>
            </li>
          ))}
        </ul>
      )}

      {props.pivotSuggestions && props.pivotSuggestions.length > 0 && (
        <div className="score-card__pivots" aria-live="polite">
          <h3
            className="score-card__pivots-heading"
            style={{ color: 'var(--color-warning)' }}
          >
            Pivot Directions
          </h3>
          <div className="score-card__pivot-list">
            {props.pivotSuggestions.map((suggestion, index) => {
              const title = suggestion.title || suggestion.direction || `Pivot Direction ${index + 1}`
              const description = suggestion.description || suggestion.rationale || ''
              const projectedScore = suggestion.projected_score ?? suggestion.projectedScore ?? ''
              const keyChanges = suggestion.key_changes || suggestion.keyChanges || []

              return (
                <motion.div
                  key={title || index}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                  className="score-card__pivot-card"
                  style={{ backgroundColor: 'var(--color-surface-raised)' }}
                >
                  <h4 className="score-card__pivot-title font-bold">{title}</h4>
                  {description && (
                    <p className="score-card__pivot-description">{description}</p>
                  )}
                  <span
                    className="score-card__pivot-projected"
                    style={{ fontFamily: 'var(--font-mono)' }}
                  >
                    Projected Score: {projectedScore}
                  </span>
                  {keyChanges.length > 0 && (
                    <ul className="score-card__pivot-changes">
                      {keyChanges.map((change, i) => (
                        <li key={i}>{change}</li>
                      ))}
                    </ul>
                  )}
                </motion.div>
              )
            })}
          </div>
        </div>
      )}
    </section>
  )
}
