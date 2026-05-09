# Sesión 01 — Análisis inicial y planificación del frontend

**Fecha:** 13 de abril de 2026

---

## Qué se hizo en esta sesión

### 1. Análisis del proyecto
Se analizó el repositorio completo. El proyecto PlomerIA es una app tipo Uber para plomeros, desarrollada por el Grupo 3 para la materia Desarrollo de Software (UNAB), con entrega el 17 de junio de 2026.

### 2. Estado actual del proyecto

| Componente | Estado |
|-----------|--------|
| Backend (servidor FastAPI) | Funcional parcialmente |
| Autenticación usuarios | Funciona |
| Autenticación plomeros | Funciona |
| Búsqueda de plomeros | Funciona (sin GPS real) |
| Solicitudes | Funciona básicamente |
| IA (Google Gemini) | No implementada |
| Calificaciones | Modelo existe, router desactivado |
| Asignaciones | Modelo existe, sin lógica |
| App cliente (móvil) | No existe — es la plantilla por defecto de Expo |
| App plomero (móvil) | No existe — es la plantilla por defecto de Expo |

### 3. Problemas identificados en el backend

- **Archivo duplicado con typo:** `solitud_repository.py` (le falta la "i") es una copia exacta de `solicitud_repository.py`
- **Clave JWT hardcodeada:** `SECRET_KEY = "plomeria_secreta_2024"` visible en el código
- **Algoritmos de password inconsistentes:** usuarios usan `pbkdf2_sha256`, plomeros usan `bcrypt`
- **`SolicitudCreate` requiere `id_plomero` como obligatorio** aunque debería ser opcional (la IA lo asignaría)
- **Geolocalización del plomero sin usar:** tiene campos `latitud`/`longitud` pero el filtro de búsqueda solo usa texto
- **Calificaciones desactivadas:** comentado en `main.py` línea 25
- **IA no implementada:** los campos `etiqueta_ia`, `urgencia_ia`, `presupuesto_min`, `presupuesto_max` siempre quedan vacíos

### 4. Decisiones tomadas

- **Una sola app móvil** en lugar de dos apps separadas (`app_cliente` y `app_plomero` se unificarán)
- La app detecta el tipo de usuario por el token JWT (`"tipo": "usuario"` o `"tipo": "plomero"`) y muestra pantallas distintas
- **El backend se va a deployar en Render.com** (gratis) para poder usarlo desde la universidad sin depender de que una computadora esté encendida

### 5. Próximos pasos acordados

```
Paso 1: Instalar Node.js en la computadora de Luis
Paso 2: Instalar Expo Go en el dispositivo Android
Paso 3: Levantar el backend localmente (para desarrollar)
Paso 4: Arrancar con las pantallas del frontend
Paso 5: Subir el backend a Render cuando haya algo para mostrar
```

---

## Stack tecnológico del proyecto

| Área | Tecnología |
|------|-----------|
| Lenguaje backend | Python 3.11 |
| Framework API | FastAPI |
| Base de datos | SQLite + SQLAlchemy |
| Autenticación | JWT (python-jose) |
| App móvil | React Native + Expo |
| IA (planeada) | Google Gemini API |
| Geolocalización | GeoPy |
| Deploy backend | Render.com (pendiente) |

---

## Estructura del repositorio

```
PlomerIA/
├── Backend/
│   ├── main.py               # Punto de entrada de la API
│   ├── database.py           # Configuración SQLite
│   ├── models/               # Usuario, Plomero, Solicitud, Asignacion, Calificacion
│   ├── routers/              # auth, usuarios, plomeros, solicitudes (calificaciones desactivado)
│   ├── services/             # Lógica de negocio
│   ├── repositories/         # Acceso a base de datos
│   ├── schemas/              # Validación de datos (Pydantic)
│   └── utils/auth_plomeros.py # Verificación de tokens JWT
├── app_cliente/              # Plantilla vacía — a reemplazar
├── app_plomero/              # Plantilla vacía — a reemplazar
├── docs/diagramas/uml_clases.md
└── requirements.txt
```
