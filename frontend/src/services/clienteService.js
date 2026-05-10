import api from './api'

/** POST /api/solicitudes — crear nueva solicitud */
export const crearSolicitud = async (payload) => {
  const { data } = await api.post('/solicitudes', payload)
  return data
}



