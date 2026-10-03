import gsap from 'gsap'
import { useLayoutEffect, useRef } from 'react'
import { prefersReducedMotion } from '../../utils/motion.js'
import './ScoreCard.css'

const RADIUS = 52
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

function getBand(score) {
  if (score > 70) {
    return 'good'
  }
  if (score >= 50) {
    return 'fair'
  }
  return 'poor'
}

function dashOffsetFor(score) {
  return CIRCUMFERENCE * (1 - score / 100)
}

export function ScoreRing({ score }) {
  const safeScore = Math.min(100, Math.max(0, Number(score) || 0))
  const progressRef = useRef(null)
  const valueRef = useRef(null)

  useLayoutEffect(() => {
    if (prefersReducedMotion()) {
      return undefined
    }

    const progress = progressRef.current
    const valueText = valueRef.current
    const counter = { value: 0 }

    progress.setAttribute('stroke-dashoffset', dashOffsetFor(0))
    valueText.textContent = '0'

    const tween = gsap.to(counter, {
      value: safeScore,
      duration: 1.8,
      ease: 'power2.out',
      onUpdate: () => {
        progress.setAttribute('stroke-dashoffset', dashOffsetFor(counter.value))
        valueText.textContent = String(Math.round(counter.value))
      },
    })

    return () => {
      tween.kill()
    }
  }, [safeScore])

  return (
    <div className="score-ring">
      <svg
        className="score-ring__svg"
        viewBox="0 0 120 120"
        data-band={getBand(safeScore)}
        role="img"
        aria-label={`Investor readiness score ${safeScore} out of 100`}
      >
        <circle className="score-ring__track" cx="60" cy="60" r={RADIUS} fill="none" strokeWidth="10" />
        <circle
          ref={progressRef}
          className="score-ring__progress"
          cx="60"
          cy="60"
          r={RADIUS}
          fill="none"
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={dashOffsetFor(safeScore)}
          transform="rotate(-90 60 60)"
        />
      </svg>
      <div className="score-ring__center" aria-hidden="true">
        <span ref={valueRef} className="score-ring__value">{safeScore}</span>
        <span className="score-ring__max">/ 100</span>
      </div>
    </div>
  )
}
