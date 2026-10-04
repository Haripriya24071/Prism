import { useEffect, useState } from 'react'
import { SESSION_STATUS, useSession } from './useSession.js'

export function useSSE(sessionId) {
  const { setStatus, setAgentStatus, setBrdData, failSession } = useSession()
  const [contextReady, setContextReady] = useState(false)
  const [progressPct, setProgressPct] = useState(0)
  const [stageMessage, setStageMessage] = useState('Initializing generation pipeline...')

  useEffect(() => {
    if (!sessionId) {
      return undefined
    }

    const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    const url = `${apiBase}/generate/stream/${sessionId}`
    const source = new EventSource(url)
    let finished = false

    // Context harvest events
    source.addEventListener('context_start', () => {
      setStageMessage('Harvesting real-world context data (NewsAPI, Crunchbase, World Bank)...')
      setProgressPct((prev) => Math.max(prev, 10))
    })

    source.addEventListener('context_ready', () => {
      setContextReady(true)
      setStageMessage('Context harvested. Preparing 6 adversarial agent personas...')
      setProgressPct((prev) => Math.max(prev, 20))
    })

    // Swarm execution events
    source.addEventListener('swarm_start', () => {
      setStatus(SESSION_STATUS.SWARM_RUNNING)
      setStageMessage('6 Swarm Agents are analyzing market, unit economics, tech stack & regulatory risks...')
      setProgressPct((prev) => Math.max(prev, 25))
    })

    source.addEventListener('agent_status', (event) => {
      try {
        const payload = JSON.parse(event.data)
        if (payload?.agent && payload?.status) {
          setAgentStatus(payload.agent, payload.status)
        }
        if (typeof payload?.progress_pct === 'number') {
          setProgressPct((prev) => Math.max(prev, payload.progress_pct))
        }
      } catch {
        // parse error ignored
      }
    })

    source.addEventListener('swarm_complete', () => {
      setStageMessage('All 6 personas completed evaluation. Evaluating against 5-axis rubric...')
      setProgressPct((prev) => Math.max(prev, 68))
    })

    // Evaluation & Merge events
    source.addEventListener('evaluation_start', () => {
      setStatus(SESSION_STATUS.EVALUATING)
      setStageMessage('Gemini Pro scoring agent submissions on feasibility, defensibility & rigor...')
      setProgressPct((prev) => Math.max(prev, 70))
    })

    source.addEventListener('evaluation_complete', (event) => {
      try {
        const payload = JSON.parse(event.data)
        const winner = payload?.winning_agent ? ` (Winning base: ${payload.winning_agent.toUpperCase()})` : ''
        setStageMessage(`Evaluation complete${winner}. Merging best sections into unified BRD...`)
      } catch {
        setStageMessage('Evaluation complete. Merging best sections into unified BRD...')
      }
      setProgressPct((prev) => Math.max(prev, 80))
    })

    source.addEventListener('merge_start', () => {
      setStatus(SESSION_STATUS.MERGING)
      setStageMessage('Transplanting highest-scoring sections with provenance lineage...')
      setProgressPct((prev) => Math.max(prev, 82))
    })

    source.addEventListener('merge_complete', () => {
      setStageMessage('BRD sections merged. Stress-testing assumptions & failure modes...')
      setProgressPct((prev) => Math.max(prev, 88))
    })

    source.addEventListener('analysis_start', () => {
      setStageMessage('Generating divergence heatmap & investor readiness score...')
      setProgressPct((prev) => Math.max(prev, 89))
    })

    // Generic progress event
    source.addEventListener('progress', (event) => {
      try {
        const payload = JSON.parse(event.data)
        if (typeof payload?.progress_pct === 'number') {
          setProgressPct((prev) => Math.max(prev, payload.progress_pct))
        }
      } catch {
        // parse error ignored
      }
    })

    // Final BRD Ready event
    source.addEventListener('brd_ready', (event) => {
      finished = true
      try {
        const payload = JSON.parse(event.data)
        if (payload && Array.isArray(payload.sections) && payload.sections.length > 0) {
          setBrdData(payload)
        }
      } catch {
        // parse error ignored
      }
      setStageMessage('BRD and Investor Readiness Score locked! Launching Results...')
      setProgressPct(100)
      setStatus(SESSION_STATUS.COMPLETE)
    })

    // Error event
    source.addEventListener('error', (event) => {
      if (finished) return
      try {
        if (event.data) {
          const payload = JSON.parse(event.data)
          if (payload?.message) {
            finished = true
            source.close()
            failSession(payload.message)
            return
          }
        }
      } catch {
        // ignore
      }
    })

    // Done signal from server
    source.addEventListener('done', () => {
      finished = true
      source.close()
    })

    // Fallback message handler for SSE streams without explicit event names
    source.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data)
        const eventType = payload?.event
        const data = payload?.data || payload

        if (eventType === 'done') {
          finished = true
          source.close()
          return
        }
        if (eventType === 'brd_ready') {
          finished = true
          if (data && Array.isArray(data.sections) && data.sections.length > 0) {
            setBrdData(data)
          }
          setStageMessage('BRD and Investor Readiness Score locked! Launching Results...')
          setProgressPct(100)
          setStatus(SESSION_STATUS.COMPLETE)
          return
        }
        if (eventType === 'error') {
          finished = true
          source.close()
          failSession(data?.message || 'Pipeline generation failed.')
          return
        }
        if (eventType === 'agent_status' && data?.agent && data?.status) {
          setAgentStatus(data.agent, data.status)
        }
        if (typeof data?.progress_pct === 'number') {
          setProgressPct((prev) => Math.max(prev, data.progress_pct))
        }
      } catch {
        // ignore
      }
    }

    source.onerror = () => {
      source.close()
      if (!finished) {
        failSession('Lost connection to the generation stream. Please retry.')
      }
    }

    return () => {
      source.close()
    }
  }, [sessionId, setStatus, setAgentStatus, setBrdData, failSession])

  return { contextReady, progressPct, stageMessage }
}
