import { useState, useEffect, useCallback } from "react";
import api from "../services/api";
import { useAuthStore } from "../store/authStore";

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

function ScreenActivos({ activos, onEnCamino, onCompletar, onCancelar, loading }) {
  const [loadingId,  setLoadingId]  = useState(null);
  const [cancelando, setCancelando] = useState(null);

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
                  ["Localidad",      t.localidad_evento || "—"],
                  ["Turno pedido",   t.turno_solicitado ? formatearTurno(t.turno_solicitado) : "A confirmar"],
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

            {/* Botones de acción según estado */}
            {esEnProgreso && (() => {
              const esDiaDelTurno = (() => {
                if (!t.turno_solicitado) return true;
                try {
                  const IDX = {"Lun":1,"Mar":2,"Mié":3,"Jue":4,"Vie":5,"Sáb":6,"Dom":0};
                  const dia = t.turno_solicitado.split("_")[0];
                  return new Date().getDay() === (IDX[dia] ?? -1);
                } catch { return true; }
              })();
              return (
                <button
                  onClick={async () => {
                    setLoadingId("camino_" + t.id_solicitud);
                    await onEnCamino(t.id_solicitud);
                    setLoadingId(null);
                  }}
                  disabled={!!loadingId || !esDiaDelTurno}
                  title={!esDiaDelTurno ? "Solo podés marcar en camino el día del trabajo" : ""}
                  style={{ width:"100%",
                    background: esDiaDelTurno
                      ? "linear-gradient(135deg,#3B82F6,#2563EB)" : "#E2E8F0",
                    border:"none", borderRadius:"14px", padding:"13px",
                    fontFamily:"'DM Sans',sans-serif", fontWeight:"800", fontSize:"14px",
                    color: esDiaDelTurno ? "#fff" : "#94A3B8",
                    cursor: esDiaDelTurno ? "pointer" : "not-allowed",
                    marginBottom:"10px",
                    boxShadow: esDiaDelTurno ? "0 4px 14px rgba(59,130,246,0.3)" : "none",
                    display:"flex", alignItems:"center", justifyContent:"center", gap:"8px",
                  }}>
                  {loadingId === "camino_" + t.id_solicitud ? <Spinner size={16}/> : null}
                  🚗 {esDiaDelTurno ? "Voy en camino" : "Disponible el día del trabajo"}
                </button>
              );
            })()}

            {esEnCamino && (() => {
              // Habilitar "Terminé" solo 3hs después de marcar en camino
              const keyTs = `en_camino_ts_${t.id_solicitud}`;
              let tsGuardado = null;
              try {
                // Guardar timestamp la primera vez que vemos en_camino
                const stored = sessionStorage.getItem(keyTs);
                if (!stored) {
                  sessionStorage.setItem(keyTs, Date.now().toString());
                  tsGuardado = Date.now();
                } else {
                  tsGuardado = parseInt(stored);
                }
              } catch { tsGuardado = Date.now(); }
              const horasTranscurridas = (Date.now() - tsGuardado) / 1000 / 3600;
              const puedeCompletar = horasTranscurridas >= 3;
              const minutosRestantes = Math.ceil((3 - horasTranscurridas) * 60);
              return (
                <button
                  onClick={async () => {
                    if (!puedeCompletar) return;
                    setLoadingId("completar_" + t.id_solicitud);
                    await onCompletar(t.id_solicitud);
                    setLoadingId(null);
                  }}
                  disabled={!!loadingId || !puedeCompletar}
                  title={!puedeCompletar ? `Disponible en ${minutosRestantes} minutos` : ""}
                  style={{ width:"100%",
                    background: puedeCompletar
                      ? "linear-gradient(135deg,#22C55E,#16A34A)" : "#E2E8F0",
                    border:"none", borderRadius:"14px", padding:"13px",
                    fontFamily:"'DM Sans',sans-serif", fontWeight:"800", fontSize:"14px",
                    color: puedeCompletar ? "#fff" : "#94A3B8",
                    cursor: puedeCompletar ? "pointer" : "not-allowed",
                    marginBottom:"10px",
                    boxShadow: puedeCompletar ? "0 4px 14px rgba(34,197,94,0.3)" : "none",
                    display:"flex", alignItems:"center", justifyContent:"center", gap:"8px",
                  }}>
                  {loadingId === "completar_" + t.id_solicitud ? <Spinner size={16}/> : null}
                  🏁 {puedeCompletar ? "Terminé el trabajo" : `Disponible en ${minutosRestantes} min`}
                </button>
              );
            })()}

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
function ScreenAgenda({ activos }) {
  const hoy = new Date();
  const [year,  setYear]  = useState(hoy.getFullYear());
  const [month, setMonth] = useState(hoy.getMonth());
  const [selected, setSelected] = useState(null);

  const firstDay    = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month+1, 0).getDate();
  const fmt = d => `${year}-${String(month+1).padStart(2,"0")}-${String(d).padStart(2,"0")}`;

  const fechasOcupadas = activos
    .filter(a => a.turno_solicitado || a.fecha)
    .reduce((acc, a) => {
      const fecha = a.turno_solicitado?.split("_")[0]
        || a.fecha?.split("T")[0];
      if (fecha) {
        acc[fecha] = acc[fecha] || [];
        acc[fecha].push({ descripcion: a.descripcion_raw, tipo: a.etiqueta_ia });
      }
      return acc;
    }, {});

  const selectedJobs = selected ? (fechasOcupadas[selected]||[]) : [];

  const prev = () => { if(month===0){setMonth(11);setYear(y=>y-1);}else setMonth(m=>m-1); setSelected(null); };
  const next = () => { if(month===11){setMonth(0);setYear(y=>y+1);}else setMonth(m=>m+1); setSelected(null); };

  return (
    <div style={{ maxWidth:"800px", margin:"0 auto", padding:"28px 24px" }}>
      <h1 style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800", fontSize:"22px",
        color:"#0F172A", margin:"0 0 20px" }}>Mi agenda</h1>

      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"16px", alignItems:"start" }}>
        {/* Calendario */}
        <div style={{ background:"#fff", borderRadius:"16px",
          border:"1.5px solid #F1F5F9", padding:"16px",
          boxShadow:"0 4px 20px rgba(0,0,0,0.06)" }}>

          <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:"14px" }}>
            <button onClick={prev} style={{ background:"#F1F5F9", border:"none", borderRadius:"8px",
              width:"30px", height:"30px", cursor:"pointer", fontSize:"16px", color:"#475569",
              display:"flex", alignItems:"center", justifyContent:"center" }}>‹</button>
            <span style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
              fontSize:"14px", color:"#0F172A" }}>{MONTHS[month]} {year}</span>
            <button onClick={next} style={{ background:"#F1F5F9", border:"none", borderRadius:"8px",
              width:"30px", height:"30px", cursor:"pointer", fontSize:"16px", color:"#475569",
              display:"flex", alignItems:"center", justifyContent:"center" }}>›</button>
          </div>

          <div style={{ display:"grid", gridTemplateColumns:"repeat(7,1fr)", gap:"2px", marginBottom:"6px" }}>
            {DAYS_FULL.map(d => (
              <div key={d} style={{ textAlign:"center", fontSize:"10px", fontWeight:"700",
                color:"#94A3B8", fontFamily:"'DM Sans',sans-serif", padding:"3px 0" }}>{d}</div>
            ))}
          </div>

          <div style={{ display:"grid", gridTemplateColumns:"repeat(7,1fr)", gap:"3px" }}>
            {Array.from({length:firstDay}).map((_,i)=><div key={`e${i}`}/>)}
            {Array.from({length:daysInMonth}).map((_,i)=>{
              const d   = i+1;
              const ds  = fmt(d);
              const isHoy = new Date(year,month,d).toDateString()===hoy.toDateString();
              const tieneJobs = !!fechasOcupadas[ds];
              const isSel = selected===ds;
              return (
                <button key={d} onClick={()=> setSelected(isSel ? null : ds)}
                  style={{
                    border:"none", borderRadius:"8px", padding:"6px 2px",
                    cursor: tieneJobs ? "pointer" : "default",
                    fontFamily:"'DM Sans',sans-serif",
                    fontWeight: isHoy||tieneJobs ? "800" : "400", fontSize:"12px",
                    background: isSel ? "#3B82F6"
                      : tieneJobs ? "#EFF6FF"
                      : isHoy ? "#F0FDF4"
                      : "transparent",
                    color: isSel ? "#fff"
                      : isHoy ? "#16A34A"
                      : tieneJobs ? "#1D4ED8"
                      : "#94A3B8",
                    position:"relative", transition:"all 0.15s",
                  }}>
                  {d}
                  {tieneJobs && !isSel && (
                    <div style={{ position:"absolute", bottom:"2px", left:"50%",
                      transform:"translateX(-50%)", width:"4px", height:"4px",
                      borderRadius:"50%", background:"#3B82F6" }}/>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        {/* Panel detalle */}
        <div style={{ background:"#fff", borderRadius:"16px",
          border:"1.5px solid #F1F5F9", padding:"16px",
          boxShadow:"0 4px 20px rgba(0,0,0,0.06)", minHeight:"200px" }}>
          {!selected ? (
            <div style={{ display:"flex", flexDirection:"column", alignItems:"center",
              justifyContent:"center", height:"100%", minHeight:"180px", textAlign:"center" }}>
              <div style={{ fontSize:"32px", marginBottom:"10px" }}>📅</div>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"700",
                fontSize:"14px", color:"#94A3B8" }}>Seleccioná un día</div>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
                color:"#CBD5E1", lineHeight:"1.5", marginTop:"6px" }}>
                Los días con punto azul tienen trabajos asignados
              </div>
            </div>
          ) : (
            <>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
                fontSize:"15px", color:"#0F172A", marginBottom:"4px" }}>
                {new Date(selected + "T12:00:00").toLocaleDateString("es-AR", {
                  weekday:"long", day:"numeric", month:"long"
                })}
              </div>
              <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
                color:"#94A3B8", marginBottom:"14px" }}>
                {selectedJobs.length > 0
                  ? `${selectedJobs.length} trabajo${selectedJobs.length!==1?"s":""} este día`
                  : "Sin trabajos asignados"}
              </div>
              {selectedJobs.length === 0 ? (
                <div style={{ background:"#F8FAFC", borderRadius:"10px", padding:"16px", textAlign:"center" }}>
                  <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"13px", color:"#94A3B8" }}>
                    Día libre 🎉
                  </div>
                </div>
              ) : selectedJobs.map((j,i) => (
                <div key={i} style={{ background:"#F8FAFC", borderRadius:"10px",
                  padding:"12px", border:"1px solid #E2E8F0", marginBottom:"8px" }}>
                  <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"700",
                    fontSize:"13px", color:"#0F172A", marginBottom:"6px", lineHeight:"1.4" }}>
                    {j.descripcion}
                  </div>
                  <Badge label={j.tipo}/>
                </div>
              ))}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── SCREEN: HISTORIAL ────────────────────────────────────────────────────────
function ScreenHistorial({ historial, loading, puntuacionPerfil }) {
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

  const promedioCalculado = terminados.length > 0
    ? (terminados.reduce((a,t) => a + (t.calificacion || 0), 0) / terminados.length).toFixed(1)
    : null;
  const promedio = promedioCalculado ?? (puntuacionPerfil ? puntuacionPerfil.toFixed(1) : "—");

  return (
    <div style={{ maxWidth:"640px", margin:"0 auto", padding:"28px 24px" }}>
      <h1 style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800", fontSize:"22px",
        color:"#0F172A", margin:"0 0 6px" }}>Historial de trabajos</h1>
      <p style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"14px",
        color:"#64748B", margin:"0 0 20px" }}>{terminados.length} trabajos finalizados</p>

      <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:"12px", marginBottom:"24px" }}>
        {[
          { label:"Trabajos",  value:terminados.length, color:"#3B82F6" },
          { label:"Promedio",  value:`⭐ ${promedio}`,  color:"#F59E0B" },
          { label:"Este mes",  value:terminados.filter(t => {
              const d = new Date(t.fecha); const n = new Date();
              return d.getMonth()===n.getMonth() && d.getFullYear()===n.getFullYear();
            }).length, color:"#22C55E" },
        ].map(s => (
          <div key={s.label} style={{ background:"#fff", borderRadius:"14px",
            border:"1.5px solid #F1F5F9", padding:"16px", textAlign:"center" }}>
            <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"800",
              fontSize:"22px", color:s.color, marginBottom:"4px" }}>{s.value}</div>
            <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px", color:"#94A3B8" }}>{s.label}</div>
          </div>
        ))}
      </div>

      {terminados.length === 0 ? (
        <div style={{ textAlign:"center", padding:"60px 20px",
          border:"2px dashed #E2E8F0", borderRadius:"16px" }}>
          <div style={{ fontSize:"36px", marginBottom:"12px" }}>📋</div>
          <div style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"700",
            fontSize:"15px", color:"#94A3B8" }}>Todavía no tenés trabajos finalizados.</div>
        </div>
      ) : terminados.map(t => (
        <div key={t.id_solicitud} style={{ background:"#fff", borderRadius:"16px",
          border:"1.5px solid #F1F5F9", padding:"18px 20px", marginBottom:"10px" }}>
          <div style={{ display:"flex", alignItems:"center", gap:"8px", marginBottom:"6px" }}>
            <Badge label={t.etiqueta_ia || "PLOMERIA_GENERAL"}/>
          </div>
          <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"12px",
            color:"#94A3B8", marginBottom:"8px" }}>
            {t.fecha ? new Date(t.fecha).toLocaleDateString("es-AR") : ""}
          </div>
          <div style={{ fontFamily:"'DM Sans',sans-serif", fontSize:"13px",
            color:"#475569", fontStyle:"italic" }}>"{t.descripcion_raw}"</div>
          {t.calificacion > 0 && (
            <div style={{ display:"flex", alignItems:"center", gap:"8px", marginTop:"8px" }}>
              <Stars val={t.calificacion} size={14}/>
              <span style={{ fontFamily:"'DM Sans',sans-serif", fontWeight:"700",
                fontSize:"13px", color:"#92400E" }}>{t.calificacion}</span>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// ─── HOME PLOMERO PRINCIPAL ───────────────────────────────────────────────────
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

  useEffect(() => {
    api.get("/plomeros/me")
      .then(res => { setPerfil(res.data); setDisponible(res.data?.disponible_ahora ?? true); })
      .catch(() => {});
  }, []);

  const cargarSolicitudes = useCallback(async () => {
    setLoading(true);
    try {
      const res  = await api.get("/solicitudes/plomero/me");
      const todas = Array.isArray(res.data) ? res.data : [];

      setSolicitudes(todas.filter(s => {
        const e = (s.estado || "").toLowerCase();
        // Pendientes que le llegaron (sugerido) o asignadas a él
        return e === "pendiente";
      }));

      setActivos(todas.filter(s => {
        const e = (s.estado || "").toLowerCase();
        return e === "en_progreso" || e === "en_camino";
      }));

      setHistorial(todas.filter(s => {
        const e = (s.estado || "").toLowerCase();
        return e === "completada" || e === "completado" || e === "finalizado"
          || e === "pendiente_calificacion";
      }));
    } catch (e) {
      console.error("Error cargando solicitudes:", e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { cargarSolicitudes(); }, [cargarSolicitudes]);
  useEffect(() => {
    const interval = setInterval(cargarSolicitudes, 15000);
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

  const handleLogout = () => { logout(); onLogout(); };

  return (
    <div style={{ minHeight:"100vh",
      background:"linear-gradient(160deg,#F0F9FF 0%,#F8FAFC 50%,#F0FDF4 100%)" }}>
      <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
      <style>{`@keyframes _sp{to{transform:rotate(360deg)}}`}</style>

      <Header
        screen={screen} onNav={setScreen}
        disponible={disponible} onToggleDisp={handleToggleDisp}
        pendientes={solicitudes.length} user={user} onLogout={handleLogout}
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
          onCompletar={handleCompletar} onCancelar={handleCancelar} loading={loading}
        />
      )}
      {screen==="agenda" && <ScreenAgenda activos={activos}/>}
      {screen==="historial" && (
        <ScreenHistorial historial={historial} loading={loading} puntuacionPerfil={perfil?.puntuacion}/>
      )}
    </div>
  );
}