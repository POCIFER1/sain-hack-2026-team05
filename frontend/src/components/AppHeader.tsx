import {
  Bell,
  ChartNoAxesColumnIncreasing,
  House,
  TrendingUp,
  UserRound,
} from 'lucide-react'

import './AppHeader.css'

export default function AppHeader() {
  return (
    <header className="app-header">
      <a className="app-brand" href="/" aria-label="sain — Главная">
        <svg viewBox="0 0 48 48" fill="currentColor" aria-hidden="true">
          {Array.from({ length: 8 }, (_, index) => (
            <circle
              key={index}
              cx="24"
              cy="5"
              r="4.8"
              transform={`rotate(${index * 45} 24 24)`}
            />
          ))}
        </svg>
        <span>sain</span>
      </a>

      <nav className="header-nav" aria-label="Основная навигация">
        <a className="header-nav__item" href="/" aria-current="page">
          <House aria-hidden="true" />
          Главная
        </a>

        <button className="header-nav__item" type="button" disabled>
          <ChartNoAxesColumnIncreasing aria-hidden="true" />
          Результат недели
        </button>

        <button className="header-nav__item" type="button" disabled>
          <TrendingUp aria-hidden="true" />
          История изменений
        </button>
      </nav>

      <div className="header-actions">
        <button type="button" aria-label="Уведомления" disabled>
          <Bell aria-hidden="true" />
        </button>
        <button type="button" aria-label="Профиль" disabled>
          <UserRound aria-hidden="true" />
        </button>
      </div>
    </header>
  )
}