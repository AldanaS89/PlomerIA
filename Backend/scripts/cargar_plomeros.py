"""
cargar_plomeros.py
==================
Importa los 100 plomeros de plomeros_enriquecido.json a la base de datos.

Uso (desde la carpeta Backend/):
    python scripts\cargar_plomeros.py

Podés correrlo varias veces — si el email ya existe, lo saltea.
"""

import sys
import os
import json
from pathlib import Path

# ─── Path portable: funciona en cualquier PC ─────────────────────────────────
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

# ─── Imports del proyecto ────────────────────────────────────────────────────
from utils.seguridad import hash_password
from database import SessionLocal, engine, Base
from models.plomero import Plomero

# ─── Crear tablas si no existen ──────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ─── Cargar JSON ─────────────────────────────────────────────────────────────
json_path = Path(__file__).resolve().parent / "plomeros_enriquecido.json"

if not json_path.exists():
    print(f"❌ No se encontró el archivo: {json_path}")
    print("   Asegurate de que plomeros_enriquecido.json esté en Backend/scripts/")
    sys.exit(1)

with open(json_path, encoding="utf-8") as f:
    plomeros_data = json.load(f)

print(f"📋 {len(plomeros_data)} plomeros encontrados en el JSON\n")

# ─── Cargar en la base de datos ──────────────────────────────────────────────
db = SessionLocal()

cargados = 0
saltados = 0
errores  = 0

try:
    for datos in plomeros_data:

        existe = db.query(Plomero).filter(Plomero.email == datos["email"]).first()
        if existe:
            saltados += 1
            continue

        try:
            plomero = Plomero(
                nombre            = datos["nombre"],
                apellido          = datos["apellido"],
                email             = datos["email"],
                password_hash     = hash_password(datos["password"]),
                # telefono eliminado — reemplazado por mensajería interna
                localidad         = datos["localidad"],
                latitud           = datos.get("latitud"),
                longitud          = datos.get("longitud"),
                especialidades    = datos["especialidades"],
                genero            = datos["genero"],
                atiende_urgencias = datos["atiende_urgencias"],
                matricula_gas     = datos.get("matricula_gas", False),
                puntuacion        = datos["puntuacion"],
                total_trabajos    = datos["total_trabajos"],
                disponible_ahora  = datos["disponible_ahora"],
                agenda            = datos.get("agenda", {}),
                foto_perfil_path  = datos.get("foto_perfil_path"),
            )

            db.add(plomero)
            cargados += 1
            print(f"  ✓ {datos['nombre']} {datos['apellido']} — {datos['localidad']}")

        except Exception as e:
            errores += 1
            print(f"  ✗ Error con {datos.get('email', '?')}: {e}")

    db.commit()

except Exception as e:
    db.rollback()
    print("❌ Error general:", e)

finally:
    db.close()

print(f"\n{'─' * 50}")
print(f"  Cargados : {cargados}")
print(f"  Saltados : {saltados}  (ya existían en la BD)")
print(f"  Errores  : {errores}")
print(f"{'─' * 50}")