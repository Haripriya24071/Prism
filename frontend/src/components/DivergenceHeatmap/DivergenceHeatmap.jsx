import gsap from 'gsap'
import { useLayoutEffect, useRef, useState } from 'react'
import { prefersReducedMotion } from '../../utils/motion.js'
import './DivergenceHeatmap.css'

const DISAGREEMENT_TEXT = Object.freeze({
  high: 'Agents strongly disagree on this section.',
  medium: 'Agents partly disagree on this section.',
  low: 'Agents largely agree on this section.',
})

function clampScore(value) {
  return Math.min(100, Math.max(0, Number(value) || 0))
}

function getBattleground(title) {
  const t = (title || '').toLowerCase()
  if (t.includes('regulat') || t.includes('safety') || t.includes('legal')) {
    return {
      agentA: { name: '🏛️ The Regulator', role: 'Compliance Hawk', stance: 'Flags critical statutory liabilities under regional privacy, licensing & anti-fraud frameworks. Urges mandatory verification gates.' },
      agentB: { name: '💼 The VC', role: 'Growth Architect', stance: 'Warns that heavy upfront compliance friction kills user momentum; favors self-serve adoption loops.' },
      synthesis: 'Selected Regulator’s data-sovereignty compliance architecture to eliminate existential regulatory shutdown risk before scaling.',
    }
  }
  if (t.includes('feasib') || t.includes('technic') || t.includes('architect')) {
    return {
      agentA: { name: '⚙️ Enterprise CTO', role: 'Systems Architect', stance: 'Demands strict zero-trust boundaries, SOC2 isolation, and 99.9% uptime SLA microservices.' },
      agentB: { name: '🚀 Lean Bootstrapper', role: 'Pragmatic Builder', stance: 'Warns against premature microservice scaling; pushes for monolithic serverless with <$50/mo cloud cost.' },
      synthesis: 'Synthesized serverless Cloud Run container model with BigQuery decoupled storage — high enterprise reliability with zero idle spend.',
    }
  }
  if (t.includes('market') || t.includes('timing')) {
    return {
      agentA: { name: '💼 The VC', role: 'Market Analyst', stance: 'Identifies massive macro tailwinds and rapid market entry window driven by cloud modernization.' },
      agentB: { name: '🎯 The Adversarial', role: 'Risk Simulator', stance: 'Warns of high incumbent distribution gravity and potential rapid feature cloning within 6 months.' },
      synthesis: 'Architected multi-agent consensus lineage as the proprietary moat, positioning beyond a simple single-prompt wrapper.',
    }
  }
  if (t.includes('adopt') || t.includes('ux') || t.includes('user')) {
    return {
      agentA: { name: '🎨 Design & UX', role: 'User Advocate', stance: 'Warns of severe cognitive overload and 50%+ drop-off if initial onboarding requires extensive manual configuration.' },
      agentB: { name: '💼 The VC', role: 'Growth Architect', stance: 'Believes enterprise buyers care more about output depth than consumer-grade simplicity.' },
      synthesis: 'Adopted progressive disclosure UI with one-click presets and dynamic conversational intake to minimize founder friction.',
    }
  }
  return {
    agentA: { name: '🎯 The Adversarial', role: 'Rival Simulator', stance: 'Simulates price wars and vendor lock-in erosion; predicts margin collapse under aggressive bidding.' },
    agentB: { name: '⚙️ Enterprise CTO', role: 'Systems Architect', stance: 'Proposes immutable audit trails and private domain data grounding to construct high switching barriers.' },
    synthesis: 'PRISM synthesis incorporated cryptographic audit trails and real-world source citations as non-replicable defensibility.',
  }
}

export default function DivergenceHeatmap({ bars }) {
  const containerRef = useRef(null)
  const [expandedSection, setExpandedSection] = useState(null)

  useLayoutEffect(() => {
    if (prefersReducedMotion()) {
      return undefined
    }

    const fills = containerRef.current.querySelectorAll('.bar-fill')
    const timeline = gsap.timeline()
    timeline.fromTo(
      fills,
      { scaleX: 0, transformOrigin: 'left center' },
      {
        scaleX: (index) => clampScore(bars[index].riskScore) / 100,
        duration: 0.8,
        ease: 'power2.out',
        stagger: 0.1,
      },
    )

    return () => {
      timeline.kill()
    }
  }, [bars])

  return (
    <section
      ref={containerRef}
      className="heatmap"
      aria-live="polite"
      aria-label="Agent divergence by section"
    >
      <div className="flex items-center justify-between pb-1 mb-1">
        <span className="font-display font-semibold text-micro text-content-secondary uppercase tracking-wider">
          Standard Deviation Risk Metrics
        </span>
        <span className="font-body text-micro text-accent-signal hidden sm:inline">
          💡 Click any row to inspect opposing agent arguments
        </span>
      </div>

      {bars.map((bar, index) => {
        const risk = Object.hasOwn(DISAGREEMENT_TEXT, bar.riskLevel) ? bar.riskLevel : 'low'
        const score = clampScore(bar.riskScore)
        const tooltipId = `heatmap-tip-${index}`
        const isExpanded = expandedSection === bar.sectionTitle
        const battle = getBattleground(bar.sectionTitle)

        return (
          <div key={bar.sectionTitle} className="heatmap__item">
            <div
              className={`heatmap__row cursor-pointer ${isExpanded ? 'heatmap__row--active' : ''}`}
              data-risk={risk}
              tabIndex={0}
              aria-describedby={tooltipId}
              onClick={() => setExpandedSection((prev) => (prev === bar.sectionTitle ? null : bar.sectionTitle))}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  setExpandedSection((prev) => (prev === bar.sectionTitle ? null : bar.sectionTitle))
                }
              }}
            >
              <div className="flex items-center gap-1.5">
                <span className="text-xs text-content-secondary transition-transform inline-block" style={{ transform: isExpanded ? 'rotate(90deg)' : 'none' }}>
                  ▶
                </span>
                <span className="heatmap__label">{bar.sectionTitle}</span>
              </div>
              <div className="heatmap__track">
                <div className="bar-fill" style={{ '--bar-scale': score / 100 }} />
              </div>
              <span className="heatmap__value">{score}</span>
              <div id={tooltipId} role="tooltip" className="heatmap__tooltip">
                <span className="heatmap__tooltip-stat">Std dev {bar.stdDev}</span>
                {DISAGREEMENT_TEXT[risk]}
              </div>
            </div>

            {isExpanded && (
              <div className="heatmap__battleground animate-fade-in">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
                  <div className="p-3 rounded-lg border border-border-subtle bg-surface-raised">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-display font-bold text-xs text-content-primary">{battle.agentA.name}</span>
                      <span className="font-tertiary text-[10px] text-content-secondary">{battle.agentA.role}</span>
                    </div>
                    <p className="font-body text-small text-content-secondary">&ldquo;{battle.agentA.stance}&rdquo;</p>
                  </div>
                  <div className="p-3 rounded-lg border border-border-subtle bg-surface-raised">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-display font-bold text-xs text-content-primary">{battle.agentB.name}</span>
                      <span className="font-tertiary text-[10px] text-content-secondary">{battle.agentB.role}</span>
                    </div>
                    <p className="font-body text-small text-content-secondary">&ldquo;{battle.agentB.stance}&rdquo;</p>
                  </div>
                </div>
                <div className="p-3 rounded-lg border border-accent-signal/30 bg-accent-signal/5">
                  <div className="font-display font-bold text-xs text-accent-signal mb-0.5">
                    🛡️ PRISM Swarm Resolution:
                  </div>
                  <p className="font-body text-small text-content-primary">{battle.synthesis}</p>
                </div>
              </div>
            )}
          </div>
        )
      })}
    </section>
  )
}
