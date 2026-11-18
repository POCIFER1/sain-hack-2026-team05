import { useEffect, useRef, useState } from 'react'
import { ArrowRight, Check, X } from 'lucide-react'

import './WeekAnalysis.css'

const questions = [
  {
    id: 'sleep',
    title: 'Кажется, на этой неделе ты стал больше спать?',
    detail: 'В среднем сон стал длиннее на 32 минуты по сравнению с прошлой неделей.',
  },
  {
    id: 'activity',
    title: 'На этой неделе ты больше ходил пешком?',
    detail: 'Среднее количество шагов выросло на 12% по сравнению с прошлой неделей.',
  },
  {
    id: 'sedentary-time',
    title: 'Ты стал проводить меньше времени сидя?',
    detail: 'В среднем сидячее время сократилось на 18 минут в день.',
  },
]

const options = [
  { value: 'yes', label: 'Да, это про меня' },
  { value: 'no', label: 'Нет, это не так' },
  { value: 'unsure', label: 'Затрудняюсь ответить' },
] as const

type AnswerValue = (typeof options)[number]['value']

type Answer = {
  questionId: string
  value: AnswerValue
}

const ANSWER_TRANSITION_MS = 220

export default function WeekAnalysis() {
  const dialogRef = useRef<HTMLDialogElement>(null)
  const questionTitleRef = useRef<HTMLHeadingElement>(null)

  const [answers, setAnswers] = useState<Answer[]>([])
  const [selected, setSelected] = useState<AnswerValue | null>(null)

  const question = questions[answers.length]
  const total = questions.length
  const step = Math.min(answers.length + 1, total)

  useEffect(() => {
    if (selected === null || !question) return

    const reducedMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)',
    ).matches

    const timer = window.setTimeout(() => {
      if (!dialogRef.current?.open) return

      setAnswers((previous) => [
        ...previous,
        { questionId: question.id, value: selected },
      ])
      setSelected(null)
    }, reducedMotion ? 0 : ANSWER_TRANSITION_MS)

    return () => window.clearTimeout(timer)
  }, [question, selected])

  useEffect(() => {
    if (answers.length > 0 && dialogRef.current?.open) {
      questionTitleRef.current?.focus({ preventScroll: true })
    }
  }, [answers.length])

  function startAnalysis() {
    setAnswers([])
    setSelected(null)
    dialogRef.current?.showModal()
  }

  return (
    <>
      <button
        className="week-hero__action week-analysis-trigger"
        type="button"
        aria-haspopup="dialog"
        onClick={startAnalysis}
      >
        Начать анализ
        <ArrowRight aria-hidden="true" />
      </button>

      <dialog
        ref={dialogRef}
        className="week-analysis"
        aria-labelledby="week-analysis-title"
        onClose={() => setSelected(null)}
      >
        <div className="week-analysis__header">
          <h2 id="week-analysis-title">Анализ недели</h2>

          <span className="week-analysis__count">
            {step} из {total}
          </span>

          <button
            className="week-analysis__close"
            type="button"
            aria-label="Закрыть анализ"
            onClick={() => dialogRef.current?.close()}
          >
            <X aria-hidden="true" />
          </button>
        </div>

        <progress
          className="week-analysis__progress"
          aria-label="Текущий шаг анализа"
          value={step}
          max={total}
        />

        <div
          key={question?.id ?? 'complete'}
          className="week-analysis__step"
          data-leaving={selected !== null}
        >
          <h3
            ref={questionTitleRef}
            className="week-analysis__question"
            tabIndex={-1}
          >
            {question ? question.title : 'Анализ недели завершён'}
          </h3>

          <p className="week-analysis__detail">
            {question ? question.detail : 'Ты ответил на все три вопроса.'}
          </p>

          {question ? (
            <div className="week-analysis__options">
              {options.map((option) => (
                <button
                  key={option.value}
                  className="week-analysis__option"
                  type="button"
                  data-selected={selected === option.value}
                  aria-disabled={selected !== null}
                  onClick={() => {
                    if (selected === null) setSelected(option.value)
                  }}
                >
                  <span>{option.label}</span>
                  {selected === option.value && <Check aria-hidden="true" />}
                </button>
              ))}
            </div>
          ) : (
            <button
              className="week-analysis__done"
              type="button"
              onClick={() => {
                dialogRef.current?.close() 
                window.location.hash = '/week-result'
              }}
            >
              <Check aria-hidden="true" />
              Посмотреть результат
            </button>
          )}
        </div>
      </dialog>
    </>
  )
}