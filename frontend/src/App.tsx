import AppHeader from './components/AppHeader'
import WeekHero from './components/WeekHero'

export default function App() {
  return (
    <>
      <AppHeader />
      <main>
        <WeekHero observationCount={3} />
      </main>
    </>
  )
}