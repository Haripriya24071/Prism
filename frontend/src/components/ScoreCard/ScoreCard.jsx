import { ScoreRing } from './ScoreRing.jsx'
import './ScoreCard.css'

export { ScoreRing }

export default function ScoreCard({
  score,
  confidenceBand,
  gapFlags = [],
  pivotTriggered = false,
  pivots = [],
}) {
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

      <div className="score-card__pivots" data-visible={pivotTriggered}>
        <h3 className="score-card__pivots-title">Suggested pivots</h3>
        <ul className="score-card__pivot-list">
          {pivots.map((pivot) => (
            <li key={pivot.direction} className="score-card__pivot">
              <span>{pivot.direction}</span>
              <span className="score-card__pivot-score">{pivot.projectedScore}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
