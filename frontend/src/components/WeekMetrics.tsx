import {
  Armchair,
  ArrowDown,
  ArrowUp,
  Ellipsis,
  Minus,
  Moon,
  Sun,
  Zap,
  type LucideIcon,
} from 'lucide-react'

import './WeekMetrics.css'

type Metric = {
  id: string
  title: string
  value: string
  icon: LucideIcon
  change: {
    text: string
    direction: 'up' | 'down' | 'stable'
    highlighted: boolean
  }
}

const weeklyMetrics: Metric[] = [
  {
    id: 'sleep',
    title: 'Сон',
    value: '7 ч 42 мин',
    icon: Moon,
    change: { text: '+32 мин', direction: 'up', highlighted: true },
  },
  {
    id: 'activity',
    title: 'Активность',
    value: '8 420 шагов',
    icon: Zap,
    change: { text: '+12%', direction: 'up', highlighted: true },
  },
  {
    id: 'sedentary-time',
    title: 'Сидячее время',
    value: '6 ч 20 мин',
    icon: Armchair,
    change: { text: '−18 мин', direction: 'down', highlighted: false },
  },
  {
    id: 'chronotype',
    title: 'Хронотип',
    value: 'Вечерний',
    icon: Sun,
    change: { text: 'Без изменений', direction: 'stable', highlighted: false },
  },
]

const changeIcons = {
  up: ArrowUp,
  down: ArrowDown,
  stable: Minus,
}

function MetricCard({ metric }: { metric: Metric }) {
  const Icon = metric.icon
  const ChangeIcon = changeIcons[metric.change.direction]

  return (
    <li className="metric-card">
      <span className="metric-card__icon" aria-hidden="true">
        <Icon />
      </span>

      <h2 className="metric-card__title">{metric.title}</h2>

      <button
        className="metric-card__menu"
        type="button"
        aria-label={`Действия с виджетом «${metric.title}»`}
        disabled
      >
        <Ellipsis aria-hidden="true" />
      </button>

      <p className="metric-card__value">{metric.value}</p>

      <p
        className="metric-card__change"
        data-highlighted={metric.change.highlighted}
      >
        <ChangeIcon aria-hidden="true" />
        {metric.change.text}
      </p>
    </li>
  )
}

export default function WeekMetrics() {
  return (
    <section className="week-metrics" aria-label="Показатели недели">
      <ul className="week-metrics__grid">
        {weeklyMetrics.map((metric) => (
          <MetricCard key={metric.id} metric={metric} />
        ))}
      </ul>
    </section>
  )
}