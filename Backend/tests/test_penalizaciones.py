"""
Pruebas UNITARIAS de la penalización automática por cancelación
(services/calificacion_service._estrellas_automaticas).

Caja blanca: las 4 combinaciones de la regla (comunicación × tiempo) más el
caso sin fecha. El valor exacto de estrellas es imposible de verificar a ojo
probando manualmente — acá queda fijado. (Ya tuvimos un bug en este cálculo.)

Regla:
  | Tiempo        | sin comunicación | con comunicación |
  | Más de 24 h   | 1.0 ⭐           | 2.0 ⭐           |
  | 24 h o menos  | 0.5 ⭐           | 1.5 ⭐           |

Correr con:   pytest
"""
from services.calificacion_service import _estrellas_automaticas


def test_menos_24h_sin_comunicacion():
    assert _estrellas_automaticas(10, hubo_msg=False) == 0.5


def test_menos_24h_con_comunicacion():
    assert _estrellas_automaticas(10, hubo_msg=True) == 1.5


def test_mas_24h_sin_comunicacion():
    assert _estrellas_automaticas(48, hubo_msg=False) == 1.0


def test_mas_24h_con_comunicacion():
    assert _estrellas_automaticas(48, hubo_msg=True) == 2.0


def test_borde_exactamente_24h_cuenta_como_menos():
    # CASO BORDE: 24 h exactas cuentan como "24 o menos".
    assert _estrellas_automaticas(24, hubo_msg=True) == 1.5


def test_sin_fecha_de_trabajo():
    # Si no se pudo calcular el tiempo (horas=None), se trata como "24 o menos".
    assert _estrellas_automaticas(None, hubo_msg=False) == 0.5
