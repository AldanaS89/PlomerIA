import api from './api'

export const crearSolicitud = (body) =>
  api.post('/solicitudes/', body).then((r) => r.data)

export const misSolicitudes = () =>
  api.get('/solicitudes/mis-solicitudes').then((r) => r.data)

export const solicitudesAsignadas = () =>
  api.get('/solicitudes/asignadas').then((r) => r.data)

export const aceptarSolicitud = (id) =>
  api.patch(`/solicitudes/${id}/aceptar`).then((r) => r.data)

export const rechazarSolicitud = (id) =>
  api.patch(`/solicitudes/${id}/rechazar`).then((r) => r.data)

export const completarSolicitud = (id) =>
  api.patch(`/solicitudes/${id}/completar`).then((r) => r.data)