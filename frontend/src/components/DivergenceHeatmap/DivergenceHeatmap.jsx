import gsap from 'gsap'
import { useLayoutEffect, useRef } from 'react'
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

export default function DivergenceHeatmap({ bars }) {
  const containerRef = useRef(null)

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
      {bars.map((bar, index) => {
        const risk = Object.hasOwn(DISAGREEMENT_TEXT, bar.riskLevel) ? bar.riskLevel : 'low'
        const score = clampScore(bar.riskScore)
        const tooltipId = `heatmap-tip-${index}`

        return (
          <div
            key={bar.sectionTitle}
            className="heatmap__row"
            data-risk={risk}
            tabIndex={0}
            aria-describedby={tooltipId}
          >
            <span className="heatmap__label">{bar.sectionTitle}</span>
            <div className="heatmap__track">
              <div className="bar-fill" style={{ '--bar-scale': score / 100 }} />
            </div>
            <span className="heatmap__value">{score}</span>
            <div id={tooltipId} role="tooltip" className="heatmap__tooltip">
              <span className="heatmap__tooltip-stat">Std dev {bar.stdDev}</span>
              {DISAGREEMENT_TEXT[risk]}
            </div>
          </div>
        )
      })}
    </section>
  )
}
