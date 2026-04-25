from fastapi import FastAPI
from database import engine, Base
import models  # Carga la configuración de todos los modelos (Usuario, Plomero, etc.)
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, usuarios, plomeros, solicitudes 

app = FastAPI(title="PlomerIA API - Almirante Brown")

# --- CONFIGURACIÓN DE CORS ---
# Fundamental para que el equipo de Front (React Native) pueda conectarse
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CREACIÓN DE BASE DE DATOS ---
# Esto genera las tablas automáticamente basándose en tus modelos actualizados
Base.metadata.create_all(bind=engine)

# --- REGISTRO DE RUTAS ---
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(plomeros.router, prefix="/plomeros", tags=["Plomeros"])
app.include_router(solicitudes.router, prefix="/solicitudes", tags=["Solicitudes"])

@app.get("/")
def inicio():
    return {
        "mensaje": "Servidor de PlomerIA activo",
        "estado": "Conectado a Base de Datos",
        "zona": "Almirante Brown"
    }

# --- BLOQUE DE ARRANQUE (Conveniente para el equipo) ---
if __name__ == "__main__":
    import uvicorn
    # reload=True reinicia el servidor automáticamente al guardar cambios
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)