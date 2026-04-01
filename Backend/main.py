from fastapi import FastAPI
from database import engine, Base
import models # Esto carga el __init__.py con todos los modelos

app = FastAPI(title="PlomerIA API")

# Crea las tablas si no existen
Base.metadata.create_all(bind=engine)

@app.get("/")
def inicio():
    return {"mensaje": "Servidor de PlomerIA activo y Base de Datos vinculada"}