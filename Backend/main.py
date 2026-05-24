from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.chat_ws import router as chat_ws_router
from database import Base, engine

from routers import (
    auth_router,
    usuarios_routes,
    plomeros_routes,
    solicitudes,
    disponibilidad_router,
    calificaciones_routes,
)

app = FastAPI(title="PlomerIA API")

# ─────────────────────────────
# CORS
# ─────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción: dominios reales
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────
# DB
# ─────────────────────────────
Base.metadata.create_all(bind=engine)

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

# WS
app.include_router(chat_ws_router)
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