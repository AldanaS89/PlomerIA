import api from './api'

export const login = async ({ email, password }) => {
  const params = new URLSearchParams()
  params.append('username', email)
  params.append('password', password)

  const { data } = await api.post('/usuarios/login', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })

  return data
}

export const register = async (payload) => {
  const { data } = await api.post('/usuarios/registro', payload)
  return data
}

export const getMe = async () => {
  const { data } = await api.get('/usuarios/perfil')
  return data
}

export const olvidarPassword = async (email) => {
  const { data } = await api.post('/usuarios/olvide-password', { email })
  return data
}

export const resetPassword = async ({ token, nueva_password }) => {
  const { data } = await api.post('/usuarios/reset-password', {
    token,
    nueva_password,
  })
  return data
}