from google import genai
from dotenv import load_dotenv
import os
import json
import base64

load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


SYSTEM_PROMPT = """
Sos un clasificador de solicitudes de plomería y gas en Argentina.

Tu tarea es analizar el problema descrito por el cliente y responder
EXCLUSIVAMENTE con JSON válido.

NO expliques nada fuera del JSON.
NO uses markdown.
NO uses ```json.
NO agregues texto adicional.

Las etiquetas válidas son:
- PLOMERIA_GENERAL
- DESTAPES
- GAS_MATRICULADO
- OBRA

Las urgencias válidas son:
- NORMAL
- URGENTE
- EMERGENCIA

Formato obligatorio:

{
  "etiqueta": "...",
  "urgencia": "...",
  "presupuesto_min": 0,
  "presupuesto_max": 0,
  "explicacion": "..."
}
"""


def diagnosticar(descripcion: str, imagen_path: str = None) -> dict:

    contents = [
        {
            "role": "user",
            "parts": [
                {"text": SYSTEM_PROMPT},
                {"text": f"Problema del cliente: {descripcion}"}
            ]
        }
    ]

    # ✅ Si hay imagen
    if imagen_path and os.path.exists(imagen_path):
        with open(imagen_path, "rb") as f:
            imagen_bytes = f.read()

        contents[0]["parts"].append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(imagen_bytes).decode("utf-8")
            }
        })

    # ✅ Llamada nueva API
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=contents
    )

    texto = response.text.strip()

    # limpiar ```json
    if texto.startswith("```"):
        texto = texto.split("```")[1]
        if texto.startswith("json"):
            texto = texto[4:]

    return json.loads(texto)