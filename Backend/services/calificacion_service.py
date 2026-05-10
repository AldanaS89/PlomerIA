from fastapi import HTTPException
from sqlalchemy.orm import Session
from repositories.calificacion_repository import crear_calificacion
from models import Solicitud, EstadoSolicitud

def calificar_trabajo(db: Session, id_solicitud: int, id_cliente: int, estrellas: int, comentario: str):
    # 1. Validar que la solicitud exista y esté completada
    solicitud = db.query(Solicitud).filter(Solicitud.id_solicitud == id_solicitud).first()
    
    if not solicitud or solicitud.id_usuario != id_cliente:
        raise HTTPException(status_code=403, detail="No puedes calificar este trabajo.")
    
    if solicitud.estado != EstadoSolicitud.COMPLETADO:
        raise HTTPException(status_code=400, detail="Solo puedes calificar trabajos finalizados.")

    # 2. Armar el objeto
    data = {
        "id_asignacion": id_solicitud,
        "id_cliente": id_cliente,
        "id_plomero": solicitud.id_plomero,
        "estrellas": estrellas,
        "comentario": comentario
    }
    
    return crear_calificacion(db, data)