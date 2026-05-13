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
from utils.auth_plomeros import get_plomero_actual

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
    otra_especialidades: Optional[str]  = Form(None),
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
        otra_especialidades = otra_especialidades,
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
def sugerir(
    datos: dict,
    db: Session = Depends(get_db),
):
    from services import ia_service
    from repositories import plomero_repository
    from datetime import datetime

    descripcion      = datos.get("descripcion", "")
    solo_mujeres     = datos.get("solo_mujeres", False)
    lat_usuario      = datos.get("latitud",  None)
    lon_usuario      = datos.get("longitud", None)
    urgencia_forzada = datos.get("urgencia_forzada", False)

    diagnostico = ia_service.analizar_descripcion(descripcion)
    etiqueta    = diagnostico["etiqueta_ia"]
    urgencia_ia = diagnostico["urgencia_ia"]

    es_urgente = urgencia_forzada or (urgencia_ia == "URGENTE")
    genero_filtro = "F" if solo_mujeres else None

    # ── Franjas válidas para urgencias: hoy (lo que queda) + mañana ──────────
    DIAS_ES  = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    FRANJAS  = ["manana", "tarde", "noche"]
    FRANJA_INICIO = {"manana": 8, "tarde": 13, "noche": 18}

    ahora       = datetime.now()
    hora_actual = ahora.hour
    dia_hoy     = DIAS_ES[ahora.weekday()]
    dia_manana  = DIAS_ES[(ahora.weekday() + 1) % 7]

    # Franjas de hoy que todavía tienen más de 1 hora por delante
    franjas_hoy = [f for f in FRANJAS if FRANJA_INICIO[f] > hora_actual + 1]
    # Mañana: mañana y tarde (no noche para urgencias)
    franjas_manana = ["manana", "tarde"]

    keys_urgencia = (
        {f"{dia_hoy}_{f}" for f in franjas_hoy} |
        {f"{dia_manana}_{f}" for f in franjas_manana}
    )

    def tiene_slot_urgente(p) -> bool:
        if not p.agenda:
            return p.disponible_ahora
        return any(p.agenda.get(k) for k in keys_urgencia)

    # ── Query con radio progresivo para urgencias ─────────────────────────────
    if es_urgente:
        # Intentar con radios crecientes hasta tener 5 resultados
        RADIOS = [5, 10, 20, 50, None]  # None = sin límite de distancia
        plomeros = []
        for radio in RADIOS:
            candidatos = plomero_repository.filtrar(
                db,
                genero            = genero_filtro,
                atiende_urgencias = True,
                solo_disponibles  = True,
                lat_usuario       = lat_usuario if radio else None,
                lon_usuario       = lon_usuario if radio else None,
                radio_km          = radio,
            )
            candidatos = [p for p in candidatos if tiene_slot_urgente(p)]
            if len(candidatos) >= 5:
                plomeros = candidatos
                break
            plomeros = candidatos  # guardar los que hay aunque sean menos

        # Fallback final: cualquier disponible con slot urgente
        if len(plomeros) < 5:
            ids_ya = {p.id_plomero for p in plomeros}
            resto = plomero_repository.filtrar(
                db,
                genero           = genero_filtro,
                solo_disponibles = True,
            )
            for p in resto:
                if p.id_plomero not in ids_ya and tiene_slot_urgente(p):
                    plomeros.append(p)
                    ids_ya.add(p.id_plomero)
    else:
        plomeros = plomero_repository.filtrar(
            db,
            genero      = genero_filtro,
            lat_usuario = lat_usuario,
            lon_usuario = lon_usuario,
        )

    # ── Distancia ─────────────────────────────────────────────────────────────
    def _dist(p):
        if lat_usuario and lon_usuario and p.latitud and p.longitud:
            return plomero_repository._distancia_km(
                lat_usuario, lon_usuario, p.latitud, p.longitud
            )
        return 9999

    # ── Relevancia ────────────────────────────────────────────────────────────
    def _relevancia(p):
        score = 0
        if etiqueta and p.especialidades and etiqueta in p.especialidades:
            score += 3
        if es_urgente and p.atiende_urgencias and p.disponible_ahora:
            score += 5
        return score

    # ── Deduplicar ────────────────────────────────────────────────────────────
    vistos, unicos = set(), []
    for p in plomeros:
        if p.id_plomero not in vistos:
            vistos.add(p.id_plomero)
            unicos.append(p)

    resultado = sorted(
        unicos,
        key=lambda p: (-_relevancia(p), -p.puntuacion, _dist(p))
    )[:5]

    # Para urgencias: filtrar la agenda mostrando solo hoy y mañana
    def agenda_filtrada(p):
        if not es_urgente or not p.agenda:
            return p.agenda or {}
        return {k: True for k in keys_urgencia if p.agenda.get(k)}

    return [
        {
            "id_plomero":        p.id_plomero,
            "nombre":            p.nombre,
            "apellido":          p.apellido,
            "foto_perfil_path":  p.foto_perfil_path,
            "especialidad":      (p.especialidades or [etiqueta])[0],
            "especialidades":    p.especialidades or [],
            "localidad":         p.localidad,
            "puntuacion":        p.puntuacion,
            "total_trabajos":    p.total_trabajos,
            "atiende_urgencias": p.atiende_urgencias,
            "disponible_ahora":  p.disponible_ahora,
            "genero":            p.genero,
            "distancia_km":      round(_dist(p), 2) if _dist(p) < 9999 else None,
            "etiqueta_ia":       etiqueta,
            "urgencia_ia":       urgencia_ia,
            "agenda":            agenda_filtrada(p),
        }
        for p in resultado
    ]


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