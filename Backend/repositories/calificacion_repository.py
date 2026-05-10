from sqlalchemy.orm import Session
from models import Calificacion, Plomero

def crear_calificacion(db: Session, calificacion_data: dict):
    nueva_redenia = Calificacion(**calificacion_data)
    db.add(nueva_redenia)
    
    # Lógica extra: Actualizar el promedio del plomero
    actualizar_promedio_plomero(db, calificacion_data["id_plomero"])
    
    db.commit()
    db.refresh(nueva_redenia)
    return nueva_redenia

def actualizar_promedio_plomero(db: Session, id_plomero: int):
    # Obtenemos todas las estrellas de ese plomero
    calificaciones = db.query(Calificacion).filter(Calificacion.id_plomero == id_plomero).all()
    if calificaciones:
        promedio = sum([c.estrellas for c in calificaciones]) / len(calificaciones)
        # Actualizamos el campo puntuacion en el modelo Plomero
        plomero = db.query(Plomero).filter(Plomero.id_plomero == id_plomero).first()
        if plomero:
            plomero.puntuacion = round(promedio, 1)