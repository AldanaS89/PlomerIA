from math import radians, sin, cos, sqrt, atan2


from math import cos

RADIO_KM = 5.0
def distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def geocodificar(direccion: str, localidad: str) -> tuple[float, float]:
    try:
        from geopy.geocoders import Nominatim
        geolocator = Nominatim(user_agent="plomeria_app_v1")
        query = f"{direccion}, {localidad}, Buenos Aires, Argentina"
        location = geolocator.geocode(query, timeout=5)
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        print(f"[auth_service] Geopy falló, usando fallback: {e}")
    return -34.8116, -58.3967  # centroide Almirante Brown