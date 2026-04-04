from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.usuario import UsuarioResponse
from repositories import usuario_repository

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.get("/{id}", response_model=UsuarioResponse)
def obtener(id: int, db: Session = Depends(get_db)):
    usuario = usuario_repository.buscar_por_id(db, id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return UsuarioResponse.model_validate(usuario)