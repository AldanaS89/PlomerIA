"""
services/moderacion.py
======================
Moderación del chat y manejo de suspensiones de cuentas.

Responsabilidad única (SRP): todo lo de "censurar groserías" y "suspender /
reactivar cuentas" vive acá, separado del flujo de mensajería y de solicitudes.

- censurar(texto): reemplaza malas palabras por asteriscos (palabra completa).
- registrar_mensaje_ofensivo(persona): suma una amonestación; a la 3ª suspende
  la cuenta por 2 meses.
- suspender(persona, dias): suspende con fecha de fin (reactivación automática).
- reactivar_si_corresponde / esta_suspendido: levantan la suspensión sola cuando
  venció el plazo (sin necesidad de un proceso de fondo).
"""
import re
import unicodedata
import logging
from datetime import datetime, timedelta

from models.plomero import Plomero

logger = logging.getLogger(__name__)

# Parámetros de moderación
AMONESTACIONES_PARA_SUSPENSION = 3      # a la 3ª grosería → suspensión
DIAS_SUSPENSION_GROSERIAS      = 60     # 2 meses
DIAS_SUSPENSION_CANCELACIONES  = 30     # 1 mes

# Lista de groserías (es-AR). En minúscula y sin acentos: el match normaliza.
_GROSERIAS = {
    "boludo", "boluda", "boludos", "boludas", "pelotudo", "pelotuda",
    "pelotudos", "pelotudas", "forro", "forra", "forros", "forras",
    "conchudo", "conchuda", "concha", "puta", "putas", "puto", "putos",
    "mierda", "mierdas", "carajo", "gil", "giles", "sorete", "soretes",
    "choto", "chota", "pajero", "pajera", "imbecil", "imbeciles", "idiota",
    "idiotas", "estupido", "estupida", "estupidos", "estupidas", "tarado",
    "tarada", "tarados", "taradas", "cagon", "cagona", "garca", "garcas",
    "ortiba", "trolo", "trola", "verga", "pija", "culiao", "culiada",
    "culiados", "mogolico", "mogolica", "subnormal", "cornudo", "cornuda",
    "reculiao", "reculiada", "zorra", "puto", "putazo",
}


def _normalizar(palabra: str) -> str:
    """Pasa a minúscula y quita acentos para comparar contra la lista."""
    p = unicodedata.normalize("NFD", palabra.lower())
    return "".join(c for c in p if unicodedata.category(c) != "Mn")


def censurar(texto: str) -> tuple[str, bool]:
    """
    Devuelve (texto_censurado, hubo_groseria). Reemplaza cada mala palabra
    (como palabra completa) por asteriscos del mismo largo.
    """
    if not texto:
        return texto, False
    hubo = {"v": False}

    def _reemplazo(match):
        palabra = match.group(0)
        if _normalizar(palabra) in _GROSERIAS:
            hubo["v"] = True
            return "*" * len(palabra)
        return palabra

    # \w incluye letras acentuadas y ñ en Python 3 con re.UNICODE (por defecto)
    censurado = re.sub(r"\w+", _reemplazo, texto, flags=re.UNICODE)
    return censurado, hubo["v"]


# ── Suspensiones (compartidas por groserías y por cancelaciones) ──────────────

def suspender(db, persona, dias: int) -> None:
    """Suspende la cuenta por `dias` días, con reactivación automática al vencer."""
    if not persona:
        return
    persona.suspendido = True
    persona.suspendido_hasta = datetime.now() + timedelta(days=dias)
    if isinstance(persona, Plomero):
        persona.disponible_ahora = False
    db.commit()
    logger.warning("%s id=%s suspendido hasta %s",
                   type(persona).__name__, getattr(persona, "get_id", lambda: "?")(),
                   persona.suspendido_hasta)


def reactivar_si_corresponde(db, persona) -> None:
    """Si la suspensión venció, reactiva la cuenta sola y limpia los contadores."""
    if not persona:
        return
    hasta = getattr(persona, "suspendido_hasta", None)
    if getattr(persona, "suspendido", False) and hasta and datetime.now() >= hasta:
        persona.suspendido = False
        persona.suspendido_hasta = None
        persona.cancelaciones_consecutivas = 0
        persona.mensajes_ofensivos = 0
        db.commit()
        logger.info("%s id=%s reactivado automáticamente",
                    type(persona).__name__, getattr(persona, "get_id", lambda: "?")())


def esta_suspendido(db, persona) -> bool:
    """True si la cuenta sigue suspendida (reactivando antes si ya venció el plazo)."""
    if not persona:
        return False
    reactivar_si_corresponde(db, persona)
    return bool(getattr(persona, "suspendido", False))


def mensaje_suspension(persona) -> str:
    """Texto claro para mostrarle al usuario suspendido."""
    hasta = getattr(persona, "suspendido_hasta", None)
    if hasta:
        return f"Tu cuenta está suspendida hasta el {hasta.strftime('%d/%m/%Y')}."
    return "Tu cuenta está suspendida."


def registrar_mensaje_ofensivo(db, persona) -> tuple[bool, int]:
    """
    Suma una amonestación por groserías. Avisa en la 1ª y 2ª; a la 3ª suspende
    la cuenta 2 meses.
    Devuelve (suspendido, numero_de_aviso) — numero_de_aviso es 1, 2 o 3.
    """
    if not persona:
        return (False, 0)
    persona.mensajes_ofensivos = (getattr(persona, "mensajes_ofensivos", 0) or 0) + 1
    numero = persona.mensajes_ofensivos
    if numero >= AMONESTACIONES_PARA_SUSPENSION:
        persona.mensajes_ofensivos = 0           # se reinicia al cumplir la sanción
        suspender(db, persona, DIAS_SUSPENSION_GROSERIAS)
        return (True, numero)
    db.commit()
    return (False, numero)
