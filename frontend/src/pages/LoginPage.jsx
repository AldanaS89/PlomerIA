import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";

import { Eye, EyeOff, Wrench, Home, X, CheckCircle2 } from "lucide-react";

import { login, register, olvidarPassword } from "../services/authService";

import { useAuthStore } from "../store/authStore";

// ─────────────────────────────────────────────
// Modal recuperar contraseña
// ─────────────────────────────────────────────
function ForgotPasswordModal({ onClose }) {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [err, setErr] = useState("");

  const mut = useMutation({
    mutationFn: olvidarPassword,

    onSuccess: () => setSent(true),

    onError: () => {
      setErr("No se pudo enviar el email");
    },
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-600"
        >
          <X className="w-5 h-5" />
        </button>

        {sent ? (
          <div className="text-center py-4">
            <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3" />

            <h3 className="font-semibold text-lg mb-2">¡Listo!</h3>

            <p className="text-sm text-slate-500">
              Revisá tu email para continuar.
            </p>

            <button
              onClick={onClose}
              className="mt-5 w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-xl"
            >
              Cerrar
            </button>
          </div>
        ) : (
          <>
            <h3 className="font-semibold text-lg mb-4">Recuperar contraseña</h3>

            <input
              type="email"
              placeholder="tu@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border rounded-xl px-4 py-3 text-sm"
            />

            {err && <p className="text-red-500 text-sm mt-2">{err}</p>}

            <button
              onClick={() => mut.mutate(email)}
              className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-xl"
            >
              {mut.isPending ? "Enviando..." : "Enviar link"}
            </button>
          </>
        )}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────
// Login principal
// ─────────────────────────────────────────────
export default function LoginPage() {
  const navigate = useNavigate();

  const setAuth = useAuthStore((s) => s.setAuth);

  const [mode, setMode] = useState("login");

  const [showPass, setShowPass] = useState(false);

  const [showForgot, setShowForgot] = useState(false);

  const [error, setError] = useState("");

  const [form, setForm] = useState({
    nombre: "",
    apellido: "",
    email: "",
    password: "",
    direccion: "",
    localidad: "",
    telefono: "",
  });

  const isRegister = mode.startsWith("register");

  const rolRegistro = mode === "register-plomero" ? "plomero" : "cliente";

  // ─────────────────────────────────────────
  // LOGIN
  // ─────────────────────────────────────────
  // En LoginPage.jsx — reemplazar loginMut
  const loginMut = useMutation({
    mutationFn: async ({ email, password }) => {
      // Intenta login como usuario primero
      try {
        return await login({ email, password });
      } catch {
        // Si falla, intenta como plomero
        return await loginPlomero({ email, password });
      }
    },
    onSuccess: (data) => {
      const usuario = {
        id: data.id_usuario ?? data.id_plomero,
        nombre: data.nombre,
        rol: data.rol ?? (data.id_plomero ? "plomero" : "cliente"),
      };
      localStorage.setItem(
        "plomeria-auth",
        JSON.stringify({
          token: data.access_token,
          usuario,
        }),
      );
      setAuth(data.access_token, usuario);
      navigate(usuario.rol === "plomero" ? "/plomero/solicitudes" : "/cliente");
    },
    onError: () => setError("Email o contraseña incorrectos"),
  });

  // ─────────────────────────────────────────
  // REGISTER
  // ─────────────────────────────────────────
  const registerMut = useMutation({
    mutationFn: register,

    onSuccess: (data) => {
      const usuario = {
        id_usuario: data.id_usuario,
        nombre: data.nombre,
        rol: data.rol,
      };

      localStorage.setItem(
        "plomeria-auth",
        JSON.stringify({
          token: data.access_token,
          usuario,
        }),
      );

      setAuth(data.access_token, usuario);

      navigate(data.rol === "plomero" ? "/plomero/solicitudes" : "/cliente");
    },

    onError: (err) => {
      console.error(err);

      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("No se pudo crear la cuenta");
      }
    },
  });

  // ─────────────────────────────────────────
  // SUBMIT
  // ─────────────────────────────────────────
  const handleSubmit = () => {
    setError("");

    if (!form.email || !form.password) {
      return setError("Completá email y contraseña");
    }

    if (isRegister) {
      if (
        !form.nombre ||
        !form.apellido ||
        !form.direccion ||
        !form.localidad ||
        !form.telefono
      ) {
        return setError("Completá todos los campos");
      }

      registerMut.mutate({
        ...form,
        rol: rolRegistro,
      });
    } else {
      loginMut.mutate({
        email: form.email,
        password: form.password,
      });
    }
  };

  const isPending = loginMut.isPending || registerMut.isPending;

  return (
    <>
      {showForgot && (
        <ForgotPasswordModal onClose={() => setShowForgot(false)} />
      )}

      <div className="min-h-screen bg-gradient-to-br from-slate-100 to-blue-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md p-8">
          {/* Logo */}
          <div className="flex items-center justify-center gap-3 mb-6">
            <div className="w-11 h-11 bg-blue-600 rounded-2xl flex items-center justify-center">
              <Wrench className="w-5 h-5 text-white" />
            </div>

            <h1 className="text-3xl font-bold">
              Plomer<span className="text-blue-600">IA</span>
            </h1>
          </div>

          {/* Header */}
          <h2 className="text-center text-2xl font-semibold text-slate-800">
            {isRegister ? "Crear cuenta" : "Bienvenido"}
          </h2>

          <p className="text-center text-slate-500 text-sm mt-1 mb-6">
            {isRegister
              ? `Registro como ${rolRegistro}`
              : "Ingresá para continuar"}
          </p>

          {/* Formulario */}
          <div className="space-y-4">
            {isRegister && (
              <>
                <input
                  type="text"
                  placeholder="Nombre"
                  value={form.nombre}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      nombre: e.target.value,
                    })
                  }
                  className="w-full border rounded-xl px-4 py-3"
                />

                <input
                  type="text"
                  placeholder="Apellido"
                  value={form.apellido}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      apellido: e.target.value,
                    })
                  }
                  className="w-full border rounded-xl px-4 py-3"
                />

                <input
                  type="text"
                  placeholder="Dirección"
                  value={form.direccion}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      direccion: e.target.value,
                    })
                  }
                  className="w-full border rounded-xl px-4 py-3"
                />

                <input
                  type="text"
                  placeholder="Localidad"
                  value={form.localidad}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      localidad: e.target.value,
                    })
                  }
                  className="w-full border rounded-xl px-4 py-3"
                />

                <input
                  type="text"
                  placeholder="Teléfono"
                  value={form.telefono}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      telefono: e.target.value,
                    })
                  }
                  className="w-full border rounded-xl px-4 py-3"
                />
              </>
            )}

            <input
              type="email"
              placeholder="Email"
              value={form.email}
              onChange={(e) =>
                setForm({
                  ...form,
                  email: e.target.value,
                })
              }
              className="w-full border rounded-xl px-4 py-3"
            />

            <div className="relative">
              <input
                type={showPass ? "text" : "password"}
                placeholder="Contraseña"
                value={form.password}
                onChange={(e) =>
                  setForm({
                    ...form,
                    password: e.target.value,
                  })
                }
                className="w-full border rounded-xl px-4 py-3 pr-10"
              />

              <button
                type="button"
                onClick={() => setShowPass(!showPass)}
                className="absolute right-3 top-1/2 -translate-y-1/2"
              >
                {showPass ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>

          {!isRegister && (
            <div className="text-right mt-2">
              <button
                onClick={() => setShowForgot(true)}
                className="text-sm text-blue-600 hover:underline"
              >
                ¿Olvidaste tu contraseña?
              </button>
            </div>
          )}

          {error && (
            <p className="text-red-500 text-sm text-center mt-4">{error}</p>
          )}

          <button
            onClick={handleSubmit}
            disabled={isPending}
            className="mt-6 w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-xl font-semibold"
          >
            {isPending
              ? "Cargando..."
              : isRegister
                ? "Crear cuenta"
                : "Ingresar"}
          </button>

          {!isRegister ? (
            <>
              <p className="text-center text-sm text-slate-400 mt-6 mb-3">
                ¿Primera vez?
              </p>

              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => setMode("register-cliente")}
                  className="border rounded-2xl p-4 hover:border-blue-500"
                >
                  <Home className="mx-auto mb-2 text-blue-600" />

                  <p className="font-semibold text-blue-600">Cliente</p>
                </button>

                <button
                  onClick={() => navigate("/registro-plomero")}
                  className="border rounded-2xl p-4 hover:border-emerald-500"
                >
                  <Wrench className="mx-auto mb-2 text-emerald-600" />
                  <p className="font-semibold text-emerald-600">Plomero</p>
                </button>
              </div>
            </>
          ) : (
            <p className="text-center text-sm mt-5">
              ¿Ya tenés cuenta?{" "}
              <button
                onClick={() => {
                  setMode("login");
                  setError("");
                }}
                className="text-blue-600 hover:underline font-semibold"
              >
                Ingresá
              </button>
            </p>
          )}
        </div>
      </div>
    </>
  );
}
