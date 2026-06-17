// Cartel/toast con la estética de PlomerIA. Reemplaza los alert() nativos.
// El color y el ícono dependen del tipo de mensaje.
// Uso:  mostrarCartel("Guardado", "exito")  |  "error" | "aviso" | "info"
// Se renderiza por DOM para poder usarse desde cualquier lado (componentes,
// interceptores, etc.).

const ESTILOS = {
  exito: { bg: "#F0FDF4", border: "#86EFAC", color: "#15803D", icon: "✓" },
  error: { bg: "#FEF2F2", border: "#FECACA", color: "#B91C1C", icon: "⚠️" },
  aviso: { bg: "#FFFBEB", border: "#FDE68A", color: "#B45309", icon: "⚠️" },
  info:  { bg: "#EFF6FF", border: "#BFDBFE", color: "#1D4ED8", icon: "ℹ️" },
};

export function mostrarCartel(mensaje, tipo = "info") {
  const e = ESTILOS[tipo] || ESTILOS.info;

  let cont = document.getElementById("cartel-contenedor");
  if (!cont) {
    cont = document.createElement("div");
    cont.id = "cartel-contenedor";
    cont.style.cssText = [
      "position:fixed", "top:18px", "left:50%", "transform:translateX(-50%)",
      "z-index:99998", "display:flex", "flex-direction:column", "gap:10px",
      "align-items:center", "pointer-events:none",
    ].join(";");
    document.body.appendChild(cont);
  }

  const card = document.createElement("div");
  card.style.cssText = [
    "pointer-events:auto", "display:flex", "align-items:center", "gap:10px",
    `background:${e.bg}`, `border:1.5px solid ${e.border}`, `color:${e.color}`,
    "border-radius:14px", "padding:12px 16px", "max-width:90vw",
    "box-shadow:0 10px 30px rgba(15,23,42,0.18)",
    "font-family:'DM Sans',sans-serif", "font-size:13.5px", "font-weight:600",
    "line-height:1.4", "opacity:0", "transform:translateY(-8px)",
    "transition:opacity .2s, transform .2s", "cursor:pointer",
  ].join(";");

  const ic = document.createElement("span");
  ic.textContent = e.icon;
  ic.style.cssText = "font-size:16px;flex-shrink:0;";

  const tx = document.createElement("span");
  tx.textContent = mensaje || "";

  card.appendChild(ic);
  card.appendChild(tx);
  cont.appendChild(card);

  requestAnimationFrame(() => {
    card.style.opacity = "1";
    card.style.transform = "translateY(0)";
  });

  const quitar = () => {
    card.style.opacity = "0";
    card.style.transform = "translateY(-8px)";
    setTimeout(() => card.remove(), 200);
  };
  card.onclick = quitar;
  setTimeout(quitar, 4200);
}
