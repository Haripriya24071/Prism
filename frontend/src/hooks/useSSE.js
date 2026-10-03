import { useEffect, useState } from 'react'
import { SESSION_STATUS, useSession } from './useSession.js'

export function useSSE(sessionId) {
  const { setStatus, setAgentStatus, setBrdData, failSession } = useSession()
  const [contextReady, setContextReady] = useState(false)
  const [progressPct, setProgressPct] = useState(0)

  useEffect(() => {
    if (!sessionId) {
      return undefined
    }

    const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    const url = `${apiBase}/generate/stream/${sessionId}`
    const source = new EventSource(url)

    source.addEventListener('agent_status', (event) => {
      try {
        const payload = JSON.parse(event.data)
        if (payload?.agent && payload?.status) {
          setAgentStatus(payload.agent, payload.status)
        }
        if (typeof payload?.progress_pct === 'number') {
          setProgressPct(payload.progress_pct)
        }
      } catch {
        // parse error ignored
      }
    })

    source.addEventListener('progress', (event) => {
      try {
        const payload = JSON.parse(event.data)
        if (typeof payload?.progress_pct === 'number') {
          setProgressPct(payload.progress_pct)
        }
      } catch {
        // parse error ignored
      }
    })

    source.addEventListener('context_ready', () => {
      setContextReady(true)
      setStatus(SESSION_STATUS.HARVESTING)
    })

    source.addEventListener('evaluation_complete', () => {
      setStatus(SESSION_STATUS.EVALUATING)
    })

    source.addEventListener('brd_ready', (event) => {
      try {
        const payload = JSON.parse(event.data)
        setBrdData(payload)
      } catch {
        // parse error ignored
      }
      setProgressPct(100)
      setStatus(SESSION_STATUS.COMPLETE)
    })

    source.onerror = (err) => {
      failSession(err?.message || 'SSE connection failed')
      source.close()
    }

    return () => {
      source.close()
    }
  }, [sessionId, setStatus, setAgentStatus, setBrdData, failSession])

  return { contextReady, progressPct }
}
