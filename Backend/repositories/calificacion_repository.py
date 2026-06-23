# repositories/calificacion_repository.py
from sqlalchemy.orm import Session
from models.calificacion import Calificacion


# ─────────────────────────────────────────────
# ESCRITURA
# ─────────────────────────────────────────────

def registrar_calificacion(
    db:           Session,
    id_solicitud: int,
    id_plomero:   int,
    id_cliente:   int,
    autor_rol:    str,
    estrellas:    float,
    comentario:   str | None,
) -> Calificacion:
    """
    Registra una calificación.
    autor_rol puede ser:
      "cliente"         → calificación real del cliente al plomero
      "plomero"         → calificación real del plomero al cliente
      "sistema_cliente" → calificación automática por cancelación del cliente
      "sistema_plomero" → calificación automática por cancelación del plomero
    """
    nueva = Calificacion(
        id_solicitud = id_solicitud,
        id_plomero   = id_plomero,
        id_cliente   = id_cliente,
        autor_rol    = autor_rol,
        estrellas    = estrellas,
        comentario   = comentario,
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


# ─────────────────────────────────────────────
# VERIFICACIÓN DE DUPLICADOS
# ─────────────────────────────────────────────

def ya_califico(
    db:           Session,
    id_solicitud: int,
    autor_rol:    str,
) -> bool:
    """
    Verifica si ya existe una calificación para esta solicitud
    emitida por el rol indicado. Evita doble calificación.
    Para calificaciones automáticas del sistema usa
    autor_rol="sistema_cliente" o "sistema_plomero".
    """
    return db.query(Calificacion).filter(
        Calificacion.id_solicitud == id_solicitud,
        Calificacion.autor_rol    == autor_rol,
    ).first() is not None


# ─────────────────────────────────────────────
# CÁLCULO DE PROMEDIOS
# ─────────────────────────────────────────────

def calcular_promedio_plomero(db: Session, id_plomero: int) -> float:
    """
    Promedio ponderado de la reputación del plomero.
    Incluye calificaciones reales ("cliente") y automáticas ("sistema_cliente").
    El 5 inicial cuenta como 1 trabajo base para que los plomeros nuevos
    no arranquen en 0 si aún no tienen evaluaciones.

    Ejemplo:
      3 trabajos bien calificados (5, 4, 5) + 1 cancelación sin aviso (0.5)
      → (5_base + 5 + 4 + 5 + 0.5) / 5 = 3.9
    """
    calificaciones = (
        db.query(Calificacion)
        .filter(
            Calificacion.id_plomero == id_plomero,
            Calificacion.autor_rol.in_(["cliente", "sistema_cliente"]),
        )
        .all()
    )

    if not calificaciones:
        return 5.0

    suma     = 5.0   # reputación inicial base
    cantidad = 1     # cuenta como 1 valoración

    for c in calificaciones:
        suma     += c.estrellas
        cantidad += 1

    return round(suma / cantidad, 2)


def calcular_promedio_cliente(db: Session, id_cliente: int) -> float:
    """
    Promedio ponderado de la reputación del cliente.
    Incluye calificaciones reales ("plomero") y automáticas ("sistema_plomero").
    Misma lógica de base 5 que para el plomero.
    """
    calificaciones = (
        db.query(Calificacion)
        .filter(
            Calificacion.id_cliente == id_cliente,
            Calificacion.autor_rol.in_(["plomero", "sistema_plomero"]),
        )
        .all()
    )

    if not calificaciones:
        return 5.0

    suma     = 5.0
    cantidad = 1

    for c in calificaciones:
        suma     += c.estrellas
        cantidad += 1

    return round(suma / cantidad, 2)


# ─────────────────────────────────────────────
# CONSULTAS
# ─────────────────────────────────────────────

def obtener_calificaciones_plomero(
    db: Session, id_plomero: int
) -> list[Calificacion]:
    """Todas las evaluaciones recibidas por el plomero (reales + automáticas)."""
    return (
        db.query(Calificacion)
        .filter(
            Calificacion.id_plomero == id_plomero,
            Calificacion.autor_rol.in_(["cliente", "sistema_cliente"]),
        )
        .order_by(Calificacion.fecha_resenia.desc())
        .all()
    )


def obtener_calificaciones_cliente(
    db: Session, id_cliente: int
) -> list[Calificacion]:
    """Todas las evaluaciones recibidas por el cliente (reales + automáticas)."""
    return (
        db.query(Calificacion)
        .filter(
            Calificacion.id_cliente == id_cliente,
            Calificacion.autor_rol.in_(["plomero", "sistema_plomero"]),
        )
        .order_by(Calificacion.fecha_resenia.desc())
        .all()
    )