# repositories/usuario_repository.py
from sqlalchemy.orm import Session
from models.usuario import Usuario

def buscar_por_email(db: Session, email: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.email == email).first()

def buscar_por_id(db: Session, id: int) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.id_usuario == id).first()

def crear_usuario(db: Session, usuario: Usuario) -> Usuario:
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario