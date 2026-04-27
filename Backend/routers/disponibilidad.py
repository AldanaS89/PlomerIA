# routers/disponibilidad.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from database import get_db, Base
from utils.auth_plomeros import get_plomero_actual
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(tags=["Disponibilidad"])


class BloqueHorario(Base):
    __tablename__ = "bloques_horarios"
    id         = Column(Integer, primary_key=True, index=True)
    id_plomero = Column(Integer, ForeignKey("plomeros.id_plomero"), nullable=False)
    inicio     = Column(DateTime, nullable=False)
    fin        = Column(DateTime, nullable=False)
    ocupado    = Column(Boolean, default=False)
    descripcion= Column(String, nullable=True)


class BloqueOut(BaseModel):
    id: int
    inicio: datetime
    fin: datetime
    ocupado: bool
    descripcion: Optional[str] = None
    class Config:
        from_attributes = True


class BloquearRequest(BaseModel):
    inicio: datetime
    fin: datetime
    descripcion: Optional[str] = None


def _generar_slots_demo(id_plomero: int) -> list:
    slots = []
    base = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    idx = 0
    for dia in range(1, 8):
        fecha = base + timedelta(days=dia)
        if fecha.weekday() >= 5:
            continue
        for hora_ini, hora_fin in [(9, 11), (11, 13), (14, 16), (16, 18)]:
            inicio = fecha.replace(hour=hora_ini)
            fin    = fecha.replace(hour=hora_fin)
            idx += 1
            slots.append(BloqueOut(id=-(id_plomero * 100 + idx), inicio=inicio, fin=fin, ocupado=False))
    return slots


@router.get("/{id_plomero}", response_model=list[BloqueOut])
def ver_disponibilidad(id_plomero: int, db: Session = Depends(get_db)):
    ahora  = datetime.now()
    limite = ahora + timedelta(days=7)
    bloques = (
        db.query(BloqueHorario)
        .filter(
            BloqueHorario.id_plomero == id_plomero,
            BloqueHorario.ocupado == False,
            BloqueHorario.inicio >= ahora,
            BloqueHorario.inicio <= limite,
        )
        .order_by(BloqueHorario.inicio)
        .all()
    )
    return bloques if bloques else _generar_slots_demo(id_plomero)


@router.post("/{id_plomero}/bloquear", response_model=BloqueOut)
def bloquear_horario(
    id_plomero: int,
    datos: BloquearRequest,
    db: Session = Depends(get_db),
    id_plomero_auth: int = Depends(get_plomero_actual),
):
    if id_plomero != id_plomero_auth:
        raise HTTPException(status_code=403, detail="No podés modificar la agenda de otro plomero")
    bloque = BloqueHorario(id_plomero=id_plomero, inicio=datos.inicio, fin=datos.fin, ocupado=True, descripcion=datos.descripcion)
    db.add(bloque)
    db.commit()
    db.refresh(bloque)
    return bloque


@router.delete("/{id_plomero}/{id_bloque}")
def liberar_horario(
    id_plomero: int,
    id_bloque: int,
    db: Session = Depends(get_db),
    id_plomero_auth: int = Depends(get_plomero_actual),
):
    if id_plomero != id_plomero_auth:
        raise HTTPException(status_code=403, detail="No podés modificar la agenda de otro plomero")
    bloque = db.query(BloqueHorario).filter(BloqueHorario.id == id_bloque, BloqueHorario.id_plomero == id_plomero).first()
    if not bloque:
        raise HTTPException(status_code=404, detail="Bloque no encontrado")
    db.delete(bloque)
    db.commit()
    return {"mensaje": "Bloque eliminado"}