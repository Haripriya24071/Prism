import './Header.css'

const STAGES = [
  { id: 'intake', label: '1. Prompt Intake' },
  { id: 'generation', label: '2. Multi-Agent Synthesis' },
  { id: 'results', label: '3. BRD & Metrics' },
]

export function Header({ currentStage = 'intake', sessionId }) {
  return (
    <header className="app-header">
      <div className="app-header__brand">
        <span className="app-header__logo">PRISM</span>
        <span className="app-header__version">v1.0.0</span>
      </div>

      <nav className="app-header__stages" aria-label="Progress">
        {STAGES.map((stage) => (
          <span
            key={stage.id}
            className="app-header__stage"
            data-active={currentStage === stage.id}
            aria-current={currentStage === stage.id ? 'step' : undefined}
          >
            {stage.label}
          </span>
        ))}
      </nav>

      <div className="app-header__right">
        <a
          href="/pitch_deck.html"
          target="_blank"
          rel="noopener noreferrer"
          className="app-header__deck-link"
          title="Open interactive 6-slide Hackathon Pitch Deck"
        >
          Pitch Deck ↗
        </a>
        <div className="app-header__session">
          <span className="app-header__dot" aria-hidden="true" />
          {sessionId ? `Session: ${sessionId.slice(0, 8)}...` : 'Ready'}
        </div>
      </div>
    </header>
  )
}
