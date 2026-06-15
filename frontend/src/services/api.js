import axios from 'axios';
import { mostrarCartelSuspension } from '../utils/suspensionModal';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' }
});

api.interceptors.request.use((config) => {
  const raw = localStorage.getItem('plomeria-auth');
  if (raw) {
    try {
      const parsed = JSON.parse(raw);
      const token = parsed.state?.token;
      if (token) config.headers.Authorization = `Bearer ${token}`;
    } catch (e) { /* Si falla el parseo, no bloqueamos la petición */ }
  }
  return config;
});

// Si en plena sesión una acción devuelve "cuenta suspendida" (403), mostramos
// el cartel y cerramos la sesión automáticamente. No se aplica al login (ese
// error lo muestra la pantalla de login con los días que faltan).
api.interceptors.response.use(
  (resp) => resp,
  (error) => {
    const detail = error?.response?.data?.detail;
    const url = error?.config?.url || '';
    const esSuspension =
      error?.response?.status === 403 &&
      typeof detail === 'string' &&
      detail.toLowerCase().includes('suspendid');
    if (esSuspension && !url.includes('/auth/login')) {
      // Cartel propio de la app; al "Aceptar" cierra sesión y vuelve al login.
      mostrarCartelSuspension(detail, () => {
        try { localStorage.removeItem('plomeria-auth'); } catch (e) { /* noop */ }
        window.location.reload();
      });
      return new Promise(() => {});
    }
    return Promise.reject(error);
  }
);

export default api;
