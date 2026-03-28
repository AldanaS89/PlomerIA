# App Cliente - PlomerIA 📱

Esta carpeta contiene el código fuente de la aplicación móvil orientada a los usuarios que necesitan servicios de plomería. La interfaz está desarrollada íntegramente en **Python** utilizando el framework **Kivy + KivyMD**.

## 🚀 Funcionalidades Principales
Según el alcance de nuestro MVP, esta aplicación permite:
* **Registro y Login**: Gestión de perfiles de clientes con sus datos de contacto y ubicación.
* **Descripción del Problema**: Espacio para que el usuario explique su inconveniente con sus propias palabras.
* **Adjunto de Imagen**: Opción de cargar una foto para dar contexto al diagnóstico de la IA.
* **Diagnóstico Inteligente**: Visualización de la etiqueta técnica, el nivel de urgencia y un presupuesto estimado orientativo.
* **Filtros Personalizados**: Búsqueda de profesionales por cercanía (radio de 5 km) y opción de "Solo Mujeres".
* **Solicitud On-Demand**: Envío de solicitudes a los mejores plomeros y confirmación de turnos para casos no urgentes.

## 📁 Estructura de la Carpeta
* `main.py`: Archivo principal que lanza la aplicación.
* `/screens`: Lógica de las diferentes pantallas de la interfaz.
* `/assets`: Logos, iconos y recursos visuales de la app.
* `buildozer.spec`: Configuración necesaria para compilar el archivo APK para Android.

## 🛠️ Tecnologías Utilizadas
* **Lenguaje**: Python 3.11.
* **Interfaz**: Kivy 2.x + KivyMD (Material Design).
* **Conectividad**: API REST (FastAPI).
