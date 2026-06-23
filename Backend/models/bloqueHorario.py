from database import Base

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String


class BloqueHorario(Base):
    __tablename__ = "bloques_horarios"
    id         = Column(Integer, primary_key=True, index=True)
    id_plomero = Column(Integer, ForeignKey("plomeros.id_plomero"), nullable=False)
    inicio     = Column(DateTime, nullable=False)
    fin        = Column(DateTime, nullable=False)
    ocupado    = Column(Boolean, default=False)
    descripcion= Column(String, nullable=True)

