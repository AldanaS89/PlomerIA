import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import json
from database import SessionLocal
from models.plomero import Plomero
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()

def hash_password(password: str):
    return pwd_context.hash(password[:72])

def separar_nombre(nombre_completo: str):
    partes = nombre_completo.split(" ")
    nombre = " ".join(partes[:-1])
    apellido = partes[-1]
    return nombre, apellido


with open("scripts/plomeros.json", encoding="utf-8") as f:
    datos = json.load(f)

for item in datos:

    nombre, apellido = separar_nombre(item["nombre"])

    nuevo = Plomero(
        nombre=nombre,
        apellido=apellido,
        especialidad=item["especialidad"],
        localidad=item["localidad"],
        genero=item.get("genero", "No especificado"),
        atiende_urgencias=item.get("atiende_urgencias", False),

        # mapping de nombres distintos
        puntuacion=item.get("calificacion", 0.0),

        # datos fake necesarios
        email=f"{nombre.replace(' ','').lower()}@fake.com",
        telefono="0000000000",
        password_hash=hash_password("1234"),
    )

    db.add(nuevo)

db.commit()
db.close()

print("✅ Plomeros cargados correctamente")