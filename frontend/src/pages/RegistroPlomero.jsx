// src/pages/RegistroPlomero.jsx
import { useState, useRef, useCallback } from "react";
import { useMutation } from "@tanstack/react-query";
import { registerPlomero, validarFotoPlomero } from "../services/plomeroService";
import DireccionConMapa from "../components/DireccionConMapa";
import TerminosCondiciones from "../components/TerminosCondiciones";
import { useAuthStore } from "../store/authStore";

// ─── PASOS ────────────────────────────────────────────────────────────────────
const PASOS = ["Oficio", "Perfil", "Especialidades", "Agenda", "Acceso"];

// ─── OFICIOS — solo plomería habilitado, el resto próximamente ────────────────
const OFICIOS = [
  { key: "plomeria",     label: "Plomería",     icon: "🔧", disponible: true,  desc: "Canillas, cañerías, destapes, gas" },
  { key: "electricidad", label: "Electricidad", icon: "⚡", disponible: false, desc: "Próximamente disponible" },
  { key: "gas",          label: "Gasista",      icon: "🔥", disponible: false, desc: "Próximamente disponible" },
  { key: "carpinteria",  label: "Carpintería",  icon: "🪚", disponible: false, desc: "Próximamente disponible" },
];

// ─── ESPECIALIDADES DE PLOMERÍA ───────────────────────────────────────────────
const ESPECIALIDADES = [
  { key: "PLOMERIA_GENERAL", label: "Plomería general", icon: "🔧", desc: "Canillas, pérdidas, inodoros, bombas" },
  { key: "DESTAPES",         label: "Destapes",         icon: "🚿", desc: "Cañerías, cloacas, desagües, pozos" },
  { key: "GAS_MATRICULADO",  label: "Gas matriculado",  icon: "🔥", desc: "Calefón, caldera, termotanque, cocina" },
  { key: "OBRA",             label: "Obra",             icon: "🏗️", desc: "Cañerías nuevas, reformas, impermeabilización" },
  { key: "FILTRACIONES",     label: "Filtraciones",     icon: "💧", desc: "Techos, paredes, terrazas, medianeras" },
  { key: "CALEFACCION",      label: "Calefacción",      icon: "♨️", desc: "Radiadores, losa radiante, fancoil" },
  { key: "OTRA",             label: "Otra",             icon: "➕", desc: "Especificá tu especialidad" },
];

const LOCALIDADES = [
  "Adrogué","Burzaco","Claypole","Don Orione","Glew","José Mármol",
  "Longchamps","Ministro Rivadavia","Monte Grande","Rafael Calzada",
  "San Francisco de Asís","San José","Temperley","Turdera","Lomas de Zamora",
  "Banfield","Lanús","Avellaneda","Quilmes","Berazategui","Florencio Varela","Otra",
];

const DIAS_SEMANA = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"];

const FRANJAS = [
  { key: "manana", label: "Mañana", rango: "08:00–13:00" },
  { key: "tarde",  label: "Tarde",  rango: "13:00–18:00" },
  { key: "noche",  label: "Noche",  rango: "18:00–22:00" },
];

const MIME_PERMITIDOS = ["image/jpeg", "image/png", "image/webp"];
const EXT_PERMITIDAS  = ["jpg", "jpeg", "png", "webp"];
const MAX_MB          = 5;

function cx(...args) { return args.filter(Boolean).join(" "); }

function validarFotoLocal(file) {
  if (!file) return "Seleccioná una foto";
  if (!MIME_PERMITIDOS.includes(file.type)) return "Solo se aceptan imágenes JPG, PNG o WEBP";
  const ext = file.name.split(".").pop().toLowerCase();
  if (!EXT_PERMITIDAS.includes(ext)) return "Extensión no permitida. Usá JPG, PNG o WEBP";
  if (file.size > MAX_MB * 1024 * 1024) return `La imagen no puede superar ${MAX_MB} MB`;
  return null;
}

// ─── STEP INDICATOR ───────────────────────────────────────────────────────────
function StepIndicator({ paso, labels }) {
  return (
    <div className="flex items-center justify-center gap-0 mb-8">
      {labels.map((label, i) => (
        <div key={i} className="flex items-center">
          <div className="flex flex-col items-center">
            <div className={cx(
              "w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all duration-300",
              i < paso   && "bg-emerald-500 text-white",
              i === paso && "bg-emerald-600 text-white ring-4 ring-emerald-100",
              i > paso   && "bg-slate-100 text-slate-400",
            )}>
              {i < paso ? "✓" : i + 1}
            </div>
            <span className={cx(
              "text-xs mt-1 font-medium whitespace-nowrap",
              i === paso ? "text-emerald-600" : "text-slate-400",
            )}>{label}</span>
          </div>
          {i < labels.length - 1 && (
            <div className={cx(
              "w-8 h-0.5 mx-1 mb-4 transition-all duration-300",
              i < paso ? "bg-emerald-400" : "bg-slate-200",
            )}/>
          )}
        </div>
      ))}
    </div>
  );
}

function Campo({ label, hint, error, children }) {
  return (
    <div>
      <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-1.5">
        {label}
        {hint && <span className="ml-1 text-slate-400 font-normal normal-case">{hint}</span>}
      </label>
      {children}
      {error && <p className="text-red-500 text-xs mt-1">⚠ {error}</p>}
    </div>
  );
}

function InputText({ placeholder, value, onChange, type = "text", error }) {
  return (
    <input
      type={type} placeholder={placeholder} value={value}
      onChange={(e) => onChange(e.target.value)}
      className={cx(
        "w-full border rounded-xl px-4 py-3 text-sm outline-none transition-all",
        "focus:ring-2 focus:ring-emerald-400 focus:border-transparent",
        error ? "border-red-300 bg-red-50" : "border-slate-200 bg-white",
      )}
    />
  );
}

// ─── PASO 0: OFICIO ───────────────────────────────────────────────────────────
function PasoOficio({ oficio, setOficio }) {
  return (
    <div className="space-y-3">
      <p className="text-sm text-slate-500 mb-4">
        Seleccioná a qué oficio te dedicás. Las especialidades se cargarán según tu elección.
      </p>
      {OFICIOS.map(({ key, label, icon, disponible, desc }) => (
        <button
          key={key}
          type="button"
          disabled={!disponible}
          onClick={() => disponible && setOficio(key)}
          className={cx(
            "w-full flex items-center gap-4 p-4 rounded-2xl border-2 text-left transition-all duration-200",
            !disponible && "opacity-50 cursor-not-allowed border-slate-100 bg-slate-50",
            disponible && oficio === key && "border-emerald-500 bg-emerald-50",
            disponible && oficio !== key && "border-slate-200 bg-white hover:border-slate-300",
          )}
        >
          <div className={cx(
            "w-11 h-11 rounded-xl flex items-center justify-center text-xl flex-shrink-0",
            disponible && oficio === key ? "bg-emerald-500" : "bg-slate-100",
          )}>
            {icon}
          </div>
          <div className="flex-1 min-w-0">
            <p className={cx("font-semibold text-sm",
              disponible && oficio === key ? "text-emerald-700" : "text-slate-800")}>
              {label}
            </p>
            <p className="text-xs text-slate-400 mt-0.5">{desc}</p>
          </div>
          {!disponible && (
            <span className="text-xs font-semibold text-slate-400 border border-slate-200 px-2 py-1 rounded-lg whitespace-nowrap">
              Próximamente
            </span>
          )}
          {disponible && (
            <div className={cx(
              "w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0",
              oficio === key ? "bg-emerald-500 border-emerald-500" : "border-slate-300",
            )}>
              {oficio === key && <span className="text-white text-xs font-bold">✓</span>}
            </div>
          )}
        </button>
      ))}
    </div>
  );
}

// ─── PASO 1: PERFIL ───────────────────────────────────────────────────────────
function PasoPerfil({ form, setForm, foto, setFoto, preview, setPreview,
                      fotoValida, setFotoValida, errores }) {
  const inputRef = useRef(null);
  const [fotoError, setFotoError] = useState("");
  const [validando, setValidando] = useState(false);
  const set = (k) => (v) => setForm((f) => ({ ...f, [k]: v }));

  const procesarFoto = useCallback(async (file) => {
    const errLocal = validarFotoLocal(file);
    if (errLocal) { setFotoError(errLocal); setFotoValida(false); return; }
    setFoto(file);
    setFotoValida(false);
    setFotoError("");
    const reader = new FileReader();
    reader.onload = (ev) => setPreview(ev.target.result);
    reader.readAsDataURL(file);
    setValidando(true);
    try {
      await validarFotoPlomero(file);
      setFotoValida(true);
      setFotoError("");
    } catch (err) {
      const detalle = err?.response?.data?.detail
        ?? "No se detectó un rostro. Subí una foto donde se vea tu cara.";
      setFotoError(detalle);
      setFotoValida(false);
      setFoto(null);
      setPreview(null);
      if (inputRef.current) inputRef.current.value = "";
    } finally {
      setValidando(false);
    }
  }, [setFoto, setPreview, setFotoValida]);

  const handleFoto = (e) => { const f = e.target.files?.[0]; if (f) procesarFoto(f); };
  const handleDrop = (e) => { e.preventDefault(); const f = e.dataTransfer.files?.[0]; if (f) procesarFoto(f); };

  return (
    <div className="space-y-4">
      <Campo label="Foto de perfil" hint="(JPG/PNG/WEBP · máx. 5 MB)" error={fotoError}>
        {preview ? (
          <div className={cx(
            "flex items-center gap-4 p-3 border rounded-xl",
            validando  && "border-amber-200 bg-amber-50",
            fotoValida && "border-emerald-200 bg-emerald-50",
            !fotoValida && !validando && fotoError && "border-red-200 bg-red-50",
          )}>
            <img src={preview} alt="preview" className="w-16 h-16 rounded-xl object-cover border-2 border-slate-200"/>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-slate-800 truncate">{foto?.name}</p>
              <p className="text-xs text-slate-500">
                {foto ? (foto.size / 1024 / 1024).toFixed(2) : "—"} MB ·{" "}
                {validando  && <span className="text-amber-600">Verificando rostro…</span>}
                {fotoValida && <span className="text-emerald-600">Rostro verificado ✓</span>}
                {!fotoValida && !validando && fotoError && <span className="text-red-500">Foto inválida</span>}
              </p>
            </div>
            <button type="button"
              onClick={() => { setFoto(null); setPreview(null); setFotoError(""); setFotoValida(false); if (inputRef.current) inputRef.current.value = ""; }}
              className="text-xs text-red-500 border border-red-200 hover:bg-red-50 px-3 py-1.5 rounded-lg transition-colors">
              Cambiar
            </button>
          </div>
        ) : (
          <label
            className="flex flex-col items-center justify-center gap-2 border-2 border-dashed border-slate-300 hover:border-emerald-400 hover:bg-emerald-50 rounded-xl p-6 cursor-pointer transition-all"
            onDragOver={(e) => e.preventDefault()} onDrop={handleDrop}>
            <input ref={inputRef} type="file"
              accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
              onChange={handleFoto} className="hidden"/>
            <div className="text-3xl">📷</div>
            <div className="text-center">
              <p className="text-sm font-semibold text-slate-700">Subir foto de perfil</p>
              <p className="text-xs text-slate-400 mt-0.5">Solo fotos con tu cara visible</p>
            </div>
          </label>
        )}
      </Campo>

      <div className="grid grid-cols-2 gap-3">
        <Campo label="Nombre" error={errores.nombre}>
          <InputText placeholder="Carlos" value={form.nombre} onChange={set("nombre")} error={errores.nombre}/>
        </Campo>
        <Campo label="Apellido" error={errores.apellido}>
          <InputText placeholder="Mendoza" value={form.apellido} onChange={set("apellido")} error={errores.apellido}/>
        </Campo>
      </div>

      {/* Dirección con mapa — reemplaza los campos separados de dirección y localidad */}
      <DireccionConMapa
        direccion={form.direccion}
        localidad={form.localidad}
        latitud={form.latitud}
        longitud={form.longitud}
        onDireccionChange={(v) => setForm((f) => ({ ...f, direccion: v }))}
        onLocalidadChange={(v) => setForm((f) => ({ ...f, localidad: v }))}
        onCoordsChange={(lat, lon) => setForm((f) => ({ ...f, latitud: lat, longitud: lon }))}
        error={errores.direccion || errores.localidad}
        localidades={LOCALIDADES}
      />

      <Campo label="Género">
        <div className="flex gap-3">
          {[["M","Masculino"],["F","Femenino"],["X","No binario"]].map(([v,l]) => (
            <button key={v} type="button" onClick={() => set("genero")(v)}
              className={cx("flex-1 py-2.5 rounded-xl text-sm font-semibold border transition-all",
                form.genero === v ? "bg-emerald-600 text-white border-emerald-600" : "bg-white text-slate-500 border-slate-200 hover:border-emerald-300")}>
              {l}
            </button>
          ))}
        </div>
      </Campo>

      <div className="flex flex-wrap gap-5 pt-1">
        {[["atiende_urgencias","Atiende urgencias (24hs)"],["matricula_gas","Matrícula de gas"]].map(([key, label]) => (
          <label key={key} className="flex items-center gap-2.5 cursor-pointer" onClick={() => set(key)(!form[key])}>
            <div className={cx("w-5 h-5 rounded-md border-2 flex items-center justify-center transition-all",
              form[key] ? "bg-emerald-500 border-emerald-500" : "border-slate-300")}>
              {form[key] && <span className="text-white text-xs font-bold">✓</span>}
            </div>
            <span className="text-sm text-slate-700">{label}</span>
          </label>
        ))}
      </div>
    </div>
  );
}

function PasoEspecialidades({ form, setForm, otraEsp, setOtraEsp, errores }) {
  const toggle = (key) => setForm((f) => ({
    ...f,
    especialidades: f.especialidades.includes(key)
      ? f.especialidades.filter((e) => e !== key)
      : [...f.especialidades, key],
  }));

  return (
    <div className="space-y-3">
      <p className="text-sm text-slate-500 mb-1">Seleccioná todos los tipos de trabajo que realizás.</p>
      {errores.especialidades && <p className="text-red-500 text-sm">⚠ {errores.especialidades}</p>}
      {ESPECIALIDADES.map(({ key, label, icon, desc }) => {
        const sel = form.especialidades.includes(key);
        return (
          <button key={key} type="button" onClick={() => toggle(key)}
            className={cx("w-full flex items-center gap-4 p-4 rounded-2xl border-2 text-left transition-all duration-200",
              sel ? "border-emerald-500 bg-emerald-50" : "border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50")}>
            <div className={cx("w-11 h-11 rounded-xl flex items-center justify-center text-xl flex-shrink-0 transition-all",
              sel ? "bg-emerald-500" : "bg-slate-100")}>{icon}</div>
            <div className="flex-1 min-w-0">
              <p className={cx("font-semibold text-sm", sel ? "text-emerald-700" : "text-slate-800")}>{label}</p>
              <p className="text-xs text-slate-400 mt-0.5">{desc}</p>
            </div>
            <div className={cx("w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all",
              sel ? "bg-emerald-500 border-emerald-500" : "border-slate-300")}>
              {sel && <span className="text-white text-xs font-bold">✓</span>}
            </div>
          </button>
        );
      })}
      {form.especialidades.includes("OTRA") && (
        <input type="text" placeholder="Especificá tu especialidad…" value={otraEsp}
          onChange={(e) => setOtraEsp(e.target.value)}
          className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-emerald-400 mt-1"/>
      )}
      {form.especialidades.length > 0 && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl">
          <p className="text-xs font-bold text-emerald-700 uppercase tracking-wide mb-1">Seleccionadas ({form.especialidades.length})</p>
          <p className="text-xs text-emerald-600">{form.especialidades.map((k) => ESPECIALIDADES.find((e) => e.key === k)?.label || k).join(" · ")}</p>
        </div>
      )}
    </div>
  );
}

// ─── PASO 3: AGENDA ───────────────────────────────────────────────────────────
function PasoAgenda({ agenda, setAgenda }) {
  const toggle = (dia, franja) => setAgenda((prev) => ({
    ...prev, [dia]: { ...(prev[dia] || {}), [franja]: !(prev[dia]?.[franja]) },
  }));
  const selTodaFranja = (franja) => {
    const todosActivos = DIAS_SEMANA.every((d) => agenda[d]?.[franja]);
    setAgenda((prev) => {
      const next = { ...prev };
      DIAS_SEMANA.forEach((d) => { next[d] = { ...(next[d] || {}), [franja]: !todosActivos }; });
      return next;
    });
  };
  const totalFranjas = DIAS_SEMANA.reduce((acc, d) => acc + FRANJAS.filter((f) => agenda[d]?.[f.key]).length, 0);

  return (
    <div>
      <p className="text-sm text-slate-500 mb-4">Marcá en qué días y franjas estás disponible. Podés modificarla después.</p>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead><tr>
            <th className="text-left pb-2 font-bold text-slate-400 uppercase tracking-wide w-24">Franja</th>
            {DIAS_SEMANA.map((d) => <th key={d} className="pb-2 font-bold text-slate-600 text-center">{d}</th>)}
          </tr></thead>
          <tbody>
            {FRANJAS.map(({ key, label, rango }) => (
              <tr key={key} className="border-t border-slate-100">
                <td className="py-2 pr-3">
                  <button type="button" onClick={() => selTodaFranja(key)} className="text-left hover:text-emerald-600 transition-colors">
                    <p className="font-semibold text-slate-700">{label}</p>
                    <p className="text-slate-400">{rango}</p>
                  </button>
                </td>
                {DIAS_SEMANA.map((dia) => {
                  const activo = agenda[dia]?.[key] || false;
                  return (
                    <td key={dia} className="py-2 text-center">
                      <button type="button" onClick={() => toggle(dia, key)}
                        className={cx("w-8 h-8 rounded-lg border-2 mx-auto flex items-center justify-center transition-all duration-150",
                          activo ? "bg-emerald-500 border-emerald-500 text-white" : "border-slate-200 hover:border-emerald-300 bg-white")}>
                        {activo && <span className="text-xs font-bold">✓</span>}
                      </button>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-slate-400 mt-3">💡 Hacé clic en el nombre de la franja para marcar todos los días.</p>
      {totalFranjas > 0 ? (
        <div className="mt-4 p-3 bg-emerald-50 border border-emerald-200 rounded-xl">
          <p className="text-xs font-bold text-emerald-700">{totalFranjas} franja{totalFranjas !== 1 ? "s" : ""} seleccionada{totalFranjas !== 1 ? "s" : ""}</p>
        </div>
      ) : (
        <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-xl">
          <p className="text-xs text-amber-700">⚠ Si no marcás ninguna franja, los clientes verán horarios por defecto.</p>
        </div>
      )}
    </div>
  );
}

// ─── PASO 4: ACCESO ───────────────────────────────────────────────────────────
function PasoAcceso({ form, setForm, errores, oficio }) {
  const [showPass, setShowPass] = useState(false);
  const set = (k) => (v) => setForm((f) => ({ ...f, [k]: v }));
  const strength = form.password.length < 4 ? 1 : form.password.length < 8 ? 2 : 3;
  const strengthLabel = ["", "Débil", "Regular", "Fuerte"][strength];
  const strengthColor = ["", "#EF4444", "#F59E0B", "#22C55E"][strength];
  const oficioLabel = OFICIOS.find(o => o.key === oficio)?.label || oficio;

  return (
    <div className="space-y-4">
      <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4">
        <p className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-3">Resumen de tu perfil</p>
        <div className="space-y-2">
          {[
            ["Oficio",         oficioLabel],
            ["Nombre",         `${form.nombre} ${form.apellido}`],
            ["Localidad",      form.localidad || "—"],
            ["Especialidades", form.especialidades.length > 0 ? `${form.especialidades.length} seleccionadas` : "—"],
            ["Urgencias",      form.atiende_urgencias ? "✓ Sí" : "No"],
            ["Gas",            form.matricula_gas ? "✓ Matriculado" : "No"],
          ].map(([k, v]) => (
            <div key={k} className="flex justify-between items-center">
              <span className="text-xs text-slate-400">{k}</span>
              <span className="text-xs font-semibold text-slate-700">{v}</span>
            </div>
          ))}
        </div>
      </div>
      <Campo label="Email" error={errores.email}>
        <InputText placeholder="tu@email.com" type="email" value={form.email} onChange={set("email")} error={errores.email}/>
      </Campo>
      <Campo label="Contraseña" error={errores.password}>
        <div className="relative">
          <input type={showPass ? "text" : "password"} placeholder="Mínimo 6 caracteres"
            value={form.password} onChange={(e) => set("password")(e.target.value)}
            className={cx("w-full border rounded-xl px-4 py-3 pr-10 text-sm outline-none transition-all focus:ring-2 focus:ring-emerald-400 focus:border-transparent",
              errores.password ? "border-red-300 bg-red-50" : "border-slate-200")}/>
          <button type="button" onClick={() => setShowPass((p) => !p)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
            {showPass ? "🙈" : "👁"}
          </button>
        </div>
        {form.password.length > 0 && (
          <div className="mt-1.5 flex items-center gap-2">
            <div className="flex gap-1">
              {[1,2,3].map((i) => (
                <div key={i} className="w-8 h-1 rounded-full transition-all"
                  style={{ background: i <= strength ? strengthColor : "#E2E8F0" }}/>
              ))}
            </div>
            <span className="text-xs font-semibold" style={{ color: strengthColor }}>{strengthLabel}</span>
          </div>
        )}
      </Campo>
      <Campo label="Confirmar contraseña" error={errores.confirmar}>
        <InputText placeholder="Repetí la contraseña" type={showPass ? "text" : "password"}
          value={form.confirmar} onChange={set("confirmar")} error={errores.confirmar}/>
      </Campo>
    </div>
  );
}

// ─── COMPONENTE PRINCIPAL ─────────────────────────────────────────────────────
export default function RegistroPlomero({ onNav }) {
  const setAuth = useAuthStore((s) => s.setAuth);
  const [paso,       setPaso]       = useState(0);
  const [error,      setError]      = useState("");
  const [errores,    setErrores]    = useState({});
  const [foto,       setFoto]       = useState(null);
  const [preview,    setPreview]    = useState(null);
  const [fotoValida, setFotoValida] = useState(false);
  const [otraEsp,    setOtraEsp]    = useState("");
  const [agenda,     setAgenda]     = useState({});
  const [oficio,     setOficio]     = useState("plomeria");
  const [acepta,     setAcepta]     = useState(false);
  const [verTyC,     setVerTyC]     = useState(false);

  const [form, setForm] = useState({
    nombre: "", apellido: "", email: "", password: "", confirmar: "",
    direccion: "", localidad: "", latitud: null, longitud: null, especialidades: [], genero: "M",
    atiende_urgencias: false, matricula_gas: false,
  });

  const validar = () => {
    const e = {};
    if (paso === 0) {
      if (!oficio) e.oficio = "Seleccioná un oficio";
    }
    if (paso === 1) {
      if (!form.nombre.trim())    e.nombre    = "Requerido";
      if (!form.apellido.trim())  e.apellido  = "Requerido";
      if (!form.direccion.trim()) e.direccion = "Requerido";
      if (!form.localidad)        e.localidad = "Seleccioná una localidad";
      if (!fotoValida)            e.foto      = "Subí una foto de perfil con tu cara visible y esperá la verificación";
    }
    if (paso === 2) {
      if (form.especialidades.length === 0) e.especialidades = "Seleccioná al menos una especialidad";
    }
    if (paso === 4) {
      if (!form.email.includes("@")) e.email    = "Email inválido";
      if (form.password.length < 6)  e.password = "Mínimo 6 caracteres";
      if (form.password !== form.confirmar) e.confirmar = "Las contraseñas no coinciden";
      if (!acepta) e.acepta = "Tenés que aceptar las Bases y Condiciones para registrarte";
    }
    setErrores(e);
    return Object.keys(e).length === 0;
  };

  const avanzar = () => {
    setError("");
    if (!validar()) return;
    if (paso < 4) { setPaso((p) => p + 1); return; }
    submit();
  };

  const mut = useMutation({
    mutationFn: registerPlomero,
    onSuccess: (data) => {
      const usuario = { id: data.id_plomero, nombre: data.nombre, rol: "plomero" };
      setAuth(data.access_token, usuario);
      onNav("login"); // vuelve al login para que ingrese con sus credenciales
    },
    onError: (err) => {
      const det = err?.response?.data?.detail;
      if (Array.isArray(det)) setError(det.map((e) => e.msg).join(", "));
      else setError(det ?? "Error al registrar. Intentá de nuevo.");
    },
  });

  const submit = () => {
    setError("");
    let espFinal = [...form.especialidades];
    if (espFinal.includes("OTRA") && otraEsp.trim()) {
      espFinal = espFinal.filter((e) => e !== "OTRA");
      espFinal.push(`OTRA:${otraEsp.trim()}`);
    }
    const agendaFlat = {};
    Object.entries(agenda).forEach(([dia, franjas]) => {
      Object.entries(franjas).forEach(([franja, activo]) => {
        if (activo) agendaFlat[`${dia}_${franja}`] = true;
      });
    });
    mut.mutate({ ...form, especialidades: espFinal, agenda: agendaFlat, foto: foto || undefined });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 to-emerald-50 flex items-start justify-center p-4 py-10">
      <div className="bg-white rounded-3xl shadow-2xl w-full max-w-lg p-8">
        <div className="flex items-center justify-center gap-2 mb-2">
          <div className="w-9 h-9 bg-emerald-600 rounded-xl flex items-center justify-center text-lg">🔧</div>
          <span className="text-2xl font-bold text-slate-800">Plomer<span className="text-emerald-600">IA</span></span>
        </div>
        <p className="text-center text-slate-500 text-sm mb-6">Creá tu perfil profesional</p>
        <StepIndicator paso={paso} labels={PASOS} />

        {errores.foto && paso === 1 && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-xl px-4 py-3">
            <p className="text-red-600 text-sm text-center">⚠ {errores.foto}</p>
          </div>
        )}

        {paso === 0 && <PasoOficio oficio={oficio} setOficio={setOficio} />}
        {paso === 1 && <PasoPerfil form={form} setForm={setForm} foto={foto} setFoto={setFoto}
          preview={preview} setPreview={setPreview} fotoValida={fotoValida} setFotoValida={setFotoValida} errores={errores}/>}
        {paso === 2 && <PasoEspecialidades form={form} setForm={setForm} otraEsp={otraEsp} setOtraEsp={setOtraEsp} errores={errores}/>}
        {paso === 3 && <PasoAgenda agenda={agenda} setAgenda={setAgenda}/>}
        {paso === 4 && <PasoAcceso form={form} setForm={setForm} errores={errores} oficio={oficio}/>}

        {paso === 4 && (
          <div className="mt-4">
            <label className="flex items-start gap-2 text-sm text-slate-600 cursor-pointer select-none">
              <input type="checkbox" checked={acepta} onChange={(e) => setAcepta(e.target.checked)}
                className="mt-0.5 w-4 h-4 accent-emerald-600" />
              <span>
                Leí y acepto las{" "}
                <button type="button" onClick={() => setVerTyC(true)}
                  className="text-emerald-600 font-semibold hover:underline">
                  Bases y Condiciones
                </button>.
              </span>
            </label>
            {errores.acepta && (
              <p className="text-red-600 text-xs mt-1">{errores.acepta}</p>
            )}
          </div>
        )}

        {error && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-xl px-4 py-3">
            <p className="text-red-600 text-sm text-center">{error}</p>
          </div>
        )}

        <div className="flex gap-3 mt-6">
          {paso > 0 && (
            <button type="button" onClick={() => { setPaso((p) => p - 1); setErrores({}); setError(""); }}
              className="flex-1 border border-slate-200 hover:border-slate-300 bg-white text-slate-600 font-semibold py-3 rounded-xl text-sm transition-colors">
              ← Atrás
            </button>
          )}
          <button type="button" onClick={avanzar} disabled={mut.isPending || (paso === 4 && !acepta)}
            className="flex-1 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed text-white font-bold py-3 rounded-xl text-sm transition-colors">
            {mut.isPending ? "Registrando…" : paso === 4 ? "Crear cuenta →" : "Siguiente →"}
          </button>
        </div>

        <p className="text-center text-sm text-slate-400 mt-4">
          ¿Ya tenés cuenta?{" "}
          <button type="button" onClick={() => onNav("login")} className="text-emerald-600 hover:underline font-semibold">
            Ingresá
          </button>
        </p>
      </div>

      <TerminosCondiciones open={verTyC} onClose={() => setVerTyC(false)} />
    </div>
  );
}