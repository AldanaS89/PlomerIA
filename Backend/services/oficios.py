# services/oficios.py
"""
Registro central de OFICIOS de la plataforma.

Objetivo (Open/Closed): agregar un oficio nuevo = agregar una entrada acá y
ponerle "habilitado": True. La IA, el filtrado y la UI consumen este registro,
así no hay que tocar la lógica para sumar electricista, cerrajero, etc.

Hoy solo PLOMERIA está habilitado; los demás se definen pero quedan inhabilitados
(se ven, no se pueden elegir todavía), tal como se pensó el producto.
"""

OFICIOS = {
    "PLOMERIA": {
        "label": "Plomería",
        "habilitado": True,
        "especialidades": {
            "PLOMERIA_GENERAL": "Plomería general",
            "DESTAPES":         "Destapes",
            "GAS_MATRICULADO":  "Gas matriculado",
            "OBRA":             "Obra",
        },
        "rangos": {  # presupuesto de materiales (min, max) por especialidad
            "PLOMERIA_GENERAL": (12000.0, 50000.0),
            "DESTAPES":         (15000.0, 45000.0),
            "GAS_MATRICULADO":  (25000.0, 80000.0),
            "OBRA":             (40000.0, 150000.0),
        },
        "pistas": [
            "agua", "canilla", "caño", "cano", "cañeria", "caneria", "gotea",
            "gotera", "perdida", "pérdida", "pierde", "inodoro", "baño", "pileta",
            "rejilla", "desague", "cloaca", "gas", "calefon", "termotanque",
            "caldera", "destape", "tapado", "humedad", "filtra", "bomba", "ducha",
        ],
        "descripcion_ia": "problemas de agua, gas, cañerías, sanitarios, humedad y destapes",
    },

    # ── Inhabilitados (definidos para futuro, no seleccionables aún) ──
    "ELECTRICIDAD": {
        "label": "Electricidad",
        "habilitado": False,
        "especialidades": {
            "ELEC_GENERAL": "Electricidad general",
            "TABLEROS":     "Tableros y disyuntores",
            "ILUMINACION":  "Iluminación",
        },
        "rangos": {
            "ELEC_GENERAL": (10000.0, 45000.0),
            "TABLEROS":     (20000.0, 70000.0),
            "ILUMINACION":  (8000.0, 40000.0),
        },
        "pistas": ["luz", "sin luz", "corto", "cortocircuito", "enchufe", "tomas",
                   "disyuntor", "tablero", "cable", "chispa", "térmica", "termica"],
        "descripcion_ia": "problemas eléctricos: cortes, cortocircuitos, tableros, enchufes, iluminación",
    },
    "CERRAJERIA": {
        "label": "Cerrajería",
        "habilitado": False,
        "especialidades": {
            "CERR_GENERAL": "Cerrajería general",
            "APERTURAS":    "Aperturas de urgencia",
        },
        "rangos": {
            "CERR_GENERAL": (8000.0, 35000.0),
            "APERTURAS":    (12000.0, 50000.0),
        },
        "pistas": ["cerradura", "llave", "traba", "puerta", "candado", "me quedé afuera"],
        "descripcion_ia": "problemas de cerraduras, llaves, puertas trabadas y aperturas",
    },
}

# Palabras que indican urgencia en cualquier oficio
URGENCIA_KEYWORDS = [
    "urgente", "urgencia", "emergencia", "inunda", "inundacion", "fuga",
    "sin agua", "no tengo agua", "sin luz", "corto", "cortocircuito", "chispa",
    "olor a gas", "explota", "revienta", "no para", "chorrea", "sale agua",
    "me quedé afuera", "me quede afuera",
]


def oficios_habilitados() -> dict:
    return {k: v for k, v in OFICIOS.items() if v.get("habilitado")}


def especialidades_validas(solo_habilitados: bool = True) -> list[str]:
    fuente = oficios_habilitados() if solo_habilitados else OFICIOS
    out = []
    for o in fuente.values():
        out += list(o["especialidades"].keys())
    return out


def rango_presupuesto(especialidad: str, default=(15000.0, 60000.0)):
    for o in OFICIOS.values():
        if especialidad in o.get("rangos", {}):
            return o["rangos"][especialidad]
    return default


def oficio_de_especialidad(especialidad: str) -> str | None:
    for k, o in OFICIOS.items():
        if especialidad in o["especialidades"]:
            return k
    return None


def detectar_oficio(texto: str) -> str | None:
    """Detecta el oficio por palabras clave (fallback, entre los habilitados)."""
    t = (texto or "").lower()
    mejor, score = None, 0
    for k, o in oficios_habilitados().items():
        c = sum(1 for p in o["pistas"] if p in t)
        if c > score:
            mejor, score = k, c
    return mejor


def guia_especialidades_ia() -> str:
    """Texto para el prompt: lista de especialidades de los oficios habilitados."""
    lineas = []
    for o in oficios_habilitados().values():
        for code, label in o["especialidades"].items():
            lineas.append(f"- {code}: {label} ({o['label']})")
    return "\n".join(lineas)
