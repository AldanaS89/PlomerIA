from sqlalchemy.orm import Session

def guardar_reset_token(db: Session, modelo, id_campo: str, id_valor: int, token: str):
    entidad = (
        db.query(modelo)
        .filter(getattr(modelo, id_campo) == id_valor)
        .first()
    )

    if not entidad:
        return None

    entidad.reset_token = token

    db.commit()

    return entidad


def buscar_por_reset_token(db: Session, modelo, token: str):
    return (
        db.query(modelo)
        .filter(modelo.reset_token == token)
        .first()
    )


def actualizar_password(
    db: Session,
    modelo,
    id_campo: str,
    id_valor: int,
    nuevo_hash: str
):
    entidad = (
        db.query(modelo)
        .filter(getattr(modelo, id_campo) == id_valor)
        .first()
    )

    if not entidad:
        return None

    entidad.password_hash = nuevo_hash
    entidad.reset_token = None

    db.commit()
    db.refresh(entidad)

    return entidad

