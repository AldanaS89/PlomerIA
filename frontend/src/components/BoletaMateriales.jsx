import { useState, useEffect, useCallback, useRef } from "react";
import api from "../services/api";

const fmt = (n) => "$" + Number(n || 0).toLocaleString("es-AR");

/**
 * Boleta / presupuesto de un trabajo, con aspecto de comprobante.
 * El plomero carga renglones (concepto + monto), incluida la mano de obra,
 * y el total se suma solo. El cliente la ve siempre y se actualiza en vivo.
 *
 * props: idSolicitud, editable, diagnostico, fecha
 */
export default function BoletaMateriales({ idSolicitud, editable = false, diagnostico, fecha }) {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [concepto, setConcepto] = useState("");
  const [monto, setMonto] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [abierto, setAbierto] = useState(false);
  const montoRef = useRef(null);

  const cargar = useCallback(async () => {
    if (!idSolicitud) return;
    try {
      const res = await api.get(`/boleta/${idSolicitud}`);
      const nuevos = Array.isArray(res.data?.items) ? res.data.items : [];
      // Sin re-render si no cambió (no interrumpe la escritura del plomero)
      setItems(prev => JSON.stringify(prev) === JSON.stringify(nuevos) ? prev : nuevos);
      setTotal(res.data?.total || 0);
    } catch { /* noop */ }
  }, [idSolicitud]);

  // Carga inicial + refresco en vivo (el cliente ve lo que el plomero va cargando)
  useEffect(() => {
    cargar();
    const id = setInterval(cargar, 8000);
    return () => clearInterval(id);
  }, [cargar]);

  const agregar = async (desc, valor) => {
    const d = (desc ?? concepto).trim();
    const v = parseFloat(valor ?? monto) || 0;
    if (!d) return;
    if (v <= 0) {           // no se cargan montos negativos ni en cero
      alert("El monto debe ser mayor a 0.");
      return;
    }
    setGuardando(true);
    try {
      const res = await api.post(`/boleta/${idSolicitud}`, { descripcion: d, cantidad: 1, precio: v });
      setItems(res.data?.items || []);
      setTotal(res.data?.total || 0);
      setConcepto(""); setMonto("");
    } catch { /* noop */ } finally { setGuardando(false); }
  };

  const borrar = async (idItem) => {
    try {
      const res = await api.delete(`/boleta/item/${idItem}`);
      setItems(res.data?.items || []);
      setTotal(res.data?.total || 0);
    } catch { /* noop */ }
  };

  // Precarga el concepto "Mano de obra" para que el plomero escriba el monto
  const prepararManoDeObra = () => {
    setConcepto("Mano de obra");
    if (montoRef.current) montoRef.current.focus();
  };

  const fechaTxt = fecha ? new Date(fecha).toLocaleDateString("es-AR") : new Date().toLocaleDateString("es-AR");

  return (
    <div style={{ marginTop: "12px" }}>
      <button onClick={() => setAbierto(o => !o)} style={{
        width: "100%", display: "flex", justifyContent: "space-between", alignItems: "center",
        background: "#F8FAFC", border: "1.5px solid #F1F5F9", borderRadius: "10px", cursor: "pointer",
        padding: "10px 14px", fontFamily: "'DM Sans',sans-serif", fontWeight: "700",
        fontSize: "13px", color: "#0F172A",
      }}>
        <span>🧾 Presupuesto / Boleta {total > 0 ? `· ${fmt(total)}` : ""}</span>
        <span style={{ color: "#94A3B8" }}>{abierto ? "▾" : "▸"}</span>
      </button>

      {abierto && (
        <div style={{
          marginTop: "8px", background: "#FFFEF7",
          border: "1px solid #E7E2CF", borderRadius: "10px", padding: "16px 18px",
          boxShadow: "0 2px 10px rgba(0,0,0,0.05)",
        }}>
          {/* Encabezado del comprobante */}
          <div style={{ textAlign: "center", borderBottom: "2px dashed #D6CFB4", paddingBottom: "10px", marginBottom: "10px" }}>
            <div style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800",
              fontSize: "15px", letterSpacing: "1px", color: "#0F172A" }}>PRESUPUESTO</div>
            <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "12px", color: "#64748B", marginTop: "3px" }}>
              Diagnóstico: <strong>{diagnostico || "Trabajo de plomería"}</strong>
            </div>
            <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "11px", color: "#94A3B8" }}>
              Fecha: {fechaTxt}
            </div>
          </div>

          {/* Renglones */}
          {items.length === 0 && (
            <div style={{ fontFamily: "'DM Sans',sans-serif", fontSize: "12px",
              color: "#94A3B8", textAlign: "center", padding: "8px 0" }}>
              {editable
                ? "Agregá materiales y la mano de obra."
                : "El profesional todavía no cargó la boleta."}
            </div>
          )}

          {items.map(it => (
            <div key={it.id_item} style={{ display: "flex", alignItems: "center",
              gap: "8px", padding: "5px 0", borderBottom: "1px dotted #E2DDC8" }}>
              <span style={{ flex: 1, minWidth: 0, fontFamily: "'DM Sans',sans-serif",
                fontSize: "13px", color: "#1F2937" }}>{it.descripcion}</span>
              <span style={{ fontFamily: "'Courier New',monospace", fontSize: "13px",
                fontWeight: "700", color: "#1F2937", whiteSpace: "nowrap" }}>
                {fmt(it.cantidad * it.precio)}
              </span>
              {editable && (
                <button onClick={() => borrar(it.id_item)} title="Quitar" style={{
                  background: "transparent", border: "none", cursor: "pointer",
                  color: "#EF4444", fontSize: "14px", padding: "0 2px" }}>✕</button>
              )}
            </div>
          ))}

          {/* Total */}
          {items.length > 0 && (
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center",
              marginTop: "10px", paddingTop: "8px", borderTop: "2px solid #0F172A" }}>
              <span style={{ fontFamily: "'DM Sans',sans-serif", fontWeight: "800", fontSize: "14px", color: "#0F172A" }}>TOTAL</span>
              <span style={{ fontFamily: "'Courier New',monospace", fontWeight: "800", fontSize: "16px", color: "#16A34A" }}>{fmt(total)}</span>
            </div>
          )}

          {/* Alta de renglón (solo plomero) */}
          {editable && (
            <div style={{ marginTop: "14px", borderTop: "1px dashed #D6CFB4", paddingTop: "12px" }}>
              <div style={{ display: "flex", gap: "6px", alignItems: "center", flexWrap: "wrap" }}>
                <input value={concepto} onChange={e => setConcepto(e.target.value)}
                  placeholder="Concepto (material / mano de obra)"
                  style={{ flex: "1 1 140px", minWidth: 0, border: "1.5px solid #E2E8F0", borderRadius: "8px",
                    padding: "8px 10px", fontSize: "13px", fontFamily: "'DM Sans',sans-serif", outline: "none", background: "#fff" }} />
                <input ref={montoRef} value={monto} onChange={e => setMonto(e.target.value)} placeholder="Monto" type="number" min="0"
                  style={{ width: "92px", border: "1.5px solid #E2E8F0", borderRadius: "8px",
                    padding: "8px", fontSize: "13px", fontFamily: "'DM Sans',sans-serif", outline: "none", background: "#fff" }} />
                <button onClick={() => agregar()} disabled={guardando || !concepto.trim()} style={{
                  background: concepto.trim() ? "linear-gradient(135deg,#3B82F6,#2563EB)" : "#E2E8F0",
                  color: concepto.trim() ? "#fff" : "#94A3B8", border: "none", borderRadius: "8px",
                  padding: "8px 14px", fontFamily: "'DM Sans',sans-serif", fontWeight: "700",
                  fontSize: "13px", cursor: concepto.trim() ? "pointer" : "not-allowed" }}>Agregar</button>
              </div>
              <button onClick={prepararManoDeObra} disabled={guardando}
                style={{ marginTop: "8px", background: "transparent", border: "1px dashed #CBD5E1",
                  borderRadius: "8px", padding: "6px 12px", fontFamily: "'DM Sans',sans-serif",
                  fontSize: "12px", color: "#475569", cursor: "pointer" }}>
                + Mano de obra (escribí el monto y tocá Agregar)
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
