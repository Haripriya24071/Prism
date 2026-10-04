import './VentureDossier.css'

const PARAMETER_CONFIG = [
  {
    key: 'raw_idea',
    label: 'Core Concept & Offer',
    icon: '💡',
    placeholder: 'Listening for problem statement & what you are building...',
    tag: 'Problem & Value Loop',
  },
  {
    key: 'region',
    label: 'Target Region',
    icon: '🌍',
    placeholder: 'Where are we setting it up? E.g., India, US, UK, UAE...',
    tag: 'Regional REST Harvesters',
  },
  {
    key: 'industry',
    label: 'Industry Vertical',
    icon: '🏷️',
    placeholder: 'Fintech, Healthcare, B2B SaaS, Logistics...',
    tag: 'Sector Intelligence',
  },
  {
    key: 'stage',
    label: 'Venture Stage',
    icon: '🚀',
    placeholder: 'Fresh new idea, working prototype, or active MVP with a team?',
    tag: 'Execution Maturity',
  },
  {
    key: 'budget_range',
    label: 'Budget & Income Range',
    icon: '💰',
    placeholder: 'Expected revenue model, starting budget, or runway...',
    tag: 'Unit Economics Grounding',
  },
  {
    key: 'success_definition',
    label: '12-Month Target',
    icon: '🎯',
    placeholder: 'What milestone defines success for you in year one?',
    tag: 'Success Benchmark',
  },
]

function formatRegionName(code) {
  if (!code) return null
  const map = {
    IN: '🇮🇳 India (IN)',
    US: '🇺🇸 United States (US)',
    GB: '🇬🇧 United Kingdom (GB)',
    AE: '🇦🇪 UAE (AE)',
    SG: '🇸🇬 Singapore (SG)',
    DE: '🇩🇪 Germany (DE)',
    EU: '🇪🇺 European Union (EU)',
    AU: '🇦🇺 Australia (AU)',
  }
  return map[code.toUpperCase()] || `🌐 ${code.toUpperCase()}`
}

function formatStageName(stage) {
  if (!stage) return null
  const map = {
    idea: '💡 Idea Stage (Pre-development)',
    prototype: '🛠️ Working Prototype',
    mvp: '🚀 Active MVP (Testing with users)',
    growth: '📈 Growth & Scaling Stage',
  }
  return map[stage.toLowerCase()] || stage
}

export default function VentureDossier({ extraction = {}, completionPct = 0, onRunSwarm, isComplete = false }) {
  const fields = extraction || {}

  const capturedCount = PARAMETER_CONFIG.filter((param) => {
    const val = fields[param.key]
    return val !== null && val !== undefined && String(val).trim() !== ''
  }).length

  const progress = Math.max(completionPct, Math.round((capturedCount / 6) * 100))

  return (
    <aside className="dossier-card" aria-label="Structured Venture Blueprint">
      <div className="dossier-card__header">
        <div className="flex items-center justify-between">
          <div className="dossier-card__badge">
            <span className="dossier-card__dot" />
            LIVE VENTURE BLUEPRINT
          </div>
          <span className="font-tertiary text-micro font-bold text-accent-signal uppercase tracking-wider">
            {capturedCount} of 6 Locked
          </span>
        </div>

        <h2 className="dossier-card__title">Structured Intake Dossier</h2>
        <p className="dossier-card__subtitle">
          Form fields fill behind the scenes as you chat. Zero friction, zero manual forms.
        </p>

        {/* Dynamic Progress Bar */}
        <div className="dossier-progress">
          <div className="dossier-progress__bar" style={{ width: `${progress}%` }} />
        </div>
        <div className="flex justify-between items-center text-[11px] font-tertiary text-content-secondary mt-1">
          <span>Swarm Readiness</span>
          <span className="font-bold text-content-primary">{progress}% Calibrated</span>
        </div>
      </div>

      {/* Field List */}
      <div className="dossier-list">
        {PARAMETER_CONFIG.map((param) => {
          let value = fields[param.key]
          if (param.key === 'region') value = formatRegionName(value)
          if (param.key === 'stage') value = formatStageName(value)

          const isFilled = value !== null && value !== undefined && String(value).trim() !== ''

          return (
            <div
              key={param.key}
              className={`dossier-item ${isFilled ? 'dossier-item--filled' : 'dossier-item--pending'}`}
            >
              <div className="dossier-item__top">
                <span className="dossier-item__icon">{param.icon}</span>
                <span className="dossier-item__label">{param.label}</span>
                <span className={`dossier-status-badge ${isFilled ? 'dossier-status-badge--locked' : 'dossier-status-badge--waiting'}`}>
                  {isFilled ? '✓ Locked' : 'Listening...'}
                </span>
              </div>

              <div className="dossier-item__content">
                {isFilled ? (
                  <p className="dossier-item__value">{String(value)}</p>
                ) : (
                  <p className="dossier-item__placeholder">{param.placeholder}</p>
                )}
              </div>

              {isFilled && param.key === 'region' && (
                <div className="dossier-item__footnote">
                  🏛️ Triggers live NewsAPI, Wikipedia Geopolitics, and Forex REST harvesters for {String(value)}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Call to action footer */}
      <div className="dossier-footer">
        <p className="dossier-footer__text">
          {capturedCount >= 3 ? (
            <span>🚀 <strong>Swarm Threshold Reached.</strong> All 6 agents are calibrated with your business context.</span>
          ) : (
            <span>💬 Answer the dynamic follow-up questions in chat to enrich your final BRD.</span>
          )}
        </p>

        {capturedCount >= 3 && onRunSwarm && (
          <button
            type="button"
            onClick={onRunSwarm}
            className={`dossier-footer__btn ${isComplete ? 'dossier-footer__btn--pulse' : ''}`}
          >
            <span>Run 6-Agent Swarm</span>
            <span>→</span>
          </button>
        )}
      </div>
    </aside>
  )
}
