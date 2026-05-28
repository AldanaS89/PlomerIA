# services/filtrado_service.py
"""
Responsabilidad única: encontrar los profesionales adecuados para una solicitud.
Implementa 3 niveles de fallback por radio de distancia.
El filtro de género aplica en todos los niveles si está activo.
"""
from sqlalchemy.orm import Session
from repositories import plomero_repository
from repositories.plomero_repository import RADIO_KM_1, RADIO_KM_2

MAX_PLOMEROS = 5


class FiltradoService:

    def obtener_plomeros_para_solicitud(
        self,
        db:                Session,
        etiqueta:          str,
        lat:               float | None,
        lon:               float | None,
        es_urgente:        bool,
        genero:            str | None = None,
        ids_seleccionados: list[int] | None = None,
    ) -> list:
        """
        Estrategia de filtrado con 3 niveles de fallback por radio:

        Nivel 0 — IDs elegidos por el cliente (si los hay)
        Nivel 1 — Radio 5km + especialidad + urgencia + género
        Nivel 2 — Radio 10km + especialidad + urgencia + género
        Nivel 3 — Sin límite de radio + especialidad + urgencia + género
        Nivel 4 — Sin límite de radio, sin filtro de especialidad + género
                  (último recurso)

        Si en ningún nivel hay resultados devuelve lista vacía.
        """

        # Nivel 0 — cliente eligió plomeros específicos
        if ids_seleccionados:
            return [
                p for pid in ids_seleccionados
                if (p := plomero_repository.buscar_por_id(db, pid))
            ]

        # Argumentos comunes a todos los niveles
        base = dict(
            especialidades    = etiqueta,
            atiende_urgencias = es_urgente,
            genero            = genero,
            limite            = MAX_PLOMEROS,
        )

        # Nivel 1 — 5km
        plomeros = plomero_repository.buscar_para_solicitud(
            db, **base, lat_usuario=lat, lon_usuario=lon, radio_km=RADIO_KM_1
        )
        if plomeros:
            return plomeros

        # Nivel 2 — 10km
        plomeros = plomero_repository.buscar_para_solicitud(
            db, **base, lat_usuario=lat, lon_usuario=lon, radio_km=RADIO_KM_2
        )
        if plomeros:
            return plomeros

        # Nivel 3 — sin límite de radio
        plomeros = plomero_repository.buscar_para_solicitud(
            db, **base, lat_usuario=lat, lon_usuario=lon, radio_km=None
        )
        if plomeros:
            return plomeros

        # Nivel 4 — último recurso: sin especialidad, sin límite
        return plomero_repository.buscar_para_solicitud(
            db,
            atiende_urgencias = es_urgente,
            genero            = genero,
            lat_usuario       = lat,
            lon_usuario       = lon,
            radio_km          = None,
            limite            = MAX_PLOMEROS,
        )


filtrado_service = FiltradoService()