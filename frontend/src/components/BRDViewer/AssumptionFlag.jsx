import { useId, useState } from 'react'
import './BRDViewer.css'

export function AssumptionFlag({ text, confidenceLevel, evidence, recommendedAction }) {
  const [isOpen, setIsOpen] = useState(false)
  const panelId = useId()

  return (
    <div className="assumption-flag">
      <button
        type="button"
        className="assumption-flag__header"
        aria-expanded={isOpen}
        aria-controls={panelId}
        onClick={() => setIsOpen((open) => !open)}
      >
        <span className="assumption-flag__title">{text}</span>
        <span className="assumption-flag__level">{confidenceLevel}</span>
        <span className="brd-section__chevron" aria-hidden="true" data-open={isOpen} />
      </button>
      <dl id={panelId} className="assumption-flag__details" hidden={!isOpen}>
        <dt>Evidence</dt>
        <dd>{evidence}</dd>
        <dt>Recommended action</dt>
        <dd>{recommendedAction}</dd>
      </dl>
    </div>
  )
}
