import { useState } from 'react'
import { api } from '../api'
import { guardarSesion } from '../auth'

export default function Login({ onLogin }) {
  const [tipo, setTipo] = useState('usuario')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setCargando(true)
    try {
      const fn = tipo === 'usuario' ? api.loginCliente : api.loginPlomero
      const res = await fn({ email, password })
      const id = tipo === 'usuario' ? res.id_usuario : res.id_plomero
      guardarSesion({
        token: res.access_token,
        tipo,
        nombre: res.nombre,
        id,
      })
      onLogin({ token: res.access_token, tipo, nombre: res.nombre, id })
    } catch (err) {
      setError(err.message)
    } finally {
      setCargando(false)
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h2>Iniciar sesión</h2>
      <div className="form-group">
        <label>Soy</label>
        <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
          <option value="usuario">Cliente</option>
          <option value="plomero">Plomero</option>
        </select>
      </div>
      <div className="form-group">
        <label>Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </div>
      <div className="form-group">
        <label>Contraseña</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </div>
      {error && <div className="error">{error}</div>}
      <button type="submit" disabled={cargando}>
        {cargando ? 'Ingresando…' : 'Ingresar'}
      </button>
    </form>
  )
}
