import { useState, useEffect, useCallback, useRef } from "react";
import api from "../services/api";           // axios instance con interceptor de token
import { useAuthStore } from "../store/authStore"; // zustand store
import ChatWidget from "../components/ChatWidget";
import BoletaMateriales from "../components/BoletaMateriales"; // chat flotante cliente/plomero
import UserBadge from "../components/UserBadge";

// ─── CONSTANTS ───────────────────────────────────────────────────────────────

const BADGE_STYLES = {
  Destapes:          { bg: "#E0F2FE", text: "#0369A1" },
  Urgencias:         { bg: "#FEE2E2", text: "#B91C1C" },
  "Obra general":    { bg: "#DCFCE7", text: "#15803D" },
  Instalaciones:     { bg: "#F3E8FF", text: "#7E22CE" },
  "Plomería general":{ bg: "#EFF6FF", text: "#1D4ED8" },
  "Gas matriculado": { bg: "#FEF9C3", text: "#854D0E" },
  Calefacción:       { bg: "#FEE2E2", text: "#9F1239" },
  Filtraciones:      { bg: "#ECFDF5", text: "#065F46" },
  Obra:              { bg: "#DCFCE7", text: "#15803D" },
  DESTAPES:          { bg: "#E0F2FE", text: "#0369A1" },
  URGENCIAS:         { bg: "#FEE2E2", text: "#B91C1C" },
  OBRA:              { bg: "#DCFCE7", text: "#15803D" },
  INSTALACIONES:     { bg: "#F3E8FF", text: "#7E22CE" },
};

// Traducción de keys del enum a texto legible
const ESP_LABELS = {
  PLOMERIA_GENERAL:  "Plomería general",
  DESTAPES:          "Destapes",
  GAS_MATRICULADO:   "Gas matriculado",
  OBRA:              "Obra",
  FILTRACIONES:      "Filtraciones",
  CALEFACCION:       "Calefacción",
  OTRA:              "Otra especialidad",
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
  // Busca el estilo por el label legible o por el key del enum
  const s = BADGE_STYLES[label] || BADGE_STYLES[label?.toUpperCase()] || { bg: "#F3F4F6", text: "#374151" };
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
  const fullSrc = src && !src.startsWith("http") ? `/${src}` : src;
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
    { key: "problema",          label: "Inicio",             icon: "🏠" },
    { key: "mi-solicitud",      label: "Mi solicitud",       icon: "📡" },
    { key: "trabajos-finalizados", label: "Finalizados",     icon: "✅" },
    { key: "notificaciones",    label: "Alertas",            icon: "🔔", badge: notifCount },
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
        <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
          <UserBadge nombre={user?.nombre} apellido={user?.apellido} rol="Cliente" />
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
  const [texto,     setTexto]     = useState("");
  const [urgencia,  setUrgencia]  = useState(false);
  const [validando, setValidando] = useState(false);
  const [errorDesc, setErrorDesc] = useState("");
  const [avisoLenguaje, setAvisoLenguaje] = useState(null);

  const URGENCIA_KEYWORDS = [
    "inunda","pérdida","perder","no cierra","roto","explota",
    "revienta","urgente","emergencia","fuga","chorrea","sale agua",
  ];

  const handleChange = (v) => {
    setTexto(v);
    setErrorDesc("");
    setUrgencia(URGENCIA_KEYWORDS.some(k => v.toLowerCase().includes(k)));
  };

  const handleBuscar = async () => {
    if (texto.trim().length < 10) return;
    setValidando(true);
    setErrorDesc("");
    try {
      // Validar descripción con el backend antes de avanzar
      const res = await api.post("/plomeros/sugerir", {
        descripcion:      texto,
        solo_mujeres:     false,
        urgencia_forzada: urgencia,
        latitud:          -34.85,
        longitud:         -58.38,
        solo_validar:     true,  // flag para que solo valide sin devolver plomeros
      });
      // Si el backend devuelve valido: false en el diagnóstico
      if (res.data?.diagnostico?.valido === false) {
        setErrorDesc(res.data.diagnostico.mensaje_error ||
          "Por favor describí mejor el problema.");
        return;
      }
      // Lenguaje ofensivo: NO avanzamos a recomendaciones (eso lo vería el
      // profesional). Mostramos el cartel y limpiamos el cuadro para reescribir.
      if (res.data?.aviso_lenguaje?.mensaje) {
        setAvisoLenguaje(res.data.aviso_lenguaje.mensaje);
        return;
      }
      onBuscar(texto, urgencia);
    } catch (e) {
      const detail = e.response?.data?.detail;
      if (detail) {
        setErrorDesc(detail);
      } else {
        onBuscar(texto, urgencia);
      }
    } finally {
      setValidando(false);
    }
  };

  return (
    <div style={{ maxWidth: "640px", margin: "0 auto", padding: "60px 24px" }}>
      {avisoLenguaje && (
        <div style={{ position:"fixed", inset:0, zIndex:1000, background:"rgba(15,23,42,0.55)",
          backdropFilter:"blur(2px)", display:"flex", alignItems:"center", justifyContent:"center",
          padding:20 }}>
          <div style={{ background:"#fff", borderRadius:20, maxWidth:380, width:"100%",
            padding:"30px 26px", textAlign:"center", boxShadow:"0 24px 70px rgba(0,0,0,0.35)",
            border:"1px solid #FDE68A", fontFamily:"'DM Sans',sans-serif" }}>
            <div style={{ fontSize:44, marginBottom:12 }}>⚠️</div>
            <div style={{ fontWeight:800, fontSize:19, color:"#0F172A", marginBottom:10 }}>
              Cuidá el lenguaje
            </div>
            <div style={{ fontSize:14, color:"#475569", lineHeight:1.55, marginBottom:22 }}>
              {avisoLenguaje}
            </div>
            <button onClick={() => { setAvisoLenguaje(null); setTexto(""); setUrgencia(false); setErrorDesc(""); }}
              style={{ background:"linear-gradient(135deg,#F59E0B,#D97706)", color:"#fff",
                border:"none", borderRadius:12, padding:"12px 32px", fontFamily:"'DM Sans',sans-serif",
                fontWeight:700, fontSize:14, cursor:"pointer", width:"100%" }}>
              Aceptar
            </button>
          </div>
        </div>
      )}
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
            border: errorDesc
              ? "2px solid #FCA5A5"
              : urgencia
                ? "2px solid #FCA5A5"
                : "2px solid #E2E8F0",
            fontFamily: "'DM Sans',sans-serif", fontSize: "15px",
            color: "#0F172A", resize: "vertical", outline: "none",
            lineHeight: "1.6", boxSizing: "border-box",
            background: errorDesc ? "#FFF5F5" : urgencia ? "#FFF5F5" : "#F8FAFC",
            transition: "all 0.2s",
          }}
        />

        {/* Error de descripción inválida */}
        {errorDesc && (
          <div style={{
            marginTop: "12px", background: "#FEF2F2",
            border: "1.5px solid #FECACA", borderRadius: "12px",
            padding: "14px 16px",
          }}>
            <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
              fontSize: "13px", color: "#B91C1C", marginBottom: "4px" }}>
              ⚠️ Descripción inválida
            </div>
            <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "13px",
              color: "#7F1D1D", lineHeight: "1.5" }}>
              {errorDesc}
            </div>
          </div>
        )}

        {/* Urgencia detectada */}
        {urgencia && !errorDesc && (
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
            disabled={texto.trim().length < 10 || validando}
            onClick={handleBuscar}
            style={{
              background: texto.trim().length >= 10 && !validando
                ? urgencia
                  ? "linear-gradient(135deg,#EF4444,#B91C1C)"
                  : "linear-gradient(135deg,#3B82F6,#2563EB)"
                : "#E2E8F0",
              color: texto.trim().length >= 10 && !validando ? "#fff" : "#94A3B8",
              border: "none", borderRadius: "12px", padding: "13px 28px",
              fontFamily: "'DM Sans',sans-serif", fontWeight: "700",
              fontSize: "15px", cursor: texto.trim().length >= 10 && !validando
                ? "pointer" : "default",
              transition: "all 0.2s",
            }}>
            {validando
              ? "Analizando..."
              : urgencia
                ? "🚨 Buscar ahora"
                : "Buscar profesionales →"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── TURNO SELECTOR ──────────────────────────────────────────────────────────

const FRANJAS_DISP = [
  { key: "manana", horas: [8, 9, 10, 11, 12] },
  { key: "tarde",  horas: [13, 14, 15, 16, 17] },
  { key: "noche",  horas: [18, 19, 20, 21] },
];
const DIAS_DISP = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"];

// Nombres completos de días para mostrar con fecha
const DIAS_NOMBRE = ["Domingo","Lunes","Martes","Miércoles","Jueves","Viernes","Sábado"];
const MESES = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"];

function getFechaParaDia(diaStr) {
  // Devuelve el próximo Date que coincida con el día de la semana.
  // diff === 0 = HOY (no lo empujamos a la semana que viene): así coincide con
  // el backend (_calcular_fecha_trabajo) y se ofrecen los días reales de esta semana.
  const IDX = { "Lun":1,"Mar":2,"Mié":3,"Jue":4,"Vie":5,"Sáb":6,"Dom":0 };
  const hoy = new Date();
  const hoyNum = hoy.getDay();
  const target = IDX[diaStr] ?? 1;
  let diff = target - hoyNum;
  if (diff < 0) diff += 7;        // solo días ya pasados de esta semana → próxima
  const fecha = new Date(hoy);
  fecha.setDate(hoy.getDate() + diff);
  return fecha;
}

function formatearTurno(turnoStr) {
  if (!turnoStr) return null;
  try {
    const IDX = { "Lun":1,"Mar":2,"Mié":3,"Jue":4,"Vie":5,"Sáb":6,"Dom":0 };
    const partes = turnoStr.split("_");
    const dia = partes[0];
    const hora = partes[2] ? parseInt(partes[2]) : null;
    const hoy = new Date();
    const hoyNum = hoy.getDay();
    const target = IDX[dia] ?? 1;
    let diff = target - hoyNum;
    if (diff < 0) diff += 7;
    const fecha = new Date(hoy);
    fecha.setDate(hoy.getDate() + diff);
    const fechaStr = `${fecha.getDate()}/${fecha.getMonth() + 1}`;
    return hora !== null ? `${dia} ${fechaStr} a las ${hora}:00hs` : `${dia} ${fechaStr}`;
  } catch { return turnoStr.replace(/_/g, " "); }
}

// Muestra la fecha del trabajo. Prioriza la fecha REAL guardada (fecha_trabajo)
// en vez de recalcular del día de la semana (que "drifta" y manda al futuro).
function fechaTurnoStr(h) {
  if (h?.fecha_trabajo) {
    const d = new Date(h.fecha_trabajo);
    if (!isNaN(d.getTime())) {
      const dias = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];
      const hh = d.getHours();
      const mm = d.getMinutes();
      const horaTxt = (hh || mm)
        ? ` a las ${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}hs`
        : "";
      return `${dias[d.getDay()]} ${d.getDate()}/${d.getMonth() + 1}${horaTxt}`;
    }
  }
  return formatearTurno(h?.turno_solicitado);
}

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

  // Franjas ya reservadas (de otros trabajos en curso): "YYYY-MM-DD_franja".
  // Si una franja está ocupada ese día, no la ofrecemos (bloqueo por franja).
  const ocupados = plomero.ocupados || [];
  const fechaISOde = (dia) => {
    const f = getFechaParaDia(dia);
    return `${f.getFullYear()}-${String(f.getMonth() + 1).padStart(2, "0")}-${String(f.getDate()).padStart(2, "0")}`;
  };
  const franjaOcupada = (dia, franjaKey) => ocupados.includes(`${fechaISOde(dia)}_${franjaKey}`);

  // Si el día es HOY, solo se ofrecen horas desde la hora SIGUIENTE a la actual
  // (no se agenda en horarios ya pasados).
  const ahoraSel = new Date();
  const esHoy = (dia) => {
    const f = getFechaParaDia(dia);
    return f.getFullYear() === ahoraSel.getFullYear()
      && f.getMonth() === ahoraSel.getMonth()
      && f.getDate() === ahoraSel.getDate();
  };
  const horasDisponiblesDe = (dia) =>
    FRANJAS_DISP
      .filter(f => agenda[`${dia}_${f.key}`] && !franjaOcupada(dia, f.key))
      .flatMap(f => f.horas)
      .filter(hora => !esHoy(dia) || hora >= ahoraSel.getHours() + 1);

  // Días con al menos una hora disponible a futuro
  const diasDisponibles = DIAS_DISP.filter(dia => horasDisponiblesDe(dia).length > 0);

  // Horas disponibles para el día elegido
  const horasDelDia = diaElegido ? horasDisponiblesDe(diaElegido) : [];

  // Parsear turno seleccionado: "Lun_manana_9" → dia, franja, hora
  const partesTurno = turnoActual ? turnoActual.split("_") : [];
  const diaActual   = partesTurno[0] || null;
  const franjaActual = partesTurno[1] || null;
  const horaActual  = partesTurno[2] ? parseInt(partesTurno[2]) : null;

  const getFranjaPorHora = (hora) => {
    for (const f of FRANJAS_DISP) {
      if (f.horas.includes(hora)) return f.key;
    }
    return "manana";
  };

  return (
    <div onClick={e => e.stopPropagation()}>
      <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "10px",
        fontWeight: "700", color: "#94A3B8", textTransform: "uppercase",
        letterSpacing: "0.8px", marginBottom: "8px" }}>
        Elegí un turno
      </div>

      {/* Paso 1: elegir día con fecha */}
      <div style={{ marginBottom: "8px" }}>
        <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "11px",
          color: "#64748B", marginBottom: "5px" }}>Día:</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "5px" }}>
          {diasDisponibles.map(dia => {
            const esDiaActual  = diaActual === dia;
            const esDiaElegido = diaElegido === dia;
            const fecha = getFechaParaDia(dia);
            const label = `${dia} ${fecha.getDate()}/${fecha.getMonth() + 1}`;
            return (
              <button key={dia}
                onClick={() => {
                  setDiaElegido(esDiaElegido ? null : dia);
                  if (esDiaActual) onSelect(plomero.id_plomero, null);
                }}
                style={{
                  padding: "6px 11px", borderRadius: "8px",
                  border: esDiaActual ? "2px solid #3B82F6" : "1.5px solid #E2E8F0",
                  background: esDiaActual ? "#EFF6FF" : esDiaElegido ? "#F1F5F9" : "#fff",
                  color: esDiaActual ? "#1D4ED8" : "#475569",
                  fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
                  fontWeight: esDiaActual || esDiaElegido ? "700" : "500",
                  cursor: "pointer", transition: "all 0.15s",
                }}>
                {label}{esDiaActual ? " ✓" : ""}
              </button>
            );
          })}
        </div>
      </div>

      {/* Paso 2: elegir hora exacta */}
      {diaElegido && (
        <div>
          <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "11px",
            color: "#64748B", marginBottom: "5px" }}>Hora:</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "5px" }}>
            {horasDelDia.map(hora => {
              const franja = getFranjaPorHora(hora);
              const key = `${diaElegido}_${franja}_${hora}`;
              const sel = turnoActual === key;
              return (
                <button key={hora}
                  onClick={() => onSelect(plomero.id_plomero, sel ? null : key)}
                  style={{
                    padding: "7px 12px", borderRadius: "9px",
                    border: sel ? "none" : "1.5px solid #E2E8F0",
                    background: sel ? "#3B82F6" : "#F8FAFC",
                    color: sel ? "#fff" : "#475569",
                    fontFamily: "'DM Sans',sans-serif", fontSize: "13px",
                    fontWeight: "600", cursor: "pointer", transition: "all 0.15s",
                    minWidth: "52px", textAlign: "center",
                  }}>
                  {hora}:00
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Confirmación */}
      {turnoActual && diaActual && horaActual && (
        <div style={{ marginTop: "8px", background: "#F0FDF4",
          border: "1px solid #86EFAC", borderRadius: "8px",
          padding: "6px 10px", fontFamily: "'DM Sans',sans-serif",
          fontSize: "11px", color: "#15803D", fontWeight: "600" }}>
          ✓ {(() => {
            const fecha = getFechaParaDia(diaActual);
            return `${diaActual} ${fecha.getDate()}/${fecha.getMonth() + 1} a las ${horaActual}:00hs`;
          })()}
        </div>
      )}
    </div>
  );
}

// ─── SCREEN: RESULTADOS ───────────────────────────────────────────────────────

function ScreenResultados({ problema, urgencia, idsExcluidos = [], reintentarId = null, borradorId = null, onEnviar }) {
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
  const [geoMsg, setGeoMsg]       = useState("");
  const coordsRef  = useRef(null);
  const mountedRef = useRef(false); // para saber si ya hicimos la búsqueda inicial

  // Función de búsqueda reutilizable
  const buscar = useCallback(async (genero, lat, lon) => {
    setLoading(true); setError(""); setSelec([]); setTurnos({});
    try {
      const res = await api.post("/plomeros/sugerir", {
        descripcion:      problema,
        solo_mujeres:     genero === "F",
        urgencia_forzada: urgencia, // le decimos al backend que el cliente detectó urgencia
        latitud:          lat ?? -34.85,
        longitud:         lon ?? -58.38,
        // Los excluidos (rechazados/contactados) los filtra el BACKEND antes de
        // recortar a 5, así siempre completa los 5 con el resto del pool.
        excluidos:        idsExcluidos,
      });
      const todos = Array.isArray(res.data?.plomeros)
        ? res.data.plomeros
        : Array.isArray(res.data)
          ? res.data
          : [];
      setPlomeros(todos);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  }, [problema, urgencia, idsExcluidos]);

  // Al montar: definir la ubicación base y hacer la búsqueda inicial.
  // Para un servicio a domicilio, la base correcta es la DIRECCIÓN REGISTRADA
  // del cliente (la confirmó con el mapa), no el GPS del dispositivo.
  useEffect(() => {
    const u = useAuthStore.getState().user;
    if (u?.latitud != null && u?.longitud != null) {
      const lat = u.latitud, lon = u.longitud;
      coordsRef.current = { lat, lon };
      setCoords({ lat, lon });
      setGeoMsg("📍 Usando tu dirección registrada");
      setTimeout(() => setGeoMsg(""), 2000);
      buscar(filtroGenero, lat, lon);
      mountedRef.current = true;
      return;
    }
    // Sin dirección registrada con coordenadas: intentar geolocalización
    if (!navigator.geolocation) {
      buscar("todos", null, null);
      mountedRef.current = true;
      return;
    }
    setGeoMsg("📍 Obteniendo tu ubicación...");
    navigator.geolocation.getCurrentPosition(
      pos => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        coordsRef.current = { lat, lon };
        setCoords({ lat, lon });
        setGeoMsg("");
        buscar(filtroGenero, lat, lon);
        mountedRef.current = true;
      },
      () => {
        setGeoMsg("");
        buscar(filtroGenero, null, null);
        mountedRef.current = true;
      },
      { timeout: 6000 }
    );
  }, []);  // eslint-disable-line react-hooks/exhaustive-deps

  // Cuando cambia el filtro de género (después del montaje inicial)
  useEffect(() => {
    if (!mountedRef.current) return; // evitar doble búsqueda al montar
    const c = coordsRef.current;
    buscar(filtroGenero, c?.lat, c?.lon);
  }, [filtroGenero]); // eslint-disable-line react-hooks/exhaustive-deps

  const setTurno = (idPlomero, turno) => {
    setTurnos(prev => ({ ...prev, [idPlomero]: turno }));
    if (turno) {
      setSelec(prev => prev.includes(idPlomero) ? prev : [...prev, idPlomero]);
    } else {
      setSelec(prev => prev.filter(x => x !== idPlomero));
    }
  };

  // En modo URGENCIA no hay turno (va "lo antes posible"), así que la selección
  // se hace tocando la tarjeta. En modo normal la selección se hace eligiendo turno.
  const toggle = (idPlomero) => {
    if (!urgencia) return;
    setSelec(prev => prev.includes(idPlomero)
      ? prev.filter(x => x !== idPlomero)
      : [...prev, idPlomero]);
  };

  const handleEnviar = async () => {
    setEnviando(true);
    try {
      const turnosPayload = (() => {
        const t = {};
        seleccionados.forEach(id => { if (turnos[id]) t[String(id)] = turnos[id]; });
        return t;
      })();
      // 1) Reintento sobre la misma solicitud (excluye a los que rechazaron).
      // 2) Confirmar un borrador existente (lo más común): BORRADOR → PENDIENTE.
      // 3) Fallback: crear una solicitud nueva (si por algo no hubo borrador).
      let resp;
      if (reintentarId) {
        resp = await api.post(`/solicitudes/${reintentarId}/reintentar`, {
          ids_plomeros_seleccionados: seleccionados,
          turnos_por_plomero: turnosPayload,
        });
      } else if (borradorId) {
        resp = await api.post(`/solicitudes/${borradorId}/confirmar`, {
          ids_plomeros_seleccionados: seleccionados,
          turnos_por_plomero: turnosPayload,
        });
      } else {
        resp = await api.post("/solicitudes/", {
          descripcion_raw:           problema,
          solo_mujeres:              filtroGenero === "F",
          localidad_evento: useAuthStore.getState().user?.localidad || "Sin especificar",
          latitud_evento:            coords?.lat ?? -34.85,
          longitud_evento:           coords?.lon ?? -58.38,
          ids_plomeros_seleccionados: seleccionados,
          turnos_por_plomero: turnosPayload,
        });
      }
      setSolicitud(resp.data);
      setEnviado(true);
      setTimeout(() => onEnviar(resp.data), 1800);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
      setEnviando(false);
    }
  };

  // Horario tardío: de noche (21:00 a 06:59) un plomero no responde al instante,
  // así que para urgencias avisamos que se consigue a primera hora.
  const horaActual = new Date().getHours();
  const esTardio = horaActual >= 21 || horaActual < 7;

  if (enviado) return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center",
      justifyContent: "center", minHeight: "60vh", padding: "40px 24px", textAlign: "center" }}>
      <style>{`@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.12)}}`}</style>
      <div style={{ fontSize: "56px", marginBottom: "16px", animation: "pulse 1s ease infinite" }}>📡</div>
      <h2 style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
        fontSize: "22px", color: "#0F172A", margin: "0 0 8px" }}>¡Solicitud enviada!</h2>
      <p style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "15px",
        color: "#64748B", maxWidth: "360px", lineHeight: "1.6" }}>
        {urgencia
          ? (esTardio
              ? "Es de noche. Enseguida te conseguimos un profesional: les avisamos a primera hora de la mañana (7am) para que respondan cuanto antes."
              : "Notificamos a los profesionales que atienden urgencias. Te avisamos cuando alguien acepte.")
          : "Notificamos a los profesionales seleccionados. Te avisamos cuando alguien acepte el trabajo."}
      </p>
      {urgencia && (
        <div style={{ marginTop: "16px", maxWidth: "360px", background: "#FEF2F2",
          border: "1px solid #FECACA", borderRadius: "12px", padding: "12px 14px",
          fontFamily: "'DM Sans',sans-serif", fontSize: "13px", color: "#991B1B" }}>
          💡 <strong>Mientras tanto:</strong> cerrá la llave de paso principal de agua para evitar daños.
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
          ? <div style={{ textAlign: "center", padding: "56px 24px",
              border: "2px dashed #E2E8F0", borderRadius: "16px" }}>
              <div style={{ fontSize: "40px", marginBottom: "12px" }}>🙏</div>
              <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
                fontSize: "16px", color: "#475569", marginBottom: "6px" }}>
                Disculpá las molestias
              </div>
              <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "14px",
                color: "#94A3B8", maxWidth: "360px", margin: "0 auto" }}>
                No encontramos un profesional disponible en este momento. Por favor,
                volvé a intentarlo más tarde.
              </div>
            </div>
          : <div style={{ display: "grid",
              gridTemplateColumns: "repeat(auto-fill,minmax(270px,1fr))", gap: "16px" }}>
              {plomeros.map((p, i) => {
                const isSelected = seleccionados.includes(p.id_plomero);
                return (
                  <div key={p.id_plomero}
                    onClick={(e) => { if (!e.defaultPrevented) toggle(p.id_plomero); }}
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
                        letterSpacing: "0.8px", marginBottom: "7px" }}>Trabaja en</div>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "5px" }}>
                        {(p.especialidades || [p.especialidad || "PLOMERIA_GENERAL"]).map(esp => (
                          <Badge key={esp} label={ESP_LABELS[esp] || esp} />
                        ))}
                        {p.atiende_urgencias && <Badge label="Urgencias" />}
                      </div>
                    </div>

                    {/* Turno: solo si NO es urgencia */}
                    {!urgencia && (
                      <div onClick={e => e.stopPropagation()}>
                        <TurnoSelector
                          plomero={p}
                          turnoActual={turnos[p.id_plomero]}
                          onSelect={setTurno}
                        />
                      </div>
                    )}

                    {/* Urgencia: mostrar disponibilidad inmediata */}
                    {urgencia && (
                      <div style={{
                        background: p.disponible_ahora ? "#F0FDF4" : "#FEF2F2",
                        border: `1px solid ${p.disponible_ahora ? "#86EFAC" : "#FECACA"}`,
                        borderRadius: "8px", padding: "7px 12px",
                        fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
                        color: p.disponible_ahora ? "#15803D" : "#B91C1C",
                        fontWeight: "600",
                      }}>
                        {p.disponible_ahora ? "🟢 Disponible ahora" : "🔴 No disponible en este momento"}
                      </div>
                    )}

                    {isSelected && turnos[p.id_plomero] && (
                      <div style={{
                        background: "linear-gradient(135deg,#F0FDF4,#DCFCE7)",
                        border: "1.5px solid #86EFAC", borderRadius: "12px",
                        padding: "9px 12px", display: "flex",
                        alignItems: "center", gap: "6px",
                        fontFamily: "'DM Sans',sans-serif", fontSize: "13px",
                        fontWeight: "700", color: "#15803D",
                      }}>
                        <span>✓</span>
                        <span>Turno elegido — incluido en el envío</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
      }

      {/* Barra de envío — siempre visible */}
      <div style={{
        marginTop: "28px", background: "linear-gradient(135deg,#0F172A,#1E3A5F)",
        borderRadius: "20px", padding: "22px 26px",
        display: "flex", alignItems: "center",
        justifyContent: "space-between", gap: "16px", flexWrap: "wrap",
        boxShadow: "0 8px 32px rgba(15,23,42,0.2)",
      }}>
        <div>
          <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "11px",
            fontWeight: "700", textTransform: "uppercase",
            letterSpacing: "0.8px", marginBottom: "6px",
            color: seleccionados.length > 0 ? "#94A3B8" : "#475569" }}>
            {seleccionados.length > 0
              ? `${seleccionados.length} profesional${seleccionados.length > 1 ? "es" : ""} seleccionado${seleccionados.length > 1 ? "s" : ""}`
              : urgencia
                ? "Tocá una tarjeta para seleccionar al profesional"
                : "Elegí un turno para seleccionar un profesional"}
          </div>
          {seleccionados.length > 0 && (
            <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "13px", color: "#94A3B8" }}>
              {urgencia
                ? "Tienen 30 min para responder · El primero que acepte queda asignado"
                : "Tienen 3 hs para responder · El primero que acepte queda asignado"}
            </div>
          )}
        </div>
        <button
          onClick={handleEnviar}
          disabled={enviando || seleccionados.length === 0}
          style={{
            background: seleccionados.length === 0
              ? "linear-gradient(135deg,#94A3B8,#64748B)"
              : "linear-gradient(135deg,#22C55E,#16A34A)",
            color: "#fff", border: "none", borderRadius: "14px",
            padding: "13px 26px", fontFamily: "'DM Sans',sans-serif",
            fontWeight: "800", fontSize: "14px",
            cursor: (enviando || seleccionados.length === 0) ? "not-allowed" : "pointer",
            boxShadow: seleccionados.length === 0 ? "none" : "0 4px 16px rgba(34,197,94,0.35)",
            whiteSpace: "nowrap", display: "flex", alignItems: "center", gap: "8px",
            opacity: enviando ? 0.7 : 1, transition: "all 0.2s",
          }}>
          {enviando ? <Spinner size={16} color="#fff" /> : null}
          Enviar solicitud →
        </button>
      </div>
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
      await api.post(`/calificaciones/${solicitud.id_solicitud}`, {
        estrellas: rating,
        comentario: comentario || null,
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

// ─── SCREEN: MI SOLICITUD ────────────────────────────────────────────────────

// Registro local de solicitudes cerradas-sin-respuesta que el cliente ya
// "vio" (tocó Volver al inicio). Persiste entre pestañas y recargas para no
// volver a mostrar el cartel de disculpas una vez reconocido.
const CERRADAS_VISTAS_KEY = "plomeria:cerradas_vistas";

function leerCerradasVistas() {
  try { return new Set(JSON.parse(localStorage.getItem(CERRADAS_VISTAS_KEY) || "[]")); }
  catch { return new Set(); }
}

function marcarCerradaVista(id) {
  try {
    const s = leerCerradasVistas();
    s.add(id);
    localStorage.setItem(CERRADAS_VISTAS_KEY, JSON.stringify([...s]));
  } catch { /* noop */ }
}

// Tarjeta para una solicitud que se CERRÓ sola porque nadie la aceptó tras
// agotar los reintentos. Muestra disculpas + botón para volver al inicio.
function CerradaSinRespuestaCard({ h, onVolver }) {
  return (
    <div style={{ background: "#fff", borderRadius: "20px",
      border: "1px solid #EEF2F7", padding: "40px 32px",
      boxShadow: "0 8px 30px rgba(15,23,42,0.06)", textAlign: "center" }}>
      <div style={{ width: "68px", height: "68px", borderRadius: "50%",
        background: "#FFF7ED", display: "flex", alignItems: "center",
        justifyContent: "center", fontSize: "32px", margin: "0 auto 18px" }}>
        🙏
      </div>
      <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
        fontSize: "19px", color: "#0F172A", marginBottom: "10px" }}>
        Disculpá las molestias
      </div>
      <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "14px",
        color: "#64748B", lineHeight: "1.6", maxWidth: "400px", margin: "0 auto" }}>
        Probamos con varios profesionales y ninguno pudo tomar tu pedido. Cerramos
        esta solicitud; podés volver a intentarlo más tarde.
      </div>
      {h?.descripcion_raw && (
        <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "13px",
          color: "#94A3B8", fontStyle: "italic", marginTop: "12px",
          background: "#F8FAFC", borderRadius: "10px", padding: "10px 14px",
          display: "inline-block", maxWidth: "400px" }}>
          “{h.descripcion_raw}”
        </div>
      )}
      <div>
        <button onClick={onVolver} style={{
          marginTop: "24px", background: "linear-gradient(135deg,#3B82F6,#2563EB)",
          color: "#fff", border: "none", borderRadius: "12px", padding: "13px 30px",
          fontFamily: "'DM Sans',sans-serif", fontWeight: "700", fontSize: "14px",
          cursor: "pointer", boxShadow: "0 4px 14px rgba(59,130,246,0.3)",
        }}>← Volver al inicio</button>
      </div>
    </div>
  );
}

// Tarjeta de un BORRADOR: el cliente pidió diagnóstico pero todavía no envió a
// nadie. Muestra el diagnóstico y deja continuar (elegir profesional) o cancelar.
function BorradorCard({ h, onContinuar }) {
  const urgente = h.urgencia_ia === "URGENTE";
  const $ = (n) => "$" + Math.round(n || 0).toLocaleString("es-AR");
  return (
    <div style={{ background: "#fff", borderRadius: "20px", border: "1.5px solid #DBEAFE",
      padding: "22px", marginBottom: "16px", boxShadow: "0 2px 16px rgba(0,0,0,0.05)" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "14px", flexWrap: "wrap" }}>
        <span style={{ background: "#EFF6FF", color: "#1D4ED8", fontSize: "11px", fontWeight: "800",
          padding: "4px 10px", borderRadius: "999px", fontFamily: "'DM Sans',sans-serif",
          textTransform: "uppercase", letterSpacing: "0.5px" }}>📝 Pedido en preparación</span>
        {urgente && <span style={{ background: "#FEF2F2", color: "#B91C1C", fontSize: "11px",
          fontWeight: "800", padding: "4px 10px", borderRadius: "999px",
          fontFamily: "'DM Sans',sans-serif" }}>🚨 Urgencia</span>}
      </div>

      <div style={{ background: "#F8FAFC", borderRadius: "10px", padding: "10px 14px", marginBottom: "12px" }}>
        <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "10px", fontWeight: "700",
          color: "#94A3B8", textTransform: "uppercase", letterSpacing: "0.6px", marginBottom: "4px" }}>Tu problema</div>
        <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "13px", color: "#0F172A", lineHeight: "1.5" }}>
          {h.descripcion_raw}
        </div>
      </div>

      {h.diagnostico_ia && (
        <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "13px", color: "#475569",
          lineHeight: "1.5", marginBottom: "10px" }}>
          <strong>Diagnóstico:</strong> {h.diagnostico_ia}
        </div>
      )}

      {(h.presupuesto_min || h.presupuesto_max) ? (
        <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "13px", color: "#0F172A", marginBottom: "12px" }}>
          💰 Presupuesto estimado: {$(h.presupuesto_min)} – {$(h.presupuesto_max)}
        </div>
      ) : null}

      <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "12px", color: "#94A3B8",
        marginBottom: "14px", lineHeight: "1.5" }}>
        Todavía no enviaste tu pedido a ningún profesional. Elegí uno para continuar
        — si no lo enviás, se cierra solo a las 48 hs.
      </div>

      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
        <button onClick={onContinuar} style={{
          flex: 1, minWidth: "180px", background: "linear-gradient(135deg,#3B82F6,#2563EB)",
          color: "#fff", border: "none", borderRadius: "12px", padding: "12px",
          fontFamily: "'DM Sans',sans-serif", fontWeight: "700", fontSize: "14px", cursor: "pointer" }}>
          Elegir profesional →
        </button>
        <CancelarSolicitudBtn idSolicitud={h.id_solicitud} inline />
      </div>
    </div>
  );
}

function SolicitudCard({ h, onReSolicitar }) {
  const estado = (h.estado || "").toUpperCase();
  const ahora  = new Date();
  // Para el temporizador usamos el último envío real (reintentos resetean el reloj)
  const refFecha = h.fecha_ultimo_envio || h.fecha;
  const mins   = refFecha ? (ahora - new Date(refFecha)) / 1000 / 60 : 0;
  const limite = h.urgencia_ia === "URGENTE" ? 30 : 180;
  const sinRespuesta = estado === "SIN_RESPUESTA";           // todos rechazaron
  const reasignacion = estado === "REASIGNACION_PENDIENTE";  // el plomero asignado canceló
  const vencida = estado === "PENDIENTE" && mins > limite;   // nadie respondió a tiempo
  const necesitaAccion = sinRespuesta || vencida || reasignacion;
  const intentosRestantes = h.intentos_restantes ?? 3;

  const ESTADOS = [
    { key: "pendiente",              label: "Solicitud enviada",           icon: "📡", desc: "Esperando que un profesional acepte" },
    { key: "en_progreso",            label: "Trabajo aceptado",            icon: "✅", desc: "Un profesional aceptó tu solicitud" },
    { key: "en_camino",              label: "El profesional va en camino", icon: "🚗", desc: "Ya está yendo a tu domicilio" },
    { key: "pendiente_calificacion", label: "Trabajo finalizado",          icon: "🏁", desc: "Podés calificar el servicio" },
  ];
  const estadoNorm = (estado || "").toLowerCase();
  const idxActual = ESTADOS.findIndex(e => e.key === estadoNorm);

  return (
    <div style={{ background: "#fff", borderRadius: "20px",
      border: necesitaAccion ? "1.5px solid #FECACA" : "1.5px solid #F1F5F9",
      padding: "20px", marginBottom: "16px",
      boxShadow: "0 2px 16px rgba(0,0,0,0.05)" }}>

      {necesitaAccion && (
        <div style={{ background: "#FEF2F2", border: "1px solid #FECACA",
          borderRadius: "12px", padding: "14px 16px", marginBottom: "16px",
          display: "flex", gap: "10px", alignItems: "flex-start" }}>
          <span style={{ fontSize: "18px" }}>{reasignacion ? "⚠️" : sinRespuesta ? "🙅" : "⏰"}</span>
          <div style={{ flex: 1 }}>
            <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
              fontSize: "13px", color: "#B91C1C", marginBottom: "4px" }}>
              {reasignacion
                ? "El profesional canceló el trabajo"
                : sinRespuesta
                  ? "Los profesionales rechazaron tu pedido"
                  : "Nadie respondió esta solicitud"}
            </div>
            <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
              color: "#7F1D1D", marginBottom: "10px" }}>
              {intentosRestantes > 0
                ? `Volvé a buscar otros profesionales (te queda${intentosRestantes !== 1 ? "n" : ""} ${intentosRestantes} intento${intentosRestantes !== 1 ? "s" : ""}) o cancelá la solicitud.`
                : "Se agotaron los reintentos. Cancelá la solicitud para cerrarla."}
            </div>
            <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
              {intentosRestantes > 0 && (
                <button onClick={() => onReSolicitar(h)} style={{
                  background: "linear-gradient(135deg,#EF4444,#B91C1C)",
                  color: "#fff", border: "none", borderRadius: "8px",
                  padding: "7px 14px", fontFamily: "'DM Sans',sans-serif",
                  fontWeight: "700", fontSize: "12px", cursor: "pointer",
                }}>Volver a buscar →</button>
              )}
              <CancelarSolicitudBtn idSolicitud={h.id_solicitud} inline />
            </div>
          </div>
        </div>
      )}

      <div style={{ background: "#F8FAFC", borderRadius: "10px",
        padding: "10px 14px", marginBottom: "16px" }}>
        <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "10px",
          fontWeight: "700", color: "#94A3B8", textTransform: "uppercase",
          letterSpacing: "0.6px", marginBottom: "4px" }}>Tu problema</div>
        <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "13px",
          color: "#0F172A", lineHeight: "1.5" }}>{h.descripcion_raw}</div>
        <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "11px",
          color: "#94A3B8", marginTop: "6px" }}>
          {h.fecha ? new Date(h.fecha).toLocaleString("es-AR") : ""}
        </div>
      </div>

      <div style={{ padding: "4px 0", marginBottom: "16px" }}>
        {ESTADOS.map((e, i) => {
          const completado = i < idxActual;
          const current    = i === idxActual;
          const pendiente  = i > idxActual;
          return (
            <div key={e.key} style={{ display: "flex", gap: "12px",
              alignItems: "flex-start", marginBottom: i < ESTADOS.length - 1 ? "16px" : 0 }}>
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                <div style={{
                  width: "36px", height: "36px", borderRadius: "50%",
                  background: current ? "linear-gradient(135deg,#3B82F6,#2563EB)"
                    : completado ? "#F0FDF4" : "#F1F5F9",
                  border: current ? "none" : completado ? "2px solid #86EFAC" : "2px solid #E2E8F0",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: "15px", flexShrink: 0, opacity: pendiente ? 0.4 : 1,
                  boxShadow: current ? "0 3px 12px rgba(59,130,246,0.3)" : "none",
                }}>{completado ? "✓" : e.icon}</div>
                {i < ESTADOS.length - 1 && (
                  <div style={{ width: "2px", height: "16px", marginTop: "3px",
                    background: completado ? "#86EFAC" : "#E2E8F0" }} />
                )}
              </div>
              <div style={{ paddingTop: "6px" }}>
                <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "700",
                  fontSize: "13px",
                  color: current ? "#0F172A" : completado ? "#15803D" : "#94A3B8" }}>
                  {e.label}
                </div>
                {current && (
                  <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
                    color: "#64748B", marginTop: "2px" }}>{e.desc}</div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {estado === "PENDIENTE" && !vencida && h.plomeros_notificados?.length > 0 && (
        <div style={{ background: "#F8FAFC", borderRadius: "12px",
          border: "1px solid #E2E8F0", padding: "14px 16px", marginBottom: "12px" }}>
          <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "700",
            fontSize: "10px", color: "#94A3B8", textTransform: "uppercase",
            letterSpacing: "0.6px", marginBottom: "4px" }}>
            Profesionales notificados ({h.plomeros_notificados.length})
          </div>
          <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "11px",
            color: "#64748B", marginBottom: "10px" }}>
            El primero que acepte queda asignado.
          </div>
          {h.plomeros_notificados.map((p, idx) => (
            <div key={p.id_plomero} style={{
              display: "flex", gap: "10px", alignItems: "center",
              paddingTop: idx > 0 ? "8px" : 0,
              paddingBottom: idx < h.plomeros_notificados.length - 1 ? "8px" : 0,
              borderBottom: idx < h.plomeros_notificados.length - 1 ? "1px solid #F1F5F9" : "none",
            }}>
              <Avatar src={p.foto_perfil_path} nombre={p.nombre} apellido={p.apellido} size={38} />
              <div style={{ flex: 1 }}>
                <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "700",
                  fontSize: "13px", color: "#0F172A" }}>{p.nombre} {p.apellido}</div>
                <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "11px", color: "#94A3B8" }}>
                  📍 {p.localidad}{p.puntuacion > 0 ? ` · ⭐ ${p.puntuacion?.toFixed(1)}` : ""}
                </div>
              </div>
              <div style={{ background: "#FFFBEB", border: "1px solid #FDE68A",
                borderRadius: "6px", padding: "3px 8px",
                fontFamily: "'DM Sans',sans-serif", fontSize: "10px",
                color: "#92400E", fontWeight: "600" }}>⏳ Esperando</div>
            </div>
          ))}
        </div>
      )}

      {(h.id_plomero || h.nombre_plomero) && (
        <div style={{ background: "linear-gradient(135deg,#F0FDF4,#ECFDF5)",
          border: "1.5px solid #86EFAC", borderRadius: "14px", padding: "14px 16px" }}>
          <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "700",
            fontSize: "10px", color: "#15803D", textTransform: "uppercase",
            letterSpacing: "0.6px", marginBottom: "10px" }}>✅ Profesional asignado</div>
          <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
            <Avatar
              src={h.foto_plomero || h.plomero?.foto_perfil_path}
              nombre={(h.nombre_plomero || h.plomero?.nombre || "P").split(" ")[0]}
              apellido={(h.nombre_plomero || "").split(" ").slice(1).join(" ") || h.plomero?.apellido || ""}
              size={52}
            />
            <div style={{ flex: 1 }}>
              <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
                fontSize: "16px", color: "#0F172A" }}>
                {h.nombre_plomero || (h.plomero ? `${h.plomero.nombre} ${h.plomero.apellido}` : "Profesional asignado")}
              </div>
              <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
                color: "#64748B", marginTop: "3px" }}>
                📍 {h.localidad_plomero || h.plomero?.localidad || "—"}
              </div>
              {(h.fecha_trabajo || h.turno_solicitado) ? (
                <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "13px",
                  color: "#15803D", fontWeight: "700", marginTop: "6px",
                  background: "#DCFCE7", borderRadius: "6px", padding: "4px 8px",
                  display: "inline-block" }}>
                  📅 {fechaTurnoStr(h)}
                </div>
              ) : (
                <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
                  color: "#94A3B8", marginTop: "4px" }}>📅 Horario a confirmar</div>
              )}
            </div>
          </div>
        </div>
      )}

      {h.presupuesto_max > 0 && (
        <div style={{ background: "#FFFBEB", border: "1px solid #FDE68A", borderRadius: "10px",
          padding: "10px 14px", marginTop: "12px", fontFamily: "'DM Sans',sans-serif",
          fontSize: "12px", color: "#92400E" }}>
          💰 Presupuesto estimado (materiales): <strong>${Number(h.presupuesto_min || 0).toLocaleString("es-AR")} – ${Number(h.presupuesto_max || 0).toLocaleString("es-AR")}</strong>
        </div>
      )}

      <BoletaMateriales idSolicitud={h.id_solicitud} diagnostico={h.diagnostico_ia || h.etiqueta_ia} fecha={h.fecha} />

      {(estadoNorm === "pendiente" || estadoNorm === "en_progreso" || estadoNorm === "en_camino") && !vencida && (
        <CancelarSolicitudBtn idSolicitud={h.id_solicitud} />
      )}
    </div>
  );
}

function CancelarSolicitudBtn({ idSolicitud, inline = false }) {
  const [confirmando, setConfirmando] = useState(false);
  const [loading, setLoading]         = useState(false);
  const [cancelada, setCancelada]     = useState(false);

  const handleCancelar = async () => {
    setLoading(true);
    try {
      await api.patch(`/solicitudes/${idSolicitud}/cancelar`);
      setCancelada(true);
    } catch {
      setCancelada(true);
    } finally {
      setLoading(false);
      setConfirmando(false);
    }
  };

  if (cancelada) return (
    <div style={{
      marginTop: inline ? 0 : "12px",
      background: "#F8FAFC", borderRadius: "8px", padding: "6px 12px",
      fontFamily: "'DM Sans',sans-serif", fontSize: "12px", color: "#94A3B8",
    }}>
      Solicitud cancelada
    </div>
  );

  if (confirmando) return (
    <div style={{
      marginTop: inline ? 0 : "12px",
      background: inline ? "rgba(0,0,0,0.08)" : "#FEF2F2",
      border: inline ? "none" : "1px solid #FECACA",
      borderRadius: "10px", padding: "10px 12px",
      display: "flex", gap: "8px", alignItems: "center", flexWrap: "wrap",
    }}>
      <span style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
        color: inline ? "#fff" : "#B91C1C", fontWeight: "600" }}>
        ¿Cancelar?
      </span>
      <div style={{ display: "flex", gap: "6px" }}>
        <button onClick={() => setConfirmando(false)} style={{
          background: "#F8FAFC", border: "1px solid #E2E8F0",
          borderRadius: "6px", padding: "4px 10px",
          fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
          color: "#475569", cursor: "pointer", fontWeight: "600",
        }}>No</button>
        <button onClick={handleCancelar} disabled={loading} style={{
          background: "#EF4444", border: "none", borderRadius: "6px",
          padding: "4px 10px", fontFamily: "'DM Sans',sans-serif",
          fontSize: "12px", color: "#fff", cursor: "pointer", fontWeight: "700",
        }}>{loading ? "..." : "Sí"}</button>
      </div>
    </div>
  );

  if (inline) return (
    <button onClick={() => setConfirmando(true)} style={{
      background: "rgba(0,0,0,0.15)", border: "1px solid rgba(255,255,255,0.2)",
      borderRadius: "8px", padding: "7px 14px",
      fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
      color: "#fff", cursor: "pointer", fontWeight: "600",
    }}>
      Cancelar solicitud
    </button>
  );

  return (
    <button onClick={() => setConfirmando(true)} style={{
      marginTop: "12px", width: "100%", background: "transparent",
      border: "1px solid #E2E8F0", borderRadius: "10px", padding: "9px",
      fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
      color: "#94A3B8", cursor: "pointer", fontWeight: "600",
      transition: "all 0.15s",
    }}
    onMouseEnter={e => { e.target.style.borderColor = "#FECACA"; e.target.style.color = "#EF4444"; }}
    onMouseLeave={e => { e.target.style.borderColor = "#E2E8F0"; e.target.style.color = "#94A3B8"; }}
    >
      Cancelar solicitud
    </button>
  );
}


function CalificarPlomeroInline({ idSolicitud, nombrePlomero, onRated }) {
  const [rating, setRating]   = useState(0);
  const [coment, setComent]   = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");

  const enviar = async () => {
    if (!rating) return;
    setLoading(true); setError("");
    try {
      await api.post(`/calificaciones/${idSolicitud}`, { estrellas: rating, comentario: coment || null });
      if (onRated) onRated();
    } catch (e) {
      setError(e.response?.data?.detail || "No se pudo enviar la calificación.");
      setLoading(false);
    }
  };

  return (
    <div style={{ background:"#fff", borderRadius:"16px", border:"2px solid #FEF3C7",
      padding:"20px", marginBottom:"16px", boxShadow:"0 4px 20px rgba(0,0,0,0.06)" }}>
      <div style={{ display:"flex", alignItems:"center", gap:"10px", marginBottom:"14px" }}>
        <div style={{ fontSize:"22px" }}>🏁</div>
        <div>
          <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
            fontSize:"15px", color:"#B45309" }}>Trabajo finalizado</div>
          <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px", color:"#94A3B8" }}>
            Calificá a {nombrePlomero || "tu plomero"}
          </div>
        </div>
      </div>
      <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px", fontWeight:"700",
        color:"#64748B", marginBottom:"8px" }}>¿Cómo estuvo el trabajo?</div>
      <div style={{ display:"flex", gap:"6px", marginBottom:"10px" }}>
        {[1,2,3,4,5].map(i => (
          <button key={i} onClick={() => setRating(i)} disabled={loading}
            style={{ width:"34px", height:"34px", borderRadius:"8px",
              border: rating >= i ? "2px solid #F59E0B" : "2px solid #E2E8F0",
              background: rating >= i ? "#FFFBEB" : "#F8FAFC",
              fontSize:"16px", cursor:"pointer" }}>⭐</button>
        ))}
      </div>
      {rating > 0 && (
        <>
          <textarea value={coment} onChange={e => setComent(e.target.value)}
            placeholder="Contá tu experiencia (opcional)..." rows={2}
            style={{ width:"100%", borderRadius:"10px", padding:"10px 12px",
              border:"1.5px solid #E2E8F0", fontFamily:"'DM Sans',sans-serif",
              fontSize:"13px", color:"#0F172A", resize:"none", outline:"none",
              boxSizing:"border-box", background:"#F8FAFC", marginBottom:"8px" }} />
          <button onClick={enviar} disabled={loading}
            style={{ width:"100%", background:"linear-gradient(135deg,#F59E0B,#D97706)",
              color:"#fff", border:"none", borderRadius:"10px", padding:"10px",
              fontFamily:"'DM Sans',sans-serif", fontWeight:"700", fontSize:"13px",
              cursor:"pointer" }}>
            {loading ? "Enviando…" : "Enviar valoración ⭐"}
          </button>
        </>
      )}
      {error && (
        <div style={{ marginTop:"8px", color:"#B91C1C", fontSize:"12px",
          fontFamily:"'DM Sans',sans-serif", fontWeight:"600" }}>{error}</div>
      )}
    </div>
  );
}

function ScreenMiSolicitud({ historial, loading, onNav, onReSolicitar, onContinuarBorrador, onRated }) {
  const [vistas, setVistas] = useState(leerCerradasVistas);

  // Al tocar "Volver al inicio": marca la cerrada como vista (no vuelve a aparecer) y navega.
  const volverAlInicio = (id) => {
    if (id) { marcarCerradaVista(id); setVistas(leerCerradasVistas()); }
    onNav("problema");
  };

  const activas = historial
    .filter(h => {
      const e = (h.estado || "").toLowerCase();
      // Solo activas. pendiente_calificacion ya es un trabajo terminado → va en Finalizados.
      // sin_respuesta = todos rechazaron y sigue abierta para volver a buscar o cancelar.
      // cerrada_sin_respuesta = se cerró sola (nadie aceptó): mostramos el cartel de disculpas
      // SOLO hasta que el cliente lo reconoce con "Volver al inicio".
      if (e === "cancelada" && h.cerrada_sin_respuesta) {
        return !vistas.has(h.id_solicitud);
      }
      // borrador = pedido en preparación (diagnóstico pedido, todavía sin enviar a nadie).
      return e === "borrador" || e === "pendiente" || e === "en_progreso" || e === "en_camino"
        || e === "reasignacion_pendiente" || e === "sin_respuesta"
        || (e === "pendiente_calificacion" && !h.cliente_califico);
    })
    .sort((a, b) => new Date(b.fecha) - new Date(a.fecha));

  if (loading) return (
    <div style={{ display: "flex", justifyContent: "center", padding: "80px" }}>
      <Spinner size={36} />
    </div>
  );

  if (activas.length === 0) return (
    <div style={{ maxWidth: "600px", margin: "0 auto", padding: "60px 24px", textAlign: "center" }}>
      <div style={{ fontSize: "52px", marginBottom: "16px" }}>📭</div>
      <h2 style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
        fontSize: "20px", color: "#0F172A", margin: "0 0 8px" }}>
        No tenés solicitudes activas
      </h2>
      <p style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "14px",
        color: "#64748B", marginBottom: "24px" }}>
        Cuando enviés una solicitud, vas a poder seguir su estado acá.
      </p>
      <button onClick={() => onNav("problema")} style={{
        background: "linear-gradient(135deg,#3B82F6,#2563EB)",
        color: "#fff", border: "none", borderRadius: "12px",
        padding: "12px 28px", fontFamily: "'DM Sans',sans-serif",
        fontWeight: "700", fontSize: "14px", cursor: "pointer",
      }}>Solicitar un plomero →</button>
    </div>
  );

  // Si lo único "activo" son solicitudes que se cerraron sin respuesta, mostramos
  // SOLO el cartel de disculpas (sin encabezado "activas" ni botón duplicado).
  const soloCerradas = activas.length > 0 && activas.every(h => h.cerrada_sin_respuesta);
  if (soloCerradas) return (
    <div style={{ maxWidth: "560px", margin: "0 auto", padding: "56px 24px" }}>
      {activas.map(h => (
        <CerradaSinRespuestaCard key={h.id_solicitud} h={h} onVolver={() => volverAlInicio(h.id_solicitud)} />
      ))}
    </div>
  );

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto", padding: "32px 24px" }}>
      <h1 style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
        fontSize: "22px", color: "#0F172A", letterSpacing: "-0.4px", margin: "0 0 6px" }}>
        Mis solicitudes activas
      </h1>
      <p style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "13px",
        color: "#94A3B8", margin: "0 0 24px" }}>
        {activas.length} solicitud{activas.length > 1 ? "es" : ""} en curso
      </p>

      {activas.map(h => (
        h.cerrada_sin_respuesta
          ? <CerradaSinRespuestaCard key={h.id_solicitud} h={h} onVolver={() => volverAlInicio(h.id_solicitud)} />
          : (h.estado || "").toLowerCase() === "pendiente_calificacion"
            ? <CalificarPlomeroInline key={h.id_solicitud} idSolicitud={h.id_solicitud} nombrePlomero={h.nombre_plomero} onRated={onRated} />
          : (h.estado || "").toLowerCase() === "borrador"
            ? <BorradorCard key={h.id_solicitud} h={h} onContinuar={() => onContinuarBorrador(h)} />
            : <SolicitudCard key={h.id_solicitud} h={h} onReSolicitar={onReSolicitar} />
      ))}

      <button onClick={() => onNav("problema")} style={{
        width: "100%", background: "#F8FAFC", border: "1.5px solid #E2E8F0",
        borderRadius: "12px", padding: "12px", marginTop: "4px",
        fontFamily: "'DM Sans',sans-serif", fontWeight: "600",
        fontSize: "14px", color: "#475569", cursor: "pointer",
      }}>← Volver al inicio</button>
    </div>
  );
}


// ─── RE-SOLICITAR A UN PLOMERO ESPECÍFICO (inline, desde Finalizados) ─────────

function ReSolicitarForm({ plomeroId, plomeroNombre, onResolicitado, onCancel }) {
  const [plomero, setPlomero]   = useState(null);
  const [turno, setTurno]       = useState(null);
  const [problema, setProblema] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [error, setError]       = useState("");

  useEffect(() => {
    api.get(`/plomeros/${plomeroId}`)
      .then(res => setPlomero(res.data))
      .catch(() => setPlomero({ id_plomero: plomeroId, agenda: null }));
  }, [plomeroId]);

  const hayAgenda = plomero?.agenda && Object.values(plomero.agenda).some(Boolean);
  const URGENCIA_KW = ["inunda", "pérdida", "perder", "no cierra", "roto", "explota",
    "revienta", "urgente", "emergencia", "fuga", "chorrea", "sale agua", "brota",
    "no para", "caño roto", "cano roto", "sin agua", "gas"];
  const esUrgente = URGENCIA_KW.some(k => problema.toLowerCase().includes(k));
  // Si es urgencia no exigimos turno (va "lo antes posible").
  const puedeEnviar = problema.trim().length > 0
    && (esUrgente || !!turno || (plomero && !hayAgenda)) && !enviando;

  const enviar = async () => {
    if (!puedeEnviar) return;
    setEnviando(true); setError("");
    try {
      const resp = await api.post("/solicitudes/", {
        descripcion_raw:            problema,
        solo_mujeres:               false,
        localidad_evento:           useAuthStore.getState().user?.localidad || "Sin especificar",
        latitud_evento:             -34.85,
        longitud_evento:            -58.38,
        ids_plomeros_seleccionados: [plomeroId],
        turnos_por_plomero:         turno ? { [String(plomeroId)]: turno } : {},
      });
      onResolicitado(resp.data);
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
      setEnviando(false);
    }
  };

  return (
    <div style={{ marginTop: "14px", borderTop: "1px solid #F1F5F9", paddingTop: "14px" }}>
      <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
        fontSize: "14px", color: "#0F172A", marginBottom: "10px" }}>
        Volver a solicitar a {plomeroNombre}
      </div>

      {!plomero ? (
        <div style={{ display: "flex", justifyContent: "center", padding: "16px" }}>
          <Spinner size={20} />
        </div>
      ) : (
        <>
          {plomero.disponible_ahora === false && (
            <div style={{ marginBottom: "12px", background: "#FFFBEB",
              border: "1.5px solid #FDE68A", borderRadius: "10px", padding: "12px 14px",
              fontFamily: "'DM Sans',sans-serif", fontSize: "12px", color: "#92400E" }}>
              ⚠️ <strong>{plomeroNombre} está inactivo en este momento.</strong> Podés proponerle
              una visita igual: le avisamos por correo y tiene <strong>72 horas</strong> para
              responder. Si no responde o la rechaza, tu solicitud queda activa y vas a poder
              buscar otros profesionales disponibles.
            </div>
          )}

          {/* 1) Describir el problema (primero) */}
          <div style={{ marginBottom: "10px" }}>
            <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
              fontWeight: "700", color: "#64748B", marginBottom: "6px" }}>
              Contanos el problema
            </div>
            <textarea
              value={problema}
              onChange={e => setProblema(e.target.value)}
              placeholder="Describí qué necesitás resolver..."
              rows={3}
              style={{ width: "100%", borderRadius: "10px", padding: "10px 12px",
                border: "1.5px solid #E2E8F0", fontFamily: "'DM Sans',sans-serif",
                fontSize: "13px", color: "#0F172A", resize: "none",
                outline: "none", boxSizing: "border-box", background: "#F8FAFC" }}
            />
          </div>

          {/* 2) Urgencia → solución inmediata + lo antes posible; si no, elegir turno */}
          {esUrgente ? (
            <div style={{ background: "#FEF2F2", border: "1px solid #FECACA", borderRadius: "10px",
              padding: "10px 12px", fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
              color: "#991B1B", marginBottom: "4px" }}>
              🚨 <strong>Urgencia detectada.</strong> Se enviará para <strong>lo antes posible</strong>.
              Mientras tanto, cerrá la llave de paso principal de agua. Si {plomeroNombre} no puede,
              vas a poder buscar profesionales disponibles ya.
            </div>
          ) : hayAgenda ? (
            <TurnoSelector
              plomero={plomero}
              turnoActual={turno}
              onSelect={(_id, t) => setTurno(t)}
            />
          ) : (
            <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
              color: "#94A3B8", fontStyle: "italic", marginBottom: "8px" }}>
              Este profesional coordinará el horario directamente.
            </div>
          )}

          <div style={{ display: "flex", gap: "8px", marginTop: "10px" }}>
            <button onClick={onCancel} style={{
              background: "#F8FAFC", border: "1.5px solid #E2E8F0", borderRadius: "10px",
              padding: "10px 14px", fontFamily: "'DM Sans',sans-serif", fontWeight: "600",
              fontSize: "13px", color: "#475569", cursor: "pointer" }}>
              Cancelar
            </button>
            <button onClick={enviar} disabled={!puedeEnviar} style={{
              flex: 1, background: puedeEnviar ? "linear-gradient(135deg,#3B82F6,#2563EB)" : "#E2E8F0",
              color: puedeEnviar ? "#fff" : "#94A3B8", border: "none", borderRadius: "10px",
              padding: "10px", fontFamily: "'DM Sans',sans-serif", fontWeight: "700",
              fontSize: "13px", cursor: puedeEnviar ? "pointer" : "not-allowed",
              display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
              {enviando ? <Spinner size={14} color="#fff" /> : null}
              {plomero.disponible_ahora === false ? "Proponer visita" : "Enviar solicitud"}
            </button>
          </div>

          {error && (
            <div style={{ marginTop: "8px", color: "#B91C1C", fontSize: "12px",
              fontFamily: "'DM Sans',sans-serif", fontWeight: "600" }}>
              {error}
            </div>
          )}
        </>
      )}
    </div>
  );
}

// ─── SCREEN: TRABAJOS FINALIZADOS ─────────────────────────────────────────────

// Reseñas públicas de un plomero (reales + ficticias del backend)
function ResenasPlomero({ idPlomero }) {
  const [data, setData] = useState(null);
  useEffect(() => {
    let ok = true;
    api.get(`/plomeros/${idPlomero}/resenas`).then(r => { if (ok) setData(r.data); }).catch(() => {});
    return () => { ok = false; };
  }, [idPlomero]);
  if (!data) return null;
  return (
    <div style={{ background: "#F8FAFC", borderRadius: "12px", padding: "14px", marginBottom: "14px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
        <span style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800", fontSize: "15px", color: "#92400E" }}>
          ⭐ {Number(data.puntuacion || 0).toFixed(1)}
        </span>
        <span style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "12px", color: "#94A3B8" }}>
          Puntuación pública · {data.total_trabajos} trabajos
        </span>
      </div>
      {(data.resenas || []).map((r, i) => (
        <div key={i} style={{ borderTop: i ? "1px solid #E2E8F0" : "none", padding: "8px 0" }}>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "700", fontSize: "13px", color: "#0F172A" }}>{r.autor}</span>
            <span style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "12px", color: "#92400E", fontWeight: "700" }}>⭐ {Number(r.estrellas).toFixed(1)}</span>
          </div>
          <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "12px", color: "#64748B", fontStyle: "italic", marginTop: "2px" }}>"{r.comentario}"</div>
        </div>
      ))}
    </div>
  );
}

function ScreenTrabajosFinalizados({ historial, loading, onResolicitado }) {
  const [rating, setRating]     = useState({});
  const [comentario, setComent] = useState({});
  const [valorado, setValorado] = useState({});
  const [loadingCal, setLoadingCal] = useState({});
  const [errorCal, setErrorCal] = useState({});
  const [abierto, setAbierto] = useState(null);   // id_plomero expandido
  const [reSolic, setReSolic] = useState(null);   // id_plomero del form de recontacto

  const finalizados = historial
    .filter(h => {
      const e = (h.estado || "").toLowerCase();
      return e === "completada" || e === "completado"
        || e === "finalizado" || e === "pendiente_calificacion";
    })
    .sort((a, b) => new Date(b.fecha) - new Date(a.fecha));

  const handleCalificar = async (h) => {
    const stars = rating[h.id_solicitud];
    if (!stars) return;
    setLoadingCal(prev => ({ ...prev, [h.id_solicitud]: true }));
    setErrorCal(prev => ({ ...prev, [h.id_solicitud]: null }));
    try {
      await api.post(`/calificaciones/${h.id_solicitud}`, {
        estrellas: stars,
        comentario: comentario[h.id_solicitud] || null,
      });
      setValorado(prev => ({ ...prev, [h.id_solicitud]: true }));
    } catch (e) {
      setErrorCal(prev => ({
        ...prev,
        [h.id_solicitud]: e.response?.data?.detail || "No se pudo enviar la calificación.",
      }));
    } finally {
      setLoadingCal(prev => ({ ...prev, [h.id_solicitud]: false }));
    }
  };

  // Render de un trabajo dentro del detalle del plomero
  const renderTrabajo = (h) => (
    <div key={h.id_solicitud} style={{ border: "1px solid #F1F5F9", borderRadius: "12px",
      padding: "14px", marginBottom: "10px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: "8px", marginBottom: "6px" }}>
        <span style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "700", fontSize: "13px", color: "#0F172A" }}>
          {h.diagnostico_ia || `"${h.descripcion_raw}"`}
        </span>
        <span style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "11px", color: "#94A3B8", whiteSpace: "nowrap" }}>
          {h.fecha ? new Date(h.fecha).toLocaleDateString("es-AR") : ""}
        </span>
      </div>

      <BoletaMateriales idSolicitud={h.id_solicitud} diagnostico={h.diagnostico_ia || h.etiqueta_ia} fecha={h.fecha} />

      {(h.cliente_califico || valorado[h.id_solicitud])
        ? <div style={{ marginTop: "10px", background: "#F0FDF4", border: "1px solid #86EFAC",
            borderRadius: "10px", padding: "10px 14px", fontFamily: "'DM Sans',sans-serif",
            fontSize: "13px", color: "#15803D", fontWeight: "600" }}>
            ✓ Gracias por tu valoración
          </div>
        : (h.estado || "").toLowerCase() !== "pendiente_calificacion"
        ? <div style={{ marginTop: "10px", background: "#F8FAFC", border: "1px solid #E2E8F0",
            borderRadius: "10px", padding: "10px 14px", fontFamily: "'DM Sans',sans-serif",
            fontSize: "13px", color: "#94A3B8", fontWeight: "600" }}>
            Trabajo cerrado, no admite calificación.
          </div>
        : <div style={{ marginTop: "10px" }}>
            <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
              fontWeight: "700", color: "#64748B", marginBottom: "8px" }}>
              ¿Cómo estuvo el trabajo?
            </div>
            <div style={{ display: "flex", gap: "6px", marginBottom: "10px" }}>
              {[1,2,3,4,5].map(i => (
                <button key={i}
                  onClick={() => setRating(prev => ({ ...prev, [h.id_solicitud]: i }))}
                  style={{
                    width: "34px", height: "34px", borderRadius: "8px",
                    border: rating[h.id_solicitud] >= i ? "2px solid #F59E0B" : "2px solid #E2E8F0",
                    background: rating[h.id_solicitud] >= i ? "#FFFBEB" : "#F8FAFC",
                    fontSize: "16px", cursor: "pointer",
                    display: "flex", alignItems: "center", justifyContent: "center",
                  }}>⭐</button>
              ))}
            </div>
            {rating[h.id_solicitud] > 0 && (
              <>
                <textarea
                  value={comentario[h.id_solicitud] || ""}
                  onChange={e => setComent(prev => ({ ...prev, [h.id_solicitud]: e.target.value }))}
                  placeholder="Contá tu experiencia (opcional)..."
                  rows={2}
                  style={{ width: "100%", borderRadius: "10px", padding: "10px 12px",
                    border: "1.5px solid #E2E8F0", fontFamily: "'DM Sans',sans-serif",
                    fontSize: "13px", color: "#0F172A", resize: "none",
                    outline: "none", boxSizing: "border-box", background: "#F8FAFC", marginBottom: "8px" }}
                />
                <button onClick={() => handleCalificar(h)} disabled={loadingCal[h.id_solicitud]}
                  style={{ width: "100%", background: "linear-gradient(135deg,#F59E0B,#D97706)",
                    color: "#fff", border: "none", borderRadius: "10px", padding: "10px",
                    fontFamily: "'DM Sans',sans-serif", fontWeight: "700", fontSize: "13px", cursor: "pointer",
                    display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
                  {loadingCal[h.id_solicitud] ? <Spinner size={14} color="#fff" /> : null}
                  Enviar valoración ⭐
                </button>
                {errorCal[h.id_solicitud] && (
                  <div style={{ marginTop: "8px", color: "#B91C1C", fontSize: "12px",
                    fontFamily: "'DM Sans',sans-serif", fontWeight: "600" }}>
                    {errorCal[h.id_solicitud]}
                  </div>
                )}
              </>
            )}
          </div>
      }
    </div>
  );

  if (loading) return (
    <div style={{ display: "flex", justifyContent: "center", padding: "80px" }}>
      <Spinner size={36} />
    </div>
  );

  // Agrupar trabajos por plomero
  const porPlomero = {};
  finalizados.forEach(h => {
    if (!h.id_plomero) return;
    const pid = h.id_plomero;
    porPlomero[pid] = porPlomero[pid] || {
      id: pid, nombre: h.nombre_plomero, foto: h.foto_plomero,
      localidad: h.localidad_plomero, jobs: [],
    };
    porPlomero[pid].jobs.push(h);
  });
  const plomeros = Object.values(porPlomero)
    .sort((a, b) => new Date(b.jobs[0].fecha) - new Date(a.jobs[0].fecha));

  return (
    <div style={{ maxWidth: "640px", margin: "0 auto", padding: "32px 24px" }}>
      <h1 style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
        fontSize: "22px", color: "#0F172A", letterSpacing: "-0.4px", margin: "0 0 6px" }}>
        Trabajos finalizados
      </h1>
      <p style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "13px",
        color: "#94A3B8", margin: "0 0 24px" }}>
        Por profesional
      </p>

      {plomeros.length === 0
        ? <div style={{ textAlign: "center", padding: "60px 20px",
            border: "2px dashed #E2E8F0", borderRadius: "16px" }}>
            <div style={{ fontSize: "36px", marginBottom: "12px" }}>✅</div>
            <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "700",
              fontSize: "15px", color: "#94A3B8" }}>
              Todavía no tenés trabajos finalizados.
            </div>
          </div>
        : plomeros.map(p => {
          const open = abierto === p.id;
          return (
            <div key={p.id} style={{ background: "#fff", borderRadius: "20px",
              border: "1.5px solid #F1F5F9", marginBottom: "16px",
              boxShadow: "0 2px 12px rgba(0,0,0,0.04)", overflow: "hidden" }}>
              <button onClick={() => setAbierto(open ? null : p.id)}
                style={{ width: "100%", background: "transparent", border: "none", cursor: "pointer",
                  padding: "18px 20px", display: "flex", alignItems: "center", gap: "14px", textAlign: "left" }}>
                <Avatar src={p.foto}
                  nombre={p.nombre?.split(" ")[0] || "P"}
                  apellido={p.nombre?.split(" ").slice(1).join(" ") || ""} size={52} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
                    fontSize: "16px", color: "#0F172A" }}>{p.nombre || "Plomero"}</div>
                  <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "12px", color: "#64748B", marginTop: "2px" }}>
                    📍 {p.localidad || "—"} · {p.jobs.length} trabajo{p.jobs.length !== 1 ? "s" : ""}
                  </div>
                </div>
                <span style={{ color: "#94A3B8", fontSize: "18px" }}>{open ? "▾" : "▸"}</span>
              </button>

              {open && (
                <div style={{ padding: "0 20px 20px" }}>
                  <ResenasPlomero idPlomero={p.id} />

                  <button onClick={() => setReSolic(reSolic === p.id ? null : p.id)}
                    style={{ width: "100%", marginBottom: "6px",
                      background: reSolic === p.id ? "#EFF6FF" : "linear-gradient(135deg,#3B82F6,#2563EB)",
                      color: reSolic === p.id ? "#1D4ED8" : "#fff",
                      border: reSolic === p.id ? "1.5px solid #BFDBFE" : "none",
                      borderRadius: "10px", padding: "10px", fontFamily: "'DM Sans',sans-serif",
                      fontWeight: "700", fontSize: "13px", cursor: "pointer" }}>
                    {reSolic === p.id ? "Cerrar" : "Contactar de nuevo"}
                  </button>
                  {reSolic === p.id && (
                    <ReSolicitarForm
                      plomeroId={p.id}
                      plomeroNombre={p.nombre || "este profesional"}
                      onResolicitado={(data) => { setReSolic(null); onResolicitado && onResolicitado(data); }}
                      onCancel={() => setReSolic(null)}
                    />
                  )}

                  <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "700", fontSize: "11px",
                    color: "#94A3B8", textTransform: "uppercase", letterSpacing: "0.6px", margin: "14px 0 8px" }}>
                    Tus trabajos con {p.nombre?.split(" ")[0] || "este plomero"}
                  </div>
                  {p.jobs.map(renderTrabajo)}
                </div>
              )}
            </div>
          );
        })
      }
    </div>
  );
}

// ─── SCREEN: NOTIFICACIONES ───────────────────────────────────────────────────

function ScreenNotificaciones({ notifs, onMark, onClear }) {
  return (
    <div style={{ maxWidth: "600px", margin: "0 auto", padding: "32px 24px" }}>
      <div style={{ display: "flex", justifyContent: "space-between",
        alignItems: "center", marginBottom: "24px" }}>
        <h1 style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
          fontSize: "22px", color: "#0F172A", letterSpacing: "-0.4px", margin: 0 }}>
          Notificaciones
        </h1>
        <div style={{ display: "flex", gap: "14px", alignItems: "center" }}>
          {notifs.some(n => !n.leida) && (
            <button onClick={onMark} style={{
              background: "transparent", border: "none",
              fontFamily: "'DM Sans',sans-serif", fontWeight: "600",
              fontSize: "13px", color: "#3B82F6", cursor: "pointer",
            }}>Marcar todas como leídas</button>
          )}
          {notifs.length > 0 && (
            <button onClick={onClear} style={{
              background: "transparent", border: "none",
              fontFamily: "'DM Sans',sans-serif", fontWeight: "600",
              fontSize: "13px", color: "#EF4444", cursor: "pointer",
            }}>Borrar todas</button>
          )}
        </div>
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

// ─── NOTIFICACIONES (backend persistente) ────────────────────────────────────

const ICONOS_NOTIF = {
  nueva_solicitud:    "📩",
  urgencia:           "🚨",
  solicitud_aceptada: "✅",
  en_camino:          "🚗",
  trabajo_finalizado: "🏁",
  cancelada_cliente:  "❌",
  cancelada_plomero:  "⚠️",
  mensaje:            "💬",
};

function tiempoRelativo(fechaISO) {
  if (!fechaISO) return "";
  const normal = (fechaISO.endsWith("Z") || fechaISO.includes("+")) ? fechaISO : fechaISO + "Z";
  const f = new Date(normal);
  const seg = Math.floor((Date.now() - f.getTime()) / 1000);
  if (seg < 60)    return "Hace un momento";
  if (seg < 3600)  return `Hace ${Math.floor(seg / 60)} min`;
  if (seg < 86400) return `Hace ${Math.floor(seg / 3600)} h`;
  return `Hace ${Math.floor(seg / 86400)} d`;
}

function mapNotif(n) {
  return {
    id:      n.id_notificacion,
    icon:    ICONOS_NOTIF[n.tipo] || "🔔",
    titulo:  n.titulo,
    mensaje: n.mensaje,
    tiempo:  tiempoRelativo(n.fecha),
    leida:   n.leida,
  };
}

// Hook reutilizable — consume la pestaña Alertas desde el backend.
export function useNotificaciones(token) {
  const [notifs, setNotifs] = useState([]);

  const poll = useCallback(async () => {
    if (!token) return;
    try {
      const res = await api.get("/notificaciones/");
      const arr = Array.isArray(res.data) ? res.data : [];
      const mapped = arr.map(mapNotif);
      // No re-renderizar si no cambió (evita interrumpir la escritura)
      setNotifs(prev => JSON.stringify(prev) === JSON.stringify(mapped) ? prev : mapped);
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

  const marcarTodas = useCallback(async () => {
    setNotifs(prev => prev.map(x => ({ ...x, leida: true })));
    try { await api.patch("/notificaciones/leer-todas"); } catch { /* noop */ }
    poll(); // re-sincroniza con el servidor (evita que un fetch viejo las reviva)
  }, [poll]);

  const eliminarTodas = useCallback(async () => {
    setNotifs([]);
    try { await api.delete("/notificaciones/"); } catch { /* noop */ }
    poll();
  }, [poll]);

  return [notifs, marcarTodas, eliminarTodas];
}

// ─── HOME CLIENTE ─────────────────────────────────────────────────────────────
// App.jsx lo monta cuando view==="app". Solo recibe onLogout como prop.

export default function HomeCliente({ onLogout }) {
  const [screen, setScreen]     = useState("problema");
  const [problema, setProblema] = useState("");
  const [urgencia, setUrgencia] = useState(false);
  const [solicitudActiva, setSolicitud] = useState(null);
  const [idsExcluidos, setIdsExcluidos] = useState([]);
  // Si está seteado, "Enviar solicitud" reintenta SOBRE esta solicitud (misma, no nueva)
  const [reintentarId, setReintentarId] = useState(null);
  // Borrador persistente abierto (pedido en preparación, todavía sin enviar a nadie)
  const [borradorId, setBorradorId] = useState(null);

  // Historial real
  const [historial, setHistorial]       = useState([]);
  const [loadingHistorial, setLoadingH] = useState(false);
  const [errorHistorial, setErrorH]     = useState("");

  // Token y user desde zustand (persist lo restaura de localStorage automáticamente)
  const token = useAuthStore(s => s.token);
  const [notifs, marcarTodasNotifs, eliminarTodasNotifs] = useNotificaciones(token);
  const notifCount = notifs.filter(n => !n.leida).length;

  // Conversaciones activas para el chat: solo trabajos en curso (con plomero)
  const conversacionesActivas = historial
    .filter(h => ["en_progreso", "en_camino"].includes((h.estado || "").toLowerCase()))
    .map(h => ({
      id_solicitud: h.id_solicitud,
      titulo:       h.nombre_plomero || "Profesional",
      subtitulo:    h.localidad_plomero || h.etiqueta_ia || "Trabajo en curso",
    }));

  // Cargar historial — función reutilizable para poder refrescarlo.
  // En modo silencioso (polling) NO toca loading ni reemplaza el estado si los
  // datos no cambiaron: así no re-renderiza y no te saca el foco mientras escribís.
  const cargarHistorial = useCallback(async (silencioso = false) => {
    if (!silencioso) setLoadingH(true);
    setErrorH("");
    const aplicar = (arr) =>
      setHistorial(prev => JSON.stringify(prev) === JSON.stringify(arr) ? prev : arr);
    try {
      const res = await api.get("/solicitudes/mis-solicitudes");
      aplicar(Array.isArray(res.data) ? res.data : []);
    } catch (e) {
      try {
        const res2 = await api.get("/solicitudes/buscar", { params: { q: "" } });
        aplicar(Array.isArray(res2.data) ? res2.data : []);
      } catch {
        setErrorH(e.message);
      }
    } finally {
      if (!silencioso) setLoadingH(false);
    }
  }, []);

  // Cargar al montar
  useEffect(() => { cargarHistorial(); }, [cargarHistorial]);

  // Refrescar historial cada 15 segundos (silencioso: no interrumpe la escritura)
  useEffect(() => {
    const interval = setInterval(() => cargarHistorial(true), 15000);
    return () => clearInterval(interval);
  }, [cargarHistorial]);

  const logout = useAuthStore(s => s.logout);
  const user   = useAuthStore(s => s.user);

  const handleLogout = () => {
    logout();                  // limpia zustand + localStorage via persist
    onLogout();                // App.jsx vuelve a view="login"
  };

  const handleBuscar = async (texto, urg) => {
    setProblema(texto);
    setUrgencia(urg);
    setReintentarId(null);   // búsqueda nueva: NO reintenta sobre una solicitud previa
    setIdsExcluidos([]);     // búsqueda nueva: sin exclusiones
    // Guardamos un BORRADOR persistente con el diagnóstico, así no se pierde
    // si el cliente navega a otra pestaña (queda abierto hasta enviar/cancelar/48hs).
    try {
      const res = await api.post("/solicitudes/borrador", { descripcion: texto });
      setBorradorId(res.data?.borrador?.id_solicitud || null);
    } catch {
      setBorradorId(null);   // si falla, "Enviar" creará una solicitud nueva igual
    }
    cargarHistorial(true);   // refresca "Mi solicitud" con el borrador recién creado
    setScreen("resultados");
  };

  // Continuar un borrador ya guardado (desde "Mi solicitud") → vuelve a resultados.
  const handleContinuarBorrador = (h) => {
    const desc = h.descripcion_raw || "";
    const URGENCIA_KEYWORDS = ["inunda","pérdida","perder","no cierra","roto","explota","revienta","urgente","emergencia","fuga","chorrea","sale agua"];
    setProblema(desc);
    setUrgencia(URGENCIA_KEYWORDS.some(k => desc.toLowerCase().includes(k)));
    setReintentarId(null);
    setIdsExcluidos([]);
    setBorradorId(h.id_solicitud);
    setScreen("resultados");
  };

  // Volver a buscar SOBRE LA MISMA solicitud (no crea una nueva), excluyendo
  // SOLO a los que rechazaron o cancelaron (los que no respondieron siguen elegibles).
  const handleReSolicitar = (solicitud) => {
    const desc = solicitud.descripcion_raw || "";
    setProblema(desc);
    // Detectar urgencia por palabras clave
    const URGENCIA_KEYWORDS = ["inunda","pérdida","perder","no cierra","roto","explota","revienta","urgente","emergencia","fuga","chorrea","sale agua"];
    setUrgencia(URGENCIA_KEYWORDS.some(k => desc.toLowerCase().includes(k)));
    // Excluir SOLO a los que rechazaron o cancelaron en ESTA solicitud.
    const excluidos = (solicitud.invitaciones || [])
      .filter(i => ["rechazado", "cancelado"].includes((i.estado || "").toLowerCase()))
      .map(i => i.id_plomero);
    setIdsExcluidos(excluidos);
    setReintentarId(solicitud.id_solicitud);   // reintenta sobre la misma solicitud
    setBorradorId(null);                       // no es un borrador, es un reintento
    setScreen("resultados");
  };

  // Cuando el cliente quiere volver a contratar a un plomero finalizado
  const handleSolicitarDeNuevo = (h) => {
    // Ir al inicio para que escriba el problema (con el nombre del plomero como sugerencia)
    setScreen("problema");
  };

  // Tras re-solicitar a un plomero específico desde Finalizados:
  // refresca el historial y lleva a "Mis solicitudes" (queda como solicitud activa)
  const handleResolicitado = () => {
    cargarHistorial();
    setScreen("mi-solicitud");
  };

  const handleEnviar = (resp) => {
    setSolicitud(resp);
    if (resp) setHistorial(prev => [resp, ...prev]);
    setReintentarId(null);   // ya se envió: limpiar el modo reintento
    setBorradorId(null);     // el borrador ya pasó a solicitud enviada
    cargarHistorial(); // refrescar con datos reales del backend
    setScreen("mi-solicitud");
  };

  return (
    <div style={{ minHeight: "100vh",
      background: "linear-gradient(160deg,#F0F9FF 0%,#F8FAFC 50%,#F0FDF4 100%)" }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>

      <Header
        screen={["resultados","estado"].includes(screen) ? "problema" : screen}
        onNav={setScreen}
        notifCount={notifCount}
        onLogout={handleLogout}
        user={user}
      />

      {screen === "problema" && (
        <ScreenProblema onBuscar={handleBuscar} />
      )}
      {screen === "resultados" && (
        <ScreenResultados
          problema={problema}
          urgencia={urgencia}
          idsExcluidos={idsExcluidos}
          reintentarId={reintentarId}
          borradorId={borradorId}
          onEnviar={handleEnviar}
          onNav={setScreen}
        />
      )}
      {screen === "estado" && (
        <ScreenEstado solicitud={solicitudActiva} onNav={setScreen} />
      )}
      {screen === "mi-solicitud" && (
        <ScreenMiSolicitud
          historial={historial}
          loading={loadingHistorial}
          onNav={setScreen}
          onReSolicitar={handleReSolicitar}
          onContinuarBorrador={handleContinuarBorrador}
          onRated={() => { cargarHistorial(); setScreen("problema"); }}
        />
      )}
      {screen === "trabajos-finalizados" && (
        <ScreenTrabajosFinalizados
          historial={historial}
          loading={loadingHistorial}
          onResolicitado={handleResolicitado}
        />
      )}
      {screen === "notificaciones" && (
        <ScreenNotificaciones
          notifs={notifs}
          onMark={marcarTodasNotifs}
          onClear={eliminarTodasNotifs}
        />
      )}

      {/* Chat flotante — visible siempre, activo solo con trabajos en curso */}
      <ChatWidget conversaciones={conversacionesActivas} />
    </div>
  );
}