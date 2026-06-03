from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    comandos = [
        # ── Migraciones originales ─────────────────────────────────────────────
        "ALTER TABLE solicitudes ADD COLUMN turno_solicitado VARCHAR",
        "ALTER TABLE plomeros ADD COLUMN cancelaciones_consecutivas INTEGER DEFAULT 0",
        "ALTER TABLE plomeros ADD COLUMN suspendido INTEGER DEFAULT 0",
        "ALTER TABLE usuarios ADD COLUMN cancelaciones_consecutivas INTEGER DEFAULT 0",
        "ALTER TABLE usuarios ADD COLUMN suspendido INTEGER DEFAULT 0",

        # ── Columnas de tracking de plomeros en solicitudes ───────────────────
        # Estas son las que causan el error actual
        "ALTER TABLE solicitudes ADD COLUMN ids_plomeros_contactados VARCHAR",
        "ALTER TABLE solicitudes ADD COLUMN ids_plomeros_activos VARCHAR",
        "ALTER TABLE solicitudes ADD COLUMN ids_plomeros_sugeridos VARCHAR",

        # ── Columnas de turno y fecha de trabajo ──────────────────────────────
        "ALTER TABLE solicitudes ADD COLUMN fecha_trabajo DATETIME",
        "ALTER TABLE solicitudes ADD COLUMN fecha_ultimo_envio DATETIME",
        "ALTER TABLE solicitudes ADD COLUMN intentos_reasignacion INTEGER DEFAULT 0",

        # ── Calificación bidireccional ─────────────────────────────────────────
        "ALTER TABLE calificaciones ADD COLUMN autor_rol VARCHAR DEFAULT 'cliente'",

        # ── Puntuación del cliente ─────────────────────────────────────────────
        "ALTER TABLE usuarios ADD COLUMN puntuacion REAL DEFAULT 5.0",
        "ALTER TABLE usuarios ADD COLUMN total_trabajos INTEGER DEFAULT 0",
    ]

    for cmd in comandos:
        try:
            conn.execute(text(cmd))
            print(f"OK: {cmd}")
        except Exception as e:
            print(f"Ya existe (ignorado): {e}")

    conn.commit()
    print("\nMigracion completada")