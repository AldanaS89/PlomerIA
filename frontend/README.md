# PlomerIA — Frontend

## Stack
- **Vite** + React 18
- **Tailwind CSS** (fuentes: DM Sans + Sora vía Google Fonts)
- **React Router v6** — rutas protegidas por rol
- **Zustand** — estado de auth (JWT persistido en localStorage)
- **React Query** — fetching, caché y refetch automático
- **Axios** — cliente HTTP con interceptor JWT

## Instalación

```bash
npm install
npm run dev
```

## Requisitos
- El back FastAPI corriendo en `localhost:8000`
- Vite proxea `/api/*` → `localhost:8000/*` automáticamente (sin CORS)

## Estructura

```
src/
├── components/
│   ├── plomero/
│   │   ├── PlomeroLayout.jsx   — navbar + toggle disponibilidad
│   │   └── SolicitudCard.jsx   — card con timer + accept/reject
│   └── cliente/
│       └── ClienteLayout.jsx   — navbar con badge de alertas
├── pages/
│   ├── LoginPage.jsx           — login + registro por rol
│   ├── NotFound.jsx
│   ├── plomero/
│   │   ├── PlomeroDashboard.jsx  — solicitudes entrantes
│   │   ├── PlomeroEnCurso.jsx
│   │   ├── PlomeroAgenda.jsx
│   │   └── PlomeroHistorial.jsx
│   └── cliente/
│       ├── ClienteHome.jsx       — buscar + plomeros de confianza
│       ├── ClienteMisTrabajos.jsx
│       └── ClienteAlertas.jsx
├── services/
│   ├── api.js                  — axios instance + interceptores
│   ├── authService.js
│   ├── plomeroService.js
│   └── clienteService.js
├── store/
│   └── authStore.js            — zustand con persist
├── hooks/
│   └── useCountdown.js         — countdown visual en segundos
└── router/
    └── AppRouter.jsx           — rutas + guards por rol
```

## Endpoints esperados del back

### Auth
| Método | Ruta | Body |
|--------|------|------|
| POST | `/auth/login` | form-data: `username`, `password` |
| POST | `/auth/register` | JSON: `{ nombre, email, password, rol }` |
| GET  | `/auth/me` | — |

### Plomero
| Método | Ruta |
|--------|------|
| GET | `/plomero/solicitudes` |
| POST | `/plomero/solicitudes/:id/aceptar` |
| POST | `/plomero/solicitudes/:id/rechazar` |
| GET | `/plomero/trabajos` |
| GET | `/plomero/agenda` |
| GET | `/plomero/historial` |
| PATCH | `/plomero/disponibilidad` |

### Cliente
| Método | Ruta |
|--------|------|
| POST | `/cliente/solicitudes` |
| GET | `/cliente/solicitudes` |
| GET | `/cliente/plomeros-confianza` |
| GET | `/cliente/buscar?q=` |
| GET | `/cliente/alertas` |
| PATCH | `/cliente/alertas/:id/leida` |

## Modelo de datos esperado — Solicitud (plomero)
```json
{
  "id": "uuid",
  "tipo": "Urgencias",
  "urgente": true,
  "zona": "Longchamps",
  "fecha": "Hoy, 14:32",
  "turnoSugerido": "14/05/2026 a las 10:00 hs",
  "descripcion": "Se me rompió una cañería...",
  "segundosRestantes": 1777
}
```

## Ajuste del login
Por defecto usa `application/x-www-form-urlencoded` (OAuth2PasswordRequestForm de FastAPI).
Si tu endpoint `/auth/login` acepta JSON, editá `authService.js` y reemplazá el `URLSearchParams` por un objeto JSON normal.
