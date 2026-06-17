import { useQuery } from '@tanstack/react-query'
import { Inbox } from 'lucide-react'
import PlomeroLayout from '../../components/plomero/PlomeroLayout'
import SolicitudCard from '../../components/plomero/SolicitudCard'
import { getMisSolicitudesPlomero } from '../../services/plomeroService'

export default function PlomeroDashboard() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['solicitudes'],
    queryFn: getMisSolicitudesPlomero,
    refetchInterval: 30_000,
  })

  // 🔥 normalizamos SIEMPRE a array
  const solicitudes = Array.isArray(data)
    ? data
    : data?.solicitudes || data?.data || []

  return (
    <PlomeroLayout>
      <div className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="font-display text-2xl font-bold text-slate-800 mb-1">
          Solicitudes entrantes
        </h1>

        <p className="text-sm text-slate-500 mb-6">
          El primero en aceptar queda asignado · La dirección se revela al aceptar
        </p>

        {isLoading && (
          <div className="space-y-4">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="bg-white rounded-2xl border border-slate-200 h-48 animate-pulse"
              />
            ))}
          </div>
        )}

        {isError && (
          <div className="bg-red-50 text-red-600 rounded-xl px-4 py-3 text-sm">
            No se pudieron cargar las solicitudes. Intentá de nuevo.
          </div>
        )}

        {!isLoading && !isError && solicitudes.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-slate-400">
            <Inbox className="w-12 h-12 mb-3 opacity-30" />
            <p className="text-sm">No hay solicitudes por el momento</p>
          </div>
        )}

        {!isLoading && !isError && solicitudes.length > 0 && (
          <div className="space-y-4">
            {solicitudes.map((s) => (
              <SolicitudCard key={s.id} solicitud={s} />
            ))}
          </div>
        )}
      </div>
    </PlomeroLayout>
  )
}