from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional

from utils.seguridad import create_token, hash_password, verify_password
from services.disponibilidad_service import guardar_agenda_inicial
from repositories import plomero_repository
from schemas.plomero import (
    PlomeroLoginRequest,
    PlomeroLoginResponse,
    PlomeroResponse
)



from utils.geolocalizacion import (
    geocodificar
)

from utils.email import enviar_reset_password

from models.plomero import Plomero

import secrets

RADIO_KM = 5.0


# ─────────────────────────────
# LOGIN
# ─────────────────────────────

def login(
    db: Session,
    datos: PlomeroLoginRequest
) -> PlomeroLoginResponse:

    plomero = plomero_repository.buscar_por_email(
        db,
        datos.email
    )

    if not plomero or not verify_password(
        datos.password,
        plomero.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Email o contraseña incorrectos"
        )

    token = create_token({"sub": str(plomero.id_plomero), "tipo": "plomero"})

    return PlomeroLoginResponse(
        access_token = token,
        token_type   = "bearer",
        id_plomero   = plomero.id_plomero,
        nombre       = plomero.nombre,
    )


# ─────────────────────────────
# REGISTRO
# ─────────────────────────────

def registrar_completo(
    db: Session,
    nombre: str,
    apellido: str,
    email: str,
    password: str,
    telefono: str,
    direccion: str,
    localidad: str,
    especialidades: list[str],
    otra_especialidad: Optional[str],
    genero: str,
    atiende_urgencias: bool,
    matricula_gas: bool,
    agenda: dict,
    foto_path: Optional[str],
):
    if plomero_repository.buscar_por_email(db, email):
        raise HTTPException(
            status_code=400,
            detail="El email ya está registrado"
        )

    latitud, longitud = geocodificar(direccion, localidad)

    esp_final = []
    otra_custom = otra_especialidad

    for e in especialidades:
        if e.startswith("OTRA:"):
            otra_custom = e[5:]
        else:
            esp_final.append(e.upper())

    nuevo = Plomero(
        especialidad        = esp_final[0] if esp_final else "PLOMERIA_GENERAL",
        especialidades      = esp_final,
        otra_especialidad   = otra_custom,
        nombre              = nombre,
        apellido            = apellido,
        email               = email,
        telefono            = telefono,
        genero              = genero,
        localidad           = localidad,
        latitud             = latitud,
        longitud            = longitud,
        atiende_urgencias   = atiende_urgencias,
        matricula_gas       = matricula_gas,
        password_hash       = hash_password(password),
        disponible_ahora    = True,
        puntuacion          = 0.0,
        total_trabajos      = 0,
        foto_perfil_path    = foto_path,
        agenda              = agenda if agenda else None,
    )

    plomero = plomero_repository.crear_plomero(db, nuevo)

    if agenda:
        guardar_agenda_inicial(db, plomero.id_plomero, agenda)

    token = create_token({"sub": str(plomero.id_plomero), "tipo": "plomero"})

    return {
        "mensaje":      "Plomero registrado correctamente",
        "access_token": token,
        "token_type":   "bearer",
        "id_plomero":   plomero.id_plomero,
        "nombre":       plomero.nombre,
    }


# ─────────────────────────────
# RESET PASSWORD
# ─────────────────────────────

def olvide_password(
    db: Session,
    email: str
):

    plomero = plomero_repository.buscar_por_email(
        db,
        email
    )

    if not plomero:
        return {
            "mensaje":
            "Si el email existe, vas a recibir un link para restablecer tu contraseña"
        }

    token = secrets.token_urlsafe(32)

    plomero_repository.guardar_reset_token(
        db,
        plomero.id_plomero,
        token
    )

    try:
        enviar_reset_password(
            plomero.email,
            token
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al enviar el email: {str(e)}"
        )

    return {
        "mensaje":
        "Si el email existe, vas a recibir un link para restablecer tu contraseña"
    }


def reset_password(
    db: Session,
    token: str,
    nueva_password: str
):

    plomero = plomero_repository.buscar_por_reset_token(
        db,
        token
    )

    if not plomero:
        raise HTTPException(
            status_code=400,
            detail="Token inválido o ya usado"
        )

    nuevo_hash = hash_password(
        nueva_password
    )

    plomero_repository.actualizar_password(
        db,
        plomero.id_plomero,
        nuevo_hash
    )

    return {
        "mensaje":
        "Contraseña actualizada correctamente"
    }
    
    
# ─────────────────────────────
# SUGERIR
# ─────────────────────────────

DIAS_ES       = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
FRANJAS       = ["manana", "tarde", "noche"]
FRANJA_INICIO = {"manana": 8, "tarde": 13, "noche": 18}


def sugerir(
    db:              Session,
    descripcion:     str,
    solo_mujeres:    bool,
    lat_usuario:     float | None,
    lon_usuario:     float | None,
    urgencia_forzada: bool,
):
    from services import ia_service

    diagnostico   = ia_service.analizar_descripcion(descripcion)
    etiqueta      = diagnostico["etiqueta_ia"]
    urgencia_ia   = diagnostico["urgencia_ia"]
    es_urgente    = urgencia_forzada or (urgencia_ia == "URGENTE")
    genero_filtro = "F" if solo_mujeres else None

    ahora       = datetime.now()
    hora_actual = ahora.hour
    dia_hoy     = DIAS_ES[ahora.weekday()]
    dia_manana  = DIAS_ES[(ahora.weekday() + 1) % 7]
    franjas_hoy = [f for f in FRANJAS if FRANJA_INICIO[f] > hora_actual + 1]
    keys_urgencia = (
        {f"{dia_hoy}_{f}" for f in franjas_hoy} |
        {f"{dia_manana}_{f}" for f in ["manana", "tarde"]}
    )

    def tiene_slot(p):
        if not p.agenda:
            return p.disponible_ahora
        return any(p.agenda.get(k) for k in keys_urgencia)

    def dist(p):
        if lat_usuario and lon_usuario and p.latitud and p.longitud:
            return plomero_repository._distancia_km(lat_usuario, lon_usuario, p.latitud, p.longitud)
        return 9999

    def relevancia(p):
        score = 0
        if etiqueta and p.especialidades and etiqueta in p.especialidades:
            score += 3
        if es_urgente and p.atiende_urgencias and p.disponible_ahora:
            score += 5
        return score

    if es_urgente:
        plomeros = []
        for radio in [5, 10, 20, 50, None]:
            candidatos = plomero_repository.filtrar(
                db,
                genero            = genero_filtro,
                atiende_urgencias = True,
                solo_disponibles  = True,
                lat_usuario       = lat_usuario if radio else None,
                lon_usuario       = lon_usuario if radio else None,
                radio_km          = radio,
            )
            candidatos = [p for p in candidatos if tiene_slot(p)]
            if len(candidatos) >= 5:
                plomeros = candidatos
                break
            plomeros = candidatos

        if len(plomeros) < 5:
            ids_ya = {p.id_plomero for p in plomeros}
            for p in plomero_repository.filtrar(db, genero=genero_filtro, solo_disponibles=True):
                if p.id_plomero not in ids_ya and tiene_slot(p):
                    plomeros.append(p)
                    ids_ya.add(p.id_plomero)
    else:
        plomeros = plomero_repository.filtrar(db, genero=genero_filtro, lat_usuario=lat_usuario, lon_usuario=lon_usuario)

    vistos, unicos = set(), []
    for p in plomeros:
        if p.id_plomero not in vistos:
            vistos.add(p.id_plomero)
            unicos.append(p)

    resultado = sorted(unicos, key=lambda p: (-relevancia(p), -p.puntuacion, dist(p)))[:5]

    return [
        {
            "id_plomero":        p.id_plomero,
            "nombre":            p.nombre,
            "apellido":          p.apellido,
            "foto_perfil_path":  p.foto_perfil_path,
            "especialidad":      (p.especialidades or [etiqueta])[0],
            "especialidades":    p.especialidades or [],
            "localidad":         p.localidad,
            "puntuacion":        p.puntuacion,
            "total_trabajos":    p.total_trabajos,
            "atiende_urgencias": p.atiende_urgencias,
            "disponible_ahora":  p.disponible_ahora,
            "genero":            p.genero,
            "distancia_km":      round(dist(p), 2) if dist(p) < 9999 else None,
            "etiqueta_ia":       etiqueta,
            "urgencia_ia":       urgencia_ia,
            "agenda":            {k: True for k in keys_urgencia if p.agenda.get(k)} if es_urgente and p.agenda else p.agenda or {},
        }
        for p in resultado
    ]
    
# ─────────────────────────────
# DISPONIBILIDAD
# ─────────────────────────────

def cambiar_disponibilidad(db: Session, id_plomero: int, disponible: bool):
    plomero = plomero_repository.actualizar_disponibilidad(db, id_plomero, disponible)
    if not plomero:
        raise HTTPException(status_code=404, detail="Plomero no encontrado")
    return {"mensaje": "Disponibilidad actualizada", "disponible_ahora": plomero.disponible_ahora}


# ─────────────────────────────
# PERFIL
# ─────────────────────────────

def obtener_por_id(db: Session, id: int):
    plomero = plomero_repository.buscar_por_id(db, id)
    if not plomero:
        raise HTTPException(status_code=404, detail="Plomero no encontrado")
    return PlomeroResponse.model_validate(plomero)