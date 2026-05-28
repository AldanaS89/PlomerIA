# services/foto_service.py
"""
Responsabilidad única: validar y persistir imágenes de perfil.
"""
import uuid
import os
import numpy as np
import cv2
from pathlib import Path
from fastapi import HTTPException, UploadFile

UPLOAD_DIR      = Path("uploads/fotos")
MIME_PERMITIDOS = {"image/jpeg", "image/png", "image/webp"}
EXT_PERMITIDAS  = {".jpg", ".jpeg", ".png", ".webp"}
MAX_BYTES       = 5 * 1024 * 1024

# Ruta al clasificador — copiado a Backend/ para evitar bug de OpenCV con
# rutas que contienen caracteres especiales (°, Ñ) en Windows
RUTA_CLASIFICADOR = r"C:\temp\haarcascade.xml"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class FotoService:
    """
    Patrón Strategy implícito: si en el futuro queremos guardar
    en S3 en lugar de disco, solo cambiamos esta clase.
    """

    async def guardar(self, foto: UploadFile) -> str:
        """Valida, verifica rostro y guarda la foto. Devuelve la ruta para la BD."""
        contenido = await self._validar(foto)
        self._validar_rostro(contenido)
        return self._persistir(contenido, foto.filename)

    async def solo_validar(self, foto: UploadFile) -> None:
        """
        Solo verifica formato y rostro — no guarda nada.
        Usado por el endpoint /validar-foto para feedback
        inmediato en el paso 1 del registro.
        """
        contenido = await self._validar(foto)
        self._validar_rostro(contenido)

    async def _validar(self, foto: UploadFile) -> bytes:
        if foto.content_type not in MIME_PERMITIDOS:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo no permitido: {foto.content_type}. Usá JPG, PNG o WEBP."
            )
        sufijo = Path(foto.filename or "").suffix.lower()
        if sufijo not in EXT_PERMITIDAS:
            raise HTTPException(
                status_code=400,
                detail=f"Extensión '{sufijo}' no permitida."
            )
        contenido = await foto.read()
        if len(contenido) > MAX_BYTES:
            raise HTTPException(status_code=400, detail="La imagen supera 5 MB.")
        if not self._magic_bytes_ok(contenido):
            raise HTTPException(
                status_code=400,
                detail="El archivo no es una imagen válida."
            )
        return contenido

    def _magic_bytes_ok(self, contenido: bytes) -> bool:
        jpeg = contenido[:3]  == b'\xff\xd8\xff'
        png  = contenido[:8]  == b'\x89PNG\r\n\x1a\n'
        webp = contenido[:4]  == b'RIFF' and contenido[8:12] == b'WEBP'
        return jpeg or png or webp

    def _validar_rostro(self, contenido: bytes) -> None:
        nparr = np.frombuffer(contenido, np.uint8)
        img   = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return

        cascade = cv2.CascadeClassifier(RUTA_CLASIFICADOR)

        if cascade.empty():
            print(f"[foto_service] Clasificador no encontrado en: {RUTA_CLASIFICADOR}")
            raise HTTPException(
                status_code=500,
                detail="Error interno: clasificador de rostros no disponible."
            )

        gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=8,
            minSize=(60, 60)
        )
        if len(faces) == 0:
            raise HTTPException(
                status_code=400,
                detail="No se detectó un rostro. Subí una foto de perfil donde se vea tu cara."
            )

    def _persistir(self, contenido: bytes, filename: str) -> str:
        sufijo  = Path(filename or "").suffix.lower()
        nombre  = f"{uuid.uuid4().hex}{sufijo}"
        ruta    = UPLOAD_DIR / nombre
        ruta.write_bytes(contenido)
        return f"uploads/fotos/{nombre}"


# Instancia con nombre distinto al módulo para evitar conflicto de imports
servicio_foto = FotoService()