import axios from 'axios';

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

// Si en plena sesi