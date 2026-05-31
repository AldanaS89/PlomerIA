from sqlalchemy.orm import Session, joinedload
from models.solicitud import Solicitud, EstadoSolicitud
from models.plomero import Plomero


def _cargar_relaciones(query):
    return query.options(
        joinedload(Solicitud.plomero),
        joinedload(Solicitud.usuario),
    )


def crear(db: Session, id_usuario: int, datos, diagnostico: dict) -> Solicitud:
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
        estado=EstadoSolicitud.PENDIENTE,
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)
    return solicitud


def asignar_plomero(db: Session, id_solicitud: int, id_plomero: int | None):
    solicitud = obtener_por_id(db, id_solicitud)
    if not solicitud:
        return None

    solicitud.id_plomero = id_plomero
    db.commit()
    db.refresh(solicitud)
    return solicitud


def obtener_por_id(db: Session, id: int):
    return (
        _cargar_relaciones(db.query(Solicitud))
        .filter(Solicitud.id_solicitud == id)
        .first()
    )


def listar_por_usuario(db: Session, id_usuario: int):
    return (
        _cargar_relaciones(db.query(Solicitud))
        .filter(Solicitud.id_usuario == id_usuario)
        .order_by(Solicitud.fecha.desc())
        .all()
    )


def listar_por_plomero(db: Session, id_plomero: int):
    return (
        _cargar_relaciones(db.query(Solicitud))
        .filter(Solicitud.estado != EstadoSolicitud.CANCELADA)
        .order_by(Solicitud.fecha.desc())
        .all()
    )


def cambiar_estado(db: Session, id: int, nuevo_estado):
    solicitud = obtener_por_id(db, id)
    if not solicitud:
        return None

    solicitud.estado = nuevo_estado
    db.commit()

    return (
        _cargar_relaciones(db.query(Solicitud))
        .filter(Solicitud.id_solicitud == id)
        .first()
    )


def guardar_ids_sugeridos(db: Session, id_solicitud: int, ids: list[int]):
    solicitud = obtener_por_id(db, id_solicitud)
    if solicitud:
        solicitud.ids_plomeros_sugeridos = ",".join(str(i) for i in ids)
        db.commit()


def buscar_por_texto(db: Session, q: str):
    query = _cargar_relaciones(db.query(Solicitud))
    if q:
        query = query.filter(Solicitud.descripcion_raw.ilike(f"%{q}%"))
    return query.order_by(Solicitud.fecha.desc()).all()


# ─────────────────────────────────────────────
# SCHEDULER (UNIFICADO)
# ─────────────────────────────────────────────
def actualizar_scheduler(db: Session, solicitud: Solicitud, contactados: set, activos: set):
    solicitud.ids_plomeros_contactados = ",".join(contactados)
    solicitud.ids_plomeros_activos = ",".join(activos)
    db.commit()
    db.refresh(solicitud)
    return solicitud