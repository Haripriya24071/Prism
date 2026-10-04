import { useState } from 'react'
import './Workspace.css'

const TABS = [
  { id: 'overview', label: 'Overview', icon: '📊', hash: '#overview' },
  { id: 'swarm', label: 'Swarm', icon: '🐝', hash: '#swarm' },
  { id: 'deliberation', label: 'Deliberation', icon: '⚔️', hash: '#deliberation' },
  { id: 'final_brd', label: 'Final BRD', icon: '📑', hash: '#final-brd' },
  { id: 'risks', label: 'Risks', icon: '⚠️', hash: '#risks' },
  { id: 'export', label: 'Exports', icon: '📥', hash: '#exports' },
]

export default function WorkspaceNav({
  activeTab,
  setActiveTab,
  score,
  confidenceBand,
  sessionId,
  onReset,
}) {
  const [copiedUrl, setCopiedUrl] = useState(false)
  const currentTabObj = TABS.find((t) => t.id === activeTab) || TABS[0]
  const currentHash = currentTabObj.hash

  const handleCopyUrl = () => {
    const fullUrl = `${window.location.origin}${window.location.pathname}${currentHash}`
    if (navigator.clipboard) {
      navigator.clipboard.writeText(fullUrl)
      setCopiedUrl(true)
      setTimeout(() => setCopiedUrl(false), 2200)
    }
  }

  const handleToggleObserver = () => {
    window.dispatchEvent(new CustomEvent('prism-toggle-observer'))
  }

  return (
    <header className="comic-nav-header">
      <div className="comic-nav-container mx-auto max-w-7xl">
        {/* Left: Brand + Comic URL Locator */}
        <div className="flex items-center gap-2.5 shrink-0">
          <div
            className="flex items-center gap-1.5 cursor-pointer select-none"
            onClick={() => setActiveTab('overview')}
            title="PRISM Autonomous Decision Workspace"
          >
            <span className="font-display font-extrabold text-xl tracking-tight text-content-primary">
              PRISM
            </span>
            <span className="font-mono text-[10px] font-bold px-1.5 py-0.5 rounded bg-surface border border-border text-accent-signal shadow-[1px_1px_0px_var(--color-border)]">
              ✦ SWARM
            </span>
          </div>

          {/* Artistic Comic URL Locator Bar */}
          <div
            className="comic-url-bar hidden sm:flex items-center gap-1.5 px-2 py-1 rounded-md border border-border bg-surface text-content-secondary font-mono text-[11px] shadow-[1.5px_1.5px_0px_var(--color-border)]"
            title="Current Site URL Locator (Click copy to share deep-link)"
          >
            <span className="text-accent-signal text-xs">📍</span>
            <span className="text-content-muted text-[10px]">prism://</span>
            {sessionId && (
              <span className="text-content-muted text-[10px] hidden md:inline">
                {sessionId.slice(0, 8)}/
              </span>
            )}
            <span className="font-bold text-content-primary">{currentHash}</span>
            <button
              type="button"
              onClick={handleCopyUrl}
              className="comic-url-copy-btn ml-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-surface-raised hover:bg-accent-tint text-content-primary border border-border-subtle transition-colors cursor-pointer"
              title="Copy shareable link"
            >
              {copiedUrl ? '✓ Copied' : '🔗 Copy'}
            </button>
          </div>
        </div>

        {/* Center: Minimal Comic Navigation Tabs */}
        <nav className="comic-tabs-nav flex items-center gap-1 sm:gap-1.5 overflow-x-auto scrollbar-none" aria-label="Workspace Views">
          {TABS.map((tab) => {
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`comic-tab-item ${
                  isActive ? 'comic-tab-item--active' : ''
                }`}
                aria-current={isActive ? 'page' : undefined}
                title={`Navigate to ${tab.label} (${tab.hash})`}
              >
                <span className="text-xs" aria-hidden="true">{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            )
          })}
        </nav>

        {/* Right: Score Pill, Observer Trigger & Reset */}
        <div className="flex items-center gap-2 shrink-0">
          {score !== null && score !== undefined && (
            <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-md border border-border bg-surface shadow-[1.5px_1.5px_0px_var(--color-border)]">
              <span className="font-display font-bold text-xs text-content-primary">
                {score}/100
              </span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-accent-tint text-accent-signal uppercase tracking-wider">
                {confidenceBand ? confidenceBand.replace(/_/g, ' ') : 'Fundable'}
              </span>
            </div>
          )}

          {/* Observer Companion Toggle Button */}
          <button
            type="button"
            onClick={handleToggleObserver}
            className="comic-action-btn comic-observer-toggle px-2.5 py-1 rounded-md border border-border bg-surface hover:bg-surface-raised text-content-primary font-display font-semibold text-xs flex items-center gap-1.5 shadow-[1.5px_1.5px_0px_var(--color-border)] transition-all cursor-pointer"
            title="Open PRISM Observer guy (bottom-left corner)"
          >
            <span>🕵️</span>
            <span className="hidden md:inline">Observer</span>
          </button>

          {typeof onReset === 'function' && (
            <button
              type="button"
              onClick={onReset}
              className="comic-action-btn px-2.5 py-1 rounded-md border border-border bg-surface hover:bg-surface-raised text-content-secondary hover:text-content-primary font-display font-semibold text-xs flex items-center gap-1 shadow-[1.5px_1.5px_0px_var(--color-border)] transition-all cursor-pointer"
              title="Start a new pitch evaluation"
            >
              <span>↺</span>
              <span className="hidden sm:inline">New Pitch</span>
            </button>
          )}
        </div>
      </div>
    </header>
  )
}
