import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";

import { registerPlomero} from "../../services/plomeroService";
import { useAuthStore } from "../../store/authStore";

export default function RegisterPlomero() {

  const navigate = useNavigate();
  const setAuth = useAuthStore((s) => s.setAuth);

  const [error, setError] = useState("");
  const [otraEspecialidad, setOtraEspecialidad] = useState("");

  const [form, setForm] = useState({
    nombre: "",
    apellido: "",
    email: "",
    password: "",
    telefono: "",
    direccion: "",        // 👈 NUEVO
    localidad: "",
    especialidades: [],
    genero: "M",
    atiende_urgencias: false,
    matricula_gas: false,
  });

  /* ───────────────────────────── */
  /* MUTATION */
  /* ───────────────────────────── */
  const mut = useMutation({
    mutationFn: registerPlomero,

    onSuccess: (data) => {
      const usuario = {
        id_usuario: data.id_plomero,
        nombre: data.nombre,
        rol: "plomero",
      };

      localStorage.setItem(
        "plomeria-auth",
        JSON.stringify({
          token: data.access_token,
          usuario,
        })
      );

      setAuth(data.access_token, usuario);
      navigate("/plomero/solicitudes");
    },

    onError: (err) => {
      const details = err.response?.data?.detail;

      if (Array.isArray(details)) {
        setError(details.map((e) => e.msg).join(", "));
      } else {
        setError("Error desconocido");
      }
    },
  });

  /* ───────────────────────────── */
  /* TOGGLE ESPECIALIDADES */
  /* ───────────────────────────── */
  const toggleEspecialidad = (value) => {
    setForm((prev) => {
      const exists = prev.especialidades.includes(value);

      return {
        ...prev,
        especialidades: exists
          ? prev.especialidades.filter((e) => e !== value)
          : [...prev.especialidades, value],
      };
    });
  };

  /* ───────────────────────────── */
  /* SUBMIT */
  /* ───────────────────────────── */
  const handleSubmit = () => {
    setError("");

    if (
      !form.nombre ||
      !form.apellido ||
      !form.email ||
      !form.password ||
      !form.telefono ||
      !form.localidad ||
      !form.direccion      // 👈 NUEVO VALIDATION
    ) {
      return setError("Completá todos los campos obligatorios");
    }

    if (form.especialidades.length === 0) {
      return setError("Seleccioná al menos una especialidad");
    }

    let especialidadesFinal = [...form.especialidades];

    if (
      form.especialidades.includes("OTRA") &&
      otraEspecialidad.trim()
    ) {
      especialidadesFinal = especialidadesFinal.filter(
        (e) => e !== "OTRA"
      );

      especialidadesFinal.push(`OTRA:${otraEspecialidad.trim()}`);
    }

    mut.mutate({
      ...form,
      especialidades: especialidadesFinal,
    });
  };

  /* ───────────────────────────── */
  /* INPUT HELPER */
  /* ───────────────────────────── */
  const input = (placeholder, key, type = "text") => (
    <input
      type={type}
      placeholder={placeholder}
      value={form[key]}
      onChange={(e) =>
        setForm({ ...form, [key]: e.target.value })
      }
      className="w-full border rounded-xl px-4 py-3 text-sm"
    />
  );

  /* ───────────────────────────── */
  /* UI */
  /* ───────────────────────────── */
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 to-emerald-50 flex items-center justify-center p-4">

      <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md p-8">

        <h2 className="text-2xl font-semibold text-center mb-2">
          Registro de plomero
        </h2>

        <p className="text-center text-slate-500 text-sm mb-6">
          Completá tu perfil profesional
        </p>

        {/* FORM */}
        <div className="space-y-4">

          {input("Nombre", "nombre")}
          {input("Apellido", "apellido")}
          {input("Email", "email", "email")}
          {input("Contraseña", "password", "password")}
          {input("Teléfono", "telefono")}

          {/* 👇 NUEVO */}
          {input("Dirección", "direccion")}

          {input("Localidad", "localidad")}

          {/* ESPECIALIDADES */}
          <div className="space-y-2">
            <p className="text-sm font-medium">
              Especialidades
            </p>

            {[
              "PLOMERIA_GENERAL",
              "DESTAPES",
              "GAS_MATRICULADO",
              "OBRA",
              "OTRA",
            ].map((esp) => (
              <label
                key={esp}
                className="flex items-center gap-2"
              >
                <input
                  type="checkbox"
                  checked={form.especialidades.includes(esp)}
                  onChange={() =>
                    toggleEspecialidad(esp)
                  }
                />

                <span className="text-sm">{esp}</span>
              </label>
            ))}

            {/* INPUT OTRA */}
            {form.especialidades.includes("OTRA") && (
              <input
                type="text"
                placeholder="Especificá otra especialidad"
                value={otraEspecialidad}
                onChange={(e) =>
                  setOtraEspecialidad(e.target.value)
                }
                className="w-full border rounded-xl px-4 py-2 text-sm mt-2"
              />
            )}
          </div>

          {/* GENERO */}
          <select
            value={form.genero}
            onChange={(e) =>
              setForm({ ...form, genero: e.target.value })
            }
            className="w-full border rounded-xl px-4 py-3 text-sm"
          >
            <option value="M">Masculino</option>
            <option value="F">Femenino</option>
          </select>

          {/* CHECKS */}
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={form.atiende_urgencias}
              onChange={(e) =>
                setForm({
                  ...form,
                  atiende_urgencias: e.target.checked,
                })
              }
            />
            <span className="text-sm">
              Atiende urgencias (24hs)
            </span>
          </label>

          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={form.matricula_gas}
              onChange={(e) =>
                setForm({
                  ...form,
                  matricula_gas: e.target.checked,
                })
              }
            />
            <span className="text-sm">
              Matrícula de gas
            </span>
          </label>

        </div>

        {/* ERROR */}
        {error && (
          <p className="text-red-500 text-sm text-center mt-4">
            {error}
          </p>
        )}

        {/* BUTTON */}
        <button
          onClick={handleSubmit}
          disabled={mut.isPending}
          className="mt-6 w-full bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-xl font-semibold"
        >
          {mut.isPending
            ? "Registrando..."
            : "Crear cuenta"}
        </button>

      </div>
    </div>
  );
}