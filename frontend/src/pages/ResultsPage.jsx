import { useCallback, useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { fetchBRD, fetchPDF } from '../api.js'
import { getPageVariants } from '../animations/variants.js'
import BRDViewer from '../components/BRDViewer/BRDViewer.jsx'
import DivergenceHeatmap from '../components/DivergenceHeatmap/DivergenceHeatmap.jsx'
import ScoreCard from '../components/ScoreCard/ScoreCard.jsx'
import { useSession } from '../hooks/useSession.js'

const PDF_VIEWS = ['investor', 'technical', 'regulatory']
const HIGH_RISK_FROM = 60
const MEDIUM_RISK_FROM = 30

function toRiskLevel(riskScore) {
  if (riskScore >= HIGH_RISK_FROM) return 'high'
  if (riskScore >= MEDIUM_RISK_FROM) return 'medium'
  return 'low'
}

function toSection(section) {
  const lineage = section.lineage
  return {
    title: section.title,
    content: section.content,
    lineage: lineage
      ? {
          sourceAgent: lineage.source_agent,
          confidence: `${Math.round(lineage.confidence * 100)}%`,
          dataCitation: lineage.data_citation,
        }
      : { sourceAgent: 'unknown', confidence: 'n/a', dataCitation: 'No lineage recorded.' },
    dissentingAgents: [],
  }
}

function toAssumption(item) {
  return {
    text: item.assumption,
    confidenceLevel: item.confidence,
    evidence: item.evidence ?? 'No evidence provided.',
    recommendedAction: item.recommended_action,
  }
}

export default function ResultsPage() {
  const { sessionId, brdData, setBrdData, heatmapData, investorScore } = useSession()
  const [loadError, setLoadError] = useState(null)
  const [attempt, setAttempt] = useState(0)
  const [downloadingView, setDownloadingView] = useState(null)
  const [downloadError, setDownloadError] = useState(null)

  useEffect(() => {
    if (!sessionId || brdData) {
      return undefined
    }
    let cancelled = false

    async function load() {
      try {
        const data = await fetchBRD(sessionId)
        if (!cancelled) {
          setLoadError(null)
          setBrdData(data)
        }
      } catch (err) {
        if (!cancelled) {
          setLoadError(err?.message || 'Could not load the BRD.')
        }
      }
    }
    load()

    return () => {
      cancelled = true
    }
  }, [sessionId, brdData, setBrdData, attempt])

  const retry = useCallback(() => {
    setLoadError(null)
    setAttempt((count) => count + 1)
  }, [])

  const handleDownload = useCallback(
    async (view) => {
      setDownloadingView(view)
      setDownloadError(null)
      try {
        const blob = await fetchPDF(sessionId, view)
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `prism-brd-${view}.pdf`
        document.body.appendChild(link)
        link.click()
        link.remove()
        URL.revokeObjectURL(url)
      } catch (err) {
        setDownloadError(err?.message || `Could not download the ${view} PDF.`)
      } finally {
        setDownloadingView(null)
      }
    },
    [sessionId],
  )

  const sections = (brdData?.sections ?? []).map(toSection)
  const assumptions = (brdData?.assumptions ?? []).map(toAssumption)
  const bars = (heatmapData?.bars ?? []).map((bar) => ({
    sectionTitle: bar.section_title,
    riskScore: bar.risk_score,
    stdDev: bar.std_dev,
    riskLevel: toRiskLevel(bar.risk_score),
  }))
  const score = investorScore?.score ?? brdData?.investor_readiness_score ?? null

  return (
    <motion.main
      className="mx-auto min-h-screen max-w-6xl bg-void p-8 font-body text-content-primary"
      variants={getPageVariants()}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      <header className="grid gap-4 border-b border-border pb-6">
        <h1 className="font-display text-h1 font-bold">Your BRD</h1>
        <div className="flex flex-wrap gap-2">
          {PDF_VIEWS.map((view) => (
            <button
              key={view}
              type="button"
              disabled={downloadingView !== null || !brdData}
              onClick={() => handleDownload(view)}
              className="rounded-md border border-border bg-surface-raised px-3 py-2 font-body text-small text-content-primary disabled:text-content-muted"
            >
              {downloadingView === view ? 'Preparing...' : `Download ${view} PDF`}
            </button>
          ))}
        </div>
        {downloadError && (
          <p role="alert" className="font-body text-small text-error">
            {downloadError}
          </p>
        )}
      </header>

      {loadError && (
        <div role="alert" className="mt-6 flex items-center justify-between rounded-md border border-error bg-surface p-4">
          <span className="font-body text-small text-error">{loadError}</span>
          <button
            type="button"
            onClick={retry}
            className="rounded-md bg-accent-signal px-3 py-1 font-body text-small text-void"
          >
            Retry
          </button>
        </div>
      )}

      {!brdData && !loadError && (
        <div className="mt-8 grid items-start gap-8 lg:grid-cols-3" aria-busy="true" aria-live="polite">
          <span className="sr-only">Loading your BRD</span>
          <div className="grid gap-8 lg:col-span-2">
            <div className="grid gap-3 rounded-lg border border-border bg-surface p-6">
              {Array.from({ length: 5 }, (_, i) => (
                <div key={i} className="skeleton skeleton--row" />
              ))}
            </div>
            <div className="grid gap-4 rounded-lg border border-border bg-surface p-6">
              {Array.from({ length: 5 }, (_, i) => (
                <div key={i} className="skeleton skeleton--accordion" />
              ))}
            </div>
          </div>
          <div className="grid justify-items-center rounded-xl border border-border bg-surface p-8">
            <div className="skeleton skeleton--ring" />
          </div>
        </div>
      )}

      {brdData && (
        <div className="mt-8 grid items-start gap-8 lg:grid-cols-3">
          <div className="grid gap-8 lg:col-span-2">
            {bars.length > 0 && (
              <section className="rounded-lg border border-border bg-surface p-6">
                <h2 className="mb-4 font-display text-h2 font-semibold">Where the agents disagreed</h2>
                <DivergenceHeatmap bars={bars} />
              </section>
            )}
            <section className="rounded-lg border border-border bg-surface p-6">
              <h2 className="mb-4 font-display text-h2 font-semibold">Requirements</h2>
              <BRDViewer sections={sections} assumptions={assumptions} />
            </section>
          </div>

          {score !== null && (
            <ScoreCard
              score={score}
              confidenceBand={investorScore?.confidence_band}
              gapFlags={(investorScore?.gap_flags ?? []).map((flag) => ({
                criterion: flag.criterion,
                score: flag.score,
                actionItem: flag.action_item,
              }))}
              pivotTriggered={false}
              pivots={[]}
            />
          )}
        </div>
      )}
    </motion.main>
  )
}
