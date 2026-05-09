# CLAUDE.md — Contexto del proyecto PlomerIA

## Qué es este proyecto

App tipo Uber para plomeros. El cliente describe su problema, una IA lo analiza, y la app conecta al cliente con el plomero más cercano y disponible. Zona de cobertura: Almirante Brown y alrededores (Buenos Aires, Argentina).

**Materia:** Desarrollo de Software — UNAB  
**Grupo:** Grupo 3 (6 integrantes)  
**Entrega:** 17 de junio de 2026  
**Estado:** En desarrollo (iniciado hace ~2 semanas)

---

## Sobre el usuario (Luis)

- Nivel de programación básico — conoce objetos pero poco de bases de datos, librerías o frameworks
- Usa IA para asistencia en el desarrollo
- Lo que evalúan en la materia es trabajo en equipo y que funcione, no profundidad técnica
- Tiene dispositivos Android para probar
- Trabaja en Linux

---

## Decisiones de arquitectura tomadas

- **Una sola app móvil** (no dos apps separadas). El tipo de usuario se detecta por el campo `"tipo"` dentro del token JWT (`"usuario"` o `"plomero"`), y la app muestra pantallas distintas según eso.
- **Deploy del backend en Render.com** para poder usarlo desde la universidad sin depender de que una computadora esté encendida.
- El frontend se va a construir desde cero — las carpetas `app_cliente/` y `app_plomero/` son plantillas vacías que no se van a usar.

---

## Stack tecnológico

| Área | Tecnología |
|------|-----------|
| Backend | Python 3.11 + FastAPI |
| Base de datos | SQLite + SQLAlchemy |
| Autenticación | JWT con python-jose |
| Encriptación passwords | pbkdf2_sha256 (usuarios) / bcrypt (plomeros) — inconsistente, a unificar |
| App móvil | React Native + Expo |
| IA (pendiente) | Google Gemini API |
| Geolocalización | GeoPy (Nominatim) |
| Deploy backend | Render.com (pendiente) |

---

## Estado del backend

### Endpoints activos
- `POST /auth/registro` — Registrar usuario cliente
- `POST /auth/login` — Login de cliente → devuelve JWT con `"tipo": "usuario"`
- `POST /plomeros/registro` — Registrar plomero
- `POST /plomeros/login` — Login de plomero → devuelve JWT con `"tipo": "plomero"`
- `GET /plomeros/buscar` — Filtrar plomeros (localidad, genero, especialidad, atiende_urgencias)
- `GET /plomeros/{id}` — Detalle de un plomero
- `PATCH /plomeros/disponibilidad` — Plomero activa/desactiva disponibilidad (requiere JWT plomero)
- `POST /solicitudes/` — Crear solicitud (requiere JWT usuario)
- `GET /solicitudes/mis-solicitudes` — Ver solicitudes del usuario logueado
- `GET /solicitudes/{id}` — Detalle de una solicitud

### Endpoints desactivados
- `/calificaciones` — router comentado en main.py

### No implementado aún
- Lógica de asignación de plomero a solicitud
- Integración con Google Gemini (campos `etiqueta_ia`, `urgencia_ia`, `presupuesto_min`, `presupuesto_max` existen en el modelo pero siempre quedan vacíos)
- Búsqueda por distancia geográfica (campos `latitud`/`longitud` existen en Plomero pero no se usan en los filtros)

---

## Problemas conocidos en el código

1. **Archivo duplicado con typo:** `repositories/solitud_repository.py` (sin "i") es copia exacta de `solicitud_repository.py` — el incorrecto no se usa
2. **SECRET_KEY hardcodeada:** `"plomeria_secreta_2024"` visible en `auth_service.py` y `plomero_service.py` — mover a `.env`
3. **`SolicitudCreate.id_plomero` es obligatorio** (`int`) cuando debería ser `Optional[int]` — el modelo de BD ya lo permite como nullable
4. **Algoritmos de hash inconsistentes:** usuarios usan `pbkdf2_sha256`, plomeros usan `bcrypt`

---

## Modelos de base de datos

```
usuarios        → id, nombre, apellido, email, password_hash, direccion, telefono, latitud, longitud
plomeros        → id, nombre, apellido, email, telefono, especialidad, genero, localidad,
                   latitud, longitud, atiende_urgencias, disponible_ahora, puntuacion,
                   total_trabajos, matricula_gas, password_hash
solicitudes     → id, id_usuario (FK), id_plomero (FK nullable), descripcion_raw,
                   imagen_path, video_path, etiqueta_ia, urgencia_ia,
                   presupuesto_min, presupuesto_max, estado (PENDIENTE/ACEPTADO/RECHAZADO), fecha
asignaciones    → id, id_solicitud, id_plomero, estado, fecha_aceptacion, fecha_completado
calificaciones  → id, id_asignacion, id_cliente, id_plomero, estrellas, comentario, fecha_resenia
```

---

## Estructura del repositorio

```
PlomerIA/
├── CLAUDE.md                 # Este archivo
├── Backend/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   │   ├── usuario.py
│   │   ├── plomero.py
│   │   ├── solicitud.py
│   │   ├── asignacion.py
│   │   └── calificacion.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── usuarios.py
│   │   ├── plomeros.py
│   │   ├── solicitudes.py
│   │   └── calificaciones.py  (desactivado)
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── plomero_service.py
│   │   └── solicitud_service.py
│   ├── repositories/
│   │   ├── usuario_repository.py
│   │   ├── plomero_repository.py
│   │   ├── solicitud_repository.py
│   │   └── solitud_repository.py  (typo — duplicado sin usar)
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── plomero.py
│   │   ├── solicitud.py
│   │   └── usuario.py
│   ├── utils/
│   │   └── auth_plomeros.py   # get_usuario_actual() y get_plomero_actual()
│   └── data/
│       ├── plomeros.json
│       └── cargar_plomeros.py
├── app_cliente/              # Plantilla Expo vacía — NO usar
├── app_plomero/              # Plantilla Expo vacía — NO usar
├── docs/
│   └── diagramas/uml_clases.md
└── requirements.txt
```

---

## Sesiones anteriores

- [sesion_01.md](sesion_01.md) — Análisis inicial del proyecto y planificación del frontend (13/04/2026)
