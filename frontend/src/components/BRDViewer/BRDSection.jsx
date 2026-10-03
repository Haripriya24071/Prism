import { useId, useState } from 'react'
import { LineageTag } from './LineageTag.jsx'
import './BRDViewer.css'

export function BRDSection({ title, content, lineage, dissentingAgents = [] }) {
  const [isOpen, setIsOpen] = useState(false)
  const [isDissentOpen, setIsDissentOpen] = useState(false)
  const baseId = useId()
  const panelId = `${baseId}-panel`
  const dissentId = `${baseId}-dissent`
  const dissentCount = dissentingAgents.length

  return (
    <article className="brd-section">
      <h3 className="brd-section__heading">
        <button
          type="button"
          className="brd-section__header"
          aria-expanded={isOpen}
          aria-controls={panelId}
          onClick={() => setIsOpen((open) => !open)}
        >
          <span className="brd-section__title">{title}</span>
          <LineageTag lineage={lineage} />
          <span className="brd-section__chevron" aria-hidden="true" data-open={isOpen} />
        </button>
      </h3>

      <div id={panelId} className="brd-section__panel" hidden={!isOpen}>
        <p className="brd-section__content">{content}</p>
        <LineageTag lineage={lineage} detailed />

        {dissentCount > 0 && (
          <div className="dissent">
            <button
              type="button"
              className="dissent__toggle"
              aria-expanded={isDissentOpen}
              aria-controls={dissentId}
              onClick={() => setIsDissentOpen((open) => !open)}
            >
              {dissentCount} {dissentCount === 1 ? 'agent' : 'agents'} disagreed
            </button>
            <ul id={dissentId} className="dissent__list" hidden={!isDissentOpen}>
              {dissentingAgents.map((entry) => (
                <li key={entry.agent} className="dissent__item" data-agent={entry.agent}>
                  <span className="dissent__agent">{entry.agent}</span>
                  <span className="dissent__note">{entry.note}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </article>
  )
}
