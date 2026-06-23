// src/hooks/useTimer.js
import { useState, useEffect } from 'react'

/**
 * Cuenta regresiva desde `initialSeconds`.
 * Devuelve { label, pct } donde pct va de 100 → 0.
 */
export function useTimer(initialSeconds) {
  const [secs, setSecs] = useState(initialSeconds)

  useEffect(() => {
    if (secs <= 0) return
    const id = setInterval(() => setSecs(s => Math.max(0, s - 1)), 1000)
    return () => clearInterval(id)
  }, [])

  const h = Math.floor(secs / 3600)
  const m = Math.floor((secs % 3600) / 60)
  const s = secs % 60

  let label
  if (h > 0) label = `${h}h ${m}m`
  else        label = `${m}:${s < 10 ? '0' : ''}${s}`

  const pct = Math.round((secs / initialSeconds) * 100)
  return { label, pct, secs }
}
