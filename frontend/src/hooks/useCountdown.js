import { useState, useEffect, useRef } from 'react'

/**
 * @param {number} initialSeconds  — segundos totales al inicio
 * @returns {{ remaining, percent, formatted, expired }}
 */
export function useCountdown(initialSeconds) {
  const [remaining, setRemaining] = useState(initialSeconds)
  const ref = useRef(initialSeconds)

  useEffect(() => {
    ref.current = initialSeconds
    setRemaining(initialSeconds)
  }, [initialSeconds])

  useEffect(() => {
    if (remaining <= 0) return
    const id = setInterval(() => {
      setRemaining((r) => {
        if (r <= 1) { clearInterval(id); return 0 }
        return r - 1
      })
    }, 1000)
    return () => clearInterval(id)
  }, [initialSeconds]) // restart when initialSeconds changes

  const percent = initialSeconds > 0 ? (remaining / initialSeconds) * 100 : 0

  const hh = Math.floor(remaining / 3600)
  const mm = Math.floor((remaining % 3600) / 60)
  const ss = remaining % 60

  const formatted =
    hh > 0
      ? `${hh}h ${String(mm).padStart(2, '0')}m`
      : `${String(mm).padStart(2, '0')}:${String(ss).padStart(2, '0')}`

  return { remaining, percent, formatted, expired: remaining <= 0 }
}
