from fastapi import FastAPI
from routers import usuarios_routes, plomeros_routes
from database import engine, Base
import models # Esto carga el __init__.py con todos los modelos
from fastapi.middleware.cors import CORSMiddleware

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
app.include_router(usuarios_routes.router)
app.include_router(plomeros_routes.router)
#app.include_router(solicitudes.router)
# app.include_router(calificaciones.router)

@app.get("/")
def inicio():
    return {"mensaje": "Servidor de PlomerIA activo y Base de Datos vinculada"}