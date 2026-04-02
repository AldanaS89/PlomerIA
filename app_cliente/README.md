# App Cliente - PlomerIA 📱

App móvil para usuarios que necesitan servicios de plomería.
Desarrollada en React Native con Expo.

## 🚀 Funcionalidades del MVP

- Registro y login de clientes
- Descripción del problema en texto libre
- Adjunto de foto o video
- Diagnóstico por IA (etiqueta, urgencia y presupuesto estimado)
- Lista de plomeros filtrada por cercanía (5 km) y calificación
- Filtro solo mujeres
- Solicitud on-demand a los 3 mejores plomeros
- Selección de turno para urgencias normales
- Calificación post-servicio

## 📁 Estructura de la carpeta

- `App.js` — punto de entrada de la aplicación
- `app.json` — configuración de la app (nombre, ícono, splash)
- `package.json` — dependencias del proyecto
- `/screens` — una pantalla por archivo
- `/assets` — logos, íconos y recursos visuales

## 🛠️ Tecnologías

- React Native con Expo
- JavaScript
- Conexión al backend via API REST (FastAPI)

## Para correr la app

1. `npm install`
2. `npx expo start`
3. Escanear el QR con Expo Go en el celular
