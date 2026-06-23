// src/components/UserBadge.jsx
// Identidad del usuario en el header (avatar + nombre + rol).
// Compartido por el panel del cliente y el del profesional para que se vea
// EXACTAMENTE igual en los dos (consistencia visual).
export default function UserBadge({ nombre, apellido, rol }) {
  const inicial = (nombre?.[0] || "?").toUpperCase();
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "9px" }}>
      <div style={{
        width: "36px", height: "36px", borderRadius: "50%", flexShrink: 0,
        background: "linear-gradient(135deg,#3B82F6,#06B6D4)", color: "#fff",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontWeight: "800", fontSize: "15px", fontFamily: "'DM Sans',sans-serif",
      }}>
        {inicial}
      </div>
      <div style={{ lineHeight: "1.2" }}>
        <div style={{
          color: "#fff", fontWeight: "700", fontSize: "14px",
          fontFamily: "'DM Sans',sans-serif", whiteSpace: "nowrap",
        }}>
          {nombre}{apellido ? " " + apellido : ""}
        </div>
        <div style={{
          color: "#7DD3FC", fontSize: "11px", fontWeight: "600",
          fontFamily: "'DM Sans',sans-serif",
        }}>
          {rol}
        </div>
      </div>
    </div>
  );
}
