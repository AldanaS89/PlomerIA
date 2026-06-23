// src/pages/Registro.jsx — Formulario de registro de CLIENTE
import { useState } from 'react'
import api from '../services/api'
import { useAuthStore } from '../store/authStore'
import DireccionConMapa from '../components/DireccionConMapa'
import TerminosCondiciones from '../components/TerminosCondiciones'

const LOCALIDADES = [
  "Adrogué","Burzaco","Claypole","Don Orione","Glew","José Mármol",
  "Longchamps","Ministro Rivadavia","Monte Grande","Rafael Calzada",
  "San Francisco de Asís","San José","Temperley","Turdera","Lomas de Zamora",
  "Banfield","Lanús","Avellaneda","Quilmes","Berazategui","Florencio Varela","Otra",
]

export default function Registro({ onNav }) {
  const setAuth = useAuthStore((s) => s.setAuth);

  const [form, setForm] = useState({
    nombre: '', apellido: '', email: '', password: '', confirmar: '',
    direccion: '', localidad: '', latitud: null, longitud: null,
  });
  const [error,    setError]    = useState('')
  const [cargando, setCargando] = useState(false)
  const [showPass, setShowPass] = useState(false)
  const [acepta,   setAcepta]   = useState(false)
  const [verTyC,   setVerTyC]   = useState(false)

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (form.password !== form.confirmar)
      return setError('Las contraseñas no coinciden')
    if (form.password.length < 6)
      return setError('La contraseña debe tener al menos 6 caracteres')
    if (!form.direccion.trim())
      return setError('Ingresá tu dirección')
    if (!form.localidad)
      return setError('Seleccioná tu localidad')
    if (!acepta)
      return setError('Tenés que aceptar las Bases y Condiciones para registrarte')

    setCargando(true)
    try {
      const res = await api.post('/usuarios/registro', {
        nombre:    form.nombre,
        apellido:  form.apellido,
        email:     form.email,
        password:  form.password,
        direccion: form.direccion,
        localidad: form.localidad,
        latitud:   form.latitud,
        longitud:  form.longitud,
        rol:       'cliente',
      })

      const usuario = {
        id:     res.data.id_usuario,
        nombre: res.data.nombre,
        rol:    'cliente',
      }
      setAuth(res.data.access_token, usuario)
      onNav('app')

    } catch (err) {
      setError(err.response?.data?.detail || 'Error al registrar. Intentá de nuevo.')
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="bg-white p-8 rounded-[2.5rem] shadow-xl w-full max-w-md border border-slate-100">

        {/* Logo */}
        <div className="flex justify-center mb-6">
          <div className="bg-blue-600 px-4 py-2 rounded-xl shadow-lg shadow-blue-100">
            <span className="text-white font-black text-2xl tracking-tighter">
              🔧 PlomerIA
            </span>
          </div>
        </div>

        <h2 className="text-2xl font-black text-center text-slate-800 mb-1">
          Crear cuenta de cliente
        </h2>
        <p className="text-slate-400 text-center text-sm mb-6">
          Completá tus datos para empezar
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[10px] font-black text-slate-400 mb-1 uppercase tracking-widest">
                Nombre
              </label>
              <input
                required type="text" placeholder="Carlos"
                value={form.nombre} onChange={set('nombre')}
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              />
            </div>
            <div>
              <label className="block text-[10px] font-black text-slate-400 mb-1 uppercase tracking-widest">
                Apellido
              </label>
              <input
                required type="text" placeholder="García"
                value={form.apellido} onChange={set('apellido')}
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              />
            </div>
          </div>

          {/* Dirección con mapa */}
          <DireccionConMapa
            direccion={form.direccion}
            localidad={form.localidad}
            latitud={form.latitud}
            longitud={form.longitud}
            onDireccionChange={(v) => setForm((f) => ({ ...f, direccion: v }))}
            onLocalidadChange={(v) => setForm((f) => ({ ...f, localidad: v }))}
            onCoordsChange={(lat, lon) => setForm((f) => ({ ...f, latitud: lat, longitud: lon }))}
            localidades={LOCALIDADES}
          />

          <div>
            <label className="block text-[10px] font-black text-slate-400 mb-1 uppercase tracking-widest">
              Email
            </label>
            <input
              required type="email" placeholder="tu@email.com"
              value={form.email} onChange={set('email')}
              className="w-full p-3 bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            />
          </div>

          <div>
            <label className="block text-[10px] font-black text-slate-400 mb-1 uppercase tracking-widest">
              Contraseña
            </label>
            <div className="relative">
              <input
                required type={showPass ? 'text' : 'password'}
                placeholder="Mínimo 6 caracteres"
                value={form.password} onChange={set('password')}
                className="w-full p-3 bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm pr-10"
              />
              <button type="button" onClick={() => setShowPass((p) => !p)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                {showPass ? '🙈' : '👁'}
              </button>
            </div>
          </div>

          <div>
            <label className="block text-[10px] font-black text-slate-400 mb-1 uppercase tracking-widest">
              Confirmar contraseña
            </label>
            <input
              required type={showPass ? 'text' : 'password'}
              placeholder="Repetí la contraseña"
              value={form.confirmar} onChange={set('confirmar')}
              className="w-full p-3 bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-2xl px-4 py-3">
              <p className="text-red-600 text-sm text-center">{error}</p>
            </div>
          )}

          {/* Bases y Condiciones — obligatorio para registrarse */}
          <label className="flex items-start gap-2 text-sm text-slate-600 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={acepta}
              onChange={(e) => setAcepta(e.target.checked)}
              className="mt-0.5 w-4 h-4 accent-blue-600"
            />
            <span>
              Leí y acepto las{' '}
              <button type="button" onClick={() => setVerTyC(true)}
                className="text-blue-600 font-semibold hover:underline">
                Bases y Condiciones
              </button>.
            </span>
          </label>

          <button
            type="submit" disabled={cargando || !acepta}
            className="w-full font-black py-4 rounded-2xl transition-all shadow-lg uppercase text-xs tracking-[0.2em] bg-blue-600 text-white hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed"
          >
            {cargando ? 'Registrando...' : 'Crear cuenta →'}
          </button>

          <p className="text-center text-sm text-slate-400 mt-2">
            ¿Ya tenés cuenta?{' '}
            <button type="button" onClick={() => onNav('login')}
              className="text-blue-600 hover:underline font-semibold">
              Ingresá
            </button>
          </p>
        </form>
      </div>

      <TerminosCondiciones open={verTyC} onClose={() => setVerTyC(false)} />
    </div>
  )
}