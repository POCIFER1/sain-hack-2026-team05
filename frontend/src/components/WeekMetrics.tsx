import { useRef, useState } from 'react'
import {
  AlarmClock,
  Armchair,
  ArrowDown,
  ArrowUp,
  BedDouble,
  CalendarDays,
  Check,
  Dumbbell,
  Ellipsis,
  Flame,
  HeartPulse,
  Minus,
  Moon,
  Plus,
  Route,
  Sun,
  X,
  Zap,
  Settings2,
  type LucideIcon,
} from 'lucide-react'

import './WeekMetrics.css'

type Metric = {
  id: string
  title: string
  value: string
  icon: LucideIcon
  change?: {
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

const widgetCatalog: Metric[] = [
  ...weeklyMetrics,
  { id: 'resting-pulse', title: 'Пульс в покое', icon: HeartPulse, value: 'Нет данных' },
  { id: 'distance', title: 'Дистанция', icon: Route, value: 'Нет данных' },
  { id: 'workouts', title: 'Тренировки', icon: Dumbbell, value: 'Нет данных' },
  { id: 'active-calories', title: 'Калории активности', icon: Flame, value: 'Нет данных' },
  { id: 'wake-time', title: 'Время подъёма', icon: AlarmClock, value: 'Нет данных' },
  { id: 'bedtime', title: 'Время отхода ко сну', icon: BedDouble, value: 'Нет данных' },
  { id: 'sleep-regularity', title: 'Регулярность сна', icon: CalendarDays, value: 'Нет данных' },
]

const changeIcons = {
  up: ArrowUp,
  down: ArrowDown,
  stable: Minus,
}

function MetricCard({ metric }: { metric: Metric }) {
  const Icon = metric.icon
  const ChangeIcon = metric.change ? changeIcons[metric.change.direction] : null

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

      {metric.change && ChangeIcon && (
        <p
          className="metric-card__change"
          data-highlighted={metric.change.highlighted}
        >
          <ChangeIcon aria-hidden="true" />
          {metric.change.text}
        </p>
      )}
    </li>
  )
}

export default function WeekMetrics({ showHeading = false }: { showHeading?: boolean }) {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const [visibleMetrics, setVisibleMetrics] = useState<Metric[]>(weeklyMetrics)
  const visibleIds = new Set(visibleMetrics.map((metric) => metric.id))

  function addWidget(metric: Metric) {
    setVisibleMetrics((current) => {
      if (current.some((item) => item.id === metric.id)) return current
      return [...current, metric]
    })

    dialogRef.current?.close()
  }

  return (
    <section className="week-metrics" aria-label="Показатели недели">
      {showHeading && (
        <div className="result-metrics-heading">
          <h2>Мои показатели</h2>
          <span>Выбрано: {visibleMetrics.length}</span>
          <button type="button" onClick={() => dialogRef.current?.showModal()}>
            <Settings2 aria-hidden="true" />
            Настроить
          </button>
        </div>
      )}
      <ul className="week-metrics__grid">
        {visibleMetrics.map((metric) => (
          <MetricCard key={metric.id} metric={metric} />
        ))}
      </ul>

      <button
        className="week-metrics__add"
        type="button"
        aria-haspopup="dialog"
        onClick={() => dialogRef.current?.showModal()}
      >
        <Plus aria-hidden="true" />
        Добавить виджет
      </button>

      <dialog
        ref={dialogRef}
        className="widget-picker"
        aria-labelledby="widget-picker-title"
      >
        <div className="widget-picker__header">
          <h2 id="widget-picker-title">Добавить виджет</h2>
          <button
            className="widget-picker__close"
            type="button"
            aria-label="Закрыть окно"
            onClick={() => dialogRef.current?.close()}
          >
            <X aria-hidden="true" />
          </button>
        </div>

        <ul className="widget-picker__list">
          {widgetCatalog.map((metric) => {
            const Icon = metric.icon
            const added = visibleIds.has(metric.id)

            return (
              <li key={metric.id}>
                <button
                  className="widget-option"
                  type="button"
                  disabled={added}
                  onClick={() => addWidget(metric)}
                >
                  <span className="widget-option__icon">
                    <Icon aria-hidden="true" />
                  </span>

                  <span className="widget-option__text">
                    <span>{metric.title}</span>
                    {added && <small>Добавлен</small>}
                  </span>

                  {added ? (
                    <Check className="widget-option__mark" aria-hidden="true" />
                  ) : (
                    <Plus className="widget-option__mark" aria-hidden="true" />
                  )}
                </button>
              </li>
            )
          })}
        </ul>
      </dialog>
    </section>
  )
}