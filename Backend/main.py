import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import usuarios_routes, plomeros_routes, solicitudes, disponibilidad, calificaciones_routes

app = FastAPI(title="PlomerIA - Zona Sur", redirect_slashes=False)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

API_PREFIX = "/api"

# tiene prefix="/usuarios" adentro → solo /api
app.include_router(usuarios_routes.router, prefix=API_PREFIX)

# NO tiene prefix adentro → /api/plomeros
app.include_router(plomeros_routes.router, prefix=API_PREFIX + "/plomeros")

# tiene prefix="/solicitudes" adentro → solo /api
app.include_router(solicitudes.router, prefix=API_PREFIX)

# NO tiene prefix adentro → /api/disponibilidad
app.include_router(disponibilidad.router, prefix=API_PREFIX + "/disponibilidad")

# tiene prefix="/calificaciones" adentro → solo /api
app.include_router(calificaciones_routes.router, prefix=API_PREFIX)

@app.get("/")
def inicio():
    return {"mensaje": "Servidor de PlomerIA activo"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)