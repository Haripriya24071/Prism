import { useEffect } from 'react'
import './Workspace.css'

export default function AgentDetailModal({ agentData, onClose, onOpenEvidence }) {
  useEffect(() => {
    function handleKeyDown(e) {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  if (!agentData) return null

  const {
    name = 'The VC',
    role = 'Venture Capitalist',
    badge = '10x Return & Moats',
    avatar = '',
    color = '#6D28D9',
    confidence = '88%',
    mandate = 'Unit economics, venture scale & defensible moat.',
    recommendation = '',
    keyConcern = '',
    sections = {},
    citations = [],
    isWinnerIn = [],
  } = agentData

  return (
    <div
      className="workspace-modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="agent-modal-title"
      onClick={onClose}
    >
      <div
        className="workspace-drawer animate-slide-left"
        style={{ borderLeftColor: color }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between pb-4 border-b border-border-subtle mb-4">
          <div className="flex items-center gap-3">
            {avatar && (
              <img
                src={avatar}
                alt={name}
                className="w-14 h-14 rounded-full border-2 object-cover shadow-xs"
                style={{ borderColor: color }}
              />
            )}
            <div>
              <div className="flex items-center gap-2">
                <h3 id="agent-modal-title" className="font-display font-extrabold text-h2 text-content-primary">
                  {name}
                </h3>
              </div>
              <p className="font-tertiary text-micro text-content-secondary font-medium mb-1">
                {role}
              </p>
              <span
                className="inline-block px-2 py-0.5 rounded text-[11px] font-bold font-tertiary uppercase tracking-wider text-void"
                style={{ backgroundColor: color }}
              >
                {badge}
              </span>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="w-8 h-8 rounded-full border border-border bg-surface-raised hover:bg-surface flex items-center justify-center font-bold text-content-secondary hover:text-content-primary cursor-pointer"
            aria-label="Close drawer"
          >
            ✕
          </button>
        </div>

        <div className="space-y-5 text-content-primary">
          {/* Persona Mandate */}
          <div className="p-3.5 rounded-lg border border-border-subtle bg-surface-raised space-y-1">
            <span className="font-tertiary text-[10px] uppercase font-bold text-content-secondary tracking-wider block">
              Analytical Mandate & Lens
            </span>
            <p className="font-body text-small text-content-primary">
              {mandate}
            </p>
            <div className="pt-2 flex items-center justify-between text-micro text-content-secondary border-t border-border-subtle">
              <span>Persona Assessment Score:</span>
              <span className="font-mono font-bold text-sm text-content-primary">{confidence}</span>
            </div>
          </div>

          {/* Primary Position / Recommendation */}
          <div>
            <span className="font-tertiary text-[11px] font-bold uppercase tracking-wider text-content-secondary block mb-1">
              Core Strategic Recommendation
            </span>
            <div className="p-3 rounded-md border border-border-subtle bg-surface font-body text-body font-medium">
              &ldquo;{recommendation || 'Focus ruthlessly on market defensibility and scalable unit margins.'}&rdquo;
            </div>
          </div>

          {/* Key Concern */}
          <div>
            <span className="font-tertiary text-[11px] font-bold uppercase tracking-wider text-error block mb-1">
              Top Lethal Vulnerability Flagged
            </span>
            <div className="p-3 rounded-md border border-error/30 bg-error/5 font-body text-small text-content-primary">
              ⚠️ {keyConcern || 'Unvalidated acquisition assumptions under competitive bidding.'}
            </div>
          </div>

          {/* Winning Sections Badge */}
          {isWinnerIn.length > 0 && (
            <div>
              <span className="font-tertiary text-[11px] font-bold uppercase tracking-wider text-success block mb-1.5">
                Won Consensus In Merged BRD
              </span>
              <div className="flex flex-wrap gap-1.5">
                {isWinnerIn.map((secTitle) => (
                  <span
                    key={secTitle}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-success/10 border border-success/30 font-tertiary text-micro font-bold text-success"
                  >
                    🏆 {secTitle}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Agent Authored Sections */}
          {Object.keys(sections).length > 0 && (
            <div>
              <span className="font-tertiary text-[11px] font-bold uppercase tracking-wider text-content-secondary block mb-2">
                Deliberation Draft Excerpts
              </span>
              <div className="space-y-3">
                {Object.entries(sections).map(([sTitle, sContent]) => (
                  <div key={sTitle} className="p-3 rounded-lg border border-border-subtle bg-surface space-y-1">
                    <h4 className="font-display font-bold text-xs text-content-primary">
                      {sTitle}
                    </h4>
                    <p className="font-body text-small text-content-secondary line-clamp-4">
                      {typeof sContent === 'string' ? sContent : JSON.stringify(sContent)}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Evidence Citations */}
          {citations.length > 0 && (
            <div>
              <span className="font-tertiary text-[11px] font-bold uppercase tracking-wider text-content-secondary block mb-2">
                Grounding Citations Utilized
              </span>
              <div className="space-y-1.5">
                {citations.map((cite, i) => (
                  <div
                    key={i}
                    onClick={() => onOpenEvidence && onOpenEvidence({ source: name, quote: cite, claim: `Referenced in ${name} analysis` })}
                    className="p-2 rounded border border-border-subtle bg-surface-raised font-mono text-micro text-content-secondary flex items-center justify-between cursor-pointer hover:border-border"
                  >
                    <span>{cite}</span>
                    <span className="text-accent-signal font-bold">Inspect →</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="pt-4 border-t border-border-subtle flex justify-end">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-1.5 rounded-md border border-border bg-surface-raised font-display font-semibold text-small hover:bg-surface cursor-pointer"
            >
              Close Inspector
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
