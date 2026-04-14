// Manejo simple de sesión en localStorage

export function guardarSesion({ token, tipo, nombre, id }) {
  localStorage.setItem('token', token)
  localStorage.setItem('tipo', tipo)
  localStorage.setItem('nombre', nombre)
  localStorage.setItem('id', String(id))
}

export function leerSesion() {
  const token = localStorage.getItem('token')
  if (!token) return null
  return {
    token,
    tipo: localStorage.getItem('tipo'),
    nombre: localStorage.getItem('nombre'),
    id: Number(localStorage.getItem('id')),
  }
}

export function cerrarSesion() {
  localStorage.clear()
}
