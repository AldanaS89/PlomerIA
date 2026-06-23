import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Search, MessageCircle, Star, Loader2 } from 'lucide-react'
import ClienteLayout from '../../components/cliente/ClienteLayout'
import { buscarPlomeros, getPlomerosConfianza, crearSolicitud } from '../../services/clienteService'

function Avatar({ nombre, color = 'bg-brand-600' }) {
  const initials = nombre
    ?.split(' ')
    .map((p) => p[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
  return (
    <div className={`w-10 h-10 ${color} rounded-xl flex items-center justify-center text-white font-bold text-sm shrink-0`}>
      {initials}
    </div>
  )
}

const avatarColors = ['bg-brand-600', 'bg-emerald-500', 'bg-violet-500', 'bg-amber-500', 'bg-rose-500']

export default function ClienteHome() {
  const [descripcion, setDescripcion] = useState('')
  const [resultados, setResultados] = useState(null)
  const [solicitudEnviada, setSolicitudEnviada] = useState(false)

  const { data: confianza = [] } = useQuery({
    queryKey: ['plomeros-confianza'],
    queryFn: getPlomerosConfianza,
  })

  const buscar = useMutation({
    mutationFn: buscarPlomeros,
    onSuccess: (data) => setResultados(data),
  })

  const solicitar = useMutation({
    mutationFn: crearSolicitud,
    onSuccess: () => {
      setSolicitudEnviada(true)
      setDescripcion('')
      setResultados(null)
    },
  })

  const handleBuscar = () => {
    if (descripcion.trim().length < 10) return
    setResultados(null)
    setSolicitudEnviada(false)
    buscar.mutate(descripcion)
  }

  return (
    <ClienteLayout>
      <div className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="font-display text-2xl font-bold text-slate-800 mb-1">
          ¿Qué problema tenés?
        </h1>
        <p className="text-sm text-slate-500 mb-6">
          Describilo y te mostramos los mejores plomeros cerca tuyo.
        </p>

        {/* Formulario */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-5 mb-6">
          <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
            Describí tu problema
          </label>
          <textarea
            rows={5}
            value={descripcion}
            onChange={(e) => setDescripcion(e.target.value)}
            placeholder="Ej: Se me rompió una cañería debajo de la pileta y el agua no para de salir..."
            className="w-full resize-none border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400"
          />
          <div className="flex items-center justify-between mt-3">
            <span className="text-xs text-slate-400">{descripcion.length} caracteres</span>
            <button
              onClick={handleBuscar}
              disabled={descripcion.trim().length < 10 || buscar.isPending}
              className="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 disabled:bg-slate-200 disabled:text-slate-400 text-white text-sm font-semibold px-5 py-2.5 rounded-xl transition-colors"
            >
              {buscar.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Search className="w-4 h-4" />
              )}
              Buscar profesionales →
            </button>
          </div>
        </div>

        {/* Éxito */}
        {solicitudEnviada && (
          <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-5 mb-6 text-center">
            <p className="text-emerald-700 font-semibold">¡Solicitud enviada!</p>
            <p className="text-sm text-emerald-600 mt-1">
              Los plomeros disponibles serán notificados. Te avisamos cuando alguien acepte.
            </p>
          </div>
        )}

        {/* Resultados de búsqueda */}
        {resultados && resultados.length > 0 && (
          <div className="mb-6">
            <h2 className="text-sm font-semibold text-slate-600 uppercase tracking-wide mb-3">
              Plomeros disponibles
            </h2>
            <div className="space-y-3">
              {resultados.map((p, i) => (
                <div
                  key={p.id}
                  className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm flex items-center gap-4"
                >
                  <Avatar nombre={p.nombre} color={avatarColors[i % avatarColors.length]} />
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-slate-800">{p.nombre}</p>
                    <p className="text-sm text-slate-500 truncate">{p.especialidad}</p>
                    {p.calificacion && (
                      <div className="flex items-center gap-1 mt-0.5">
                        <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                        <span className="text-xs text-slate-500">{p.calificacion}</span>
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => solicitar.mutate({ descripcion, plomeroId: p.id })}
                    disabled={solicitar.isPending}
                    className="text-sm font-semibold text-brand-600 border border-brand-200 hover:bg-brand-50 px-3 py-1.5 rounded-xl transition-colors"
                  >
                    Contactar
                  </button>
                </div>
              ))}
            </div>
            <button
              onClick={() => solicitar.mutate({ descripcion })}
              disabled={solicitar.isPending}
              className="mt-4 w-full bg-brand-600 hover:bg-brand-700 text-white font-semibold py-3 rounded-xl text-sm transition-colors disabled:opacity-50"
            >
              {solicitar.isPending ? 'Enviando...' : 'Enviar solicitud a todos →'}
            </button>
          </div>
        )}

        {resultados && resultados.length === 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-2xl p-5 mb-6 text-center">
            <p className="text-amber-700 font-semibold">Sin plomeros disponibles ahora</p>
            <p className="text-sm text-amber-600 mt-1">
              Podés dejar tu solicitud igual y te contactamos en cuanto haya disponibilidad.
            </p>
            <button
              onClick={() => solicitar.mutate({ descripcion })}
              className="mt-3 bg-amber-500 hover:bg-amber-600 text-white text-sm font-semibold px-5 py-2 rounded-xl transition-colors"
            >
              Dejar solicitud de todas formas
            </button>
          </div>
        )}

        {/* Plomeros de confianza */}
        {confianza.length > 0 && (
          <div>
            <h2 className="text-sm font-semibold text-slate-600 uppercase tracking-wide mb-3">
              Mis plomeros de confianza
            </h2>
            <div className="space-y-3">
              {confianza.map((p, i) => (
                <div
                  key={p.id}
                  className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm flex items-center gap-4"
                >
                  <Avatar nombre={p.nombre} color={avatarColors[i % avatarColors.length]} />
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-slate-800">{p.nombre}</p>
                    <p className="text-sm text-slate-500 truncate">{p.ultimoServicio}</p>
                  </div>
                  <button className="flex items-center gap-1.5 text-sm font-semibold text-brand-600 border border-brand-200 hover:bg-brand-50 px-3 py-1.5 rounded-xl transition-colors">
                    <MessageCircle className="w-3.5 h-3.5" />
                    Contactar
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </ClienteLayout>
  )
}
