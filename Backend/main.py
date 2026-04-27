import sys
import os

# Esto le dice a Python que la carpeta Backend es una raíz de búsqueda
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI
from database import engine, Base
import models  # Carga la configuración de todos los modelos
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, usuarios, plomeros, solicitudes 

# --- CONFIGURACIÓN DE APP ---
# redirect_slashes=False ayuda a que el Front no falle por una "/" de más
app = FastAPI(
    title="PlomerIA - Zona Sur",
    redirect_slashes=False
)

# --- CONFIGURACIÓN DE CORS ---
# Permite que tu Frontend (puerto 5173) se comunique sin bloqueos de seguridad
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CREACIÓN DE BASE DE DATOS ---
# Genera las tablas con tus campos de latitud/longitud automáticamente
from routers import disponibilidad
app.include_router(disponibilidad.router, prefix="/api/disponibilidad")
Base.metadata.create_all(bind=engine)

# --- REGISTRO DE RUTAS CON PREFIJO /API ---
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(plomeros.router, prefix="/api/plomeros", tags=["Plomeros"])
app.include_router(solicitudes.router, prefix="/api/solicitudes", tags=["Solicitudes"])

@app.get("/")
def inicio():
    return {
        "mensaje": "Servidor de PlomerIA activo",
        "estado": "Conectado a Base de Datos",
        "zona": "Almirante Brown"
    }

# --- BLOQUE DE ARRANQUE ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)