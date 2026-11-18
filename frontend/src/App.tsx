import AppHeader from './components/AppHeader'
import WeekHero from './components/WeekHero'
import WeekMetrics from './components/WeekMetrics'

export default function App() {
  return (
    <>
      <AppHeader />
      <main>
        <WeekHero observationCount={3} />
        <WeekMetrics />
      </main>
    </>
  )
}