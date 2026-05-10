import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: { 'Content-Type': 'application/json' },
})

// Inject JWT on every request
api.interceptors.request.use((config) => {
  const raw = localStorage.getItem('plomeria-auth')
  if (raw) {
    const { state } = JSON.parse(raw)
    if (state?.token) {
      config.headers.Authorization = `Bearer ${state.token}`
    }
  }
  return config
})

// Global 401 → redirect to login
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('plomeria-auth')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
