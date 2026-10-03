import { AnimatePresence } from 'framer-motion'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/tokens.css'
import './index.css'
import { SESSION_STATUS, SessionProvider, useSession } from './hooks/useSession.js'
import GenerationPage from './pages/GenerationPage.jsx'
import IntakePage from './pages/IntakePage.jsx'
import ResultsPage from './pages/ResultsPage.jsx'

function renderPage(status) {
  switch (status) {
    case SESSION_STATUS.HARVESTING:
    case SESSION_STATUS.SWARM_RUNNING:
    case SESSION_STATUS.EVALUATING:
    case SESSION_STATUS.MERGING:
      return <GenerationPage key="generation" />
    case SESSION_STATUS.COMPLETE:
      return <ResultsPage key="results" />
    case SESSION_STATUS.IDLE:
    case SESSION_STATUS.INTAKE:
    case SESSION_STATUS.FAILED:
    default:
      return <IntakePage key="intake" />
  }
}

function PageRouter() {
  const { status } = useSession()

  return <AnimatePresence mode="wait">{renderPage(status)}</AnimatePresence>
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <SessionProvider>
      <PageRouter />
    </SessionProvider>
  </StrictMode>,
)
