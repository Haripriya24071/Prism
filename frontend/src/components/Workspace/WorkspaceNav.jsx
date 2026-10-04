import { useState } from 'react'
import prismLogo from '../../assets/landing/prism_logo.jpg'
import './Workspace.css'

const PRIMARY_TABS = [
  { id: 'overview', label: 'Overview' },
  { id: 'swarm', label: 'Swarm' },
  { id: 'deliberation', label: 'Deliberation' },
  { id: 'final_brd', label: 'Final BRD' },
  { id: 'risks', label: 'Risks' },
  { id: 'export', label: 'Exports' },
]

export default function WorkspaceNav({
  activeTab,
  setActiveTab,
  onReset,
}) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-40 w-full bg-void border-b border-border-subtle select-none">
      <div className="max-w-7xl mx-auto px-4 sm:px-8 h-[74px] flex items-center justify-between">
        
        {/* LEFT: Circular Logo Mark + Bold PRISM Wordmark with generous breathing room */}
        <div className="flex items-center gap-3 shrink-0 mr-6 lg:mr-10">
          <button
            type="button"
            onClick={() => setActiveTab('overview')}
            className="group flex items-center gap-3 cursor-pointer select-none text-left focus-visible:outline-none"
            aria-label="PRISM Home - Return to Overview"
          >
            <img
              src={prismLogo}
              alt="PRISM"
              className="w-10 h-10 rounded-full border-2 border-border shadow-[1.5px_1.5px_0px_var(--color-border)] object-cover group-hover:scale-105 transition-transform duration-200"
            />
            <span className="font-display font-black text-2xl sm:text-[28px] tracking-[0.06em] text-content-primary leading-none">
              PRISM
            </span>
          </button>
        </div>

        {/* CENTER: Typography-Driven Text Navigation without emojis or button pills */}
        <nav
          className="hidden md:flex items-center gap-6 lg:gap-8 flex-1 justify-center"
          aria-label="Workspace Views"
        >
          {PRIMARY_TABS.map((tab) => {
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`font-display text-sm tracking-tight transition-colors cursor-pointer relative py-2 ${
                  isActive
                    ? 'font-semibold text-content-primary'
                    : 'font-medium text-content-secondary hover:text-content-primary'
                }`}
                aria-current={isActive ? 'page' : undefined}
              >
                {tab.label}
                {isActive && (
                  <span className="absolute -bottom-1 left-0 right-0 h-[2px] bg-content-primary rounded-full" />
                )}
              </button>
            )
          })}
        </nav>

        {/* RIGHT: Quiet Live Status Indicator + Single Strong Primary CTA */}
        <div className="flex items-center gap-4 sm:gap-6 shrink-0 ml-4">
          {/* Subtle Live Swarm Status */}
          <div className="flex items-center gap-2 text-xs font-tertiary text-content-secondary">
            <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse" />
            <span className="hidden sm:inline font-medium">Live Swarm</span>
          </div>

          {/* Strong Primary CTA: Pitch Idea → */}
          {typeof onReset === 'function' && (
            <button
              type="button"
              onClick={onReset}
              className="px-5 py-2 bg-content-primary text-surface font-display font-semibold text-xs rounded-full hover:bg-accent-signal transition-colors shadow-sm cursor-pointer whitespace-nowrap"
              title="Start a new founder pitch evaluation"
            >
              Pitch Idea →
            </button>
          )}

          {/* Mobile Menu Toggle Button */}
          <button
            type="button"
            onClick={() => setMobileMenuOpen((prev) => !prev)}
            className="md:hidden p-1.5 rounded text-content-secondary hover:text-content-primary cursor-pointer"
            aria-label="Toggle navigation menu"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {mobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile Navigation Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-border-subtle bg-surface px-4 py-3 space-y-1">
          {PRIMARY_TABS.map((tab) => {
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => {
                  setActiveTab(tab.id)
                  setMobileMenuOpen(false)
                }}
                className={`w-full text-left px-3 py-2 rounded-md font-display text-sm ${
                  isActive
                    ? 'font-bold bg-surface-raised text-content-primary'
                    : 'font-medium text-content-secondary hover:text-content-primary'
                }`}
              >
                {tab.label}
              </button>
            )
          })}
        </div>
      )}
    </header>
  )
}
