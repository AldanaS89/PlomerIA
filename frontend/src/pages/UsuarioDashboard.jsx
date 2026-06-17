// src/pages/UsuarioDashboard.jsx
import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { solicitudesApi, plomerosApi } from '../services/api'
import { UsuarioNavbar } from '../components/Navbar'
import './UsuarioDashboard.css'

const TABS = [
  { key: 'inicio',    icon: '🏠', label: 'Inicio' },
  { key: 'trabajos',  icon: '📋', label: 'Mis trabajos' },
  { key: 'alertas',   icon: '🔔', label: 'Alertas', badge: 2 },
]

// Avatar con iniciales
function Avatar({ nombre, color }) {
  const initials = nombre?.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase() || '?'
  return (
    <div className="avatar" style={{ background: color || '#3b82f6' }}>
      {initials}
    </div>
  )
}

const AVATAR_COLORS = ['#3b82f6', '#8b5cf6', '#16a34a', '#d97706', '#ec4899']

export default function UsuarioDashboard() {
  const { token, user } = useAuth()
  const { show } = useToast()

  const [tab,      setTab]      = useState('inicio')
  const [texto,    setTexto]    = useState('')
  const [loading,  setLoading]  = useState(false)
  const [sugeridos, setSugeridos] = useState([]) // tras buscar
  const [confianza, setConfianza] = useState([]) // plomeros previos (mock por ahora)
  const [soloMujeres, setSoloMujeres] = useState(false)

  // Cargar plomeros de confianza al montar (simulados con buscar)
  useEffect(() => {
    plomerosApi.buscar({}).then(setSugeridos).catch(() => {})
  }, [])

  const handleBuscar = async () => {
    if (texto.trim().length < 10) return
    setLoading(true)
    try {
      // Obtener ubicación del dispositivo
      const getCoords = () =>
        new Promise((res, rej) =>
          navigator.geolocation?.getCurrentPosition(
            p => res({ lat: p.coords.latitude, lon: p.coords.longitude }),
            () => res({ lat: -34.85, lon: -58.38 }) // fallback Longchamps
          ) ?? res({ lat: -34.85, lon: -58.38 })
        )

      const { lat, lon } = await getCoords()

      const data = await solicitudesApi.crear(
        {
          descripcion_raw:  texto,
          localidad_evento: 'Mi ubicación',
          latitud_evento:   lat,
          longitud_evento:  lon,
          solo_mujeres:     soloMujeres,
        },
        token
      )

      // El back devuelve plomeros_sugeridos_detallados
      const detallados = data.plomeros_sugeridos_detallados || []
      setSugeridos(detallados)
      show(`¡Encontramos ${detallados.length} plomeros cerca tuyo!`, 'success')
    } catch (err) {
      show(err.message, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <UsuarioNavbar
        tabs={TABS}
        activeTab={tab}
        onTab={setTab}
        userName={user?.nombre || user?.email || 'Usuario'}
      />

      <div className="page-body">
        {tab === 'inicio' && (
          <>
            <h1 className="hero-title">¿Qué problema tenés?</h1>
            <p className="hero-sub">Describilo y te mostramos los mejores plomeros cerca tuyo.</p>

            {/* Tarjeta de búsqueda */}
            <div className="search-card">
              <label className="search-label">Describí tu problema</label>
              <textarea
                className="search-input"
                placeholder="Ej: Se me rompió una cañería debajo de la pileta y el agua no para de salir..."
                value={texto}
                onChange={e => setTexto(e.target.value)}
                rows={5}
              />

              <div className="search-options">
                <label className="solo-mujeres">
                  <input
                    type="checkbox"
                    checked={soloMujeres}
                    onChange={e => setSoloMujeres(e.target.checked)}
                  />
                  Solo plomeras mujeres
                </label>
              </div>

              <div className="search-footer">
                <span className="char-count">{texto.length} caracteres</span>
                <button
                  className="btn-search"
                  disabled={texto.trim().length < 10 || loading}
                  onClick={handleBuscar}
                >
                  {loading ? 'Buscando…' : 'Buscar profesionales →'}
                </button>
              </div>
            </div>

            {/* Lista de plomeros */}
            {sugeridos.length > 0 && (
              <>
                <div className="section-title">
                  {texto ? 'Plomeros sugeridos' : 'Mis plomeros de confianza'}
                </div>
                <div className="plomero-list">
                  {sugeridos.map((p, i) => (
                    <PlomeroItem
                      key={p.id ?? i}
                      plomero={p}
                      color={AVATAR_COLORS[i % AVATAR_COLORS.length]}
                      onContactar={() => show(`Contactando a ${p.nombre}…`)}
                    />
                  ))}
                </div>
              </>
            )}
          </>
        )}

        {tab === 'trabajos' && (
          <div className="empty-state">
            <span>📋</span>
            <p>No tenés trabajos en curso.</p>
          </div>
        )}

        {tab === 'alertas' && (
          <div className="empty-state">
            <span>🔔</span>
            <p>No hay alertas nuevas.</p>
          </div>
        )}
      </div>
    </div>
  )
}

function PlomeroItem({ plomero, color, onContactar }) {
  const nombre    = plomero.nombre
    ? `${plomero.nombre} ${plomero.apellido ?? ''}`.trim()
    : plomero.nombre ?? 'Plomero'
  const spec      = plomero.especialidad || plomero.localidad || ''
  const cal       = plomero.calificacion ?? plomero.puntuacion

  return (
    <div className="plomero-item">
      <div className="avatar" style={{ background: color }}>
        {nombre.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()}
      </div>
      <div className="plomero-info">
        <div className="plomero-name">{nombre}</div>
        <div className="plomero-spec">
          {spec}
          {cal != null && (
            <span className="plomero-rating"> ⭐ {Number(cal).toFixed(1)}</span>
          )}
        </div>
      </div>
      <button className="btn-contactar" onClick={onContactar}>Contactar</button>
    </div>
  )
}
