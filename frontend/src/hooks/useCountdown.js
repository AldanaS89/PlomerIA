import { useState, useEffect, useRef } from 'react'

export function useCountdown(seconds, onEnd) {
  const [remaining, setRemaining] = useState(seconds)
  const onEndRef = useRef(onEnd)
  onEndRef.current = onEnd

  useEffect(() => {
    if (remaining <= 0) { onEndRef.current?.(); return }
    const id = setInterval(() => setRemaining((r) => r - 1), 1000)
    return () => clearInterval(id)
  }, [remaining])

  const mm = String(Math.floor(remaining / 60)).padStart(2, '0')
  const ss = String(remaining % 60).padStart(2, '0')
  return { remaining, label: `${mm}:${ss}`, pct: remaining / seconds }
}