from fastapi import HTTPException
from sqlalchemy.orm import Session

from schemas.solicitud import SolicitudCreate, SolicitudResponse
from models.solicitud import EstadoSolicitud
from repositories import solicitud_repository, plomero_repository, usuario_repository
from services import ia_service


def _to_response(s) -> SolicitudResponse:
    return SolicitudResponse.from_orm_obj(s)


def crear_solicitud(db: Session, datos: SolicitudCreate, id_usuario: int) -> SolicitudResponse:
    diagnostico = ia_service.analizar_descripcion(datos.descripcion_raw)

    if not datos.id_plomero:
        usuario = usuario_repository.buscar_por_id(db, id_usuario)
        localidad = usuario.localidad if usuario else None

        plomero = plomero_repository.buscar_disponible_para(
            db,
            especialidad=diagnostico["etiqueta_ia"],
            localidad=localidad,
            atiende_urgencias=(diagnostico["urgencia_ia"] == "URGENTE"),
        )
        if not plomero:
            plomero = plomero_repository.buscar_disponible_para(
                db, especialidad=diagnostico["etiqueta_ia"]
            )
        if not plomero:
            plomero = plomero_repository.buscar_disponible_para(db)

        if plomero:
            datos.id_plomero = plomero.id_plomero

    solicitud = solicitud_repository.crear(db, id_usuario, datos, diagnostico)
    return _to_response(solicitud)


def obtener_por_id_s(db: Session, id: int) -> SolicitudResponse | None:
    s = solicitud_repository.obtener_por_id(db, id)
    return _to_response(s) if s else None


def listar_por_usuario_s(db: Session, id_usuario: int) -> list[SolicitudResponse]:
    return [_to_response(s) for s in solicitud_repository.listar_por_usuario(db, id_usuario)]


def listar_por_plomero_s(db: Session, id_plomero: int) -> list[SolicitudResponse]:
    return [_to_response(s) for s in solicitud_repository.listar_por_plomero(db, id_plomero)]


def _cambiar_estado_plomero(
    db: Session, id_solicitud: int, id_plomero: int, nuevo_estado: EstadoSolicitud
) -> SolicitudResponse:
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if solicitud.id_plomero != id_plomero:
        raise HTTPException(status_code=403, detail="Esta solicitud no está asignada a vos")
    solicitud = solicitud_repository.cambiar_estado(db, id_solicitud, nuevo_estado)
    return _to_response(solicitud)


def aceptar(db: Session, id_solicitud: int, id_plomero: int) -> SolicitudResponse:
    return _cambiar_estado_plomero(db, id_solicitud, id_plomero, EstadoSolicitud.ACEPTADO)


def rechazar(db: Session, id_solicitud: int, id_plomero: int) -> SolicitudResponse:
    return _cambiar_estado_plomero(db, id_solicitud, id_plomero, EstadoSolicitud.RECHAZADO)
