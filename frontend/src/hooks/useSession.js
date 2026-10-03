import { createContext, createElement, useCallback, useContext, useMemo, useReducer } from 'react'

export const SESSION_STATUS = Object.freeze({
  IDLE: 'idle',
  INTAKE: 'intake',
  HARVESTING: 'harvesting',
  SWARM_RUNNING: 'swarm_running',
  EVALUATING: 'evaluating',
  MERGING: 'merging',
  COMPLETE: 'complete',
  FAILED: 'failed',
})

const ACTIONS = Object.freeze({
  SET_SESSION_ID: 'set_session_id',
  SET_STATUS: 'set_status',
  SET_AGENT_STATUS: 'set_agent_status',
  SET_BRD: 'set_brd',
  SET_HEATMAP: 'set_heatmap',
  SET_INVESTOR_SCORE: 'set_investor_score',
  FAIL: 'fail',
  RESET: 'reset',
})

function createInitialState() {
  return {
    sessionId: null,
    status: SESSION_STATUS.IDLE,
    error: null,
    agentStatuses: {},
    brdData: null,
    heatmapData: null,
    investorScore: null,
  }
}

function sessionReducer(state, action) {
  switch (action.type) {
    case ACTIONS.SET_SESSION_ID:
      return { ...state, sessionId: action.sessionId }
    case ACTIONS.SET_STATUS:
      return { ...state, status: action.status, error: null }
    case ACTIONS.SET_AGENT_STATUS:
      return {
        ...state,
        agentStatuses: { ...state.agentStatuses, [action.agent]: action.agentStatus },
      }
    case ACTIONS.SET_BRD:
      return { ...state, brdData: action.brdData }
    case ACTIONS.SET_HEATMAP:
      return { ...state, heatmapData: action.heatmapData }
    case ACTIONS.SET_INVESTOR_SCORE:
      return { ...state, investorScore: action.investorScore }
    case ACTIONS.FAIL:
      return { ...state, status: SESSION_STATUS.FAILED, error: action.error }
    case ACTIONS.RESET:
      return createInitialState()
    default:
      return state
  }
}

const SessionContext = createContext(null)

export function SessionProvider({ children }) {
  const [state, dispatch] = useReducer(sessionReducer, undefined, createInitialState)

  const setSessionId = useCallback((sessionId) => dispatch({ type: ACTIONS.SET_SESSION_ID, sessionId }), [])
  const setStatus = useCallback((status) => dispatch({ type: ACTIONS.SET_STATUS, status }), [])
  const setAgentStatus = useCallback(
    (agent, agentStatus) => dispatch({ type: ACTIONS.SET_AGENT_STATUS, agent, agentStatus }),
    [],
  )
  const setBrdData = useCallback((brdData) => dispatch({ type: ACTIONS.SET_BRD, brdData }), [])
  const setHeatmapData = useCallback(
    (heatmapData) => dispatch({ type: ACTIONS.SET_HEATMAP, heatmapData }),
    [],
  )
  const setInvestorScore = useCallback(
    (investorScore) => dispatch({ type: ACTIONS.SET_INVESTOR_SCORE, investorScore }),
    [],
  )
  const failSession = useCallback((error) => dispatch({ type: ACTIONS.FAIL, error }), [])
  const resetSession = useCallback(() => dispatch({ type: ACTIONS.RESET }), [])

  const value = useMemo(
    () => ({
      ...state,
      setSessionId,
      setStatus,
      setAgentStatus,
      setBrdData,
      setHeatmapData,
      setInvestorScore,
      failSession,
      resetSession,
    }),
    [state, setSessionId, setStatus, setAgentStatus, setBrdData, setHeatmapData, setInvestorScore, failSession, resetSession],
  )

  return createElement(SessionContext.Provider, { value }, children)
}

export function useSession() {
  const context = useContext(SessionContext)
  if (context === null) {
    throw new Error('useSession must be used inside a SessionProvider')
  }
  return context
}
