# repositories/solicitud_repository.py
from sqlalchemy.orm import Session
from models.solicitud import Solicitud, EstadoSolicitud
from models.plomero import Plomero 
from schemas.solicitud import SolicitudCreate
from typing import List, Optional


def crear(db: Session, id_usuario: int, datos: SolicitudCreate, diagnostico: dict) -> Solicitud:
    solicitud = Solicitud(
        id_usuario             = id_usuario,
        id_plomero             = datos.id_plomero,
        descripcion_raw        = datos.descripcion_raw,
        localidad_evento       = datos.localidad_evento,
        imagen_path            = datos.imagen_path,
        video_path             = datos.video_path,
        estado                 = EstadoSolicitud.PENDIENTE
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
    """Busca todas las solicitudes de un cliente específico."""
    return db.query(Solicitud).filter(Solicitud.id_usuario == id_usuario).all()

def listar_por_plomero(db: Session, id_plomero: int) -> list[Solicitud]:
    """
    Devuelve las solicitudes relevantes para un plomero:
    - Pendientes donde su ID aparece en ids_plomeros_sugeridos (le llegó la notificación)
    - Aceptadas/completadas donde él es el plomero asignado
    """
    todas = db.query(Solicitud).filter(
        Solicitud.estado != EstadoSolicitud.RECHAZADO
    ).order_by(Solicitud.fecha.desc()).all()

    resultado = []
    id_str = str(id_plomero)

    for s in todas:
        # Es el plomero asignado
        if s.id_plomero == id_plomero:
            resultado.append(s)
            continue
        # Está en la lista de sugeridos (pendiente y le llegó la notif)
        if s.estado == EstadoSolicitud.PENDIENTE and s.ids_plomeros_sugeridos:
            ids = [i.strip() for i in s.ids_plomeros_sugeridos.split(",")]
            if id_str in ids:
                resultado.append(s)

    return resultado

def listar_con_nombres(db: Session) -> list:
    """Trae todas las solicitudes unidas con el nombre del plomero."""
    resultados = db.query(
        Solicitud, 
        (Plomero.nombre + " " + Plomero.apellido).label("nombre_plomero")
    ).outerjoin(Plomero, Solicitud.id_plomero == Plomero.id_plomero).all()
    
    for solicitud, nombre in resultados:
        solicitud.nombre_plomero = nombre if nombre else "Sin asignar"
    
    return [r[0] for r in resultados]

def cambiar_estado(db: Session, id: int, nuevo_estado: str) -> Solicitud | None:
    solicitud = obtener_por_id(db, id)
    if not solicitud:
        return None
    solicitud.estado = nuevo_estado
    db.commit()
    db.refresh(solicitud)
    return solicitud

# solicitud_repository.py — agregar esta función
def guardar_ids_sugeridos(db: Session, id_solicitud: int, ids: list[int]) -> None:
    solicitud = obtener_por_id(db, id_solicitud)
    if solicitud:
        solicitud.ids_plomeros_sugeridos = ", ".join(str(i) for i in ids)
        db.commit()


def _plomero_a_dict(p: Plomero) -> dict:
    return {
        "id_plomero":        p.id_plomero,
        "nombre":            p.nombre,
        "apellido":          p.apellido,
        "foto_perfil_path":  p.foto_perfil_path,
        "localidad":         p.localidad,
        "puntuacion":        p.puntuacion,
        "total_trabajos":    p.total_trabajos,
        "atiende_urgencias": p.atiende_urgencias,
        "especialidades":    p.especialidades or [],
        "telefono":          p.telefono,
    }


def listar_por_usuario_con_detalle(db: Session, id_usuario: int) -> list[dict]:
    """
    Devuelve las solicitudes del usuario con datos completos:
    - plomero asignado (si aceptó)
    - plomeros_notificados: lista con datos de cada plomero sugerido
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
            "id_solicitud":         s.id_solicitud,
            "id_usuario":           s.id_usuario,
            "descripcion_raw":      s.descripcion_raw,
            "estado":               s.estado.value if hasattr(s.estado, "value") else str(s.estado),
            "fecha":                s.fecha.isoformat() if s.fecha else None,
            "plomero":              None,
            "plomeros_notificados": [],
        }

        if s.id_plomero:
            p = db.query(Plomero).filter(Plomero.id_plomero == s.id_plomero).first()
            if p:
                item["plomero"] = _plomero_a_dict(p)

        if s.ids_plomeros_sugeridos:
            try:
                ids = [int(i.strip()) for i in s.ids_plomeros_sugeridos.split(",") if i.strip()]
                plomeros = db.query(Plomero).filter(Plomero.id_plomero.in_(ids)).all()
                orden = {pid: idx for idx, pid in enumerate(ids)}
                plomeros_ord = sorted(plomeros, key=lambda p: orden.get(p.id_plomero, 99))
                item["plomeros_notificados"] = [_plomero_a_dict(p) for p in plomeros_ord]
            except Exception:
                item["plomeros_notificados"] = []

        resultado.append(item)

    return resultado