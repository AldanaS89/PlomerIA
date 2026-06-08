# routers/plomeros_routes.py
import json
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from repositories import plomero_repository
from services.foto_service import servicio_foto
from database import get_db
from schemas.plomero import PlomeroResponse

from services import plomero_service, ia_service
from core.auth import get_plomero_actual

router = APIRouter(tags=["Plomeros"])


# ── VALIDAR FOTO ──────────────────────────────────────────────────────────────
@router.post("/validar-foto")
async def validar_foto(
    foto: UploadFile = File(...),
):
    await servicio_foto.solo_validar(foto)
    return {"valido": True, "mensaje": "Rostro detectado correctamente"}


# ── REGISTRO ──────────────────────────────────────────────────────────────────
@router.post("/registro")
async def registrar(
    nombre:            str                  = Form(...),
    apellido:          str                  = Form(...),
    email:             str                  = Form(...),
    password:          str                  = Form(...),
    localidad:         str                  = Form(...),
    especialidades:    str                  = Form(...),
    genero:            str                  = Form("M"),
    atiende_urgencias: bool                 = Form(False),
    matricula_gas:     bool                 = Form(False),
    agenda:            str                  = Form("{}"),
    otra_especialidad: Optional[str]        = Form(None),
    direccion:         Optional[str]        = Form(None),
    latitud:           Optional[float]      = Form(None),   # coordenadas del mapa
    longitud:          Optional[float]      = Form(None),   # coordenadas del mapa
    foto:              Optional[UploadFile] = File(None),
    db:                Session              = Depends(get_db),
):
    try:
        lista_esp = json.loads(especialidades)
    except Exception:
        lista_esp = [e.strip() for e in especialidades.split(",") if e.strip()]

    try:
        agenda_dict = json.loads(agenda)
        if not isinstance(agenda_dict, dict):
            agenda_dict = {}
    except Exception:
        agenda_dict = {}

    foto_path = await servicio_foto.guardar(foto) if foto and foto.filename else None

    return plomero_service.registrar_completo(
        db                = db,
        nombre            = nombre,
        apellido          = apellido,
        email             = email,
        password          = password,
        localidad         = localidad,
        especialidades    = lista_esp,
        otra_especialidad = otra_especialidad,
        genero            = genero,
        atiende_urgencias = atiende_urgencias,
        matricula_gas     = matricula_gas,
        agenda            = agenda_dict,
        foto_path         = foto_path,
        direccion         = direccion,
        latitud           = latitud,
        longitud          = longitud,
    )


# ── PERFIL DEL PLOMERO LOGUEADO ───────────────────────────────────────────────
@router.get("/me", response_model=PlomeroResponse)
def obtener_mi_perfil(
    db: Session = Depends(get_db),
    id_plomero: int = Depends(get_plomero_actual)
):
    return plomero_service.obtener_mi_perfil(db, id_plomero)


# ── BUSCAR ────────────────────────────────────────────────────────────────────
@router.get("/buscar")
def buscar(
    localidad: Optional[str] = None,
    genero: Optional[str] = None,
    especialidad: Optional[str] = None,
    atiende_urgencias: Optional[bool] = None,
    disponible_ahora: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    return plomero_service.buscar_manual(
        db,
        localidad,
        genero,
        especialidad,
        atiende_urgencias,
        disponible_ahora,
    )

# ── SUGERIR — con validación de descripción ───────────────────────────────────
@router.post("/sugerir")
def sugerir(datos: dict, db: Session = Depends(get_db)):
    descripcion      = datos.get("descripcion", "")
    solo_validar     = datos.get("solo_validar", False)
    solo_mujeres     = datos.get("solo_mujeres", False)
    urgencia_forzada = datos.get("urgencia_forzada", False)
    lat              = datos.get("latitud")
    lon              = datos.get("longitud")
    excluidos        = datos.get("excluidos") or []   # ids a NO recomendar (ya rechazaron)

    diagnostico = ia_service.analizar_descripcion(descripcion)

    if not diagnostico.get("valido", True):
        return {
            "diagnostico": diagnostico,
            "plomeros":    [],
        }

    if solo_validar:
        return {
            "diagnostico": diagnostico,
            "plomeros":    [],
        }

    plomeros = plomero_service.sugerir(
        db               = db,
        descripcion      = descripcion,
        solo_mujeres     = solo_mujeres,
        lat_usuario      = lat,
        lon_usuario      = lon,
        urgencia_forzada = urgencia_forzada,
        excluidos        = excluidos,
    )

    return {
        "diagnostico": diagnostico,
        "plomeros":    plomeros,
    }


# ── DISPONIBILIDAD ────────────────────────────────────────────────────────────
@router.patch("/disponibilidad")
def cambiar_disponibilidad(
    disponible: bool,
    db: Session = Depends(get_db),
    id_plomero: int = Depends(get_plomero_actual),
):
    return plomero_service.cambiar_disponibilidad(db, id_plomero, disponible)


# ── RESEÑAS PÚBLICAS ──────────────────────────────────────────────────────────
@router.get("/{id}/resenas")
def resenas(id: int, db: Session = Depends(get_db)):
    return plomero_service.obtener_resenas(db, id)


# ── PERFIL POR ID ─────────────────────────────────────────────────────────────
@router.get("/{id}", response_model=PlomeroResponse)
def obtener(id: int, db: Session = Depends(get_db)):
    return plomero_service.obtener_por_id(db, id)