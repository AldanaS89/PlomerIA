from sqlalchemy.orm import Session
from models.solicitud import Solicitud, EstadoSolicitud
from schemas.solicitud import SolicitudCreate


def crear(db: Session, id_usuario: int, datos: SolicitudCreate, diagnostico: dict) -> Solicitud:
    solicitud = Solicitud(
        id_usuario=id_usuario,
        id_plomero=datos.id_plomero,
        descripcion_raw=datos.descripcion_raw,
        imagen_path=datos.imagen_path,
        video_path=datos.video_path,
        etiqueta_ia=diagnostico.get("etiqueta_ia"),
        urgencia_ia=diagnostico.get("urgencia_ia"),
        presupuesto_min=diagnostico.get("presupuesto_min"),
        presupuesto_max=diagnostico.get("presupuesto_max"),
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)
    return solicitud


def asignar_plomero(db: Session, id_solicitud: int, id_plomero: int) -> Solicitud | None:
    solicitud = obtener_por_id(db, id_solicitud)
    if not solicitud:
        return None
    solicitud.id_plomero = id_plomero
    db.commit()
    db.refresh(solicitud)
    return solicitud


def obtener_por_id(db: Session, id: int) -> Solicitud | None:
    return db.query(Solicitud).filter(Solicitud.id_solicitud == id).first()


def listar_por_usuario(db: Session, id_usuario: int) -> list[Solicitud]:
    return (
        db.query(Solicitud)
        .filter(Solicitud.id_usuario == id_usuario)
        .order_by(Solicitud.fecha.desc())
        .all()
    )


def listar_por_plomero(db: Session, id_plomero: int) -> list[Solicitud]:
    return (
        db.query(Solicitud)
        .filter(Solicitud.id_plomero == id_plomero)
        .order_by(Solicitud.fecha.desc())
        .all()
    )


def cambiar_estado(db: Session, id: int, estado: EstadoSolicitud) -> Solicitud | None:
    solicitud = obtener_por_id(db, id)
    if not solicitud:
        return None
    solicitud.estado = estado
    db.commit()
    db.refresh(solicitud)
    return solicitud
