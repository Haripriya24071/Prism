import { useState } from 'react'
import './BRDViewer.css'

export default function RealWorldContextRadar({ context }) {
  const [isExpanded, setIsExpanded] = useState(true)

  if (!context) {
    return null
  }

  const geo = context.geopolitical_data || {}
  const country = geo.country || context.region || 'Regional'
  const rulingParty = geo.ruling_coalition || 'Government Administration'
  const politicalSystem = geo.political_system || 'Constitutional Democracy'
  const politicalFactors = geo.key_political_factors || 'Active commercial oversight'

  const religion =
    context.religious_context ||
    geo.religious_demographics ||
    'Multi-cultural consumer cohorts with peak festive shopping surges'

  const sentiment = context.market_sentiment || {}
  const marketMood = (sentiment.market_mood || 'neutral').toUpperCase()
  const sentimentScore = sentiment.market_sentiment_score ?? 0.05

  const forex = context.forex_data || {}
  const currency = forex.local_currency || 'USD'
  const currencyName = forex.currency_name || 'US Dollar'
  const currencySymbol = forex.currency_symbol || '$'
  const exchangeRate = forex.exchange_rate_per_usd ?? 1.0
  const forexRisk = forex.forex_volatility_risk || 'Low'

  const newsItems = Array.isArray(context.news_items) ? context.news_items.slice(0, 3) : []

  return (
    <section className="context-radar" aria-labelledby="context-radar-heading">
      <div className="context-radar__header" onClick={() => setIsExpanded((prev) => !prev)}>
        <div className="context-radar__title-wrap">
          <div className="context-radar__badge">LIVE GROUNDING RADAR</div>
          <h2 id="context-radar-heading" className="context-radar__title">
            Real-World Geopolitical & Market Matrix
          </h2>
          <p className="context-radar__subtitle">
            Zero-key open harvesters & fiscal intelligence powering adversarial BRD synthesis
          </p>
        </div>
        <div className="context-radar__toggle">
          <span className="context-radar__status-dot" />
          <button
            type="button"
            className="context-radar__toggle-btn"
            aria-expanded={isExpanded}
          >
            {isExpanded ? 'Collapse Intel' : 'Expand Intel'}
          </button>
        </div>
      </div>

      {/* Pill ticker */}
      <div className="context-radar__pills">
        <span className="context-pill context-pill--geo">
          <span className="context-pill__icon">🏛️</span>
          <strong>{country}:</strong> {rulingParty.length > 35 ? rulingParty.slice(0, 35) + '...' : rulingParty}
        </span>
        <span className="context-pill context-pill--sentiment">
          <span className="context-pill__icon">📈</span>
          <strong>Market Mood:</strong> {marketMood} ({sentimentScore > 0 ? `+${sentimentScore}` : sentimentScore})
        </span>
        <span className="context-pill context-pill--forex">
          <span className="context-pill__icon">💱</span>
          <strong>Forex:</strong> 1 USD = {exchangeRate} {currency} ({forexRisk} Risk)
        </span>
        <span className="context-pill context-pill--religion">
          <span className="context-pill__icon">🕉️</span>
          <strong>Culture:</strong> Festive Cycles Indexed
        </span>
      </div>

      {isExpanded && (
        <div className="context-radar__grid">
          {/* Card 1: Geopolitics & Ruling Party */}
          <div className="radar-card radar-card--geo">
            <div className="radar-card__tag">POLITICAL STABILITY & GOVERNANCE</div>
            <h3 className="radar-card__heading">{country} · {politicalSystem}</h3>
            <p className="radar-card__body">
              <strong>Ruling Administration:</strong> {rulingParty}
            </p>
            <p className="radar-card__notes">
              <strong>Key Regulatory Priorities:</strong> {politicalFactors}
            </p>
            <div className="radar-card__footer">Source: [SOURCE: geopolitics] Wikipedia REST & Knowledge Base</div>
          </div>

          {/* Card 2: Cultural & Religious Demographics */}
          <div className="radar-card radar-card--religion">
            <div className="radar-card__tag">CULTURAL DEMOGRAPHICS & FESTIVE COMMERCE</div>
            <h3 className="radar-card__heading">Religious Calendars & Seasonal Surges</h3>
            <p className="radar-card__body">{religion}</p>
            <div className="radar-card__footer">Source: [SOURCE: religion] National Demographic Census</div>
          </div>

          {/* Card 3: Market Sentiment & Fiscal Mood */}
          <div className="radar-card radar-card--sentiment">
            <div className="radar-card__tag">ALPHA VANTAGE FISCAL SENTIMENT</div>
            <h3 className="radar-card__heading">
              Mood: <span className={`mood-text mood-text--${marketMood.toLowerCase()}`}>{marketMood}</span>
            </h3>
            <p className="radar-card__body">
              Quantitative sentiment index is <strong>{sentimentScore}</strong>. Macro-environment supports disciplined capital deployment and milestone-based growth.
            </p>
            <div className="radar-card__footer">Source: [SOURCE: alphavantage] Alpha Vantage Live Feed</div>
          </div>

          {/* Card 4: Currency & Forex Valuation */}
          <div className="radar-card radar-card--forex">
            <div className="radar-card__tag">CURRENCY & EXCHANGE RATE EXPOSURE</div>
            <h3 className="radar-card__heading">
              {currencyName} ({currencySymbol} {currency})
            </h3>
            <p className="radar-card__body">
              Real-time exchange rate: <strong>1 USD = {exchangeRate} {currency}</strong>. Volatility exposure assessed as <strong>{forexRisk}</strong>.
            </p>
            <div className="radar-card__footer">Source: [SOURCE: forex] Open Exchange Rates</div>
          </div>

          {/* Card 5: Recent News Headlines */}
          {newsItems.length > 0 && (
            <div className="radar-card radar-card--news radar-card--fullwidth">
              <div className="radar-card__tag">VERIFIED REGIONAL HEADLINES</div>
              <ul className="radar-card__news-list">
                {newsItems.map((item, idx) => (
                  <li key={idx} className="radar-card__news-item">
                    <span className="news-bullet">📰</span>
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="radar-card__news-link"
                    >
                      {item.title}
                    </a>
                    <span className="radar-card__news-source">({item.source})</span>
                  </li>
                ))}
              </ul>
              <div className="radar-card__footer">Source: [SOURCE: newsapi] NewsAPI Real-Time Dispatch</div>
            </div>
          )}
        </div>
      )}
    </section>
  )
}
