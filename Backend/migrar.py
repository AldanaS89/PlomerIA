from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    comandos = [
        "ALTER TABLE solicitudes ADD COLUMN turno_solicitado VARCHAR",
        "ALTER TABLE plomeros ADD COLUMN cancelaciones_consecutivas INTEGER DEFAULT 0",
        "ALTER TABLE plomeros ADD COLUMN suspendido INTEGER DEFAULT 0",
        "ALTER TABLE usuarios ADD COLUMN cancelaciones_consecutivas INTEGER DEFAULT 0",
        "ALTER TABLE usuarios ADD COLUMN suspendido INTEGER DEFAULT 0",
    ]
    for cmd in comandos:
        try:
            conn.execute(text(cmd))
            print(f"OK: {cmd}")
        except Exception as e:
            print(f"Ya existe: {e}")
    conn.commit()
    print("Listo")