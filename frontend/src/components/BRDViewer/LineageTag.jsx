import './BRDViewer.css'

export function LineageTag({ lineage = {}, detailed = false }) {
  const sourceAgent = lineage.sourceAgent || lineage.source_agent || 'unknown'
  const confidence = lineage.confidence ?? lineage.confidence_score ?? 'N/A'
  const dataCitation =
    lineage.dataCitation ||
    (Array.isArray(lineage.data_citations) ? lineage.data_citations.join('; ') : '') ||
    'No citation provided'

  const chip = (
    <span className="lineage-tag" data-agent={sourceAgent}>
      <span className="lineage-tag__source">Source: {sourceAgent}</span>
      <span className="lineage-tag__confidence">{confidence}</span>
    </span>
  )

  if (!detailed) {
    return chip
  }

  return (
    <div className="lineage-block">
      {chip}
      <p className="lineage-block__citation">{dataCitation}</p>
    </div>
  )
}
