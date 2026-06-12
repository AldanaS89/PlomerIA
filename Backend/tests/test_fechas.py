"""
Pruebas UNITARIAS del cálculo de la fecha del trabajo
(services/solicitud_service._calcular_fecha_trabajo).

Caja blanca, enfocada en los CASOS BORDE de fechas, que es donde se esconden
los bugs más difíciles de ver a mano (de hecho ya tuvimos uno: el día de HOY
se iba a la semana siguiente).

Convierte un turno tipo "Mié_manana_8" en la próxima fecha concreta (hoy o
posterior) que cae en ese día de la semana, con esa hora.

Correr con:   pytest
"""
from datetime import datetime
from services.solicitud_service import _calcular_fecha_trabajo

# Índice = weekday() de Python (lunes=0 ... domingo=6)
ABBR_POR_WEEKDAY = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
WEEKDAY_ESPERADO = {"Lun": 0, "Mar": 1, "Mié": 2, "Jue": 3, "Vie": 4, "Sáb": 5, "Dom": 6}


def test_dia_y_hora_correctos():
    f = _calcular_fecha_trabajo("Mié_manana_8")
    assert f.weekday() == WEEKDAY_ESPERADO["Mié"]   # cae miércoles
    assert f.hour == 8                               # con la hora pedida


def test_distintas_franjas_horas():
    assert _calcular_fecha_trabajo("Vie_tarde_14").hour == 14
    assert _calcular_fecha_trabajo("Sáb_noche_18").hour == 18


def test_nunca_en_el_pasado():
    # Para cualquier día válido, la fecha calculada es hoy o futura.
    for abbr in ABBR_POR_WEEKDAY:
        f = _calcular_fecha_trabajo(f"{abbr}_manana_9")
        assert f.date() >= datetime.now().date()


def test_hoy_es_hoy():
    # CASO BORDE: si el turno cae en el día de HOY, debe ser HOY (no la semana que viene).
    hoy_abbr = ABBR_POR_WEEKDAY[datetime.now().weekday()]
    f = _calcular_fecha_trabajo(f"{hoy_abbr}_manana_10")
    assert f.date() == datetime.now().date()


def test_turno_invalido_devuelve_none():
    assert _calcular_fecha_trabajo("cualquier_cosa") is None
    assert _calcular_fecha_trabajo("") is None
    assert _calcular_fecha_trabajo(None) is None
