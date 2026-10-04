import { useId, useState } from 'react'
import { LineageTag } from './LineageTag.jsx'
import './BRDViewer.css'

function renderFormattedContent(text) {
  if (!text) return ''
  const regex = /\[SOURCE:\s*([^\]]+)\]/g
  const parts = []
  let lastIndex = 0
  let match

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index))
    }
    const sourceName = match[1].trim()
    const sourceLower = sourceName.toLowerCase()

    let icon = '📌'
    let typeClass = 'default'

    if (sourceLower.includes('geopolitic')) {
      icon = '🏛️'
      typeClass = 'geo'
    } else if (sourceLower.includes('religion') || sourceLower.includes('cultur')) {
      icon = '🕉️'
      typeClass = 'religion'
    } else if (sourceLower.includes('alphavantage') || sourceLower.includes('sentiment')) {
      icon = '📈'
      typeClass = 'sentiment'
    } else if (sourceLower.includes('forex') || sourceLower.includes('currenc')) {
      icon = '💱'
      typeClass = 'forex'
    } else if (sourceLower.includes('news')) {
      icon = '📰'
      typeClass = 'news'
    } else if (sourceLower.includes('worldbank')) {
      icon = '🌐'
      typeClass = 'worldbank'
    } else if (sourceLower.includes('govt')) {
      icon = '⚖️'
      typeClass = 'govt'
    } else if (sourceLower.includes('crunchbase')) {
      icon = '💼'
      typeClass = 'crunchbase'
    } else if (sourceLower.includes('prism') || sourceLower.includes('synthesis')) {
      icon = '🤖'
      typeClass = 'prism'
    }

    parts.push(
      <span key={match.index} className={`source-chip source-chip--${typeClass}`} title={`Verified source: ${sourceName}`}>
        <span className="source-chip__icon" aria-hidden="true">{icon}</span>
        <span className="source-chip__text">{sourceName}</span>
      </span>
    )
    lastIndex = regex.lastIndex
  }

  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex))
  }

  return parts
}

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
        <p className="brd-section__content">{renderFormattedContent(content)}</p>
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
