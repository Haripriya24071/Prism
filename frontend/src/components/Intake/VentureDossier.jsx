import { useState } from 'react'
import './VentureDossier.css'

const PARAMETER_CONFIG = [
  {
    key: 'raw_idea',
    label: 'Core Concept',
    icon: '💡',
    placeholder: 'Listening for problem & value proposition...',
  },
  {
    key: 'region',
    label: 'Target Market',
    icon: '🌍',
    placeholder: 'Pending region selection...',
  },
  {
    key: 'industry',
    label: 'Sector Vertical',
    icon: '🏷️',
    placeholder: 'Pending industry classification...',
  },
  {
    key: 'stage',
    label: 'Venture Stage',
    icon: '🚀',
    placeholder: 'Pending maturity level...',
  },
  {
    key: 'budget_range',
    label: 'Runway / Budget',
    icon: '💰',
    placeholder: 'Pending economic range...',
  },
  {
    key: 'success_definition',
    label: '12-Month Target',
    icon: '🎯',
    placeholder: 'Pending key milestone...',
  },
]

function formatRegionName(code) {
  if (!code) return null
  const map = {
    IN: '🇮🇳 India',
    US: '🇺🇸 United States',
    GB: '🇬🇧 United Kingdom',
    AE: '🇦🇪 UAE',
    SG: '🇸🇬 Singapore',
    DE: '🇩🇪 Germany',
    EU: '🇪🇺 European Union',
    AU: '🇦🇺 Australia',
  }
  return map[code.toUpperCase()] || code.toUpperCase()
}

function formatStageName(stage) {
  if (!stage) return null
  const map = {
    idea: '💡 Idea (Pre-Seed)',
    prototype: '🛠️ Working Prototype',
    mvp: '🚀 Active MVP',
    growth: '📈 Growth & Scaling',
  }
  return map[stage.toLowerCase()] || stage
}

export default function VentureDossier({
  extraction = {},
  completionPct = 0,
  onRunSwarm,
  isComplete = false,
}) {
  const [showHarvesterInfo, setShowHarvesterInfo] = useState(false)
  const fields = extraction || {}

  const capturedCount = PARAMETER_CONFIG.filter((param) => {
    const val = fields[param.key]
    return val !== null && val !== undefined && String(val).trim() !== ''
  }).length

  const progress = Math.max(completionPct, Math.round((capturedCount / 6) * 100))
  const isReady = capturedCount >= 3 || isComplete

  return (
    <aside className="venture-matrix" aria-label="Live Venture Calibration Matrix">
      {/* Matrix Header Strip */}
      <div className="venture-matrix__header">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="venture-matrix__status-dot" aria-hidden="true" />
            <div>
              <div className="flex items-center gap-2">
                <span className="font-tertiary text-micro font-bold text-accent-signal uppercase tracking-wider">
                  Live Swarm Calibration
                </span>
                <span className="text-content-muted text-micro">•</span>
                <span className="font-tertiary text-micro font-semibold text-content-secondary">
                  {capturedCount} of 6 Parameters Armed
                </span>
              </div>
              <p className="font-body text-micro text-content-secondary mt-0.5">
                Form fields lock behind the scenes as you chat or voice dictate.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 self-end sm:self-auto">
            {/* Progress Meter */}
            <div className="flex items-center gap-2">
              <div className="venture-matrix__progress-track" aria-hidden="true">
                <div
                  className="venture-matrix__progress-fill"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <span className="font-tertiary text-micro font-bold text-content-primary">
                {progress}%
              </span>
            </div>

            {/* Run Swarm CTA button if ready */}
            {isReady && onRunSwarm && (
              <button
                type="button"
                onClick={onRunSwarm}
                className="venture-matrix__cta-btn"
              >
                <span>Launch Swarm</span>
                <span className="venture-matrix__cta-arrow">→</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* 6 Responsive Parameter Matrix Cards */}
      <div className="venture-matrix__grid">
        {PARAMETER_CONFIG.map((param) => {
          let value = fields[param.key]
          if (param.key === 'region') value = formatRegionName(value)
          if (param.key === 'stage') value = formatStageName(value)

          const isFilled = value !== null && value !== undefined && String(value).trim() !== ''

          return (
            <div
              key={param.key}
              className={`venture-matrix__cell ${
                isFilled ? 'venture-matrix__cell--locked' : 'venture-matrix__cell--pending'
              }`}
            >
              <div className="venture-matrix__cell-top">
                <div className="flex items-center gap-1.5 overflow-hidden">
                  <span className="text-sm">{param.icon}</span>
                  <span className="font-display text-micro font-bold text-content-primary truncate">
                    {param.label}
                  </span>
                </div>
                {isFilled && (
                  <span className="venture-matrix__badge-locked">
                    ✓
                  </span>
                )}
              </div>

              <div className="venture-matrix__cell-body">
                {isFilled ? (
                  <p className="venture-matrix__value" title={String(value)}>
                    {String(value)}
                  </p>
                ) : (
                  <p className="venture-matrix__placeholder">
                    {param.placeholder}
                  </p>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Harvester Intel Dropdown Toggle */}
      {fields.region && (
        <div className="venture-matrix__harvester-bar">
          <button
            type="button"
            onClick={() => setShowHarvesterInfo(!showHarvesterInfo)}
            className="text-micro font-tertiary text-content-secondary hover:text-content-primary transition-colors flex items-center gap-1.5"
          >
            <span>🏛️</span>
            <span>Regional Harvesters Active for <strong>{formatRegionName(fields.region)}</strong></span>
            <span>{showHarvesterInfo ? '▴' : '▾'}</span>
          </button>

          {showHarvesterInfo && (
            <div className="venture-matrix__harvester-details">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 mt-2 pt-2 border-t border-border-subtle text-micro font-tertiary">
                <div>
                  <span className="font-bold text-content-primary block">NewsAPI:</span>
                  <span className="text-content-secondary">Harvesting local sector headlines & sentiment</span>
                </div>
                <div>
                  <span className="font-bold text-content-primary block">Wikipedia:</span>
                  <span className="text-content-secondary">Analyzing regional demographics & cultural landscape</span>
                </div>
                <div>
                  <span className="font-bold text-content-primary block">Markets:</span>
                  <span className="text-content-secondary">Tracking local FX volatility & AlphaVantage indexes</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </aside>
  )
}
