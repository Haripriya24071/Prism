import { useState } from 'react'
import { parseRequirements } from '../../utils/brdParser.js'
import './Workspace.css'

export default function ExportCenterView({
  sessionId,
  brdData,
  score,
  onDownloadPdf,
  pdfLoading = {},
}) {
  const [copiedType, setCopiedType] = useState(null)

  const rawBrd = brdData?.brd ?? brdData
  const sections = Array.isArray(rawBrd?.sections) ? rawBrd.sections : []
  const requirements = parseRequirements(sections)
  const projectName = brdData?.project_name || 'PRISM Autonomous Specification'

  // Jira Backlog / Markdown Export
  const handleExportJira = () => {
    let jira = `h1. PRISM Requirements Backlog - ${projectName}\n\n`
    requirements.forEach((req) => {
      jira += `h2. [${req.priority}] ${req.id}: ${req.title}\n`
      jira += `*Type:* ${req.type}\n`
      jira += `*Priority:* ${req.priority}\n`
      jira += `*Consensus:* ${req.consensus}\n`
      jira += `*Source Persona:* ${req.source}\n\n`
      jira += `*Description:*\n${req.description}\n\n`
      jira += `*Architectural Rationale:*\n${req.rationale}\n\n`
      jira += `----\n\n`
    })

    navigator.clipboard.writeText(jira)
    setCopiedType('jira')
    setTimeout(() => setCopiedType(null), 3000)
  }

  const exportCards = [
    {
      id: 'final',
      title: 'Complete Master BRD',
      format: 'Full PDF Document',
      badge: 'Unabridged Master',
      description: 'The authoritative, end-to-end specification containing all sections, executive summary, complete requirements table, risk matrix, and consensus metrics.',
      actionText: pdfLoading.final ? 'Generating Master PDF...' : '📥 Download Complete BRD (PDF)',
      isPrimary: true,
      onClick: () => onDownloadPdf?.('final'),
      loading: pdfLoading.final,
    },
    {
      id: 'investor',
      title: 'Investor Evaluation BRD',
      format: 'PDF Document',
      badge: 'Commercial & Moats',
      description: 'Executive brief, addressable market size, unit economics, defensible competitive moat, and capital allocation risks.',
      actionText: pdfLoading.investor ? 'Rendering PDF...' : 'Download Investor PDF',
      isPrimary: false,
      onClick: () => onDownloadPdf?.('investor'),
      loading: pdfLoading.investor,
    },
    {
      id: 'technical',
      title: 'Technical Architecture BRD',
      format: 'PDF Document',
      badge: 'Systems & Stack',
      description: 'System topology, container isolation, database scaling bottlenecks, API latency boundaries, and functional requirements.',
      actionText: pdfLoading.technical ? 'Rendering PDF...' : 'Download Technical PDF',
      isPrimary: false,
      onClick: () => onDownloadPdf?.('technical'),
      loading: pdfLoading.technical,
    },
    {
      id: 'regulatory',
      title: 'Regulatory & Governance BRD',
      format: 'PDF Document',
      badge: 'Compliance Shield',
      description: 'SOC2 Type II controls, data sovereignty boundaries, PII tokenization, audit trails, and statutory liability protections.',
      actionText: pdfLoading.regulatory ? 'Rendering PDF...' : 'Download Regulatory PDF',
      isPrimary: false,
      onClick: () => onDownloadPdf?.('regulatory'),
      loading: pdfLoading.regulatory,
    },
    {
      id: 'deliberation',
      title: 'Swarm Deliberation Report',
      format: 'PDF Document',
      badge: 'Adversarial Dialectics',
      description: 'Full record of all six agents\' independent positions, contested battleground arguments, and PRISM synthesis rationales.',
      actionText: pdfLoading.deliberation ? 'Rendering PDF...' : 'Download Deliberation PDF',
      isPrimary: false,
      onClick: () => onDownloadPdf?.('deliberation'),
      loading: pdfLoading.deliberation,
    },
    {
      id: 'jira',
      title: 'Jira / Linear Backlog',
      format: 'Clipboard Export',
      badge: 'Sprint Import',
      description: 'Formatted user stories with requirement IDs (FR/TR/SEC), priorities (P0/P1), and source persona tags ready for Jira or Linear import.',
      actionText: copiedType === 'jira' ? '✓ Copied to Clipboard!' : 'Copy Jira User Stories',
      isPrimary: false,
      onClick: handleExportJira,
      loading: false,
    },
  ]

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="workspace-card p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs px-2 py-0.5 rounded bg-surface-raised border border-border-subtle text-content-secondary">
              Artifact Publishing Hub
            </span>
            <span className="font-mono text-xs text-content-muted">
              ReportLab Engine
            </span>
          </div>
          <h2 className="font-display font-bold text-xl text-content-primary mt-1">
            Stakeholder Export Center
          </h2>
          <p className="font-body text-xs text-content-secondary max-w-2xl mt-1">
            Download the complete master document or targeted stakeholder perspectives formatted directly for investors, architects, and compliance officers.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="font-mono text-xs px-2.5 py-1 rounded bg-surface-raised border border-border text-content-secondary">
            Score: {score ?? 74}/100
          </span>
          <span className="font-mono text-xs px-2.5 py-1 rounded bg-surface-raised border border-border text-content-secondary">
            Session: {sessionId ? sessionId.slice(0, 8) : 'ACTIVE'}
          </span>
        </div>
      </div>

      {/* 6 Dedicated Export Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {exportCards.map((card) => (
          <div
            key={card.id}
            className="export-card space-y-4"
          >
            <div>
              {/* Header */}
              <div className="flex items-start justify-between gap-2 pb-2.5 border-b border-border-subtle">
                <div>
                  <span className="font-mono text-micro text-content-muted block">
                    {card.format}
                  </span>
                  <h3 className="font-display font-bold text-base text-content-primary mt-0.5">
                    {card.title}
                  </h3>
                </div>
                <span className="font-mono text-[10px] px-2 py-0.5 rounded bg-surface-raised border border-border-subtle text-content-secondary shrink-0">
                  {card.badge}
                </span>
              </div>

              {/* Description */}
              <p className="font-body text-xs text-content-secondary leading-relaxed mt-2.5">
                {card.description}
              </p>
            </div>

            {/* Action Button */}
            <div className="pt-3 border-t border-border-subtle">
              <button
                type="button"
                onClick={card.onClick}
                disabled={card.loading}
                className={`w-full inline-flex items-center justify-center gap-1.5 font-display text-xs font-semibold py-2 px-3 rounded border transition-all cursor-pointer ${
                  card.isPrimary
                    ? 'border-accent-signal bg-accent-signal text-void hover:opacity-90 shadow-xs'
                    : 'border-border bg-surface hover:bg-surface-raised text-content-primary shadow-xs'
                } ${card.loading ? 'opacity-60 cursor-not-allowed' : ''}`}
              >
                <span>{card.actionText}</span>
                {!card.loading && <span className="text-xs">→</span>}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Document Guarantee Notice */}
      <div className="workspace-card p-4 bg-surface-raised flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div className="space-y-0.5">
          <span className="font-semibold text-content-primary">
            🛡️ Production-Grade Artifact Guarantee
          </span>
          <p className="font-body text-content-secondary">
            All PDF exports include page numbers, running headers, confidentiality notices, and structured requirement registers formatted directly for enterprise stakeholders.
          </p>
        </div>
        <span className="font-mono text-[11px] text-content-muted whitespace-nowrap">
          ReportLab Two-Pass Engine
        </span>
      </div>
    </div>
  )
}
