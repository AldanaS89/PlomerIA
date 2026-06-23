"""
Pruebas UNITARIAS del registro de oficios (services/oficios.py).

Son de CAJA BLANCA: conocemos el código y diseñamos casos según su lógica
(qué oficios están habilitados, cómo se detecta por palabras clave, etc.).
No tocan base de datos ni red → son rápidas y aisladas.

Correr con:   pytest
"""
from services import oficios


# ── oficios habilitados ───────────────────────────────────────────────
def test_solo_plomeria_habilitada():
    habilitados = oficios.oficios_habilitados()
    assert "PLOMERIA" in habilitados
    assert "ELECTRICIDAD" not in habilitados   # definida pero inhabilitada
    assert "CERRAJERIA" not in habilitados


# ── especialidades válidas ────────────────────────────────────────────
def test_especialidades_solo_habilitadas():
    esp = oficios.especialidades_validas()  # solo habilitados (default)
    assert "PLOMERIA_GENERAL" in esp
    assert "DESTAPES" in esp
    assert "ELEC_GENERAL" not in esp         # electricidad está inhabilitada


def test_especialidades_incluyendo_inhabilitadas():
    esp = oficios.especialidades_validas(solo_habilitados=False)
    assert "ELEC_GENERAL" in esp
    assert "CERR_GENERAL" in esp


# ── rangos de presupuesto ─────────────────────────────────────────────
def test_rango_conocido():
    assert oficios.rango_presupuesto("DESTAPES") == (15000.0, 45000.0)


def test_rango_inexistente_devuelve_default():
    default = (1.0, 2.0)
    assert oficios.rango_presupuesto("NO_EXISTE", default=default) == default


# ── oficio de una especialidad ────────────────────────────────────────
def test_oficio_de_especialidad_plomeria():
    assert oficios.oficio_de_especialidad("OBRA") == "PLOMERIA"


def test_oficio_de_especialidad_otra():
    assert oficios.oficio_de_especialidad("TABLEROS") == "ELECTRICIDAD"


def test_oficio_de_especialidad_inexistente():
    assert oficios.oficio_de_especialidad("NO_EXISTE") is None


# ── detección por palabras clave (fallback) ───────────────────────────
def test_detectar_plomeria():
    assert oficios.detectar_oficio("se me tapó el caño y gotea el inodoro") == "PLOMERIA"


def test_detectar_sin_pistas():
    assert oficios.detectar_oficio("hola, una consulta general") is None


def test_detectar_oficio_inhabilitado_no_se_devuelve():
    # Habla de electricidad, pero ese oficio está INHABILITADO → no se sugiere.
    assert oficios.detectar_oficio("se cortó la luz, hay un cortocircuito") is None


# ── guía para el prompt de la IA ──────────────────────────────────────
def test_guia_ia_solo_habilitados():
    guia = oficios.guia_especialidades_ia()
    assert "PLOMERIA_GENERAL" in guia
    assert "ELEC_GENERAL" not in guia   # no se ofrece lo inhabilitado
