import { useState, useEffect, useCallback } from "react";
import api from "../services/api";

// Mapeo tipo de notificación -> ícono mostrado en la pestaña Alertas.
export const ICONOS_NOTIF = {
  nueva_solicitud:    "📩",
  urgencia:           "🚨",
  solicitud_aceptada: "✅",
  en_camino:          "🚗",
  trabajo_finalizado: "🏁",
  cancelada_cliente:  "❌",
  cancelada_plomero:  "⚠️",
  mensaje:            "💬",
};

export function tiempoRelativo(fechaISO) {
  if (!fechaISO) return "";
  const normal = (fechaISO.endsWith("Z") || fechaISO.includes("+")) ? fechaISO : fechaISO + "Z";
  const f = new Date(normal);
  const seg = Math.floor((Date.now() - f.getTime()) / 1000);
  if (seg < 60)    return "Hace un momento";
  if (seg < 3600)  return `Hace ${Math.floor(seg / 60)} min`;
  if (seg < 86400) return `Hace ${Math.floor(seg / 3600)} h`;
  return `Hace ${Math.floor(seg / 86400)} d`;
}

export function mapNotif(n) {
  return {
    id:      n.id_notificacion,
    icon:    ICONOS_NOTIF[n.tipo] || "🔔",
    titulo:  n.titulo,
    mensaje: n.mensaje,
    tiempo:  tiempoRelativo(n.fecha),
    leida:   n.leida,
  };
}

/**
 * Consume la pestaña Alertas desde el backend (sirve para cliente y plomero,
 * el backend filtra por el rol del token). Devuelve [notifs, marcarTodas].
 */
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
    const interval = setInterval(poll, 15000);
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
