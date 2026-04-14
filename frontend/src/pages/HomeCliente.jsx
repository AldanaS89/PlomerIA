import { useEffect, useState } from 'react'
import { api } from '../api'

function formatoFecha(f) {
  try {
    return new Date(f).toLocaleString('es-AR')
  } catch {
    return f
  }
}

function formatoPesos(n) {
  if (n == null) return '—'
  return `$${Math.round(n).toLocaleString('es-AR')}`
}

export default function HomeCliente() {
  const [descripcion, setDescripcion] = useState('')
  const [solicitudes, setSolicitudes] = useState([])
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)
  const [enviando, setEnviando] = useState(false)

  async function cargar() {
    setCargando(true)
    try {
      const lista = await api.misSolicitudes()
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

  async function crear(e) {
    e.preventDefault()
    setError('')
    setEnviando(true)
    try {
      await api.crearSolicitud({ descripcion_raw: descripcion })
      setDescripcion('')
      await cargar()
    } catch (err) {
      setError(err.message)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <>
      <form className="card" onSubmit={crear}>
        <h2>Nueva solicitud</h2>
        <p className="muted">
          Describí tu problema con tus palabras. La IA va a clasificarlo y asignarte
          un plomero automáticamente.
        </p>
        <div className="form-group">
          <textarea
            value={descripcion}
            onChange={(e) => setDescripcion(e.target.value)}
            placeholder="Ej: Tengo una pérdida de agua debajo de la pileta de la cocina..."
            required
          />
        </div>
        {error && <div className="error">{error}</div>}
        <button type="submit" disabled={enviando || !descripcion.trim()}>
          {enviando ? 'Analizando con IA…' : 'Pedir plomero'}
        </button>
      </form>

      <h2>Mis solicitudes</h2>
      {cargando && <p className="muted">Cargando…</p>}
      {!cargando && solicitudes.length === 0 && (
        <p className="muted">Todavía no hiciste ninguna solicitud.</p>
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
          <div className="row">
            {s.etiqueta_ia && (
              <div>
                <div className="muted">Diagnóstico IA</div>
                <strong>{s.etiqueta_ia}</strong>
              </div>
            )}
            {s.urgencia_ia && (
              <div>
                <div className="muted">Urgencia</div>
                <span className={`badge urgencia-${s.urgencia_ia}`}>{s.urgencia_ia}</span>
              </div>
            )}
            <div>
              <div className="muted">Presupuesto estimado</div>
              <strong>
                {formatoPesos(s.presupuesto_min)} – {formatoPesos(s.presupuesto_max)}
              </strong>
            </div>
          </div>
          <div className="muted" style={{ marginTop: '0.5rem' }}>
            {s.id_plomero ? `Plomero asignado: #${s.id_plomero}` : 'Sin plomero asignado'}
          </div>
        </div>
      ))}
    </>
  )
}
