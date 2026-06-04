
from requests import Session

from models.solicitud_plomero import EstadoInvitacion, SolicitudPlomero

# repositories/solicitud_plomero_repository.py

from sqlalchemy.orm import Session

from models.solicitud_plomero import (
    SolicitudPlomero,
    EstadoInvitacion
)


def crear_invitacion(
    db: Session,
    id_solicitud: int,
    id_plomero: int
):
    invitacion = SolicitudPlomero(
        id_solicitud=id_solicitud,
        id_plomero=id_plomero,
        estado=EstadoInvitacion.CONTACTADO
    )

    db.add(invitacion)
    db.commit()
    db.refresh(invitacion)

    return invitacion

def crear_invitaciones_bulk(
    db: Session,
    id_solicitud: int,
    ids_plomeros: list[int]
) -> list[SolicitudPlomero]:

    invitaciones = []

    for id_plomero in ids_plomeros:

        existe = (
            db.query(SolicitudPlomero)
            .filter(
                SolicitudPlomero.id_solicitud == id_solicitud,
                SolicitudPlomero.id_plomero == id_plomero,
            )
            .first()
        )

        if existe:
            continue

        inv = SolicitudPlomero(
            id_solicitud=id_solicitud,
            id_plomero=id_plomero,
            estado=EstadoInvitacion.CONTACTADO
        )

        db.add(inv)
        invitaciones.append(inv)

    db.commit()

    for inv in invitaciones:
        db.refresh(inv)

    return invitaciones

def obtener_invitacion(
    db: Session,
    id_solicitud: int,
    id_plomero: int
):
    return (
        db.query(SolicitudPlomero)
        .filter(
            SolicitudPlomero.id_solicitud == id_solicitud,
            SolicitudPlomero.id_plomero == id_plomero
        )
        .first()
    )


def cambiar_estado_invitacion(
    db: Session,
    id_solicitud: int,
    id_plomero: int,
    estado: EstadoInvitacion
):
    invitacion = obtener_invitacion(
        db,
        id_solicitud,
        id_plomero
    )

    if not invitacion:
        return None

    invitacion.estado = estado

    db.commit()
    db.refresh(invitacion)

    return invitacion


def obtener_aceptado(
    db: Session,
    id_solicitud: int
):
    return (
        db.query(SolicitudPlomero)
        .filter(
            SolicitudPlomero.id_solicitud == id_solicitud,
            SolicitudPlomero.estado == EstadoInvitacion.ACEPTADO
        )
        .first()
    )


def obtener_por_solicitud(
    db: Session,
    id_solicitud: int
):
    return (
        db.query(SolicitudPlomero)
        .filter(
            SolicitudPlomero.id_solicitud == id_solicitud
        )
        .all()
    )


def quedan_contactados(
    db: Session,
    id_solicitud: int
):
    cantidad = (
        db.query(SolicitudPlomero)
        .filter(
            SolicitudPlomero.id_solicitud == id_solicitud,
            SolicitudPlomero.estado == EstadoInvitacion.CONTACTADO
        )
        .count()
    )

    return cantidad > 0

#Ver estos
def obtener_contactados(db: Session, id_solicitud: int) -> set[int]:
    """IDs de todos los plomeros que ya fueron contactados."""
    rows = db.query(SolicitudPlomero.id_plomero).filter(
        SolicitudPlomero.id_solicitud == id_solicitud,
    ).all()
    return {r.id_plomero for r in rows}

def obtener_activos(db: Session, id_solicitud: int) -> list[SolicitudPlomero]:
    """Invitaciones en estado CONTACTADO (esperando respuesta)."""
    return db.query(SolicitudPlomero).filter(
        SolicitudPlomero.id_solicitud == id_solicitud,
        SolicitudPlomero.estado       == EstadoInvitacion.CONTACTADO,
    ).all()

def cancelar_activos(db: Session, id_solicitud: int, excluir_id: int | None = None) -> None:
    """Marca como CANCELADO todas las invitaciones activas excepto una."""
    query = db.query(SolicitudPlomero).filter(
        SolicitudPlomero.id_solicitud == id_solicitud,
        SolicitudPlomero.estado       == EstadoInvitacion.CONTACTADO,
    )
    if excluir_id:
        query = query.filter(SolicitudPlomero.id_plomero != excluir_id)
    query.update({"estado": EstadoInvitacion.CANCELADO}, synchronize_session=False)
    db.commit()