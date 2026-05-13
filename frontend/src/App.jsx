import React, { useState } from 'react';
import Login from './pages/Login';
import Registro from './pages/Registro';
import RegistroPlomero from './pages/RegistroPlomero';
import HomeCliente from './pages/HomeCliente';
import OlvidePassword from './pages/OlvidePassword';

export default function App() {
  const [view, setView] = useState("login");

  const handleNav = (nuevaVista) => {
    window.scrollTo(0, 0);
    setView(nuevaVista);
  };

  const handleLogout = () => {
    localStorage.removeItem('plomeria-auth');
    handleNav("login");
  };

  return (
    <>
      {view === "login" && (
        <Login onNav={handleNav} />
      )}
      {view === "registro" && (
        <Registro onNav={handleNav} />
      )}
      {view === "registro-plomero" && (
        <RegistroPlomero onNav={handleNav} />
      )}
      {view === "olvide-password" && (
        <OlvidePassword onNav={handleNav} />
      )}
      {view === "app" && (
        <HomeCliente onLogout={handleLogout} />
      )}
      {view === "plomero" && (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-emerald-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-[2.5rem] shadow-xl p-10 w-full max-w-md border border-slate-100 text-center">
            <div className="flex justify-center mb-6">
              <div className="bg-emerald-600 px-4 py-2 rounded-xl shadow-lg shadow-emerald-100">
                <span className="text-white font-black text-2xl tracking-tighter">
                  🔧 PlomerIA
                </span>
              </div>
            </div>
            <div className="text-5xl mb-4">🔧</div>
            <h2 className="text-2xl font-black text-slate-800 mb-2">
              Panel del Plomero
            </h2>
            <p className="text-slate-400 text-sm mb-2">
              Estamos construyendo tu espacio de trabajo.
            </p>
            <p className="text-slate-300 text-xs mb-8">
              Próximamente podrás ver y gestionar tus solicitudes desde acá.
            </p>
            <button
              onClick={handleLogout}
              className="text-xs text-slate-400 hover:text-slate-600 hover:underline transition-all"
            >
              Cerrar sesión
            </button>
          </div>
        </div>
      )}
    </>
  );
}