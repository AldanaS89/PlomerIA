"""
Pruebas UNITARIAS de la validación de la boleta de materiales
(services/material_service._validar_item).

Caja blanca + pruebas NEGATIVAS: confirman que un ítem inválido (precio
negativo, cantidad 0 o negativa, descripción vacía) sea RECHAZADO con error
400 y no se guarde. Justo el caso que a mano podría escaparse.

Correr con:   pytest
"""
import pytest
from fastapi import HTTPException
from services.material_service import _validar_item


def test_item_valido_no_lanza():
    # Un ítem correcto no debe lanzar ninguna excepción.
    _validar_item("Caño de PVC", 2, 1500.0)


def test_precio_negativo_rechazado():
    with pytest.raises(HTTPException) as exc:
        _validar_item("Caño", 1, -100.0)
    assert exc.value.status_code == 400


def test_cantidad_cero_rechazada():
    with pytest.raises(HTTPException):
        _validar_item("Caño", 0, 100.0)


def test_cantidad_negativa_rechazada():
    with pytest.raises(HTTPException):
        _validar_item("Caño", -3, 100.0)


def test_descripcion_vacia_rechazada():
    with pytest.raises(HTTPException):
        _validar_item("   ", 1, 100.0)


def test_precio_cero_permitido():
    # Precio 0 es válido (por ejemplo, un ítem sin costo / incluido).
    _validar_item("Mano de obra incluida", 1, 0.0)
