import { useQuery } from '@tanstack/react-query'
import { History, Star } from 'lucide-react'
import PlomeroLayout from '../../components/plomero/PlomeroLayout'

/* =========================
   FAKE DATA
========================= */
const fakeHistorial = [
  {
    id: 1,
    tipo: 'Cambio de grifería en baño',
    zona: 'Quilmes',
    fecha: '2026-05-10',
    calificacion: 5,
    comentario: 'Excelente trabajo, muy prolijo y rápido.',
  },
  {
    id: 2,
    tipo: 'Reparación de pérdida en cocina',
    zona: 'Avellaneda',
    fecha: '2026-05-02',
    calificacion: 4,
    comentario: 'Buen servicio, llegó a horario.',
  },
  {
    id: 3,
    tipo: 'Destapación de cañería',
    zona: 'Lanús',
    fecha: '2026-04-28',
    calificacion: 5,
    comentario: 'Muy recomendable, resolvió todo en minutos.',
  },
]

/* =========================
   MOCK FETCH
========================= */
const fetchHistorialFake = () =>
  new Promise((resolve) => {
    setTimeout(() => {
      resolve(fakeHistorial)
    }, 800)
  })

export default function PlomeroHistorial() {
  const { data: trabajos = [], isLoading } = useQuery({
    queryKey: ['historial'],
    queryFn: fetchHistorialFake,
  })

  return (
    <PlomeroLayout>
      <div className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="font-display text-2xl font-bold text-slate-800 mb-6">
          Historial
        </h1>

        {/* LOADING */}
        {isLoading && (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="bg-white rounded-2xl border border-slate-200 h-20 animate-pulse"
              />
            ))}
          </div>
        )}

        {/* EMPTY */}
        {!isLoading && trabajos.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-slate-400">
            <History className="w-12 h-12 mb-3 opacity-30" />
            <p className="text-sm">
              Todavía no tenés trabajos finalizados
            </p>
          </div>
        )}

        {/* LISTA */}
        {!isLoading &&
          trabajos.map((t) => (
            <div
              key={t.id}
              className="bg-white rounded-2xl border border-slate-200 p-4 mb-3 shadow-sm"
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold text-slate-800">
                    {t.tipo}
                  </p>
                  <p className="text-sm text-slate-500">
                    {t.zona} · {t.fecha}
                  </p>
                </div>

                {/* CALIFICACIÓN */}
                {t.calificacion != null && (
                  <div className="flex items-center gap-1 text-amber-400">
                    <Star className="w-4 h-4 fill-amber-400" />
                    <span className="text-sm font-semibold text-slate-700">
                      {t.calificacion}
                    </span>
                  </div>
                )}
              </div>

              {/* COMENTARIO */}
              {t.comentario && (
                <p className="text-sm text-slate-500 mt-2 italic">
                  "{t.comentario}"
                </p>
              )}
            </div>
          ))}
      </div>
    </PlomeroLayout>
  )
}