import { useState, useEffect, useRef, useCallback } from "react";
import api from "../services/api";
import { useAuthStore } from "../store/authStore";

// Deriva la base del WebSocket a partir de la baseURL del cliente HTTP.
// http://localhost:8000/api  ->  ws://localhost:8000
function wsBase() {
  const base = api?.defaults?.baseURL || "http://localhost:8000/api";
  return base.replace(/^http/i, "ws").replace(/\/api\/?$/i, "");
}

function Avatar({ nombre, size = 38 }) {
  const inicial = (nombre || "?").trim().charAt(0).toUpperCase();
  return (
    <div style={{
      width: size, height: size, borderRadius: "50%", flexShrink: 0,
      background: "linear-gradient(135deg,#3B82F6,#06B6D4)", color: "#fff",
      display: "flex", alignItems: "center", justifyContent: "center",
      fontWeight: 800, fontSize: size * 0.42, fontFamily: "'DM Sans',sans-serif",
    }}>{inicial}</div>
  );
}

/**
 * ChatWidget — burbuja de chat flotante, visible siempre.
 * Solo se "activa" si hay conversaciones (solicitudes en curso).
 *
 * props:
 *   conversaciones: [{ id_solicitud, titulo, subtitulo }]
 */
export default function ChatWidget({ conversaciones = [] }) {
  const token = useAuthStore(s => s.token);
  const user  = useAuthStore(s => s.user);
  const miId  = user?.id;
  const miRol = user?.rol; // "usuario" | "plomero"

  const [abierto, setAbierto]   = useState(false);
  const [activa, setActiva]     = useState(null);   // id_solicitud seleccionado
  const [mensajes, setMensajes] = useState([]);
  const [texto, setTexto]       = useState("");
  const [conectado, setConect]  = useState(false);

  const wsRef     = useRef(null);
  const scrollRef = useRef(null);
  const hayActivas = conversaciones.length > 0;

  // Si solo hay una conversación, la auto-selecciona al abrir
  useEffect(() => {
    if (abierto && !activa && conversaciones.length === 1) {
      setActiva(conversaciones[0].id_solicitud);
    }
  }, [abierto, activa, conversaciones]);

  // Permite abrir el chat desde otros lados (ej. botón "coordinar para reprogramar")
  useEffect(() => {
    const handler = (e) => {
      setAbierto(true);
      const id = e.detail?.idSolicitud;
      if (id) setActiva(id);
    };
    window.addEventListener("plomeria:abrir-chat", handler);
    return () => window.removeEventListener("plomeria:abrir-chat", handler);
  }, []);

  // Si la conversación activa deja de existir (trabajo terminó/canceló), salir
  useEffect(() => {
    if (activa && !conversaciones.some(c => c.id_solicitud === activa)) {
      setActiva(null);
    }
  }, [conversaciones, activa]);

  const scrollAbajo = useCallback(() => {
    requestAnimationFrame(() => {
      if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    });
  }, []);

  // Cargar historial + abrir WebSocket + polling de respaldo
  useEffect(() => {
    if (!activa || !token) return;
    let cancelado = false;

    // Trae el historial y lo fusiona por id (sirve como respaldo si el WS falla)
    const cargarHistorial = async () => {
      try {
        const res = await api.get(`/mensajes/${activa}`);
        const arr = Array.isArray(res.data) ? res.data : [];
        if (cancelado) return;
        setMensajes(prev => {
          const map = new Map();
          [...prev, ...arr].forEach(m => {
            const k = (m && m.id_mensaje != null) ? "id" + m.id_mensaje : "tmp" + Math.random();
            map.set(k, m);
          });
          return Array.from(map.values()).sort(
            (a, b) => new Date(a.fecha || 0) - new Date(b.fecha || 0)
          );
        });
        scrollAbajo();
      } catch { /* noop */ }
    };

    setMensajes([]);
    cargarHistorial();
    const pollId = setInterval(cargarHistorial, 4000); // respaldo: refresca cada 4s

    const url = `${wsBase()}/ws/chat/${activa}?token=${token}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen    = () => setConect(true);
    ws.onclose   = () => setConect(false);
    ws.onerror   = () => setConect(false);
    ws.onmessage = (ev) => {
      try {
        const m = JSON.parse(ev.data);
        setMensajes(prev => {
          if (m.id_mensaje && prev.some(x => x.id_mensaje === m.id_mensaje)) return prev;
          return [...prev, m];
        });
        scrollAbajo();
      } catch { /* noop */ }
    };

    return () => {
      cancelado = true;
      clearInterval(pollId);
      try { ws.close(); } catch { /* noop */ }
      wsRef.current = null;
    };
  }, [activa, token, scrollAbajo]);

  const enviar = () => {
    const t = texto.trim();
    if (!t) return;
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ texto: t }));
      setTexto("");
    } else {
      // Fallback REST si el socket no está listo
      api.post("/mensajes/", { id_solicitud: activa, texto: t })
        .then(res => { setMensajes(prev => [...prev, res.data]); setTexto(""); scrollAbajo(); })
        .catch(() => {});
    }
  };

  const convActiva = conversaciones.find(c => c.id_solicitud === activa);

  return (
    <>
      {/* Botón flotante */}
      <button
        onClick={() => setAbierto(o => !o)}
        title={hayActivas ? "Mensajes" : "No tenés conversaciones activas"}
        style={{
          position: "fixed", bottom: 24, right: 24, zIndex: 1000,
          width: 58, height: 58, borderRadius: "50%", border: "none",
          cursor: "pointer", fontSize: 24,
          background: hayActivas ? "linear-gradient(135deg,#3B82F6,#06B6D4)" : "#94A3B8",
          color: "#fff", boxShadow: "0 8px 24px rgba(15,23,42,0.28)",
          display: "flex", alignItems: "center", justifyContent: "center",
        }}
      >
        💬
        {hayActivas && (
          <span style={{
            position: "absolute", top: 2, right: 2, background: "#22C55E",
            width: 14, height: 14, borderRadius: "50%", border: "2px solid #fff",
          }} />
        )}
      </button>

      {/* Panel */}
      {abierto && (
        <div style={{
          position: "fixed", bottom: 92, right: 24, zIndex: 1000,
          width: 340, height: 460, background: "#fff", borderRadius: 18,
          boxShadow: "0 16px 48px rgba(15,23,42,0.28)", overflow: "hidden",
          display: "flex", flexDirection: "column", fontFamily: "'DM Sans',sans-serif",
          border: "1px solid #E2E8F0",
        }}>
          {/* Header del panel */}
          <div style={{
            background: "linear-gradient(135deg,#0F172A,#1E3A5F)", color: "#fff",
            padding: "14px 16px", display: "flex", alignItems: "center", gap: 10,
          }}>
            {activa && (
              <button onClick={() => setActiva(null)} style={{
                background: "transparent", border: "none", color: "#fff",
                cursor: "pointer", fontSize: 18, padding: 0, lineHeight: 1,
              }}>‹</button>
            )}
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontWeight: 800, fontSize: 15 }}>
                {activa ? (convActiva?.titulo || "Chat") : "Mensajes"}
              </div>
              <div style={{ fontSize: 11, color: "#94A3B8" }}>
                {activa
                  ? (conectado ? "En línea" : "Conectando…")
                  : (hayActivas ? `${conversaciones.length} conversación(es) activa(s)` : "Sin conversaciones")}
              </div>
            </div>
            <button onClick={() => setAbierto(false)} style={{
              background: "transparent", border: "none", color: "#fff",
              cursor: "pointer", fontSize: 18, padding: 0, lineHeight: 1,
            }}>✕</button>
          </div>

          {/* Cuerpo */}
          {!hayActivas ? (
            <div style={{
              flex: 1, display: "flex", flexDirection: "column",
              alignItems: "center", justifyContent: "center",
              color: "#94A3B8", textAlign: "center", padding: 24,
            }}>
              <div style={{ fontSize: 34, marginBottom: 10 }}>💬</div>
              <div style={{ fontWeight: 700, fontSize: 14, color: "#64748B" }}>
                No tenés conversaciones activas
              </div>
              <div style={{ fontSize: 12, marginTop: 6 }}>
                El chat se habilita cuando hay un trabajo en curso.
              </div>
            </div>
          ) : !activa ? (
            /* Lista de conversaciones */
            <div style={{ flex: 1, overflowY: "auto", padding: 8 }}>
              {conversaciones.map(c => (
                <div key={c.id_solicitud} onClick={() => setActiva(c.id_solicitud)}
                  style={{
                    display: "flex", alignItems: "center", gap: 12, padding: "10px 12px",
                    borderRadius: 12, cursor: "pointer",
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = "#F1F5F9"}
                  onMouseLeave={e => e.currentTarget.style.background = "transparent"}
                >
                  <Avatar nombre={c.titulo} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 700, fontSize: 14, color: "#0F172A" }}>
                      {c.titulo || "Contacto"}
                    </div>
                    <div style={{ fontSize: 12, color: "#94A3B8", whiteSpace: "nowrap",
                      overflow: "hidden", textOverflow: "ellipsis" }}>
                      {c.subtitulo || "Trabajo en curso"}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            /* Vista de chat */
            <>
              <div ref={scrollRef} style={{
                flex: 1, overflowY: "auto", padding: 14,
                background: "#F8FAFC", display: "flex", flexDirection: "column", gap: 8,
              }}>
                {mensajes.length === 0 && (
                  <div style={{ textAlign: "center", color: "#CBD5E1", fontSize: 12, marginTop: 20 }}>
                    Todavía no hay mensajes. ¡Escribí el primero!
                  </div>
                )}
                {mensajes.map((m, i) => {
                  const mio = (m.emisor_id === miId) || (m.emisor_rol === miRol);
                  return (
                    <div key={m.id_mensaje || i} style={{
                      alignSelf: mio ? "flex-end" : "flex-start", maxWidth: "78%",
                      background: mio ? "linear-gradient(135deg,#3B82F6,#06B6D4)" : "#fff",
                      color: mio ? "#fff" : "#0F172A",
                      border: mio ? "none" : "1px solid #E2E8F0",
                      borderRadius: 14, padding: "8px 12px", fontSize: 13, lineHeight: 1.35,
                      boxShadow: "0 1px 2px rgba(15,23,42,0.06)",
                    }}>
                      {m.texto}
                    </div>
                  );
                })}
              </div>
              <div style={{ display: "flex", gap: 8, padding: 10, borderTop: "1px solid #E2E8F0" }}>
                <input
                  value={texto}
                  onChange={e => setTexto(e.target.value)}
                  onKeyDown={e => { if (e.key === "Enter") enviar(); }}
                  placeholder="Escribí un mensaje…"
                  style={{
                    flex: 1, border: "1.5px solid #E2E8F0", borderRadius: 12,
                    padding: "10px 12px", fontSize: 13, outline: "none",
                    fontFamily: "'DM Sans',sans-serif",
                  }}
                />
                <button onClick={enviar} style={{
                  background: "linear-gradient(135deg,#3B82F6,#06B6D4)", color: "#fff",
                  border: "none", borderRadius: 12, padding: "0 16px", cursor: "pointer",
                  fontWeight: 800, fontSize: 15,
                }}>➤</button>
              </div>
            </>
          )}
        </div>
      )}
    </>
  );
}
