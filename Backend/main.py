from fastapi import FastAPI
from database import engine, Base
import models # Esto carga el __init__.py con todos los modelos
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, usuarios, plomeros, calificaciones
app = FastAPI(title="PlomerIA API")

#Configuracion de cors para comunicacion con el front
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crea las tablas si no existen
Base.metadata.create_all(bind=engine)

# Registra los grupos de rutas, "suma todas estas rutas al servidor principal"
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(plomeros.router)
#app.include_router(solicitudes.router)
# app.include_router(calificaciones.router)

@app.get("/")
def inicio():
    return {"mensaje": "Servidor de PlomerIA activo y Base de Datos vinculada"}