import React, { useState } from 'react';
import Login from './pages/Login';
import Registro from './pages/Registro';
import RegistroPlomero from './pages/RegistroPlomero';
import HomeCliente from './pages/HomeCliente';
import HomePlomero from './pages/HomePlomero';
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
      {view === "login" && <Login onNav={handleNav} />}
      {view === "registro" && <Registro onNav={handleNav} />}
      {view === "registro-plomero" && <RegistroPlomero onNav={handleNav} />}
      {view === "olvide-password" && <OlvidePassword onNav={handleNav} />}
      {view === "app" && <HomeCliente onLogout={handleLogout} />}
      {view === "plomero" && <HomePlomero onLogout={handleLogout} />}
    </>
  );
}