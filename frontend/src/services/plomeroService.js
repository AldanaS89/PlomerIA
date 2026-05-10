import api from './api'

/* =========================
   AUTH PLOMERO
========================= */
export const registerPlomero = async (payload) => {
  const { data } = await api.post('/plomeros/registro', payload)
  return data
}

export const loginPlomero = async ({ email, password }) => {
  const params = new URLSearchParams()
  params.append('username', email)
  params.append('password', password)

  const { data } = await api.post('/plomeros/login', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })

  return data
}

/* =========================
   SOLICITUDES
========================= */
export const getMisSolicitudesPlomero = async () => {
  const { data } = await api.get('/solicitudes/plomero/me')
  return data
}

export const aceptarSolicitud = async (id) => {
  const { data } = await api.post(`/solicitudes/${id}/aceptar`)
  return data
}

export const rechazarSolicitud = async (id) => {
  const { data } = await api.post(`/solicitudes/${id}/rechazar`)
  return data
}

/* =========================
   DISPONIBILIDAD
========================= */
export const setDisponibilidad = async (disponible) => {
  const { data } = await api.patch(
    `/plomeros/disponibilidad?disponible=${disponible}`
  )
  return data
}