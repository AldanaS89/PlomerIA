# repositories/calificacion_repository.py
from sqlalchemy.orm import Session
from models.calificacion import Calificacion


def registrar_calificacion_de_trabajo(
    db:           Session,
    id_solicitud: int,
    id_plomero:   int,
    id_cliente:   int,
    estrellas:    int,
    comentario:   str | None
) -> Calificacion:
    """
    Registra una nueva calificación post-servicio.
    """
    nueva = Calificacion(
        id_solicitud = id_solicitud,
        id_plomero   = id_plomero,
        id_cliente   = id_cliente,
        estrellas    = estrellas,
        comentario   = comentario,
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


def calcular_promedio_puntuacion(
    db: Session,
    id_plomero: int
) -> float:

    calificaciones = (
        db.query(Calificacion)
        .filter(Calificacion.id_plomero == id_plomero)
        .all()
    )

    if not calificaciones:
        return 5.0

    suma = 5  # reputación inicial
    cantidad = 1 # cuenta como una valoración base

    for c in calificaciones:
        suma += c.estrellas
        cantidad += 1

    return round(suma / cantidad, 2)


def cliente_ya_califico_trabajo(
    db:           Session,
    id_solicitud: int,
    id_cliente:   int
) -> bool:
    """
    Evita que el mismo cliente califique dos veces el mismo trabajo.
    """
    return db.query(Calificacion).filter(
        Calificacion.id_solicitud == id_solicitud,
        Calificacion.id_cliente   == id_cliente,
    ).first() is not None


def obtener_calificaciones_plomero(
    db:        Session,
    id_plomero: int
) -> list[Calificacion]:
    """
    Devuelve todas las calificaciones de un plomero
    ordenadas de más reciente a más antigua.
    """
    return db.query(Calificacion).filter(
        Calificacion.id_plomero == id_plomero
    ).order_by(Calificacion.fecha_resenia.desc()).all()