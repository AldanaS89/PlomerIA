import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { Eye, EyeOff, Wrench, CheckCircle2, AlertCircle } from 'lucide-react'
import { resetPassword } from '../services/authService'

export default function ResetPasswordPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')

  const [pass, setPass] = useState('')
  const [pass2, setPass2] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [error, setError] = useState('')

  const mut = useMutation({
    mutationFn: resetPassword,
    onError: (err) =>
      setError(err?.response?.data?.detail ?? 'Token inválido o ya usado.'),
  })

  const handleSubmit = () => {
    setError('')
    if (!pass || pass.length < 6) return setError('La contraseña debe tener al menos 6 caracteres')
    if (pass !== pass2) return setError('Las contraseñas no coinciden')
    if (!token) return setError('Token inválido. Pedí un nuevo link.')
    mut.mutate({ token, nueva_password: pass })
  }

  // Sin token en la URL
  if (!token) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-100 to-blue-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm p-8 text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
          <h2 className="font-semibold text-slate-800 text-lg mb-2">Link inválido</h2>
          <p className="text-sm text-slate-500 mb-5">
            Este link no es válido o ya fue utilizado. Pedí uno nuevo desde el login.
          </p>
          <button
            onClick={() => navigate('/login')}
            className="w-full bg-brand-600 hover:bg-brand-700 text-white font-semibold py-3 rounded-xl text-sm transition-colors"
          >
            Ir al login
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 to-blue-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 sm:p-8">

        {/* Logo */}
        <div className="flex items-center justify-center gap-2 mb-6">
          <div className="w-9 h-9 bg-brand-600 rounded-xl flex items-center justify-center">
            <Wrench className="w-4 h-4 text-white" />
          </div>
          <span className="font-display text-xl font-bold text-slate-800">
            Plomer<span className="text-brand-600">IA</span>
          </span>
        </div>

        {mut.isSuccess ? (
          <div className="text-center py-2">
            <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
            <h2 className="font-semibold text-slate-800 text-lg mb-2">¡Contraseña actualizada!</h2>
            <p className="text-sm text-slate-500 mb-6">
              Ya podés ingresar con tu nueva contraseña.
            </p>
            <button
              onClick={() => navigate('/login')}
              className="w-full bg-brand-600 hover:bg-brand-700 text-white font-semibold py-3 rounded-xl text-sm transition-colors"
            >
              Ir al login →
            </button>
          </div>
        ) : (
          <>
            <h2 className="text-center text-xl font-semibold text-slate-800 mb-1">
              Nueva contraseña
            </h2>
            <p className="text-center text-sm text-slate-500 mb-6">
              Elegí una contraseña nueva para tu cuenta.
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wide mb-1">
                  Nueva contraseña
                </label>
                <div className="relative">
                  <input
                    type={showPass ? 'text' : 'password'}
                    placeholder="Mínimo 6 caracteres"
                    value={pass}
                    onChange={(e) => setPass(e.target.value)}
                    className="w-full border border-slate-200 rounded-xl px-4 py-3 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPass(!showPass)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  >
                    {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wide mb-1">
                  Repetir contraseña
                </label>
                <input
                  type={showPass ? 'text' : 'password'}
                  placeholder="Repetí la contraseña"
                  value={pass2}
                  onChange={(e) => setPass2(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
                  className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-400"
                />
              </div>
            </div>

            {error && (
              <p className="mt-3 text-sm text-red-500 text-center">{error}</p>
            )}

            <button
              onClick={handleSubmit}
              disabled={mut.isPending}
              className="mt-5 w-full bg-brand-600 hover:bg-brand-700 disabled:bg-slate-200 disabled:text-slate-400 text-white font-semibold py-3 rounded-xl text-sm transition-colors"
            >
              {mut.isPending ? 'Guardando...' : 'Guardar contraseña →'}
            </button>
          </>
        )}
      </div>
    </div>
  )
}
