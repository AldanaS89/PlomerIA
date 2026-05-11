import { useState, useEffect, useCallback, useRef } from "react";
import api from "../services/api";           // axios instance con interceptor de token
import { useAuthStore } from "../store/authStore"; // zustand store

// ─── CONSTANTS ───────────────────────────────────────────────────────────────

const BADGE_STYLES = {
  Destapes:       { bg: "#E0F2FE", text: "#0369A1" },
  Urgencias:      { bg: "#FEE2E2", text: "#B91C1C" },
  "Obra general": { bg: "#DCFCE7", text: "#15803D" },
  Instalaciones:  { bg: "#F3E8FF", text: "#7E22CE" },
  DESTAPES:       { bg: "#E0F2FE", text: "#0369A1" },
  URGENCIAS:      { bg: "#FEE2E2", text: "#B91C1C" },
  OBRA:           { bg: "#DCFCE7", text: "#15803D" },
  INSTALACIONES:  { bg: "#F3E8FF", text: "#7E22CE" },
};

const URGENCIA_KEYWORDS = ["inunda", "pérdida", "perder", "no cierra", "roto", "explota", "revienta", "urgente", "emergencia"];

// ─── SHARED COMPONENTS ───────────────────────────────────────────────────────

function Stars({ val = 0, size = 13, interactive = false, onRate }) {
  return (
    <div style={{ display: "flex", gap: "2px", alignItems: "center" }}>
      {[1, 2, 3, 4, 5].map(i => {
        const full = i <= Math.floor(val);
        const half = !full && i - 0.5 <= val;
        return (
          <svg key={i} width={size} height={size} viewBox="0 0 24 24"
            onClick={() => interactive && onRate && onRate(i)}
            style={{ cursor: interactive ? "pointer" : "default" }}>
            <defs>
              <linearGradient id={`hg${i}${size}`}>
                <stop offset="50%" stopColor="#FBBF24" />
                <stop offset="50%" stopColor="#E5E7EB" />
              </linearGradient>
            </defs>
            <polygon
              points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"
              fill={half ? `url(#hg${i}${size})` : full ? "#FBBF24" : "#E5E7EB"}
            />
          </svg>
        );
      })}
    </div>
  );
}

function Badge({ label }) {
  const s = BADGE_STYLES[label] || { bg: "#F3F4F6", text: "#374151" };
  return (
    <span style={{
      background: s.bg, color: s.text, fontSize: "11px", fontWeight: "600",
      padding: "3px 10px", borderRadius: "20px",
      fontFamily: "'DM Sans',sans-serif", whiteSpace: "nowrap",
    }}>{label}</span>
  );
}

function Avatar({ src, nombre, apellido, size = 52 }) {
  const [err, setErr] = useState(false);
  const fullSrc = src && !src.startsWith("http") ? `http://localhost:8000/${src}` : src;
  if (fullSrc && !err) return (
    <img src={fullSrc} alt="" onError={() => setErr(true)}
      style={{ width: size, height: size, borderRadius: "14px", objectFit: "cover",
        boxShadow: "0 2px 8px rgba(0,0,0,0.12)", flexShrink: 0 }} />
  );
  return (
    <div style={{
      width: size, height: size, borderRadius: "14px", flexShrink: 0,
      background: "linear-gradient(135deg,#3B82F6,#2563EB)",
      display: "flex", alignItems: "center", justifyContent: "center",
      fontSize: size * 0.32, fontWeight: "800", color: "#fff",
      fontFamily: "'DM Sans',sans-serif",
    }}>{nombre?.[0]}{apellido?.[0]}</div>
  );
}

function Spinner({ size = 24, color = "#3B82F6" }) {
  return (
    <div style={{
      width: size, height: size, border: `3px solid #E2E8F0`,
      borderTop: `3px solid ${color}`, borderRadius: "50%",
      animation: "spin 0.7s linear infinite",
    }} />
  );
}

function ErrorBanner({ msg, onClose }) {
  if (!msg) return null;
  return (
    <div style={{
      background: "#FEF2F2", border: "1.5px solid #FECACA", borderRadius: "12px",
      padding: "12px 16px", marginBottom: "16px",
      display: "flex", justifyContent: "space-between", alignItems: "center",
      fontFamily: "'DM Sans',sans-serif", fontSize: "13px", color: "#B91C1C",
    }}>
      <span>⚠️ {msg}</span>
      {onClose && <button onClick={onClose} style={{ background: "none", border: "none",
        cursor: "pointer", color: "#B91C1C", fontWeight: "700", fontSize: "16px" }}>×</button>}
    </div>
  );
}

// ─── HEADER ──────────────────────────────────────────────────────────────────

function Header({ screen, onNav, notifCount, onLogout, user }) {
  const tabs = [
    { key: "problema",      label: "Inicio",       icon: "🏠" },
    { key: "historial",     label: "Mis trabajos", icon: "📋" },
    { key: "notificaciones",label: "Alertas",      icon: "🔔", badge: notifCount },
  ];
  return (
    <div style={{
      background: "linear-gradient(135deg,#0F172A,#1E3A5F)",
      padding: "0 24px", position: "sticky", top: 0, zIndex: 100,
    }}>
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        paddingTop: "14px", paddingBottom: "10px",
        borderBottom: "1px solid rgba(255,255,255,0.08)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div style={{
            background: "linear-gradient(135deg,#3B82F6,#06B6D4)",
            borderRadius: "10px", width: "34px", height: "34px",
            display: "flex", alignItems: "center", justifyContent: "center", fontSize: "16px",
          }}>🔧</div>
          <span style={{ fontWeight: "800", fontSize: "20px", color: "#fff",
            letterSpacing: "-0.4px", fontFamily: "'DM Sans',sans-serif" }}>
            Plomer<span style={{ color: "#38BDF8" }}>IA</span>
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span style={{ color: "#94A3B8", fontSize: "13px", fontFamily: "'DM Sans',sans-serif" }}>
            {user?.nombre}
          </span>
          <button onClick={onLogout} style={{
            background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.25)",
            borderRadius: "8px", padding: "5px 12px", color: "#FCA5A5",
            fontSize: "12px", fontWeight: "600", cursor: "pointer",
            fontFamily: "'DM Sans',sans-serif",
          }}>Cerrar sesión</button>
        </div>
      </div>
      <div style={{ display: "flex", gap: "4px" }}>
        {tabs.map(t => (
          <button key={t.key} onClick={() => onNav(t.key)} style={{
            background: "transparent", border: "none", cursor: "pointer",
            padding: "10px 16px", display: "flex", alignItems: "center", gap: "6px",
            fontFamily: "'DM Sans',sans-serif", fontSize: "13px", fontWeight: "600",
            color: screen === t.key ? "#38BDF8" : "#64748B",
            borderBottom: screen === t.key ? "2px solid #38BDF8" : "2px solid transparent",
            transition: "all 0.18s", position: "relative", whiteSpace: "nowrap",
          }}>
            <span>{t.icon}</span>
            <span>{t.label}</span>
            {t.badge > 0 && (
              <div style={{
                background: "#EF4444", color: "#fff", borderRadius: "10px",
                fontSize: "10px", fontWeight: "800", padding: "1px 6px", minWidth: "16px",
              }}>{t.badge}</div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}

// ─── SCREEN: PROBLEMA ────────────────────────────────────────────────────────

function ScreenProblema({ onBuscar }) {
  const [texto, setTexto] = useState("");
  const [urgencia, setUrgencia] = useState(false);

  const handleChange = (v) => {
    setTexto(v);
    setUrgencia(URGENCIA_KEYWORDS.some(k => v.toLowerCase().includes(k)));
  };

  return (
    <div style={{ maxWidth: "640px", margin: "0 auto", padding: "60px 24px" }}>
      <div style={{ marginBottom: "32px" }}>
        <h1 style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
          fontSize: "28px", color: "#0F172A", letterSpacing: "-0.5px", margin: "0 0 8px" }}>
          ¿Qué problema tenés?
        </h1>
        <p style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "15px",
          color: "#64748B", margin: 0 }}>
          Describilo y te mostramos los mejores plomeros cerca tuyo.
        </p>
      </div>

      <div style={{
        background: "#fff", borderRadius: "20px",
        border: "2px solid #F1F5F9", padding: "24px",
        boxShadow: "0 4px 24px rgba(0,0,0,0.06)",
      }}>
        <label style={{
          fontFamily: "'DM Sans',sans-serif", fontWeight: "700",
          fontSize: "13px", color: "#475569",
          textTransform: "uppercase", letterSpacing: "0.6px",
          display: "block", marginBottom: "10px",
        }}>Describí tu problema</label>
        <textarea
          value={texto}
          onChange={e => handleChange(e.target.value)}
          placeholder="Ej: Se me rompió una cañería debajo de la pileta y el agua no para de salir..."
          rows={6}
          style={{
            width: "100%", borderRadius: "12px", padding: "14px",
            border: urgencia ? "2px solid #FCA5A5" : "2px solid #E2E8F0",
            fontFamily: "'DM Sans',sans-serif", fontSize: "15px",
            color: "#0F172A", resize: "vertical", outline: "none",
            lineHeight: "1.6", boxSizing: "border-box",
            background: urgencia ? "#FFF5F5" : "#F8FAFC",
            transition: "all 0.2s",
          }}
        />

        {urgencia && (
          <div style={{
            marginTop: "12px", background: "#FEF2F2",
            border: "1.5px solid #FECACA", borderRadius: "12px",
            padding: "14px 16px",
          }}>
            <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
              fontSize: "13px", color: "#B91C1C", marginBottom: "6px" }}>
              ⚠️ Urgencia detectada
            </div>
            <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "13px",
              color: "#7F1D1D", lineHeight: "1.5" }}>
              <strong>Acción inmediata:</strong> Cerrá la llave de paso principal.
              Luego te buscamos un profesional disponible ahora.
            </div>
          </div>
        )}

        <div style={{ display: "flex", justifyContent: "space-between",
          alignItems: "center", marginTop: "20px", gap: "12px", flexWrap: "wrap" }}>
          <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "12px", color: "#94A3B8" }}>
            {texto.length} caracteres
            {urgencia && <span style={{ color: "#EF4444", fontWeight: "700",
              marginLeft: "8px" }}>· Modo urgencia activado</span>}
          </div>
          <button
            disabled={texto.trim().length < 10}
            onClick={() => onBuscar(texto, urgencia)}
            style={{
              background: texto.trim().length >= 10
                ? urgencia
                  ? "linear-gradient(135deg,#EF4444,#B91C1C)"
                  : "linear-gradient(135deg,#3B82F6,#2563EB)"
                : "#E2E8F0",
              color: texto.trim().length >= 10 ? "#fff" : "#94A3B8",
              border: "none", borderRadius: "12px", padding: "13px 28px",
              fontFamily: "'DM Sans',sans-serif", fontWeight: "700",
              fontSize: "15px", cursor: texto.trim().length >= 10 ? "pointer" : "default",
              transition: "all 0.2s",
            }}>
            {urgencia ? "🚨 Buscar ahora" : "Buscar profesionales →"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── TURNO SELECTOR ──────────────────────────────────────────────────────────

const FRANJAS_DISP = [
  { key: "manana", label: "Mañana", rango: "08:00–13:00" },
  { key: "tarde",  label: "Tarde",  rango: "13:00–18:00" },
  { key: "noche",  label: "Noche",  rango: "18:00–22:00" },
];
const DIAS_DISP = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"];

function TurnoSelector({ plomero, turnoActual, onSelect }) {
  const agenda = plomero.agenda || {};
  const hayAgenda = Object.values(agenda).some(Boolean);
  const [diaElegido, setDiaElegido] = useState(null);

  if (!hayAgenda) return (
    <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "11px",
      color: "#94A3B8", fontStyle: "italic" }}>
      Sin agenda — el plomero coordinará el horario
    </div>
  );

  // Días que tienen al menos una franja disponible
  const diasDisponibles = DIAS_DISP.filter(dia =>
    FRANJAS_DISP.some(f => agenda[`${dia}_${f.key}`])
  );

  // Franjas disponibles para el día elegido
  const franjasDelDia = diaElegido
    ? FRANJAS_DISP.filter(f => agenda[`${diaElegido}_${f.key}`])
    : [];

  const turnoSelKey = turnoActual; // "Lun_manana"
  const [diaActual, franjaActual] = turnoSelKey ? turnoSelKey.split("_") : [null, null];

  return (
    <div onClick={e => e.stopPropagation()}>
      <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "10px",
        fontWeight: "700", color: "#94A3B8", textTransform: "uppercase",
        letterSpacing: "0.8px", marginBottom: "8px" }}>
        Elegí un turno
      </div>

      {/* Paso 1: elegir día */}
      <div style={{ marginBottom: "8px" }}>
        <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "11px",
          color: "#64748B", marginBottom: "5px" }}>Día:</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "4px" }}>
          {diasDisponibles.map(dia => {
            const esDiaActual = diaActual === dia;
            const esDiaElegido = diaElegido === dia;
            return (
              <button key={dia}
                onClick={() => {
                  setDiaElegido(esDiaElegido ? null : dia);
                  // Si cambiás de día, limpiá el turno si era de ese día
                  if (esDiaActual) onSelect(plomero.id_plomero, null);
                }}
                style={{
                  padding: "5px 10px", borderRadius: "8px",
                  border: esDiaActual ? "2px solid #3B82F6" : "1.5px solid #E2E8F0",
                  background: esDiaActual ? "#EFF6FF" : esDiaElegido ? "#F1F5F9" : "#fff",
                  color: esDiaActual ? "#1D4ED8" : "#475569",
                  fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
                  fontWeight: esDiaActual || esDiaElegido ? "700" : "500",
                  cursor: "pointer", transition: "all 0.15s",
                }}>
                {dia} {esDiaActual ? "✓" : ""}
              </button>
            );
          })}
        </div>
      </div>

      {/* Paso 2: elegir franja */}
      {diaElegido && (
        <div>
          <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "11px",
            color: "#64748B", marginBottom: "5px" }}>Horario:</div>
          <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
            {franjasDelDia.map(f => {
              const key = `${diaElegido}_${f.key}`;
              const sel = turnoActual === key;
              return (
                <button key={key}
                  onClick={() => onSelect(plomero.id_plomero, sel ? null : key)}
                  style={{
                    padding: "7px 12px", borderRadius: "10px",
                    border: sel ? "none" : "1.5px solid #E2E8F0",
                    background: sel ? "#3B82F6" : "#F8FAFC",
                    color: sel ? "#fff" : "#475569",
                    fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
                    fontWeight: "600", cursor: "pointer", transition: "all 0.15s",
                    display: "flex", flexDirection: "column", alignItems: "center", gap: "1px",
                  }}>
                  <span>{f.label}</span>
                  <span style={{ fontSize: "10px", opacity: 0.75 }}>{f.rango}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Turno confirmado */}
      {turnoActual && (
        <div style={{ marginTop: "8px", background: "#F0FDF4",
          border: "1px solid #86EFAC", borderRadius: "8px",
          padding: "6px 10px", fontFamily: "'DM Sans',sans-serif",
          fontSize: "11px", color: "#15803D", fontWeight: "600" }}>
          ✓ {diaActual} · {FRANJAS_DISP.find(f => f.key === franjaActual)?.label}{" "}
          ({FRANJAS_DISP.find(f => f.key === franjaActual)?.rango})
        </div>
      )}
    </div>
  );
}

// ─── SCREEN: RESULTADOS ───────────────────────────────────────────────────────

function ScreenResultados({ problema, urgencia, onEnviar }) {
  const [plomeros, setPlomeros]   = useState([]);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState("");
  const [seleccionados, setSelec] = useState([]);
  const [filtroGenero, setFiltro] = useState("todos");
  const [turnos, setTurnos]       = useState({});
  const [enviando, setEnviando]   = useState(false);
  const [enviado, setEnviado]     = useState(false);
  const [solicitudResp, setSolicitud] = useState(null);
  const [coords, setCoords]       = useState(null);
  const [geoMsg, setGeoMsg]       = useState("📍 Obteniendo tu ubicación...");

  // Fix 2: Geolocalización real
  useEffect(() => {
    if (!navigator.geolocation) { setGeoMsg(""); return; }
    navigator.geolocation.getCurrentPosition(
      pos => {
        setCoords({ lat: pos.coords.latitude, lon: pos.coords.longitude });
        setGeoMsg("📍 Ubicación obtenida");
        setTimeout(() => setGeoMsg(""), 2000);
      },
      () => {
        setGeoMsg("📍 Sin GPS — usando ubicación por defecto");
        setTimeout(() => setGeoMsg(""), 3000);
      },
      { timeout: 6000 }
    );
  }, []);

  useEffect(() => {
    const cargar = async () => {
      setLoading(true); setError(""); setSelec([]); setTurnos({});
      try {
        const res = await api.post("/plomeros/sugerir", {
          descripcion:  problema,
          solo_mujeres: filtroGenero === "F",
          latitud:      coords?.lat ?? -34.85,
          longitud:     coords?.lon ?? -58.38,
        });
        // Fix 5: Deduplicar por id_plomero
        const vistos = new Set();
        const unicos = (Array.isArray(res.data) ? res.data : []).filter(p => {
          if (vistos.has(p.id_plomero)) return false;
          vistos.add(p.id_plomero);
          return true;
        });
        setPlomeros(unicos);
      } catch (e) {
        setError(e.response?.data?.detail || e.message);
      } finally {
        setLoading(false);
      }
    };
    cargar();
  }, [problema, filtroGenero, coords]);

  const toggle = id => setSelec(prev =>
    prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
  );

  const setTurno = (idPlomero, turno) =>
    setTurnos(prev => ({ ...prev, [idPlomero]: turno }));

  const handleEnviar = async () => {
    setEnviando(true);
    try {
      const resp = await api.post("/solicitudes/", {
        descripcion_raw:  problema,
        solo_mujeres:     filtroGenero === "F",
        localidad_evento: "Sin especificar",
        latitud_evento:   coords?.lat ?? -34.85,
        longitud_evento:  coords?.lon ?? -58.38,
      });
      setSolicitud(resp.data);
      setEnviado(true);
      setTimeout(() => onEnviar(resp.data), 1800);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
      setEnviando(false);
    }
  };

  if (enviado) return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center",
      justifyContent: "center", minHeight: "60vh", padding: "40px 24px", textAlign: "center" }}>
      <style>{`@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.12)}}`}</style>
      <div style={{ fontSize: "56px", marginBottom: "16px", animation: "pulse 1s ease infinite" }}>📡</div>
      <h2 style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
        fontSize: "22px", color: "#0F172A", margin: "0 0 8px" }}>Solicitud enviada</h2>
      <p style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "15px",
        color: "#64748B", maxWidth: "320px" }}>
        Notificamos a los profesionales.{" "}
        {urgencia ? "Tienen 30 minutos para responder." : "Tienen 3 horas para responder."}
      </p>
      {solicitudResp && (
        <div style={{ marginTop: "16px", background: "#F0FDF4", border: "1.5px solid #86EFAC",
          borderRadius: "12px", padding: "12px 20px", fontFamily: "'DM Sans',sans-serif",
          fontSize: "13px", color: "#15803D" }}>
          Solicitud #{solicitudResp.id_solicitud} · Estado: {solicitudResp.estado}
        </div>
      )}
    </div>
  );

  return (
    <div style={{ maxWidth: "960px", margin: "0 auto", padding: "28px 24px" }}>
      {/* Fix 2: Mensaje de geolocalización */}
      {geoMsg && (
        <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
          color: "#64748B", marginBottom: "12px", display: "flex",
          alignItems: "center", gap: "6px" }}>
          {geoMsg}
        </div>
      )}
      {urgencia && (
        <div style={{ background: "#FFF7ED", border: "1.5px solid #FED7AA",
          borderRadius: "14px", padding: "14px 18px", marginBottom: "24px",
          display: "flex", gap: "12px", alignItems: "flex-start" }}>
          <span style={{ fontSize: "20px" }}>⚠️</span>
          <div>
            <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
              fontSize: "12px", color: "#C2410C", textTransform: "uppercase",
              letterSpacing: "0.6px", marginBottom: "4px" }}>Urgencia detectada</div>
            <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "13px",
              color: "#7C2D12", fontWeight: "500" }}>"{problema}"</div>
            <div style={{ marginTop: "8px", background: "#FEF2F2",
              border: "1px solid #FECACA", borderRadius: "8px",
              padding: "8px 12px", color: "#991B1B", fontSize: "13px",
              fontFamily: "'DM Sans',sans-serif" }}>
              💡 <strong>Acción inmediata:</strong> Cerrá la llave de paso principal.
            </div>
          </div>
        </div>
      )}

      <div style={{ display: "flex", justifyContent: "space-between",
        alignItems: "flex-end", marginBottom: "20px", flexWrap: "wrap", gap: "12px" }}>
        <div>
          <h1 style={{ margin: 0, fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
            fontSize: "22px", color: "#0F172A", letterSpacing: "-0.4px" }}>
            Profesionales disponibles
          </h1>
          <p style={{ margin: "4px 0 0", fontFamily: "'DM Sans',sans-serif",
            fontSize: "13px", color: "#64748B" }}>
            Sugeridos por IA según tu problema
          </p>
        </div>
        <div style={{ display: "flex", background: "#F1F5F9",
          borderRadius: "12px", padding: "4px", gap: "2px" }}>
          {[{ key: "todos", label: "Indistinto" }, { key: "F", label: "👩 Solo mujeres" }].map(({ key, label }) => (
            <button key={key} onClick={() => setFiltro(key)} style={{
              background: filtroGenero === key ? "#fff" : "transparent",
              border: "none", borderRadius: "9px", padding: "7px 14px",
              fontSize: "13px", fontWeight: filtroGenero === key ? "700" : "500",
              color: filtroGenero === key ? "#0F172A" : "#64748B",
              cursor: "pointer", transition: "all 0.18s",
              fontFamily: "'DM Sans',sans-serif", whiteSpace: "nowrap",
              boxShadow: filtroGenero === key ? "0 1px 4px rgba(0,0,0,0.1)" : "none",
            }}>{label}</button>
          ))}
        </div>
      </div>

      <ErrorBanner msg={error} onClose={() => setError("")} />

      {loading
        ? <div style={{ display: "flex", justifyContent: "center", padding: "60px" }}>
            <Spinner size={36} />
          </div>
        : plomeros.length === 0
          ? <div style={{ textAlign: "center", padding: "60px 20px",
              border: "2px dashed #E2E8F0", borderRadius: "16px" }}>
              <div style={{ fontSize: "36px", marginBottom: "12px" }}>🔍</div>
              <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "700",
                fontSize: "15px", color: "#94A3B8" }}>
                No se encontraron profesionales
              </div>
            </div>
          : <div style={{ display: "grid",
              gridTemplateColumns: "repeat(auto-fill,minmax(270px,1fr))", gap: "16px" }}>
              {plomeros.map((p, i) => {
                const isSelected = seleccionados.includes(p.id_plomero);
                return (
                  <div key={p.id_plomero}
                    onClick={() => toggle(p.id_plomero)}
                    style={{
                      background: isSelected ? "linear-gradient(145deg,#EFF6FF,#F0FDF4)" : "#fff",
                      border: isSelected ? "2px solid #3B82F6" : "2px solid #F1F5F9",
                      borderRadius: "20px", padding: "20px",
                      display: "flex", flexDirection: "column", gap: "14px",
                      cursor: "pointer", position: "relative", transition: "all 0.2s",
                      boxShadow: isSelected
                        ? "0 0 0 4px rgba(59,130,246,0.08), 0 4px 20px rgba(59,130,246,0.1)"
                        : "0 2px 12px rgba(0,0,0,0.05)",
                    }}>
                    {/* Rank badge */}
                    <div style={{
                      position: "absolute", top: "14px", right: "14px",
                      background: i < 3
                        ? `linear-gradient(135deg,${["#F59E0B","#94A3B8","#CD7C2F"][i]},${["#D97706","#64748B","#92400E"][i]})`
                        : "#F1F5F9",
                      color: i < 3 ? "#fff" : "#94A3B8",
                      width: "26px", height: "26px", borderRadius: "50%",
                      display: "flex", alignItems: "center", justifyContent: "center",
                      fontSize: "11px", fontWeight: "800", fontFamily: "'DM Sans',sans-serif",
                    }}>{i + 1}</div>

                    {isSelected && (
                      <div style={{
                        position: "absolute", top: "14px", right: "46px",
                        background: "#22C55E", color: "#fff",
                        width: "22px", height: "22px", borderRadius: "50%",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        fontSize: "11px", fontWeight: "900",
                      }}>✓</div>
                    )}

                    <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                      <div style={{ position: "relative", flexShrink: 0 }}>
                        <Avatar src={p.foto_perfil_path} nombre={p.nombre} apellido={p.apellido} size={58} />
                        <div style={{
                          position: "absolute", bottom: "-3px", right: "-3px",
                          background: "#3B82F6", borderRadius: "50%",
                          width: "18px", height: "18px",
                          display: "flex", alignItems: "center", justifyContent: "center",
                          border: "2px solid #fff", fontSize: "9px", color: "#fff", fontWeight: "900",
                        }}>✓</div>
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
                          fontSize: "16px", color: "#0F172A",
                          whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                          {p.nombre} {p.apellido}
                        </div>
                        <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
                          color: "#64748B", marginTop: "3px",
                          display: "flex", alignItems: "center", gap: "4px" }}>
                          <span>📍</span>
                          <span>{p.localidad}</span>
                          {p.distancia_km && (
                            <>
                              <span style={{ color: "#CBD5E1" }}>·</span>
                              <span style={{ color: "#3B82F6", fontWeight: "600" }}>
                                {p.distancia_km?.toFixed(1)} km
                              </span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>

                    <div style={{ display: "flex", alignItems: "center", gap: "8px",
                      background: "#FFFBEB", border: "1px solid #FDE68A",
                      borderRadius: "10px", padding: "7px 12px" }}>
                      <Stars val={p.puntuacion || 0} />
                      <span style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
                        fontSize: "14px", color: "#92400E" }}>
                        {(p.puntuacion || 0).toFixed(1)}
                      </span>
                      <span style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
                        color: "#B45309" }}>({p.total_trabajos || 0} trabajos)</span>
                    </div>

                    <div>
                      <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "10px",
                        fontWeight: "700", color: "#94A3B8", textTransform: "uppercase",
                        letterSpacing: "0.8px", marginBottom: "7px" }}>Especialidad</div>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "5px" }}>
                        <Badge label={p.especialidad || p.etiqueta_ia || "General"} />
                        {p.atiende_urgencias && <Badge label="Urgencias" />}
                      </div>
                    </div>

                    {/* Fix 4: Selector de turno según agenda del plomero */}
                    {isSelected && (
                      <TurnoSelector
                        plomero={p}
                        turnoActual={turnos[p.id_plomero]}
                        onSelect={setTurno}
                      />
                    )}

                    {p.urgencia_ia === "URGENTE" && urgencia && (
                      <div style={{ background: "#FEF2F2", border: "1px solid #FECACA",
                        borderRadius: "8px", padding: "6px 10px",
                        fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
                        color: "#B91C1C", fontWeight: "600" }}>
                        🚨 Atiende urgencias ahora
                      </div>
                    )}

                    <button onClick={e => { e.stopPropagation(); toggle(p.id_plomero); }} style={{
                      background: isSelected
                        ? "linear-gradient(135deg,#3B82F6,#2563EB)"
                        : "linear-gradient(135deg,#F8FAFC,#F1F5F9)",
                      color: isSelected ? "#fff" : "#475569",
                      border: isSelected ? "none" : "1.5px solid #E2E8F0",
                      borderRadius: "12px", padding: "10px 8px",
                      fontFamily: "'DM Sans',sans-serif", fontWeight: "700",
                      fontSize: "13px", cursor: "pointer", transition: "all 0.18s",
                    }}>{isSelected ? "✓ Seleccionado" : "Seleccionar"}</button>
                  </div>
                );
              })}
            </div>
      }

      {seleccionados.length > 0 && (
        <div style={{
          marginTop: "28px", background: "linear-gradient(135deg,#0F172A,#1E3A5F)",
          borderRadius: "20px", padding: "22px 26px",
          display: "flex", alignItems: "center",
          justifyContent: "space-between", gap: "16px", flexWrap: "wrap",
          boxShadow: "0 8px 32px rgba(15,23,42,0.2)",
        }}>
          <div>
            <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "11px",
              fontWeight: "700", color: "#475569", textTransform: "uppercase",
              letterSpacing: "0.8px", marginBottom: "6px" }}>
              {seleccionados.length} profesional{seleccionados.length > 1 ? "es" : ""} seleccionado{seleccionados.length > 1 ? "s" : ""}
            </div>
            <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "13px", color: "#94A3B8" }}>
              {urgencia
                ? "Tienen 30 min para responder · El primero que acepte queda asignado"
                : "Tienen 3 hs para responder · El primero que acepte queda asignado"}
            </div>
          </div>
          <button onClick={handleEnviar} disabled={enviando} style={{
            background: "linear-gradient(135deg,#22C55E,#16A34A)",
            color: "#fff", border: "none", borderRadius: "14px",
            padding: "13px 26px", fontFamily: "'DM Sans',sans-serif",
            fontWeight: "800", fontSize: "14px", cursor: enviando ? "default" : "pointer",
            boxShadow: "0 4px 16px rgba(34,197,94,0.35)", whiteSpace: "nowrap",
            display: "flex", alignItems: "center", gap: "8px",
            opacity: enviando ? 0.7 : 1,
          }}>
            {enviando ? <Spinner size={16} color="#fff" /> : null}
            Enviar solicitud →
          </button>
        </div>
      )}
    </div>
  );
}

// ─── SCREEN: ESTADO ───────────────────────────────────────────────────────────

function ScreenEstado({ solicitud, onNav }) {
  const [rating, setRating]       = useState(0);
  const [comentario, setComentario] = useState("");
  const [valorado, setValorado]   = useState(false);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState("");

  const estado = solicitud?.estado || "PENDIENTE";

  const ESTADOS = [
    { key: "PENDIENTE",  label: "Solicitud enviada",  icon: "📡", desc: "Esperando respuesta de los profesionales" },
    { key: "ACEPTADO",   label: "Trabajo aceptado",   icon: "✅", desc: "Un plomero aceptó tu solicitud" },
    { key: "FINALIZADO", label: "Trabajo finalizado",  icon: "🏁", desc: "El trabajo fue completado" },
  ];

  const idxActual = ESTADOS.findIndex(e => e.key === estado);

  const handleCalificar = async () => {
    if (!rating || !solicitud?.id_solicitud) return;
    setLoading(true); setError("");
    try {
      await api.post(`/calificaciones/${solicitud.id_solicitud}`, null, {
        params: { estrellas: rating, ...(comentario ? { comentario } : {}) },
      });
      setValorado(true);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "640px", margin: "0 auto", padding: "32px 24px" }}>
      <h1 style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
        fontSize: "22px", color: "#0F172A", letterSpacing: "-0.4px", margin: "0 0 24px" }}>
        Estado del trabajo
      </h1>

      {solicitud && (
        <div style={{ background: "#F8FAFC", borderRadius: "12px",
          padding: "12px 16px", marginBottom: "24px",
          fontFamily: "'DM Sans',sans-serif", fontSize: "13px", color: "#64748B" }}>
          Solicitud #{solicitud.id_solicitud} · {solicitud.descripcion_raw}
        </div>
      )}

      {/* Timeline */}
      <div style={{ background: "#fff", borderRadius: "20px",
        border: "1.5px solid #F1F5F9", padding: "24px",
        boxShadow: "0 2px 16px rgba(0,0,0,0.05)", marginBottom: "20px" }}>
        {ESTADOS.map((e, i) => {
          const done    = i <= idxActual;
          const current = i === idxActual;
          return (
            <div key={e.key} style={{ display: "flex", gap: "16px",
              alignItems: "flex-start", marginBottom: i < ESTADOS.length - 1 ? "24px" : 0 }}>
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                <div style={{
                  width: "40px", height: "40px", borderRadius: "50%",
                  background: done
                    ? current ? "linear-gradient(135deg,#3B82F6,#2563EB)" : "#F0FDF4"
                    : "#F1F5F9",
                  border: current ? "none" : done ? "2px solid #86EFAC" : "2px solid #E2E8F0",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "18px", flexShrink: 0,
                  boxShadow: current ? "0 4px 16px rgba(59,130,246,0.3)" : "none",
                  transition: "all 0.3s",
                }}>{e.icon}</div>
                {i < ESTADOS.length - 1 && (
                  <div style={{ width: "2px", height: "24px", marginTop: "4px",
                    background: i < idxActual ? "#86EFAC" : "#E2E8F0" }} />
                )}
              </div>
              <div style={{ paddingTop: "8px" }}>
                <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "700",
                  fontSize: "14px", color: done ? "#0F172A" : "#94A3B8" }}>
                  {e.label}
                </div>
                {current && (
                  <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "13px",
                    color: "#64748B", marginTop: "3px" }}>{e.desc}</div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <ErrorBanner msg={error} onClose={() => setError("")} />

      {/* Plomero asignado */}
      {solicitud?.id_plomero && (
        <div style={{ background: "#fff", borderRadius: "16px",
          border: "1.5px solid #F1F5F9", padding: "18px 20px", marginBottom: "20px" }}>
          <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "700",
            fontSize: "12px", color: "#94A3B8", textTransform: "uppercase",
            letterSpacing: "0.6px", marginBottom: "10px" }}>Plomero asignado</div>
          <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
            <Avatar nombre={solicitud.nombre_plomero?.split(" ")[0]}
              apellido={solicitud.nombre_plomero?.split(" ")[1]} size={48} />
            <div>
              <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
                fontSize: "15px", color: "#0F172A" }}>{solicitud.nombre_plomero}</div>
            </div>
          </div>
        </div>
      )}

      {/* Calificación (solo si finalizado) */}
      {estado === "FINALIZADO" && !valorado && (
        <div style={{ background: "#fff", borderRadius: "16px",
          border: "2px solid #FDE68A", padding: "22px" }}>
          <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
            fontSize: "16px", color: "#0F172A", marginBottom: "6px" }}>
            ¿Cómo estuvo el trabajo?
          </div>
          <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "13px",
            color: "#64748B", marginBottom: "16px" }}>
            Tu valoración ayuda a otros usuarios a elegir mejor.
          </div>
          <div style={{ display: "flex", gap: "6px", marginBottom: "16px" }}>
            <Stars val={rating} size={32} interactive onRate={setRating} />
            {rating > 0 && (
              <span style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "700",
                fontSize: "15px", color: "#92400E", alignSelf: "center", marginLeft: "8px" }}>
                {["","Malo","Regular","Bueno","Muy bueno","Excelente"][rating]}
              </span>
            )}
          </div>
          <textarea
            value={comentario}
            onChange={e => setComentario(e.target.value)}
            placeholder="Contá tu experiencia (opcional)..."
            rows={3}
            style={{ width: "100%", borderRadius: "10px", padding: "12px",
              border: "1.5px solid #E2E8F0", fontFamily: "'DM Sans',sans-serif",
              fontSize: "14px", color: "#0F172A", resize: "vertical",
              outline: "none", boxSizing: "border-box", background: "#F8FAFC" }}
          />
          <button
            disabled={rating === 0 || loading}
            onClick={handleCalificar}
            style={{
              marginTop: "14px", width: "100%",
              background: rating > 0 ? "linear-gradient(135deg,#F59E0B,#D97706)" : "#F1F5F9",
              color: rating > 0 ? "#fff" : "#CBD5E1",
              border: "none", borderRadius: "12px", padding: "12px",
              fontFamily: "'DM Sans',sans-serif", fontWeight: "700",
              fontSize: "14px", cursor: rating > 0 ? "pointer" : "default",
              display: "flex", alignItems: "center", justifyContent: "center", gap: "8px",
            }}>
            {loading ? <Spinner size={16} color="#fff" /> : null}
            Enviar valoración ⭐
          </button>
        </div>
      )}

      {valorado && (
        <div style={{ background: "#F0FDF4", border: "2px solid #86EFAC",
          borderRadius: "16px", padding: "22px", textAlign: "center" }}>
          <div style={{ fontSize: "36px", marginBottom: "10px" }}>🎉</div>
          <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
            fontSize: "16px", color: "#15803D", marginBottom: "6px" }}>
            ¡Gracias por tu valoración!
          </div>
        </div>
      )}

      <button onClick={() => onNav("problema")} style={{
        marginTop: "20px", width: "100%",
        background: "#F8FAFC", border: "1.5px solid #E2E8F0",
        borderRadius: "12px", padding: "12px",
        fontFamily: "'DM Sans',sans-serif", fontWeight: "600",
        fontSize: "14px", color: "#475569", cursor: "pointer",
      }}>← Volver al inicio</button>
    </div>
  );
}

// ─── SCREEN: HISTORIAL ────────────────────────────────────────────────────────

function ScreenHistorial({ historial, loading, error }) {
  const [detalle, setDetalle] = useState(null);

  return (
    <div style={{ maxWidth: "640px", margin: "0 auto", padding: "32px 24px" }}>
      <h1 style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
        fontSize: "22px", color: "#0F172A", letterSpacing: "-0.4px", margin: "0 0 6px" }}>
        Mis reparaciones
      </h1>
      <p style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "14px",
        color: "#64748B", margin: "0 0 24px" }}>
        Historial de solicitudes enviadas
      </p>

      <ErrorBanner msg={error} />

      {loading
        ? <div style={{ display: "flex", justifyContent: "center", padding: "60px" }}>
            <Spinner size={36} />
          </div>
        : historial.length === 0
          ? <div style={{ textAlign: "center", padding: "60px 20px",
              border: "2px dashed #E2E8F0", borderRadius: "16px" }}>
              <div style={{ fontSize: "36px", marginBottom: "12px" }}>📋</div>
              <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "700",
                fontSize: "15px", color: "#94A3B8" }}>
                Todavía no tenés trabajos registrados.
              </div>
            </div>
          : historial.map(h => (
            <div key={h.id_solicitud} style={{
              background: "#fff", borderRadius: "16px",
              border: "1.5px solid #F1F5F9", padding: "18px 20px",
              marginBottom: "12px", transition: "all 0.18s",
            }}
            onMouseEnter={e => e.currentTarget.style.border = "1.5px solid #BFDBFE"}
            onMouseLeave={e => e.currentTarget.style.border = "1.5px solid #F1F5F9"}
            >
              <div style={{ display: "flex", gap: "14px", alignItems: "center" }}>
                <Avatar nombre={h.nombre_plomero?.split(" ")[0] || "P"}
                  apellido={h.nombre_plomero?.split(" ")[1] || ""} size={52} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
                    fontSize: "15px", color: "#0F172A" }}>
                    {h.nombre_plomero || "Sin asignar"}
                  </div>
                  <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "13px",
                    color: "#64748B", marginTop: "2px",
                    whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {h.descripcion_raw}
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", marginTop: "5px" }}>
                    <span style={{
                      background: h.estado === "ACEPTADO" ? "#F0FDF4" : h.estado === "PENDIENTE" ? "#FFFBEB" : "#F0F9FF",
                      color: h.estado === "ACEPTADO" ? "#15803D" : h.estado === "PENDIENTE" ? "#B45309" : "#0369A1",
                      fontSize: "11px", fontWeight: "700", padding: "2px 8px",
                      borderRadius: "6px", fontFamily: "'DM Sans',sans-serif",
                    }}>{h.estado}</span>
                    <span style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "11px",
                      color: "#94A3B8" }}>
                      {h.fecha ? new Date(h.fecha).toLocaleDateString("es-AR") : ""}
                    </span>
                  </div>
                </div>
                <button onClick={() => setDetalle(detalle === h.id_solicitud ? null : h.id_solicitud)}
                  style={{ background: "#F8FAFC", border: "1.5px solid #E2E8F0",
                    borderRadius: "8px", padding: "6px 12px",
                    fontFamily: "'DM Sans',sans-serif", fontWeight: "600",
                    fontSize: "12px", color: "#475569", cursor: "pointer" }}>
                  {detalle === h.id_solicitud ? "Cerrar" : "Ver detalle"}
                </button>
              </div>

              {detalle === h.id_solicitud && (
                <div style={{ marginTop: "14px", paddingTop: "14px",
                  borderTop: "1px solid #F1F5F9" }}>
                  <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "13px",
                    color: "#475569", lineHeight: "1.6", marginBottom: "10px" }}>
                    {h.descripcion_raw}
                  </div>
                  {h.plomeros_sugeridos_detallados?.length > 0 && (
                    <div>
                      <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "700",
                        fontSize: "12px", color: "#94A3B8", textTransform: "uppercase",
                        letterSpacing: "0.6px", marginBottom: "8px" }}>Plomeros sugeridos</div>
                      {h.plomeros_sugeridos_detallados.map(p => (
                        <div key={p.id} style={{ fontFamily: "'DM Sans',sans-serif",
                          fontSize: "12px", color: "#64748B", marginBottom: "4px" }}>
                          · {p.nombre} — {p.localidad} — ⭐ {p.calificacion?.toFixed(1)}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))
      }
    </div>
  );
}

// ─── SCREEN: NOTIFICACIONES ───────────────────────────────────────────────────

function ScreenNotificaciones({ notifs, onMark }) {
  return (
    <div style={{ maxWidth: "600px", margin: "0 auto", padding: "32px 24px" }}>
      <div style={{ display: "flex", justifyContent: "space-between",
        alignItems: "center", marginBottom: "24px" }}>
        <h1 style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
          fontSize: "22px", color: "#0F172A", letterSpacing: "-0.4px", margin: 0 }}>
          Notificaciones
        </h1>
        {notifs.some(n => !n.leida) && (
          <button onClick={onMark} style={{
            background: "transparent", border: "none",
            fontFamily: "'DM Sans',sans-serif", fontWeight: "600",
            fontSize: "13px", color: "#3B82F6", cursor: "pointer",
          }}>Marcar todas como leídas</button>
        )}
      </div>

      {notifs.length === 0
        ? <div style={{ textAlign: "center", padding: "60px 20px",
            color: "#94A3B8", fontFamily: "'DM Sans',sans-serif" }}>
            <div style={{ fontSize: "36px", marginBottom: "12px" }}>🔔</div>
            <div style={{ fontWeight: "700", fontSize: "15px" }}>Sin notificaciones</div>
          </div>
        : notifs.map(n => (
          <div key={n.id} style={{
            background: n.leida ? "#fff" : "#EFF6FF",
            border: n.leida ? "1.5px solid #F1F5F9" : "1.5px solid #BFDBFE",
            borderRadius: "14px", padding: "16px 18px", marginBottom: "10px",
            display: "flex", gap: "14px", alignItems: "flex-start",
          }}>
            <div style={{ fontSize: "22px", flexShrink: 0,
              width: "40px", height: "40px", borderRadius: "12px",
              background: n.leida ? "#F8FAFC" : "#DBEAFE",
              display: "flex", alignItems: "center", justifyContent: "center" }}>
              {n.icon}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "700",
                fontSize: "14px", color: "#0F172A", marginBottom: "3px" }}>
                {n.titulo}
              </div>
              <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "13px",
                color: "#64748B", lineHeight: "1.4" }}>{n.mensaje}</div>
              <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "11px",
                color: "#CBD5E1", marginTop: "6px" }}>{n.tiempo}</div>
            </div>
            {!n.leida && (
              <div style={{ width: "8px", height: "8px", borderRadius: "50%",
                background: "#3B82F6", flexShrink: 0, marginTop: "6px" }} />
            )}
          </div>
        ))
      }
    </div>
  );
}

// ─── NOTIFICACIONES DERIVADAS DE SOLICITUDES (polling) ───────────────────────

function useSolicitudNotifs(token) {
  const [notifs, setNotifs] = useState([]);
  const prevStates = useRef({});

  const poll = useCallback(async () => {
    if (!token) return;
    try {
      // Usamos el endpoint de solicitudes del usuario (ajustá si cambia el route)
      const res = await api.get("/solicitudes/buscar", { params: { q: "" } });
      const arr = Array.isArray(res.data) ? res.data : [];
      const nuevas = [];

      arr.forEach(s => {
        const prev = prevStates.current[s.id_solicitud];
        if (prev && prev !== s.estado) {
          if (s.estado === "ACEPTADO") {
            nuevas.push({
              id: Date.now() + s.id_solicitud,
              icon: "✅",
              titulo: "Solicitud aceptada",
              mensaje: `${s.nombre_plomero || "Un plomero"} aceptó tu solicitud.`,
              tiempo: "Ahora",
              leida: false,
            });
          }
          if (s.estado === "FINALIZADO") {
            nuevas.push({
              id: Date.now() + s.id_solicitud + 1,
              icon: "🏁",
              titulo: "Trabajo finalizado",
              mensaje: "El trabajo fue marcado como finalizado. ¡Podés valorar el servicio!",
              tiempo: "Ahora",
              leida: false,
            });
          }
        }
        prevStates.current[s.id_solicitud] = s.estado;
      });

      if (nuevas.length > 0) {
        setNotifs(prev => [...nuevas, ...prev]);
      }
    } catch {
      // silencioso — no mostramos error de polling
    }
  }, [token]);

  useEffect(() => {
    if (!token) return;
    poll();
    const interval = setInterval(poll, 15000); // cada 15 segundos
    return () => clearInterval(interval);
  }, [token, poll]);

  return [notifs, setNotifs];
}

// ─── HOME CLIENTE ─────────────────────────────────────────────────────────────
// App.jsx lo monta cuando view==="app". Solo recibe onLogout como prop.

export default function HomeCliente({ onLogout }) {
  const [screen, setScreen]     = useState("problema");
  const [problema, setProblema] = useState("");
  const [urgencia, setUrgencia] = useState(false);
  const [solicitudActiva, setSolicitud] = useState(null);

  // Historial real
  const [historial, setHistorial]       = useState([]);
  const [loadingHistorial, setLoadingH] = useState(false);
  const [errorHistorial, setErrorH]     = useState("");

  // Token y user desde zustand (persist lo restaura de localStorage automáticamente)
  const token = useAuthStore(s => s.token);
  const [notifs, setNotifs] = useSolicitudNotifs(token);
  const notifCount = notifs.filter(n => !n.leida).length;

  // Cargar historial al montar
  useEffect(() => {
    const cargar = async () => {
      setLoadingH(true); setErrorH("");
      try {
        const res = await api.get("/solicitudes/buscar", { params: { q: "" } });
        setHistorial(Array.isArray(res.data) ? res.data : []);
      } catch (e) {
        setErrorH(e.message);
      } finally {
        setLoadingH(false);
      }
    };
    cargar();
  }, []);

  const logout = useAuthStore(s => s.logout);
  const user   = useAuthStore(s => s.user);

  const handleLogout = () => {
    logout();                  // limpia zustand + localStorage via persist
    onLogout();                // App.jsx vuelve a view="login"
  };

  const handleBuscar = (texto, urg) => {
    setProblema(texto);
    setUrgencia(urg);
    setScreen("resultados");
  };

  const handleEnviar = (resp) => {
    setSolicitud(resp);
    if (resp) setHistorial(prev => [resp, ...prev]);
    setScreen("estado");
  };

  return (
    <div style={{ minHeight: "100vh",
      background: "linear-gradient(160deg,#F0F9FF 0%,#F8FAFC 50%,#F0FDF4 100%)" }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>

      <Header
        screen={screen === "resultados" || screen === "estado" ? "problema" : screen}
        onNav={setScreen}
        notifCount={notifCount}
        onLogout={handleLogout}
        user={user}
      />

      {screen === "problema" && (
        <ScreenProblema
          onBuscar={handleBuscar}
        />
      )}
      {screen === "resultados" && (
        <ScreenResultados
          problema={problema}
          urgencia={urgencia}
          onEnviar={handleEnviar}
          onNav={setScreen}
        />
      )}
      {screen === "estado" && (
        <ScreenEstado
          solicitud={solicitudActiva}
          onNav={setScreen}
        />
      )}
      {screen === "historial" && (
        <ScreenHistorial
          historial={historial}
          loading={loadingHistorial}
          error={errorHistorial}
        />
      )}
      {screen === "notificaciones" && (
        <ScreenNotificaciones
          notifs={notifs}
          onMark={() => setNotifs(n => n.map(x => ({ ...x, leida: true })))}
        />
      )}
    </div>
  );
}