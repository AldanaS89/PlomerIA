import { useEffect, useState } from 'react'
import { api } from '../api'

export default function HomeCliente() {
  const [nombreUsuario, setNombreUsuario] = useState('')
  const [descripcion, setDescripcion] = useState('')
  const [soloPlomeras, setSoloPlomeras] = useState(false)
  const [recomendados, setRecomendados] = useState([]) 
  const [mostrarResultados, setMostrarResultados] = useState(false)
  const [cargando, setCargando] = useState(false)

  useEffect(() => {
    const nombre = localStorage.getItem('nombre') || 'Aldana'
    setNombreUsuario(nombre)
  }, [])

  const solicitarPlomero = async (e) => {
    e.preventDefault()
    if (!descripcion.trim()) return
    
    setCargando(true)
    try {
      // Enviamos la solicitud al backend
      const respuesta = await api.crearSolicitud({ 
        descripcion_raw: descripcion,
        solo_mujeres: soloPlomeras,
        latitud_evento: -34.85, 
        longitud_evento: -58.38
      })
      
      // Al recibir la respuesta, mostramos a los 5 profesionales seleccionados
      setRecomendados(respuesta.plomeros_sugeridos_detallados || [])
      setMostrarResultados(true)
    } catch (err) {
      console.error(err)
      alert("Error al conectar con el servidor. Verifica que el Backend esté encendido.")
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="home-main-layout">
      <header className="top-bar">
        <span className="user-greeting">Hola, "{nombreUsuario}"</span>
        <button onClick={() => { localStorage.clear(); window.location.href='/'; }} className="btn-exit-dark">Salir</button>
      </header>

      <div className="brand-hero">
        <h1 className="brand-logo">PlomerIA.</h1>
        <p className="brand-tagline">Tu experto a la vuelta de casa.</p>
      </div>

      <div className="request-container">
        <div className="request-header">
          <h3>Nueva solicitud</h3>
          <p className="request-subtitle">Contanos tu problema y nosotros te ofrecemos las mejores opciones para vos.</p>
        </div>

        <form onSubmit={solicitarPlomero}>
          <textarea 
            value={descripcion} 
            onChange={(e) => setDescripcion(e.target.value)}
            placeholder="Escriba aquí..."
            className="main-textarea"
          />
          
          <div className="gender-filter">
            <div 
              onClick={() => setSoloPlomeras(!soloPlomeras)}
              className={`toggle-ui ${soloPlomeras ? 'is-active' : ''}`}
            >
              <div className="toggle-knob" />
            </div>
            <span className="toggle-text">Ver solo plomeras</span>
          </div>

          <button type="submit" className="btn-submit-action" disabled={cargando}>
            {cargando ? 'BUSCANDO PROFESIONALES...' : 'PEDIR PLOMERO'}
          </button>
        </form>
      </div>

      {mostrarResultados && (
        <div className="results-wrapper">
          <div className="results-top">
            <h3 style={{ margin: 0 }}>Mis Solicitudes</h3>
            <button onClick={() => setMostrarResultados(false)} className="btn-close-inline">
              Cerrar lista ×
            </button>
          </div>
          <p className="results-subtext">Estas son nuestras 5 recomendaciones para vos:</p>
          
          <div className="plumber-scroll-list">
            {recomendados.length > 0 ? (
              recomendados.map((p) => (
                <div key={p.id} className="plumber-card-item">
                  <div className="plumber-meta-info">
                    <strong className="p-name">“{p.nombre}”</strong>
                    <span className="p-stats">⭐ {p.calificacion} | {p.localidad}</span>
                  </div>
                  <button className="btn-view-availability" onClick={() => alert(`Calendario de ${p.nombre}`)}>
                    Ver disponibilidad horaria.
                  </button>
                </div>
              ))
            ) : (
              <p style={{ textAlign: 'center', color: '#7f8c8d' }}>No hay plomeros disponibles actualmente.</p>
            )}
          </div>
        </div>
      )}

      <style>{`
        .home-main-layout { max-width: 650px; margin: 0 auto; padding: 20px; font-family: 'Segoe UI', Tahoma, sans-serif; }
        .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .btn-exit-dark { background: #2c3e50; color: white; border: none; padding: 7px 18px; border-radius: 5px; cursor: pointer; }
        .brand-hero { text-align: center; margin-bottom: 40px; }
        .brand-logo { color: #3498db; font-size: 3.5rem; margin: 0; font-weight: 800; }
        .brand-tagline { color: #95a5a6; font-size: 1.1rem; }
        .request-container { border: 1px solid #ddd; border-radius: 15px; padding: 30px; background: #fff; box-shadow: 0 4px 20px rgba(0,0,0,0.06); }
        .request-header h3 { margin: 0; font-size: 1.4rem; color: #2c3e50; }
        .request-subtitle { font-size: 0.9rem; color: #95a5a6; margin-bottom: 20px; }
        .main-textarea { width: 100%; height: 120px; padding: 15px; border: 2px solid #2c3e50; border-radius: 10px; box-sizing: border-box; font-size: 1.1rem; resize: none; outline: none; }
        .gender-filter { display: flex; align-items: center; gap: 12px; margin: 20px 0; }
        .toggle-ui { width: 48px; height: 24px; background: #bdc3c7; border-radius: 20px; position: relative; cursor: pointer; transition: 0.3s; }
        .toggle-ui.is-active { background: #ffc0cb; }
        .toggle-knob { width: 18px; height: 18px; background: #fff; border-radius: 50%; position: absolute; top: 3px; left: 4px; transition: 0.3s; }
        .toggle-ui.is-active .toggle-knob { left: 26px; }
        .btn-submit-action { width: 100%; background: #2ecc71; color: white; border: none; padding: 16px; border-radius: 10px; font-weight: bold; cursor: pointer; font-size: 1.1rem; }
        .results-wrapper { margin-top: 35px; border: 2px solid #2c3e50; border-radius: 15px; padding: 25px; background: #fafafa; }
        .results-top { display: flex; justify-content: space-between; align-items: center; }
        .btn-close-inline { background: none; border: none; color: #e74c3c; font-weight: bold; cursor: pointer; text-decoration: underline; font-size: 0.9rem; }
        .plumber-card-item { display: flex; justify-content: space-between; align-items: center; border: 1px solid #ddd; border-radius: 50px; padding: 14px 25px; margin-bottom: 12px; background: #fff; box-shadow: 0 2px 5px rgba(0,0,0,0.03); }
        .btn-view-availability { background: #2c3e50; color: white; border: none; padding: 10px 18px; border-radius: 25px; font-size: 0.75rem; cursor: pointer; }
      `}</style>
    </div>
  );
}