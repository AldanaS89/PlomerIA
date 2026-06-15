from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from models.solicitud_plomero import EstadoInvitacion, SolicitudPlomero
from models.solicitud import Solicitud, EstadoSolicitud
from models.plomero import Plomero

from sqlalchemy.orm import joinedload, Session

from models.solicitud import Solicitud, EstadoSolicitud
from models.solicitud_plomero import (
    SolicitudPlomero,
    EstadoInvitacion,
)


def _cargar_relaciones(query):
    return query.options(
        joinedload(Solicitud.plomero),
        joinedload(Solicitud.usuario),
        joinedload(Solicitud.plomeros)
            .joinedload(SolicitudPlomero.plomero)
    )


def crear(
    db: Session,
    id_usuario: int,
    datos,
    diagnostico: dict
) -> Solicitud:

    solicitud = Solicitud(
        id_usuario=id_usuario,
        descripcion_raw=datos.descripcion_raw,
        localidad_evento=datos.localidad_evento,
        latitud_evento=datos.latitud_evento,
        longitud_evento=datos.longitud_evento,
        etiqueta_ia=diagnostico["etiqueta_ia"],
        urgencia_ia=diagnostico["urgencia_ia"],
        presupuesto_min=diagnostico["presupuesto_min"],
        presupuesto_max=diagnostico["presupuesto_max"],
        fecha_trabajo=datos.fecha_trabajo,
        # turno_solicitado=(
        #     next(
        #         iter(datos.turnos_por_plomero.values()),
        #         None
        #     )
        #     if datos.turnos_por_plomero
        #     else None
        # ),
        estado=EstadoSolicitud.PENDIENTE,
    )

    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)

    return solicitud


def asignar_plomero(
    db: Session,
    id_solicitud: int,
    id_plomero: int | None
):
    solicitud = obtener_por_id(db, id_solicitud)

    if not solicitud:
        return None

    solicitud.id_plomero = id_plomero

    db.commit()
    db.refresh(solicitud)

    return solicitud


def obtener_por_id(
    db: Session,
    id_solicitud: int
):
    return (
        _cargar_relaciones(
            db.query(Solicitud)
        )
        .filter(
            Solicitud.id_solicitud == id_solicitud
        )
        .first()
    )


def listar_por_usuario(
    db: Session,
    id_usuario: int
):
    return (
        _cargar_relaciones(
            db.query(Solicitud)
        )
        .filter(
            Solicitud.id_usuario == id_usuario
        )
        .order_by(Solicitud.fecha.desc())
        .all()
    )


def listar_por_plomero(
    db: Session,
    id_plomero: int
):
    solicitudes_asignadas = (
        _cargar_relaciones(
            db.query(Solicitud)
        )
        .filter(
            Solicitud.id_plomero == id_plomero,
            Solicitud.estado != EstadoSolicitud.CANCELADA,
        )
        .all()
    )

    invitaciones = (
        db.query(SolicitudPlomero)
        .filter(
            SolicitudPlomero.id_plomero == id_plomero,
            SolicitudPlomero.estado == EstadoInvitacion.CONTACTADO,
        )
        .all()
    )

    ids_solicitudes = {
        invitacion.id_solicitud
        for invitacion in invitaciones
    }

    solicitudes_pendientes = []

    if ids_solicitudes:
        solicitudes_pendientes = (
            _cargar_relaciones(
                db.query(Solicitud)
            )
            .filter(
                Solicitud.id_solicitud.in_(ids_solicitudes),
                Solicitud.estado != EstadoSolicitud.CANCELADA,
            )
            .all()
        )

    return list({
        solicitud.id_solicitud: solicitud
        for solicitud in (
            solicitudes_asignadas +
            solicitudes_pendientes
        )
    }.values())


def cambiar_estado(
    db: Session,
    id_solicitud: int,
    nuevo_estado
):
    solicitud = obtener_por_id(
        db,
        id_solicitud
    )

    if not solicitud:
        return None

    solicitud.estado = nuevo_estado

    db.commit()
    db.refresh(solicitud)

    return solicitud


def buscar_por_texto(
    db: Session,
    q: str
):
    query = _cargar_relaciones(
        db.query(Solicitud)
    )

    if q:
        query = query.filter(
            Solicitud.descripcion_raw.ilike(f"%{q}%")
        )

    return query.order_by(
        Solicitud.fecha.desc()
    ).all()