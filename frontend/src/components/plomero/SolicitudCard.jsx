import { useState } from 'react'
import { MapPin, Clock, AlertTriangle, Lock, ChevronDown, ChevronUp, Calendar } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { aceptarSolicitud, rechazarSolicitud } from '../../services/plomeroService'
import { useCountdown } from '../../hooks/useCountdown'

export default function SolicitudCard({ solicitud }) {
  const qc = useQueryClient()
  const [expanded, setExpanded] = useState(false)

  const {
    id,
    tipo,           // 'Urgencias' | 'Destapes' | etc.
    urgente,
    zona,
    fecha,
    turnoSugerido,  // opcional, ej. "14/05/2026 a las 10:00 hs"
    descripcion,
    segundosRestantes, // número de segundos que quedan para responder
  } = solicitud

  const { formatted, percent, expired } = useCountdown(segundosRestantes ?? 0)

  const aceptar = useMutation({
    mutationFn: () => aceptarSolicitud(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['solicitudes'] }),
  })
  const rechazar = useMutation({
    mutationFn: () => rechazarSolicitud(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['solicitudes'] }),
  })

  const isUrgente = urgente === true || tipo?.toLowerCase() === 'urgencias'

  const timerColor = percent > 50 ? 'bg-brand-500' : percent > 20 ? 'bg-amber-400' : 'bg-red-500'
  const timerTextColor = percent > 50 ? 'text-brand-600' : percent > 20 ? 'text-amber-600' : 'text-red-600'

  return (
    <div
      className={`rounded-2xl border bg-white shadow-sm overflow-hidden ${
        isUrgente ? 'border-red-200' : 'border-slate-200'
      }`}
    >
      {/* Header */}
      <div className="px-5 pt-4 pb-3">
        <div className="flex items-center gap-2 mb-2 flex-wrap">
          <span
            className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
              isUrgente ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
            }`}
          >
            {tipo ?? 'General'}
          </span>
          {isUrgente && (
            <span className="flex items-center gap-1 text-xs font-bold text-red-600">
              <AlertTriangle className="w-3.5 h-3.5" /> URGENTE
            </span>
          )}
        </div>

        <div className="flex items-center gap-1.5 text-sm text-slate-500">
          <MapPin className="w-3.5 h-3.5 shrink-0" />
          <span>{zona}</span>
          <span className="text-slate-300">·</span>
          <span>{fecha}</span>
        </div>

        {turnoSugerido && (
          <div className="flex items-center gap-1.5 text-sm text-slate-500 mt-1">
            <Calendar className="w-3.5 h-3.5 shrink-0" />
            <span>Turno sugerido: {turnoSugerido}</span>
          </div>
        )}
      </div>

      {/* Timer */}
      {segundosRestantes != null && (
        <div className="mx-5 mb-3 bg-slate-50 rounded-xl px-4 py-2.5">
          <div className="flex items-center justify-between mb-1.5">
            <div className="flex items-center gap-1.5">
              <Clock className={`w-3.5 h-3.5 ${timerTextColor}`} />
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                Tiempo para responder
              </span>
            </div>
            <span className={`text-sm font-bold ${timerTextColor}`}>
              {expired ? 'Expirado' : formatted}
            </span>
          </div>
          <div className="h-1.5 bg-slate-200 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-1000 ${timerColor}`}
              style={{ width: `${percent}%` }}
            />
          </div>
        </div>
      )}

      {/* Descripción */}
      <div className="mx-5 mb-3 bg-slate-50 rounded-xl px-4 py-3">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1">
          Lo que describe el cliente
        </p>
        <p className={`text-sm text-slate-700 ${!expanded ? 'line-clamp-3' : ''}`}>
          "{descripcion}"
        </p>
        {descripcion?.length > 120 && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-brand-600 text-xs font-medium mt-1 hover:underline"
          >
            {expanded ? (
              <><ChevronUp className="w-3 h-3" /> Ver menos</>
            ) : (
              <><ChevronDown className="w-3 h-3" /> Ver más</>
            )}
          </button>
        )}
      </div>

      {/* Dirección oculta */}
      <div className="mx-5 mb-4 flex items-center gap-1.5 text-xs text-slate-400">
        <Lock className="w-3.5 h-3.5" />
        La dirección exacta se revela solo si aceptás el trabajo
      </div>

      {/* Acciones */}
      <div className="px-5 pb-5 grid grid-cols-2 gap-3">
        <button
          onClick={() => rechazar.mutate()}
          disabled={rechazar.isPending || aceptar.isPending || expired}
          className="py-3 rounded-xl border border-red-200 text-red-500 font-semibold text-sm hover:bg-red-50 transition-colors disabled:opacity-40"
        >
          ✕ Rechazar
        </button>
        <button
          onClick={() => aceptar.mutate()}
          disabled={aceptar.isPending || rechazar.isPending || expired}
          className="py-3 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white font-semibold text-sm transition-colors disabled:opacity-40"
        >
          {aceptar.isPending ? 'Aceptando...' : '✓ Aceptar trabajo'}
        </button>
      </div>
    </div>
  )
}
