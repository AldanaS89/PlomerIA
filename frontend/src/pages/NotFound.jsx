import { useNavigate } from 'react-router-dom'
import { Wrench } from 'lucide-react'

export default function NotFound() {
  const navigate = useNavigate()
  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-center p-8">
      <Wrench className="w-16 h-16 text-brand-200 mb-4" />
      <h1 className="font-display text-4xl font-bold text-slate-800 mb-2">404</h1>
      <p className="text-slate-500 mb-6">Esta página no existe o fue removida.</p>
      <button
        onClick={() => navigate('/')}
        className="bg-brand-600 hover:bg-brand-700 text-white font-semibold px-6 py-2.5 rounded-xl transition-colors"
      >
        Volver al inicio
      </button>
    </div>
  )
}
