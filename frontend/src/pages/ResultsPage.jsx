import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { fetchBRD, fetchPDF } from '../api.js'
import { getPageVariants } from '../animations/variants.js'
import BRDViewer from '../components/BRDViewer/BRDViewer.jsx'
import DivergenceHeatmap from '../components/DivergenceHeatmap/DivergenceHeatmap.jsx'
import ScoreCard from '../components/ScoreCard/ScoreCard.jsx'
import { SESSION_STATUS, useSession } from '../hooks/useSession.js'

export default function ResultsPage() {
  const { sessionId, brdData, setBrdData, status, failSession } = useSession()
  const [loading, setLoading] = useState(!brdData)
  const [downloadingView, setDownloadingView] = useState(null)
  const [downloadError, setDownloadError] = useState(null)

  useEffect(() => {
    async function loadData() {
      if (!sessionId) return
      try {
        setLoading(true)
        const data = await fetchBRD(sessionId)
        setBrdData(data)
      } catch (err) {
        failSession(err?.message || 'Failed to fetch BRD data')
      } finally {
        setLoading(false)
      }
    }

    if (!brdData && sessionId) {
      loadData()
    }
  }, [sessionId, brdData, setBrdData, failSession])

  const handleDownloadPDF = async (view) => {
    if (!sessionId) return
    setDownloadingView(view)
    setDownloadError(null)

    try {
      const blob = await fetchPDF(sessionId, view)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `PRISM_BRD_${view}_${sessionId.slice(0, 8)}.pdf`
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      setDownloadError(`Failed to download ${view} PDF: ${err?.message || 'Error'}`)
    } finally {
      setDownloadingView(null)
    }
  }

  // Parse sections for BRDViewer
  const rawSections = brdData?.sections || {}
  const sectionsList = Object.entries(rawSections).map(([key, val]) => ({
    title: key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
    content: val?.content || '',
    lineage: {
      sourceAgent: val?.source_agent || val?.sourceAgent || 'vc',
      confidence: val?.confidence_score ?? val?.confidence ?? 85,
      dataCitation: Array.isArray(val?.data_citations)
        ? val.data_citations.join('; ')
        : val?.dataCitation || '',
    },
    dissentingAgents: (val?.dissenting_agents || val?.dissentingAgents || []).map((d) => ({
      agent: d.agent,
      note: d.key_disagreement || d.note || '',
    })),
  }))

  // Extract all assumptions across sections or from root
  const allAssumptions = (brdData?.assumptions || []).concat(
    Object.values(rawSections).flatMap((s) => s?.assumptions || []),
  ).map((a) => ({
    text: a.text || a.assumption || '',
    confidenceLevel: a.confidence || a.confidenceLevel || 'medium',
    evidence: a.evidence || '',
    recommendedAction: a.action || a.recommendedAction || '',
  }))

  // Format heatmap bars
  const heatmapBars = (brdData?.heatmap?.bars || brdData?.heatmap_data || []).length > 0
    ? (brdData?.heatmap?.bars || brdData?.heatmap_data)
    : Object.keys(rawSections).map((key, i) => ({
        sectionTitle: key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
        riskScore: 25 + (i * 10) % 50, // deterministic fallback
        stdDev: 4.2,
        riskLevel: 'low',
      }))

  // Score details
  const investorScore = brdData?.investor_readiness_score ?? brdData?.score ?? 78
  const gapFlags = (brdData?.investor_readiness_gaps || brdData?.gaps || []).map((gap, i) => ({
    criterion: typeof gap === 'string' ? `Gap ${i + 1}` : gap.criterion,
    score: typeof gap === 'string' ? '' : gap.score,
    actionItem: typeof gap === 'string' ? gap : gap.actionItem,
  }))

  const pivots = (brdData?.pivot_suggestions || []).map((p) => ({
    direction: p.title || p.direction,
    projectedScore: p.projected_score || p.projectedScore,
  }))

  return (
    <motion.main
      className="min-h-screen bg-void p-8 font-body text-content-primary max-w-6xl mx-auto flex flex-col gap-8"
      variants={getPageVariants()}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-border pb-6">
        <div>
          <h1 className="font-display text-h1 font-bold text-content-primary">
            PRISM Results: Final BRD
          </h1>
          <p className="font-body text-content-secondary mt-1">
            Consolidated business requirements synthesized across 6 AI swarm evaluations.
          </p>
        </div>

        {/* PDF Download buttons */}
        <div className="flex flex-wrap gap-2">
          {['investor', 'technical', 'regulatory'].map((view) => (
            <button
              key={view}
              type="button"
              disabled={downloadingView !== null}
              onClick={() => handleDownloadPDF(view)}
              className="px-3 py-2 bg-surface-raised border border-border hover:border-accent-signal rounded-md font-body text-small text-content-primary flex items-center gap-2 transition"
            >
              <span>{downloadingView === view ? 'Downloading...' : `Download ${view.toUpperCase()} PDF`}</span>
            </button>
          ))}
        </div>
      </header>

      {downloadError && (
        <div role="alert" className="p-3 bg-surface rounded-md border border-error text-error font-body text-small">
          {downloadError}
        </div>
      )}

      {status === SESSION_STATUS.FAILED && (
        <div role="alert" className="p-4 bg-surface rounded-md border border-error text-error font-body text-small">
          An error occurred loading the final results.
        </div>
      )}

      {loading ? (
        <div className="py-20 flex justify-center items-center">
          <p className="font-display text-h3 text-content-secondary animate-pulse">
            Loading consolidated BRD...
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
          {/* Left 2 Cols: Heatmap and BRD Document */}
          <div className="lg:col-span-2 flex flex-col gap-8">
            <section className="p-6 bg-surface border border-border rounded-lg">
              <h2 className="font-display text-h2 font-semibold mb-4 text-content-primary">
                Divergence Heatmap
              </h2>
              <DivergenceHeatmap bars={heatmapBars} />
            </section>

            <section className="p-6 bg-surface border border-border rounded-lg">
              <h2 className="font-display text-h2 font-semibold mb-4 text-content-primary">
                Consolidated Requirements Document
              </h2>
              <BRDViewer sections={sectionsList} assumptions={allAssumptions} />
            </section>
          </div>

          {/* Right 1 Col: ScoreCard */}
          <div className="lg:col-span-1">
            <ScoreCard
              score={investorScore}
              confidenceBand="Grounded Validation Tier"
              gapFlags={gapFlags}
              pivotTriggered={brdData?.pivot_triggered ?? false}
              pivots={pivots}
            />
          </div>
        </div>
      )}
    </motion.main>
  )
}
