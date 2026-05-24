# routers/plomeros.py
import json
import uuid
import cv2
import numpy as np
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from database import get_db
from schemas.plomero import (
    PlomeroResponse, PlomeroLoginRequest, PlomeroLoginResponse,
    OlvidePasswordPlomeroRequest, ResetPasswordPlomeroRequest,
)
from services import plomero_service
from core.auth import get_plomero_actual

router = APIRouter(tags=["Plomeros"])

# ── Directorio de fotos ───────────────────────────────────────────────────────
UPLOAD_DIR = Path("uploads/fotos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MIME_PERMITIDOS = {"image/jpeg", "image/png", "image/webp"}
EXT_PERMITIDAS  = {".jpg", ".jpeg", ".png", ".webp"}
MAX_BYTES       = 5 * 1024 * 1024  # 5 MB

def _guardar_foto(foto: UploadFile) -> str:
    """
    Valida tipo, extensión, tamaño, magic bytes y presencia de rostro. 
    Guarda el archivo y retorna la ruta para la base de datos.
    """

    # 1. Validar content-type
    if foto.content_type not in MIME_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de imagen no permitido: {foto.content_type}. Usá JPG, PNG o WEBP.",
        )

    # 2. Validar extensión
    sufijo = Path(foto.filename or "").suffix.lower()
    if sufijo not in EXT_PERMITIDAS:
        raise HTTPException(
            status_code=400,
            detail=f"Extensión '{sufijo}' no permitida. Usá .jpg, .png o .webp.",
        )

    # 3. Leer y validar tamaño
    contenido = foto.file.read()
    if len(contenido) > MAX_BYTES:
        raise HTTPException(status_code=400, detail="La imagen supera el límite de 5 MB.")

    # 4. Validar magic bytes (firma real del archivo)
    jpeg_ok = contenido[:3] == b'\xff\xd8\xff'
    png_ok  = contenido[:8] == b'\x89PNG\r\n\x1a\n'
    webp_ok = contenido[:4] == b'RIFF' and contenido[8:12] == b'WEBP'

    if not (jpeg_ok or png_ok or webp_ok):
        raise HTTPException(
            status_code=400,
            detail="El archivo no es una imagen válida. No se permiten archivos disfrazados.",
        )

    # ─── VALIDACIÓN DE SEGURIDAD: DETECCIÓN DE ROSTRO ───
    # Convertimos los bytes a una imagen que OpenCV pueda procesar
    nparr = np.frombuffer(contenido, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is not None:
        # Usamos el clasificador frontal de rostros de OpenCV
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detectamos rostros
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) == 0:
            raise HTTPException(
                status_code=400, 
                detail="No se detectó un rostro humano claro. Por seguridad, subí una foto de perfil real donde se vea tu cara."
            )
    # ───────────────────────────────────────────────────

    # 5. Guardar con nombre único
    nombre_archivo = f"{uuid.uuid4().hex}{sufijo}"
    ruta_fisica = UPLOAD_DIR / nombre_archivo
    
    # Escribimos el archivo en el disco
    with open(ruta_fisica, "wb") as f:
        f.write(contenido)

    # Retornamos la ruta con formato de URL para el frontend (uploads/fotos/...)
    return f"uploads/fotos/{nombre_archivo}"

# ── REGISTRO (multipart/form-data — acepta foto opcional) ────────────────────

@router.post("/registro")
async def registrar(
    nombre:              str            = Form(...),
    apellido:            str            = Form(...),
    email:               str            = Form(...),
    password:            str            = Form(...),
    telefono:            str            = Form(...),
    direccion:           str            = Form(...),
    localidad:           str            = Form(...),
    especialidades:      str            = Form(...),   # JSON: '["DESTAPES","OBRA"]'
    genero:              str            = Form("M"),
    atiende_urgencias:   bool           = Form(False),
    matricula_gas:       bool           = Form(False),
    agenda:              str            = Form("{}"),  # JSON: '{"Lun_manana":true}'
    otra_especialidad: Optional[str]  = Form(None),
    foto:                Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    # Parsear especialidades
    try:
        lista_esp = json.loads(especialidades)
    except Exception:
        lista_esp = [e.strip() for e in especialidades.split(",") if e.strip()]

    # Parsear agenda
    try:
        agenda_dict = json.loads(agenda)
        if not isinstance(agenda_dict, dict):
            agenda_dict = {}
    except Exception:
        agenda_dict = {}

    # Guardar foto si se envió
    foto_path = None
    if foto and foto.filename:
        foto_path = _guardar_foto(foto)

    return plomero_service.registrar_completo(
        db                  = db,
        nombre              = nombre,
        apellido            = apellido,
        email               = email,
        password            = password,
        telefono            = telefono,
        direccion           = direccion,
        localidad           = localidad,
        especialidades      = lista_esp,
        otra_especialidad = otra_especialidad,
        genero              = genero,
        atiende_urgencias   = atiende_urgencias,
        matricula_gas       = matricula_gas,
        agenda              = agenda_dict,
        foto_path           = foto_path,
    )


# ── LOGIN ─────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=PlomeroLoginResponse)
def login(datos: PlomeroLoginRequest, db: Session = Depends(get_db)):
    return plomero_service.login(db, datos)


# ── BUSCAR / SUGERIR ──────────────────────────────────────────────────────────

@router.get("/buscar", response_model=list[PlomeroResponse])
def buscar(
    localidad:         Optional[str]  = None,
    genero:            Optional[str]  = None,
    especialidad:      Optional[str]  = None,
    atiende_urgencias: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    return plomero_service.buscar(db, localidad, genero, especialidad, atiende_urgencias)


@router.post("/sugerir")
def sugerir(datos: dict, db: Session = Depends(get_db)):
    return plomero_service.sugerir(
        db               = db,
        descripcion      = datos.get("descripcion", ""),
        solo_mujeres     = datos.get("solo_mujeres", False),
        lat_usuario      = datos.get("latitud"),
        lon_usuario      = datos.get("longitud"),
        urgencia_forzada = datos.get("urgencia_forzada", False),
    )


# ── DISPONIBILIDAD ────────────────────────────────────────────────────────────

@router.patch("/disponibilidad")
def cambiar_disponibilidad(
    disponible: bool,
    db: Session = Depends(get_db),
    id_plomero: int = Depends(get_plomero_actual),
):
    return plomero_service.cambiar_disponibilidad(db, id_plomero, disponible)


# ── PERFIL ────────────────────────────────────────────────────────────────────

@router.get("/{id}", response_model=PlomeroResponse)
def obtener(id: int, db: Session = Depends(get_db)):
    return plomero_service.obtener_por_id(db, id)


# ── RECUPERACIÓN DE CONTRASEÑA ────────────────────────────────────────────────

@router.post("/olvide-password")
def olvide_password(datos: OlvidePasswordPlomeroRequest, db: Session = Depends(get_db)):
    return plomero_service.olvide_password(db, datos.email)


@router.post("/reset-password")
def reset_password(datos: ResetPasswordPlomeroRequest, db: Session = Depends(get_db)):
    return plomero_service.reset_password(db, datos.token, datos.nueva_password)