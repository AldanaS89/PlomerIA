from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from geopy.distance import geodesic
from services import solicitud_service
from utils.auth_plomeros import get_plomero_actual
from database import get_db
from models.solicitud import Solicitud, EstadoSolicitud
from models.plomero import Plomero
from schemas.solicitud import SolicitudCreate, SolicitudResponse

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes"])

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
    return [c["id"] for c in candidatos[:5]]
    
import json # Importamos json para manejar la lista de forma limpia

@router.post("/", response_model=SolicitudResponse)
async def crear_solicitud(data: SolicitudCreate, db: Session = Depends(get_db)):
    # 1. Obtenemos la lista de IDs (es una lista de Python: [1, 5, 10...])
    sugeridos_ids_lista = buscar_5_mejores(db, data.latitud_evento, data.longitud_evento, data.solo_mujeres)
    
    # 2. CONVERSIÓN CRÍTICA: Transformamos la lista [1, 2] en un string "1,2" 
    # Esto es lo que guardaremos en la base de datos para que SQLite no de error.
    sugeridos_string = ",".join(map(str, sugeridos_ids_lista))

    nueva_solicitud = Solicitud(
        id_usuario=1,  # ID para la demo
        descripcion_raw=data.descripcion_raw,
        localidad_evento=data.localidad_evento,
        latitud_evento=data.latitud_evento,
        longitud_evento=data.longitud_evento,
        ids_plomeros_sugeridos=sugeridos_string, # <--- Pasamos el STRING, no la lista
        estado=EstadoSolicitud.PENDIENTE
    )
    
    db.add(nueva_solicitud)
    db.commit()
    db.refresh(nueva_solicitud)

    # 3. Transformamos para la respuesta del Front
    detalles = []
    # Usamos la lista original que ya teníamos para no tener que hacer split de nuevo
    if sugeridos_ids_lista:
        for p_id in sugeridos_ids_lista:
            p = db.query(Plomero).filter(Plomero.id_plomero == p_id).first()
            if p:
                detalles.append({
                    "id": p.id_plomero,
                    "nombre": f"{p.nombre} {p.apellido}",
                    "calificacion": p.puntuacion if p.puntuacion else 0.0,
                    "localidad": p.localidad
                })
    
    # Inyectamos los detalles en el objeto para que el response_model los vea
    nueva_solicitud.plomeros_sugeridos_detallados = detalles
    
    return nueva_solicitud

@router.get("/plomero/me")
def mis_solicitudes(
    db: Session = Depends(get_db),
    id_plomero: int = Depends(get_plomero_actual)
):
    return solicitud_service.por_plomero(db, id_plomero)

@router.get("/buscar")
def buscar(q: str, db: Session = Depends(get_db)):
    return solicitud_service.buscar_por_texto(db, q)

#Ver si va -----------@router.patch("/{id_solicitud}/responder")
# En tu router de solicitudes
@router.patch("/{id_solicitud}/responder")
def responder_solicitud(
    id_solicitud: int, 
    accion: str, # "aceptar" o "rechazar"
    db: Session = Depends(get_db),
    id_plomero: int = Depends(get_plomero_actual)
):
    solicitud = db.query(Solicitud).filter(Solicitud.id_solicitud == id_solicitud).first()
    
    if not solicitud:
        raise HTTPException(status_code=404, detail="La solicitud ya no existe.")

    # Si alguien más ya la aceptó
    if solicitud.estado == EstadoSolicitud.ACEPTADO and accion == "aceptar":
        raise HTTPException(status_code=400, detail="Lo sentimos, otro plomero ya tomó este trabajo.")

    if accion == "aceptar":
        solicitud.estado = EstadoSolicitud.ACEPTADO
        solicitud.id_plomero = id_plomero  # Asignamos al plomero que clickeó
        mensaje = "¡Trabajo asignado correctamente!"
    
    elif accion == "rechazar":
        # Lógica opcional: podrías quitar el ID de este plomero de ids_plomeros_sugeridos
        # o simplemente marcar que para este plomero ya no es visible (requeriría tabla intermedia)
        mensaje = "Solicitud rechazada."

    db.commit()
    return {"status": "ok", "mensaje": mensaje}