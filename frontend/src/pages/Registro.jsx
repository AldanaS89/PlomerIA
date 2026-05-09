import { useState } from 'react'
import { api } from '../api'

const ESPECIALIDADES = ['PLOMERIA_GENERAL', 'DESTAPES', 'GAS_MATRICULADO', 'OBRA']

export default function Registro({ onRegistrado }) {
  const [tipo, setTipo] = useState('usuario')
  const [form, setForm] = useState({
    nombre: '',
    apellido: '',
    email: '',
    password: '',
    telefono: '',
    localidad: 'Longchamps', // Valor por defecto sugerido
    direccion: '',           // Campo obligatorio para el backend
    // Valores fijos temporales para que el backend no tire error 422
    latitud: -34.85,          
    longitud: -58.38,
    // Datos específicos de plomero
    especialidad: 'PLOMERIA_GENERAL',
    genero: 'M',
    atiende_urgencias: false,
    matricula_gas: false,
  })
  
  const [error, setError] = useState('')
  const [ok, setOk] = useState('')
  const [cargando, setCargando] = useState(false)

  function upd(k, v) {
    setForm({ ...form, [k]: v })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setOk('')
    setCargando(true)

    try {
      // Enviamos el objeto 'form' completo. 
      // Ahora incluye dirección, latitud y longitud, evitando el error 422.
      if (tipo === 'usuario') {
        await api.registroCliente(form)
      } else {
        await api.registroPlomero(form)
      }
      
      setOk('¡Registro exitoso! Ya puedes iniciar sesión.')
      if (onRegistrado) onRegistrado()
    } catch (err) {
      setError(err.message)
    } finally {
      setCargando(false)
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h2>Crear cuenta</h2>
      
      <div className="form-group">
        <label>Tipo de cuenta</label>
        <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
          <option value="usuario">Cliente (Busco plomero)</option>
          <option value="plomero">Plomero (Busco trabajo)</option>
        </select>
      </div>

      <div className="row">
        <div className="form-group">
          <label>Nombre</label>
          <input type="text" value={form.nombre} onChange={(e) => upd('nombre', e.target.value)} required />
        </div>
        <div className="form-group">
          <label>Apellido</label>
          <input type="text" value={form.apellido} onChange={(e) => upd('apellido', e.target.value)} required />
        </div>
      </div>

      <div className="form-group">
        <label>Email</label>
        <input type="email" value={form.email} onChange={(e) => upd('email', e.target.value)} required />
      </div>

      <div className="form-group">
        <label>Contraseña</label>
        <input type="password" value={form.password} onChange={(e) => upd('password', e.target.value)} required />
      </div>

      <div className="form-group">
        <label>Teléfono</label>
        <input type="text" value={form.telefono} onChange={(e) => upd('telefono', e.target.value)} required />
      </div>

      {/* --- CAMPOS DE UBICACIÓN REQUERIDOS --- */}
      <div className="form-group">
        <label>Dirección</label>
        <input 
          type="text" 
          placeholder="Ej: Av. Aviación 123" 
          value={form.direccion} 
          onChange={(e) => upd('direccion', e.target.value)} 
          required 
        />
      </div>

      <div className="form-group">
        <label>Localidad</label>
        <input type="text" value={form.localidad} onChange={(e) => upd('localidad', e.target.value)} required />
      </div>
      {/* ------------------------------------- */}

      {tipo === 'plomero' && (
        <>
          <div className="form-group">
            <label>Especialidad</label>
            <select value={form.especialidad} onChange={(e) => upd('especialidad', e.target.value)}>
              {ESPECIALIDADES.map((es) => (
                <option key={es} value={es}>{es}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Género</label>
            <select value={form.genero} onChange={(e) => upd('genero', e.target.value)}>
              <option value="M">M</option>
              <option value="F">F</option>
            </select>
          </div>
          <div className="form-group">
            <label className="toggle">
              <input type="checkbox" checked={form.atiende_urgencias} onChange={(e) => upd('atiende_urgencias', e.target.checked)} />
              Atiende urgencias
            </label>
          </div>
        </>
      )}

      {error && <div className="error">{error}</div>}
      {ok && <div className="success-msg">{ok}</div>}
      
      <button type="submit" disabled={cargando}>
        {cargando ? 'Registrando...' : 'Registrarme'}
      </button>
    </form>
  )
}