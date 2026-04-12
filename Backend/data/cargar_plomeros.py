# data/cargar_plomeros.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import json
from database import SessionLocal, engine, Base
from models.plomero import Plomero
from passlib.context import CryptContext

Base.metadata.create_all(bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Mapeo de especialidades del JSON al formato del sistema
ESPECIALIDAD_MAP = {
    # DESTAPES
    "destapaciones":                      "DESTAPES",
    "destapaciones y emergencias":        "DESTAPES",
    "desagües y cloacas":                 "DESTAPES",
    "desagües cloacales y pluviales":     "DESTAPES",
    "desagües y cloacas industriales":    "DESTAPES",
    "limpieza de pozos ciegos":           "DESTAPES",
    "limpieza de canaletas":              "DESTAPES",
    "limpieza de canaletas y techos":     "DESTAPES",

    # GAS_MATRICULADO
    "gasista matriculada":                "GAS_MATRICULADO",
    "gasista matriculado":                "GAS_MATRICULADO",
    "gasista de obra":                    "GAS_MATRICULADO",
    "gasista de obra nueva":              "GAS_MATRICULADO",
    "detección de fugas de gas":          "GAS_MATRICULADO",
    "estufas y calefones":                "GAS_MATRICULADO",
    "calderas y calefacción":             "GAS_MATRICULADO",
    "calderas y calefacción central":     "GAS_MATRICULADO",
    "reparación de calderas":             "GAS_MATRICULADO",
    "reparación de calentadores":         "GAS_MATRICULADO",
    "instalación de termotanques":        "GAS_MATRICULADO",
    "instalación de termotanques eléctricos": "GAS_MATRICULADO",
    "instalación de termotanques a gas":  "GAS_MATRICULADO",

    # OBRA
    "obra y reparaciones":                "OBRA",
    "obra civil":                         "OBRA",
    "instalaciones de obra":              "OBRA",
    "instalaciones sanitarias":           "OBRA",
    "impermeabilización de tanques":      "OBRA",
    "humedad de cimientos":               "OBRA",
    "mantenimiento de redes de incendio": "OBRA",
    "mantenimiento de redes contra incendio": "OBRA",
    "termofusión y cañerías":             "OBRA",
    "termofusión en exterior":            "OBRA",
    "termofusión en interior":            "OBRA",
    "termofusión y redes de agua":        "OBRA",
    "termofusión de grandes diámetros":   "OBRA",
    "soldadura de hidrobronz":            "OBRA",
    "soldadura de cañerías de bronce":    "OBRA",
    "soldadura de cañerías de hidrobronz": "OBRA",
    "soldadura de caños de plomo":        "OBRA",
    "soldaduras de cobre":                "OBRA",
    "restauración de cañerías antiguas":  "OBRA",
    "columnas de agua":                   "OBRA",
    "reparación de columnas":             "OBRA",
    "reparación de columnas de agua":     "OBRA",
    "reparación de colectores":           "OBRA",
    "reparación de colectores de agua":   "OBRA",
    "reparación de colectores de red":    "OBRA",
    "reparación de tanques de agua":      "OBRA",
    "plomería para reformas":             "OBRA",
    "plomería integral":                  "PLOMERIA_GENERAL",

    # PLOMERIA_GENERAL
    "plomería general":                   "PLOMERIA_GENERAL",
    "plomeria general":                   "PLOMERIA_GENERAL",
    "grifería y sanitarios":              "PLOMERIA_GENERAL",
    "grifería fina":                      "PLOMERIA_GENERAL",
    "grifería de cocina":                 "PLOMERIA_GENERAL",
    "grifería de cocina y monocomandos":  "PLOMERIA_GENERAL",
    "grifería y mezcladoras de ducha":    "PLOMERIA_GENERAL",
    "grifería de alta gama y sanitarios": "PLOMERIA_GENERAL",
    "grifería y accesorios de cocina":    "PLOMERIA_GENERAL",
    "instalación de grifería monocomando":"PLOMERIA_GENERAL",
    "válvulas de inodoro":                "PLOMERIA_GENERAL",
    "reparación de válvulas de inodoro":  "PLOMERIA_GENERAL",
    "reparación de válvulas de retención":"PLOMERIA_GENERAL",
    "reparación de válvulas de seguridad":"PLOMERIA_GENERAL",
    "instalación de sanitarios":          "PLOMERIA_GENERAL",
    "sanitarios y vanitorys":             "PLOMERIA_GENERAL",
    "accesorios de baño y grifería":      "PLOMERIA_GENERAL",
    "instalación de bombas":              "PLOMERIA_GENERAL",
    "instalación de bombas de achique":   "PLOMERIA_GENERAL",
    "instalación de bombas presurizadoras":"PLOMERIA_GENERAL",
    "instalación de bombas elevadoras":   "PLOMERIA_GENERAL",
    "mantenimiento de bombas":            "PLOMERIA_GENERAL",
    "tanques y bombas de achique":        "PLOMERIA_GENERAL",
    "detección de filtraciones":          "PLOMERIA_GENERAL",
    "detección de filtraciones con cámara":"PLOMERIA_GENERAL",
    "filtros y purificadores":            "PLOMERIA_GENERAL",
    "filtros y purificadores de agua":    "PLOMERIA_GENERAL",
    "filtros de agua y purificadores":    "PLOMERIA_GENERAL",
    "sistemas de riego":                  "PLOMERIA_GENERAL",
    "sistemas de riego automatizado":     "PLOMERIA_GENERAL",
    "instalación de lavavajillas":        "PLOMERIA_GENERAL",
    "instalación de lavarropas":          "PLOMERIA_GENERAL",
    "mantenimiento de jacuzzis":          "PLOMERIA_GENERAL",
    "aire comprimido":                    "PLOMERIA_GENERAL",
    "reparación de mezcladoras":          "PLOMERIA_GENERAL",
}

def mapear_especialidad(especialidad_raw: str) -> str:
    key = especialidad_raw.lower().strip()
    # Buscar coincidencia exacta
    if key in ESPECIALIDAD_MAP:
        return ESPECIALIDAD_MAP[key]
    # Buscar coincidencia parcial
    for k, v in ESPECIALIDAD_MAP.items():
        if k in key or key in k:
            return v
    # Si no encuentra nada, asignar PLOMERIA_GENERAL por defecto
    print(f"  ⚠️  Especialidad no mapeada: '{especialidad_raw}' → PLOMERIA_GENERAL")
    return "PLOMERIA_GENERAL"

def mapear_genero(genero_raw: str) -> str:
    if genero_raw.lower() in ["femenino", "f", "mujer"]:
        return "F"
    return "M"

def cargar():
    # Ruta al JSON — ajustá si está en otro lugar
    json_path = os.path.join(os.path.dirname(__file__), "plomeros.json")

    with open(json_path, "r", encoding="utf-8") as f:
        plomeros_json = json.load(f)

    db = SessionLocal()
    cargados  = 0
    omitidos  = 0

    for p in plomeros_json:
        # Generar email ficticio único basado en el ID
        email_ficticio = f"plomero{p['id']}@plomeria.com"

        # Verificar que no exista ya
        existe = db.query(Plomero).filter(Plomero.email == email_ficticio).first()
        if existe:
            omitidos += 1
            continue

        # Separar nombre y apellido (el JSON tiene nombre completo)
        partes   = p["nombre"].strip().split(" ")
        apellido = partes[-1]                        # última palabra = apellido
        nombre   = " ".join(partes[:-1]) if len(partes) > 1 else partes[0]

        nuevo = Plomero(
            nombre            = nombre,
            apellido          = apellido,
            email             = email_ficticio,
            telefono          = f"11{p['id']:08d}",  # teléfono ficticio
            especialidad      = mapear_especialidad(p["especialidad"]),
            genero            = mapear_genero(p["genero"]),
            localidad         = p["localidad"],
            latitud           = p.get("latitud"),
            longitud          = p.get("longitud"),
            atiende_urgencias = p.get("atiende_urgencias", False),
            disponible_ahora  = True,
            puntuacion        = p.get("calificacion", 0.0),
            total_trabajos    = 0,
            matricula_gas     = mapear_especialidad(p["especialidad"]) == "GAS_MATRICULADO",
            password_hash     = pwd_context.hash("plomero1234"),
        )
        db.add(nuevo)
        cargados += 1

    db.commit()
    db.close()

    print(f"\n✅ Cargados:  {cargados} plomeros")
    print(f"⏭️  Omitidos:  {omitidos} (ya existían)")
    print(f"📋 Total JSON: {len(plomeros_json)}")
    print("\nTodos los plomeros tienen password: plomero1234")

if __name__ == "__main__":
    cargar()