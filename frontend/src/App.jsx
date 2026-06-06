import React, { useEffect } from 'react'; 
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

  // 1. Dejamos que la vista inicial arranque con la lógica normal
  const getVistaInicial = () => {
    if (!token || !user) return 'login';
    if (user.rol === 'plomero') return 'plomero';
    return 'app';
  };

  const [view, setView] = React.useState(getVistaInicial);

   // Esto corre apenas carga la app en el navegador
  useEffect(() => {
    const parametros = new URLSearchParams(window.location.search);
    
    if (parametros.get('logout') === 'true') {
      // Borramos el token de Zustand/localStorage por la fuerza
      localStorage.removeItem('plomeria-auth'); 
      
      // Limpiamos la URL para que quede impecable en la exposición
      window.history.replaceState({}, document.title, window.location.pathname);
      
      // Forzamos a React a cambiar la pantalla a 'login' en vivo
      setView('login');
    }
  }, []); // El array vacío asegura que corra una sola vez al cargar

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