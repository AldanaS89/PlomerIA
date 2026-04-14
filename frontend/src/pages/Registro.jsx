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
    direccion: '',
    latitud: -34.8,
    longitud: -58.4,
    // plomero
    especialidad: 'PLOMERIA_GENERAL',
    genero: 'M',
    localidad: '',
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
      if (tipo === 'usuario') {
        await api.registroCliente({
          nombre: form.nombre,
          apellido: form.apellido,
          email: form.email,
          password: form.password,
          direccion: form.direccion,
          telefono: form.telefono,
          latitud: Number(form.latitud),
          longitud: Number(form.longitud),
        })
      } else {
        await api.registroPlomero({
          nombre: form.nombre,
          apellido: form.apellido,
          email: form.email,
          password: form.password,
          telefono: form.telefono,
          especialidad: form.especialidad,
          genero: form.genero,
          localidad: form.localidad,
          atiende_urgencias: form.atiende_urgencias,
          matricula_gas: form.matricula_gas,
        })
      }
      setOk('¡Registro exitoso! Ya podés iniciar sesión.')
      setTimeout(() => onRegistrado(), 1500)
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
          <option value="usuario">Cliente</option>
          <option value="plomero">Plomero</option>
        </select>
      </div>
      <div className="row">
        <div className="form-group">
          <label>Nombre</label>
          <input value={form.nombre} onChange={(e) => upd('nombre', e.target.value)} required />
        </div>
        <div className="form-group">
          <label>Apellido</label>
          <input value={form.apellido} onChange={(e) => upd('apellido', e.target.value)} required />
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
        <input value={form.telefono} onChange={(e) => upd('telefono', e.target.value)} required />
      </div>

      {tipo === 'usuario' ? (
        <>
          <div className="form-group">
            <label>Dirección</label>
            <input value={form.direccion} onChange={(e) => upd('direccion', e.target.value)} required />
          </div>
          <div className="row">
            <div className="form-group">
              <label>Latitud</label>
              <input type="number" step="any" value={form.latitud} onChange={(e) => upd('latitud', e.target.value)} />
            </div>
            <div className="form-group">
              <label>Longitud</label>
              <input type="number" step="any" value={form.longitud} onChange={(e) => upd('longitud', e.target.value)} />
            </div>
          </div>
        </>
      ) : (
        <>
          <div className="form-group">
            <label>Especialidad</label>
            <select value={form.especialidad} onChange={(e) => upd('especialidad', e.target.value)}>
              {ESPECIALIDADES.map((es) => (
                <option key={es} value={es}>{es}</option>
              ))}
            </select>
          </div>
          <div className="row">
            <div className="form-group">
              <label>Género</label>
              <select value={form.genero} onChange={(e) => upd('genero', e.target.value)}>
                <option value="M">M</option>
                <option value="F">F</option>
              </select>
            </div>
            <div className="form-group">
              <label>Localidad</label>
              <input value={form.localidad} onChange={(e) => upd('localidad', e.target.value)} required />
            </div>
          </div>
          <div className="form-group">
            <label className="toggle">
              <input
                type="checkbox"
                checked={form.atiende_urgencias}
                onChange={(e) => upd('atiende_urgencias', e.target.checked)}
              />
              Atiende urgencias
            </label>
          </div>
          <div className="form-group">
            <label className="toggle">
              <input
                type="checkbox"
                checked={form.matricula_gas}
                onChange={(e) => upd('matricula_gas', e.target.checked)}
              />
              Matrícula de gas
            </label>
          </div>
        </>
      )}

      {error && <div className="error">{error}</div>}
      {ok && <div className="success-msg">{ok}</div>}
      <button type="submit" disabled={cargando}>
        {cargando ? 'Creando…' : 'Crear cuenta'}
      </button>
    </form>
  )
}
