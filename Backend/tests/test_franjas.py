"""
Pruebas UNITARIAS de la franja horaria (services/plomero_service._franja_de_hora).

Caja blanca: probamos cada rama y los CASOS BORDE (los límites 12 y 17, que es
donde más fácil se cuela un bug por usar < en vez de <=).

Correr con:   pytest
"""
from services.plomero_service import _franja_de_hora


def test_manana():
    assert _franja_de_hora(8) == "manana"
    assert _franja_de_hora(10) == "manana"


def test_tarde():
    assert _franja_de_hora(13) == "tarde"
    assert _franja_de_hora(16) == "tarde"


def test_noche():
    assert _franja_de_hora(18) == "noche"
    assert _franja_de_hora(22) == "noche"


# ── Casos borde (los límites de cada franja) ──────────────────────────
def test_borde_mediodia_es_manana():
    assert _franja_de_hora(12) == "manana"   # 12 cae en mañana


def test_borde_17_es_tarde():
    assert _franja_de_hora(17) == "tarde"    # 17 cae en tarde


def test_borde_18_es_noche():
    assert _franja_de_hora(18) == "noche"    # 18 ya es noche
