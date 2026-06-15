// src/components/DireccionConMapa.jsx
// Componente reutilizable para selección de dirección con autocomplete y mapa
// Usado en: Registro.jsx (cliente) y RegistroPlomero.jsx (profesional)

import { useState, useEffect, useRef, useCallback } from "react";
import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Fix para el ícono del marker en Leaflet con Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
  iconUrl:       "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
  shadowUrl:     "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
});

// Centroide zona sur GBA — fallback si no hay coordenadas
const DEFAULT_LAT = -34.8116;
const DEFAULT_LON = -58.3967;

// Componente interno que mueve el mapa cuando cambian las coordenadas
function MapController({ lat, lon }) {
  const map = useMap();
  useEffect(() => {
    if (lat && lon) {
      map.setView([lat, lon], 15, { animate: true });
    }
  }, [lat, lon, map]);
  return null;
}

// Componente interno que detecta clicks en el mapa
function MapClickHandler({ onLocationSelect }) {
  useMapEvents({
    click(e) {
      onLocationSelect(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

export default function DireccionConMapa({
  direccion,
  localidad,
  latitud,
  longitud,
  onDireccionChange,
  onLocalidadChange,
  onCoordsChange,
  error,
  labelDireccion = "Dirección",
  labelLocalidad = "Localidad",
  localidades = [],
}) {
  const [sugerencias,    setSugerencias]    = useState([]);
  const [buscando,       setBuscando]       = useState(false);
  const [mostrarMapa,    setMostrarMapa]    = useState(false);
  const [coords,         setCoords]         = useState({
    lat: latitud  || DEFAULT_LAT,
    lon: longitud || DEFAULT_LON,
  });
  const [confirmado,     setConfirmado]     = useState(false);
  const debounceRef = useRef(null);

  // Buscar sugerencias en Nominatim cuando el usuario escribe
  const buscarSugerencias = useCallback(async (texto) => {
    if (texto.length < 4) { setSugerencias([]); return; }

    setBuscando(true);
    try {
      const q = encodeURIComponent(`${texto}, ${localidad || "Buenos Aires"}, Argentina`);
      const res = await fetch(
        `https://nominatim.openstreetmap.org/search?q=${q}&format=json&limit=5&countrycodes=ar&addressdetails=1`,
        { headers: { "Accept-Language": "es" } }
      );
      const data = await res.json();
      setSugerencias(data);
    } catch {
      setSugerencias([]);
    } finally {
      setBuscando(false);
    }
  }, [localidad]);

  const handleDireccionInput = (valor) => {
    onDireccionChange(valor);
    setConfirmado(false);
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => buscarSugerencias(valor), 500);
  };

  const elegirSugerencia = (sug) => {
    const lat = parseFloat(sug.lat);
    const lon = parseFloat(sug.lon);
    // Extraer dirección legible
    const addr = sug.address;
    const calle = addr.road || addr.pedestrian || "";
    const numero = addr.house_number || "";
    const dirLegible = numero ? `${calle} ${numero}` : calle || sug.display_name.split(",")[0];
    const localidadDetectada = addr.suburb || addr.city_district || addr.town || addr.village || "";

    onDireccionChange(dirLegible);
    if (localidadDetectada && localidades.includes(localidadDetectada)) {
      onLocalidadChange(localidadDetectada);
    }
    setCoords({ lat, lon });
    onCoordsChange(lat, lon);
    setSugerencias([]);
    setMostrarMapa(true);
    setConfirmado(true);
  };

  const handlePinMove = (lat, lon) => {
    setCoords({ lat, lon });
    onCoordsChange(lat, lon);
  };

  const confirmarUbicacion = () => {
    setConfirmado(true);
    setMostrarMapa(false);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>

      {/* Campo dirección con autocomplete */}
      <div>
        <label style={{
          display: "block", fontSize: "12px", fontWeight: "700",
          color: "#64748B", textTransform: "uppercase", letterSpacing: "0.6px",
          marginBottom: "6px", fontFamily: "'DM Sans',sans-serif",
        }}>
          {labelDireccion}
        </label>
        <div style={{ position: "relative" }}>
          <input
            type="text"
            placeholder="Ej: Av. Mitre 1234"
            value={direccion}
            onChange={(e) => handleDireccionInput(e.target.value)}
            style={{
              width: "100%", padding: "12px 40px 12px 14px",
              border: `1.5px solid ${error ? "#FCA5A5" : confirmado ? "#86EFAC" : "#E2E8F0"}`,
              borderRadius: "12px", fontSize: "14px", outline: "none",
              fontFamily: "'DM Sans',sans-serif", boxSizing: "border-box",
              background: error ? "#FFF5F5" : confirmado ? "#F0FDF4" : "#F8FAFC",
              transition: "all 0.2s",
            }}
          />
          <div style={{
            position: "absolute", right: "12px", top: "50%",
            transform: "translateY(-50%)", fontSize: "16px",
          }}>
            {buscando ? "⏳" : confirmado ? "✅" : "📍"}
          </div>

          {/* Lista de sugerencias */}
          {sugerencias.length > 0 && (
            <div style={{
              position: "absolute", top: "100%", left: 0, right: 0,
              background: "#fff", border: "1.5px solid #E2E8F0",
              borderRadius: "12px", boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
              zIndex: 1000, overflow: "hidden", marginTop: "4px",
            }}>
              {sugerencias.map((s, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => elegirSugerencia(s)}
                  style={{
                    width: "100%", padding: "10px 14px", textAlign: "left",
                    border: "none", borderBottom: i < sugerencias.length - 1 ? "1px solid #F1F5F9" : "none",
                    background: "transparent", cursor: "pointer",
                    fontFamily: "'DM Sans',sans-serif", fontSize: "13px",
                    color: "#0F172A", lineHeight: "1.4",
                    transition: "background 0.15s",
                  }}
                  onMouseEnter={(e) => e.target.style.background = "#F8FAFC"}
                  onMouseLeave={(e) => e.target.style.background = "transparent"}
                >
                  <div style={{ fontWeight: "600" }}>
                    {s.address?.road || s.display_name.split(",")[0]}
                    {s.address?.house_number ? ` ${s.address.house_number}` : ""}
                  </div>
                  <div style={{ fontSize: "11px", color: "#94A3B8", marginTop: "2px" }}>
                    {s.display_name.split(",").slice(1, 4).join(",")}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
        {error && (
          <p style={{ color: "#EF4444", fontSize: "12px", marginTop: "4px",
            fontFamily: "'DM Sans',sans-serif" }}>⚠ {error}</p>
        )}
      </div>

      {/* Selector de localidad */}
      {localidades.length > 0 && (
        <div>
          <label style={{
            display: "block", fontSize: "12px", fontWeight: "700",
            color: "#64748B", textTransform: "uppercase", letterSpacing: "0.6px",
            marginBottom: "6px", fontFamily: "'DM Sans',sans-serif",
          }}>
            {labelLocalidad}
          </label>
          <select
            value={localidad}
            onChange={(e) => onLocalidadChange(e.target.value)}
            style={{
              width: "100%", padding: "12px 14px",
              border: "1.5px solid #E2E8F0", borderRadius: "12px",
              fontSize: "14px", outline: "none", background: "#F8FAFC",
              fontFamily: "'DM Sans',sans-serif", boxSizing: "border-box",
            }}
          >
            <option value="">Seleccioná tu localidad</option>
            {localidades.map((l) => <option key={l} value={l}>{l}</option>)}
          </select>
        </div>
      )}

      {/* Botón para abrir/cerrar el mapa */}
      <button
        type="button"
        onClick={() => setMostrarMapa((v) => !v)}
        style={{
          display: "flex", alignItems: "center", gap: "8px",
          background: mostrarMapa ? "#EFF6FF" : "#F8FAFC",
          border: `1.5px solid ${mostrarMapa ? "#BFDBFE" : "#E2E8F0"}`,
          borderRadius: "10px", padding: "9px 14px", cursor: "pointer",
          fontFamily: "'DM Sans',sans-serif", fontSize: "13px",
          color: mostrarMapa ? "#1D4ED8" : "#475569", fontWeight: "600",
          transition: "all 0.2s",
        }}
      >
        🗺️ {mostrarMapa ? "Ocultar mapa" : "Ver y confirmar ubicación en el mapa"}
        {confirmado && !mostrarMapa && (
          <span style={{ marginLeft: "auto", color: "#22C55E", fontSize: "12px" }}>
            ✓ Ubicación confirmada
          </span>
        )}
      </button>

      {/* Mapa interactivo */}
      {mostrarMapa && (
        <div style={{ borderRadius: "14px", overflow: "hidden",
          border: "1.5px solid #BFDBFE", boxShadow: "0 4px 16px rgba(59,130,246,0.1)" }}>

          <div style={{
            background: "#EFF6FF", padding: "10px 14px",
            fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
            color: "#1D4ED8", fontWeight: "600",
            borderBottom: "1px solid #BFDBFE",
          }}>
            📍 Arrastrá el pin o hacé clic en el mapa para ajustar la ubicación exacta
          </div>

          <div style={{ height: "280px" }}>
            <MapContainer
              center={[coords.lat, coords.lon]}
              zoom={15}
              style={{ height: "100%", width: "100%" }}
              scrollWheelZoom={false}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <MapController lat={coords.lat} lon={coords.lon} />
              <MapClickHandler onLocationSelect={handlePinMove} />
              <Marker
                position={[coords.lat, coords.lon]}
                draggable={true}
                eventHandlers={{
                  dragend(e) {
                    const { lat, lng } = e.target.getLatLng();
                    handlePinMove(lat, lng);
                  },
                }}
              />
            </MapContainer>
          </div>

          <div style={{
            background: "#F8FAFC", padding: "12px 14px",
            display: "flex", justifyContent: "space-between",
            alignItems: "center", borderTop: "1px solid #E2E8F0",
          }}>
            <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "11px", color: "#94A3B8" }}>
              Lat: {coords.lat.toFixed(6)} · Lon: {coords.lon.toFixed(6)}
            </div>
            <button
              type="button"
              onClick={confirmarUbicacion}
              style={{
                background: "linear-gradient(135deg,#22C55E,#16A34A)",
                border: "none", borderRadius: "8px", padding: "8px 16px",
                fontFamily: "'DM Sans',sans-serif", fontSize: "13px",
                color: "#fff", fontWeight: "700", cursor: "pointer",
                boxShadow: "0 2px 8px rgba(34,197,94,0.3)",
              }}
            >
              ✓ Confirmar ubicación
            </button>
          </div>
        </div>
      )}
    </div>
  );
}