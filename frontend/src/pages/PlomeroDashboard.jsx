// src/pages/PlomeroDashboard.jsx
import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { solicitudesApi } from '../services/api'
import { PlomeroNavbar } from '../components/Navbar'
import SolicitudCard from '../components/SolicitudCard'
import './PlomeroDashboard.css'

const TABS = [
  { key: 'solicitudes', icon: '🗂', label: 'Solicitudes', badge: null },
  { key: 'en_curso',    icon: '✏', label: 'En curso' },
  { key: 'agenda',      icon: '📅', label: 'Mi agenda' },
  { key: 'historial',   icon: '📋', label: 'Historial' },
]

// Solicitudes demo para cuando el back no devuelve datos
const MOCK_SOLICITUDES = [
  {
    id: 1,
    descripcion_raw: 'Se me rompió una cañería debajo de la pileta y el agua no para de salir. Ya cerré la llave de paso pero necesito que lo arreglen hoy.',
    localidad_evento: 'Longchamps',
    hora_creacion: 'Hoy, 14:32',
    estado_urgencia: 'urgente',
    categoria: 'Urgencias',
  },
  {
    id: 2,
    descripcion_raw: 'Tengo un destape en el baño principal, el agua tarda mucho en bajar. No es urgente pero me gustaría resolverlo esta semana.',
    localidad_evento: 'Monte Grande',
    hora_creacion: 'Hoy, 11:15',
    turno_sugerido: '14/05/2026 a las 10:00 hs',
    categoria: 'Destapes',
  },
  {
    id: 3,
    descripcion_raw: 'La canilla del baño gotea constantemente. Quiero cambiarla o repararla según lo que corresponda.',
    localidad_evento: 'Lomas de Zamora',
    hora_creacion: 'Ayer, 18:00',
    turno_sugerido: '15/05/2026 a las 14:00 hs',
    categoria: 'Reparaciones',
  },
]

export default function PlomeroDashboard() {
  const { token, user } = useAuth()
  const { show } = useToast()

  const [tab,         setTab]         = useState('solicitudes')
  const [solicitudes, setSolicitudes] = useState([])
  const [loading,     setLoading]     = useState(true)

  const cargarSolicitudes = useCallback(async () => {
    setLoading(true)
    try {
      const data = await solicitudesApi.misSolicitudes(token)
      setSolicitudes(Array.isArray(data) && data.length ? data : MOCK_SOLICITUDES)
    } catch {
      // Sin conexión al back → usamos mock
      setSolicitudes(MOCK_SOLICITUDES)
    } finally {
      setLoading(false)
    }
  }, [token])

  useEffect(() => { cargarSolicitudes() }, [cargarSolicitudes])

  // Actualizar badge del tab de solicitudes
  const tabsConBadge = TABS.map(t =>
    t.key === 'solicitudes' ? { ...t, badge: solicitudes.length || null } : t
  )

  const handleAceptar = async (sol) => {
    show(`✓ Trabajo aceptado — ${sol.localidad_evento}`, 'success')
    setSolicitudes(s => s.filter(x => x.id !== sol.id))
  }

  const handleRechazar = async (sol) => {
    show('Solicitud rechazada')
    setSolicitudes(s => s.filter(x => x.id !== sol.id))
  }

  return (
    <div>
      <PlomeroNavbar
        tabs={tabsConBadge}
        activeTab={tab}
        onTab={setTab}
        plomero={user}
      />

      <div className="page-body">

        {tab === 'solicitudes' && (
          <>
            <h1 className="hero-title" style={{ fontSize: '1.4rem' }}>Solicitudes entrantes</h1>
            <p className="hero-sub">El primero en aceptar queda asignado · La dirección se revela al aceptar</p>

            {loading ? (
              <div className="loading-grid">
                <div className="skeleton-card" />
                <div className="skeleton-card" />
              </div>
            ) : solicitudes.length === 0 ? (
              <div className="empty-state">
                <span>🎉</span>
                <p>No tenés solicitudes pendientes por ahora.</p>
              </div>
            ) : (
              <div className="solicitudes-grid">
                {solicitudes.map(s => (
                  <SolicitudCard
                    key={s.id}
                    solicitud={s}
                    onAceptar={handleAceptar}
                    onRechazar={handleRechazar}
                  />
                ))}
              </div>
            )}
          </>
        )}

        {tab === 'en_curso' && (
          <div className="empty-state">
            <span>✏</span>
            <p>No tenés trabajos en curso.</p>
          </div>
        )}

        {tab === 'agenda' && (
          <div className="empty-state">
            <span>📅</span>
            <p>Tu agenda está vacía.</p>
          </div>
        )}

        {tab === 'historial' && (
          <div className="empty-state">
            <span>📋</span>
            <p>Todavía no tenés trabajos finalizados.</p>
          </div>
        )}

      </div>
    </div>
  )
}
