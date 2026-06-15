"""
Pruebas UNITARIAS del filtro de groserías (services/moderacion.censurar).

Caja blanca. La censura es una función pura (texto → texto), perfecta para
probar: que reemplace la palabra completa por asteriscos, que avise si hubo
groserías, y que NO toque palabras limpias (ni siquiera las parecidas).

Correr con:   pytest
"""
from services.moderacion import censurar


def test_censura_una_groseria():
    texto, hubo = censurar("sos un boludo")
    assert texto == "sos un ******"   # misma cantidad de asteriscos que letras
    assert hubo is True


def test_no_toca_texto_limpio():
    texto, hubo = censurar("hola, necesito que vengas a las 10")
    assert texto == "hola, necesito que vengas a las 10"
    assert hubo is False


def test_es_insensible_a_mayusculas():
    texto, hubo = censurar("BOLUDO no vengas")
    assert texto == "****** no vengas"
    assert hubo is True


def test_censura_varias():
    texto, hubo = censurar("no seas idiota, forro")
    assert texto == "no seas ******, *****"
    assert hubo is True


def test_palabra_parecida_no_se_censura():
    # 'boludazo' no está en la lista: solo se censura la palabra EXACTA.
    texto, hubo = censurar("sos un boludazo")
    assert hubo is False
    assert texto == "sos un boludazo"


def test_texto_vacio():
    assert censurar("") == ("", False)
    assert censurar(None) == (None, False)
