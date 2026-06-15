import api from './api'

// ── VALIDAR FOTO — llamado en el paso 1 antes de avanzar ─────────────────────
export async function validarFotoPlomero(file) {
  const fd = new FormData()
  fd.append('foto', file)
  const res = await api.post('/plomeros/validar-foto', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export async function registerPlomero(payload) {
  const fd = new FormData()
  Object.entries(payload).forEach(([k, v]) => {
    if (k === 'confirmar') return
    if (k === 'foto' && v instanceof File) {
      fd.append('foto', v)
    } else if (k === 'especialidades' && Array.isArray(v)) {
      fd.append('especialidades', JSON.stringify(v))
    } else if (k === 'agenda' && typeof v === 'object' && v !== null) {
      fd.append('agenda', JSON.stringify(v))
    } else if (v !== null && v !== undefined) {
      fd.append(k, String(v))
    }
  })
  const res = await api.post('/plomeros/registro', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export async function loginPlomero(datos) {
  const res = await api.post('/plomeros/login', datos)
  return res.data
}

export async function getMisSolicitudesPlomero() {
  const res = await api.get('/solicitudes/plomero/me')
  return Array.isArray(res.data) ? res.data : []
}

export async function aceptarSolicitud(id) {
  const res = await api.patch(`/solicitudes/${id}/aceptar`)
  return res.data
}

export async function rechazarSolicitud(id) {
  const res = await api.patch(`/solicitudes/${id}/rechazar`)
  return res.data
}

export async function completarSolicitud(id) {
  const res = await api.patch(`/solicitudes/${id}/completar`)
  return res.data
}

export async function cambiarDisponibilidad(disponible) {
  const res = await api.patch(`/plomeros/disponibilidad?disponible=${disponible}`)
  return res.data
}

export async function getAgenda(idPlomero) {
  const res = await api.get(`/disponibilidad/${idPlomero}`)
  return res.data
}