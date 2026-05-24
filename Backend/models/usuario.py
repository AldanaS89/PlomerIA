# models/usuario.py
from sqlalchemy import Column, Integer, String
from database import Base
from models.personaMixin import PersonaMixin

class Usuario(PersonaMixin, Base):
    __tablename__ = "usuarios"
    id_usuario = Column(Integer, primary_key=True, index=True)
    direccion  = Column(String)
    rol        = Column(String, default="cliente")
