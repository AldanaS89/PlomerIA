from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from repositories import disponibilidad_repository

from models.bloqueHorario import BloqueHorario

from schemas.disponibilidad import (
    BloqueOut,
    BloquearRequest
)
def guardar_agenda_inicial(db: Session, id_plomero: int, agenda: dict) -> None:
    """
    Convierte la agenda del formulario en bloques horarios para las próximas 4 semanas.
    agenda = {"Lun_manana": True, "Mar_tarde": True, ...}
    """
    try:

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


# ─────────────────────────────
# VER DISPONIBILIDAD
# ─────────────────────────────

def ver_disponibilidad(
    db: Session,
    id_plomero: int
):

    ahora = datetime.now()
    limite = ahora + timedelta(days=7)

    return disponibilidad_repository.obtener_disponibles(
        db,
        id_plomero,
        ahora,
        limite
    )

# ─────────────────────────────
# BLOQUEAR HORARIO
# ─────────────────────────────

def bloquear_horario(
    db: Session,
    id_plomero: int,
    id_plomero_auth: int,
    datos: BloquearRequest
):

    if id_plomero != id_plomero_auth:
        raise HTTPException(
            status_code=403,
            detail="No podés modificar la agenda de otro plomero"
        )

    nuevo_bloque = BloqueHorario(
        id_plomero = id_plomero,
        inicio     = datos.inicio,
        fin        = datos.fin,
        ocupado    = True,
        descripcion= datos.descripcion
    )

    return disponibilidad_repository.crear_bloque(
        db,
        nuevo_bloque
    )


# ─────────────────────────────
# LIBERAR HORARIO
# ─────────────────────────────

def liberar_horario(
    db: Session,
    id_plomero: int,
    id_bloque: int,
    id_plomero_auth: int
):

    if id_plomero != id_plomero_auth:
        raise HTTPException(
            status_code=403,
            detail="No podés modificar la agenda de otro plomero"
        )

    bloque = disponibilidad_repository.buscar_bloque(
        db,
        id_bloque,
        id_plomero
    )

    if not bloque:
        raise HTTPException(
            status_code=404,
            detail="Bloque no encontrado"
        )

    disponibilidad_repository.eliminar_bloque(
        db,
        bloque
    )

    return {
        "mensaje": "Bloque eliminado"
    }
# ─────────────────────────────

