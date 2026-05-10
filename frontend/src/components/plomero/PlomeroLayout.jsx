import { NavLink, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { Wrench, Bell, Calendar, History, PlayCircle, Menu, X, LogOut } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { useMutation } from '@tanstack/react-query'
import { setDisponibilidad } from '../../services/plomeroService'

export default function PlomeroLayout({ children }) {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [menuOpen, setMenuOpen] = useState(false)
  const [activo, setActivo] = useState(true)

  const disponMut = useMutation({
    mutationFn: setDisponibilidad,
    onSuccess: (_, v) => setActivo(v),
  })

  const handleLogout = () => { logout(); navigate('/login') }

  const navItems = [
    { to: '/plomero/solicitudes', icon: Bell, label: 'Solicitudes' },
    { to: '/plomero/en-curso', icon: PlayCircle, label: 'En curso' },
    { to: '/plomero/agenda', icon: Calendar, label: 'Mi agenda' },
    { to: '/plomero/historial', icon: History, label: 'Historial' },
  ]

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      <header className="bg-navy text-white sticky top-0 z-50 shadow-lg">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-brand-500 rounded-lg flex items-center justify-center">
              <Wrench className="w-4 h-4 text-white" />
            </div>
            <span className="font-display font-bold text-lg">
              Plomer<span className="text-brand-400">IA</span>
            </span>
            {user && (
              <span className="hidden sm:block text-slate-400 text-xs ml-1">
                · {user.nombre}
              </span>
            )}
          </div>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-white/10 text-white'
                      : 'text-slate-300 hover:text-white hover:bg-white/5'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                {label}
              </NavLink>
            ))}
          </nav>

          {/* Right side */}
          <div className="flex items-center gap-3">
            {/* Disponibilidad toggle */}
            <div className="hidden sm:flex items-center gap-2 text-xs">
              <span className="text-slate-400">{activo ? 'Activo' : 'Inactivo'}</span>
              <button
                onClick={() => disponMut.mutate(!activo)}
                className={`relative w-10 h-5 rounded-full transition-colors ${
                  activo ? 'bg-emerald-500' : 'bg-slate-600'
                }`}
              >
                <span
                  className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${
                    activo ? 'translate-x-5' : 'translate-x-0.5'
                  }`}
                />
              </button>
            </div>

            <button
              onClick={handleLogout}
              className="hidden sm:flex items-center gap-1 text-slate-400 hover:text-white text-xs"
            >
              <LogOut className="w-4 h-4" />
            </button>

            {/* Mobile hamburger */}
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="md:hidden text-slate-300"
            >
              {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {menuOpen && (
          <div className="md:hidden bg-navy border-t border-white/10 px-4 pb-4 pt-2 space-y-1">
            {navItems.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                onClick={() => setMenuOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-2 px-3 py-2 rounded-lg text-sm ${
                    isActive ? 'bg-white/10 text-white' : 'text-slate-300'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                {label}
              </NavLink>
            ))}
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-3 py-2 text-slate-400 text-sm w-full"
            >
              <LogOut className="w-4 h-4" /> Cerrar sesión
            </button>
          </div>
        )}
      </header>

      <main className="flex-1 bg-slate-50">{children}</main>
    </div>
  )
}
