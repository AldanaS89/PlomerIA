"""
Servicio de IA: interpreta la descripcion en lenguaje natural del cliente y
devuelve un diagnostico tecnico (para el plomero), la especialidad sugerida,
la urgencia y un rango de presupuesto de materiales.

Usa google-genai. Si la API falla o no hay key, usa un fallback por palabras
clave. La idea central: el cliente escribe coloquial ("el cosito de la canilla
pierde") y la IA traduce eso a un diagnostico de plomeria.
"""
import json
import re
from typing import TypedDict

from config import GEMINI_API_KEY

ESPECIALIDADES = ["PLOMERIA_GENERAL", "DESTAPES", "GAS_MATRICULADO", "OBRA"]
URGENCIAS      = ["NORMAL", "URGENTE"]

# Palabras que sugieren un problema de plomeria/hogar (solo se usan en el
# fallback, cuando NO hay IA disponible — la IA entiende lenguaje natural).
PALABRAS_VALIDAS = [
    "agua", "canilla", "caño", "cano", "cañeria", "caneria", "gotea", "gotera",
    "gota", "perdida", "pérdida", "pierde", "moja", "mojado", "chorro", "chorrea",
    "inodoro", "baño", "bano", "pileta", "rejilla", "desague", "desagüe", "cloaca",
    "gas", "calefon", "calefón", "termotanque", "caldera", "cocina", "horno",
    "obra", "filtra", "filtracion", "filtración", "humedad", "humedo", "húmedo",
    "techo", "pared", "patio", "bomba", "presion", "presión", "llave", "grifo",
    "ducha", "ducharse", "destape", "tapon", "tapado", "tapada", "tapa",
    "desborde", "pozo", "reforma", "impermea", "fuga", "inunda", "inundacion",
    "tuberia", "tubería", "sale agua", "no anda", "cisterna", "mochila",
    "sanitario", "bidet", "lavatorio", "lavabo", "termo", "cosito", "perdiendo",
]

# Sanity minimo: que haya algo escrito (la IA decide el resto)
MIN_CARACTERES = 4
MIN_PALABRAS   = 2


class DiagnosticoIA(TypedDict):
    etiqueta_ia:     str
    urgencia_ia:     str
    diagnostico_ia:  str
    presupuesto_min: float
    presupuesto_max: float
    valido:          bool
    mensaje_error:   str


RANGOS = {
    "GAS_MATRICULADO":  (25000.0, 80000.0),
    "DESTAPES":         (15000.0, 45000.0),
    "OBRA":             (40000.0, 150000.0),
    "PLOMERIA_GENERAL": (12000.0, 50000.0),
}


def _invalido(msg: str) -> DiagnosticoIA:
    return {
        "etiqueta_ia":     "PLOMERIA_GENERAL",
        "urgencia_ia":     "NORMAL",
        "diagnostico_ia":  "",
        "presupuesto_min": 0.0,
        "presupuesto_max": 0.0,
        "valido":          False,
        "mensaje_error":   msg,
    }


def _diagnostico_fallback(etiqueta: str, urgencia: str) -> str:
    base = {
        "GAS_MATRICULADO":  "Posible problema de gas/artefacto — requiere matriculado",
        "DESTAPES":         "Cañería obstruida / desagote — requiere destape",
        "OBRA":             "Trabajo de obra/filtración — requiere intervención mayor",
        "PLOMERIA_GENERAL": "Problema de plomería general (pérdida/grifería/sanitario)",
    }.get(etiqueta, "Problema de plomería a evaluar en el domicilio")
    if urgencia == "URGENTE":
        base = "URGENTE — " + base
    return base


def _fallback(descripcion: str) -> DiagnosticoIA:
    desc = descripcion.lower()

    # ¿Hay al menos una pista de plomeria/hogar? Si no, lo marcamos invalido.
    if not any(k in desc for k in PALABRAS_VALIDAS):
        return _invalido(
            "No pudimos identificar un problema de plomería u hogar. "
            "Contanos qué está pasando con el agua, el gas o las cañerías."
        )

    if any(k in desc for k in ["gas", "calefon", "calefón", "termotanque", "caldera"]):
        etiqueta = "GAS_MATRICULADO"
    elif any(k in desc for k in ["tapad", "tapa", "destap", "cloaca", "desague", "desagüe", "pozo", "rejilla"]):
        etiqueta = "DESTAPES"
    elif any(k in desc for k in ["obra", "reforma", "filtra", "impermea", "humedad", "pared", "techo"]):
        etiqueta = "OBRA"
    else:
        etiqueta = "PLOMERIA_GENERAL"

    if any(k in desc for k in [
        "urgente", "urgencia", "emergencia", "inunda", "fuga", "pérdida", "perdida",
        "pierde", "olor a gas", "sin agua", "no tengo agua", "explota", "revienta",
        "roto", "no cierra", "no para", "chorrea", "chorro", "sale agua",
    ]):
        urgencia = "URGENTE"
    else:
        urgencia = "NORMAL"

    pmin, pmax = RANGOS.get(etiqueta, (15000.0, 60000.0))
    return {
        "etiqueta_ia":     etiqueta,
        "urgencia_ia":     urgencia,
        "diagnostico_ia":  _diagnostico_fallback(etiqueta, urgencia),
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


_PROMPT = """Sos un plomero experto en Argentina que interpreta lo que escribe un cliente.
El cliente NO sabe términos técnicos y escribe de forma coloquial (por ejemplo
"el cosito de la canilla pierde" o "sale un chorro de la rejilla del patio").
Tu trabajo es ENTENDER el problema real y traducirlo a un diagnóstico técnico.

Reglas:
- Si el texto describe (aunque sea coloquialmente) un problema de plomería, gas,
  cañerías, humedad u hogar relacionado, es válido. Interpretá las palabras
  informales. No exijas vocabulario técnico.
- Si el texto mezcla cosas irrelevantes con un problema real del hogar (ej:
  "me duele el dedo y gotea la canilla"), IGNORÁ lo irrelevante y diagnosticá el
  problema del hogar.
- Si NO hay ningún problema de plomería/hogar (ej: "me duele el dedo", "hola",
  texto sin sentido), devolvé valido: false.

Devolvé SOLO un JSON (sin texto extra, sin markdown) con estas claves:
- "valido": true/false
- "mensaje_error": si valido es false, explicación breve y amable; si no, ""
- "diagnostico_ia": diagnóstico técnico BREVE (una sola oración, máx ~12 palabras)
  en lenguaje de plomero. Ej: "Pérdida en sello de canilla de cocina".
- "etiqueta_ia": una de [PLOMERIA_GENERAL, DESTAPES, GAS_MATRICULADO, OBRA]
- "urgencia_ia": una de [NORMAL, URGENTE]
- "presupuesto_min": número en pesos argentinos (solo materiales, mínimo)
- "presupuesto_max": número en pesos argentinos (solo materiales, máximo)

Guía de especialidades:
- DESTAPES: cañerías tapadas, cloacas, pozos, desagües, rejillas que rebalsan.
- GAS_MATRICULADO: fugas de gas, calefón, caldera, termotanque, cocina a gas.
- OBRA: cañerías nuevas, reformas, filtraciones estructurales, humedad, impermeabilización.
- PLOMERIA_GENERAL: canillas, inodoros, pérdidas comunes, bombas, griferías.

Guía de urgencia:
- URGENTE: fuga activa, olor a gas, inundación, sin agua, problema que empeora rápido.
- NORMAL: problema molesto pero estable, cambio estético o preventivo.

Descripción del cliente:
\"\"\"{descripcion}\"\"\"

JSON:"""


def analizar_descripcion(descripcion: str) -> DiagnosticoIA:
    """
    Interpreta la descripción del cliente.
    Con IA disponible, la IA entiende el lenguaje natural y decide la validez.
    Sin IA, cae a un fallback por palabras clave (más permisivo).
    """
    desc_limpia = (descripcion or "").strip()

    # Sanity mínimo: que haya algo escrito
    if len(desc_limpia) < MIN_CARACTERES or len(desc_limpia.split()) < MIN_PALABRAS:
        return _invalido("Contanos un poco más: ¿qué está pasando en tu casa?")

    if GEMINI_API_KEY:
        try:
            from google import genai

            client = genai.Client(api_key=GEMINI_API_KEY)
            respuesta = client.models.generate_content(
                model    = "gemini-2.0-flash",
                contents = _PROMPT.format(descripcion=desc_limpia),
            )
            data = _parse_json(respuesta.text or "")

            if data:
                if not data.get("valido", True):
                    return _invalido(data.get(
                        "mensaje_error",
                        "No pudimos identificar un problema del hogar. Contanos qué está pasando.",
                    ))

                etiqueta = str(data.get("etiqueta_ia", "")).upper()
                urgencia = str(data.get("urgencia_ia", "")).upper()
                if etiqueta not in ESPECIALIDADES:
                    etiqueta = _fallback(desc_limpia)["etiqueta_ia"]
                if urgencia not in URGENCIAS:
                    urgencia = "NORMAL"

                pmin_def, pmax_def = RANGOS.get(etiqueta, (15000.0, 60000.0))
                diagnostico = str(data.get("diagnostico_ia", "")).strip() \
                    or _diagnostico_fallback(etiqueta, urgencia)

                return {
                    "etiqueta_ia":     etiqueta,
                    "urgencia_ia":     urgencia,
                    "diagnostico_ia":  diagnostico,
                    "presupuesto_min": float(data.get("presupuesto_min", pmin_def)),
                    "presupuesto_max": float(data.get("presupuesto_max", pmax_def)),
                    "valido":          True,
                    "mensaje_error":   "",
                }
            # Si no se pudo parsear, caemos al fallback
        except Exception as e:  # noqa: BLE001
            print(f"[ia_service] Error llamando a Gemini, usando fallback: {e}")

    return _fallback(desc_limpia)
