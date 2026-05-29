# repositories/solicitud_repository.py
from sqlalchemy.orm import Session, joinedload
from models.solicitud import EstadoSolicitud, Solicitud
from models.plomero import Plomero
from models.usuario import Usuario
from schemas.solicitud import SolicitudCreate


def _cargar_relaciones(query):
    """Carga plomero y usuario junto con cada solicitud para evitar lazy loading."""
    return query.options(
        joinedload(Solicitud.plomero),
        joinedload(Solicitud.usuario),
    )


def crear(db: Session, id_usuario: int, datos: SolicitudCreate, diagnostico: dict) -> Solicitud:
    solicitud = Solicitud(
        id_usuario       = id_usuario,
        descripcion_raw  = datos.descripcion_raw,
        localidad_evento = datos.localidad_evento,
        latitud_evento   = datos.latitud_evento,
        longitud_evento  = datos.longitud_evento,
        etiqueta_ia      = diagnostico["etiqueta_ia"],
        urgencia_ia      = diagnostico["urgencia_ia"],
        presupuesto_min  = diagnostico["presupuesto_min"],
        presupuesto_max  = diagnostico["presupuesto_max"],
        estado           = EstadoSolicitud.PENDIENTE
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)
    return solicitud


def asignar_plomero(db: Session, id_solicitud: int, id_plomero: int | None) -> Solicitud | None:
    solicitud = obtener_por_id(db, id_solicitud)
    if not solicitud:
        return None
    solicitud.id_plomero = id_plomero
    db.commit()
    db.refresh(solicitud)
    return solicitud


def obtener_por_id(db: Session, id: int) -> Solicitud | None:
    return (
        _cargar_relaciones(db.query(Solicitud))
        .filter(Solicitud.id_solicitud == id)
        .first()
    )


def listar_por_usuario(db: Session, id_usuario: int) -> list[Solicitud]:
    return (
        _cargar_relaciones(db.query(Solicitud))
        .filter(Solicitud.id_usuario == id_usuario)
        .order_by(Solicitud.fecha.desc())
        .all()
    )


def listar_por_plomero(db: Session, id_plomero: int) -> list[Solicitud]:
    todas = (
        _cargar_relaciones(db.query(Solicitud))
        .filter(Solicitud.estado != EstadoSolicitud.CANCELADA)
        .order_by(Solicitud.fecha.desc())
        .all()
    )

    resultado = []
    id_str = str(id_plomero)

    for s in todas:
        if s.id_plomero == id_plomero:
            resultado.append(s)
            continue
        if s.estado == EstadoSolicitud.PENDIENTE and s.ids_plomeros_sugeridos:
            ids = [i.strip() for i in s.ids_plomeros_sugeridos.split(",")]
            if id_str in ids:
                resultado.append(s)

    return resultado


def cambiar_estado(db: Session, id: int, nuevo_estado) -> Solicitud | None:
    solicitud = obtener_por_id(db, id)
    if not solicitud:
        return None
    solicitud.estado = nuevo_estado
    db.commit()
    # Re-cargar con relaciones después del commit
    return (
        _cargar_relaciones(db.query(Solicitud))
        .filter(Solicitud.id_solicitud == id)
        .first()
    )


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
    }


def buscar_por_texto(db: Session, q: str) -> list[Solicitud]:
    query = _cargar_relaciones(db.query(Solicitud))
    if q:
        query = query.filter(Solicitud.descripcion_raw.ilike(f"%{q}%"))
    return query.order_by(Solicitud.fecha.desc()).all()


def cancelar(db: Session, solicitud: Solicitud):
    solicitud.estado = EstadoSolicitud.CANCELADA
    solicitud.ids_plomeros_sugeridos = None
    db.commit()
    db.refresh(solicitud)
    return solicitud


def remover_plomero_sugerido(db, solicitud, id_plomero):
    if not solicitud.ids_plomeros_sugeridos:
        return
    ids = [i.strip() for i in solicitud.ids_plomeros_sugeridos.split(",") if i.strip()]
    ids = [i for i in ids if i != str(id_plomero)]
    solicitud.ids_plomeros_sugeridos = ",".join(ids)
    db.commit()


def listar_con_nombres(db: Session) -> list[Solicitud]:
    """Trae todas las solicitudes unidas con el nombre del plomero."""
    resultados = db.query(
        Solicitud,
        (Plomero.nombre + " " + Plomero.apellido).label("nombre_plomero")
    ).outerjoin(Plomero, Solicitud.id_plomero == Plomero.id_plomero).all()

    for solicitud, nombre in resultados:
        solicitud.nombre_plomero = nombre if nombre else "Sin asignar"

    return [r[0] for r in resultados]


def listar_por_usuario_con_detalle(db: Session, id_usuario: int) -> list[dict]:
    """
    Devuelve las solicitudes del usuario con datos completos:
    - plomero asignado (si aceptó)
    - plomeros_notificados: lista con datos de cada plomero sugerido
    """
    solicitudes = (
        _cargar_relaciones(db.query(Solicitud))
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

        if s.plomero:
            item["plomero"] = _plomero_a_dict(s.plomero)

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