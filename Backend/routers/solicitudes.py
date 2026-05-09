from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from geopy.distance import geodesic
from database import get_db
from models.solicitud import Solicitud, EstadoSolicitud
from models.plomero import Plomero
from schemas.solicitud import SolicitudCreate, SolicitudResponse

router = APIRouter(prefix="", tags=["Solicitudes"])

def buscar_5_mejores(db: Session, lat: float, lon: float, solo_mujeres: bool = False):
    # 1. MODIFICACIÓN: Quitamos temporalmente el filtro de 'disponible_ahora' 
    # para asegurar que tus 100 plomeros de prueba aparezcan.
    query = db.query(Plomero)
    
    # 2. Filtro por género (se activa con tu switch rosado)
    if solo_mujeres:
        query = query.filter(Plomero.genero == 'F')
        
    plomeros = query.all()
    
    # DEBUG: Esto imprimirá en tu terminal cuántos plomeros encontró en la base
    print(f"DEBUG: Se encontraron {len(plomeros)} plomeros en la base de datos.")
    
    candidatos = []
    punto_usuario = (lat, lon)
    
    for p in plomeros:
        # Si p.latitud es None, les asignamos una posición cercana a Longchamps para la demo.
        p_lat = p.latitud if p.latitud else -34.85
        p_lon = p.longitud if p.longitud else -58.38
        
        dist = geodesic(punto_usuario, (p_lat, p_lon)).km
        candidatos.append({
            "id": p.id_plomero, 
            "distancia": dist, 
            "puntuacion": p.puntuacion if p.puntuacion else 0.0
        })
    
    # Ordenamos: más cercanos primero
    candidatos.sort(key=lambda x: (x['distancia'], -x['puntuacion']))
    
    # Devolvemos los IDs de los 5 mejores
    return ", ".join([str(c['id']) for c in candidatos[:5]])
    
@router.post("/", response_model=SolicitudResponse)
async def crear_solicitud(data: SolicitudCreate, db: Session = Depends(get_db)):
    sugeridos_ids = buscar_5_mejores(db, data.latitud_evento, data.longitud_evento, data.solo_mujeres)
    
    nueva_solicitud = Solicitud(
        id_usuario=1,  # ID de Aldana para la demo
        descripcion_raw=data.descripcion_raw,
        localidad_evento=data.localidad_evento,
        latitud_evento=data.latitud_evento,
        longitud_evento=data.longitud_evento,
        ids_plomeros_sugeridos=sugeridos_ids,
        estado=EstadoSolicitud.PENDIENTE # Usamos el Enum para evitar el KeyError
    )
    
    db.add(nueva_solicitud)
    db.commit()
    db.refresh(nueva_solicitud)

    # Transformamos los IDs en datos legibles (Nombre, Calificación) para el Front
    detalles = []
    if sugeridos_ids:
        ids_lista = [int(x.strip()) for x in sugeridos_ids.split(',')]
        for p_id in ids_lista:
            p = db.query(Plomero).filter(Plomero.id_plomero == p_id).first()
            if p:
                detalles.append({
                    "id": p.id_plomero,
                    "nombre": f"{p.nombre} {p.apellido}",
                    "calificacion": p.puntuacion,
                    "localidad": p.localidad
                })
    
    nueva_solicitud.plomeros_sugeridos_detallados = detalles
    return nueva_solicitud