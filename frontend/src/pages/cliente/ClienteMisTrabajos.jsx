import { useQuery } from '@tanstack/react-query'
import { Briefcase, MapPin, Clock } from 'lucide-react'
import ClienteLayout from '../../components/cliente/ClienteLayout'
import { getMisSolicitudes } from '../../services/clienteService'

const estadoConfig = {
  pendiente:  { label: 'Pendiente',  cls: 'bg-amber-100 text-amber-700' },
  en_curso:   { label: 'En curso',   cls: 'bg-blue-100 text-blue-700' },
  finalizado: { label: 'Finalizado', cls: 'bg-emerald-100 text-emerald-700' },
  cancelado:  { label: 'Cancelado',  cls: 'bg-red-100 text-red-700' },
}

export default function ClienteMisTrabajos() {
  const { data: solicitudes = [], isLoading } = useQuery({
    queryKey: ['mis-solicitudes'],
    queryFn: getMisSolicitudes,
    refetchInterval: 20_000,
  })

  return (
    <ClienteLayout>
      <div className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="font-display text-2xl font-bold text-slate-800 mb-6">Mis trabajos</h1>

        {isLoading && (
          <div className="space-y-3">
            {[1, 2].map((i) => (
              <div key={i} className="bg-white rounded-2xl border border-slate-200 h-28 animate-pulse" />
            ))}
          </div>
        )}

        {!isLoading && solicitudes.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-slate-400">
            <Briefcase className="w-12 h-12 mb-3 opacity-30" />
            <p className="text-sm">Todavía no solicitaste ningún servicio</p>
          </div>
        )}

        {!isLoading && solicitudes.map((s) => {
          const est = estadoConfig[s.estado] ?? { label: s.estado, cls: 'bg-slate-100 text-slate-600' }
          return (
            <div
              key={s.id}
              className="bg-white rounded-2xl border border-slate-200 p-5 mb-3 shadow-sm"
            >
              <div className="flex items-start justify-between mb-2">
                <p className="font-semibold text-slate-800">{s.tipo ?? 'Solicitud'}</p>
                <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${est.cls}`}>
                  {est.label}
                </span>
              </div>
              <p className="text-sm text-slate-600 mb-2 line-clamp-2">"{s.descripcion}"</p>
              <div className="flex flex-wrap gap-3 text-xs text-slate-400">
                {s.direccion && (
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3 h-3" /> {s.direccion}
                  </span>
                )}
                {s.fecha && (
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" /> {s.fecha}
                  </span>
                )}
                {s.plomero && (
                  <span className="text-brand-500 font-medium">Plomero: {s.plomero}</span>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </ClienteLayout>
  )
}
