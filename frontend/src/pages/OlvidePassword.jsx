import { useState } from 'react';
import api from '../services/api';

export default function OlvidePassword({ onNav }) {
  const [email,    setEmail]    = useState('');
  const [enviado,  setEnviado]  = useState(false);
  const [cargando, setCargando] = useState(false);
  const [error,    setError]    = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setCargando(true);
    try {
      await api.post('/auth/forgot-password', { email });
      setEnviado(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al enviar. Intentá de nuevo.');
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6 font-sans">
      <div className="bg-white p-10 rounded-[2.5rem] shadow-xl w-full max-w-md text-center border border-slate-100">

        <div className="text-4xl mb-4">🔑</div>
        <h2 className="text-2xl font-black text-slate-800 mb-2">Recuperar acceso</h2>
        <p className="text-slate-400 text-sm mb-8">
          Te enviaremos un link para restablecer tu contraseña.
        </p>

        {enviado ? (
          <div className="space-y-4">
            <div className="bg-emerald-50 border border-emerald-200 rounded-2xl px-4 py-4">
              <p className="text-emerald-700 font-semibold text-sm">
                ✓ Si el email existe en el sistema, recibirás el link en tu casilla.
              </p>
            </div>
            <button
              onClick={() => onNav('login')}
              className="w-full border border-slate-200 hover:border-slate-300 bg-white text-slate-600 font-semibold py-3 rounded-2xl text-sm transition-colors"
            >
              ← Volver al inicio
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              required
              type="email"
              placeholder="Ingresá tu email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            />

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-2xl px-4 py-3">
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={cargando}
              className="w-full bg-blue-600 text-white font-black py-4 rounded-2xl shadow-lg shadow-blue-100 hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400 transition-all uppercase text-xs tracking-widest"
            >
              {cargando ? 'Enviando...' : 'Enviar link de reset'}
            </button>

            <button
              type="button"
              onClick={() => onNav('login')}
              className="w-full border border-slate-200 hover:border-slate-300 bg-white text-slate-600 font-semibold py-3 rounded-2xl text-sm transition-colors"
            >
              ← Volver al inicio
            </button>
          </form>
        )}
      </div>
    </div>
  );
}