import { useQuery } from '@tanstack/react-query'
import { Calendar, Clock, MapPin } from 'lucide-react'
import PlomeroLayout from '../../components/plomero/PlomeroLayout'

/* =========================
   FAKE DATA
========================= */
const fakeTurnos = [
  {
    id: 1,
    diaMes: '12',
    mes: 'MAY',
    tipo: 'Reparación de caño en cocina',
    hora: '14:00',
    zona: 'Quilmes',
  },
  {
    id: 2,
    diaMes: '13',
    mes: 'MAY',
    tipo: 'Cambio de grifería baño',
    hora: '10:30',
    zona: 'Avellaneda',
  },
  {
    id: 3,
    diaMes: '15',
    mes: 'MAY',
    tipo: 'Destape de desagüe',
    hora: '18:00',
    zona: 'Lanús',
  },
]

/* =========================
   MOCK FETCH
========================= */
const fetchAgendaFake = () =>
  new Promise((resolve) => {
    setTimeout(() => {
      resolve(fakeTurnos)
    }, 800) // simula delay API
  })

export default function PlomeroAgenda() {
  const { data: turnos = [], isLoading } = useQuery({
    queryKey: ['agenda'],
    queryFn: fetchAgendaFake,
  })

  return (
    <PlomeroLayout>
      <div className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="font-display text-2xl font-bold text-slate-800 mb-6">
          Mi agenda
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

        {/* EMPTY STATE */}
        {!isLoading && turnos.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-slate-400">
            <Calendar className="w-12 h-12 mb-3 opacity-30" />
            <p className="text-sm">No tenés turnos programados</p>
          </div>
        )}

        {/* LISTA */}
        {!isLoading &&
          turnos.map((t) => (
            <div
              key={t.id}
              className="bg-white rounded-2xl border border-slate-200 p-4 mb-3 shadow-sm flex items-center gap-4"
            >
              {/* FECHA */}
              <div className="w-12 h-12 bg-emerald-50 rounded-xl flex flex-col items-center justify-center shrink-0">
                <span className="text-xs font-bold text-emerald-600">
                  {t.diaMes}
                </span>
                <span className="text-xs text-emerald-400">
                  {t.mes}
                </span>
              </div>

              {/* INFO */}
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-slate-800 truncate">
                  {t.tipo}
                </p>

                <p className="text-sm text-slate-500 flex items-center gap-1">
                  <Clock className="w-3 h-3" /> {t.hora}
                  <span className="mx-1 text-slate-300">·</span>
                  <MapPin className="w-3 h-3" /> {t.zona}
                </p>
              </div>
            </div>
          ))}
      </div>
    </PlomeroLayout>
  )
}