const BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

function getToken() {
  return localStorage.getItem('token');
}

async function request(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  
  if (auth) {
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  // Manejo de errores de autenticación
  if (res.status === 401 && auth) {
    console.error('Sesión expirada o no autorizada');
  }

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data.detail || `Error ${res.status}`);
  }

  return data;
}

export const api = {
  // Autenticación
  registroCliente:  (d) => request('/auth/registro', { method: 'POST', body: d, auth: false }),
  loginCliente:     (d) => request('/auth/login',    { method: 'POST', body: d, auth: false }),
  registroPlomero:  (d) => request('/plomeros/registro', { method: 'POST', body: d, auth: false }),
  loginPlomero:     (d) => request('/plomeros/login',    { method: 'POST', body: d, auth: false }),

  // Solicitudes (Aquí es donde viajan tus 100 plomeros)
  crearSolicitud:   (d) => request('/solicitudes/', { method: 'POST', body: d }),
  misSolicitudes:   ()  => request('/solicitudes/mis-solicitudes'),
  
  // Disponibilidad y Agenda
  verDisponibilidad: (idPlomero) => request(`/disponibilidad/${idPlomero}`),

  // Funciones para el perfil del plomero
  solicitudesAsignadas: ()    => request('/solicitudes/asignadas'),
  aceptarSolicitud:     (id)  => request(`/solicitudes/${id}/aceptar`, { method: 'PATCH' }),
  rechazarSolicitud:    (id)  => request(`/solicitudes/${id}/rechazar`, { method: 'PATCH' }),
  cambiarDisponibilidad:(disp) => request(`/plomeros/disponibilidad?disponible=${disp}`, { method: 'PATCH' }),
};