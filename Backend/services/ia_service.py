"""
Servicio de IA: analiza la descripción de una solicitud y devuelve
etiqueta (especialidad sugerida), urgencia y rango de presupuesto.

Usa Google Gemini (google-generativeai). Si la API falla o no hay key,
devuelve un diagnóstico por defecto para que el flujo no se rompa.
"""
import json
import re
from typing import TypedDict

from config import GEMINI_API_KEY

ESPECIALIDADES = ["PLOMERIA_GENERAL", "DESTAPES", "GAS_MATRICULADO", "OBRA"]
URGENCIAS = ["BAJA", "NORMAL", "URGENTE"]


class DiagnosticoIA(TypedDict):
    etiqueta_ia: str
    urgencia_ia: str
    presupuesto_min: float
    presupuesto_max: float


_PROMPT = """Sos un asistente que clasifica problemas de plomería en Argentina.
A partir de la descripción del cliente, devolvé SOLO un JSON (sin texto extra, sin markdown) con estas claves:

- "etiqueta_ia": una de [PLOMERIA_GENERAL, DESTAPES, GAS_MATRICULADO, OBRA]
- "urgencia_ia": una de [BAJA, NORMAL, URGENTE]
- "presupuesto_min": número en pesos argentinos (estimado mínimo)
- "presupuesto_max": número en pesos argentinos (estimado máximo)

Guía:
- DESTAPES: cañerías tapadas, cloacas, pozos, desagües.
- GAS_MATRICULADO: fugas de gas, calefón, caldera, termotanque, cocina a gas.
- OBRA: cañerías nuevas, reformas, filtraciones estructurales, impermeabilización.
- PLOMERIA_GENERAL: canillas, inodoros, pérdidas comunes, bombas, griferías.
- URGENTE: fuga activa, olor a gas, inundación, sin agua en toda la casa.
- NORMAL: problema molesto pero no peligroso.
- BAJA: cambio estético o preventivo.

Descripción del cliente:
\"\"\"{descripcion}\"\"\"

JSON:"""


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

    if any(k in desc for k in ["urgente", "inunda", "fuga", "olor a gas", "sin agua"]):
        urgencia = "URGENTE"
    else:
        urgencia = "NORMAL"

    return {
        "etiqueta_ia": etiqueta,
        "urgencia_ia": urgencia,
        "presupuesto_min": 15000.0,
        "presupuesto_max": 60000.0,
    }


def _parse_json(texto: str) -> dict | None:
    match = re.search(r"\{[\s\S]*\}", texto)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def analizar_descripcion(descripcion: str) -> DiagnosticoIA:
    if not GEMINI_API_KEY:
        return _fallback(descripcion)

    try:
        import google.generativeai as genai

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-flash-latest")
        respuesta = model.generate_content(_PROMPT.format(descripcion=descripcion))
        data = _parse_json(respuesta.text or "")
        if not data:
            return _fallback(descripcion)

        etiqueta = str(data.get("etiqueta_ia", "")).upper()
        urgencia = str(data.get("urgencia_ia", "")).upper()
        if etiqueta not in ESPECIALIDADES:
            etiqueta = _fallback(descripcion)["etiqueta_ia"]
        if urgencia not in URGENCIAS:
            urgencia = "NORMAL"

        return {
            "etiqueta_ia": etiqueta,
            "urgencia_ia": urgencia,
            "presupuesto_min": float(data.get("presupuesto_min", 15000)),
            "presupuesto_max": float(data.get("presupuesto_max", 60000)),
        }
    except Exception as e:
        print(f"[ia_service] Error llamando a Gemini, usando fallback: {e}")
        return _fallback(descripcion)
