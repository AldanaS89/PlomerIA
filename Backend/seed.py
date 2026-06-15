# Backend/seed.py
import json
import os
from database import SessionLocal
from models.plomero import Plomero
# IMPORTANTE: Importamos la herramienta de seguridad
from services.auth_service import hashear_password

def cargar_desde_json():
    db = SessionLocal()
    try:
        directorio_actual = os.path.dirname(__file__)
        ruta_json = os.path.join(directorio_actual, 'data', 'plomeros.json')

        with open(ruta_json, 'r', encoding='utf-8') as f:
            datos_json = json.load(f)

        db.query(Plomero).delete()
        db.commit()
        
        plomeros_nuevos = []
        for p in datos_json:
            nuevo = Plomero(
                id_plomero=p['id'],
                nombre=p['nombre'],
                apellido="", 
                email=f"plomero{p['id']}@test.com",
                # --- CAMBIO CLAVE ---
                # Hasheamos la contraseña 'plomero1234' para que el login la acepte
                password_hash=hashear_password("plomero1234"), 
                localidad=p['localidad'],
                latitud=p['latitud'],
                longitud=p['longitud'],
                genero='F' if p['genero'] == 'Femenino' else 'M',
                puntuacion=float(p['calificacion']),
                disponible_ahora=True
            )
            plomeros_nuevos.append(nuevo)
        
        db.add_all(plomeros_nuevos)
        db.commit()
        print(f"¡Éxito! Se cargaron 100 plomeros con contraseñas seguras.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    cargar_desde_json()