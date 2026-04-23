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

def listar_todos(db: Session) -> list[Usuario]:
    return db.query(Usuario).all()

def guardar_reset_token(db: Session, id_usuario: int, token: str) -> None:
    usuario = buscar_por_id(db, id_usuario)
    usuario.reset_token = token
    db.commit()

def buscar_por_reset_token(db: Session, token: str):
    return db.query(Usuario).filter(Usuario.reset_token == token).first()

def actualizar_password(db: Session, id_usuario: int, nuevo_hash: str) -> None:
    usuario = buscar_por_id(db, id_usuario)
    usuario.password_hash = nuevo_hash
    usuario.reset_token   = None  # invalida el token después de usarlo
    db.commit()