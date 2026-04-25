import { useState, useEffect } from 'react'
import { leerSesion, cerrarSesion } from './auth'
import Login from './pages/Login.jsx'
import Registro from './pages/Registro.jsx'
import HomeCliente from './pages/HomeCliente.jsx'
import HomePlomero from './pages/HomePlomero.jsx'

export default function App() {
  const [sesion, setSesion] = useState(null)
  const [vista, setVista] = useState('login') // login | registro

  useEffect(() => {
    setSesion(leerSesion())
  }, [])

  function handleLogout() {
    cerrarSesion()
    setSesion(null)
    setVista('login')
  }

  if (sesion) {
    return (
      <div className="app">
        <header>
          <h1>PlomerIA</h1>
          <div>
            <span className="muted">Hola, {sesion.nombre}</span>
            <button className="ghost" onClick={handleLogout} style={{ marginLeft: '1rem' }}>
              Salir
            </button>
          </div>
        </header>
        {sesion.tipo === 'usuario' ? (
          <HomeCliente sesion={sesion} />
        ) : (
          <HomePlomero sesion={sesion} />
        )}
      </div>
    )
  }

  return (
    <div className="app">
      <header>
        <h1>PlomerIA</h1>
      </header>
      <div className="tabs">
        <button
          className={vista === 'login' ? 'active' : ''}
          onClick={() => setVista('login')}
        >
          Iniciar sesión
        </button>
        <button
          className={vista === 'registro' ? 'active' : ''}
          onClick={() => setVista('registro')}
        >
          Registrarme
        </button>
      </div>
      {vista === 'login' ? (
        <Login onLogin={setSesion} />
      ) : (
        <Registro onRegistrado={() => setVista('login')} />
      )}
    </div>
  )
}
