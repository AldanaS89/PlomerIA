import React, { useState, useEffect } from 'react';
// Importamos tus páginas desde la carpeta /pages
import Login from './pages/Login';
import Registro from './pages/Registro';
import RegistroPlomero from './pages/RegistroPlomero';
import HomeCliente from './pages/HomeCliente';
import OlvidePassword from './pages/OlvidePassword';

export default function App() {
  // 1. Estados principales
  const [view, setView] = useState("login"); // Controla la navegación
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // 2. Persistencia de sesión (opcional por ahora)
  useEffect(() => {
    const auth = localStorage.getItem('plomeria-auth');
    if (auth) {
      try {
        const parsed = JSON.parse(auth);
        setUser(parsed.state.user);
        setView("app");
      } catch (e) {
        localStorage.removeItem('plomeria-auth');
      }
    }
    setLoading(false);
  }, []);

  // 3. Funciones de navegación para pasar a los hijos
  const handleNav = (nuevaVista) => {
    window.scrollTo(0, 0); // Reset de scroll al cambiar de página
    setView(nuevaVista);
  };

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <p className="text-slate-400 animate-pulse font-bold">Cargando PlomerIA...</p>
    </div>
  );

  // 4. Renderizado condicional
  return (
    <>
      {/* Vistas de Acceso */}
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
      
      {/* Vista Principal (App) */}
      {view === "app" && (
        <HomeCliente 
          onLogout={() => {
            localStorage.removeItem('plomeria-auth');
            handleNav("login");
          }} 
        />
      )}
    </>
  );
}