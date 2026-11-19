import { useState, useSyncExternalStore } from 'react'

import AppHeader from './components/AppHeader'
import WeekHero from './components/WeekHero'
import WeekMetrics from './components/WeekMetrics'
import { ResultOverview, ResultSummary } from './components/WeeklyResult'

function subscribeToHash(onChange: () => void) {
  window.addEventListener('hashchange', onChange)
  return () => window.removeEventListener('hashchange', onChange)
}

function getPage() {
  return window.location.hash === '#/week-result' ? 'result' : 'home'
}

export default function App() {
  const page = useSyncExternalStore(subscribeToHash, getPage)
  const isResult = page === 'result'
  const [detailsOpen, setDetailsOpen] = useState(
    () => window.matchMedia('(min-width: 1000px)').matches,
  )

  function showDetails() {
    setDetailsOpen(true)
    requestAnimationFrame(() => {
      document.getElementById('result-summary-title')?.focus()
    })
  }

  function closeDetails() {
    setDetailsOpen(false)
    document.getElementById('result-details-trigger')?.focus()
  }

  return (
    <>
      <AppHeader page={page} />

      <main
        className={isResult ? 'result-layout' : undefined}
        data-details-open={isResult && detailsOpen}
      >
        {isResult && detailsOpen && <ResultSummary onClose={closeDetails} />}

        <div className={isResult ? 'result-main' : undefined}>
          {isResult ? (
            <ResultOverview detailsOpen={detailsOpen} onDetails={showDetails} />
          ) : (
            <WeekHero observationCount={3} />
          )}

          <WeekMetrics showHeading={isResult} />
        </div>
      </main>
    </>
  )
}