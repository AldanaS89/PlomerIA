import { useState, useEffect, useCallback } from "react";
import api from "../services/api";
import { useAuthStore } from "../store/authStore";

// ─── CONSTANTS ────────────────────────────────────────────────────────────────

const BADGE_STYLES = {
  PLOMERIA_GENERAL: { bg:"#EFF6FF", text:"#1D4ED8" },
  DESTAPES:         { bg:"#E0F2FE", text:"#0369A1" },
  GAS_MATRICULADO:  { bg:"#FEF9C3", text:"#854D0E" },
  OBRA:             { bg:"#DCFCE7", text:"#15803D" },
  FILTRACIONES:     { bg:"#FEF9C3", text:"#854D0E" },
  CALEFACCION:      { bg:"#FFF7ED", text:"#C2410C" },
  Destapes:         { bg:"#E0F2FE", text:"#0369A1" },
  Urgencias:        { bg:"#FEE2E2", text:"#B91C1C" },
  "Obra general":   { bg:"#DCFCE7", text:"#15803D" },
  Instalaciones:    { bg:"#F3E8FF", text:"#7E22CE" },
  Filtraciones:     { bg:"#FEF9C3", text:"#854D0E" },
};

const ESP_LABELS = {
  PLOMERIA_GENERAL: "Plomería general",
  DESTAPES:         "Destapes",
  GAS_MATRICULADO:  "Gas matriculado",
  OBRA:             "Obra",
  FILTRACIONES:     "Filtraciones",
  CALEFACCION:      "Calefacción",
};

const ESTADOS_TRABAJO = {
  pendiente:  { label:"Pendiente de inicio", icon:"⏳", color:"#F59E0B", bg:"#FFFBEB" },
  en_camino:  { label:"En camino",           icon:"🚗", color:"#3B82F6", bg:"#EFF6FF" },
  en_trabajo: { label:"Trabajando",          icon:"🔧", color:"#8B5CF6", bg:"#F5F3FF" },
  finalizado: { label:"Finalizado",          icon:"✅", color:"#22C55E", bg:"#F0FDF4" },
};

const FLUJO = ["pendiente","en_camino","en_trabajo","finalizado"];
const MONTHS = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"];
const DAYS_FULL = ["Dom","Lun","Mar","Mié","Jue","Vie","Sáb"];

// ─── HELPERS ─────────────────────────────────────────────────────────────────

function formatTime(secs) {
  const h = Math.floor(secs / 3600);
  const m = Math.floor((secs % 3600) / 60);
  const s = secs % 60;
  if (h > 0) return `${h}h ${String(m).padStart(2,"0")}m`;
  return `${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}`;
}

// ─── SHARED COMPONENTS ────────────────────────────────────────────────────────

function Badge({ label }) {
  const key = label?.toUpperCase().replace(/ /g,"_");
  const s = BADGE_STYLES[label] || BADGE_STYLES[key] || { bg:"#F3F4F6", text:"#374151" };
  const display = ESP_LABELS[label] || ESP_LABELS[key] || label;
  return (
    <span style={{ background:s.bg, color:s.text, fontSize:"11px",
      fontWeight:"700", padding:"3px 10px", borderRadius:"20px",
      fontFamily:"'DM Sans',sans-serif", whiteSpace:"nowrap" }}>
      {display}
    </span>
  );
}

function Stars({ val, size=13 }) {
  return (
    <div style={{ display:"flex", gap:"2px" }}>
      {[1,2,3,4,5].map(i => (
        <svg key={i} width={size} height={size} viewBox="0 0 24 24">
          <polygon
            points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"
            fill={i<=val ? "#FBBF24" : "#E5E7EB"}
          />
        </svg>
      ))}
    </div>
  );
}

function Avatar({ src, nombre, apellido, size=44 }) {
  const [err, setErr] = useState(false);
  const fullSrc = src && !src.startsWith("http") ? `http://localhost:8000/${src}` : src;
  if (fullSrc && !err) return (
    <img src={fullSrc} alt="" onError={()=>setErr(true)}
      style={{ width:size, height:size, borderRadius:"12px",
        objectFit:"cover", flexShrink:0 }}/>
  );
  return (
    <div style={{ width:size, height:size, borderRadius:"12px", flexShrink:0,
      background:"linear-gradient(135deg,#22C55E,#16A34A)",
      display:"flex", alignItems:"center", justifyContent:"center",
      fontSize:size*0.32, fontWeight:"800", color:"#fff",
      fontFamily:"'DM Sans',sans-serif" }}>
      {nombre?.[0]}{apellido?.[0]}
    </div>
  );
}

function Spinner({ size=20, color="#fff" }) {
  return (
    <>
      <style>{`@keyframes _sp{to{transform:rotate(360deg)}}`}</style>
      <div style={{ width:size, height:size,
        border:`2.5px solid rgba(255,255,255,0.3)`,
        borderTop:`2.5px solid ${color}`,
        borderRadius:"50%", animation:"_sp 0.7s linear infinite", flexShrink:0 }}/>
    </>
  );
}

function Countdown({ segundos, urgente }) {
  const [remaining, setRemaining] = useState(segundos);
  useEffect(() => {
    const t = setInterval(() => setRemaining(r => Math.max(0, r-1)), 1000);
    return () => clearInterval(t);
  }, []);
  const pct     = remaining / segundos;
  const critico = pct < 0.25;
  const color   = critico ? "#EF4444" : urgente ? "#F59E0B" : "#3B82F6";
  const bgColor = critico ? "#FEF2F2" : urgente ? "#FFFBEB" : "#EFF6FF";
  return (
    <div style={{ background:bgColor, border:`1.5px solid ${color}33`,
      borderRadius:"10px", padding:"8px 12px",
      display:"flex", alignItems:"center", gap:"8px" }}>
      <div style={{ fontSize:"14px" }}>{critico ? "🔴" : urgente ? "⚠️" : "⏱"}</div>
      <div>
        <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"10px",
          fontWeight:"700", color, textTransform:"uppercase", letterSpacing:"0.6px" }}>
          {remaining===0 ? "Tiempo agotado" : "Tiempo para responder"}
        </div>
        <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
          fontSize:"16px", color, letterSpacing:"-0.5px" }}>
          {remaining===0 ? "—" : formatTime(remaining)}
        </div>
      </div>
      <div style={{ flex:1, height:"4px", background:"#E2E8F0",
        borderRadius:"2px", overflow:"hidden" }}>
        <div style={{ width:`${pct*100}%`, height:"100%",
          background:color, borderRadius:"2px", transition:"width 1s linear" }}/>
      </div>
    </div>
  );
}

// ─── HEADER ──────────────────────────────────────────────────────────────────

function Header({ screen, onNav, disponible, onToggleDisp, pendientes, user, onLogout }) {
  const tabs = [
    { key:"solicitudes", label:"Solicitudes", icon:"📬", badge:pendientes },
    { key:"activos",     label:"En curso",    icon:"🔧" },
    { key:"agenda",      label:"Mi agenda",   icon:"📅" },
    { key:"historial",   label:"Historial",   icon:"📋" },
  ];
  return (
    <div style={{ background:"linear-gradient(135deg,#0F172A,#1E3A5F)",
      padding:"0 24px", position:"sticky", top:0, zIndex:100 }}>
      <div style={{ display:"flex", alignItems:"center",
        justifyContent:"space-between", paddingTop:"14px", paddingBottom:"10px",
        borderBottom:"1px solid rgba(255,255,255,0.08)" }}>

        <div style={{ display:"flex", alignItems:"center", gap:"12px" }}>
          <div style={{ background:"linear-gradient(135deg,#3B82F6,#06B6D4)",
            borderRadius:"10px", width:"34px", height:"34px",
            display:"flex", alignItems:"center", justifyContent:"center",
            fontSize:"16px" }}>🔧</div>
          <div>
            <span style={{ fontWeight:"800", fontSize:"18px", color:"#fff",
              letterSpacing:"-0.4px", fontFamily:"'DM Sans',sans-serif" }}>
              Plomer<span style={{ color:"#38BDF8" }}>IA</span>
            </span>
            <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"11px",
              color:"#475569", marginTop:"1px" }}>
              {user?.nombre} · Panel Plomero
            </div>
          </div>
        </div>

        <div style={{ display:"flex", alignItems:"center", gap:"12px" }}>
          {/* Toggle disponibilidad */}
          <div style={{ display:"flex", alignItems:"center", gap:"8px" }}>
            <div style={{ textAlign:"right" }}>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"10px",
                fontWeight:"700", color:"#475569", textTransform:"uppercase",
                letterSpacing:"0.6px" }}>Disponibilidad</div>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
                fontWeight:"700", color: disponible ? "#34D399" : "#F87171" }}>
                {disponible ? "Activo" : "Inactivo"}
              </div>
            </div>
            <button onClick={onToggleDisp} style={{
              width:"48px", height:"26px", borderRadius:"13px", border:"none",
              background: disponible ? "linear-gradient(135deg,#22C55E,#16A34A)" : "#334155",
              cursor:"pointer", position:"relative", transition:"all 0.25s",
              boxShadow: disponible ? "0 0 12px rgba(34,197,94,0.4)" : "none",
            }}>
              <div style={{ position:"absolute", top:"3px",
                left: disponible ? "25px" : "3px",
                width:"20px", height:"20px", borderRadius:"50%",
                background:"#fff", transition:"left 0.25s",
                boxShadow:"0 1px 4px rgba(0,0,0,0.2)" }}/>
            </button>
          </div>

          <button onClick={onLogout} style={{
            background:"rgba(239,68,68,0.1)", border:"1px solid rgba(239,68,68,0.25)",
            borderRadius:"8px", padding:"5px 12px", color:"#FCA5A5",
            fontSize:"12px", fontWeight:"600", cursor:"pointer",
            fontFamily:"'DM Sans',sans-serif",
          }}>Salir</button>
        </div>
      </div>

      <div style={{ display:"flex", gap:"2px", overflowX:"auto" }}>
        {tabs.map(t => (
          <button key={t.key} onClick={()=>onNav(t.key)} style={{
            background:"transparent", border:"none", cursor:"pointer",
            padding:"10px 14px", display:"flex", alignItems:"center", gap:"5px",
            fontFamily:"'DM Sans',sans-serif", fontSize:"13px", fontWeight:"600",
            color: screen===t.key ? "#38BDF8" : "#475569",
            borderBottom: screen===t.key ? "2px solid #38BDF8" : "2px solid transparent",
            transition:"all 0.18s", whiteSpace:"nowrap", position:"relative",
          }}>
            <span>{t.icon}</span>
            <span>{t.label}</span>
            {t.badge > 0 && (
              <div style={{ background:"#EF4444", color:"#fff",
                borderRadius:"10px", fontSize:"10px", fontWeight:"800",
                padding:"1px 6px", minWidth:"16px" }}>{t.badge}</div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}

// ─── SCREEN: SOLICITUDES ──────────────────────────────────────────────────────

function ScreenSolicitudes({ solicitudes, onAceptar, onRechazar, disponible, loading }) {
  const [expandido, setExpandido] = useState(null);
  const [loadingId, setLoadingId] = useState(null);

  const handleAceptar = async (id) => {
    setLoadingId(id);
    await onAceptar(id);
    setLoadingId(null);
  };

  const handleRechazar = async (id) => {
    setLoadingId(id + "_r");
    await onRechazar(id);
    setLoadingId(null);
  };

  if (!disponible) return (
    <div style={{ maxWidth:"560px", margin:"0 auto", padding:"60px 24px", textAlign:"center" }}>
      <div style={{ fontSize:"48px", marginBottom:"16px" }}>😴</div>
      <h2 style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
        fontSize:"20px", color:"#0F172A", margin:"0 0 8px" }}>Estás inactivo</h2>
      <p style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"14px",
        color:"#64748B", lineHeight:"1.6", maxWidth:"320px", margin:"0 auto" }}>
        Activá tu disponibilidad para recibir solicitudes.
      </p>
    </div>
  );

  if (loading) return (
    <div style={{ display:"flex", justifyContent:"center", padding:"80px" }}>
      <Spinner size={36} color="#3B82F6"/>
    </div>
  );

  if (solicitudes.length===0) return (
    <div style={{ maxWidth:"560px", margin:"0 auto", padding:"60px 24px", textAlign:"center" }}>
      <div style={{ fontSize:"48px", marginBottom:"16px" }}>📭</div>
      <h2 style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
        fontSize:"20px", color:"#0F172A", margin:"0 0 8px" }}>Sin solicitudes nuevas</h2>
      <p style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"14px", color:"#64748B" }}>
        Te avisamos cuando llegue una.
      </p>
    </div>
  );

  return (
    <div style={{ maxWidth:"640px", margin:"0 auto", padding:"28px 24px" }}>
      <h1 style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
        fontSize:"22px", color:"#0F172A", letterSpacing:"-0.4px", margin:"0 0 6px" }}>
        Solicitudes entrantes
      </h1>
      <p style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"14px",
        color:"#64748B", margin:"0 0 24px" }}>
        El primero en aceptar queda asignado · La dirección se revela al aceptar
      </p>

      {solicitudes.map(s => {
        const esUrgente = (s.urgencia_ia || "").toUpperCase() === "URGENTE";
        const tiempoLimite = esUrgente ? 30 * 60 : 3 * 60 * 60;
        const turnoStr = s.turno_solicitado
          ? `${s.turno_solicitado}`.replace(/_/g, " ")
          : null;

        return (
          <div key={s.id_solicitud} style={{
            background:"#fff", borderRadius:"20px",
            border: esUrgente ? "2px solid #FCA5A5" : "2px solid #F1F5F9",
            padding:"20px", marginBottom:"14px",
            boxShadow: esUrgente
              ? "0 4px 20px rgba(239,68,68,0.08)"
              : "0 2px 12px rgba(0,0,0,0.05)",
          }}>
            <div style={{ display:"flex", justifyContent:"space-between",
              alignItems:"flex-start", marginBottom:"14px", gap:"12px" }}>
              <div style={{ flex:1 }}>
                <div style={{ display:"flex", alignItems:"center",
                  gap:"8px", flexWrap:"wrap", marginBottom:"6px" }}>
                  <Badge label={s.etiqueta_ia || "PLOMERIA_GENERAL"}/>
                  {esUrgente && (
                    <span style={{ background:"#FEE2E2", color:"#B91C1C",
                      fontSize:"11px", fontWeight:"800", padding:"3px 10px",
                      borderRadius:"20px", fontFamily:"'DM Sans',sans-serif" }}>
                      🚨 URGENTE
                    </span>
                  )}
                </div>
                <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"13px", color:"#94A3B8" }}>
                  📍 {s.localidad_evento || "Sin localidad"} · {s.fecha ? new Date(s.fecha).toLocaleString("es-AR") : ""}
                </div>
                {turnoStr && (
                  <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
                    color:"#15803D", fontWeight:"600", marginTop:"3px" }}>
                    📅 Turno pedido: {turnoStr}
                  </div>
                )}
              </div>
            </div>

            <div style={{ marginBottom:"14px" }}>
              <Countdown segundos={tiempoLimite} urgente={esUrgente}/>
            </div>

            <div style={{ background:"#F8FAFC", border:"1.5px solid #E2E8F0",
              borderRadius:"12px", padding:"12px 14px", marginBottom:"14px" }}>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"10px",
                fontWeight:"700", color:"#94A3B8", textTransform:"uppercase",
                letterSpacing:"0.8px", marginBottom:"6px" }}>Lo que describe el cliente</div>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"13px",
                color:"#334155", lineHeight:"1.6",
                maxHeight: expandido===s.id_solicitud ? "none" : "48px",
                overflow:"hidden" }}>
                "{s.descripcion_raw}"
              </div>
              {s.descripcion_raw?.length > 120 && (
                <button onClick={()=>setExpandido(expandido===s.id_solicitud ? null : s.id_solicitud)}
                  style={{ background:"none", border:"none", cursor:"pointer",
                    fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
                    color:"#3B82F6", fontWeight:"600", padding:"4px 0 0", display:"block" }}>
                  {expandido===s.id_solicitud ? "Ver menos ↑" : "Ver más ↓"}
                </button>
              )}
            </div>

            <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"11px",
              color:"#94A3B8", marginBottom:"14px",
              display:"flex", alignItems:"center", gap:"5px" }}>
              🔒 La dirección exacta se revela solo si aceptás el trabajo
            </div>

            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"10px" }}>
              <button onClick={()=>handleRechazar(s.id_solicitud)}
                disabled={loadingId===s.id_solicitud+"_r"} style={{
                background:"#FEF2F2", border:"1.5px solid #FECACA",
                borderRadius:"12px", padding:"12px",
                fontFamily:"'DM Sans',sans-serif", fontWeight:"700",
                fontSize:"14px", color:"#EF4444", cursor:"pointer",
              }}>✕ Rechazar</button>
              <button onClick={()=>handleAceptar(s.id_solicitud)}
                disabled={loadingId===s.id_solicitud} style={{
                background:"linear-gradient(135deg,#22C55E,#16A34A)",
                border:"none", borderRadius:"12px", padding:"12px",
                fontFamily:"'DM Sans',sans-serif", fontWeight:"700",
                fontSize:"14px", color:"#fff", cursor:"pointer",
                boxShadow:"0 4px 14px rgba(34,197,94,0.3)",
                display:"flex", alignItems:"center", justifyContent:"center", gap:"8px",
              }}>
                {loadingId===s.id_solicitud ? <Spinner size={16}/> : null}
                ✓ Aceptar trabajo
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ─── SCREEN: ACTIVOS ──────────────────────────────────────────────────────────

function ScreenActivos({ activos, onCambiarEstado, onCancelar, loading }) {
  const [loadingId, setLoadingId] = useState(null);
  const [cancelando, setCancelando] = useState(null);
  const [proponiendo, setProponiendo] = useState(null);
  const [horaPropuesta, setHoraPropuesta] = useState("");

  const handleCambiar = async (id, estado) => {
    setLoadingId(id + estado);
    await onCambiarEstado(id, estado);
    setLoadingId(null);
  };

  const handleCancelar = async (id) => {
    setLoadingId("cancel" + id);
    await onCancelar(id);
    setLoadingId(null);
    setCancelando(null);
  };

  if (loading) return (
    <div style={{ display:"flex", justifyContent:"center", padding:"80px" }}>
      <Spinner size={36} color="#3B82F6"/>
    </div>
  );

  if (activos.length===0) return (
    <div style={{ maxWidth:"560px", margin:"0 auto", padding:"60px 24px", textAlign:"center" }}>
      <div style={{ fontSize:"48px", marginBottom:"16px" }}>✅</div>
      <h2 style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
        fontSize:"20px", color:"#0F172A", margin:"0 0 8px" }}>Sin trabajos activos</h2>
      <p style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"14px", color:"#64748B" }}>
        Aceptá una solicitud para verla acá.
      </p>
    </div>
  );

  return (
    <div style={{ maxWidth:"640px", margin:"0 auto", padding:"28px 24px" }}>
      <h1 style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
        fontSize:"22px", color:"#0F172A", letterSpacing:"-0.4px", margin:"0 0 24px" }}>
        Trabajos en curso
      </h1>

      {activos.map(t => {
        const estadoKey = t.estado_trabajo || "pendiente";
        const estadoActual = ESTADOS_TRABAJO[estadoKey] || ESTADOS_TRABAJO.pendiente;
        const idxActual = FLUJO.indexOf(estadoKey);
        const siguiente = FLUJO[idxActual+1];
        const sigEstado = siguiente ? ESTADOS_TRABAJO[siguiente] : null;

        return (
          <div key={t.id_solicitud} style={{
            background:"#fff", borderRadius:"20px",
            border:"2px solid #F1F5F9", padding:"22px", marginBottom:"16px",
            boxShadow:"0 4px 20px rgba(0,0,0,0.06)",
          }}>
            {/* Estado actual */}
            <div style={{ display:"flex", alignItems:"center",
              justifyContent:"space-between", marginBottom:"18px" }}>
              <div style={{ display:"flex", alignItems:"center", gap:"10px" }}>
                <div style={{ background:estadoActual.bg,
                  border:`1.5px solid ${estadoActual.color}33`,
                  borderRadius:"12px", width:"44px", height:"44px",
                  display:"flex", alignItems:"center", justifyContent:"center",
                  fontSize:"20px" }}>{estadoActual.icon}</div>
                <div>
                  <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
                    fontSize:"15px", color:estadoActual.color }}>{estadoActual.label}</div>
                  <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px", color:"#94A3B8" }}>
                    {t.fecha ? new Date(t.fecha).toLocaleString("es-AR") : ""}
                  </div>
                </div>
              </div>
              <Badge label={t.etiqueta_ia || "PLOMERIA_GENERAL"}/>
            </div>

            {/* Timeline */}
            <div style={{ display:"flex", alignItems:"center", gap:"0", marginBottom:"20px" }}>
              {FLUJO.map((f,i) => {
                const done    = i < idxActual;
                const current = i === idxActual;
                const e       = ESTADOS_TRABAJO[f];
                return (
                  <div key={f} style={{ display:"flex", alignItems:"center",
                    flex: i<FLUJO.length-1 ? 1 : "none" }}>
                    <div style={{ display:"flex", flexDirection:"column",
                      alignItems:"center", gap:"4px" }}>
                      <div style={{ width:"32px", height:"32px", borderRadius:"50%",
                        background: done?"#22C55E":current?e.color:"#F1F5F9",
                        display:"flex", alignItems:"center", justifyContent:"center",
                        fontSize:"14px",
                        border: current?`2px solid ${e.color}`:"none",
                        boxShadow: current?`0 0 0 3px ${e.color}22`:"none",
                        transition:"all 0.3s" }}>
                        {done?"✓":e.icon}
                      </div>
                      <span style={{ fontFamily:"'DM Sans',sans-serif",
                        fontSize:"9px", fontWeight:"600",
                        color: done?"#22C55E":current?e.color:"#CBD5E1",
                        textAlign:"center", whiteSpace:"nowrap" }}>
                        {e.label.split(" ")[0]}
                      </span>
                    </div>
                    {i<FLUJO.length-1 && (
                      <div style={{ flex:1, height:"2px", margin:"0 4px",
                        marginBottom:"18px",
                        background: done?"#22C55E":"#E2E8F0", transition:"all 0.3s" }}/>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Datos del cliente */}
            <div style={{ background:"#F8FAFC", borderRadius:"12px",
              padding:"14px", marginBottom:"16px" }}>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"10px",
                fontWeight:"700", color:"#94A3B8", textTransform:"uppercase",
                letterSpacing:"0.8px", marginBottom:"10px" }}>Datos del cliente</div>
              <div style={{ display:"flex", flexDirection:"column", gap:"6px" }}>
                {[
                  ["Problema",  t.descripcion_raw],
                  ["Localidad", t.localidad_evento || "—"],
                  ["Turno pedido", t.turno_solicitado || "A confirmar"],
                ].map(([k,v]) => (
                  <div key={k} style={{ display:"flex", justifyContent:"space-between", gap:"8px" }}>
                    <span style={{ fontFamily:"'DM Sans',sans-serif",
                      fontSize:"12px", color:"#94A3B8", flexShrink:0 }}>{k}</span>
                    <span style={{ fontFamily:"'DM Sans',sans-serif",
                      fontWeight:"700", fontSize:"13px", color:"#0F172A",
                      textAlign:"right" }}>{v}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Proponer horario alternativo */}
            {proponiendo === t.id_solicitud ? (
              <div style={{ background:"#EFF6FF", border:"1px solid #BFDBFE",
                borderRadius:"12px", padding:"14px", marginBottom:"14px" }}>
                <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"700",
                  fontSize:"13px", color:"#1D4ED8", marginBottom:"8px" }}>
                  Proponer horario alternativo
                </div>
                <input
                  type="text"
                  placeholder="Ej: Jueves 15/5 a las 9:00hs"
                  value={horaPropuesta}
                  onChange={e => setHoraPropuesta(e.target.value)}
                  style={{ width:"100%", padding:"10px 12px", borderRadius:"8px",
                    border:"1.5px solid #BFDBFE", fontFamily:"'DM Sans',sans-serif",
                    fontSize:"13px", outline:"none", boxSizing:"border-box",
                    marginBottom:"8px" }}
                />
                <div style={{ display:"flex", gap:"8px" }}>
                  <button onClick={() => { setProponiendo(null); setHoraPropuesta(""); }}
                    style={{ flex:1, background:"#F1F5F9", border:"none", borderRadius:"8px",
                      padding:"9px", fontFamily:"'DM Sans',sans-serif", fontSize:"13px",
                      color:"#475569", cursor:"pointer", fontWeight:"600" }}>
                    Cancelar
                  </button>
                  <button onClick={() => { setProponiendo(null); setHoraPropuesta(""); }}
                    style={{ flex:1, background:"linear-gradient(135deg,#3B82F6,#2563EB)",
                      border:"none", borderRadius:"8px", padding:"9px",
                      fontFamily:"'DM Sans',sans-serif", fontSize:"13px",
                      color:"#fff", cursor:"pointer", fontWeight:"700" }}>
                    Enviar propuesta
                  </button>
                </div>
              </div>
            ) : (
              <button onClick={() => setProponiendo(t.id_solicitud)}
                style={{ width:"100%", background:"#EFF6FF",
                  border:"1px solid #BFDBFE", borderRadius:"10px", padding:"9px",
                  fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
                  color:"#1D4ED8", cursor:"pointer", fontWeight:"600",
                  marginBottom:"10px" }}>
                📅 Proponer horario alternativo
              </button>
            )}

            {/* Botón siguiente estado */}
            {sigEstado && estadoKey !== "finalizado" && (
              <button onClick={()=>handleCambiar(t.id_solicitud, siguiente)}
                disabled={!!loadingId}
                style={{ width:"100%",
                  background: siguiente==="finalizado"
                    ? "linear-gradient(135deg,#22C55E,#16A34A)"
                    : "linear-gradient(135deg,#3B82F6,#2563EB)",
                  border:"none", borderRadius:"14px", padding:"13px",
                  fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
                  fontSize:"14px", color:"#fff", cursor:"pointer", marginBottom:"10px",
                  boxShadow: siguiente==="finalizado"
                    ? "0 4px 14px rgba(34,197,94,0.3)"
                    : "0 4px 14px rgba(59,130,246,0.3)",
                  display:"flex", alignItems:"center", justifyContent:"center", gap:"8px",
                }}>
                {loadingId===t.id_solicitud+siguiente ? <Spinner size={16}/> : null}
                {sigEstado.icon} Marcar como "{sigEstado.label}"
              </button>
            )}

            {estadoKey === "finalizado" && (
              <div style={{ background:"#F0FDF4", border:"2px solid #86EFAC",
                borderRadius:"12px", padding:"14px", textAlign:"center" }}>
                <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
                  fontSize:"14px", color:"#15803D", marginBottom:"4px" }}>
                  🎉 Trabajo finalizado
                </div>
                <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px", color:"#166534" }}>
                  El cliente puede valorar el servicio
                </div>
              </div>
            )}

            {/* Cancelar trabajo */}
            {estadoKey !== "finalizado" && (
              cancelando === t.id_solicitud ? (
                <div style={{ marginTop:"10px", background:"#FEF2F2",
                  border:"1px solid #FECACA", borderRadius:"10px", padding:"12px",
                  display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                  <span style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
                    color:"#B91C1C", fontWeight:"600" }}>¿Cancelar este trabajo?</span>
                  <div style={{ display:"flex", gap:"8px" }}>
                    <button onClick={() => setCancelando(null)} style={{
                      background:"#F8FAFC", border:"1px solid #E2E8F0",
                      borderRadius:"7px", padding:"5px 12px",
                      fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
                      color:"#475569", cursor:"pointer", fontWeight:"600" }}>No</button>
                    <button onClick={() => handleCancelar(t.id_solicitud)}
                      disabled={!!loadingId}
                      style={{ background:"#EF4444", border:"none",
                        borderRadius:"7px", padding:"5px 12px",
                        fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
                        color:"#fff", cursor:"pointer", fontWeight:"700" }}>
                      Sí, cancelar
                    </button>
                  </div>
                </div>
              ) : (
                <button onClick={() => setCancelando(t.id_solicitud)} style={{
                  marginTop:"10px", width:"100%", background:"transparent",
                  border:"1px solid #E2E8F0", borderRadius:"10px", padding:"9px",
                  fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
                  color:"#94A3B8", cursor:"pointer", fontWeight:"600",
                }}>
                  Cancelar trabajo
                </button>
              )
            )}
          </div>
        );
      })}
    </div>
  );
}

// ─── SCREEN: AGENDA ───────────────────────────────────────────────────────────

function ScreenAgenda({ activos }) {
  const hoy = new Date();
  const [year,  setYear]  = useState(hoy.getFullYear());
  const [month, setMonth] = useState(hoy.getMonth());

  const firstDay    = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month+1, 0).getDate();
  const fmt = d => `${year}-${String(month+1).padStart(2,"0")}-${String(d).padStart(2,"0")}`;

  const fechasOcupadas = activos
    .filter(a => a.turno_solicitado)
    .reduce((acc, a) => {
      const fecha = a.turno_solicitado?.split("_")[0];
      if (fecha) {
        acc[fecha] = acc[fecha] || [];
        acc[fecha].push({ descripcion: a.descripcion_raw, tipo: a.etiqueta_ia });
      }
      return acc;
    }, {});

  const [selected, setSelected] = useState(null);
  const selectedJobs = selected ? (fechasOcupadas[selected]||[]) : [];

  const prev = () => { if(month===0){setMonth(11);setYear(y=>y-1);}else setMonth(m=>m-1); setSelected(null); };
  const next = () => { if(month===11){setMonth(0);setYear(y=>y+1);}else setMonth(m=>m+1); setSelected(null); };

  return (
    <div style={{ maxWidth:"600px", margin:"0 auto", padding:"28px 24px" }}>
      <h1 style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
        fontSize:"22px", color:"#0F172A", letterSpacing:"-0.4px", margin:"0 0 6px" }}>
        Mi agenda
      </h1>
      <p style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"14px",
        color:"#64748B", margin:"0 0 24px" }}>
        Tus trabajos confirmados · Tocá un día para ver el detalle
      </p>

      <div style={{ background:"#fff", borderRadius:"20px",
        border:"1.5px solid #F1F5F9", padding:"24px",
        boxShadow:"0 4px 20px rgba(0,0,0,0.06)", marginBottom:"20px" }}>

        <div style={{ display:"flex", alignItems:"center",
          justifyContent:"space-between", marginBottom:"20px" }}>
          <button onClick={prev} style={{ background:"#F1F5F9", border:"none",
            borderRadius:"10px", width:"36px", height:"36px", cursor:"pointer",
            fontSize:"18px", color:"#475569" }}>‹</button>
          <span style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
            fontSize:"18px", color:"#0F172A" }}>{MONTHS[month]} {year}</span>
          <button onClick={next} style={{ background:"#F1F5F9", border:"none",
            borderRadius:"10px", width:"36px", height:"36px", cursor:"pointer",
            fontSize:"18px", color:"#475569" }}>›</button>
        </div>

        <div style={{ display:"grid", gridTemplateColumns:"repeat(7,1fr)",
          gap:"2px", marginBottom:"8px" }}>
          {DAYS_FULL.map(d => (
            <div key={d} style={{ textAlign:"center", fontSize:"11px",
              fontWeight:"700", color:"#94A3B8",
              fontFamily:"'DM Sans',sans-serif", padding:"4px 0" }}>{d}</div>
          ))}
        </div>

        <div style={{ display:"grid", gridTemplateColumns:"repeat(7,1fr)", gap:"4px" }}>
          {Array.from({length:firstDay}).map((_,i)=><div key={`e${i}`}/>)}
          {Array.from({length:daysInMonth}).map((_,i)=>{
            const d   = i+1;
            const ds  = fmt(d);
            const isHoy = new Date(year,month,d).toDateString()===hoy.toDateString();
            const tieneJobs = !!fechasOcupadas[ds];
            const isSel = selected===ds;
            return (
              <button key={d} onClick={()=>tieneJobs && setSelected(isSel?null:ds)} style={{
                border:"none", borderRadius:"10px", padding:"8px 4px",
                cursor: tieneJobs?"pointer":"default",
                fontFamily:"'DM Sans',sans-serif",
                fontWeight: isHoy||tieneJobs ? "800" : "400",
                fontSize:"13px",
                background: isSel?"#3B82F6": tieneJobs?"#EFF6FF":"transparent",
                color: isSel?"#fff": isHoy?"#3B82F6": tieneJobs?"#1D4ED8":"#94A3B8",
                position:"relative", transition:"all 0.15s",
                outline: isHoy ? "2px solid #BFDBFE" : "none",
              }}>
                {d}
                {tieneJobs && !isSel && (
                  <div style={{ position:"absolute", bottom:"3px", left:"50%",
                    transform:"translateX(-50%)", width:"5px", height:"5px",
                    borderRadius:"50%", background:"#3B82F6" }}/>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {selected && (
        <div style={{ background:"#fff", borderRadius:"16px",
          border:"2px solid #BFDBFE", padding:"20px",
          boxShadow:"0 4px 16px rgba(59,130,246,0.08)" }}>
          <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
            fontSize:"15px", color:"#0F172A", marginBottom:"14px" }}>
            📅 {selected.split("-").reverse().join("/")}
          </div>
          {selectedJobs.length===0
            ? <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"13px", color:"#94A3B8" }}>
                Sin trabajos este día
              </div>
            : selectedJobs.map((j,i)=>(
              <div key={i} style={{ display:"flex", alignItems:"center",
                gap:"12px", padding:"10px 0",
                borderBottom: i<selectedJobs.length-1 ? "1px solid #F1F5F9" : "none" }}>
                <div>
                  <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"700",
                    fontSize:"14px", color:"#0F172A" }}>{j.descripcion}</div>
                  <Badge label={j.tipo}/>
                </div>
              </div>
            ))
          }
        </div>
      )}
    </div>
  );
}

// ─── SCREEN: HISTORIAL ────────────────────────────────────────────────────────

function ScreenHistorial({ historial, loading }) {
  if (loading) return (
    <div style={{ display:"flex", justifyContent:"center", padding:"80px" }}>
      <Spinner size={36} color="#3B82F6"/>
    </div>
  );

  const terminados = historial.filter(h => {
    const e = (h.estado || "").toUpperCase();
    return e === "COMPLETADO" || e === "FINALIZADO";
  });

  const promedio = terminados.length > 0
    ? (terminados.reduce((a,t) => a + (t.calificacion || 0), 0) / terminados.length).toFixed(1)
    : "—";

  return (
    <div style={{ maxWidth:"640px", margin:"0 auto", padding:"28px 24px" }}>
      <h1 style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
        fontSize:"22px", color:"#0F172A", letterSpacing:"-0.4px", margin:"0 0 6px" }}>
        Historial de trabajos
      </h1>
      <p style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"14px",
        color:"#64748B", margin:"0 0 20px" }}>
        {terminados.length} trabajos finalizados
      </p>

      <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)",
        gap:"12px", marginBottom:"24px" }}>
        {[
          { label:"Trabajos",  value:terminados.length, color:"#3B82F6" },
          { label:"Promedio",  value:`⭐ ${promedio}`,  color:"#F59E0B" },
          { label:"Este mes",  value:terminados.filter(t => {
              const d = new Date(t.fecha);
              const n = new Date();
              return d.getMonth()===n.getMonth() && d.getFullYear()===n.getFullYear();
            }).length, color:"#22C55E" },
        ].map(s => (
          <div key={s.label} style={{ background:"#fff", borderRadius:"14px",
            border:"1.5px solid #F1F5F9", padding:"16px", textAlign:"center",
            boxShadow:"0 2px 8px rgba(0,0,0,0.04)" }}>
            <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
              fontSize:"22px", color:s.color, marginBottom:"4px" }}>{s.value}</div>
            <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px", color:"#94A3B8" }}>
              {s.label}
            </div>
          </div>
        ))}
      </div>

      {terminados.length === 0 ? (
        <div style={{ textAlign:"center", padding:"60px 20px",
          border:"2px dashed #E2E8F0", borderRadius:"16px" }}>
          <div style={{ fontSize:"36px", marginBottom:"12px" }}>📋</div>
          <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"700",
            fontSize:"15px", color:"#94A3B8" }}>
            Todavía no tenés trabajos finalizados.
          </div>
        </div>
      ) : terminados.map(t => (
        <div key={t.id_solicitud} style={{ background:"#fff", borderRadius:"16px",
          border:"1.5px solid #F1F5F9", padding:"18px 20px",
          marginBottom:"10px", boxShadow:"0 2px 8px rgba(0,0,0,0.04)" }}>
          <div style={{ display:"flex", justifyContent:"space-between",
            alignItems:"flex-start", gap:"12px" }}>
            <div style={{ flex:1 }}>
              <div style={{ display:"flex", alignItems:"center",
                gap:"8px", marginBottom:"6px", flexWrap:"wrap" }}>
                <Badge label={t.etiqueta_ia || "PLOMERIA_GENERAL"}/>
              </div>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
                color:"#94A3B8", marginBottom:"8px" }}>
                {t.fecha ? new Date(t.fecha).toLocaleDateString("es-AR") : ""}
              </div>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"13px",
                color:"#475569", fontStyle:"italic" }}>
                "{t.descripcion_raw}"
              </div>
              {t.calificacion > 0 && (
                <div style={{ display:"flex", alignItems:"center", gap:"8px", marginTop:"8px" }}>
                  <Stars val={t.calificacion} size={14}/>
                  <span style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"700",
                    fontSize:"13px", color:"#92400E" }}>{t.calificacion}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── HOME PLOMERO ─────────────────────────────────────────────────────────────

export default function HomePlomero({ onLogout }) {
  const user    = useAuthStore(s => s.user);
  const logout  = useAuthStore(s => s.logout);

  const [screen,      setScreen]     = useState("solicitudes");
  const [disponible,  setDisponible] = useState(true);
  const [solicitudes, setSolicitudes]= useState([]);
  const [activos,     setActivos]    = useState([]);
  const [historial,   setHistorial]  = useState([]);
  const [loading,     setLoading]    = useState(false);

  // Cargar solicitudes pendientes del plomero
  const cargarSolicitudes = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get("/solicitudes/plomero/me");
      const todas = Array.isArray(res.data) ? res.data : [];
      setSolicitudes(todas.filter(s => {
        const e = (s.estado || "").toLowerCase();
        return e === "pendiente";
      }));
      setActivos(todas.filter(s => {
        const e = (s.estado || "").toLowerCase();
        return e === "aceptado";
      }));
      setHistorial(todas.filter(s => {
        const e = (s.estado || "").toUpperCase();
        return e === "COMPLETADO" || e === "FINALIZADO";
      }));
    } catch (e) {
      console.error("Error cargando solicitudes:", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { cargarSolicitudes(); }, [cargarSolicitudes]);

  // Polling cada 15 segundos
  useEffect(() => {
    const interval = setInterval(cargarSolicitudes, 15000);
    return () => clearInterval(interval);
  }, [cargarSolicitudes]);

  const handleToggleDisp = async () => {
    const nuevo = !disponible;
    setDisponible(nuevo);
    try {
      await api.patch("/plomeros/disponibilidad", null, { params: { disponible: nuevo } });
    } catch (e) {
      setDisponible(!nuevo); // revertir si falla
    }
  };

  const handleAceptar = async (idSolicitud) => {
    try {
      await api.patch(`/solicitudes/${idSolicitud}/responder`, null, { params: { accion: "aceptar" } });
      await cargarSolicitudes();
      setScreen("activos");
    } catch (e) {
      console.error("Error aceptando:", e);
    }
  };

  const handleRechazar = async (idSolicitud) => {
    try {
      await api.patch(`/solicitudes/${idSolicitud}/responder`, null, { params: { accion: "rechazar" } });
      await cargarSolicitudes();
    } catch (e) {
      console.error("Error rechazando:", e);
    }
  };

  const handleCambiarEstado = async (idSolicitud, nuevoEstado) => {
    // Actualizar estado del trabajo localmente
    setActivos(prev => prev.map(a =>
      a.id_solicitud === idSolicitud ? { ...a, estado_trabajo: nuevoEstado } : a
    ));
    if (nuevoEstado === "finalizado") {
      try {
        await api.patch(`/solicitudes/${idSolicitud}/responder`, null, { params: { accion: "completar" } });
        await cargarSolicitudes();
      } catch (e) {
        console.error("Error finalizando:", e);
      }
    }
  };

  const handleCancelar = async (idSolicitud) => {
    try {
      await api.patch(`/solicitudes/${idSolicitud}/responder`, null, { params: { accion: "rechazar" } });
      await cargarSolicitudes();
    } catch (e) {
      console.error("Error cancelando:", e);
    }
  };

  const handleLogout = () => {
    logout();
    onLogout();
  };

  return (
    <div style={{ minHeight:"100vh",
      background:"linear-gradient(160deg,#F0F9FF 0%,#F8FAFC 50%,#F0FDF4 100%)" }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
      <style>{`@keyframes _sp{to{transform:rotate(360deg)}}`}</style>

      <Header
        screen={screen}
        onNav={setScreen}
        disponible={disponible}
        onToggleDisp={handleToggleDisp}
        pendientes={solicitudes.length}
        user={user}
        onLogout={handleLogout}
      />

      {screen==="solicitudes" && (
        <ScreenSolicitudes
          solicitudes={solicitudes}
          onAceptar={handleAceptar}
          onRechazar={handleRechazar}
          disponible={disponible}
          loading={loading}
        />
      )}
      {screen==="activos" && (
        <ScreenActivos
          activos={activos}
          onCambiarEstado={handleCambiarEstado}
          onCancelar={handleCancelar}
          loading={loading}
        />
      )}
      {screen==="agenda" && <ScreenAgenda activos={activos}/>}
      {screen==="historial" && <ScreenHistorial historial={historial} loading={loading}/>}
    </div>
  );
}