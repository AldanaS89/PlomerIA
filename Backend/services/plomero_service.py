from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional

from utils.seguridad import create_token, hash_password, verify_password
from services.disponibilidad_service import guardar_agenda_inicial
from repositories import plomero_repository, calificacion_repository
from schemas.plomero import PlomeroResponse
import random as _random

from utils.geolocalizacion import distancia_km, geocodificar
from utils.email import enviar_reset_password
from models.plomero import Plomero
from models.solicitud import Solicitud, EstadoSolicitud

import secrets


def _franja_de_hora(h: int) -> str:
    """Mapea una hora a su franja: mañana (8-12), tarde (13-17), noche (18+)."""
    if h <= 12:
        return "manana"
    if h <= 17:
        return "tarde"
    return "noche"

RADIO_KM = 5.0

# ─────────────────────────────
# RESEÑAS (públicas) — reales + ficticias según puntuación
# ─────────────────────────────
_NOMBRES_RESENA = [
    "Carlos M.", "Lucía P.", "Jorge R.", "Marta S.", "Diego F.",
    "Ana V.", "Roberto G.", "Sofía L.", "Hernán T.", "Valeria C.",
]
_RESENAS_ALTA = [
    "Excelente trabajo, muy prolijo y puntual.",
    "Resolvió todo rápido y quedó impecable.",
    "Súper recomendable, profesional y amable.",
    "Llegó en horario y dejó todo limpio.",
    "Un genio, solucionó la pérdida enseguida.",
]
_RESENAS_MEDIA = [
    "Buen trabajo, cumplió con lo pactado.",
    "Correcto, resolvió el problema.",
    "Bien, aunque tardó un poco en llegar.",
    "Cumplidor, lo recomiendo.",
]
_RESENAS_BAJA = [
    "Resolvió el problema pero llegó tarde.",
    "El trabajo quedó bien, la comunicación regular.",
    "Cumplió, aunque esperaba un poco más de prolijidad.",
]


def _pool_resenas(puntuacion: float):
    if puntuacion >= 4.5:
        return _RESENAS_ALTA
    if puntuacion >= 3.5:
        return _RESENAS_MEDIA
    return _RESENAS_BAJA


def obtener_resenas(db: Session, id_plomero: int) -> dict:
    """Reseñas públicas del plomero: reales (con comentario) + ficticias según su puntuación."""
    p = plomero_repository.buscar_por_id(db, id_plomero)
    if not p:
        raise HTTPException(status_code=404, detail="Plomero no encontrado")

    reales = []
    for c in calificacion_repository.obtener_calificaciones_plomero(db, id_plomero):
        if getattr(c, "comentario", None) and c.autor_rol == "cliente":
            reales.append({
                "autor": "Cliente",
                "estrellas": c.estrellas,
                "comentario": c.comentario,
                "fecha": c.fecha_resenia.isoformat() if getattr(c, "fecha_resenia", None) else None,
                "ficticia": False,
            })

    punt = p.puntuacion or 5.0
    rnd = _random.Random(id_plomero)
    pool = list(_pool_resenas(punt))
    rnd.shuffle(pool)
    faltan = max(0, 3 - len(reales))
    ficticias = []
    for i in range(faltan):
        est = round(min(5.0, max(1.0, punt + rnd.choice([-0.5, 0, 0, 0.5]))), 1)
        dias = rnd.randint(10, 220)
        ficticias.append({
            "autor": _NOMBRES_RESENA[(id_plomero + i) % len(_NOMBRES_RESENA)],
            "estrellas": est,
            "comentario": pool[i % len(pool)],
            "fecha": (datetime.now() - timedelta(days=dias)).isoformat(),
            "ficticia": True,
        })

    return {
        "id_plomero": id_plomero,
        "nombre": f"{p.nombre} {p.apellido}",
        "puntuacion": punt,
        "total_trabajos": p.total_trabajos or 0,
        "resenas": (reales[:3] + ficticias)[:3],
    }
DIAS_ES = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
FRANJAS = ["manana", "tarde", "noche"]
# ------- Nueva busqueda
def _keys_proximos_dias(dias: int) -> set[str]:
    """
    Genera las claves de agenda para los próximos N días
    a partir de ahora. Por ejemplo a las 23hs del lunes:
    - dia 0 (hoy): solo "noche" si quedan horas
    - dia 1 (mañana): manana, tarde, noche
    - dia 2 (pasado): manana, tarde, noche
    """
    ahora  = datetime.now()
    claves = set()

    for offset in range(dias + 1):
        fecha = ahora + timedelta(days=offset)
        dia   = DIAS_ES[fecha.weekday()]

        for franja in FRANJAS:
            # Para hoy solo incluir franjas futuras
            if offset == 0:
                hora_franja = {"manana": 8, "tarde": 13, "noche": 18}[franja]
                if ahora.hour >= hora_franja + 3:  # la franja ya pasó
                    continue
            claves.add(f"{dia}_{franja}")

    return claves

def _tiene_slot_en_claves(plomero, claves: set[str]) -> bool:
    """Verifica si el plomero tiene al menos un slot disponible en las claves dadas."""
    if not plomero.agenda:
        return False
    return any(plomero.agenda.get(k) for k in claves)

def buscar_urgencia_con_fallback(
    db:           Session,
    especialidad: str,
    lat:          float | None,
    lon:          float | None,
    genero:       str | None,
    limite:       int = 5,
) -> list:
    """
    Búsqueda para urgencias con 3 niveles de fallback.
    Nunca devuelve lista vacía si hay plomeros con atiende_urgencias=True.
    """

    def dist(p):
        if lat and lon and p.latitud and p.longitud:
            return distancia_km(lat, lon, p.latitud, p.longitud)
        return 9999

    def ordenar(lista):
        return sorted(lista, key=lambda p: (dist(p), -p.puntuacion))

    # ── NIVEL 1 — hoy y mañana, disponibles ahora, radio 5km ─────────────
    claves_2dias = _keys_proximos_dias(1)  # hoy + mañana

    nivel1 = plomero_repository.buscar_para_solicitud(
        db,
        especialidades    = especialidad,
        lat_usuario       = lat,
        lon_usuario       = lon,
        atiende_urgencias = True,
        genero            = genero,
        radio_km          = 5.0,
        limite            = 50,  # traemos más para filtrar por agenda
    )
    nivel1 = [p for p in nivel1 if _tiene_slot_en_claves(p, claves_2dias) or p.disponible_ahora]

    if len(nivel1) >= 1:
        return ordenar(nivel1)[:limite]

    # ── NIVEL 2 — hoy, mañana y pasado, sin exigir disponible_ahora, radio 10km ──
    claves_3dias = _keys_proximos_dias(2)  # hoy + mañana + pasado

    nivel2 = plomero_repository.buscar_para_solicitud(
        db,
        especialidades    = especialidad,
        lat_usuario       = lat,
        lon_usuario       = lon,
        atiende_urgencias = True,
        genero            = genero,
        radio_km          = 10.0,
        limite            = 50,
    )
    # No exigimos disponible_ahora — puede estar durmiendo
    nivel2 = [p for p in nivel2 if _tiene_slot_en_claves(p, claves_3dias)]

    if len(nivel2) >= 1:
        return ordenar(nivel2)[:limite]

    # ── NIVEL 3 — cualquiera que atienda urgencias, sin importar agenda ni radio ──
    # Último recurso: que el plomero decida si puede ir
    nivel3 = plomero_repository.buscar_para_solicitud(
        db,
        atiende_urgencias = True,
        genero            = genero,
        radio_km          = None,   # sin límite de radio
        limite            = 50,
    )

    if nivel3:
        return ordenar(nivel3)[:limite]

    # ── NIVEL 4 — cualquier plomero, sin ningún filtro ───────────────────
    # Nunca devolver lista vacía
    todos = plomero_repository.buscar_para_solicitud(
        db,
        radio_km = None,
        limite   = limite,
    )
    return ordenar(todos)[:limite]
# ─────────────────────────────
# REGISTRO
# ─────────────────────────────

def registrar_completo(
    db:                Session,
    nombre:            str,
    apellido:          str,
    email:             str,
    password:          str,
    localidad:         str,
    especialidades:    list[str],
    otra_especialidad: Optional[str],
    genero:            str,
    atiende_urgencias: bool,
    matricula_gas:     bool,
    agenda:            dict,
    foto_path:         Optional[str],
    direccion:         Optional[str]  = None,
    latitud:           Optional[float] = None,  # coordenadas del mapa
    longitud:          Optional[float] = None,  # coordenadas del mapa
):
    if plomero_repository.buscar_por_email(db, email):
        raise HTTPException(
            status_code=400,
            detail="El email ya está registrado"
        )

    # Usar coordenadas del mapa si vienen — si no, geocodificar
    if latitud is None or longitud is None:
        latitud, longitud = geocodificar(direccion or localidad, localidad)

    esp_final = []
    otra_custom = otra_especialidad

    for e in especialidades:
        if e.startswith("OTRA:"):
            otra_custom = e[5:]
        else:
            esp_final.append(e.upper())

    nuevo = Plomero(
        especialidad      = esp_final[0] if esp_final else "PLOMERIA_GENERAL",
        especialidades    = esp_final,
        otra_especialidad = otra_custom,
        nombre            = nombre,
        apellido          = apellido,
        email             = email,
        genero            = genero,
        localidad         = localidad,
        latitud           = latitud,
        longitud          = longitud,
        atiende_urgencias = atiende_urgencias,
        matricula_gas     = matricula_gas,
        password_hash     = hash_password(password),
        disponible_ahora  = True,
        puntuacion        = 5.0,   # puntuación inicial 5.0
        total_trabajos    = 0,
        foto_perfil_path  = foto_path,
        agenda            = agenda if agenda else None,
    )

    plomero = plomero_repository.crear_plomero(db, nuevo)

    if agenda:
        guardar_agenda_inicial(db, plomero.id_plomero, agenda)

    token = create_token({"sub": str(plomero.id_plomero), "tipo": "plomero"})

    return {
        "mensaje":      "Plomero registrado correctamente",
        "access_token": token,
        "token_type":   "bearer",
        "id_plomero":   plomero.id_plomero,
        "nombre":       plomero.nombre,
    }


# ─────────────────────────────
# PERFIL
# ─────────────────────────────

def obtener_mi_perfil(db: Session, id_plomero: int) -> PlomeroResponse:
    plomero = plomero_repository.buscar_por_id(db, id_plomero)
    if not plomero:
        raise HTTPException(status_code=404, detail="Plomero no encontrado")
    return PlomeroResponse.model_validate(plomero)


# ─────────────────────────────
# SUGERIR
# ─────────────────────────────

DIAS_ES       = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
FRANJAS       = ["manana", "tarde", "noche"]
FRANJA_INICIO = {"manana": 8, "tarde": 13, "noche": 18}


def ordenar_por_cercania_y_puntuacion(plomeros, dist_fn, relevancia_fn, limite=5):
    """
    Ordena los plomeros por TRAMOS de cercanía y, dentro de cada tramo, por
    relevancia y puntuación. Tramos: <5km (0), 5–10km (1), >10km (2).
    Prioridad: 1° cercanía, 2° puntuación, 3° relevancia (oficio), 4° distancia exacta.

    Función PURA (sin DB ni red): se le pasan `dist_fn(p)` y `relevancia_fn(p)`,
    para poder probarla de forma unitaria con objetos simulados.
    """
    def tramo(p):
        d = dist_fn(p)
        if d < 5:
            return 0
        if d < 10:
            return 1
        return 2

    return sorted(
        plomeros,
        key=lambda p: (tramo(p), -p.puntuacion, -relevancia_fn(p), dist_fn(p)),
    )[:limite]


def sugerir(
    db:               Session,
    descripcion:      str,
    solo_mujeres:     bool,
    lat_usuario:      float | None,
    lon_usuario:      float | None,
    urgencia_forzada: bool,
    excluidos:        list[int] | None = None,
):
    from services import ia_service

    diagnostico   = ia_service.analizar_descripcion(descripcion)
    etiqueta      = diagnostico["etiqueta_ia"]
    urgencia_ia   = diagnostico["urgencia_ia"]
    es_urgente    = urgencia_forzada or (urgencia_ia == "URGENTE")
    genero_filtro = "F" if solo_mujeres else None

    ahora       = datetime.now()
    hora_actual = ahora.hour
    dia_hoy     = DIAS_ES[ahora.weekday()]
    dia_manana  = DIAS_ES[(ahora.weekday() + 1) % 7]
    dia_pasado  = DIAS_ES[(ahora.weekday() + 2) % 7]  # ← nuevo

    franjas_hoy = [f for f in FRANJAS if FRANJA_INICIO[f] > hora_actual + 1]

    # Claves para hoy + mañana (nivel 1)
    keys_urgencia = (
        {f"{dia_hoy}_{f}" for f in franjas_hoy} |
        {f"{dia_manana}_{f}" for f in FRANJAS}   # ← mañana todas las franjas, no solo manana/tarde
    )

    # Claves para hoy + mañana + pasado mañana (nivel 2)
    keys_3dias = keys_urgencia | {f"{dia_pasado}_{f}" for f in FRANJAS}

    def _disp_ef(p):
        # "Disponible ahora" efectivo: marcado disponible, o ya pasó la hora desde
        # la que se libera tras finalizar un trabajo (disponible_desde).
        if getattr(p, "disponible_ahora", False):
            return True
        dd = getattr(p, "disponible_desde", None)
        return dd is not None and datetime.now() >= dd

    def tiene_slot(p, claves):
        """Verifica si el plomero tiene slot en las claves dadas."""
        if not p.agenda:
            return _disp_ef(p)
        return any(p.agenda.get(k) for k in claves)

    def dist(p):
        if lat_usuario and lon_usuario and p.latitud and p.longitud:
            return plomero_repository.distancia_km(lat_usuario, lon_usuario, p.latitud, p.longitud)
        return 9999

    def relevancia(p):
        score = 0
        if etiqueta and p.especialidades and etiqueta in p.especialidades:
            score += 3
        if es_urgente and p.atiende_urgencias and _disp_ef(p):
            score += 5
        return score

    # ─────────────────────────────────────────────────────────
    # URGENTE — 4 niveles de fallback, nunca devuelve vacío
    # ─────────────────────────────────────────────────────────
    if es_urgente:
        # Universo: TODOS los que atienden urgencias (con filtro de género),
        # SIN recortar por radio. La cercanía se respeta después al ordenar por
        # tramos (<5 / 5–10 / >10 km), así SIEMPRE completamos hasta 5 si los hay,
        # priorizando los más cercanos y mejor puntuados.
        universo = plomero_repository.filtrar(
            db,
            genero            = genero_filtro,
            atiende_urgencias = True,
            solo_disponibles  = False,
        )

        # Disponibilidad de más a menos estricta; acumulamos hasta llegar a 5.
        inmediatos = [
            p for p in universo
            if _disp_ef(p) or tiene_slot(p, keys_urgencia)    # ya, o franja hoy/mañana
        ]
        tres_dias = [p for p in universo if tiene_slot(p, keys_3dias)]  # hasta pasado mañana

        plomeros, vistos = [], set()

        def _sumar(lista):
            for p in lista:
                if p.id_plomero not in vistos:
                    vistos.add(p.id_plomero)
                    plomeros.append(p)

        _sumar(inmediatos)
        if len(plomeros) < 5:
            _sumar(tres_dias)
        if len(plomeros) < 5:
            _sumar(universo)   # último recurso: que el plomero decida si puede ir

        # Si NO hay ningún plomero de urgencias, plomeros queda vacío →
        # el front muestra "no encontramos un profesional, intentá más tarde".

    # ─────────────────────────────────────────────────────────
    # NO URGENTE — búsqueda normal con radio progresivo
    # ─────────────────────────────────────────────────────────
    else:
        # Universo completo (con filtro de género), SIN recortar por radio:
        # el orden por tramos prioriza la cercanía y la amplía solo si hace falta
        # para completar 5 (mismo criterio que en urgencias).
        plomeros = plomero_repository.filtrar(db, genero=genero_filtro)

    # ─────────────────────────────────────────────────────────
    # DEDUPLICAR Y ORDENAR
    # ─────────────────────────────────────────────────────────
    # Excluir a los ya contactados/rechazados ANTES de recortar a 5, así el
    # resultado siempre se completa con el resto del pool (no quedan huecos).
    excl = set(excluidos or [])

    # Plomeros NO disponibles para un trabajo nuevo: solo los que tienen un
    # trabajo activo de HOY o ya VENCIDO (sin cerrar). Un trabajo a FUTURO NO
    # los oculta —siguen apareciendo para otros días— y su franja ocupada se
    # marca aparte (ocupados_map) para no permitir doble reserva de ese turno.
    ahora_dt = datetime.now()
    hoy = ahora_dt.date()
    ocupados_activos = set()
    for id_p, ft, est in db.query(
        Solicitud.id_plomero, Solicitud.fecha_trabajo, Solicitud.estado
    ).filter(
        Solicitud.id_plomero.isnot(None),
        Solicitud.estado.in_([EstadoSolicitud.EN_PROGRESO, EstadoSolicitud.EN_CAMINO]),
    ).all():
        # EN_CAMINO = está yendo ahora; sin fecha = trabajo inmediato; fecha <= hoy
        # = de hoy o vencido. Cualquiera de esos lo deja fuera de las recomendaciones.
        if est == EstadoSolicitud.EN_CAMINO or ft is None or ft.date() <= hoy:
            ocupados_activos.add(id_p)

    vistos, unicos = set(), []
    for p in plomeros:
        if p.id_plomero in excl:
            continue
        if getattr(p, "suspendido", False):
            continue                      # cuenta suspendida → no se ofrece
        if p.id_plomero in ocupados_activos:
            continue                      # trabajo de hoy o vencido sin cerrar
        dd = getattr(p, "disponible_desde", None)
        if dd is not None and ahora_dt < dd:
            continue                      # recién finalizó: disponible desde la hora próxima
        if p.id_plomero not in vistos:
            vistos.add(p.id_plomero)
            unicos.append(p)

    # Orden por cercanía + relevancia + puntuación (función pura, ya testeada).
    resultado = ordenar_por_cercania_y_puntuacion(unicos, dist, relevancia, limite=5)

    # Franjas ya ocupadas por fecha (trabajos en curso) → "YYYY-MM-DD_franja".
    # El frontend usa esto para no ofrecer una franja ya reservada de ese plomero.
    ocupados_map = {}
    ids = [p.id_plomero for p in resultado]
    if ids:
        reservas = (
            db.query(Solicitud)
            .filter(
                Solicitud.id_plomero.in_(ids),
                Solicitud.estado.in_([EstadoSolicitud.EN_PROGRESO, EstadoSolicitud.EN_CAMINO]),
                Solicitud.fecha_trabajo.isnot(None),
            )
            .all()
        )
        for r in reservas:
            ft = r.fecha_trabajo
            clave = f"{ft.strftime('%Y-%m-%d')}_{_franja_de_hora(ft.hour)}"
            ocupados_map.setdefault(r.id_plomero, []).append(clave)

    # ─────────────────────────────────────────────────────────
    # FORMATEAR RESPUESTA
    # ─────────────────────────────────────────────────────────
    return [
        {
            "id_plomero":        p.id_plomero,
            "nombre":            p.nombre,
            "apellido":          p.apellido,
            "foto_perfil_path":  p.foto_perfil_path,
            "especialidad":      (p.especialidades or [etiqueta])[0],
            "especialidades":    p.especialidades or [],
            "localidad":         p.localidad,
            "puntuacion":        p.puntuacion,
            "total_trabajos":    p.total_trabajos,
            "atiende_urgencias": p.atiende_urgencias,
            "disponible_ahora":  p.disponible_ahora,
            "genero":            p.genero,
            "distancia_km":      round(dist(p), 2) if dist(p) < 9999 else None,
            "etiqueta_ia":       etiqueta,
            "urgencia_ia":       urgencia_ia,
            "agenda":            (
                {k: True for k in keys_urgencia if p.agenda and p.agenda.get(k)}
                if es_urgente and p.agenda
                else p.agenda or {}
            ),
            "ocupados":          ocupados_map.get(p.id_plomero, []),
        }
        for p in resultado
    ]


# ─────────────────────────────
# DISPONIBILIDAD
# ─────────────────────────────

def cambiar_disponibilidad(db: Session, id_plomero: int, disponible: bool):
    plomero = plomero_repository.actualizar_disponibilidad(db, id_plomero, disponible)
    if not plomero:
        raise HTTPException(status_code=404, detail="Plomero no encontrado")
    # Toggle manual: anula la liberación programada (manda lo que decide el plomero).
    plomero.disponible_desde = None
    db.commit()
    return {"mensaje": "Disponibilidad actualizada", "disponible_ahora": plomero.disponible_ahora}


def obtener_por_id(db: Session, id: int):
    plomero = plomero_repository.buscar_por_id(db, id)
    if not plomero:
        raise HTTPException(status_code=404, detail="Plomero no encontrado")
    return PlomeroResponse.model_validate(plomero)


def buscar_manual(
    db: Session,
    localidad: str | None = None,
    genero: str | None = None,
    especialidad: str | None = None,
    atiende_urgencias: bool | None = None,
    disponible_ahora: bool | None = None,
):

    return plomero_repository.obtener_filtrados(
        db=db,
        localidad=localidad,
        genero=genero,
        especialidades=especialidad,
        atiende_urgencias=atiende_urgencias,
        disponible_ahora=disponible_ahora,
    )

   