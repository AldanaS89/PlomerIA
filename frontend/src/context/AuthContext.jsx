// src/context/AuthContext.jsx
import { createContext, useContext, useState, useCallback } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken]   = useState(() => localStorage.getItem('token') || null)
  const [role,  setRole]    = useState(() => localStorage.getItem('role')  || null)
  const [user,  setUser]    = useState(() => {
    try { return JSON.parse(localStorage.getItem('user')) } catch { return null }
  })

  const loginUser = useCallback((data) => {
    // data viene de POST /usuarios/login  → { access_token, ... }
    const tok = data.access_token
    setToken(tok)
    setRole('usuario')
    setUser(data.usuario ?? data)
    localStorage.setItem('token', tok)
    localStorage.setItem('role',  'usuario')
    localStorage.setItem('user',  JSON.stringify(data.usuario ?? data))
  }, [])

  const loginPlomero = useCallback((data) => {
    // data viene de POST /plomeros/login → { access_token, ... }
    const tok = data.access_token
    setToken(tok)
    setRole('plomero')
    setUser(data.plomero ?? data)
    localStorage.setItem('token', tok)
    localStorage.setItem('role',  'plomero')
    localStorage.setItem('user',  JSON.stringify(data.plomero ?? data))
  }, [])

  const logout = useCallback(() => {
    setToken(null); setRole(null); setUser(null)
    localStorage.clear()
  }, [])

  return (
    <AuthContext.Provider value={{ token, role, user, loginUser, loginPlomero, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
