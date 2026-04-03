# 🔧 PlomerIA — Grupo 3

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![React Native](https://img.shields.io/badge/React_Native-Expo-black?logo=expo&logoColor=white)
![Gemini](https://img.shields.io/badge/IA-Google_Gemini-4285F4?logo=google&logoColor=white)
![SQLite](https://img.shields.io/badge/Base_de_datos-SQLite-003B57?logo=sqlite&logoColor=white)
![Estado](https://img.shields.io/badge/Estado-En_desarrollo-yellow)

> Plataforma inteligente que conecta clientes con plomeros cercanos usando IA para diagnosticar problemas y gestionar solicitudes en tiempo real.

---

## 📋 ¿Qué es PlomerIA?

PlomerIA utiliza **FastAPI** y **Google Gemini AI** para diagnosticar problemas de plomería a partir de texto o fotos, y conectar al cliente con el profesional más cercano y mejor calificado en la zona de Almirante Brown y alrededores.

El cliente describe su problema con sus propias palabras — la IA lo interpreta, clasifica la urgencia y filtra automáticamente los plomeros disponibles en un radio de 5 km.

---

## 🏗️ Estructura del Repositorio
```
PlomerIA/
├── Backend/               # Lógica central, modelos y conexión con IA
│   ├── models/            # Modelos SQLAlchemy (Usuario, Plomero, etc.)
│   ├── data/              # Datos de prueba
│   ├── database.py        # Configuración de la base de datos
│   └── main.py            # Punto de entrada de la API
├── app_cliente/           # App React Native para usuarios finales
├── app_plomero/           # App React Native para profesionales
├── crear_bd.py            # Script para inicializar la base de datos
└── cargar_datos_prueba.py # Carga plomeros y clientes ficticios para testeo
```

---

## 🛠️ Stack Tecnológico

| Área | Tecnología |
|------|-----------|
| Lenguaje | Python 3.11 |
| Framework API | FastAPI |
| Base de datos | SQLite + SQLAlchemy |
| App móvil | React Native + Expo |
| Inteligencia Artificial | Google Gemini API |
| Geolocalización | GeoPy (Nominatim) |
| Autenticación | JWT (python-jose) |

---

## 📊 Diagrama de Clases

![Diagrama de Clases](docs/uml_clases.png)

---

## 🚀 Cómo empezar

### 1. Clonar el repositorio y activar entorno
```bash
git clone https://github.com/AldanaS89/PlomerIA.git
cd PlomerIA
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Levantar la API
```bash
uvicorn Backend.main:app --reload
```

### 3. Ver la documentación automática

Abrí en el navegador: [http://localhost:8000/docs](http://localhost:8000/docs)

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

---

> 📅 Entrega: 17 de junio de 2026 · Materia: Desarrollo de Software
