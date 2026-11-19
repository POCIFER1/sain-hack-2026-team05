import {
  Armchair,
  ArrowRight,
  ChartNoAxesColumnIncreasing,
  ChevronRight,
  Clock3,
  Droplet,
  Footprints,
  History,
  Moon,
  Sun,
  X,
  Zap,
} from 'lucide-react'

import WeekWave from './WeekWave'
import './WeeklyResult.css'

const changes = [
  { title: 'Сон', text: 'Улучшение · +32 мин', icon: Moon, tone: 'good' },
  { title: 'Активность', text: 'Улучшение · +12%', icon: Zap, tone: 'good' },
  { title: 'Сидячее время', text: '−18 мин', icon: Armchair, tone: 'neutral' },
  { title: 'Режим сна', text: 'Требует внимания', icon: Clock3, tone: 'attention' },
  { title: 'Хронотип', text: 'Без изменений', icon: Sun, tone: 'neutral' },
]

const tips = [
  { icon: Moon, text: 'Попробуй выбрать удобное время отхода ко сну и придерживаться его в течение недели.' },
  { icon: Footprints, text: 'Добавь короткую прогулку днём. Начни с 10–15 минут в удобное время.' },
  { icon: Droplet, text: 'Держи воду под рукой во время работы или прогулки.' },
]

export function ResultSummary({ onClose }: { onClose: () => void }) {
  return (
    <aside
      className="result-summary"
      id="result-summary"
      aria-labelledby="result-summary-title"
    >
      <div className="result-summary__header">
        <h2 id="result-summary-title" tabIndex={-1}>Результат недели</h2>
        <button type="button" aria-label="Закрыть сводку" onClick={onClose}>
          <X aria-hidden="true" />
        </button>
      </div>

      <div className="result-summary__status">
        <span className="result-summary__orb" aria-hidden="true" />
        <div>
          <small>Общая динамика</small>
          <strong>Положительная</strong>
          <small>2 улучшения, 1 требует внимания</small>
        </div>
      </div>

      <h3>Изменения по показателям</h3>
      <ul className="result-changes">
        {changes.map(({ title, text, icon: Icon, tone }) => (
          <li key={title} data-tone={tone}>
            <span className="result-icon">
              <Icon aria-hidden="true" />
            </span>
            <div>
              <strong>{title}</strong>
              <small>{text}</small>
            </div>
            <span className="result-changes__dot" aria-hidden="true" />
          </li>
        ))}
      </ul>

      <button className="result-history" type="button" disabled>
        <History aria-hidden="true" />
        История изменений
        <ChevronRight aria-hidden="true" />
      </button>
    </aside>
  )
}

type ResultOverviewProps = {
  detailsOpen: boolean
  onDetails: () => void
}

export function ResultOverview({ detailsOpen, onDetails }: ResultOverviewProps) {
  return (
    <>
      <section className="result-hero" aria-labelledby="result-title">
        <WeekWave />

        <div className="result-hero__content">
          <p className="result-hero__label">Результат недели</p>
          <h1 id="result-title">Ты стал активнее</h1>
          <p className="result-hero__description">
            Общая динамика положительная. Есть 2 новых наблюдения,
            которые стоит изучить.
          </p>
          <button
            id="result-details-trigger"
            className="week-hero__action week-analysis-trigger"
            type="button"
            aria-expanded={detailsOpen}
            onClick={onDetails}
          >
            <ChartNoAxesColumnIncreasing aria-hidden="true" />
            Посмотреть детали
            <ArrowRight aria-hidden="true" />
          </button>
        </div>
      </section>

      <section className="result-tips" aria-labelledby="result-tips-title">
        <h2 id="result-tips-title">Наши советы для тебя</h2>
        <ul>
          {tips.map(({ icon: Icon, text }) => (
            <li key={text}>
              <span className="result-icon">
                <Icon aria-hidden="true" />
              </span>
              <p>{text}</p>
            </li>
          ))}
        </ul>
      </section>
    </>
  )
}