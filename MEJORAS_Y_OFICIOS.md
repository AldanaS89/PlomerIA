# PlomerIA — Hoja de ruta de mejoras y refactor a multi-oficio

Este documento resume el estado del proyecto, las mejoras a encarar y el plan
para soportar nuevos oficios (electricista, cerrajero, etc.) sin romper lo que
funciona. Pensado para ejecutar por pasos verificables y para defender el proyecto.

## 1. Estado actual (resumen técnico)

Arquitectura en capas: `routers` (HTTP) → `services` (lógica) → `repositories`
(datos) → `models`/`schemas`. Separación de responsabilidades clara.

- **POO**: abstracción (`PersonaMixin`), herencia (`Usuario`/`Plomero`),
  encapsulamiento (repos/services) y polimorfismo. El polimorfismo hoy es
  **por parámetro** (`rol`: calificación, penalización, `require_role`), no por
  subtipo con métodos sobreescritos.
- **SOLID**: SRP fuerte; OCP débil para agregar oficios (hay que modificar enums
  y prompt); DIP parcial (services usan repos concretos, no inyectados).
- **Patrones**: Repository, Service Layer, DTO (Pydantic), Factory
  (`require_role`), Singleton (`notificacion_service`, `manager`), Mixin,
  DI (FastAPI `Depends`).

## 2. Mejoras a encarar (prioridad y riesgo)

| # | Mejora | Valor | Riesgo | Estado |
|---|--------|-------|--------|--------|
| 1 | Registro de **Oficios** (fuente única) | Alto | Bajo | **HECHO** (`services/oficios.py`) |
| 2 | IA consume el registro + devuelve `oficio_ia` | Alto | Bajo | **HECHO** (retrocompatible) |
| 3 | IA en dos etapas (oficio → especialidad) por prompt dinámico | Alto | Medio | Pendiente |
| 4 | Columna `oficio` en profesional + en solicitud (con migración) | Alto | Medio | Pendiente |
| 5 | Filtrado por oficio (además de especialidad) | Alto | Bajo | Pendiente |
| 6 | Frontend: registro elige oficio; badges/labels/tipos desde config | Alto | Medio | Pendiente |
| 7 | Migraciones con **Alembic** (en vez de ALTER manual) | Medio | Bajo | Pendiente |
| 8 | Timers server-side (30 min, 72 hs, 7am) en el scheduler | Medio | Medio | Pendiente |
| 9 | Comisión/ticket/meta como **config del backend** | Bajo | Bajo | Pendiente |
| 10 | **Tests** (promedio, penalización, filtrado, fallback IA) | Alto | Bajo | Pendiente |
| 11 | Strategy real de notificación (email/in-app/push) | Medio | Bajo | Pendiente |
| 12 | Inyección de repos en services (DIP) | Medio | Medio | Pendiente |
| 13 | Quitar duplicación (hook notifs, UI calificación) | Bajo | Bajo | Pendiente |
| 14 | `logging` consistente (sacar `print`) | Bajo | Bajo | Pendiente |

## 3. Refactor a multi-oficio — plan

Objetivo: **agregar un oficio = agregar config**, sin tocar la lógica.

### Diseño
- `services/oficios.py` (ya creado) es el registro: cada oficio define
  `label`, `habilitado`, `especialidades`, `rangos`, `pistas` y `descripcion_ia`.
- La IA detecta primero el **oficio** y luego la **especialidad** dentro de él,
  usando el registro para armar el prompt dinámicamente.
- El **profesional** deja de ser "plomero" conceptualmente: pasa a tener un
  campo `oficio`. (El rename de la clase `Plomero` → `Profesional` es opcional y
  se puede hacer al final; lo importante es el campo `oficio` + el registro.)
- El filtrado considera `oficio` + `especialidad` + cercanía + puntuación.
- El frontend toma labels, badges y tipos de trabajo del registro (endpoint
  `GET /oficios`), no hardcodeados.

### Pasos (verificables uno a uno)
1. **(hecho)** Registro `oficios.py` + IA consume el registro y devuelve `oficio_ia`.
2. Prompt de IA dinámico con `oficios.guia_especialidades_ia()` (dos etapas).
3. Migración: `oficio` en `plomeros` (default `PLOMERIA`) y `oficio_ia` en `solicitudes`.
4. `filtrado_service` filtra por `oficio` del profesional.
5. Endpoint `GET /oficios` (habilitados) + registro de profesional elige oficio.
6. Frontend: badges/labels/tipos desde el endpoint; mostrar oficios inhabilitados como "próximamente".
7. (opcional) Rename `Plomero` → `Profesional` con alias temporal.

### Qué garantiza la extensibilidad
- Hoy: el **pipeline** (describir → diagnosticar → filtrar → recomendar) y el
  **registro/agenda/foto/urgencias** ya son genéricos en estructura.
- Tras los pasos 2–6: sumar "electricista" será poner `"habilitado": True` en el
  registro (y cargar profesionales con ese oficio). La IA lo detectará, el
  filtrado lo respetará y la UI lo mostrará, sin tocar la lógica.

## 4. Recomendación de ejecución

No hacer todo de una: en este entorno no se puede correr el build/tests para
verificar, y la app funciona. Conviene avanzar por pasos cortos, probando cada
uno (reiniciar back/front) antes del siguiente. Orden sugerido: 3 → 4 → 5 → 6
(completar multi-oficio), luego 7, 8, 10 (Alembic, timers, tests).
