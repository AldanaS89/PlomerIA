import api from './api'

export const loginUsuario = (body) =>
  api.post('/usuarios/login', body).then((r) => r.data)

export const loginPlomero = (body) =>
  api.post('/plomeros/login', body).then((r) => r.data)

export const registroUsuario = (body) =>
  api.post('/usuarios/registro', body).then((r) => r.data)

export const registroPlomero = (body) =>
  api.post('/plomeros/registro', body).then((r) => r.data)

export const olvidarPasswordUsuario = (email) =>
  api.post('/usuarios/olvide-password', { email }).then((r) => r.data)

export const olvidarPasswordPlomero = (email) =>
  api.post('/plomeros/olvide-password', { email }).then((r) => r.data)

export const resetPassword = ({ token, nueva_password }) =>
  api.post('/usuarios/reset-password', { token, nueva_password }).then((r) => r.data)

// Login unificado — intenta usuario, si falla intenta plomero
export const login = async ({ email, password }) => {
  try {
    const data = await loginUsuario({ email, password })
    return { ...data, rol: data.rol || 'cliente' }
  } catch {
    const data = await loginPlomero({ email, password })
    return { ...data, rol: 'plomero' }
  }
}