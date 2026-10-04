import { useState } from 'react'
import DivergenceHeatmap from '../DivergenceHeatmap/DivergenceHeatmap.jsx'
import './Workspace.css'

export default function DeliberationView({
  heatmapBars = [],
  disagreements = [],
  onOpenAgent,
  onOpenEvidence,
}) {
  const [filterSeverity, setFilterSeverity] = useState('all')

  const filteredDisagreements = disagreements.filter((item) => {
    if (filterSeverity === 'all') return true
    if (filterSeverity === 'high') return item.divergenceScore >= 28
    if (filterSeverity === 'contested') return item.divergenceScore >= 18 && item.divergenceScore < 28
    return item.divergenceScore < 18
  })

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="workspace-card p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs px-2 py-0.5 rounded bg-surface-raised border border-border-subtle text-content-secondary">
              Swarm Dialectics & Divergence
            </span>
            <span className="font-mono text-xs text-content-muted">
              Adversarial Synthesis
            </span>
          </div>
          <h2 className="font-display font-bold text-xl text-content-primary mt-1">
            Where the Agents Disagreed
          </h2>
          <p className="font-body text-xs text-content-secondary max-w-2xl mt-1">
            PRISM rejects simple majority voting. Agents debate polarized tradeoffs, stress-test friction points, and PRISM synthesizes the resilient conclusion.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="font-mono text-xs px-2.5 py-1 rounded bg-surface-raised border border-border text-content-secondary">
            {disagreements.length} Contested Topics
          </span>
        </div>
      </div>

      {/* Interactive Divergence Heatmap */}
      <div className="workspace-card p-6">
        <div className="flex items-center justify-between pb-3 border-b border-border-subtle mb-4">
          <div>
            <h3 className="font-display font-bold text-base text-content-primary">
              Rubric Divergence Matrix
            </h3>
            <p className="font-body text-xs text-content-secondary">
              Measured standard deviation across 5 core evaluation axes. Click any bar to inspect opposing agent arguments.
            </p>
          </div>
          <span className="font-mono text-micro px-2 py-0.5 rounded bg-surface-raised border border-border-subtle text-content-secondary">
            Mathematical Spread σ
          </span>
        </div>

        {heatmapBars.length > 0 ? (
          <DivergenceHeatmap bars={heatmapBars} />
        ) : (
          <p className="font-body text-xs text-content-secondary py-4">
            No divergence metrics available.
          </p>
        )}
      </div>

      {/* Structured Battlegrounds (Clean Comic Dialectic Cards, NO Vibe-coded Stripe Borders) */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="font-display font-bold text-lg text-content-primary">
              Structured Battleground Decisions
            </h3>
            <p className="font-body text-xs text-content-secondary">
              Side-by-side comparison: Agent A position vs Agent B position → Final PRISM resolution.
            </p>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center gap-1 bg-surface-raised p-1 rounded-lg border border-border-subtle self-start sm:self-auto text-xs">
            <button
              type="button"
              onClick={() => setFilterSeverity('all')}
              className={`px-2.5 py-1 rounded font-medium transition-colors cursor-pointer ${
                filterSeverity === 'all'
                  ? 'bg-surface text-content-primary shadow-xs border border-border'
                  : 'text-content-secondary hover:text-content-primary'
              }`}
            >
              All ({disagreements.length})
            </button>
            <button
              type="button"
              onClick={() => setFilterSeverity('high')}
              className={`px-2.5 py-1 rounded font-medium transition-colors cursor-pointer ${
                filterSeverity === 'high'
                  ? 'bg-surface text-content-primary shadow-xs border border-border'
                  : 'text-content-secondary hover:text-content-primary'
              }`}
            >
              High Divergence (σ ≥ 28)
            </button>
            <button
              type="button"
              onClick={() => setFilterSeverity('contested')}
              className={`px-2.5 py-1 rounded font-medium transition-colors cursor-pointer ${
                filterSeverity === 'contested'
                  ? 'bg-surface text-content-primary shadow-xs border border-border'
                  : 'text-content-secondary hover:text-content-primary'
              }`}
            >
              Contested (σ 18–27)
            </button>
          </div>
        </div>

        {/* Dialectic Cards */}
        <div className="space-y-4">
          {filteredDisagreements.map((item, idx) => {
            const isHigh = item.divergenceScore >= 28

            return (
              <div
                key={item.id || idx}
                className="workspace-card p-6 space-y-4"
              >
                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2 pb-3 border-b border-border-subtle">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-mono text-micro font-semibold text-content-muted">
                        {item.id || `DIS-0${idx + 1}`}
                      </span>
                      <span className="font-mono text-micro text-content-secondary">
                        Topic: {item.title}
                      </span>
                    </div>
                    <h4 className="font-display font-bold text-base text-content-primary">
                      {item.issue}
                    </h4>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <span
                      className={`font-mono text-xs font-semibold px-2 py-0.5 rounded border ${
                        isHigh
                          ? 'bg-amber-50 text-amber-900 border-amber-300'
                          : 'bg-emerald-50 text-emerald-900 border-emerald-300'
                      }`}
                    >
                      σ {item.divergenceScore}
                    </span>
                    <span className="font-mono text-micro text-content-muted">
                      {item.consensus}
                    </span>
                  </div>
                </div>

                {/* Side-by-Side Clean Speech Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="speech-bubble space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-display font-bold text-content-primary">
                        {item.agentA.name}
                      </span>
                      <span className="font-mono text-[10px] text-content-muted">Stance</span>
                    </div>
                    <p className="font-body text-xs text-content-primary leading-relaxed">
                      &ldquo;{item.agentA.stance}&rdquo;
                    </p>
                  </div>

                  <div className="speech-bubble space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-display font-bold text-content-primary">
                        {item.agentB.name}
                      </span>
                      <span className="font-mono text-[10px] text-content-muted">Counter</span>
                    </div>
                    <p className="font-body text-xs text-content-primary leading-relaxed">
                      &ldquo;{item.agentB.stance}&rdquo;
                    </p>
                  </div>
                </div>

                {/* PRISM Synthesis Callout */}
                <div className="synthesis-callout space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-display font-bold text-emerald-900 flex items-center gap-1.5">
                      <span>🛡️ PRISM Swarm Resolution:</span>
                    </span>
                    <span className="font-mono text-[11px] text-emerald-800">Synthesized Verdict</span>
                  </div>

                  <p className="font-body text-small font-medium text-emerald-950 leading-relaxed">
                    {item.synthesis}
                  </p>

                  <div className="pt-2 border-t border-emerald-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                    <p className="font-body text-emerald-900/90 italic">
                      <strong>Why PRISM chose this:</strong> Balances enterprise-grade regulatory defensibility without stalling customer iteration.
                    </p>

                    <div className="flex items-center gap-2 shrink-0">
                      {typeof onOpenAgent === 'function' && (
                        <button
                          type="button"
                          onClick={() => onOpenAgent(item.agentA.name.toLowerCase().includes('cto') ? 'cto' : 'regulator')}
                          className="font-display text-micro font-semibold px-2 py-0.5 rounded border border-emerald-300 bg-surface text-content-primary hover:bg-surface-raised cursor-pointer"
                        >
                          View Agent Reasoning
                        </button>
                      )}
                      {typeof onOpenEvidence === 'function' && (
                        <button
                          type="button"
                          onClick={() =>
                            onOpenEvidence({
                              title: `${item.title} Grounding Evidence`,
                              source: 'World Bank & Regulatory Repository',
                              confidence: '95%',
                              text: item.synthesis,
                              impact: 'Enforces statutory compliance and architectural scalability.',
                            })
                          }
                          className="font-display text-micro font-semibold px-2 py-0.5 rounded border border-emerald-400 bg-emerald-100 text-emerald-900 hover:bg-emerald-200 cursor-pointer"
                        >
                          View Evidence ↗
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
