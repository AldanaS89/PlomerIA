// Cartel de "Cuenta suspendida" con diseño propio de la app.
// Se renderiza por DOM (no React) para poder dispararse desde cualquier lado:
// el interceptor de axios (api.js) o el chat por WebSocket (ChatWidget.jsx).
export function mostrarCartelSuspension(mensaje, onAceptar) {
  // Evitar duplicados si llega más de un 403/evento seguido.
  if (document.getElementById("cartel-suspension")) return;

  const overlay = document.createElement("div");
  overlay.id = "cartel-suspension";
  overlay.style.cssText = [
    "position:fixed", "inset:0", "z-index:99999",
    "background:rgba(15,23,42,0.55)", "backdrop-filter:blur(2px)",
    "display:flex", "align-items:center", "justify-content:center",
    "padding:20px", "font-family:'DM Sans',sans-serif",
  ].join(";");

  const card = document.createElement("div");
  card.style.cssText = [
    "background:#fff", "border-radius:20px", "max-width:380px", "width:100%",
    "padding:30px 26px", "text-align:center",
    "box-shadow:0 24px 70px rgba(0,0,0,0.35)",
    "border:1px solid #FECACA",
  ].join(";");

  const icono = document.createElement("div");
  icono.textContent = "🚫";
  icono.style.cssText = "font-size:46px;margin-bottom:12px;";

  const titulo = document.createElement("div");
  titulo.textContent = "Cuenta suspendida";
  titulo.style.cssText = "font-weight:800;font-size:20px;color:#0F172A;margin-bottom:10px;";

  const texto = document.createElement("div");
  texto.textContent = mensaje || "Tu cuenta fue suspendida.";
  texto.style.cssText = "font-size:14px;color:#475569;line-height:1.55;margin-bottom:22px;";

  const boton = document.createElement("button");
  boton.textContent = "Aceptar";
  boton.style.cssText = [
    "background:linear-gradient(135deg,#EF4444,#DC2626)", "color:#fff",
    "border:none", "border-radius:12px", "padding:12px 32px",
    "font-family:'DM Sans',sans-serif", "font-weight:700", "font-size:14px",
    "cursor:pointer", "width:100%",
  ].join(";");
  boton.onclick = () => {
    overlay.remove();
    if (typeof onAceptar === "function") onAceptar();
  };

  card.appendChild(icono);
  card.appendChild(titulo);
  card.appendChild(texto);
  card.appendChild(boton);
  overlay.appendChild(card);
  document.body.appendChild(overlay);
}
