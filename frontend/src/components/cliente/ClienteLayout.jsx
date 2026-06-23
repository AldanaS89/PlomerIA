import { NavLink, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { Wrench, Home, Briefcase, Bell, LogOut, Menu, X } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { useQuery } from '@tanstack/react-query'
// import { getAlertas } from '../../services/clienteService'

export default function ClienteLayout({ children }) {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [menuOpen, setMenuOpen] = useState(false)

  // const { data: alertas = [] } = useQuery({
  //   queryKey: ['alertas'],
  //   queryFn: getAlertas,
  //   refetchInterval: 30_000,
  // })

  const handleLogout = () => { logout(); navigate('/login') }

  const navItems = [
    { to: '/cliente', icon: Home, label: 'Inicio', end: true },
    { to: '/cliente/trabajos', icon: Briefcase, label: 'Mis trabajos' },
    { to: '/cliente/alertas', icon: Bell, label: 'Alertas', badge: alertas.length },
  ]

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-navy text-white sticky top-0 z-50 shadow-lg">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-brand-500 rounded-lg flex items-center justify-center">
              <Wrench className="w-4 h-4 text-white" />
            </div>
            <span className="font-display font-bold text-lg">
              Plomer<span className="text-brand-400">IA</span>
            </span>
          </div>

          <nav className="hidden md:flex items-center gap-1">
            {navItems.map(({ to, icon: Icon, label, badge, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  `relative flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-white/10 text-white'
                      : 'text-slate-300 hover:text-white hover:bg-white/5'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                {label}
                {badge > 0 && (
                  <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full text-[10px] flex items-center justify-center font-bold">
                    {badge}
                  </span>
                )}
              </NavLink>
            ))}
          </nav>

          <div className="flex items-center gap-3">
            {user && (
              <span className="hidden sm:block text-slate-300 text-sm">{user.nombre}</span>
            )}
            <button
              onClick={handleLogout}
              className="hidden sm:flex items-center gap-1 text-slate-400 hover:text-white text-xs"
            >
              <LogOut className="w-4 h-4" />
            </button>
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="md:hidden text-slate-300"
            >
              {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {menuOpen && (
          <div className="md:hidden bg-navy border-t border-white/10 px-4 pb-4 pt-2 space-y-1">
            {navItems.map(({ to, icon: Icon, label, badge, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                onClick={() => setMenuOpen(false)}
                className={({ isActive }) =>
                  `relative flex items-center gap-2 px-3 py-2 rounded-lg text-sm ${
                    isActive ? 'bg-white/10 text-white' : 'text-slate-300'
                  }`
                }
              >
                <Icon className="w-4 h-4" />
                {label}
                {badge > 0 && (
                  <span className="ml-auto w-5 h-5 bg-red-500 rounded-full text-[10px] flex items-center justify-center font-bold">
                    {badge}
                  </span>
                )}
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
