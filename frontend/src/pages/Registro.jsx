import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import api from "../services/api";

const Registro = () => {
  const location = useLocation();
  const navigate = useNavigate();

  // 1. Detectar rol inicial desde el Login
  const [rol, setRol] = useState(location.state?.rolInicial || "usuario");
  const [loading, setLoading] = useState(false);

  // 2. Estado del formulario (unificado para cumplir con tus schemas)
  const [formData, setFormData] = useState({
    nombre: "",
    apellido: "",
    email: "",
    password: "",
    telefono: "",
    direccion: "",
    localidad: "",
    // Campos específicos de Plomero (Schema PlomeroRequest)
    especialidades: [],
    genero: "masculino",
    atiende_urgencias: false,
    matricula_gas: false,
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  // Manejo especial para la lista de especialidades
  const handleEspecialidades = (esp) => {
    const current = formData.especialidades;
    setFormData({
      ...formData,
      especialidades: current.includes(esp)
        ? current.filter((i) => i !== esp)
        : [...current, esp],
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    // Ajuste de data según el schema que espera el backend
    const dataAEnviar =
      rol === "usuario" ? { ...formData, rol: "cliente" } : formData;

    const endpoint =
      rol === "usuario" ? "/usuarios/registro" : "/plomeros/registro";

    try {
      // 1. Registro en el backend
      const res = await api.post(endpoint, dataAEnviar);

      // 2. Lógica de Auto-Login (Guardamos el token que viene del registro)
      const authData = {
        state: {
          token: res.data.access_token,
          user: {
            id: res.data.id_usuario || res.data.id_plomero,
            nombre: res.data.nombre,
            rol: res.data.rol || (rol === "usuario" ? "cliente" : "plomero"),
          },
        },
      };

      localStorage.setItem("plomeria-auth", JSON.stringify(authData));

      alert("¡Cuenta creada con éxito!");

      // 3. Redirigir según el rol
      if (rol === "plomero") {
        navigate("/plomero");
      } else {
        navigate("/cliente");
      }

    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Error en el registro. Verificá los datos.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 py-10 px-4 font-sans">
      <div className="max-w-2xl mx-auto bg-white p-10 rounded-[2.5rem] shadow-xl border border-slate-100">
        <h2 className="text-3xl font-black text-center mb-2 text-slate-800">Unite a PlomerIA</h2>
        <p className="text-center text-slate-400 mb-8 text-sm">Completá tus datos para empezar</p>

        {/* SELECTOR DE ROL */}
        <div className="flex bg-slate-100 p-2 rounded-3xl mb-8">
          <button
            type="button"
            onClick={() => setRol("usuario")}
            className={`flex-1 py-4 rounded-2xl font-bold transition-all ${rol === "usuario" ? "bg-white shadow-md text-blue-600" : "text-slate-400"}`}
          >
            🏠 Soy Cliente
          </button>
          <button
            type="button"
            onClick={() => setRol("plomero")}
            className={`flex-1 py-4 rounded-2xl font-bold transition-all ${rol === "plomero" ? "bg-white shadow-md text-emerald-600" : "text-slate-400"}`}
          >
            🔧 Soy Plomero
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-slate-400 uppercase ml-2">Nombre</label>
              <input name="nombre" placeholder="Ej: Juan" onChange={handleChange} className="w-full p-4 bg-slate-50 rounded-2xl border border-slate-100 focus:ring-2 focus:ring-blue-500 outline-none" required />
            </div>
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-slate-400 uppercase ml-2">Apellido</label>
              <input name="apellido" placeholder="Ej: Pérez" onChange={handleChange} className="w-full p-4 bg-slate-50 rounded-2xl border border-slate-100 focus:ring-2 focus:ring-blue-500 outline-none" required />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-[10px] font-bold text-slate-400 uppercase ml-2">Correo Electrónico</label>
            <input name="email" type="email" placeholder="correo@ejemplo.com" onChange={handleChange} className="w-full p-4 bg-slate-50 rounded-2xl border border-slate-100 focus:ring-2 focus:ring-blue-500 outline-none" required />
          </div>

          <div className="space-y-1">
            <label className="text-[10px] font-bold text-slate-400 uppercase ml-2">Contraseña</label>
            <input name="password" type="password" placeholder="••••••••" onChange={handleChange} className="w-full p-4 bg-slate-50 rounded-2xl border border-slate-100 focus:ring-2 focus:ring-blue-500 outline-none" required />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-slate-400 uppercase ml-2">Teléfono</label>
              <input name="telefono" placeholder="11 2233 4455" onChange={handleChange} className="w-full p-4 bg-slate-50 rounded-2xl border border-slate-100 focus:ring-2 focus:ring-blue-500 outline-none" required />
            </div>
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-slate-400 uppercase ml-2">Localidad</label>
              <input name="localidad" placeholder="Ej: Glew" onChange={handleChange} className="w-full p-4 bg-slate-50 rounded-2xl border border-slate-100 focus:ring-2 focus:ring-blue-500 outline-none" required />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-[10px] font-bold text-slate-400 uppercase ml-2">Dirección</label>
            <input name="direccion" placeholder="Calle y número" onChange={handleChange} className="w-full p-4 bg-slate-50 rounded-2xl border border-slate-100 focus:ring-2 focus:ring-blue-500 outline-none" required />
          </div>

          {/* CAMPOS EXCLUSIVOS PARA PLOMERO */}
          {rol === "plomero" && (
            <div className="pt-6 border-t border-dashed border-slate-200 space-y-6 animate-in fade-in slide-in-from-top-4">
              <div>
                <label className="text-[10px] font-black uppercase text-slate-400 ml-2">Mis Especialidades</label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {["Cañerías", "Gas", "Termotanques", "Cloacas", "Grifería"].map((esp) => (
                    <button
                      key={esp}
                      type="button"
                      onClick={() => handleEspecialidades(esp)}
                      className={`px-4 py-2 rounded-xl text-xs font-bold border transition-all ${formData.especialidades.includes(esp) ? "bg-emerald-500 border-emerald-500 text-white shadow-md shadow-emerald-100" : "bg-white border-slate-200 text-slate-400 hover:border-emerald-200"}`}
                    >
                      {esp}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <label className="flex items-center gap-3 p-4 bg-slate-50 rounded-2xl cursor-pointer hover:bg-emerald-50 transition-colors">
                  <input type="checkbox" name="atiende_urgencias" onChange={handleChange} className="w-5 h-5 accent-emerald-500" />
                  <span className="text-xs font-bold text-slate-600">Urgencias 24h</span>
                </label>
                <label className="flex items-center gap-3 p-4 bg-slate-50 rounded-2xl cursor-pointer hover:bg-emerald-50 transition-colors">
                  <input type="checkbox" name="matricula_gas" onChange={handleChange} className="w-5 h-5 accent-emerald-500" />
                  <span className="text-xs font-bold text-slate-600">Matrícula Gas</span>
                </label>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-slate-400 uppercase ml-2">Género</label>
                <select name="genero" onChange={handleChange} className="w-full p-4 bg-slate-50 rounded-2xl border border-slate-100 outline-none">
                  <option value="masculino">Masculino</option>
                  <option value="femenino">Femenino</option>
                  <option value="otro">Otro</option>
                </select>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-5 rounded-[2rem] font-black uppercase tracking-widest text-white mt-6 transition-all shadow-lg ${rol === "usuario" ? "bg-[#0f172a] hover:bg-blue-600 shadow-blue-100" : "bg-emerald-500 hover:bg-emerald-600 shadow-emerald-100"}`}
          >
            {loading ? "Creando cuenta..." : `Registrarme ahora →`}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Registro;