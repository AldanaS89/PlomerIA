"""
Servicio de IA: analiza la descripción de una solicitud y devuelve
etiqueta (especialidad sugerida), urgencia y rango de presupuesto.

Usa google-genai (nueva librería sin gRPC, compatible con Python 3.14).
Si la API falla o no hay key, usa fallback por palabras clave.
"""
import json
import re
from typing import TypedDict

from config import GEMINI_API_KEY

ESPECIALIDADES = ["PLOMERIA_GENERAL", "DESTAPES", "GAS_MATRICULADO", "OBRA"]
URGENCIAS      = ["NORMAL", "URGENTE"]

# Palabras que indican que la descripción habla de plomería u hogar
PALABRAS_VALIDAS = [
    "agua", "canilla", "caño", "cañería", "gotea", "gota", "pérdida", "perdida",
    "pierde", "inodoro", "baño", "pileta", "desagüe", "desague", "cloaca",
    "gas", "calefón", "calefon", "termotanque", "caldera", "cocina",
    "obra", "filtracion", "filtración", "humedad", "techo", "pared",
    "bomba", "presión", "presion", "llave", "grifo", "ducha", "ducharse",
    "destape", "tapon", "tapado", "tapada", "desborde", "pozo",
    "reforma", "impermeabilización", "impermeabilizacion",
    "fuga", "urgente", "emergencia", "inundacion", "inundación",
    "tubería", "tuberia", "filtra", "humedo", "húmedo",
]

MIN_PALABRAS          = 5
MIN_PALABRAS_VALIDAS  = 2


class DiagnosticoIA(TypedDict):
    etiqueta_ia:     str
    urgencia_ia:     str
    presupuesto_min: float
    presupuesto_max: float
    valido:          bool
    mensaje_error:   str


def _descripcion_valida(descripcion: str) -> tuple[bool, str]:
    palabras = descripcion.strip().split()
    if len(palabras) < MIN_PALABRAS:
        return False, (
            "Por favor describí el problema con más detalle. "
            "Contanos qué está pasando en tu casa."
        )
    desc = descripcion.lower()
    cantidad_validas = sum(1 for k in PALABRAS_VALIDAS if k in desc)
    if cantidad_validas < MIN_PALABRAS_VALIDAS:
        return False, (
            "No pudimos identificar un problema relacionado con plomería u hogar. "
            "Describí qué está pasando con el agua, gas, cañerías u otro problema del hogar."
        )
    return True, ""


def _fallback(descripcion: str) -> DiagnosticoIA:
    desc = descripcion.lower()

    if any(k in desc for k in ["gas", "calefón", "calefon", "termotanque", "caldera"]):
        etiqueta = "GAS_MATRICULADO"
    elif any(k in desc for k in ["tapad", "destap", "cloaca", "desagüe", "desague", "pozo"]):
        etiqueta = "DESTAPES"
    elif any(k in desc for k in ["obra", "reforma", "filtraci", "impermea"]):
        etiqueta = "OBRA"
    else:
        etiqueta = "PLOMERIA_GENERAL"

    if any(k in desc for k in [
        "urgente", "urgencia", "emergencia",
        "inunda", "fuga", "pérdida", "perdida", "pierde",
        "olor a gas", "sin agua", "no tengo agua",
        "explota", "revienta", "roto", "no cierra", "no para",
        "chorrea", "sale agua", "agua por todos lados",
        "caño roto", "cano roto", "cañería rota",
    ]):
        urgencia = "URGENTE"
    else:
        urgencia = "NORMAL"

    rangos = {
        "GAS_MATRICULADO":  (25000.0, 80000.0),
        "DESTAPES":         (15000.0, 45000.0),
        "OBRA":             (40000.0, 150000.0),
        "PLOMERIA_GENERAL": (12000.0, 50000.0),
    }
    pmin, pmax = rangos.get(etiqueta, (15000.0, 60000.0))

    return {
        "etiqueta_ia":     etiqueta,
        "urgencia_ia":     urgencia,
        "presupuesto_min": pmin,
        "presupuesto_max": pmax,
        "valido":          True,
        "mensaje_error":   "",
    }


def _parse_json(texto: str) -> dict | None:
    match = re.search(r"\{[\s\S]*\}", texto)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


_PROMPT = """Sos un asistente que clasifica problemas del hogar en Argentina.
Antes de clasificar, verificá si la descripción describe un problema real del hogar.
Si no tiene sentido o no es un problema del hogar, devolvé valido: false.

Devolvé SOLO un JSON (sin texto extra, sin markdown) con estas claves:

- "valido": true si describe un problema real del hogar, false si no tiene sentido
- "mensaje_error": explicación breve si valido es false, sino string vacío
- "etiqueta_ia": una de [PLOMERIA_GENERAL, DESTAPES, GAS_MATRICULADO, OBRA]
- "urgencia_ia": una de [NORMAL, URGENTE]
- "presupuesto_min": número en pesos argentinos (solo materiales, estimado mínimo)
- "presupuesto_max": número en pesos argentinos (solo materiales, estimado máximo)

Guía de especialidades:
- DESTAPES: cañerías tapadas, cloacas, pozos, desagües.
- GAS_MATRICULADO: fugas de gas, calefón, caldera, termotanque, cocina a gas.
- OBRA: cañerías nuevas, reformas, filtraciones estructurales, impermeabilización.
- PLOMERIA_GENERAL: canillas, inodoros, pérdidas comunes, bombas, griferías.

Guía de urgencia:
- URGENTE: fuga activa, olor a gas, inundación, sin agua, problema que empeora rápido.
- NORMAL: problema molesto pero estable, cambio estético o preventivo.

Nota: presupuesto incluye solo materiales estimados.
La mano de obra varía según el profesional y la zona.

Descripción del cliente:
\"\"\"{descripcion}\"\"\"

JSON:"""


def analizar_descripcion(descripcion: str) -> DiagnosticoIA:
    """
    Analiza la descripción del cliente.
    Primero valida coherencia localmente, luego llama a Gemini o usa fallback.
    """
    # Validación previa de coherencia
    es_valida, msg_error = _descripcion_valida(descripcion)
    if not es_valida:
        return {
            "etiqueta_ia":     "PLOMERIA_GENERAL",
            "urgencia_ia":     "NORMAL",
            "presupuesto_min": 0.0,
            "presupuesto_max": 0.0,
            "valido":          False,
            "mensaje_error":   msg_error,
        }

    if not GEMINI_API_KEY:
        return _fallback(descripcion)

    try:
        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)
        respuesta = client.models.generate_content(
            model  = "gemini-2.0-flash",
            contents = _PROMPT.format(descripcion=descripcion),
        )
        texto = respuesta.text or ""
        data  = _parse_json(texto)

        if not data:
            return _fallback(descripcion)

        # Si Gemini dice que no es válido
        if not data.get("valido", True):
            return {
                "etiqueta_ia":     "PLOMERIA_GENERAL",
                "urgencia_ia":     "NORMAL",
                "presupuesto_min": 0.0,
                "presupuesto_max": 0.0,
                "valido":          False,
                "mensaje_error":   data.get("mensaje_error",
                    "No pudimos identificar un problema del hogar. "
                    "Por favor describí qué está pasando."),
            }

        etiqueta = str(data.get("etiqueta_ia", "")).upper()
        urgencia = str(data.get("urgencia_ia", "")).upper()

        if etiqueta not in ESPECIALIDADES:
            etiqueta = _fallback(descripcion)["etiqueta_ia"]
        if urgencia not in URGENCIAS:
            urgencia = "NORMAL"

        rangos = {
            "GAS_MATRICULADO":  (25000.0, 80000.0),
            "DESTAPES":         (15000.0, 45000.0),
            "OBRA":             (40000.0, 150000.0),
            "PLOMERIA_GENERAL": (12000.0, 50000.0),
        }
        pmin_def, pmax_def = rangos.get(etiqueta, (15000.0, 60000.0))

        return {
            "etiqueta_ia":     etiqueta,
            "urgencia_ia":     urgencia,
            "presupuesto_min": float(data.get("presupuesto_min", pmin_def)),
            "presupuesto_max": float(data.get("presupuesto_max", pmax_def)),
            "valido":          True,
            "mensaje_error":   "",
        }

    except Exception as e:
        print(f"[ia_service] Error llamando a Gemini, usando fallback: {e}")
        return _fallback(descripcion)