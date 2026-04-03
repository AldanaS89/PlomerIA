from fastapi import FastAPI
from Backend.database import engine, Base
from Backend import models

app = FastAPI(title="PlomerIA API")

# Crea las tablas si no existen
Base.metadata.create_all(bind=engine)

@app.get("/")
def inicio():
    return {"mensaje": "Servidor de PlomerIA activo y Base de Datos vinculada"}