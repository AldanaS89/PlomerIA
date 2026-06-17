# 🔧 PlomerIA — Grupo 14

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white)
![Gemini](https://img.shields.io/badge/IA-Google_Gemini-4285F4?logo=google&logoColor=white)
![SQLite](https://img.shields.io/badge/DB-SQLite-003B57?logo=sqlite&logoColor=white)

> Plataforma que conecta clientes con plomeros usando IA. El cliente describe su
> problema con sus propias palabras, una IA lo interpreta y diagnostica, y la app
> le recomienda los mejores profesionales cercanos para que elija a quién contactar.

---

## 📋 ¿Qué hace?

1. **Cliente** escribe el problema en lenguaje natural ("se me tapó el inodoro y no baja").
2. **Gemini** lo interpreta: genera un **diagnóstico técnico**, detecta el tipo de
   trabajo, si es **urgencia** y estima un rango de presupuesto.
3. El backend **recomienda los 5 mejores** profesionales por **cercanía + puntuación**
   (con disponibilidad, y filtro opcional "solo mujeres").
4. El **cliente** elige día/horario y envía la solicitud a quien quiera.
5. El **profesional** la ve en su panel, acepta o rechaza, marca *en camino* y
   *finalizado*. Al cerrar, ambos se **califican**.

---

## 🛠️ Stack

| Área | Tecnología |
|------|-----------|
| Backend | Python 3.12 + FastAPI |
| Base de datos | SQLite + SQLAlchemy |
| Autenticación | JWT (python-jose) + hashing de contraseñas |
| IA | Google Gemini (con fallback por palabras clave) |
| Tiempo real | WebSockets (chat) |
| Frontend | React 18 + Vite + Zustand |
| Config | python-dotenv |

---

## 📂 Estructura

```
PlomerIA/
├── Backend/
│   ├── main.py               # API, routers, migración liviana, scheduler
│   ├── config.py             # Carga .env (SECRET_KEY, GEMINI_API_KEY)
│   ├── database.py
│   ├── models/               # SQLAlchemy: Usuario, Plomero, Solicitud, ...
│   ├── schemas/              # Pydantic: requests/responses
│   ├── repositories/         # Acceso a datos
│   ├── services/             # Lógica: ia_service, filtrado, calificación...
│   │   └── oficios.py        # Registro de oficios (base multi-oficio)
│   ├── routers/              # auth, usuarios, plomeros, solicitudes, chat...
│   ├── core/                 # Auth JWT y dependencias de rol
│   ├── scripts/              # Seed y simulaciones (agendas, antigüedad)
│   └── .env.example
├── frontend/                 # React + Vite
│   └── src/
│       ├── pages/            # Login, Registro, HomeCliente, HomePlomero
│       ├── components/       # ChatWidget, BoletaMateriales, DireccionConMapa
│       ├── hooks/            # useNotificaciones
│       └── services/         # api (axios)
├── docs/diagramas/           # Diagramas como código (.puml / .mmd)
├── MEJORAS_Y_OFICIOS.md      # Roadmap y refactor a multi-oficio
├── requirements.txt
└── README.md
```

---

## 🚀 Cómo correrlo

### Pre-requisitos
- **Python 3.10+** (probado con 3.12) · **Node.js 18+** · **npm** · **Git**

### Primera vez: clonar y configurar el entorno
```bash
git clone https://github.com/AldanaS89/PlomerIA.git
cd PlomerIA/Backend
cp .env.example .env
```
Editá `Backend/.env`:
1. **`SECRET_KEY`**: una cadena larga cualquiera para firmar los JWT.
2. **`GEMINI_API_KEY`**: API key de Google Gemini (gratis en
   https://aistudio.google.com/apikey → "Create API key"). 15 req/min, sin tarjeta.

> Sin `GEMINI_API_KEY`, la IA usa un **fallback por palabras clave** (clasificación
> más básica). La demo corre igual.

### Backend (FastAPI, puerto 8000)
```bash
cd Backend
python -m venv venv
source venv/Scripts/activate      # Windows: venv\Scripts\activate  ·  Linux/Mac: source venv/bin/activate
pip install -r ../requirements.txt
uvicorn main:app --reload
```
Documentación interactiva: http://localhost:8000/docs

Datos de demo (una vez):
```bash
python scripts/cargar_plomeros.py     # profesionales ficticios
python scripts/simular_antiguedad.py  # antigüedad desde el lanzamiento (mar 2026)
python scripts/generar_agendas.py     # agendas simuladas
```

### Frontend (Vite, puerto 5173)
```bash
cd frontend
npm install
npm run dev
```
Abrir http://localhost:5173 (el backend tiene que estar corriendo).

---

## 🧪 Flujo de prueba manual

1. Abrir http://localhost:5173.
2. **Registrarse como Profesional**: datos + foto, oficio (plomería),
   especialidades, urgencias, agenda y credenciales.
3. Cerrar sesión y **registrarse como Cliente** (confirmando la dirección en el mapa).
4. Como cliente, describir un problema: *"Tengo una pérdida de agua debajo de la
   pileta de la cocina"* → ver el **diagnóstico** y los **profesionales sugeridos**.
5. Elegir día/horario y **enviar la solicitud**.
6. Entrar como **plomero**: aparece la solicitud → **aceptar** → *en camino* → *finalizar*.
7. Ambos **califican**; revisar **boleta**, **notificaciones**, **agenda** e **historial/ganancias**.

---

## ✅ Features implementadas

- Registro y login (cliente y plomero) con JWT; registro del plomero **por pasos**
  (foto verificada, oficio, especialidades, urgencias, matrícula, agenda).
- **Diagnóstico por IA** (Gemini) con lenguaje natural + fallback por palabras clave.
- **Recomendación** de 5 profesionales por **tramos de distancia + puntuación**,
  con disponibilidad y filtro "solo mujeres".
- Ciclo completo de la solicitud: aceptar/rechazar, en camino, finalizar, cancelar
  (con **penalizaciones automáticas**) y reasignación.
- **Chat** en tiempo real, **notificaciones** (in-app y email).
- **Calificación bidireccional** (cliente↔plomero) con reputación base 5★ y cierre
  automático a las 72 h.
- **Boleta/presupuesto** de materiales + mano de obra, **historial con ganancias**
  (comisión 15%), **agenda** del plomero y **recontacto** a profesionales.

---

Los diagramas se ven **renderizados** al abrir el enlace (no como código).

**Diagrama de flujo** (por sub-flujo):

1. [Acceso, registro y recuperación de clave](docs/diagramas/0_flujo_acceso.drawio.svg) — Pantalla principal, login, registro de cliente y de plomero (por pasos), y bloqueo de cuentas suspendidas.
2. [Búsqueda y solicitud (cliente)](docs/diagramas/1_flujo_busqueda_solicitud.svg) — Descripción del problema, diagnóstico IA, recomendación de 5, elección de turno y envío.
3. [Ciclo de aceptación / reasignación](docs/diagramas/2_ciclo_aceptacion.drawio.svg) — Invitación a los profesionales, aceptación, rechazo y vuelta a buscar.
4. [Trabajo, finalización y calificación](docs/diagramas/3_Trabajo_finalizacioin_calificacion.drawio.svg) — En camino, boleta, finalización, ganancias y calificación mutua.
5. [Cancelación y penalidades](docs/diagramas/4_cancelacion_penalidades.drawio.svg) — Quién cancela, penalizaciones y reasignación.
6. [Panel del plomero](docs/diagramas/5_flujo_plomero.drawio.svg) — Solicitudes, trabajos en curso, agenda, ganancias e historial.
7. [Moderación de lenguaje y suspensiones](docs/diagramas/6_moderacion_lenguaje_suspension.drawio.svg) — Filtro de groserías, avisos, suspensión y reactivación automática.

**Otros diagramas:**

- 🏛️ [UML de clases](docs/diagramas/Diagrama_UML.drawio.svg) — Modelo de dominio: herencia (PersonaMixin), contrato abstracto (PersonaBase), entidades y relaciones.
- 🧩 [Casos de uso](docs/diagramas/Casos_de_uso.drawio.svg) — Acciones de Cliente, Plomero y Sistema/IA.
- 📁 Carpeta de diagramas: [`docs/diagramas/`](docs/diagramas/)
- 🗂️ **Gestión del proyecto (Trello):** https://trello.com/b/mwVOOQZJ/desarrollo-de-software

---

## ⏳ Mejoras a futuro

App móvil (React Native), refactor a multi-oficio (electricista, cerrajero…),
migraciones con Alembic, ejecución server-side de los temporizadores y deploy.
Detalle completo en [`MEJORAS_Y_OFICIOS.md`](MEJORAS_Y_OFICIOS.md).

---

## 👥 Equipo — Grupo 14

| Integrante | Rol |
|-----------|-----|
| Aldana Benavent | A definir |
| Luis Esteban Ordeñana | A definir |
| Dafne Araujo | A definir |
| Ailin Granara | A definir |
| María Florencia Iñiguez Trejo | A definir |
| Rocío Natalí Rolón | A definir |

> 📅 Entrega: 17 de junio de 2026 · Materia: Desarrollo de Software · UNAB
