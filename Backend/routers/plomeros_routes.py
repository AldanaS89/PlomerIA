# routers/plomeros.py
import json
import numpy as np

from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from services import foto_service
from database import get_db
from schemas.plomero import PlomeroResponse

from services import plomero_service
from core.auth import get_plomero_actual

router = APIRouter(tags=["Plomeros"])


# ── REGISTRO (multipart/form-data — acepta foto opcional) ────────────────────
@router.post("/registro")
async def registrar(
    nombre:            str                  = Form(...),
    apellido:          str                  = Form(...),
    email:             str                  = Form(...),
    password:          str                  = Form(...),
    telefono:          str                  = Form(...),
    localidad:         str                  = Form(...),
    especialidades:    str                  = Form(...),
    genero:            str                  = Form("M"),
    atiende_urgencias: bool                 = Form(False),
    matricula_gas:     bool                 = Form(False),
    agenda:            str                  = Form("{}"),
    otra_especialidad: Optional[str]        = Form(None),
    foto:              Optional[UploadFile] = File(None),
    db:                Session              = Depends(get_db),
):
    # Parseo de JSON strings
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

    # Guardar foto — delegado al service
    foto_path = foto_service.guardar(foto) if foto and foto.filename else None

    return plomero_service.registrar_completo(
        db                = db,
        nombre            = nombre,
        apellido          = apellido,
        email             = email,
        password          = password,
        telefono          = telefono,
        localidad         = localidad,
        especialidades    = lista_esp,
        otra_especialidad = otra_especialidad,
        genero            = genero,
        atiende_urgencias = atiende_urgencias,
        matricula_gas     = matricula_gas,
        agenda            = agenda_dict,
        foto_path         = foto_path,
    )


# ── BUSCAR / SUGERIR ──────────────────────────────────────────────────────────

@router.get("/buscar", response_model=list[PlomeroResponse])
def buscar(
    localidad:         Optional[str]  = None,
    genero:            Optional[str]  = None,
    especialidad:      Optional[str]  = None,
    atiende_urgencias: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    return plomero_service.buscar(db, localidad, genero, especialidad, atiende_urgencias)


@router.post("/sugerir")
def sugerir(datos: dict, db: Session = Depends(get_db)):
    return plomero_service.sugerir(
        db               = db,
        descripcion      = datos.get("descripcion", ""),
        solo_mujeres     = datos.get("solo_mujeres", False),
        lat_usuario      = datos.get("latitud"),
        lon_usuario      = datos.get("longitud"),
        urgencia_forzada = datos.get("urgencia_forzada", False),
    )


# ── DISPONIBILIDAD ────────────────────────────────────────────────────────────

@router.patch("/disponibilidad")
def cambiar_disponibilidad(
    disponible: bool,
    db: Session = Depends(get_db),
    id_plomero: int = Depends(get_plomero_actual),
):
    return plomero_service.cambiar_disponibilidad(db, id_plomero, disponible)


# ── PERFIL ────────────────────────────────────────────────────────────────────

@router.get("/{id}", response_model=PlomeroResponse)
def obtener(id: int, db: Session = Depends(get_db)):
    return plomero_service.obtener_por_id(db, id)
