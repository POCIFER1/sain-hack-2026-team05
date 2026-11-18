import { ArrowRight } from 'lucide-react'

import './WeekHero.css'
import WeekWave from './WeekWave'
import WeekAnalysis from './WeekAnalysis'


const pluralRules = new Intl.PluralRules('ru')

function formatObservations(count: number) {
  switch (pluralRules.select(count)) {
    case 'one':
      return `${count} новое наблюдение`
    case 'few':
      return `${count} новых наблюдения`
    default:
      return `${count} новых наблюдений`
  }
}

type WeekHeroProps = {
  observationCount: number
}

export default function WeekHero({ observationCount }: WeekHeroProps) {
  return (
    <section className="week-hero" aria-labelledby="week-title">
      <WeekWave />
      <div className="week-hero__content">
        <h1 id="week-title">Твоя неделя</h1>
        <p>{formatObservations(observationCount)}</p>
        <WeekAnalysis />
      </div>
    </section>
  )
}