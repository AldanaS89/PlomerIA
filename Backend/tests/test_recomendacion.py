"""
Pruebas UNITARIAS del orden de recomendación
(services/plomero_service.ordenar_por_cercania_y_puntuacion).

Caja blanca. Verifica la regla que a mano es casi imposible de comprobar (¿el
orden de 5 plomeros es EXACTAMENTE el correcto?). Ya tuvimos un bug donde no se
completaban los 5 y no priorizaba bien la cercanía.

Regla de orden: 1° cercanía por tramos (<5 / 5–10 / >10 km), 2° relevancia,
3° puntuación, 4° distancia exacta. Devuelve como mucho `limite` resultados.

Usamos "plomeros simulados" (objetos falsos) para no depender de la base.

Correr con:   pytest
"""
from services.plomero_service import ordenar_por_cercania_y_puntuacion


class FakePlomero:
    """Plomero mínimo para la prueba: solo lo que usa la función de orden."""
    def __init__(self, id_, distancia, puntuacion):
        self.id_plomero = id_
        self.distancia = distancia
        self.puntuacion = puntuacion


def _dist(p):
    return p.distancia


def _sin_relevancia(p):
    return 0


def test_la_cercania_gana_a_la_puntuacion():
    # Un plomero lejano (8 km) con 5★ NO debe ganarle a los cercanos con menos ★.
    cerca_a = FakePlomero("cerca_4.0", 2, 4.0)
    lejos   = FakePlomero("lejos_5.0", 8, 5.0)
    cerca_b = FakePlomero("cerca_4.5", 1, 4.5)
    orden = ordenar_por_cercania_y_puntuacion([cerca_a, lejos, cerca_b], _dist, _sin_relevancia)
    assert [p.id_plomero for p in orden] == ["cerca_4.5", "cerca_4.0", "lejos_5.0"]


def test_dentro_del_mismo_tramo_gana_la_puntuacion():
    bajo = FakePlomero("p_4.0", 2, 4.0)
    alto = FakePlomero("p_4.5", 3, 4.5)   # mismo tramo (<5 km), más puntuación
    orden = ordenar_por_cercania_y_puntuacion([bajo, alto], _dist, _sin_relevancia)
    assert orden[0].id_plomero == "p_4.5"


def test_completa_hasta_5_y_no_mas():
    pool = [FakePlomero(f"p{i}", i, 4.0) for i in range(8)]
    orden = ordenar_por_cercania_y_puntuacion(pool, _dist, _sin_relevancia, limite=5)
    assert len(orden) == 5


def test_relevancia_desempata_en_el_tramo():
    # Mismo tramo y misma puntuación: el más "relevante" (urgencia + disponible) va primero.
    comun    = FakePlomero("comun", 2, 4.0)
    relevante = FakePlomero("relevante", 2, 4.0)
    rel = lambda p: 5 if p.id_plomero == "relevante" else 0
    orden = ordenar_por_cercania_y_puntuacion([comun, relevante], _dist, rel)
    assert orden[0].id_plomero == "relevante"
