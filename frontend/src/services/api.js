import axios from 'axios';

// baseURL relativa: el navegador la resuelve contra el origen actual y deja
// que el proxy (nginx en producción / vite en desarrollo) la reenvíe al backend.
// Hardcodear http://localhost:8000 rompe el despliegue Docker, donde el puerto
// 8000 del backend no está publicado al host.
const api = axios.create({
  baseURL: '/api',
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

export default api;