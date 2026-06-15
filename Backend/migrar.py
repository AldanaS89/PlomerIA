# migrar.py
# Ejecutar UNA SOLA VEZ desde la carpeta Backend:
#   python migrar.py
# Cada comando usa try/except — si ya existe lo ignora sin romper nada.

from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    comandos = [
        # ── Tabla de invitaciones (many-to-many solicitud ↔ plomero) ──────────
        """
        CREATE TABLE solicitud_plomero (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            id_solicitud INTEGER NOT NULL REFERENCES solicitudes(id_solicitud),
            id_plomero   INTEGER NOT NULL REFERENCES plomeros(id_plomero),
            estado       VARCHAR NOT NULL DEFAULT 'contactado',
            fecha        DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(id_solicitud, id_plomero)
        )
        """,

        # ── Columnas nuevas en solicitudes ────────────────────────────────────
        "ALTER TABLE solicitudes ADD COLUMN turno_solicitado VARCHAR",
        "ALTER TABLE solicitudes ADD COLUMN fecha_trabajo DATETIME",
        "ALTER TABLE solicitudes ADD COLUMN fecha_ultimo_envio DATETIME",
        "ALTER TABLE solicitudes ADD COLUMN intentos_reasignacion INTEGER DEFAULT 0",
        "ALTER TABLE solicitudes ADD COLUMN aviso_cierre_enviado INTEGER DEFAULT 0",

        # Plazo para calificar — se llena cuando el plomero marca TERMINADO
        "ALTER TABLE solicitudes ADD COLUMN fecha_vencimiento_calificacion DATETIME",

        # ── Columnas en plomeros ───────────────────────────────────────────────
        "ALTER TABLE plomeros ADD COLUMN cancelaciones_consecutivas INTEGER DEFAULT 0",
        "ALTER TABLE plomeros ADD COLUMN suspendido INTEGER DEFAULT 0",
        "ALTER TABLE plomeros ADD COLUMN suspendido_hasta DATETIME",
        "ALTER TABLE plomeros ADD COLUMN mensajes_ofensivos INTEGER DEFAULT 0",

        # ── Columnas en usuarios ───────────────────────────────────────────────
        "ALTER TABLE usuarios ADD COLUMN cancelaciones_consecutivas INTEGER DEFAULT 0",
        "ALTER TABLE usuarios ADD COLUMN suspendido INTEGER DEFAULT 0",
        "ALTER TABLE usuarios ADD COLUMN suspendido_hasta DATETIME",
        "ALTER TABLE usuarios ADD COLUMN mensajes_ofensivos INTEGER DEFAULT 0",
        "ALTER TABLE usuarios ADD COLUMN puntuacion REAL DEFAULT 5.0",
        "ALTER TABLE usuarios ADD COLUMN total_trabajos INTEGER DEFAULT 0",

        # ── Calificación bidireccional ─────────────────────────────────────────
        # autor_rol distingue quién calificó a quién:
        #   "cliente"             → cliente califica al plomero (real)
        #   "plomero"             → plomero califica al cliente (real)
        #   "sistema_cliente"     → penalización automática por cancelación del cliente
        #   "sistema_plomero"     → penalización automática por cancelación del plomero
        #   "sistema_vencimiento" → 5 estrellas automáticas por plazo vencido
        "ALTER TABLE calificaciones ADD COLUMN autor_rol VARCHAR DEFAULT 'cliente'",

        # estrellas pasa a REAL para soportar valores decimales (0.5, 1.5, 2.0)
        # SQLite lo maneja como REAL nativo, no requiere conversión
    ]

    for cmd in comandos:
        primera_linea = cmd.strip().splitlines()[0].strip()
        try:
            conn.execute(text(cmd))
            print(f"OK:            {primera_linea}")
        except Exception:
            print(f"Ya existe:     {primera_linea}")

    conn.commit()
    print("\nMigracion completada")