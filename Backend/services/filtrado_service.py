# services/filtrado_service.py
"""
Responsabilidad única: encontrar los plomeros adecuados para una solicitud.
Encapsula toda la lógica de filtrado y fallbacks.
"""
from sqlalchemy.orm import Session
from repositories import plomero_repository

MAX_PLOMEROS = 5

class FiltradoService:

    def obtener_plomeros_para_solicitud(
        self,
        db:                Session,
        etiqueta:          str,
        lat:               float | None,
        lon:               float | None,
        es_urgente:        bool,
        ids_seleccionados: list[int] | None = None,
    ) -> list:
        """
        Estrategia de filtrado con 3 niveles de fallback:
        1. IDs seleccionados por el cliente (si los hay)
        2. Plomeros por especialidad + distancia
        3. Cualquier plomero disponible cerca
        """
        # Nivel 1 — cliente eligió plomeros específicos
        if ids_seleccionados:
            return [
                p for pid in ids_seleccionados
                if (p := plomero_repository.buscar_por_id(db, pid))
            ]

        # Nivel 2 — filtrado automático por especialidad + distancia
        plomeros = plomero_repository.buscar_para_solicitud(
            db,
            especialidades    = etiqueta,
            lat_usuario       = lat,
            lon_usuario       = lon,
            atiende_urgencias = es_urgente,
            limite            = MAX_PLOMEROS,
        )
        if plomeros:
            return plomeros

        # Nivel 3 — cualquier disponible cerca (sin filtro de especialidad)
        return plomero_repository.buscar_para_solicitud(
            db,
            lat_usuario = lat,
            lon_usuario = lon,
            limite      = MAX_PLOMEROS,
        )

filtrado_service = FiltradoService()