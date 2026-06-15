import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      token: null,
      user: null,   // { id, nombre, email, rol: 'cliente' | 'plomero' }

      setAuth: (token, user) => set({ token, user }),

      logout: () => {
        set({ token: null, user: null })
      },

      isAuthenticated: () => !!get().token,
      isPlomero: () => get().user?.rol === 'plomero',
      isCliente: () => get().user?.rol === 'cliente',
    }),
    {
      name: 'plomeria-auth',
    }
  )
)
