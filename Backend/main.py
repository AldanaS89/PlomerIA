# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routers.chat_ws import router as chat_ws_router
from database import Base, engine
import os

from routers import (
    auth_router,
    usuarios_routes,
    plomeros_routes,
    solicitudes,
    disponibilidad_router,
    calificaciones_routes,
)
from routers.mensajes_router import router as mensajes_router
from routers.notificaciones_router import router as notificaciones_router
from routers.material_router import router as material_router
from services.scheduler_service import iniciar_scheduler

app = FastAPI(title="PlomerIA API")

# ─────────────────────────────
# CORS
# ─────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────
# DB
# ─────────────────────────────
Base.metadata.create_all(bind=engine)

# ─────────────────────────────
# MIGRACIÓN LIVIANA — agrega columnas nuevas a tablas ya existentes
# (create_all no altera tablas creadas previamente)
# ─────────────────────────────
def _migrar_columnas():
    from sqlalchemy import text, inspect
    inspector = inspect(engine)
    try:
        cols = [c["name"] for c in inspector.get_columns("solicitudes")]
        if "diagnostico_ia" not in cols:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE solicitudes ADD COLUMN diagnostico_ia VARCHAR"))
                print("[migracion] Columna diagnostico_ia agregada a solicitudes")
    except Exception as e:
        print(f"[migracion] No se pudo migrar diagnostico_ia: {e}")

_migrar_columnas()

# ─────────────────────────────
# ARCHIVOS ESTÁTICOS — fotos de perfil
# ─────────────────────────────
os.makedirs("uploads/fotos", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ─────────────────────────────
# PREFIX GLOBAL
# ─────────────────────────────
API_PREFIX = "/api"

# ─────────────────────────────
# ROUTERS
# ─────────────────────────────

app.include_router(
    auth_router.router,
    prefix=f"{API_PREFIX}/auth",
    tags=["Auth"]
)

app.include_router(
    usuarios_routes.router,
    prefix=f"{API_PREFIX}/usuarios",
    tags=["Usuarios"]
)

app.include_router(
    plomeros_routes.router,
    prefix=f"{API_PREFIX}/plomeros",
    tags=["Plomeros"]
)

app.include_router(
    solicitudes.router,
    prefix=f"{API_PREFIX}/solicitudes",
    tags=["Solicitudes"]
)

app.include_router(
    disponibilidad_router.router,
    prefix=f"{API_PREFIX}/disponibilidad",
    tags=["Disponibilidad"]
)

app.include_router(
    calificaciones_routes.router,
    prefix=f"{API_PREFIX}/calificaciones",
    tags=["Calificaciones"]
)

app.include_router(
    mensajes_router,
    prefix=f"{API_PREFIX}/mensajes",
    tags=["Mensajes"]
)

app.include_router(
    notificaciones_router,
    prefix=f"{API_PREFIX}/notificaciones",
    tags=["Notificaciones"]
)

app.include_router(
    material_router,
    prefix=f"{API_PREFIX}/boleta",
    tags=["Boleta"]
)

# WebSocket — sin prefix porque el path ya lo define el router
app.include_router(chat_ws_router)

# ─────────────────────────────
# SCHEDULER — tareas en segundo plano
# ─────────────────────────────
@app.on_event("startup")
def startup_scheduler():
    iniciar_scheduler()

# ─────────────────────────────
# HEALTH CHECK
# ─────────────────────────────
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "PlomerIA API running 🚀"
    }

# ─────────────────────────────
# RUN
# ─────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)