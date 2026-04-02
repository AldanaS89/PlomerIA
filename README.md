# 🛠️ PlomerIA - Grupo 3

**Plataforma con IA para conexión de servicios de plomería y geolocalización.**

## 📋 Resumen del Proyecto
PlomerIA utiliza **FastAPI** y **Google Gemini AI** para diagnosticar problemas de plomería mediante mensajes de texto y conectar al cliente con el profesional más cercano en la zona de Almirante Brown y alrededores.

---

## 🏗️ Estructura del Repositorio

*   **/Backend**: Lógica central, modelos de base de datos y conexión con la IA.
*   **/app_cliente**: Frontend para usuarios finales (React Native).
*   **/app_plomero**: Frontend para profesionales (React Native).
*   **crear_bd.py**: Script obligatorio para inicializar la base de datos oficial.
*   **cargar_datos_prueba.py**: Carga de plomeros y clientes para testeo.

---

## 🛠️ Stack Tecnológico

*   **Lenguaje:** Python 3.11
*   **Framework API:** FastAPI
*   **Base de Datos:** SQLite 
*   **App Móvil:** React Native + Expo 
*   **IA:** Google Gemini API
*   **Geolocalización:** GeoPy (Nominatim)

---

## 🚀 Cómo empezar (Guía para el equipo)

1. **Clonar el repo y activar entorno:**
   ```bash
   git clone [https://github.com/AldanaS89/PlomerIA.git](https://github.com/AldanaS89/PlomerIA.git)
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
