import { useEffect, useState } from 'react'
import { api } from '../api'

function formatoFecha(f) {
  try {
    return new Date(f).toLocaleString('es-AR')
  } catch {
    return f
  }
}

export default function HomePlomero() {
  const [solicitudes, setSolicitudes] = useState([])
  const [disponible, setDisponible] = useState(true)
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState('')

  async function cargar() {
    setCargando(true)
    try {
      const lista = await api.solicitudesAsignadas()
      setSolicitudes(lista)
    } catch (err) {
      setError(err.message)
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargar()
  }, [])

  async function toggleDisp() {
    try {
      const nuevo = !disponible
      await api.cambiarDisponibilidad(nuevo)
      setDisponible(nuevo)
    } catch (err) {
      setError(err.message)
    }
  }

  async function aceptar(id) {
    try {
      await api.aceptarSolicitud(id)
      await cargar()
    } catch (err) {
      setError(err.message)
    }
  }

  async function rechazar(id) {
    try {
      await api.rechazarSolicitud(id)
      await cargar()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <>
      <div className="card">
        <div className="toggle" style={{ justifyContent: 'space-between' }}>
          <div>
            <strong>Estado:</strong>{' '}
            <span className={`badge ${disponible ? 'aceptado' : 'rechazado'}`}>
              {disponible ? 'Disponible' : 'No disponible'}
            </span>
          </div>
          <button className={disponible ? 'danger' : 'success'} onClick={toggleDisp}>
            {disponible ? 'Marcarme no disponible' : 'Marcarme disponible'}
          </button>
        </div>
      </div>

      <h2>Solicitudes asignadas</h2>
      {error && <div className="error">{error}</div>}
      {cargando && <p className="muted">Cargando…</p>}
      {!cargando && solicitudes.length === 0 && (
        <p className="muted">No tenés solicitudes asignadas.</p>
      )}
      {solicitudes.map((s) => (
        <div className="card" key={s.id_solicitud}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
            <strong>#{s.id_solicitud}</strong>
            <span className={`badge ${s.estado.toLowerCase()}`}>{s.estado}</span>
          </div>
          <p style={{ margin: '0.5rem 0' }}>{s.descripcion_raw}</p>
          <div className="muted" style={{ marginBottom: '0.5rem' }}>
            {formatoFecha(s.fecha)}
          </div>
          <div className="row" style={{ marginBottom: '0.75rem' }}>
            {s.etiqueta_ia && (
              <div>
                <div className="muted">Tipo</div>
                <strong>{s.etiqueta_ia}</strong>
              </div>
            )}
            {s.urgencia_ia && (
              <div>
                <div className="muted">Urgencia</div>
                <span className={`badge urgencia-${s.urgencia_ia}`}>{s.urgencia_ia}</span>
              </div>
            )}
          </div>
          {s.estado === 'pendiente' && (
            <div className="row">
              <button className="success" onClick={() => aceptar(s.id_solicitud)}>
                Aceptar
              </button>
              <button className="danger" onClick={() => rechazar(s.id_solicitud)}>
                Rechazar
              </button>
            </div>
          )}
        </div>
      ))}
    </>
  )
}
