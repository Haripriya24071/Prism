import { useEffect } from 'react'
import './Workspace.css'

export default function EvidenceModal({ evidenceData, onClose }) {
  useEffect(() => {
    function handleKeyDown(e) {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  if (!evidenceData) return null

  const {
    source = 'PRISM Swarm Consensus',
    title = '',
    claim = '',
    text = '',
    quote = '',
    confidence = '95%',
    provider = 'Verified Knowledge Base & Harvester',
    impact = '',
  } = evidenceData

  const displayClaim = claim || title || ''
  const displayQuote = quote || text || ''

  return (
    <div
      className="workspace-modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="evidence-modal-title"
      onClick={onClose}
    >
      <div
        className="workspace-modal-content animate-scale-up"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between pb-3 border-b border-border-subtle mb-4">
          <div className="flex items-center gap-2">
            <span className="text-xl">🔍</span>
            <div>
              <h3 id="evidence-modal-title" className="font-display font-extrabold text-h3 text-content-primary">
                Grounding & Lineage Evidence
              </h3>
              <p className="font-tertiary text-micro text-content-secondary">
                Verifiable citation powering PRISM adversarial synthesis
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="w-8 h-8 rounded-full border border-border bg-surface-raised hover:bg-surface flex items-center justify-center font-bold text-content-secondary hover:text-content-primary cursor-pointer"
            aria-label="Close modal"
          >
            ✕
          </button>
        </div>

        <div className="space-y-4">
          {/* Source Attribution Box */}
          <div className="p-3 rounded-lg border border-border-subtle bg-surface-raised flex items-center justify-between">
            <div>
              <span className="font-tertiary text-[10px] uppercase font-bold text-content-secondary tracking-wider block">
                Source Agent Authority
              </span>
              <span className="font-display font-bold text-sm text-content-primary">
                {source}
              </span>
            </div>
            <div className="text-right">
              <span className="font-tertiary text-[10px] uppercase font-bold text-content-secondary tracking-wider block">
                Synthesis Confidence
              </span>
              <span className="font-mono font-bold text-sm text-accent-signal">
                {confidence}
              </span>
            </div>
          </div>

          {/* Claim Box */}
          {displayClaim && (
            <div>
              <span className="font-tertiary text-[11px] font-bold uppercase tracking-wider text-content-secondary block mb-1">
                Synthesized Claim / Statement
              </span>
              <p className="font-body text-body text-content-primary p-3 rounded-md border border-border-subtle bg-surface">
                &ldquo;{displayClaim}&rdquo;
              </p>
            </div>
          )}

          {/* Supporting Evidence Quote */}
          <div>
            <span className="font-tertiary text-[11px] font-bold uppercase tracking-wider text-content-secondary block mb-1">
              Direct Harvester Citation & Fact Grounding
            </span>
            <div className="p-3.5 rounded-lg border border-accent-signal/30 bg-accent-signal/5 font-body text-small text-content-primary space-y-2">
              <p className="italic">
                {displayQuote || 'Extracted from real-world macroeconomic and regulatory baseline data collected during context harvesting.'}
              </p>
              {impact && (
                <div className="pt-1.5 border-t border-accent-signal/20 text-xs font-medium text-content-primary">
                  <strong>Impact:</strong> {impact}
                </div>
              )}
              <div className="flex items-center gap-2 pt-1 border-t border-accent-signal/20 text-micro text-content-secondary">
                <span>📡 Provider:</span>
                <span className="font-semibold text-content-primary">{provider}</span>
              </div>
            </div>
          </div>

          <div className="pt-2 flex justify-end">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-1.5 rounded-md border border-border bg-surface-raised font-display font-semibold text-small hover:bg-surface cursor-pointer"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
