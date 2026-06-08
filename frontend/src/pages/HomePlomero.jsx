import { useState, useEffect, useCallback } from "react";
import api from "../services/api";
import { useAuthStore } from "../store/authStore";
import ChatWidget from "../components/ChatWidget";
import BoletaMateriales from "../components/BoletaMateriales";
import { useNotificaciones } from "../hooks/useNotificaciones";

const BADGE_STYLES = {
  PLOMERIA_GENERAL: { bg:"#EFF6FF", text:"#1D4ED8" },
  DESTAPES:         { bg:"#E0F2FE", text:"#0369A1" },
  GAS_MATRICULADO:  { bg:"#FEF9C3", text:"#854D0E" },
  OBRA:             { bg:"#DCFCE7", text:"#15803D" },
  FILTRACIONES:     { bg:"#FEF9C3", text:"#854D0E" },
  CALEFACCION:      { bg:"#FFF7ED", text:"#C2410C" },
  Urgencias:        { bg:"#FEE2E2", text:"#B91C1C" },
};

const ESP_LABELS = {
  PLOMERIA_GENERAL: "Plomería general",
  DESTAPES:         "Destapes",
  GAS_MATRICULADO:  "Gas matriculado",
  OBRA:             "Obra",
  FILTRACIONES:     "Filtraciones",
  CALEFACCION:      "Calefacción",
};

// Estados del backend → etiqueta visual para el plomero
const ESTADO_INFO = {
  pendiente:              { label:"Pendiente de aceptar",  icon:"⏳", color:"#F59E0B", bg:"#FFFBEB" },
  en_progreso:            { label:"Trabajo aceptado",      icon:"✅", color:"#22C55E", bg:"#F0FDF4" },
  en_camino:              { label:"En camino",             icon:"🚗", color:"#3B82F6", bg:"#EFF6FF" },
  pendiente_calificacion: { label:"Esperando calificación",icon:"⭐", color:"#F59E0B", bg:"#FFFBEB" },
  completada:             { label:"Completado",            icon:"🏁", color:"#64748B", bg:"#F8FAFC" },
};

// Flujo visual para el cliente (lo que ve el plomero como barra de progreso)
const FLUJO_VISUAL = [
  { key:"pendiente",   label:"Aceptado",   icon:"✅" },
  { key:"en_camino",   label:"En camino",  icon:"🚗" },
  { key:"completada",  label:"Finalizado", icon:"🏁" },
];

const MONTHS     = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"];
const DAYS_FULL  = ["Dom","Lun","Mar","Mié","Jue","Vie","Sáb"];

function Badge({ label }) {
  const key = label?.toUpperCase().replace(/ /g,"_");
  const s = BADGE_STYLES[label] || BADGE_STYLES[key] || { bg:"#F3F4F6", text:"#374151" };
  const display = ESP_LABELS[label] || ESP_LABELS[key] || label;
  return (
    <span style={{ background:s.bg, color:s.text, fontSize:"11px", fontWeight:"700",
      padding:"3px 10px", borderRadius:"20px", fontFamily:"'DM Sans',sans-serif",
      whiteSpace:"nowrap" }}>{display}</span>
  );
}

function Stars({ val, size=13 }) {
  return (
    <div style={{ display:"flex", gap:"2px" }}>
      {[1,2,3,4,5].map(i => (
        <svg key={i} width={size} height={size} viewBox="0 0 24 24">
          <polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"
            fill={i<=val ? "#FBBF24" : "#E5E7EB"} />
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
      style={{ width:size, height:size, borderRadius:"12px", objectFit:"cover", flexShrink:0 }}/>
  );
  return (
    <div style={{ width:size, height:size, borderRadius:"12px", flexShrink:0,
      background:"linear-gradient(135deg,#22C55E,#16A34A)",
      display:"flex", alignItems:"center", justifyContent:"center",
      fontSize:size*0.32, fontWeight:"800", color:"#fff", fontFamily:"'DM Sans',sans-serif" }}>
      {nombre?.[0]}{apellido?.[0]}
    </div>
  );
}

function Spinner({ size=20, color="#fff" }) {
  return (
    <>
      <style>{`@keyframes _sp{to{transform:rotate(360deg)}}`}</style>
      <div style={{ width:size, height:size, border:`2.5px solid rgba(255,255,255,0.3)`,
        borderTop:`2.5px solid ${color}`, borderRadius:"50%",
        animation:"_sp 0.7s linear infinite", flexShrink:0 }}/>
    </>
  );
}

// ─── HEADER ──────────────────────────────────────────────────────────────────
function Header({ screen, onNav, disponible, onToggleDisp, pendientes, notifCount, user, onLogout }) {
  const tabs = [
    { key:"solicitudes", label:"Solicitudes", icon:"📬", badge:pendientes },
    { key:"activos",     label:"En curso",    icon:"🔧" },
    { key:"agenda",      label:"Mi agenda",   icon:"📅" },
    { key:"historial",   label:"Historial",   icon:"📋" },
    { key:"alertas",     label:"Alertas",     icon:"🔔", badge:notifCount },
  ];
  return (
    <div style={{ background:"linear-gradient(135deg,#0F172A,#1E3A5F)",
      padding:"0 24px", position:"sticky", top:0, zIndex:100 }}>
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between",
        paddingTop:"14px", paddingBottom:"10px", borderBottom:"1px solid rgba(255,255,255,0.08)" }}>
        <div style={{ display:"flex", alignItems:"center", gap:"12px" }}>
          <div style={{ background:"linear-gradient(135deg,#3B82F6,#06B6D4)", borderRadius:"10px",
            width:"34px", height:"34px", display:"flex", alignItems:"center",
            justifyContent:"center", fontSize:"16px" }}>🔧</div>
          <div>
            <span style={{ fontWeight:"800", fontSize:"18px", color:"#fff",
              letterSpacing:"-0.4px", fontFamily:"'DM Sans',sans-serif" }}>
              Plomer<span style={{ color:"#38BDF8" }}>IA</span>
            </span>
            <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"11px",
              color:"#475569", marginTop:"1px" }}>
              {user?.nombre} · Panel Profesional
            </div>
          </div>
        </div>
        <div style={{ display:"flex", alignItems:"center", gap:"12px" }}>
          <div style={{ display:"flex", alignItems:"center", gap:"8px" }}>
            <div style={{ textAlign:"right" }}>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"10px", fontWeight:"700",
                color:"#475569", textTransform:"uppercase", letterSpacing:"0.6px" }}>Disponibilidad</div>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px", fontWeight:"700",
                color: disponible ? "#34D399" : "#F87171" }}>
                {disponible ? "Activo" : "Inactivo"}
              </div>
            </div>
            <button onClick={onToggleDisp} style={{
              width:"48px", height:"26px", borderRadius:"13px", border:"none",
              background: disponible ? "linear-gradient(135deg,#22C55E,#16A34A)" : "#334155",
              cursor:"pointer", position:"relative", transition:"all 0.25s",
              boxShadow: disponible ? "0 0 12px rgba(34,197,94,0.4)" : "none",
            }}>
              <div style={{ position:"absolute", top:"3px", left: disponible ? "25px" : "3px",
                width:"20px", height:"20px", borderRadius:"50%", background:"#fff",
                transition:"left 0.25s", boxShadow:"0 1px 4px rgba(0,0,0,0.2)" }}/>
            </button>
          </div>
          <button onClick={onLogout} style={{
            background:"rgba(239,68,68,0.1)", border:"1px solid rgba(239,68,68,0.25)",
            borderRadius:"8px", padding:"5px 12px", color:"#FCA5A5",
            fontSize:"12px", fontWeight:"600", cursor:"pointer", fontFamily:"'DM Sans',sans-serif",
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
            transition:"all 0.18s", whiteSpace:"nowrap",
          }}>
            <span>{t.icon}</span>
            <span>{t.label}</span>
            {t.badge > 0 && (
              <div style={{ background:"#EF4444", color:"#fff", borderRadius:"10px",
                fontSize:"10px", fontWeight:"800", padding:"1px 6px", minWidth:"16px" }}>
                {t.badge}
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}

// ─── SCREEN: SOLICITUDES ENTRANTES ────────────────────────────────────────────
function ScreenSolicitudes({ solicitudes, onAceptar, onRechazar, disponible, loading }) {
  const [expandido, setExpandido] = useState(null);
  const [loadingId, setLoadingId] = useState(null);

  if (!disponible) return (
    <div style={{ maxWidth:"560px", margin:"0 auto", padding:"60px 24px", textAlign:"center" }}>
      <div style={{ fontSize:"48px", marginBottom:"16px" }}>😴</div>
      <h2 style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800", fontSize:"20px",
        color:"#0F172A", margin:"0 0 8px" }}>Estás inactivo</h2>
      <p style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"14px", color:"#64748B" }}>
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
      <h2 style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800", fontSize:"20px",
        color:"#0F172A", margin:"0 0 8px" }}>Sin solicitudes nuevas</h2>
      <p style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"14px", color:"#64748B" }}>
        Te avisamos cuando llegue una.
      </p>
    </div>
  );

  return (
    <div style={{ maxWidth:"640px", margin:"0 auto", padding:"28px 24px" }}>
      <h1 style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800", fontSize:"22px",
        color:"#0F172A", letterSpacing:"-0.4px", margin:"0 0 6px" }}>
        Solicitudes entrantes
      </h1>
      <p style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"14px",
        color:"#64748B", margin:"0 0 24px" }}>
        El primero en aceptar queda asignado · La dirección se revela al aceptar
      </p>

      {solicitudes.map(s => {
        const esUrgente = (s.urgencia_ia || "").toUpperCase() === "URGENTE";
        return (
          <div key={s.id_solicitud} style={{
            background:"#fff", borderRadius:"20px",
            border: esUrgente ? "2px solid #FCA5A5" : "2px solid #F1F5F9",
            padding:"20px", marginBottom:"14px",
            boxShadow: esUrgente ? "0 4px 20px rgba(239,68,68,0.08)" : "0 2px 12px rgba(0,0,0,0.05)",
          }}>
            {/* Encabezado */}
            <div style={{ display:"flex", justifyContent:"space-between",
              alignItems:"flex-start", marginBottom:"14px", gap:"12px" }}>
              <div style={{ flex:1 }}>
                <div style={{ display:"flex", alignItems:"center",
                  gap:"8px", flexWrap:"wrap", marginBottom:"6px" }}>
                  <Badge label={s.etiqueta_ia || "PLOMERIA_GENERAL"}/>
                  {esUrgente && (
                    <span style={{ background:"#FEE2E2", color:"#B91C1C", fontSize:"11px",
                      fontWeight:"800", padding:"3px 10px", borderRadius:"20px",
                      fontFamily:"'DM Sans',sans-serif" }}>🚨 URGENTE</span>
                  )}
                </div>
                <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"13px", color:"#94A3B8" }}>
                  📍 {s.localidad_evento || "Sin localidad"} ·{" "}
                  {s.fecha ? new Date(s.fecha).toLocaleString("es-AR") : ""}
                </div>
                {s.turno_solicitado && (
                  <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
                    color:"#15803D", fontWeight:"600", marginTop:"4px" }}>
                    📅 Turno pedido: {s.turno_solicitado.replace(/_/g," ")}
                  </div>
                )}
              </div>
            </div>

            {/* Descripción */}
            <div style={{ background:"#F8FAFC", border:"1.5px solid #E2E8F0",
              borderRadius:"12px", padding:"12px 14px", marginBottom:"14px" }}>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"10px",
                fontWeight:"700", color:"#94A3B8", textTransform:"uppercase",
                letterSpacing:"0.8px", marginBottom:"6px" }}>Lo que describe el cliente</div>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"13px",
                color:"#334155", lineHeight:"1.6",
                maxHeight: expandido===s.id_solicitud ? "none" : "48px", overflow:"hidden" }}>
                "{s.descripcion_raw}"
              </div>
              {(s.descripcion_raw?.length || 0) > 120 && (
                <button onClick={()=>setExpandido(expandido===s.id_solicitud ? null : s.id_solicitud)}
                  style={{ background:"none", border:"none", cursor:"pointer",
                    fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
                    color:"#3B82F6", fontWeight:"600", padding:"4px 0 0", display:"block" }}>
                  {expandido===s.id_solicitud ? "Ver menos ↑" : "Ver más ↓"}
                </button>
              )}
            </div>

            {/* Diagnóstico técnico de la IA */}
            {s.diagnostico_ia && (
              <div style={{ background:"#EFF6FF", border:"1.5px solid #BFDBFE",
                borderRadius:"12px", padding:"12px 14px", marginBottom:"14px" }}>
                <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"10px",
                  fontWeight:"700", color:"#1D4ED8", textTransform:"uppercase",
                  letterSpacing:"0.8px", marginBottom:"6px" }}>🔧 Diagnóstico</div>
                <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"13px",
                  color:"#1E3A8A", fontWeight:"600", lineHeight:"1.5" }}>
                  {s.diagnostico_ia}
                </div>
              </div>
            )}

            {esUrgente && (() => {
              const h = s.fecha ? new Date(s.fecha).getHours() : new Date().getHours();
              const tardio = h >= 21 || h < 7;
              return (
                <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
                  color:"#B45309", background:"#FFFBEB", border:"1px solid #FDE68A",
                  borderRadius:"8px", padding:"8px 12px", marginBottom:"10px", fontWeight:"600" }}>
                  {tardio
                    ? "⏰ Urgencia nocturna: respondé a primera hora (desde las 7am) — tenés 30 min desde entonces."
                    : "⏰ Urgencia: tenés 30 minutos para responder."}
                </div>
              );
            })()}

            <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"11px",
              color:"#94A3B8", marginBottom:"14px", display:"flex", alignItems:"center", gap:"5px" }}>
              🔒 La dirección exacta se revela solo si aceptás el trabajo
            </div>

            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"10px" }}>
              <button onClick={()=>{ setLoadingId(s.id_solicitud+"_r"); onRechazar(s.id_solicitud).finally(()=>setLoadingId(null)); }}
                disabled={!!loadingId} style={{
                  background:"#FEF2F2", border:"1.5px solid #FECACA", borderRadius:"12px",
                  padding:"12px", fontFamily:"'DM Sans',sans-serif", fontWeight:"700",
                  fontSize:"14px", color:"#EF4444", cursor:"pointer",
                }}>✕ Rechazar</button>
              <button onClick={()=>{ setLoadingId(s.id_solicitud); onAceptar(s.id_solicitud).finally(()=>setLoadingId(null)); }}
                disabled={!!loadingId} style={{
                  background:"linear-gradient(135deg,#22C55E,#16A34A)", border:"none",
                  borderRadius:"12px", padding:"12px", fontFamily:"'DM Sans',sans-serif",
                  fontWeight:"700", fontSize:"14px", color:"#fff", cursor:"pointer",
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

// ─── SCREEN: EN CURSO ─────────────────────────────────────────────────────────
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
    if (diff <= 0) diff += 7;
    const fecha = new Date(hoy);
    fecha.setDate(hoy.getDate() + diff);
    const fechaStr = `${fecha.getDate()}/${fecha.getMonth() + 1}`;
    return hora !== null ? `${dia} ${fechaStr} a las ${hora}:00hs` : `${dia} ${fechaStr}`;
  } catch { return turnoStr.replace(/_/g, " "); }
}

function ScreenActivos({ activos, onEnCamino, onCompletar, onCancelar, onReprogramar, loading }) {
  const [loadingId,  setLoadingId]  = useState(null);
  const [cancelando, setCancelando] = useState(null);
  const [reprog,     setReprog]     = useState(null);  // id con form de reprogramar abierto
  const [nuevaFecha, setNuevaFecha] = useState("");

  if (loading) return (
    <div style={{ display:"flex", justifyContent:"center", padding:"80px" }}>
      <Spinner size={36} color="#3B82F6"/>
    </div>
  );

  if (activos.length===0) return (
    <div style={{ maxWidth:"560px", margin:"0 auto", padding:"60px 24px", textAlign:"center" }}>
      <div style={{ fontSize:"48px", marginBottom:"16px" }}>✅</div>
      <h2 style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800", fontSize:"20px",
        color:"#0F172A", margin:"0 0 8px" }}>Sin trabajos activos</h2>
      <p style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"14px", color:"#64748B" }}>
        Aceptá una solicitud para verla acá.
      </p>
    </div>
  );

  return (
    <div style={{ maxWidth:"640px", margin:"0 auto", padding:"28px 24px" }}>
      <h1 style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800", fontSize:"22px",
        color:"#0F172A", letterSpacing:"-0.4px", margin:"0 0 24px" }}>
        Trabajos en curso
      </h1>

      {activos.map(t => {
        const estadoVal = (t.estado || "en_progreso").toLowerCase();
        const info = ESTADO_INFO[estadoVal] || ESTADO_INFO.en_progreso;
        const esEnCamino  = estadoVal === "en_camino";
        const esEnProgreso = estadoVal === "en_progreso";

        // Índice en barra visual
        const idxFlujo = estadoVal === "en_progreso" ? 0
          : estadoVal === "en_camino" ? 1 : 2;

        return (
          <div key={t.id_solicitud} style={{
            background:"#fff", borderRadius:"20px", border:"2px solid #F1F5F9",
            padding:"22px", marginBottom:"16px", boxShadow:"0 4px 20px rgba(0,0,0,0.06)",
          }}>
            {/* Estado actual */}
            <div style={{ display:"flex", alignItems:"center",
              justifyContent:"space-between", marginBottom:"18px" }}>
              <div style={{ display:"flex", alignItems:"center", gap:"10px" }}>
                <div style={{ background:info.bg, border:`1.5px solid ${info.color}33`,
                  borderRadius:"12px", width:"44px", height:"44px",
                  display:"flex", alignItems:"center", justifyContent:"center",
                  fontSize:"20px" }}>{info.icon}</div>
                <div>
                  <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
                    fontSize:"15px", color:info.color }}>{info.label}</div>
                  <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px", color:"#94A3B8" }}>
                    {t.fecha ? new Date(t.fecha).toLocaleString("es-AR") : ""}
                  </div>
                </div>
              </div>
              <Badge label={t.etiqueta_ia || "PLOMERIA_GENERAL"}/>
            </div>

            {/* Barra de progreso */}
            <div style={{ display:"flex", alignItems:"center", marginBottom:"20px" }}>
              {FLUJO_VISUAL.map((f, i) => {
                const done    = i < idxFlujo;
                const current = i === idxFlujo;
                return (
                  <div key={f.key} style={{ display:"flex", alignItems:"center",
                    flex: i < FLUJO_VISUAL.length - 1 ? 1 : "none" }}>
                    <div style={{ display:"flex", flexDirection:"column", alignItems:"center", gap:"4px" }}>
                      <div style={{ width:"32px", height:"32px", borderRadius:"50%",
                        background: done ? "#22C55E" : current ? info.color : "#F1F5F9",
                        display:"flex", alignItems:"center", justifyContent:"center", fontSize:"14px",
                        border: current ? `2px solid ${info.color}` : "none",
                        boxShadow: current ? `0 0 0 3px ${info.color}22` : "none",
                      }}>
                        {done ? "✓" : f.icon}
                      </div>
                      <span style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"9px",
                        fontWeight:"600", color: done ? "#22C55E" : current ? info.color : "#CBD5E1",
                        textAlign:"center", whiteSpace:"nowrap" }}>{f.label}</span>
                    </div>
                    {i < FLUJO_VISUAL.length - 1 && (
                      <div style={{ flex:1, height:"2px", margin:"0 4px", marginBottom:"18px",
                        background: done ? "#22C55E" : "#E2E8F0" }}/>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Datos del cliente */}
            <div style={{ background:"#F8FAFC", borderRadius:"12px", padding:"14px", marginBottom:"16px" }}>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"10px", fontWeight:"700",
                color:"#94A3B8", textTransform:"uppercase", letterSpacing:"0.8px", marginBottom:"10px" }}>
                Datos del cliente
              </div>
              <div style={{ display:"flex", flexDirection:"column", gap:"8px" }}>
                {[
                  ["Problema",       t.descripcion_raw],
                  ...(t.diagnostico_ia ? [["Diagnóstico", t.diagnostico_ia]] : []),
                  ["Localidad",      t.localidad_evento || "—"],
                  ["Día del trabajo", t.fecha_trabajo
                    ? new Date(t.fecha_trabajo).toLocaleString("es-AR", { weekday:"short", day:"numeric", month:"numeric", hour:"2-digit", minute:"2-digit" })
                    : (t.turno_solicitado ? formatearTurno(t.turno_solicitado) : "A confirmar")],
                ].map(([k,v]) => (
                  <div key={k} style={{ display:"flex", justifyContent:"space-between", gap:"8px" }}>
                    <span style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
                      color:"#94A3B8", flexShrink:0 }}>{k}</span>
                    <span style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"700",
                      fontSize:"13px", color:"#0F172A", textAlign:"right" }}>{v}</span>
                  </div>
                ))}

                {/* Dirección — solo visible después de aceptar */}
                {t.direccion_cliente && (
                  <div style={{ marginTop:"4px", padding:"8px 12px",
                    background:"#EFF6FF", border:"1px solid #BFDBFE", borderRadius:"8px" }}>
                    <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"10px",
                      fontWeight:"700", color:"#1D4ED8", textTransform:"uppercase",
                      letterSpacing:"0.6px", marginBottom:"4px" }}>📍 Dirección del cliente</div>
                    <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
                      fontSize:"14px", color:"#0F172A" }}>{t.direccion_cliente}</div>
                  </div>
                )}
              </div>
            </div>

            {/* Presupuesto estimado (materiales) que calculó la IA */}
            {t.presupuesto_max > 0 && (
              <div style={{ background:"#FFFBEB", border:"1px solid #FDE68A", borderRadius:"10px",
                padding:"10px 14px", marginBottom:"12px", fontFamily:"'DM Sans',sans-serif",
                fontSize:"12px", color:"#92400E" }}>
                💰 Presupuesto estimado (materiales): <strong>${Number(t.presupuesto_min||0).toLocaleString("es-AR")} – ${Number(t.presupuesto_max||0).toLocaleString("es-AR")}</strong>
              </div>
            )}

            {/* Boleta editable mientras el trabajo está en curso */}
            <BoletaMateriales idSolicitud={t.id_solicitud} editable diagnostico={t.diagnostico_ia || t.etiqueta_ia} fecha={t.fecha} />

            {/* Botones de acción según estado */}
            {esEnProgreso && (() => {
              // "En camino" se habilita desde 2 h antes del horario acordado.
              let puede = true, desdeTxt = "";
              if (t.fecha_trabajo) {
                const ft = new Date(t.fecha_trabajo);
                const habilita = new Date(ft.getTime() - 2 * 60 * 60 * 1000);
                puede = new Date() >= habilita;
                desdeTxt = habilita.toLocaleString("es-AR", { weekday:"short", hour:"2-digit", minute:"2-digit" });
              }
              return (
                <button
                  onClick={async () => {
                    setLoadingId("camino_" + t.id_solicitud);
                    await onEnCamino(t.id_solicitud);
                    setLoadingId(null);
                  }}
                  disabled={!!loadingId || !puede}
                  title={!puede ? `Disponible desde ${desdeTxt} (2 h antes del turno)` : ""}
                  style={{ width:"100%",
                    background: puede ? "linear-gradient(135deg,#3B82F6,#2563EB)" : "#E2E8F0",
                    border:"none", borderRadius:"14px", padding:"13px",
                    fontFamily:"'DM Sans',sans-serif", fontWeight:"800", fontSize:"14px",
                    color: puede ? "#fff" : "#94A3B8",
                    cursor: puede ? "pointer" : "not-allowed",
                    marginBottom:"10px",
                    boxShadow: puede ? "0 4px 14px rgba(59,130,246,0.3)" : "none",
                    display:"flex", alignItems:"center", justifyContent:"center", gap:"8px",
                  }}>
                  {loadingId === "camino_" + t.id_solicitud ? <Spinner size={16}/> : null}
                  🚗 {puede ? "Voy en camino" : `Disponible ${desdeTxt}`}
                </button>
              );
            })()}

            {esEnCamino && (() => {
              // "Finalizar" se habilita a partir de la hora del turno.
              let puede = true, horaTxt = "";
              if (t.fecha_trabajo) {
                const ft = new Date(t.fecha_trabajo);
                puede = new Date() >= ft;
                horaTxt = ft.toLocaleTimeString("es-AR", { hour:"2-digit", minute:"2-digit" });
              }
              return (
                <button
                  onClick={async () => {
                    if (!puede) return;
                    setLoadingId("completar_" + t.id_solicitud);
                    await onCompletar(t.id_solicitud);
                    setLoadingId(null);
                  }}
                  disabled={!!loadingId || !puede}
                  title={!puede ? `Podés finalizar a partir de las ${horaTxt}` : ""}
                  style={{ width:"100%",
                    background: puede ? "linear-gradient(135deg,#22C55E,#16A34A)" : "#E2E8F0",
                    border:"none", borderRadius:"14px", padding:"13px",
                    fontFamily:"'DM Sans',sans-serif", fontWeight:"800", fontSize:"14px",
                    color: puede ? "#fff" : "#94A3B8", cursor: puede ? "pointer" : "not-allowed",
                    marginBottom:"10px",
                    boxShadow: puede ? "0 4px 14px rgba(34,197,94,0.3)" : "none",
                    display:"flex", alignItems:"center", justifyContent:"center", gap:"8px",
                  }}>
                  {loadingId === "completar_" + t.id_solicitud ? <Spinner size={16}/> : null}
                  🏁 {puede ? "Terminé el trabajo" : `Finalizar disponible ${horaTxt}`}
                </button>
              );
            })()}

            {/* Reprogramar horario (si lo acuerdan por chat) */}
            {reprog === t.id_solicitud ? (
              <div style={{ marginBottom:"10px", background:"#F8FAFC", border:"1px solid #E2E8F0",
                borderRadius:"10px", padding:"12px" }}>
                <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px", fontWeight:"700",
                  color:"#475569", marginBottom:"6px" }}>Nueva fecha y hora del trabajo</div>
                <input type="datetime-local" value={nuevaFecha} onChange={e=>setNuevaFecha(e.target.value)}
                  style={{ width:"100%", border:"1.5px solid #E2E8F0", borderRadius:"8px", padding:"8px",
                    fontFamily:"'DM Sans',sans-serif", fontSize:"13px", marginBottom:"8px", boxSizing:"border-box" }} />
                <div style={{ display:"flex", gap:"8px" }}>
                  <button onClick={()=>{ setReprog(null); setNuevaFecha(""); }} style={{
                    background:"#fff", border:"1px solid #E2E8F0", borderRadius:"8px", padding:"8px 12px",
                    fontFamily:"'DM Sans',sans-serif", fontSize:"12px", color:"#475569", cursor:"pointer", fontWeight:"600" }}>
                    Cancelar
                  </button>
                  <button disabled={!nuevaFecha}
                    onClick={async ()=>{ await onReprogramar(t.id_solicitud, nuevaFecha); setReprog(null); setNuevaFecha(""); }}
                    style={{ flex:1, background: nuevaFecha ? "linear-gradient(135deg,#3B82F6,#2563EB)" : "#E2E8F0",
                      color: nuevaFecha ? "#fff" : "#94A3B8", border:"none", borderRadius:"8px", padding:"8px",
                      fontFamily:"'DM Sans',sans-serif", fontWeight:"700", fontSize:"13px",
                      cursor: nuevaFecha ? "pointer" : "not-allowed" }}>
                    Guardar nuevo horario
                  </button>
                </div>
              </div>
            ) : t.comunicacion_ok ? (
              <button onClick={()=>{ setReprog(t.id_solicitud); setNuevaFecha(""); }} style={{
                marginBottom:"10px", width:"100%", background:"transparent", border:"1px solid #BFDBFE",
                borderRadius:"10px", padding:"9px", fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
                color:"#1D4ED8", cursor:"pointer", fontWeight:"600" }}>
                🗓️ Reprogramar horario
              </button>
            ) : (
              <button
                onClick={() => window.dispatchEvent(new CustomEvent("plomeria:abrir-chat", { detail: { idSolicitud: t.id_solicitud } }))}
                style={{ marginBottom:"10px", width:"100%", background:"#F8FAFC",
                  border:"1px dashed #CBD5E1", borderRadius:"10px", padding:"9px",
                  fontFamily:"'DM Sans',sans-serif", fontSize:"11px", color:"#64748B",
                  textAlign:"center", fontWeight:"600", cursor:"pointer" }}>
                🗓️💬 Para reprogramar, coordiná primero por el chat (tocá acá para escribirle)
              </button>
            )}

            {/* Cancelar */}
            {cancelando === t.id_solicitud ? (
              <div style={{ marginTop:"10px", background:"#FEF2F2",
                border:"1px solid #FECACA", borderRadius:"10px", padding:"12px",
                display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                <span style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
                  color:"#B91C1C", fontWeight:"600" }}>¿Cancelar este trabajo?</span>
                <div style={{ display:"flex", gap:"8px" }}>
                  <button onClick={() => setCancelando(null)} style={{
                    background:"#F8FAFC", border:"1px solid #E2E8F0", borderRadius:"7px",
                    padding:"5px 12px", fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
                    color:"#475569", cursor:"pointer", fontWeight:"600" }}>No</button>
                  <button onClick={async () => {
                    setLoadingId("cancel_" + t.id_solicitud);
                    await onCancelar(t.id_solicitud);
                    setLoadingId(null);
                    setCancelando(null);
                  }} disabled={!!loadingId} style={{
                    background:"#EF4444", border:"none", borderRadius:"7px", padding:"5px 12px",
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
            )}
          </div>
        );
      })}
    </div>
  );
}

// ─── SCREEN: AGENDA ───────────────────────────────────────────────────────────
// activos  = trabajos en curso (en_progreso, en_camino)  → azul
// historial = trabajos completados                        → verde
// Cancelados no aparecen (se excluyen desde cargarSolicitudes)

function _fechaISO(s) {
  // Devuelve "YYYY-MM-DD" o null.
  // Prioridad: fecha_trabajo (fecha real del trabajo) → fecha de creación.
  // No derivamos del turno: eso calculaba siempre el próximo día de la semana
  // (futuro), y un trabajo YA finalizado terminaba apareciendo en una fecha
  // futura. La fecha real del trabajo la define fecha_trabajo (backend).
  if (s.fecha_trabajo) return s.fecha_trabajo.split("T")[0];
  // Fallback: fecha de creación, para que un trabajo terminado sin fecha
  // de trabajo igual aparezca en el calendario (en el día que se registró).
  if (s.fecha) return s.fecha.split("T")[0];
  return null;
}

function ScreenAgenda({ activos, historial }) {
  const hoy = new Date();
  const [year,     setYear]     = useState(hoy.getFullYear());
  const [month,    setMonth]    = useState(hoy.getMonth());
  const [selected, setSelected] = useState(null);

  const firstDay    = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month+1, 0).getDate();
  const fmt = d => `${year}-${String(month+1).padStart(2,"0")}-${String(d).padStart(2,"0")}`;

  // Construir mapa de fechas con sus trabajos y tipo (activo | finalizado)
  const mapaFechas = {};

  (activos || []).forEach(s => {
    const fecha = _fechaISO(s);
    if (!fecha) return;
    if (!mapaFechas[fecha]) mapaFechas[fecha] = [];
    mapaFechas[fecha].push({
      tipo:        "activo",
      descripcion: s.diagnostico_ia || s.descripcion_raw,
      etiqueta:    s.etiqueta_ia,
      cliente:     s.nombre_cliente,
      localidad:   s.localidad_evento,
      direccion:   s.direccion_cliente,
      hora:        s.turno_solicitado?.split("_")[2]
                     ? `${s.turno_solicitado.split("_")[2]}:00hs` : null,
      estado:      s.estado,
    });
  });

  (historial || []).forEach(s => {
    const fecha = _fechaISO(s);
    if (!fecha) return;
    if (!mapaFechas[fecha]) mapaFechas[fecha] = [];
    mapaFechas[fecha].push({
      tipo:        "finalizado",
      descripcion: s.diagnostico_ia || s.descripcion_raw,
      etiqueta:    s.etiqueta_ia,
      cliente:     s.nombre_cliente,
      localidad:   s.localidad_evento,
      direccion:   s.direccion_cliente,
      hora:        s.turno_solicitado?.split("_")[2]
                     ? `${s.turno_solicitado.split("_")[2]}:00hs` : null,
      estado:      s.estado,
    });
  });

  const selectedJobs = selected ? (mapaFechas[selected] || []) : [];

  const prev = () => { if(month===0){setMonth(11);setYear(y=>y-1);}else setMonth(m=>m-1); setSelected(null); };
  const next = () => { if(month===11){setMonth(0);setYear(y=>y+1);}else setMonth(m=>m+1); setSelected(null); };

  // Color del punto/día según contenido:
  // solo finalizados → verde; alguno activo → azul; mezcla → mitad/mitad → azul (prioridad activo)
  function colorDia(ds) {
    const jobs = mapaFechas[ds] || [];
    if (jobs.length === 0) return null;
    const tieneActivo = jobs.some(j => j.tipo === "activo");
    return tieneActivo ? "activo" : "finalizado";
  }

  return (
    <div style={{ maxWidth:"860px", margin:"0 auto", padding:"28px 24px" }}>
      <h1 style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800", fontSize:"22px",
        color:"#0F172A", margin:"0 0 8px" }}>Mi agenda</h1>

      {/* Leyenda de colores */}
      <div style={{ display:"flex", gap:"16px", marginBottom:"20px", flexWrap:"wrap" }}>
        {[
          { color:"#3B82F6", bg:"#EFF6FF", label:"Trabajo pendiente / en curso" },
          { color:"#16A34A", bg:"#F0FDF4", label:"Trabajo finalizado" },
        ].map(l => (
          <div key={l.label} style={{ display:"flex", alignItems:"center", gap:"7px" }}>
            <div style={{ width:"10px", height:"10px", borderRadius:"50%", background:l.color }}/>
            <span style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px", color:"#64748B" }}>{l.label}</span>
          </div>
        ))}
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"16px", alignItems:"start" }}>

        {/* ── Calendario ── */}
        <div style={{ background:"#fff", borderRadius:"16px",
          border:"1.5px solid #F1F5F9", padding:"16px",
          boxShadow:"0 4px 20px rgba(0,0,0,0.06)" }}>

          <div style={{ display:"flex", alignItems:"center",
            justifyContent:"space-between", marginBottom:"14px" }}>
            <button onClick={prev} style={{ background:"#F1F5F9", border:"none", borderRadius:"8px",
              width:"30px", height:"30px", cursor:"pointer", fontSize:"16px", color:"#475569",
              display:"flex", alignItems:"center", justifyContent:"center" }}>‹</button>
            <span style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
              fontSize:"14px", color:"#0F172A" }}>{MONTHS[month]} {year}</span>
            <button onClick={next} style={{ background:"#F1F5F9", border:"none", borderRadius:"8px",
              width:"30px", height:"30px", cursor:"pointer", fontSize:"16px", color:"#475569",
              display:"flex", alignItems:"center", justifyContent:"center" }}>›</button>
          </div>

          {/* Días de semana */}
          <div style={{ display:"grid", gridTemplateColumns:"repeat(7,1fr)",
            gap:"2px", marginBottom:"6px" }}>
            {DAYS_FULL.map(d => (
              <div key={d} style={{ textAlign:"center", fontSize:"10px", fontWeight:"700",
                color:"#94A3B8", fontFamily:"'DM Sans',sans-serif", padding:"3px 0" }}>{d}</div>
            ))}
          </div>

          {/* Grilla de días */}
          <div style={{ display:"grid", gridTemplateColumns:"repeat(7,1fr)", gap:"3px" }}>
            {Array.from({length:firstDay}).map((_,i)=><div key={`e${i}`}/>)}
            {Array.from({length:daysInMonth}).map((_,i)=>{
              const d      = i + 1;
              const ds     = fmt(d);
              const isHoy  = new Date(year,month,d).toDateString() === hoy.toDateString();
              const color  = colorDia(ds);   // "activo" | "finalizado" | null
              const isSel  = selected === ds;
              const esActivo    = color === "activo";
              const esFinalizado = color === "finalizado";

              return (
                <button key={d}
                  onClick={() => setSelected(isSel ? null : ds)}
                  style={{
                    border:"none", borderRadius:"8px", padding:"6px 2px",
                    cursor: "pointer",
                    fontFamily:"'DM Sans',sans-serif", position:"relative",
                    fontWeight: isHoy || color ? "800" : "400", fontSize:"12px",
                    transition:"all 0.15s",
                    background: isSel
                      ? (esActivo ? "#3B82F6" : "#16A34A")
                      : esActivo    ? "#EFF6FF"
                      : esFinalizado ? "#F0FDF4"
                      : isHoy       ? "#FEF9C3"
                      : "transparent",
                    color: isSel    ? "#fff"
                      : esActivo    ? "#1D4ED8"
                      : esFinalizado ? "#15803D"
                      : isHoy       ? "#92400E"
                      : "#94A3B8",
                  }}>
                  {d}
                  {/* Punto de color en días con trabajos (cuando no está seleccionado) */}
                  {color && !isSel && (
                    <div style={{
                      position:"absolute", bottom:"2px", left:"50%",
                      transform:"translateX(-50%)", width:"4px", height:"4px",
                      borderRadius:"50%",
                      background: esActivo ? "#3B82F6" : "#16A34A",
                    }}/>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* ── Panel detalle ── */}
        <div style={{ background:"#fff", borderRadius:"16px",
          border:"1.5px solid #F1F5F9", padding:"16px",
          boxShadow:"0 4px 20px rgba(0,0,0,0.06)", minHeight:"240px" }}>

          {!selected ? (
            <div style={{ display:"flex", flexDirection:"column", alignItems:"center",
              justifyContent:"center", height:"100%", minHeight:"200px", textAlign:"center" }}>
              <div style={{ fontSize:"36px", marginBottom:"10px" }}>📅</div>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"700",
                fontSize:"14px", color:"#94A3B8" }}>Seleccioná un día</div>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
                color:"#CBD5E1", lineHeight:"1.6", marginTop:"6px" }}>
                Los días marcados tienen trabajos asignados
              </div>
            </div>
          ) : (
            <>
              {/* Título del día seleccionado */}
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
                fontSize:"15px", color:"#0F172A", marginBottom:"2px" }}>
                {new Date(selected + "T12:00:00").toLocaleDateString("es-AR", {
                  weekday:"long", day:"numeric", month:"long"
                })}
              </div>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
                color:"#94A3B8", marginBottom:"14px" }}>
                {selectedJobs.length > 0
                  ? `${selectedJobs.length} trabajo${selectedJobs.length !== 1 ? "s" : ""}`
                  : "Sin trabajos"}
              </div>

              {selectedJobs.length === 0 ? (
                <div style={{ background:"#F8FAFC", borderRadius:"10px",
                  padding:"20px", textAlign:"center" }}>
                  <div style={{ fontFamily:"'DM Sans',sans-serif",
                    fontSize:"13px", color:"#94A3B8" }}>Día libre 🎉</div>
                </div>
              ) : (
                selectedJobs.map((j, i) => {
                  const esActivo = j.tipo === "activo";
                  return (
                    <div key={i} style={{
                      borderRadius:"12px", padding:"14px",
                      border:`1.5px solid ${esActivo ? "#BFDBFE" : "#BBF7D0"}`,
                      background: esActivo ? "#EFF6FF" : "#F0FDF4",
                      marginBottom:"10px",
                    }}>
                      {/* Tipo de trabajo */}
                      <div style={{ display:"flex", alignItems:"center",
                        gap:"8px", marginBottom:"8px" }}>
                        <span style={{
                          fontSize:"10px", fontWeight:"800", letterSpacing:"0.6px",
                          textTransform:"uppercase", padding:"2px 8px", borderRadius:"20px",
                          background: esActivo ? "#DBEAFE" : "#DCFCE7",
                          color: esActivo ? "#1D4ED8" : "#15803D",
                          fontFamily:"'DM Sans',sans-serif",
                        }}>
                          {esActivo ? "📋 Por realizar" : "✅ Finalizado"}
                        </span>
                        {j.hora && (
                          <span style={{ fontFamily:"'DM Sans',sans-serif",
                            fontSize:"11px", color:"#64748B", fontWeight:"600" }}>
                            🕐 {j.hora}
                          </span>
                        )}
                      </div>

                      {/* Descripción del problema */}
                      <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"700",
                        fontSize:"13px", color:"#0F172A", marginBottom:"8px", lineHeight:"1.5" }}>
                        "{j.descripcion}"
                      </div>

                      {/* Datos del cliente */}
                      <div style={{ display:"flex", flexDirection:"column", gap:"4px" }}>
                        {j.cliente && (
                          <div style={{ fontFamily:"'DM Sans',sans-serif",
                            fontSize:"12px", color:"#475569" }}>
                            👤 <strong>{j.cliente}</strong>
                          </div>
                        )}
                        {j.localidad && (
                          <div style={{ fontFamily:"'DM Sans',sans-serif",
                            fontSize:"12px", color:"#475569" }}>
                            📍 {j.localidad}
                          </div>
                        )}
                        {j.direccion && (
                          <div style={{ fontFamily:"'DM Sans',sans-serif",
                            fontSize:"12px", color:"#475569" }}>
                            🏠 {j.direccion}
                          </div>
                        )}
                        {!j.direccion && esActivo && (
                          <div style={{ fontFamily:"'DM Sans',sans-serif",
                            fontSize:"11px", color:"#94A3B8", fontStyle:"italic" }}>
                            La dirección se muestra en la pantalla En curso
                          </div>
                        )}
                      </div>

                      {/* Badge especialidad */}
                      {j.etiqueta && (
                        <div style={{ marginTop:"8px" }}>
                          <Badge label={j.etiqueta}/>
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── SCREEN: HISTORIAL ────────────────────────────────────────────────────────
function ScreenHistorial({ historial, loading, puntuacionPerfil, totalTrabajosPerfil, fechaRegistroPerfil }) {
  const [ratingCli,  setRatingCli]  = useState({});
  const [valoradoCli, setValoradoCli] = useState({});
  const [loadingCli, setLoadingCli] = useState({});
  const [openYear,  setOpenYear]  = useState(null);
  const [openMonth, setOpenMonth] = useState(null); // clave "año-mes"

  const calificarCliente = async (id, stars) => {
    if (!stars) return;
    setRatingCli(p => ({ ...p, [id]: stars }));
    setLoadingCli(p => ({ ...p, [id]: true }));
    try {
      await api.post(`/calificaciones/plomero/${id}`, { estrellas: stars, comentario: null });
      setValoradoCli(p => ({ ...p, [id]: true }));
    } catch {
      // Si ya había calificado antes, igual lo damos por hecho
      setValoradoCli(p => ({ ...p, [id]: true }));
    } finally {
      setLoadingCli(p => ({ ...p, [id]: false }));
    }
  };

  if (loading) return (
    <div style={{ display:"flex", justifyContent:"center", padding:"80px" }}>
      <Spinner size={36} color="#3B82F6"/>
    </div>
  );

  const terminados = historial.filter(h => {
    const e = (h.estado || "").toLowerCase();
    return e === "completada" || e === "completado" || e === "finalizado"
      || e === "pendiente_calificacion";
  });

  // El promedio viene del backend (perfil): ya incluye los 5 puntos base,
  // las calificaciones reales y las penalizaciones. NO se recalcula con las
  // notas por trabajo, para no perder la base ni contar como 0 los trabajos
  // que todavía no fueron calificados.
  const promedio = (puntuacionPerfil != null && !isNaN(puntuacionPerfil))
    ? Number(puntuacionPerfil).toFixed(1)
    : "—";

  const MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
    "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"];

  // Agrupar trabajos: año → mes → semana del mes
  const fechaDe = (t) => new Date(t.fecha_trabajo || t.fecha);
  const grupos = {};
  terminados.forEach(t => {
    const d = fechaDe(t);
    if (isNaN(d.getTime())) return;
    const y = d.getFullYear();
    const m = d.getMonth();
    const semana = Math.ceil(d.getDate() / 7);
    grupos[y] = grupos[y] || {};
    grupos[y][m] = grupos[y][m] || {};
    grupos[y][m][semana] = grupos[y][m][semana] || [];
    grupos[y][m][semana].push(t);
  });
  const anios = Object.keys(grupos).map(Number).sort((a, b) => b - a);
  const contarMes = (y, m) => Object.values(grupos[y][m]).reduce((a, arr) => a + arr.length, 0);

  // Tarjeta de un trabajo (detalle estilo agenda + calificación al cliente)
  const renderJob = (t) => (
    <div key={t.id_solicitud} style={{ background:"#fff", borderRadius:"14px",
      border:"1.5px solid #F1F5F9", padding:"16px 18px", marginBottom:"10px" }}>
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", gap:"8px", marginBottom:"8px" }}>
        <Badge label={t.etiqueta_ia || "PLOMERIA_GENERAL"}/>
        <span style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px", color:"#94A3B8" }}>
          {(() => { const d = fechaDe(t); return isNaN(d.getTime()) ? "" : d.toLocaleDateString("es-AR"); })()}
        </span>
      </div>
      <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"13px",
        color:"#0F172A", fontWeight:"700", marginBottom:"6px" }}>{t.diagnostico_ia || `"${t.descripcion_raw}"`}</div>
      {t.nombre_cliente && (
        <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px", color:"#475569" }}>
          👤 {t.nombre_cliente}
        </div>
      )}
      {t.localidad_evento && (
        <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px", color:"#475569" }}>
          📍 {t.localidad_evento}
        </div>
      )}
      {t.calificacion > 0 && (
        <div style={{ display:"flex", alignItems:"center", gap:"8px", marginTop:"8px" }}>
          <Stars val={t.calificacion} size={14}/>
          <span style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"700",
            fontSize:"13px", color:"#92400E" }}>{t.calificacion}</span>
        </div>
      )}

      {(t.estado || "").toLowerCase() === "pendiente_calificacion" && (
        (valoradoCli[t.id_solicitud] || t.plomero_califico) ? (
          <div style={{ marginTop:"12px", background:"#F0FDF4", border:"1px solid #86EFAC",
            borderRadius:"10px", padding:"10px 14px", fontFamily:"'DM Sans',sans-serif",
            fontSize:"13px", color:"#15803D", fontWeight:"600" }}>
            ✓ Calificaste a {t.nombre_cliente || "el cliente"}
          </div>
        ) : (
          <div style={{ marginTop:"12px", borderTop:"1px solid #F1F5F9", paddingTop:"12px" }}>
            <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
              fontWeight:"700", color:"#64748B", marginBottom:"8px" }}>
              ¿Cómo fue el cliente {t.nombre_cliente ? `(${t.nombre_cliente})` : ""}?
            </div>
            <div style={{ display:"flex", gap:"6px", alignItems:"center" }}>
              {[1,2,3,4,5].map(i => (
                <button key={i}
                  onClick={() => setRatingCli(p => ({ ...p, [t.id_solicitud]: i }))}
                  disabled={!!loadingCli[t.id_solicitud]}
                  style={{ width:"34px", height:"34px", borderRadius:"8px",
                    border: (ratingCli[t.id_solicitud] || 0) >= i ? "2px solid #F59E0B" : "2px solid #E2E8F0",
                    background: (ratingCli[t.id_solicitud] || 0) >= i ? "#FFFBEB" : "#F8FAFC",
                    fontSize:"16px", cursor:"pointer", display:"flex",
                    alignItems:"center", justifyContent:"center" }}>⭐</button>
              ))}
              <button
                onClick={() => calificarCliente(t.id_solicitud, ratingCli[t.id_solicitud])}
                disabled={!ratingCli[t.id_solicitud] || !!loadingCli[t.id_solicitud]}
                style={{ marginLeft:"8px",
                  background: ratingCli[t.id_solicitud] ? "linear-gradient(135deg,#F59E0B,#D97706)" : "#E2E8F0",
                  color: ratingCli[t.id_solicitud] ? "#fff" : "#94A3B8",
                  border:"none", borderRadius:"9px", padding:"8px 14px",
                  fontFamily:"'DM Sans',sans-serif", fontWeight:"700", fontSize:"12px",
                  cursor: ratingCli[t.id_solicitud] ? "pointer" : "not-allowed",
                  display:"flex", alignItems:"center", gap:"6px" }}>
                {loadingCli[t.id_solicitud] ? <Spinner size={13}/> : null}
                Enviar
              </button>
            </div>
          </div>
        )
      )}
    </div>
  );

  // ── Finanzas / historial: TODO se calcula con los trabajos REALES (terminados),
  //    así los stats de arriba, la facturación por mes y el listado detallado
  //    SIEMPRE coinciden. La plata es estimada (cada trabajo = su boleta, o el
  //    ticket promedio si no tiene). ──
  const COMISION = 0.15;
  const TICKET = 25000;
  const META_MENSUAL = 500000;
  const ahora = new Date();
  const trabajos = terminados.length || totalTrabajosPerfil || 0;

  const alta = fechaRegistroPerfil ? new Date(fechaRegistroPerfil) : null;
  const altaValida = alta && !isNaN(alta.getTime());

  const porMes = {};
  const addMes = (d, monto, count) => {
    if (isNaN(d.getTime())) return;
    const k = `${d.getFullYear()}-${String(d.getMonth()).padStart(2, "0")}`;
    porMes[k] = porMes[k] || { count: 0, total: 0, y: d.getFullYear(), m: d.getMonth() };
    porMes[k].total += monto; porMes[k].count += count;
  };
  terminados.forEach(t => addMes(new Date(t.fecha_trabajo || t.fecha), (t.total_boleta || TICKET), 1));

  const filas = Object.values(porMes).sort((a, b) => (b.y - a.y) || (b.m - a.m)).slice(0, 6).reverse();
  const maxTotal = Math.max(1, ...filas.map(f => f.total));
  const kMes = `${ahora.getFullYear()}-${String(ahora.getMonth()).padStart(2, "0")}`;
  const pasado = new Date(ahora.getFullYear(), ahora.getMonth() - 1, 1);
  const kPasado = `${pasado.getFullYear()}-${String(pasado.getMonth()).padStart(2, "0")}`;
  const realMes = porMes[kMes]?.total || 0;
  const realPasado = porMes[kPasado]?.total || 0;
  const variacion = realPasado > 0 ? Math.round((realMes - realPasado) / realPasado * 100) : null;
  const realTotal = terminados.reduce((a, t) => a + (t.total_boleta || TICKET), 0);
  const brutoAcumulado = realTotal;
  const MESES_ES = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"];
  const miembroDesde = altaValida ? `${MESES_ES[alta.getMonth()]} ${alta.getFullYear()}` : null;
  const comision = brutoAcumulado * COMISION;
  const neto = brutoAcumulado - comision;
  const badge = trabajos >= 100 ? { t: "Plomero Pro", e: "🏆" }
    : trabajos >= 50 ? { t: "Destacado", e: "⭐" }
    : trabajos >= 10 ? { t: "En camino", e: "🚀" } : { t: "Nuevo", e: "🌱" };
  const progreso = Math.min(100, Math.round(realMes / META_MENSUAL * 100));
  const $ = (n) => "$" + Number(Math.round(n)).toLocaleString("es-AR");
  const trabajosEsteMes = porMes[kMes]?.count || 0;

  return (
    <div style={{ maxWidth:"640px", margin:"0 auto", padding:"28px 24px" }}>
      <h1 style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800", fontSize:"22px",
        color:"#0F172A", margin:"0 0 6px" }}>Historial de trabajos</h1>
      <p style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"14px",
        color:"#64748B", margin:"0 0 20px" }}>{trabajos} trabajos finalizados</p>

      <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:"12px", marginBottom:"24px" }}>
        {[
          { label:"Trabajos",  value:trabajos, color:"#3B82F6" },
          { label:"Promedio",  value:`⭐ ${promedio}`,  color:"#F59E0B" },
          { label:"Este mes",  value:trabajosEsteMes, color:"#22C55E" },
        ].map(s => (
          <div key={s.label} style={{ background:"#fff", borderRadius:"14px",
            border:"1.5px solid #F1F5F9", padding:"16px", textAlign:"center" }}>
            <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
              fontSize:"22px", color:s.color, marginBottom:"4px" }}>{s.value}</div>
            <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px", color:"#94A3B8" }}>{s.label}</div>
          </div>
        ))}
      </div>

      {(() => {
        return (
          <>
            {/* Tarjeta destacada de ganancias */}
            <div style={{ background:"linear-gradient(135deg,#0F172A,#1E3A5F)", borderRadius:"18px",
              padding:"20px 22px", marginBottom:"14px", color:"#fff",
              boxShadow:"0 8px 24px rgba(15,23,42,0.25)" }}>
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center" }}>
                <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px", color:"#94A3B8", fontWeight:"600" }}>
                  💰 Ganancia acumulada (estimada)
                </div>
                <div style={{ background:"rgba(56,189,248,0.15)", border:"1px solid rgba(56,189,248,0.3)",
                  borderRadius:"20px", padding:"3px 10px", fontFamily:"'DM Sans',sans-serif",
                  fontSize:"11px", fontWeight:"700", color:"#7DD3FC" }}>{badge.e} {badge.t}</div>
              </div>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800", fontSize:"30px",
                margin:"6px 0 2px" }}>{$(neto)}</div>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px", color:"#CBD5E1" }}>
                Facturado {$(brutoAcumulado)} · Comisión PlomerIA (15%): -{$(comision)}
              </div>
              {miembroDesde && (
                <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"11px", color:"#7DD3FC", marginTop:"6px" }}>
                  📅 Miembro desde {miembroDesde}
                </div>
              )}
            </div>

            {/* Meta del mes (motivación) */}
            <div style={{ background:"#fff", borderRadius:"16px", border:"1.5px solid #F1F5F9",
              padding:"16px 18px", marginBottom:"14px" }}>
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"8px" }}>
                <span style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800", fontSize:"14px", color:"#0F172A" }}>
                  🎯 Meta de este mes
                </span>
                {variacion !== null && (
                  <span style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px", fontWeight:"700",
                    color: variacion >= 0 ? "#16A34A" : "#EF4444" }}>
                    {variacion >= 0 ? "▲" : "▼"} {Math.abs(variacion)}% vs mes pasado
                  </span>
                )}
              </div>
              <div style={{ display:"flex", justifyContent:"space-between", fontFamily:"'DM Sans',sans-serif",
                fontSize:"12px", color:"#475569", marginBottom:"4px" }}>
                <span style={{ fontWeight:"700" }}>{$(realMes)}</span>
                <span style={{ color:"#94A3B8" }}>Meta {$(META_MENSUAL)}</span>
              </div>
              <div style={{ background:"#F1F5F9", borderRadius:"8px", height:"12px", overflow:"hidden" }}>
                <div style={{ width:`${progreso}%`, height:"100%",
                  background: progreso >= 100 ? "linear-gradient(90deg,#22C55E,#16A34A)" : "linear-gradient(90deg,#F59E0B,#FB923C)" }} />
              </div>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"11px", color:"#94A3B8", marginTop:"6px" }}>
                {progreso >= 100 ? "¡Meta alcanzada! 🎉" : `Te falta ${$(Math.max(0, META_MENSUAL - realMes))} para tu meta`}
              </div>
            </div>

            {/* Facturación real por mes */}
            {filas.length > 0 && (
              <div style={{ background:"#fff", borderRadius:"16px", border:"1.5px solid #F1F5F9",
                padding:"18px 20px", marginBottom:"20px" }}>
                <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800", fontSize:"15px",
                  color:"#0F172A", marginBottom:"2px" }}>📊 Facturación por mes</div>
                <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px", color:"#94A3B8",
                  marginBottom:"14px" }}>Boletas emitidas en la app</div>
                {filas.map(f => (
                  <div key={`${f.y}-${f.m}`} style={{ marginBottom:"10px" }}>
                    <div style={{ display:"flex", justifyContent:"space-between",
                      fontFamily:"'DM Sans',sans-serif", fontSize:"12px", marginBottom:"3px" }}>
                      <span style={{ color:"#475569", fontWeight:"600" }}>
                        {MESES[f.m]} {f.y} · {f.count} trabajo{f.count !== 1 ? "s" : ""}
                      </span>
                      <span style={{ color:"#16A34A", fontWeight:"700" }}>
                        ${Number(f.total).toLocaleString("es-AR")}
                      </span>
                    </div>
                    <div style={{ background:"#F1F5F9", borderRadius:"6px", height:"8px", overflow:"hidden" }}>
                      <div style={{ width:`${Math.round(f.total / maxTotal * 100)}%`, height:"100%",
                        background:"linear-gradient(90deg,#3B82F6,#06B6D4)" }} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        );
      })()}

      {terminados.length === 0 ? (
        <div style={{ textAlign:"center", padding:"60px 20px",
          border:"2px dashed #E2E8F0", borderRadius:"16px" }}>
          <div style={{ fontSize:"36px", marginBottom:"12px" }}>📋</div>
          <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"700",
            fontSize:"15px", color:"#94A3B8" }}>Todavía no tenés trabajos finalizados.</div>
        </div>
      ) : anios.map(y => {
        const meses = Object.keys(grupos[y]).map(Number).sort((a, b) => b - a);
        const totalAnio = meses.reduce((a, m) => a + contarMes(y, m), 0);
        const yearOpen = openYear === y;
        return (
          <div key={y} style={{ marginBottom:"12px" }}>
            <button onClick={() => { setOpenYear(yearOpen ? null : y); setOpenMonth(null); }}
              style={{ width:"100%", display:"flex", justifyContent:"space-between", alignItems:"center",
                background:"#0F172A", color:"#fff", border:"none", borderRadius:"12px",
                padding:"12px 16px", cursor:"pointer", fontFamily:"'DM Sans',sans-serif",
                fontWeight:"800", fontSize:"15px" }}>
              <span>{yearOpen ? "▾" : "▸"} {y}</span>
              <span style={{ fontSize:"12px", fontWeight:"600", color:"#94A3B8" }}>
                {totalAnio} trabajo{totalAnio !== 1 ? "s" : ""}
              </span>
            </button>

            {yearOpen && meses.map(m => {
              const mKey = `${y}-${m}`;
              const monthOpen = openMonth === mKey;
              const totalMes = contarMes(y, m);
              const semanas = Object.keys(grupos[y][m]).map(Number).sort((a, b) => a - b);
              return (
                <div key={mKey} style={{ margin:"8px 0 0 8px" }}>
                  <button onClick={() => setOpenMonth(monthOpen ? null : mKey)}
                    style={{ width:"100%", display:"flex", justifyContent:"space-between", alignItems:"center",
                      background:"#EFF6FF", color:"#1D4ED8", border:"1px solid #BFDBFE", borderRadius:"10px",
                      padding:"10px 14px", cursor:"pointer", fontFamily:"'DM Sans',sans-serif",
                      fontWeight:"700", fontSize:"14px" }}>
                    <span>{monthOpen ? "▾" : "▸"} {MESES[m]}</span>
                    <span style={{ fontSize:"12px", fontWeight:"600", color:"#64748B" }}>
                      {totalMes} trabajo{totalMes !== 1 ? "s" : ""}
                    </span>
                  </button>

                  {monthOpen && semanas.map(sem => (
                    <div key={sem} style={{ margin:"8px 0 0 8px" }}>
                      <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
                        fontWeight:"700", color:"#94A3B8", textTransform:"uppercase",
                        letterSpacing:"0.6px", margin:"8px 0 6px" }}>
                        Semana {sem} · {grupos[y][m][sem].length} trabajo{grupos[y][m][sem].length !== 1 ? "s" : ""}
                      </div>
                      {grupos[y][m][sem].map(renderJob)}
                    </div>
                  ))}
                </div>
              );
            })}
          </div>
        );
      })}
    </div>
  );
}

// ─── HOME PLOMERO PRINCIPAL ───────────────────────────────────────────────────
// --- SCREEN: NOTIFICACIONES (plomero) ---
function ScreenNotificaciones({ notifs, onMark, onClear }) {
  return (
    <div style={{ maxWidth:"640px", margin:"0 auto", padding:"32px 20px" }}>
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"20px" }}>
        <h1 style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800", fontSize:"22px", color:"#0F172A", margin:0 }}>Notificaciones</h1>
        <div style={{ display:"flex", gap:"14px", alignItems:"center" }}>
          {notifs.some(n => !n.leida) && (
            <button onClick={onMark} style={{ background:"transparent", border:"none", fontFamily:"'DM Sans',sans-serif", fontWeight:"600", fontSize:"13px", color:"#3B82F6", cursor:"pointer" }}>Marcar todas como leidas</button>
          )}
          {notifs.length > 0 && (
            <button onClick={onClear} style={{ background:"transparent", border:"none", fontFamily:"'DM Sans',sans-serif", fontWeight:"600", fontSize:"13px", color:"#EF4444", cursor:"pointer" }}>Borrar todas</button>
          )}
        </div>
      </div>
      {notifs.length === 0 ? (
        <div style={{ textAlign:"center", padding:"60px 20px", color:"#94A3B8", fontFamily:"'DM Sans',sans-serif" }}>
          <div style={{ fontSize:"36px", marginBottom:"12px" }}>🔔</div>
          <div style={{ fontWeight:"700", fontSize:"15px" }}>Sin notificaciones</div>
        </div>
      ) : notifs.map(n => (
        <div key={n.id} style={{ background:n.leida?"#fff":"#EFF6FF", border:n.leida?"1.5px solid #F1F5F9":"1.5px solid #BFDBFE", borderRadius:"14px", padding:"16px 18px", marginBottom:"10px", display:"flex", gap:"14px", alignItems:"flex-start" }}>
          <div style={{ fontSize:"22px", flexShrink:0, width:"40px", height:"40px", borderRadius:"12px", background:n.leida?"#F8FAFC":"#DBEAFE", display:"flex", alignItems:"center", justifyContent:"center" }}>{n.icon}</div>
          <div style={{ flex:1 }}>
            <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"700", fontSize:"14px", color:"#0F172A", marginBottom:"3px" }}>{n.titulo}</div>
            <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"13px", color:"#64748B", lineHeight:"1.4" }}>{n.mensaje}</div>
            <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"11px", color:"#CBD5E1", marginTop:"6px" }}>{n.tiempo}</div>
          </div>
          {!n.leida && <div style={{ width:"8px", height:"8px", borderRadius:"50%", background:"#3B82F6", flexShrink:0, marginTop:"6px" }} />}
        </div>
      ))}
    </div>
  );
}

export default function HomePlomero({ onLogout }) {
  const user   = useAuthStore(s => s.user);
  const logout = useAuthStore(s => s.logout);

  const [screen,      setScreen]     = useState("solicitudes");
  const [disponible,  setDisponible] = useState(true);
  const [solicitudes, setSolicitudes]= useState([]);
  const [activos,     setActivos]    = useState([]);
  const [historial,   setHistorial]  = useState([]);
  const [loading,     setLoading]    = useState(false);
  const [perfil,      setPerfil]     = useState(null);

  const token = useAuthStore(s => s.token);
  const [notifs, marcarTodasNotifs, eliminarTodasNotifs] = useNotificaciones(token);
  const notifCount = notifs.filter(n => !n.leida).length;

  useEffect(() => {
    let primera = true;
    const cargarPerfil = () => api.get("/plomeros/me")
      .then(res => {
        setPerfil(prev => JSON.stringify(prev) === JSON.stringify(res.data) ? prev : res.data);
        // El estado del toggle solo se setea la primera vez, para no pisar
        // un cambio manual del plomero en cada refresco.
        if (primera) { setDisponible(res.data?.disponible_ahora ?? true); primera = false; }
      })
      .catch(() => {});
    cargarPerfil();
    const id = setInterval(cargarPerfil, 15000); // refresca puntuación
    return () => clearInterval(id);
  }, []);

  // silencioso=true (polling): no toca loading ni reemplaza el estado si no
  // cambió, para no re-renderizar ni sacarte el foco mientras cargás la boleta.
  const cargarSolicitudes = useCallback(async (silencioso = false) => {
    if (!silencioso) setLoading(true);
    const aplicar = (setter, arr) =>
      setter(prev => JSON.stringify(prev) === JSON.stringify(arr) ? prev : arr);
    try {
      const res  = await api.get("/solicitudes/plomero/me");
      const todas = Array.isArray(res.data) ? res.data : [];

      aplicar(setSolicitudes, todas.filter(s => (s.estado || "").toLowerCase() === "pendiente"));
      aplicar(setActivos, todas.filter(s => {
        const e = (s.estado || "").toLowerCase();
        return e === "en_progreso" || e === "en_camino";
      }));
      aplicar(setHistorial, todas.filter(s => {
        const e = (s.estado || "").toLowerCase();
        return e === "completada" || e === "completado" || e === "finalizado"
          || e === "pendiente_calificacion";
      }));
    } catch (e) {
      console.error("Error cargando solicitudes:", e);
    } finally {
      if (!silencioso) setLoading(false);
    }
  }, []);

  useEffect(() => { cargarSolicitudes(); }, [cargarSolicitudes]);
  useEffect(() => {
    const interval = setInterval(() => cargarSolicitudes(true), 15000);
    return () => clearInterval(interval);
  }, [cargarSolicitudes]);

  const handleToggleDisp = async () => {
    const nuevo = !disponible;
    setDisponible(nuevo);
    try {
      await api.patch("/plomeros/disponibilidad", null, { params: { disponible: nuevo } });
    } catch {
      setDisponible(!nuevo);
    }
  };

  const handleAceptar = async (idSolicitud) => {
    try {
      await api.patch(`/solicitudes/${idSolicitud}/aceptar`);
      await cargarSolicitudes();
      setScreen("activos");
    } catch (e) { console.error("Error aceptando:", e); }
  };

  const handleRechazar = async (idSolicitud) => {
    try {
      await api.patch(`/solicitudes/${idSolicitud}/rechazar`);
      await cargarSolicitudes();
    } catch (e) { console.error("Error rechazando:", e); }
  };

  const handleEnCamino = async (idSolicitud) => {
    try {
      await api.patch(`/solicitudes/${idSolicitud}/en_camino`);
      await cargarSolicitudes();
    } catch (e) { console.error("Error marcando en camino:", e); }
  };

  const handleCompletar = async (idSolicitud) => {
    try {
      await api.patch(`/solicitudes/${idSolicitud}/completar`);
      await cargarSolicitudes();
      setScreen("historial");
    } catch (e) { console.error("Error completando:", e); }
  };

  const handleCancelar = async (idSolicitud) => {
    try {
      await api.patch(`/solicitudes/${idSolicitud}/cancelar_plomero`);
      await cargarSolicitudes();
    } catch (e) { console.error("Error cancelando:", e); }
  };

  const handleReprogramar = async (idSolicitud, fechaISO) => {
    if (!fechaISO) return;
    try {
      await api.patch(`/solicitudes/${idSolicitud}/reprogramar`, { fecha_trabajo: fechaISO });
      await cargarSolicitudes();
    } catch (e) { console.error("Error reprogramando:", e); }
  };

  const handleLogout = () => { logout(); onLogout(); };

  const conversacionesActivas = activos.map(a => ({
    id_solicitud: a.id_solicitud,
    titulo:       a.nombre_cliente || "Cliente",
    subtitulo:    a.localidad_evento || a.etiqueta_ia || "Trabajo en curso",
  }));

  return (
    <div style={{ minHeight:"100vh",
      background:"linear-gradient(160deg,#F0F9FF 0%,#F8FAFC 50%,#F0FDF4 100%)" }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
      <style>{`@keyframes _sp{to{transform:rotate(360deg)}}`}</style>

      <Header
        screen={screen} onNav={setScreen}
        disponible={disponible} onToggleDisp={handleToggleDisp}
        pendientes={solicitudes.length} notifCount={notifCount} user={user} onLogout={handleLogout}
      />

      {screen==="solicitudes" && (
        <ScreenSolicitudes
          solicitudes={solicitudes} onAceptar={handleAceptar}
          onRechazar={handleRechazar} disponible={disponible} loading={loading}
        />
      )}
      {screen==="activos" && (
        <ScreenActivos
          activos={activos} onEnCamino={handleEnCamino}
          onCompletar={handleCompletar} onCancelar={handleCancelar}
          onReprogramar={handleReprogramar} loading={loading}
        />
      )}
      {screen==="agenda" && <ScreenAgenda activos={activos} historial={historial}/>}
      {screen==="historial" && (
        <ScreenHistorial historial={historial} loading={loading}
          puntuacionPerfil={perfil?.puntuacion} totalTrabajosPerfil={perfil?.total_trabajos}
          fechaRegistroPerfil={perfil?.fecha_registro}/>
      )}
      {screen==="alertas" && (
        <ScreenNotificaciones notifs={notifs} onMark={marcarTodasNotifs} onClear={eliminarTodasNotifs} />
      )}

      {/* Chat flotante - visible siempre, activo solo con trabajos en curso */}
      <ChatWidget conversaciones={conversacionesActivas} />
    </div>
  );
}