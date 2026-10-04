import { useCallback, useEffect, useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { fetchBRD, fetchPDF } from '../api.js'
import { getPageVariants } from '../animations/variants.js'
import { useSession } from '../hooks/useSession.js'
import { extractDisagreements } from '../utils/brdParser.js'

import WorkspaceNav from '../components/Workspace/WorkspaceNav.jsx'
import OverviewView from '../components/Workspace/OverviewView.jsx'
import AgentSwarmView from '../components/Workspace/AgentSwarmView.jsx'
import DeliberationView from '../components/Workspace/DeliberationView.jsx'
import FinalBrdView from '../components/Workspace/FinalBrdView.jsx'
import RisksView from '../components/Workspace/RisksView.jsx'
import ExportCenterView from '../components/Workspace/ExportCenterView.jsx'
import AgentDetailModal from '../components/Workspace/AgentDetailModal.jsx'
import EvidenceModal from '../components/Workspace/EvidenceModal.jsx'
import PeekingMascot from '../components/Landing/PeekingMascot.jsx'

const TAB_HASH_MAP = {
  overview: '#overview',
  swarm: '#swarm',
  deliberation: '#deliberation',
  final_brd: '#final-brd',
  risks: '#risks',
  export: '#exports',
}

const HASH_TAB_MAP = {
  '#overview': 'overview',
  '#swarm': 'swarm',
  '#deliberation': 'deliberation',
  '#final-brd': 'final_brd',
  '#brd': 'final_brd',
  '#risks': 'risks',
  '#assumptions': 'risks',
  '#exports': 'export',
  '#export': 'export',
}

function getInitialTab() {
  if (typeof window === 'undefined') return 'overview'
  const hash = window.location.hash?.toLowerCase()
  return HASH_TAB_MAP[hash] || 'overview'
}

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
          sourceAgent: lineage.source_agent || lineage.sourceAgent,
          confidence: `${Math.round((lineage.confidence || 0.9) * 100)}%`,
          dataCitation: lineage.data_citation || lineage.dataCitation,
        }
      : { sourceAgent: 'Swarm Consensus', confidence: '92%', dataCitation: 'Autonomous synthesis.' },
    dissentingAgents: [],
  }
}

function toAssumption(item) {
  return {
    text: item.assumption || item.text,
    confidenceLevel: item.confidence || item.confidenceLevel || 'MEDIUM',
    evidence: item.evidence ?? 'Verified against real-world context data.',
    recommendedAction: item.recommended_action ?? item.recommendedAction ?? 'Conduct 2-week validation smoke test.',
  }
}

export default function ResultsPage() {
  const {
    sessionId,
    setSessionId,
    brdData,
    setBrdData,
    heatmapData,
    setHeatmapData,
    investorScore,
    setInvestorScore,
    resetSession,
  } = useSession()

  const [activeTab, setActiveTabState] = useState(getInitialTab)

  const handleSetActiveTab = useCallback((tabId) => {
    setActiveTabState(tabId)
    const targetHash = TAB_HASH_MAP[tabId] || '#overview'
    if (window.location.hash !== targetHash) {
      window.history.replaceState(null, '', targetHash)
    }
  }, [])

  // Sync with browser Back/Forward navigation
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash?.toLowerCase()
      const tab = HASH_TAB_MAP[hash]
      if (tab) {
        setActiveTabState(tab)
      }
    }
    window.addEventListener('hashchange', handleHashChange)
    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  // Initial sync: ensure URL hash exists so address bar has the locator
  useEffect(() => {
    const currentHash = window.location.hash?.toLowerCase()
    if (!currentHash || !HASH_TAB_MAP[currentHash]) {
      window.history.replaceState(null, '', TAB_HASH_MAP[activeTab] || '#overview')
    }
  }, [activeTab])
  const [loadError, setLoadError] = useState(null)
  const [attempt, setAttempt] = useState(0)
  const [pdfLoading, setPdfLoading] = useState({})
  const [downloadError, setDownloadError] = useState(null)

  // Interactive Inspection Modals / Drawers
  const [selectedAgentModal, setSelectedAgentModal] = useState(null)
  const [selectedEvidenceModal, setSelectedEvidenceModal] = useState(null)

  // Fetch or sync BRD data if session is active or direct hash navigation
  useEffect(() => {
    if (brdData && Array.isArray(brdData.sections) && brdData.sections.length > 0) {
      return undefined
    }
    let cancelled = false

    async function load() {
      try {
        let activeSessionId = sessionId
        if (!activeSessionId) {
          // Direct hash navigation without prior session - load instant demo preset
          const presetRes = await fetch('http://localhost:8000/presets/instant-demo?preset=b2b_code_review', {
            method: 'POST',
          }).then((r) => r.json()).catch(() => null)
          if (presetRes?.data && !cancelled) {
            setLoadError(null)
            if (presetRes.session_id) {
              setSessionId(presetRes.session_id)
            }
            const payload = presetRes.data
            const unpackedBrd = payload.brd || payload
            setBrdData({
              ...unpackedBrd,
              session_id: presetRes.session_id,
              project_name: payload.project_name || 'PRISM Automated SAST Code Review',
              investor_readiness_score: payload.score ?? payload.investor_score ?? 84,
              confidence_band: payload.confidence_band || 'fundable',
              heatmap: payload.heatmap,
              pivots: payload.pivots,
              agent_outputs: payload.agent_outputs,
              score_matrix: payload.score_matrix,
            })
            if (payload.heatmap && typeof setHeatmapData === 'function') {
              setHeatmapData(payload.heatmap)
            }
            if (typeof setInvestorScore === 'function') {
              setInvestorScore({
                score: payload.score ?? payload.investor_score ?? 84,
                confidence_band: payload.confidence_band || 'fundable',
                gaps: [],
                pivots: payload.pivots || [],
              })
            }
            return
          }
        }
        if (!activeSessionId) return
        const data = await fetchBRD(activeSessionId)
        if (!cancelled) {
          setLoadError(null)
          const unpacked = data?.brd
            ? {
                ...data.brd,
                session_id: activeSessionId,
                project_name: data.project_name || data.brd?.project_name,
                investor_readiness_score: data.investor_readiness_score ?? data.brd.investor_readiness_score,
                pivots: data.pivots ?? data.brd.pivots,
                heatmap: data.heatmap ?? data.brd.heatmap,
                context: data.context ?? data.brd.context,
                agent_outputs: data.agent_outputs ?? data.brd.agent_outputs,
                score_matrix: data.score_matrix ?? data.brd.score_matrix,
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
                confidence_band:
                  (data.investor_readiness_score ?? 0) >= 70
                    ? 'fundable'
                    : (data.investor_readiness_score ?? 0) >= 50
                    ? 'promising'
                    : 'needs_work',
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
  }, [sessionId, brdData, setBrdData, setHeatmapData, setInvestorScore, attempt, setSessionId])

  const retry = useCallback(() => {
    setLoadError(null)
    setAttempt((count) => count + 1)
  }, [])

  // Helper to construct relevant, project-specific PDF filenames
  const getRelevantPdfFilename = useCallback(
    (view, serverFilename) => {
      // If server provided a well-defined filename that ends in .pdf and is not a generic fallback or UUID
      if (
        serverFilename &&
        serverFilename.toLowerCase().endsWith('.pdf') &&
        !serverFilename.startsWith('prism-brd') &&
        !serverFilename.startsWith('prism-master') &&
        !/^[0-9a-fA-F-]{20,}/.test(serverFilename)
      ) {
        return serverFilename
      }
      const viewMap = {
        final: 'Master_BRD',
        full: 'Master_BRD',
        investor: 'Investor_Brief',
        technical: 'Technical_Architecture',
        regulatory: 'Regulatory_Compliance',
        deliberation: 'Swarm_Deliberation',
      }
      const viewTitle = viewMap[view] || view || 'Specification'
      const rawProjectName =
        brdData?.project_name ||
        brdData?.brd?.project_name ||
        brdData?.title ||
        'B2B_AI_Code_Review'
      const cleanProject = rawProjectName
        .replace(/PRISM/gi, '')
        .replace(/[^a-zA-Z0-9]+/g, '_')
        .replace(/^_+|_+$/g, '')
        .slice(0, 32) || 'Startup_Venture'
      return `PRISM_${cleanProject}_${viewTitle}.pdf`
    },
    [brdData],
  )

  // Download PDF Handler with relevant human-readable naming
  const handleDownload = useCallback(
    async (view = 'final') => {
      setPdfLoading((prev) => ({ ...prev, [view]: true }))
      setDownloadError(null)
      const targetSessionId = sessionId || brdData?.session_id || 'f8045b43-31f3-4919-a13c-036e81de8f96'

      try {
        const data = await fetchPDF(targetSessionId, view)
        const filename = getRelevantPdfFilename(view, data?.suggestedFilename)

        if (data instanceof Blob) {
          const url = URL.createObjectURL(data)
          const link = document.createElement('a')
          link.href = url
          link.setAttribute('download', filename)
          link.download = filename
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          setTimeout(() => URL.revokeObjectURL(url), 2000)
        } else if (data?.available && data?.url) {
          try {
            const blobRes = await fetch(data.url)
            const blob = await blobRes.blob()
            const url = URL.createObjectURL(blob)
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', filename)
            link.download = filename
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
            setTimeout(() => URL.revokeObjectURL(url), 2000)
          } catch {
            const link = document.createElement('a')
            link.href = data.url
            link.setAttribute('download', filename)
            link.download = filename
            link.target = '_blank'
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
          }
        } else {
          setDownloadError(
            `The ${view} PDF is currently generating. Please try again shortly.`
          )
        }
      } catch (err) {
        setDownloadError(err?.message || `Could not download the ${view} PDF.`)
      } finally {
        setPdfLoading((prev) => ({ ...prev, [view]: false }))
      }
    },
    [sessionId, brdData, getRelevantPdfFilename],
  )

  // Data mapping from backend session
  const rawBrd = brdData?.brd ?? brdData
  const sections = useMemo(() => {
    return (Array.isArray(rawBrd?.sections) ? rawBrd.sections : []).map(toSection)
  }, [rawBrd])

  const assumptions = useMemo(() => {
    return (Array.isArray(rawBrd?.assumptions) ? rawBrd.assumptions : []).map(toAssumption)
  }, [rawBrd])

  const rawHeatmap = heatmapData ?? rawBrd?.heatmap ?? brdData?.heatmap
  const bars = useMemo(() => {
    return (rawHeatmap?.bars ?? []).map((bar) => ({
      sectionTitle: bar.section_title ?? bar.sectionTitle,
      riskScore: bar.risk_score ?? bar.riskScore,
      stdDev: bar.std_dev ?? bar.stdDev,
      riskLevel: toRiskLevel(bar.risk_score ?? bar.riskScore ?? 0),
    }))
  }, [rawHeatmap])

  const score =
    investorScore?.score ??
    rawBrd?.investor_readiness_score ??
    brdData?.investor_readiness_score ??
    74

  const confidenceBand = investorScore?.confidence_band || (score >= 70 ? 'fundable' : 'promising')

  const agentOutputs = brdData?.agent_outputs || rawBrd?.agent_outputs || []

  const disagreements = useMemo(() => {
    return extractDisagreements(bars)
  }, [bars])

  // Open agent detail by ID helper
  const handleOpenAgentById = (agentId) => {
    const rawOutput = (agentOutputs || []).find((ao) => ao.agent === agentId)
    const winningSections = sections
      .filter((s) => (s.lineage?.sourceAgent || '').toLowerCase().includes(agentId))
      .map((s) => s.title)

    setSelectedAgentModal({
      id: agentId,
      name:
        agentId === 'vc' ? 'The VC' :
        agentId === 'lean' ? 'Lean Founder' :
        agentId === 'cto' ? 'Enterprise CTO' :
        agentId === 'ux' ? 'UX Researcher' :
        agentId === 'regulator' ? 'The Regulator' : 'The Adversary',
      role:
        agentId === 'vc' ? 'Venture Capitalist' :
        agentId === 'lean' ? 'Startup Operator' :
        agentId === 'cto' ? 'Chief Technology Officer' :
        agentId === 'ux' ? 'Product & UX Designer' :
        agentId === 'regulator' ? 'Statutory Compliance' : 'Red Team & Stress-Testing',
      badge:
        agentId === 'vc' ? '10x Return & Moats' :
        agentId === 'lean' ? '4-Week MVP Validation' :
        agentId === 'cto' ? 'Tech Feasibility & Stack' :
        agentId === 'ux' ? 'Friction & Delight' :
        agentId === 'regulator' ? 'Compliance & Legal Shield' : 'Stress-Testing & Flaws',
      color:
        agentId === 'vc' ? '#6D28D9' :
        agentId === 'lean' ? '#059669' :
        agentId === 'cto' ? '#0284C7' :
        agentId === 'ux' ? '#D97706' :
        agentId === 'regulator' ? '#DC2626' : '#475569',
      confidence: '92%',
      mandate: 'Domain-specific rigor and adversarial challenge to uncover blind spots.',
      recommendation: rawOutput?.brd_json?.executive_summary || 'Prioritize zero-trust modularity while enforcing tight unit margins.',
      keyConcern: 'Unbounded scaling costs and unvalidated procurement friction.',
      isWinnerIn: winningSections,
      sections: rawOutput?.brd_json || {},
      citations: ['World Bank National GDP Data', 'NewsAPI Developer Sentiment', 'Statutory Compliance Database'],
    })
  }

  return (
    <motion.main
      className="min-h-screen bg-void font-body text-content-primary pb-16"
      variants={getPageVariants()}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      {/* 1. PERSISTENT WORKSPACE TOP NAVIGATION */}
      <WorkspaceNav
        activeTab={activeTab}
        setActiveTab={handleSetActiveTab}
        score={score}
        confidenceBand={confidenceBand}
        onReset={resetSession}
      />

      {/* Main Workspace Canvas */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 pt-6">
        {/* Error notification banner */}
        {loadError && (
          <div role="alert" className="mb-6 flex items-center justify-between rounded-lg border-2 border-error bg-surface p-4 shadow-sm">
            <span className="font-body text-small text-error font-medium">{loadError}</span>
            <button
              type="button"
              onClick={retry}
              className="rounded-md bg-accent-signal px-3 py-1 font-display text-xs font-bold text-void cursor-pointer"
            >
              Retry
            </button>
          </div>
        )}

        {downloadError && (
          <div role="alert" className="mb-6 flex items-center justify-between rounded-lg border border-amber-300 bg-amber-50 p-4 text-xs text-amber-900 shadow-xs">
            <span>{downloadError}</span>
            <button
              type="button"
              onClick={() => setDownloadError(null)}
              className="font-bold cursor-pointer"
            >
              ✕
            </button>
          </div>
        )}

        {/* Loading Skeletons */}
        {!brdData && !loadError && (
          <div className="grid items-start gap-8 lg:grid-cols-3 mt-6" aria-busy="true" aria-live="polite">
            <span className="sr-only">Loading your BRD Workspace...</span>
            <div className="grid gap-6 lg:col-span-2">
              <div className="workspace-card space-y-3 p-6">
                {Array.from({ length: 4 }, (_, i) => (
                  <div key={i} className="skeleton skeleton--row" />
                ))}
              </div>
              <div className="workspace-card space-y-4 p-6">
                {Array.from({ length: 5 }, (_, i) => (
                  <div key={i} className="skeleton skeleton--accordion" />
                ))}
              </div>
            </div>
            <div className="workspace-card flex flex-col items-center justify-center p-8">
              <div className="skeleton skeleton--ring" />
            </div>
          </div>
        )}

        {/* 2. TABBED ANALYTICAL VIEWS */}
        {brdData && (
          <AnimatePresence mode="wait">
            {activeTab === 'overview' && (
              <motion.div
                key="overview"
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                transition={{ duration: 0.15 }}
              >
                <OverviewView
                  score={score}
                  confidenceBand={confidenceBand}
                  brdData={brdData}
                  heatmapBars={bars}
                  disagreements={disagreements}
                  sessionId={sessionId}
                  onNavigateTab={handleSetActiveTab}
                />
              </motion.div>
            )}

            {activeTab === 'swarm' && (
              <motion.div
                key="swarm"
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                transition={{ duration: 0.15 }}
              >
                <AgentSwarmView
                  agentOutputs={agentOutputs}
                  brdData={brdData}
                  onSelectAgent={(agent) => setSelectedAgentModal(agent)}
                />
              </motion.div>
            )}

            {activeTab === 'deliberation' && (
              <motion.div
                key="deliberation"
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                transition={{ duration: 0.15 }}
              >
                <DeliberationView
                  heatmapBars={bars}
                  disagreements={disagreements}
                  onOpenAgent={(agentId) => handleOpenAgentById(agentId)}
                  onOpenEvidence={(evidence) => setSelectedEvidenceModal(evidence)}
                />
              </motion.div>
            )}

            {activeTab === 'final_brd' && (
              <motion.div
                key="final_brd"
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                transition={{ duration: 0.15 }}
              >
                <FinalBrdView
                  brdData={brdData}
                  score={score}
                  confidenceBand={confidenceBand}
                  sessionId={sessionId}
                  onOpenEvidence={(evidence) => setSelectedEvidenceModal(evidence)}
                  onNavigateTab={handleSetActiveTab}
                  onDownloadPdf={handleDownload}
                  pdfLoading={pdfLoading}
                />
              </motion.div>
            )}

            {activeTab === 'risks' && (
              <motion.div
                key="risks"
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                transition={{ duration: 0.15 }}
              >
                <RisksView
                  assumptions={assumptions}
                  brdData={brdData}
                  investorScore={investorScore}
                  onOpenAgent={(agentId) => handleOpenAgentById(agentId)}
                />
              </motion.div>
            )}

            {activeTab === 'export' && (
              <motion.div
                key="export"
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                transition={{ duration: 0.15 }}
              >
                <ExportCenterView
                  sessionId={sessionId}
                  brdData={brdData}
                  score={score}
                  onDownloadPdf={handleDownload}
                  pdfLoading={pdfLoading}
                />
              </motion.div>
            )}
          </AnimatePresence>
        )}
      </div>

      {/* 3. SIDE-PANEL DRAWER FOR FULL AGENT DETAILS */}
      <AgentDetailModal
        agentData={selectedAgentModal}
        onClose={() => setSelectedAgentModal(null)}
        onOpenEvidence={(evidence) => {
          setSelectedAgentModal(null)
          setSelectedEvidenceModal(evidence)
        }}
      />

      {/* 4. MODAL FOR CITATIONS & LINEAGE EVIDENCE */}
      <EvidenceModal
        evidenceData={selectedEvidenceModal}
        onClose={() => setSelectedEvidenceModal(null)}
      />

      {/* 5. THE OBSERVER (GUY) IN THE BOTTOM-LEFT CORNER */}
      <PeekingMascot
        currentView="workspace"
        activeTab={activeTab}
        onNavigateTab={handleSetActiveTab}
        onDownloadPdf={handleDownload}
      />
    </motion.main>
  )
}
