// src/components/ProtectedRoute.jsx
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function ProtectedRoute({ children, requiredRole }) {
  const { token, role } = useAuth()
  if (!token) return <Navigate to="/" replace />
  if (requiredRole && role !== requiredRole) {
    return <Navigate to={role === 'plomero' ? '/plomero' : '/usuario'} replace />
  }
  return children
}
