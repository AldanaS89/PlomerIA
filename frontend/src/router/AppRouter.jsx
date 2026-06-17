import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

import LoginPage from '../pages/LoginPage'
import ResetPasswordPage from '../pages/ResetPasswordPage'
import PlomeroDashboard from '../pages/plomero/PlomeroDashboard'
import PlomeroAgenda from '../pages/plomero/PlomeroAgenda'
import PlomeroHistorial from '../pages/plomero/PlomeroHistorial'
import PlomeroEnCurso from '../pages/plomero/PlomeroEnCurso'
import ClienteHome from '../pages/cliente/ClienteHome'
import ClienteMisTrabajos from '../pages/cliente/ClienteMisTrabajos'
import ClienteAlertas from '../pages/cliente/ClienteAlertas'
import NotFound from '../pages/NotFound'
import RegisterPlomero from '../pages/plomero/RegisterPlomero'

// Guarda genérica
function RequireAuth({ children }) {
  const token = useAuthStore((s) => s.token)
  return token ? children : <Navigate to="/login" replace />
}

function RequireRole({ role, children }) {
  const user = useAuthStore((s) => s.user)
  if (!user) return <Navigate to="/login" replace />
  if (user.rol !== role) return <Navigate to="/" replace />
  return children
}

function RootRedirect() {
  const user = useAuthStore((s) => s.user)
  if (!user) return <Navigate to="/login" replace />
  if (user.rol === 'plomero') return <Navigate to="/plomero/solicitudes" replace />
  return <Navigate to="/cliente" replace />
}

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        3<Route path="/registro-plomero" element={<RegisterPlomero />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/" element={<RootRedirect />} />

        {/* --- PLOMERO --- */}
        <Route
          path="/plomero/solicitudes"
          element={
            <RequireAuth>
              <RequireRole role="plomero">
                <PlomeroDashboard />
              </RequireRole>
            </RequireAuth>
          }
        />
        <Route
          path="/plomero/en-curso"
          element={
            <RequireAuth>
              <RequireRole role="plomero">
                <PlomeroEnCurso />
              </RequireRole>
            </RequireAuth>
          }
        />
        <Route
          path="/plomero/agenda"
          element={
            <RequireAuth>
              <RequireRole role="plomero">
                <PlomeroAgenda />
              </RequireRole>
            </RequireAuth>
          }
        />
        <Route
          path="/plomero/historial"
          element={
            <RequireAuth>
              <RequireRole role="plomero">
                <PlomeroHistorial />
              </RequireRole>
            </RequireAuth>
          }
        />

        {/* --- CLIENTE --- */}
        <Route
          path="/cliente"
          element={
            <RequireAuth>
              <RequireRole role="cliente">
                <ClienteHome />
              </RequireRole>
            </RequireAuth>
          }
        />
        <Route
          path="/cliente/trabajos"
          element={
            <RequireAuth>
              <RequireRole role="cliente">
                <ClienteMisTrabajos />
              </RequireRole>
            </RequireAuth>
          }
        />
        <Route
          path="/cliente/alertas"
          element={
            <RequireAuth>
              <RequireRole role="cliente">
                <ClienteAlertas />
              </RequireRole>
            </RequireAuth>
          }
        />

        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  )
}
