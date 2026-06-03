import React from 'react';
import Login from './pages/Login';
import Registro from './pages/Registro';
import RegistroPlomero from './pages/RegistroPlomero';
import HomeCliente from './pages/HomeCliente';
import HomePlomero from './pages/HomePlomero';
import OlvidePassword from './pages/OlvidePassword';
import { useAuthStore } from './store/authStore';

export default function App() {
  const token = useAuthStore(s => s.token);
  const user  = useAuthStore(s => s.user);

  // Determinar la vista inicial según la sesión persistida en localStorage.
  // Zustand persist restaura token y user antes del primer render,
  // así que esta lógica corre con los valores reales desde el inicio.
  const getVistaInicial = () => {
    if (!token || !user) return 'login';
    if (user.rol === 'plomero') return 'plomero';
    return 'app';
  };

  const [view, setView] = React.useState(getVistaInicial);

  const handleNav = (nuevaVista) => {
    window.scrollTo(0, 0);
    setView(nuevaVista);
  };

  const handleLogout = () => {
    localStorage.removeItem('plomeria-auth');
    handleNav('login');
  };

  return (
    <>
      {view === 'login'            && <Login onNav={handleNav} />}
      {view === 'registro'         && <Registro onNav={handleNav} />}
      {view === 'registro-plomero' && <RegistroPlomero onNav={handleNav} />}
      {view === 'olvide-password'  && <OlvidePassword onNav={handleNav} />}
      {view === 'app'              && <HomeCliente onLogout={handleLogout} />}
      {view === 'plomero'          && <HomePlomero onLogout={handleLogout} />}
    </>
  );
}