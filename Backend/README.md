# Backend - PlomerIA 🧠

Este es el servidor central de la plataforma, encargado de procesar los datos, gestionar la inteligencia artificial y conectar ambas aplicaciones.

## 🚀 Funcionalidades Principales
* **API REST**: Puntos de enlace (endpoints) para que las apps envíen y reciban datos.
* **Motor de IA**: Integración con la API de **Google Gemini** para realizar el diagnóstico técnico y calcular la urgencia.
* **Base de Datos**: Gestión de usuarios, solicitudes y técnicos mediante **SQLite** y SQLAlchemy.
* **Geolocalización**: Lógica para filtrar plomeros en un radio de 5 km basándose en el archivo de datos.

## 📁 Archivos y Carpetas Clave
* `main.py`: Punto de entrada del servidor FastAPI.
* `ia_engine.py`: Lógica de conexión y prompts para Gemini.
* `database.py`: Configuración de la base de datos.
* `/data`: Carpeta para el archivo `plomeros.json` (100 perfiles de prueba).

## 🛠️ Tecnologías Utilizadas
* **Lenguaje**: Python 3.11.
* **Framework**: FastAPI.
* **IA**: Google Generative AI (Gemini).
* **ORM**: SQLAlchemy.
