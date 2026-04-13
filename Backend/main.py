from fastapi import FastAPI
from database import engine, Base
import models  # Esto carga el __init__.py con todos los modelos
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, usuarios, plomeros, calificaciones, solicitudes  # ← agregás solicitudes acá

app = FastAPI(title="PlomerIA API")

# Configuración de CORS para comunicación con el front
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crea las tablas si no existen
Base.metadata.create_all(bind=engine)

# Registra los grupos de rutas
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(plomeros.router)
app.include_router(solicitudes.router)    
# app.include_router(calificaciones.router)

@app.get("/")
def inicio():
    return {"mensaje": "Servidor de PlomerIA activo y Base de Datos vinculada"}