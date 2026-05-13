# services/plomero_service.py
import secrets
from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional, List

from config import SECRET_KEY, ALGORITHM
from models.plomero import Plomero
from utils.email import enviar_reset_password
from schemas.plomero import (
    PlomeroResponse, PlomeroLoginRequest, PlomeroLoginResponse,
    OlvidePasswordPlomeroRequest, ResetPasswordPlomeroRequest,
)
from repositories import plomero_repository
from services.auth_service import _geocodificar

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _crear_token(id_plomero: int) -> str:
    expiracion = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(
        {"sub": str(id_plomero), "tipo": "plomero", "exp": expiracion},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


# ── REGISTRO COMPLETO ─────────────────────────────────────────────────────────

def registrar_completo(
    db:                  Session,
    nombre:              str,
    apellido:            str,
    email:               str,
    password:            str,
    telefono:            str,
    direccion:           str,
    localidad:           str,
    especialidades:      List[str],
    otra_especialidades: Optional[str],
    genero:              str,
    atiende_urgencias:   bool,
    matricula_gas:       bool,
    agenda:              dict,
    foto_path:           Optional[str],
) -> dict:
    if plomero_repository.buscar_por_email(db, email):
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    # Geocodificación automática
    latitud, longitud = _geocodificar(direccion, localidad)

    # Separar "OTRA:texto" del resto
    esp_final   = []
    otra_custom = otra_especialidades
    for e in especialidades:
        if e.startswith("OTRA:"):
            otra_custom = e[5:]
        else:
            esp_final.append(e)

    nuevo = Plomero(
        nombre              = nombre,
        apellido            = apellido,
        email               = email,
        telefono            = telefono,
        especialidades      = esp_final,
        otra_especialidades = otra_custom,
        genero              = genero,
        localidad           = localidad,
        latitud             = latitud,
        longitud            = longitud,
        atiende_urgencias   = atiende_urgencias,
        matricula_gas       = matricula_gas,
        password_hash       = pwd_context.hash(password),
        disponible_ahora    = True,
        puntuacion          = 0.0,
        total_trabajos      = 0,
        foto_perfil_path    = foto_path,
        agenda              = agenda if agenda else None,
    )

    plomero = plomero_repository.crear_plomero(db, nuevo)

    # Guardar agenda como bloques horarios reales en la tabla bloques_horarios
    if agenda:
        _guardar_agenda_inicial(db, plomero.id_plomero, agenda)

    token = _crear_token(plomero.id_plomero)

    return {
        "mensaje":      "Plomero registrado correctamente",
        "access_token": token,
        "token_type":   "bearer",
        "id_plomero":   plomero.id_plomero,
        "nombre":       plomero.nombre,
    }


def _guardar_agenda_inicial(db: Session, id_plomero: int, agenda: dict) -> None:
    """
    Convierte la agenda del formulario en bloques horarios para las próximas 4 semanas.
    agenda = {"Lun_manana": True, "Mar_tarde": True, ...}
    """
    try:
        from routers.disponibilidad import BloqueHorario

        FRANJA_HORAS = {
            "manana": (8,  13),
            "tarde":  (13, 18),
            "noche":  (18, 22),
        }
        DIA_NUM = {
            "Lun": 0, "Mar": 1, "Mié": 2, "Jue": 3,
            "Vie": 4, "Sáb": 5, "Dom": 6,
        }

        hoy    = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        bloques = []

        for semana in range(4):
            for clave, activo in agenda.items():
                if not activo:
                    continue
                partes = clave.split("_", 1)
                if len(partes) != 2:
                    continue
                dia_str, franja_str = partes
                num_dia = DIA_NUM.get(dia_str)
                horas   = FRANJA_HORAS.get(franja_str)
                if num_dia is None or horas is None:
                    continue

                from datetime import timedelta
                dias_hasta = (num_dia - hoy.weekday()) % 7
                if dias_hasta == 0 and semana == 0:
                    dias_hasta = 7
                fecha_base = hoy + timedelta(days=dias_hasta + semana * 7)

                inicio = fecha_base.replace(hour=horas[0])
                fin    = fecha_base.replace(hour=horas[1])

                bloques.append(BloqueHorario(
                    id_plomero  = id_plomero,
                    inicio      = inicio,
                    fin         = fin,
                    ocupado     = False,
                    descripcion = None,
                ))

        if bloques:
            db.add_all(bloques)
            db.commit()

    except Exception as e:
        # Si falla la agenda no rompemos el registro
        print(f"[plomero_service] No se pudo guardar agenda inicial: {e}")


# ── LOGIN ─────────────────────────────────────────────────────────────────────

def login(db: Session, datos: PlomeroLoginRequest) -> PlomeroLoginResponse:
    plomero = plomero_repository.buscar_por_email(db, datos.email)
    if not plomero or not pwd_context.verify(datos.password, plomero.password_hash):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
    token = _crear_token(plomero.id_plomero)
    return PlomeroLoginResponse(
        access_token = token,
        token_type   = "bearer",
        id_plomero   = plomero.id_plomero,
        nombre       = plomero.nombre,
    )


# ── OTROS ─────────────────────────────────────────────────────────────────────

def obtener_todos(db: Session) -> list[PlomeroResponse]:
    return [PlomeroResponse.model_validate(p) for p in plomero_repository.listar_todos(db)]


def obtener_por_id(db: Session, id: int) -> PlomeroResponse:
    plomero = plomero_repository.buscar_por_id(db, id)
    if not plomero:
        raise HTTPException(status_code=404, detail="Plomero no encontrado")
    return PlomeroResponse.model_validate(plomero)


def cambiar_disponibilidad(db: Session, id: int, disponible: bool) -> dict:
    plomero = plomero_repository.actualizar_disponibilidad(db, id, disponible)
    if not plomero:
        raise HTTPException(status_code=404, detail="Plomero no encontrado")
    return {"mensaje": f"Plomero marcado como {'disponible' if disponible else 'no disponible'}"}


def buscar(
    db:                Session,
    localidad:         Optional[str]  = None,
    genero:            Optional[str]  = None,
    especialidad:      Optional[str]  = None,
    atiende_urgencias: Optional[bool] = None,
) -> list[PlomeroResponse]:
    plomeros = plomero_repository.filtrar(db, localidad, genero, especialidad, atiende_urgencias)
    return [PlomeroResponse.model_validate(p) for p in plomeros]


def olvide_password(db: Session, email: str) -> dict:
    plomero = plomero_repository.buscar_por_email(db, email)
    if not plomero:
        return {"mensaje": "Si el email existe, vas a recibir un link para restablecer tu contraseña"}
    token = secrets.token_urlsafe(32)
    plomero_repository.guardar_reset_token(db, plomero.id_plomero, token)
    try:
        enviar_reset_password(plomero.email, token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar el email: {str(e)}")
    return {"mensaje": "Si el email existe, vas a recibir un link para restablecer tu contraseña"}


def reset_password(db: Session, token: str, nueva_password: str) -> dict:
    plomero = plomero_repository.buscar_por_reset_token(db, token)
    if not plomero:
        raise HTTPException(status_code=400, detail="Token inválido o ya usado")
    plomero_repository.actualizar_password(db, plomero.id_plomero, pwd_context.hash(nueva_password))
    return {"mensaje": "Contraseña actualizada correctamente"}