# services/material_service.py
from fastapi import HTTPException

from models.material import MaterialItem
from models.solicitud import EstadoSolicitud
from repositories import material_repository, solicitud_repository
from schemas.material import MaterialResponse

# El plomero puede editar la boleta mientras el trabajo está activo.
ESTADOS_EDITABLES = {
    EstadoSolicitud.EN_PROGRESO,
    EstadoSolicitud.EN_CAMINO,
}


def _serializar(db, id_solicitud):
    items = material_repository.listar_por_solicitud(db, id_solicitud)
    total = material_repository.total_por_solicitud(db, id_solicitud)
    return {
        "items": [MaterialResponse.model_validate(i) for i in items],
        "total": round(total, 2),
    }


def listar(db, id_solicitud, actor):
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    # Solo el cliente dueño o el plomero asignado pueden ver la boleta
    if actor["id"] not in [solicitud.id_usuario, solicitud.id_plomero]:
        raise HTTPException(status_code=403, detail="No autorizado")
    return _serializar(db, id_solicitud)


def agregar(db, id_solicitud, datos, id_plomero):
    solicitud = solicitud_repository.obtener_por_id(db, id_solicitud)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    if solicitud.id_plomero != id_plomero:
        raise HTTPException(status_code=403, detail="No autorizado")
    if solicitud.estado not in ESTADOS_EDITABLES:
        raise HTTPException(status_code=400, detail="La boleta solo se edita mientras el trabajo está en curso")
    if not (datos.descripcion or "").strip():
        raise HTTPException(status_code=400, detail="La descripción del material es obligatoria")

    item = MaterialItem(
        id_solicitud=id_solicitud,
        descripcion=datos.descripcion.strip(),
        cantidad=datos.cantidad or 1.0,
        precio=datos.precio or 0.0,
    )
    material_repository.crear(db, item)
    return _serializar(db, id_solicitud)


def eliminar(db, id_item, id_plomero):
    item = material_repository.obtener(db, id_item)
    if not item:
        raise HTTPException(status_code=404, detail="Ítem no encontrado")
    solicitud = solicitud_repository.obtener_por_id(db, item.id_solicitud)
    if not solicitud or solicitud.id_plomero != id_plomero:
        raise HTTPException(status_code=403, detail="No autorizado")
    if solicitud.estado not in ESTADOS_EDITABLES:
        raise HTTPException(status_code=400, detail="La boleta ya no se puede editar")
    id_solicitud = item.id_solicitud
    material_repository.eliminar(db, item)
    return _serializar(db, id_solicitud)
