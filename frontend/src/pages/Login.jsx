// src/pages/Login.jsx
import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import api from "../services/api";
import { useAuthStore } from "../store/authStore";
import TerminosCondiciones from "../components/TerminosCondiciones";

const Login = ({ onNav }) => {
  const setAuth  = useAuthStore((s) => s.setAuth);
  const [verTyC,   setVerTyC]   = useState(false);
  const [showPass, setShowPass] = useState(false);
  const [email,    setEmail]    = useState("");
  const [password, setPassword] = useState("");
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      // Un único endpoint unificado para clientes y plomeros
      const res = await api.post("/auth/login", { email, password });
      const rol = res.data.tipo || "cliente";

      const usuario = {
        id:        res.data.id,
        nombre:    res.data.nombre,
        apellido:  res.data.apellido,
        email:     res.data.email,
        localidad: res.data.localidad,
        direccion: res.data.direccion,
        latitud:   res.data.latitud,
        longitud:  res.data.longitud,
        rol:       res.data.tipo,
      };

      setAuth(res.data.access_token, usuario);

      if (rol === "plomero") {
        onNav("plomero");
      } else {
        onNav("app");
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Email o contraseña incorrectos");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4 font-sans">
      <div className="bg-white p-10 rounded-[2.5rem] shadow-xl w-full max-w-md border border-slate-100">

        {/* Logo */}
        <div className="flex justify-center mb-6">
          <div className="bg-blue-600 p-2 rounded-xl flex items-center gap-2 px-4 py-2 shadow-lg shadow-blue-100">
            <span className="text-white font-black text-2xl tracking-tighter">
              🔧 PlomerIA
            </span>
          </div>
        </div>

        <h2 className="text-2xl font-black text-center text-slate-800">
          Bienvenido de nuevo
        </h2>
        <p className="text-slate-400 text-center mb-8 text-sm font-medium">
          Ingresá con tu cuenta para continuar
        </p>

        <form className="space-y-5" onSubmit={handleLogin}>
          <div>
            <label className="block text-[10px] font-black text-slate-400 mb-1 uppercase tracking-widest ml-2">
              Correo Electrónico
            </label>
            <input
              required
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="tu@email.com"
              className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
            />
          </div>

          <div className="relative">
            <label className="block text-[10px] font-black text-slate-400 mb-1 uppercase tracking-widest ml-2">
              Contraseña
            </label>
            <input
              required
              type={showPass ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
            />
            <button
              type="button"
              onClick={() => setShowPass(!showPass)}
              className="absolute right-4 top-10 text-slate-300 hover:text-slate-500 transition-colors"
            >
              {showPass ? <EyeOff size={20} /> : <Eye size={20} />}
            </button>
          </div>

          <button
            type="button"
            onClick={() => onNav("olvide-password")}
            className="text-blue-500 text-xs font-bold w-full text-center hover:underline transition-all"
          >
            ¿Olvidaste tu contraseña?
          </button>

          {error && (
            <p className="text-red-500 text-sm text-center">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className={`w-full font-black py-4 rounded-2xl transition-all shadow-lg uppercase text-xs tracking-[0.2em] 
              ${loading ? "bg-slate-100 text-slate-300" : "bg-[#0f172a] text-white hover:bg-blue-600 shadow-blue-100"}`}
          >
            {loading ? "Cargando..." : "Ingresar →"}
          </button>
        </form>

        {/* Sección Registro */}
        <div className="mt-10 pt-8 border-t border-slate-100">
          <p className="text-center text-slate-400 text-[10px] font-black uppercase mb-6 tracking-widest">
            ¿Primera vez?
          </p>
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={() => onNav("registro")}
              className="flex flex-col items-center p-5 border border-blue-100 rounded-[2rem] bg-blue-50/50 hover:bg-blue-100 transition-all group shadow-sm shadow-blue-50"
            >
              <span className="text-3xl mb-2 group-hover:scale-110 transition-transform">🏠</span>
              <span className="text-[10px] font-extrabold text-blue-600 uppercase">Soy cliente</span>
              <span className="text-[9px] text-blue-400 mt-1 text-center leading-tight">Necesito un plomero</span>
            </button>

            <button
              onClick={() => onNav("registro-plomero")}
              className="flex flex-col items-center p-5 border border-emerald-100 rounded-[2rem] bg-emerald-50/50 hover:bg-emerald-100 transition-all group shadow-sm shadow-emerald-50"
            >
              <span className="text-3xl mb-2 group-hover:scale-110 transition-transform">🔧</span>
              <span className="text-[10px] font-extrabold text-emerald-600 uppercase">Soy profesional</span>
              <span className="text-[9px] text-emerald-400 mt-1 text-center leading-tight">Quiero ofrecer mis servicios</span>
            </button>
          </div>
        </div>

        {/* Bases y condiciones */}
        <p className="text-center text-[11px] text-slate-400 mt-6">
          Al ingresar o registrarte aceptás las{" "}
          <button
            type="button"
            onClick={() => setVerTyC(true)}
            className="text-blue-500 font-bold hover:underline"
          >
            Bases y Condiciones
          </button>
          .
        </p>
      </div>

      <TerminosCondiciones open={verTyC} onClose={() => setVerTyC(false)} />
    </div>
  );
};

export default Login;