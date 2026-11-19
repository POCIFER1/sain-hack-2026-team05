import { useEffect, useRef } from 'react'

const FLOW_SPEED = 0.26

export default function WeekWave() {
    const canvasRef = useRef<HTMLCanvasElement>(null)

    useEffect(() => {
        const canvas = canvasRef.current
        if (!canvas) return

        const context = canvas.getContext('2d')
        if (!context) return

        const ctx = context
        const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')
        const startedAt = performance.now()

        let frame = 0
        let width = 0
        let height = 0

        function draw(elapsedSeconds: number) {
            ctx.clearRect(0, 0, width, height)

            const t = elapsedSeconds * FLOW_SPEED
            const cx = width * 0.5
            const cy = height * 0.51

            // На широком экране сущность окружает текст и кнопку.
            // На телефоне сохраняет более вертикальный силуэт.
            const rx = Math.min(width * 0.41, height * 1.12, 580)
            const ry = height * 0.40

            function mist(
                x: number,
                y: number,
                radiusX: number,
                radiusY: number,
                rotation: number,
                rgb: string,
                opacity: number,
            ) {
                ctx.save()
                ctx.translate(x, y)
                ctx.rotate(rotation)
                ctx.scale(radiusX, radiusY)

                const gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, 1)
                gradient.addColorStop(0, `rgba(${rgb}, ${opacity})`)
                gradient.addColorStop(0.35, `rgba(${rgb}, ${opacity * 0.82})`)
                gradient.addColorStop(0.70, `rgba(${rgb}, ${opacity * 0.30})`)
                gradient.addColorStop(1, `rgba(${rgb}, 0)`)

                ctx.fillStyle = gradient
                ctx.fillRect(-1, -1, 2, 2)
                ctx.restore()
            }

            const driftX = Math.sin(t * 0.71) * rx * 0.07
            const driftY = Math.sin(t * 0.53) * ry * 0.06

            // Широкое внешнее свечение связывает отдельные пятна в одну форму.
            mist(cx, cy, rx * 1.18, ry * 1.21, 0, '53, 160, 8', 0.33)

            // Основная масса. Холодный изумруд сверху, травяной зелёный снизу.
            mist(cx + driftX, cy - ry * 0.19, rx, ry * 0.91, -0.07,
                '8, 166, 66', 0.85)
            mist(cx - rx * 0.12 - driftX, cy + ry * 0.26, rx * 0.85, ry * 0.81, 0.12,
                '67, 179, 5', 0.85)

            // Вытяжки растут из массы. У каждой свой наклон и темп движения.
            for (let i = 0; i < 5; i++) {
                const side = (i - 2) / 2
                const phase = t * (0.56 + i * 0.08) + i * 2.3
                const x = cx + side * rx * 0.66 + Math.sin(phase) * rx * 0.07
                const y = cy - ry * (0.54 + 0.09 * Math.cos(phase))
                const lean = side * 0.36 + Math.sin(phase * 0.83) * 0.17

                mist(x, y, rx * (0.07 + 0.03 * Math.cos(phase)), ry * 0.61, lean,
                    '27, 182, 72', 0.30)
            }

            // Смещённые блики дают светящуюся кромку отдельными участками.
            ctx.save()
            ctx.globalCompositeOperation = 'screen'

            mist(cx - rx * 0.49 + driftX, cy - ry * 0.20 + driftY,
                rx * 0.43, ry * 0.58, 0.54, '33, 238, 95', 0.65)

            mist(cx + rx * 0.46 - driftX, cy - ry * 0.16 - driftY,
                rx * 0.50, ry * 0.51, -0.52, '65, 228, 30', 0.59)

            mist(cx - rx * 0.13 + driftX, cy + ry * 0.57,
                rx * 0.55, ry * 0.36, -0.18, '143, 212, 8', 0.48)

            ctx.restore()

            // Полупрозрачная тень медленно проходит через середину.
            // Она даёт глубину и сохраняет контраст белого текста.
            mist(cx + Math.sin(t * 0.47) * rx * 0.24, cy + driftY,
                rx * 0.59, ry * 0.51, -0.23, '3, 28, 9', 0.55)
        }

        function animate(now: number) {
            draw((now - startedAt) / 1000)
            frame = requestAnimationFrame(animate)
        }

        function syncCanvas() {
            if (!canvas) return

            cancelAnimationFrame(frame)

            const bounds = canvas.getBoundingClientRect()
            width = bounds.width
            height = bounds.height
            if (!width || !height) return

            const scale = Math.min(window.devicePixelRatio || 1, 2)
            canvas.width = Math.round(width * scale)
            canvas.height = Math.round(height * scale)
            ctx.setTransform(scale, 0, 0, scale, 0, 0)

            if (reducedMotion.matches) {
                draw(1.5)
            } else {
                frame = requestAnimationFrame(animate)
            }
        }

        const observer = new ResizeObserver(syncCanvas)
        observer.observe(canvas)
        reducedMotion.addEventListener('change', syncCanvas)
        syncCanvas()

        return () => {
            cancelAnimationFrame(frame)
            observer.disconnect()
            reducedMotion.removeEventListener('change', syncCanvas)
        }
    }, [])

    return <canvas ref={canvasRef} className="week-wave" aria-hidden="true" />
}