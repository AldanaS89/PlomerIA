# repositories/solicitud_repository.py
from sqlalchemy.orm import Session
from models.solicitud import Solicitud, EstadoSolicitud
from models.plomero import Plomero
from schemas.solicitud import SolicitudCreate
from typing import List, Optional


def crear(db: Session, id_usuario: int, datos: SolicitudCreate, diagnostico: dict) -> Solicitud:
    solicitud = Solicitud(
        id_usuario       = id_usuario,
        descripcion_raw  = datos.descripcion_raw,
        localidad_evento = datos.localidad_evento,
        estado           = EstadoSolicitud.PENDIENTE
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
    return db.query(Solicitud).filter(Solicitud.id_usuario == id_usuario).all()


def listar_por_plomero(db: Session, id_plomero: int) -> list[Solicitud]:
    return db.query(Solicitud).filter(Solicitud.id_plomero == id_plomero).all()


def _plomero_a_dict(p: Plomero) -> dict:
    """Convierte un Plomero en dict con los datos que necesita el frontend."""
    return {
        "id_plomero":       p.id_plomero,
        "nombre":           p.nombre,
        "apellido":         p.apellido,
        "foto_perfil_path": p.foto_perfil_path,
        "localidad":        p.localidad,
        "puntuacion":       p.puntuacion,
        "total_trabajos":   p.total_trabajos,
        "atiende_urgencias":p.atiende_urgencias,
        "especialidades":   p.especialidades or [],
        "telefono":         p.telefono,
    }


def listar_con_nombres(db: Session) -> list:
    """Trae todas las solicitudes con nombre del plomero asignado."""
    resultados = db.query(
        Solicitud,
        (Plomero.nombre + " " + Plomero.apellido).label("nombre_plomero")
    ).outerjoin(Plomero, Solicitud.id_plomero == Plomero.id_plomero).all()

    for solicitud, nombre in resultados:
        solicitud.nombre_plomero = nombre if nombre else "Sin asignar"

    return [r[0] for r in resultados]


def listar_por_usuario_con_detalle(db: Session, id_usuario: int) -> list[dict]:
    """
    Devuelve las solicitudes del usuario con:
    - datos del plomero asignado (si lo hay)
    - datos de los plomeros sugeridos/notificados (mientras está PENDIENTE)
    """
    solicitudes = (
        db.query(Solicitud)
        .filter(Solicitud.id_usuario == id_usuario)
        .order_by(Solicitud.fecha.desc())
        .all()
    )

    resultado = []
    for s in solicitudes:
        item = {
            "id_solicitud":    s.id_solicitud,
            "id_usuario":      s.id_usuario,
            "descripcion_raw": s.descripcion_raw,
            "estado":          s.estado.value if hasattr(s.estado, "value") else str(s.estado),
            "fecha":           s.fecha.isoformat() if s.fecha else None,
            "plomero":         None,
            "plomeros_notificados": [],
        }

        # Plomero asignado (cuando ya aceptó)
        if s.id_plomero:
            p = db.query(Plomero).filter(Plomero.id_plomero == s.id_plomero).first()
            if p:
                item["plomero"] = _plomero_a_dict(p)

        # Plomeros notificados (los 5 sugeridos originalmente)
        if s.ids_plomeros_sugeridos:
            try:
                ids = [int(i.strip()) for i in s.ids_plomeros_sugeridos.split(",") if i.strip()]
                plomeros = db.query(Plomero).filter(Plomero.id_plomero.in_(ids)).all()
                # Mantener el orden original
                orden = {pid: idx for idx, pid in enumerate(ids)}
                plomeros_ordenados = sorted(plomeros, key=lambda p: orden.get(p.id_plomero, 99))
                item["plomeros_notificados"] = [_plomero_a_dict(p) for p in plomeros_ordenados]
            except Exception:
                item["plomeros_notificados"] = []

        resultado.append(item)

    return resultado


def cambiar_estado(db: Session, id: int, nuevo_estado: str) -> Solicitud | None:
    solicitud = obtener_por_id(db, id)
    if not solicitud:
        return None
    solicitud.estado = nuevo_estado
    db.commit()
    db.refresh(solicitud)
    return solicitud


def guardar_ids_sugeridos(db: Session, id_solicitud: int, ids: list[int]) -> None:
    solicitud = obtener_por_id(db, id_solicitud)
    if solicitud:
        solicitud.ids_plomeros_sugeridos = ", ".join(str(i) for i in ids)
        db.commit()