from sqlalchemy.orm import Session

from models.usuario import Usuario


def buscar_por_email(
    db: Session,
    email: str
) -> Usuario | None:

    return (
        db.query(Usuario)
        .filter(Usuario.email == email)
        .first()
    )


def buscar_por_id(
    db: Session,
    id_usuario: int
) -> Usuario | None:

    return (
        db.query(Usuario)
        .filter(Usuario.id_usuario == id_usuario)
        .first()
    )


def crear_usuario(
    db: Session,
    usuario: Usuario
) -> Usuario:

    db.add(usuario)

    db.commit()

    db.refresh(usuario)

    return usuario


def listar_todos(
    db: Session
) -> list[Usuario]:

    return db.query(Usuario).all()

def guardar_reset_token(db, user_id, token):
    user = db.query(Usuario).get(user_id)
    user.reset_token = token
    db.commit()


def buscar_por_reset_token(db, token):
    return db.query(Usuario).filter(Usuario.reset_token == token).first()


def actualizar_password(db, user_id, new_hash):
    user = db.query(Usuario).get(user_id)
    user.password_hash = new_hash
    db.commit()


def limpiar_reset_token(db, user_id):
    user = db.query(Usuario).get(user_id)
    user.reset_token = None
    db.commit()