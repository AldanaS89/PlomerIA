# 🔧 PlomerIA — Grupo 3

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white)
![Gemini](https://img.shields.io/badge/IA-Google_Gemini-4285F4?logo=google&logoColor=white)
![SQLite](https://img.shields.io/badge/DB-SQLite-003B57?logo=sqlite&logoColor=white)

> Plataforma tipo Uber para plomeros. El cliente describe su problema con sus propias palabras, una IA lo clasifica, y la app le asigna automáticamente un plomero disponible en su zona.

---

## 📋 ¿Qué hace?

1. **Cliente** escribe el problema en lenguaje natural ("se me tapó el inodoro y no baja").
2. **Gemini** clasifica el caso: tipo (destapes, gas, obra, general), urgencia (baja/normal/urgente) y estima un rango de presupuesto.
3. El backend **asigna automáticamente** al plomero disponible mejor puntuado que coincida con la especialidad y localidad.
4. El **plomero** ve la solicitud en su panel y puede aceptarla o rechazarla.

---

## 🛠️ Stack

| Área | Tecnología |
|------|-----------|
| Backend | Python 3.12 + FastAPI |
| Base de datos | SQLite + SQLAlchemy |
| Autenticación | JWT (python-jose) + pbkdf2_sha256 |
| IA | Google Gemini (`gemini-flash-latest`) |
| Frontend | React 18 + Vite (web) |
| Config | python-dotenv |

---

## 📂 Estructura

```
PlomerIA/
├── Backend/
│   ├── main.py               # Entrada de la API
│   ├── config.py             # Carga .env (SECRET_KEY, GEMINI_API_KEY)
│   ├── database.py
│   ├── models/               # SQLAlchemy: Usuario, Plomero, Solicitud, ...
│   ├── schemas/              # Pydantic: requests/responses
│   ├── routers/              # auth, usuarios, plomeros, solicitudes
│   ├── services/             # auth_service, plomero_service,
│   │                         #   solicitud_service, ia_service (Gemini)
│   ├── repositories/
│   ├── utils/auth_plomeros.py  # get_usuario_actual, get_plomero_actual
│   ├── data/cargar_plomeros.py # Seed desde data/plomeros.json
│   ├── .env                  # NO commitear — copiar desde .env.example
│   └── .env.example
├── frontend/                 # React + Vite
│   ├── src/
│   │   ├── api.js            # Cliente HTTP (fetch + proxy /api → :8000)
│   │   ├── auth.js           # Sesión en localStorage
│   │   ├── App.jsx
│   │   └── pages/            # Login, Registro, HomeCliente, HomePlomero
│   └── vite.config.js
├── requirements.txt
└── README.md
```

---

## 🚀 Cómo correrlo

### Pre-requisitos

Tenés que tener instalados en tu máquina:

- **Python 3.10 o superior** (probado con 3.12) — verificá con `python3 --version`
- **Node.js 18 o superior** — verificá con `node --version`
- **npm** (viene con Node) — verificá con `npm --version`
- **Git** para clonar el repo

### Primera vez: clonar y configurar variables de entorno

```bash
git clone https://github.com/AldanaS89/PlomerIA.git
cd PlomerIA/Backend
cp .env.example .env
```

Ahora editá `Backend/.env` con tu editor favorito. Hay dos variables:

1. **`SECRET_KEY`**: una cadena cualquiera, larga, para firmar los JWT. Ejemplo: `SECRET_KEY=esto_es_una_clave_secreta_del_grupo_3`
2. **`GEMINI_API_KEY`**: la API key de Google Gemini. Para conseguirla:
   - Andá a https://aistudio.google.com/apikey (con cualquier cuenta de Google)
   - Click en "Create API key" → "Create API key in new project"
   - Copiá la key (empieza con `AIza...`) y pegala en el `.env`
   - Es **gratis**: 15 requests por minuto, 1500 por día. No pide tarjeta de crédito.

> **Si no ponés la `GEMINI_API_KEY`**, la IA igual funciona con un **fallback** por keywords que clasifica con reglas simples (por ejemplo, si la descripción contiene "gas" la marca como `GAS_MATRICULADO`). La demo corre igual, solo que la clasificación es más básica. Útil para probar sin tener que sacar una key.

### Backend (FastAPI en puerto 8000)

```bash
cd Backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r ../requirements.txt
uvicorn main:app --reload
```

Opcional — cargar plomeros de prueba desde `data/plomeros.json`:

```bash
python data/cargar_plomeros.py
```

Documentación interactiva: http://localhost:8000/docs

### Frontend (Vite en puerto 5173)

```bash
cd frontend
npm install
npm run dev
```

Abrir http://localhost:5173. El frontend hace proxy de `/api` a `http://localhost:8000`, así que el backend tiene que estar corriendo.

---

## 🧪 Flujo de prueba manual

1. Abrir http://localhost:5173
2. Click en **"Registrarme"**, seleccionar **Plomero**, completar formulario (ej. especialidad `PLOMERIA_GENERAL`, localidad `Adrogué`).
3. Salir, registrarse de nuevo como **Cliente**.
4. Iniciar sesión como cliente y crear una solicitud: *"Tengo una pérdida de agua importante debajo de la pileta de la cocina"*.
5. La IA debería clasificarlo y asignar automáticamente al plomero creado en el paso 2.
6. Cerrar sesión, iniciar como plomero — la solicitud aparece en su panel con los botones aceptar/rechazar.

---

## ✅ Features implementadas

- Registro y login (clientes y plomeros) con JWT
- Creación de solicitudes con **clasificación automática por Gemini** (tipo, urgencia, presupuesto estimado)
- **Asignación automática**: elige el plomero disponible mejor puntuado que matchee especialidad + localidad + (urgencia si aplica)
- Panel del plomero con toggle de disponibilidad y aceptar/rechazar solicitudes
- Pantallas web funcionales para cliente y plomero desde una sola app
- Fallback de IA por keywords si Gemini falla o no hay API key

## ⏳ Pendiente / fuera de alcance (se puede dejar para después de la entrega)

- **App móvil React Native**: el frontend actual es web. Migrar a RN+Expo debería ser factible reutilizando `api.js` y la lógica de `auth.js`.
- **Calificaciones**: el router está desactivado en `main.py`. El modelo existe.
- **Búsqueda por distancia**: los campos `latitud`/`longitud` existen pero la asignación filtra por localidad textual, no por radio geográfico.
- **Upload real de imágenes/videos**: los campos están en el schema pero no hay storage.
- **Deploy a Render.com**: pendiente. Con `uvicorn main:app --host 0.0.0.0 --port $PORT` y las env vars en el dashboard debería alcanzar.

---

## 👥 Equipo — Grupo 3

| Integrante | Rol |
|-----------|-----|
| Aldana Benavent | A definir |
| Luis Esteban Ordeñana | A definir |
| Dafne Araujo | A definir |
| Ailin Granara | A definir |
| María Florencia Iñiguez Trejo | A definir |
| Rocío Natalí Rolón | A definir |

> 📅 Entrega: 17 de junio de 2026 · Materia: Desarrollo de Software · UNAB
