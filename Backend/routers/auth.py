from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# --- IMPORTACIONES  DE MODELOS ---
from database import get_db 
from models.usuario import Usuario 
from schemas.auth import RegistroRequest, LoginRequest, LoginResponse
from utils.seguridad import hashear_password, verificar_password, crear_token_acceso

router = APIRouter(prefix="", tags=["auth"])

# Configuramos GeoPy para automatizar la ubicación en Zona Sur
geolocator = Nominatim(user_agent="plomeria_unab_app")

def obtener_coordenadas(direccion, localidad):
    """Convierte dirección en latitud/longitud para el mapa"""
    try:
        consulta = f"{direccion}, {localidad}, Buenos Aires, Argentina"
        location = geolocator.geocode(consulta)
        if location:
            return location.latitude, location.longitude
        return None, None
    except (GeocoderTimedOut, Exception):
        return None, None

@router.post("/registro", status_code=status.HTTP_201_CREATED)
async def registro_cliente(data: RegistroRequest, db: Session = Depends(get_db)):
    # 1. Verificar duplicados
    existe = db.query(Usuario).filter(Usuario.email == data.email).first()
    if existe:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    # 2. Lógica GeoPy para Longchamps y alrededores
    lat, lon = data.latitud, data.longitud
    if lat is None or lon is None:
        lat_geo, lon_geo = obtener_coordenadas(data.direccion, data.localidad)
        if lat_geo and lon_geo:
            lat, lon = lat_geo, lon_geo
        else:
            # Valores por defecto si falla la búsqueda
            lat = lat or -34.85
            lon = lon or -58.38

    # 3. Crear usuario con password segura
    nuevo_usuario = Usuario(
        nombre=data.nombre,
        apellido=data.apellido,
        email=data.email,
        password_hash=hashear_password(data.password),
        telefono=data.telefono,
        localidad=data.localidad,
        direccion=data.direccion,
        latitud=lat,
        longitud=lon
    )

    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return {"message": "Usuario creado con éxito", "id": nuevo_usuario.id_usuario}

@router.post("/login", response_model=LoginResponse)
async def login_cliente(data: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == data.email).first()
    
    # 4. VALIDACIÓN DE PASSWORD REAL
    if not usuario or not verificar_password(data.password, usuario.password_hash): # ← Cambiado a password_hash
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciales incorrectas"
        )

    # 5. TOKEN CON 'TIPO'
    # Vital para que auth_plomeros.py no te tire error 403
    token = crear_token_acceso({
        "sub": str(usuario.id_usuario),
        "tipo": "usuario" 
    })
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre
    }