import { useCallback, useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { fetchBRD, fetchPDF } from '../api.js'
import { getPageVariants } from '../animations/variants.js'
import BRDViewer from '../components/BRDViewer/BRDViewer.jsx'
import RealWorldContextRadar from '../components/BRDViewer/RealWorldContextRadar.jsx'
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
  const {
    sessionId,
    brdData,
    setBrdData,
    heatmapData,
    setHeatmapData,
    investorScore,
    setInvestorScore,
  } = useSession()
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
          // Unpack res.brd if wrapped while preserving score and metadata
          const unpacked = data?.brd
            ? {
                ...data.brd,
                investor_readiness_score: data.investor_readiness_score ?? data.brd.investor_readiness_score,
                pivots: data.pivots ?? data.brd.pivots,
                heatmap: data.heatmap ?? data.brd.heatmap,
                context: data.context ?? data.brd.context,
              }
            : data
          setBrdData(unpacked)

          if (data?.heatmap && typeof setHeatmapData === 'function') {
            setHeatmapData(data.heatmap)
          }
          if ((data?.investor_score || data?.investor_readiness_score !== undefined) && typeof setInvestorScore === 'function') {
            setInvestorScore(
              data.investor_score ?? {
                score: data.investor_readiness_score ?? 0,
                confidence_band: (data.investor_readiness_score ?? 0) >= 70 ? 'fundable' : (data.investor_readiness_score ?? 0) >= 50 ? 'promising' : 'needs_work',
                gaps: [],
                pivots: data.pivots ?? [],
              }
            )
          }
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
  }, [sessionId, brdData, setBrdData, setHeatmapData, setInvestorScore, attempt])

  const retry = useCallback(() => {
    setLoadError(null)
    setAttempt((count) => count + 1)
  }, [])

  const handleDownload = useCallback(
    async (view) => {
      setDownloadingView(view)
      setDownloadError(null)
      try {
        const data = await fetchPDF(sessionId, view)
        if (data instanceof Blob) {
          const url = URL.createObjectURL(data)
          const link = document.createElement('a')
          link.href = url
          link.download = `prism-brd-${view}.pdf`
          document.body.appendChild(link)
          link.click()
          link.remove()
          URL.revokeObjectURL(url)
        } else if (data?.available && data?.url) {
          if (data.url.startsWith('http://') || data.url.startsWith('https://')) {
            window.open(data.url, '_blank', 'noopener,noreferrer')
          } else {
            const link = document.createElement('a')
            link.href = data.url
            link.download = `prism-brd-${view}.pdf`
            link.target = '_blank'
            document.body.appendChild(link)
            link.click()
            link.remove()
          }
        } else {
          setDownloadError(
            `The ${view} PDF is currently generating. Please try again shortly.`
          )
        }
      } catch (err) {
        setDownloadError(err?.message || `Could not download the ${view} PDF.`)
      } finally {
        setDownloadingView(null)
      }
    },
    [sessionId],
  )

  const rawBrd = brdData?.brd ?? brdData
  const sections = (rawBrd?.sections ?? []).map(toSection)
  const assumptions = (rawBrd?.assumptions ?? []).map(toAssumption)
  const rawHeatmap = heatmapData ?? rawBrd?.heatmap ?? brdData?.heatmap
  const bars = (rawHeatmap?.bars ?? []).map((bar) => ({
    sectionTitle: bar.section_title ?? bar.sectionTitle,
    riskScore: bar.risk_score ?? bar.riskScore,
    stdDev: bar.std_dev ?? bar.stdDev,
    riskLevel: toRiskLevel(bar.risk_score ?? bar.riskScore ?? 0),
  }))
  const score =
    investorScore?.score ??
    rawBrd?.investor_readiness_score ??
    brdData?.investor_readiness_score ??
    null

  const pivotSuggestions =
    investorScore?.pivot_suggestions ??
    investorScore?.pivotSuggestions ??
    investorScore?.pivots ??
    rawBrd?.pivot_suggestions ??
    rawBrd?.pivotSuggestions ??
    rawBrd?.pivots ??
    brdData?.pivot_suggestions ??
    brdData?.pivotSuggestions ??
    brdData?.pivots ??
    []

  const pivotTriggered = Boolean(
    investorScore?.pivot_triggered ??
    investorScore?.pivotTriggered ??
    rawBrd?.pivot_triggered ??
    brdData?.pivot_triggered ??
    (score !== null && score < 60 && pivotSuggestions.length > 0)
  )

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
            {(rawBrd?.context || brdData?.context) && (
              <RealWorldContextRadar context={rawBrd?.context || brdData?.context} />
            )}
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
              pivotTriggered={pivotTriggered}
              pivots={pivotSuggestions}
              pivotSuggestions={pivotSuggestions}
            />
          )}
        </div>
      )}
    </motion.main>
  )
}
