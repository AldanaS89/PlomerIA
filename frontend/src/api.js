const BASE = '/api'

function getToken() {
  return localStorage.getItem('token')
}

async function request(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  if (auth) {
    const token = getToken()
    if (token) headers['Authorization'] = `Bearer ${token}`
  }
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(data.detail || `Error ${res.status}`)
  }
  return data
}

export const api = {
  // Auth cliente
  registroCliente: (d) => request('/auth/registro', { method: 'POST', body: d, auth: false }),
  loginCliente: (d) => request('/auth/login', { method: 'POST', body: d, auth: false }),

  // Auth plomero
  registroPlomero: (d) => request('/plomeros/registro', { method: 'POST', body: d, auth: false }),
  loginPlomero: (d) => request('/plomeros/login', { method: 'POST', body: d, auth: false }),

  // Cliente
  crearSolicitud: (d) => request('/solicitudes/', { method: 'POST', body: d }),
  misSolicitudes: () => request('/solicitudes/mis-solicitudes'),

  // Plomero
  solicitudesAsignadas: () => request('/solicitudes/asignadas'),
  aceptarSolicitud: (id) => request(`/solicitudes/${id}/aceptar`, { method: 'PATCH' }),
  rechazarSolicitud: (id) => request(`/solicitudes/${id}/rechazar`, { method: 'PATCH' }),
  cambiarDisponibilidad: (disponible) =>
    request(`/plomeros/disponibilidad?disponible=${disponible}`, { method: 'PATCH' }),
}
