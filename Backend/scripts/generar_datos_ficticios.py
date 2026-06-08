"""
generar_datos_ficticios.py
==========================
Genera datos REALISTAS y CONSISTENTES para los plomeros precargados (ficticios):

  - Clientes ficticios (pool reutilizable, con nombre y calle/localidad reales).
    Son cuentas decorativas: no se usan para loguearse.
  - Trabajos PASADOS completados, repartidos en CADA mes desde que el plomero se
    unió (con boleta y calificación) → el historial y la facturación por mes
    muestran trabajos en todos los meses, y cuadran con el total.
  - Trabajos FUTUROS en curso que caen en franjas de su agenda → esas franjas
    aparecen OCUPADAS cuando un cliente real quiere reservarlo.

Además fija `total_trabajos` del plomero = la cantidad realmente generada, así el
número de la tarjeta, los stats, la facturación y el listado SIEMPRE coinciden.

Determinístico por id de plomero. SOLO afecta a plomeros ficticios (los del JSON).
NO toca cuentas creadas por el usuario.

Uso (desde Backend, con el venv activado):
    python scripts/generar_datos_ficticios.py
"""
import os
import sys
import json
import random
import calendar
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal                       # noqa: E402
from utils.seguridad import hash_password               # noqa: E402
from models.usuario import Usuario                      # noqa: E402
from models.plomero import Plomero                      # noqa: E402
from models.solicitud import Solicitud, EstadoSolicitud  # noqa: E402
from models.calificacion import Calificacion            # noqa: E402
from models.material import MaterialItem                # noqa: E402
from models.solicitud_plomero import SolicitudPlomero   # noqa: E402

JSON_FICTICIOS = Path(__file__).resolve().parent / "plomeros_enriquecido.json"
EMAIL_CLIENTE_FICTICIO = "cliente.demo.{i}@plomeria.local"
LANZAMIENTO = datetime(2026, 3, 1)   # la app no existía antes

NOMBRES = ["Sofía", "Mateo", "Valentina", "Joaquín", "Camila", "Benjamín",
           "Martina", "Tomás", "Julieta", "Lucas", "Catalina", "Thiago",
           "Renata", "Bautista", "Emma", "Santino", "Mía", "Lautaro",
           "Delfina", "Gael", "Olivia", "Felipe", "Isabella", "Dante",
           "Victoria", "Ciro", "Pilar", "Bruno", "Guadalupe", "León"]
APELLIDOS = ["Gómez", "Fernández", "Rodríguez", "López", "Martínez", "García",
             "Pérez", "Sánchez", "Romero", "Sosa", "Torres", "Álvarez",
             "Ruiz", "Díaz", "Acosta", "Molina", "Ríos", "Herrera",
             "Medina", "Castro", "Ortiz", "Núñez", "Vega", "Cabrera"]

# Calles reales/genéricas de la zona sur del GBA (creíbles para esas localidades)
CALLES = ["Av. Hipólito Yrigoyen", "Av. Mitre", "San Martín", "Belgrano",
          "Rivadavia", "9 de Julio", "Las Heras", "Sarmiento", "Alsina",
          "Moreno", "Av. Espora", "Av. Pte. Perón", "Lavalle", "Entre Ríos",
          "Colón", "España", "Italia", "Garibaldi", "Almirante Brown", "Mármol"]

DESCRIPCIONES = [
    "Pérdida de agua debajo de la pileta de la cocina.",
    "Se tapó el desagüe del baño y no drena.",
    "Gotea la canilla del lavatorio sin parar.",
    "Hay que cambiar el flexible del inodoro.",
    "Baja poca presión de agua en toda la casa.",
    "Filtración en la pared del baño.",
    "Necesito instalar un calefón nuevo.",
    "Se rompió la cañería del patio.",
    "El inodoro pierde agua por la base.",
    "Cambiar las rejillas y sifones del lavadero.",
    "Destapar la cañería principal del lavadero.",
    "Reparar la mochila del inodoro que pierde.",
]

ITEMS_BOLETA = [
    "Mano de obra", "Materiales y repuestos", "Flexible y accesorios",
    "Sellado y ajustes", "Reemplazo de cañería", "Limpieza de cañería",
]

COMENTARIOS_BUENOS = [
    "Excelente trabajo, muy prolijo y puntual.",
    "Resolvió todo rápido y explicó bien el problema.",
    "Muy amable y dejó todo impecable. Recomendable.",
    "Cumplió con el horario y el presupuesto. Lo vuelvo a llamar.",
    "Profesional y ordenado, quedé muy conforme.",
    "Buen trato y solución efectiva, gracias!",
]
COMENTARIOS_REGULARES = [
    "Cumplió, aunque llegó un poco tarde.",
    "Buen trabajo, el precio me pareció algo alto.",
    "Solucionó el problema, todo correcto.",
]

FRANJA_HORA = {"manana": 9, "tarde": 14, "noche": 19}
ABBR_TO_WD = {"Lun": 0, "Mar": 1, "Mié": 2, "Jue": 3, "Vie": 4, "Sáb": 5, "Dom": 6}


def _proxima_fecha(abbr: str, hora: int) -> datetime:
    hoy = datetime.now()
    target = ABBR_TO_WD.get(abbr, 0)
    diff = target - hoy.weekday()
    if diff < 0:
        diff += 7
    return (hoy + timedelta(days=diff)).replace(hour=hora, minute=0, second=0, microsecond=0)


def _meses_entre(desde: datetime, hasta: datetime):
    """Lista de primeros-de-mes entre `desde` y `hasta` (inclusive)."""
    meses = []
    cur = datetime(desde.year, desde.month, 1)
    fin = datetime(hasta.year, hasta.month, 1)
    while cur <= fin:
        meses.append(cur)
        cur = datetime(cur.year + 1, 1, 1) if cur.month == 12 else datetime(cur.year, cur.month + 1, 1)
    return meses


def _emails_ficticios() -> set[str]:
    if not JSON_FICTICIOS.exists():
        return set()
    with open(JSON_FICTICIOS, encoding="utf-8") as f:
        return {d["email"] for d in json.load(f) if "email" in d}


def _zonas_desde_json():
    if not JSON_FICTICIOS.exists():
        return [("Lanús", -34.70, -58.39)]
    with open(JSON_FICTICIOS, encoding="utf-8") as f:
        data = json.load(f)
    zonas = [(d["localidad"], d["latitud"], d["longitud"])
             for d in data if d.get("latitud") and d.get("longitud")]
    return zonas or [("Lanús", -34.70, -58.39)]


def _asegurar_clientes(db, zonas, cantidad=30):
    """Crea (si no existen) un pool de clientes ficticios con calle/localidad reales."""
    clientes = []
    rnd = random.Random(12345)
    for i in range(cantidad):
        email = EMAIL_CLIENTE_FICTICIO.format(i=i)
        u = db.query(Usuario).filter(Usuario.email == email).first()
        if not u:
            loc, lat, lon = rnd.choice(zonas)
            u = Usuario(
                nombre=NOMBRES[i % len(NOMBRES)],
                apellido=APELLIDOS[(i * 5 + 1) % len(APELLIDOS)],
                email=email,
                password_hash=hash_password("demo-ficticio-no-login"),
                localidad=loc,
                direccion=f"{rnd.choice(CALLES)} {rnd.randint(100, 4800)}",
                latitud=lat + rnd.uniform(-0.01, 0.01),
                longitud=lon + rnd.uniform(-0.01, 0.01),
                rol="cliente",
            )
            db.add(u)
        clientes.append(u)
    db.commit()
    for u in clientes:
        db.refresh(u)
    return clientes


def _limpiar_datos_previos(db, clientes):
    """Borra los trabajos ficticios anteriores (los de estos clientes) para no duplicar."""
    ids = [c.id_usuario for c in clientes]
    if not ids:
        return
    soli_ids = [s.id_solicitud for s in
                db.query(Solicitud).filter(Solicitud.id_usuario.in_(ids)).all()]
    if soli_ids:
        db.query(MaterialItem).filter(MaterialItem.id_solicitud.in_(soli_ids)).delete(synchronize_session=False)
        db.query(Calificacion).filter(Calificacion.id_solicitud.in_(soli_ids)).delete(synchronize_session=False)
        db.query(SolicitudPlomero).filter(SolicitudPlomero.id_solicitud.in_(soli_ids)).delete(synchronize_session=False)
        db.query(Solicitud).filter(Solicitud.id_solicitud.in_(soli_ids)).delete(synchronize_session=False)
    db.commit()


def _crear_trabajo(db, p, cli, ft, esp, rnd, estado):
    """Crea una solicitud (con boleta) entre el cliente y el plomero en la fecha ft."""
    s = Solicitud(
        id_usuario=cli.id_usuario,
        id_plomero=p.id_plomero,
        descripcion_raw=rnd.choice(DESCRIPCIONES),
        etiqueta_ia=esp,
        urgencia_ia="NO_URGENTE",
        localidad_evento=cli.localidad,
        latitud_evento=cli.latitud,
        longitud_evento=cli.longitud,
        fecha=ft,
        fecha_trabajo=ft,
        estado=estado,
    )
    db.add(s)
    db.flush()
    # Boleta (1-2 ítems) → monto realista
    n_items = rnd.randint(1, 2)
    for _ in range(n_items):
        db.add(MaterialItem(
            id_solicitud=s.id_solicitud,
            descripcion=rnd.choice(ITEMS_BOLETA),
            cantidad=1.0,
            precio=float(rnd.randint(8, 28) * 1000),  # $8.000 – $28.000
        ))
    return s


def main():
    db = SessionLocal()
    try:
        emails_fic = _emails_ficticios()
        if not emails_fic:
            print("⚠ No se encontró plomeros_enriquecido.json; no genero datos.")
            return

        zonas = _zonas_desde_json()
        clientes = _asegurar_clientes(db, zonas)
        _limpiar_datos_previos(db, clientes)

        plomeros = [p for p in db.query(Plomero).all() if p.email in emails_fic]
        ahora = datetime.now()
        total_pasados = total_futuros = 0

        for p in plomeros:
            rnd = random.Random(p.id_plomero)
            esp = (p.especialidades or ["PLOMERIA_GENERAL"])[0]

            alta = p.fecha_registro or LANZAMIENTO
            if alta < LANZAMIENTO:
                alta = LANZAMIENTO

            # ── PASADOS: 2 a 5 trabajos por cada mes activo ──────────────
            generados = 0
            for mes in _meses_entre(alta, ahora):
                ultimo = calendar.monthrange(mes.year, mes.month)[1]
                for _ in range(rnd.randint(2, 5)):
                    dia = rnd.randint(1, ultimo)
                    hora = rnd.choice([9, 11, 14, 16, 18])
                    ft = datetime(mes.year, mes.month, dia, hora)
                    if ft > ahora or ft < alta:
                        continue   # nada en el futuro ni antes del alta
                    s = _crear_trabajo(db, p, rnd.choice(clientes), ft, esp, rnd,
                                       EstadoSolicitud.COMPLETADA)
                    base = p.puntuacion or 4.5
                    estrellas = max(3.5, min(5.0, round(base + rnd.uniform(-0.4, 0.3), 1)))
                    db.add(Calificacion(
                        id_solicitud=s.id_solicitud,
                        id_cliente=s.id_usuario,
                        id_plomero=p.id_plomero,
                        autor_rol="cliente",
                        estrellas=estrellas,
                        comentario=(rnd.choice(COMENTARIOS_BUENOS) if estrellas >= 4.3
                                    else rnd.choice(COMENTARIOS_REGULARES)),
                        fecha_resenia=ft + timedelta(hours=3),
                    ))
                    generados += 1
                    total_pasados += 1

            # El total del perfil = lo realmente generado (todo coincide)
            p.total_trabajos = generados

            # ── FUTUROS: hasta 2 franjas de su agenda quedan ocupadas ─────
            claves = [k for k, v in (p.agenda or {}).items() if v]
            rnd.shuffle(claves)
            for clave in claves[:2]:
                try:
                    dia, franja = clave.split("_", 1)
                except ValueError:
                    continue
                hora = FRANJA_HORA.get(franja, 9)
                ft = _proxima_fecha(dia, hora)
                s = _crear_trabajo(db, p, rnd.choice(clientes), ft, esp, rnd,
                                   EstadoSolicitud.EN_PROGRESO)
                s.turno_solicitado = f"{dia}_{franja}_{hora}"
                s.fecha = ahora
                total_futuros += 1

        db.commit()
        print(f"Datos ficticios: {len(plomeros)} plomeros, "
              f"{total_pasados} trabajos pasados (repartidos por mes), "
              f"{total_futuros} futuros (agenda ocupada).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
