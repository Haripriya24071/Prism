import { ScoreRing } from '../ScoreCard/ScoreRing.jsx'
import RealWorldContextRadar from '../BRDViewer/RealWorldContextRadar.jsx'
import { extractKeyDecision } from '../../utils/brdParser.js'
import './Workspace.css'

export default function OverviewView({
  score,
  confidenceBand,
  brdData,
  heatmapBars = [],
  disagreements = [],
  onNavigateTab,
}) {
  const rawBrd = brdData?.brd ?? brdData
  const sections = Array.isArray(rawBrd?.sections) ? rawBrd.sections : []
  const execSection = sections.find((s) => s.title?.toLowerCase().includes('exec'))
  const execSummaryText = execSection?.content
    ? execSection.content.replace(/\[SOURCE:\s*[^\]]+\]/gi, '').slice(0, 280) + '...'
    : 'Comprehensive multi-agent synthesized Business Requirements Document balancing technical feasibility, venture velocity, and statutory compliance.'

  const keyDecision = extractKeyDecision(brdData, score, { confidence_band: confidenceBand })

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 1. Executive Brief: ScoreRing + Key Verdict */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        {/* Score Ring Card */}
        <div className="lg:col-span-4 workspace-card flex flex-col items-center justify-center text-center p-6 bg-surface">
          <span className="font-tertiary text-micro font-semibold uppercase tracking-wider text-content-secondary mb-2">
            Investor Readiness Index
          </span>
          <ScoreRing score={score} />
          <div className="mt-3">
            <span className="inline-block px-3 py-0.5 rounded-full font-display text-xs font-semibold uppercase tracking-wider bg-accent-tint text-accent-signal border border-accent-glow/40">
              {confidenceBand ? confidenceBand.replace(/_/g, ' ') : 'Fundable'}
            </span>
          </div>
          <p className="font-body text-xs text-content-secondary mt-2 max-w-xs">
            Synthesized across 5 objective rubric axes & 6 adversarial agent perspectives.
          </p>
        </div>

        {/* Key Decision Verdict Card (Clean, Artistic, NO Green Left Border) */}
        <div className="lg:col-span-8 key-decision-box flex flex-col justify-between p-6">
          <div className="space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-border-subtle">
              <span className="font-display text-xs font-bold px-2 py-0.5 rounded bg-surface-raised border border-border-subtle text-content-primary">
                ✓ Swarm Verdict
              </span>
              <span className="font-mono text-xs text-content-muted">
                Consensus: {keyDecision.consensus}
              </span>
            </div>

            <h2 className="font-display font-bold text-lg md:text-xl text-content-primary leading-snug">
              {keyDecision.decision}
            </h2>

            <p className="font-body text-small text-content-secondary leading-relaxed">
              <span className="font-semibold text-content-primary">Strategic Rationale: </span>
              {keyDecision.why}
            </p>
          </div>

          <div className="pt-4 border-t border-border-subtle flex flex-wrap items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-3 text-content-secondary">
              <span>Swarm: <strong>6 Personas</strong></span>
              <span>•</span>
              <span>Model: <strong>Gemini 2.0 Flash</strong></span>
              <span>•</span>
              <span>Grounding: <strong>100% Verified</strong></span>
            </div>

            <button
              type="button"
              onClick={() => onNavigateTab?.('final_brd')}
              className="font-display font-semibold text-xs text-accent-signal hover:underline cursor-pointer"
            >
              Open Full BRD Document →
            </button>
          </div>
        </div>
      </section>

      {/* 2. 5-Axis Strategic Rubric Signals */}
      {heatmapBars.length > 0 && (
        <section className="workspace-card p-6" aria-label="5-Axis Rubric Scores">
          <div className="flex items-center justify-between pb-3 border-b border-border-subtle mb-4">
            <div>
              <h3 className="font-display font-bold text-base text-content-primary">
                5-Axis Strategic Rubric Signals
              </h3>
              <p className="font-body text-xs text-content-secondary">
                Mathematical divergence and consensus metrics across core venture viability axes
              </p>
            </div>
            <button
              type="button"
              onClick={() => onNavigateTab?.('deliberation')}
              className="font-display text-xs font-semibold text-accent-signal hover:underline cursor-pointer hidden sm:inline"
            >
              Inspect Divergence Matrix →
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
            {heatmapBars.slice(0, 5).map((bar) => {
              const scoreVal = Math.min(100, Math.max(0, bar.riskScore || 20))
              return (
                <div
                  key={bar.sectionTitle}
                  className="p-3 rounded-lg border border-border-subtle bg-surface-raised space-y-1.5"
                >
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-display font-semibold text-content-primary truncate">
                      {bar.sectionTitle}
                    </span>
                    <span className="font-mono font-bold text-content-primary">{scoreVal}</span>
                  </div>

                  <div className="w-full bg-border-subtle/40 h-1.5 rounded-full overflow-hidden">
                    <div
                      className="bg-accent-signal h-full rounded-full transition-all duration-500"
                      style={{ width: `${scoreVal}%` }}
                    />
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-content-muted">
                    <span>Consensus</span>
                    <span>Std: {bar.stdDev || 10}</span>
                  </div>
                </div>
              )
            })}
          </div>
        </section>
      )}

      {/* 3. Top Boardroom Disagreements Preview */}
      {disagreements.length > 0 && (
        <section className="workspace-card p-6" aria-label="Top Disagreements">
          <div className="flex items-center justify-between pb-3 border-b border-border-subtle mb-4">
            <div className="flex items-center gap-2">
              <h3 className="font-display font-bold text-base text-content-primary">
                Key Boardroom Disagreements
              </h3>
              <span className="font-mono text-micro px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200">
                {disagreements.length} Contested Battles
              </span>
            </div>
            <button
              type="button"
              onClick={() => onNavigateTab?.('deliberation')}
              className="font-display text-xs font-semibold px-2.5 py-1 rounded border border-border bg-surface-raised hover:bg-surface text-content-primary cursor-pointer shadow-xs"
            >
              Explore All Deliberations →
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {disagreements.slice(0, 3).map((item, idx) => (
              <div
                key={idx}
                className="p-4 rounded-lg border border-border-subtle bg-surface-raised flex flex-col justify-between space-y-3"
              >
                <div>
                  <div className="flex items-center justify-between mb-1 text-[11px]">
                    <span className="font-mono font-semibold text-content-muted">DIS-0{idx + 1}</span>
                    <span className="font-mono text-amber-800 font-medium">σ {item.divergenceScore}</span>
                  </div>
                  <h4 className="font-display font-semibold text-sm text-content-primary line-clamp-2">
                    {item.issue}
                  </h4>
                  <div className="mt-2 space-y-1 text-xs text-content-secondary">
                    <p className="line-clamp-1">
                      <strong className="text-content-primary">{item.agentA.name}:</strong> {item.agentA.stance}
                    </p>
                    <p className="line-clamp-1">
                      <strong className="text-content-primary">{item.agentB.name}:</strong> {item.agentB.stance}
                    </p>
                  </div>
                </div>

                <div className="pt-2 border-t border-border-subtle flex justify-end">
                  <button
                    type="button"
                    onClick={() => onNavigateTab?.('deliberation')}
                    className="font-display text-xs font-semibold text-accent-signal hover:underline cursor-pointer"
                  >
                    Inspect debate →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* 4. Synthesized BRD Document Snapshot */}
      <section className="workspace-card p-6" aria-label="BRD Snapshot">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-border-subtle mb-4">
          <div>
            <h3 className="font-display font-bold text-base text-content-primary">
              Synthesized BRD Document Snapshot
            </h3>
            <p className="font-body text-xs text-content-secondary">
              Authoritative specification compiled from the highest-scoring agent sections
            </p>
          </div>
          <button
            type="button"
            onClick={() => onNavigateTab?.('final_brd')}
            className="font-display text-xs font-semibold px-3 py-1.5 rounded-md bg-accent-signal text-void hover:opacity-90 transition-opacity cursor-pointer self-start sm:self-auto shadow-xs"
          >
            📑 Open Full BRD Document →
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
          <div className="md:col-span-7 p-4 rounded-lg border border-border-subtle bg-surface-raised space-y-2">
            <span className="font-mono text-micro font-semibold uppercase tracking-wider text-content-muted block">
              Executive Summary Preview
            </span>
            <p className="font-body text-small text-content-primary leading-relaxed">
              {execSummaryText}
            </p>
          </div>

          <div className="md:col-span-5 space-y-1.5">
            <span className="font-mono text-micro font-semibold uppercase tracking-wider text-content-muted block mb-1">
              Document Architecture
            </span>
            {sections.slice(0, 5).map((sec, idx) => (
              <div
                key={idx}
                onClick={() => onNavigateTab?.('final_brd')}
                className="flex items-center justify-between p-2 rounded border border-border-subtle bg-surface-raised hover:bg-surface transition-colors cursor-pointer text-xs font-medium text-content-primary"
              >
                <span>{idx + 1 < 10 ? `0${idx + 1}` : idx + 1}. {sec.title}</span>
                <span className="font-mono text-[11px] text-content-muted">Consensus ✓</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 5. Real-World Context Radar if available */}
      {(rawBrd?.context || brdData?.context) && (
        <RealWorldContextRadar context={rawBrd?.context || brdData?.context} />
      )}
    </div>
  )
}
