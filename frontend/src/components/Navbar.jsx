import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

const Navbar = () => {
  const navigate  = useNavigate();
  const location  = useLocation();
  const user      = useAuthStore((s) => s.user);
  const logout    = useAuthStore((s) => s.logout);

  const cerrarSesion = () => {
    logout();
    localStorage.removeItem('plomeria-auth');
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-[#0f172a] text-white px-8 py-4 flex justify-between items-center shadow-lg">
      <div className="flex items-center gap-2">
        <span className="font-black text-xl tracking-tighter">🔧 PlomerIA</span>
      </div>
      <div className="flex gap-8 text-[13px] font-medium items-center">
        <span
          onClick={() => navigate('/cliente')}
          className={`cursor-pointer pb-1 transition-colors ${isActive('/cliente') ? 'border-b-2 border-blue-400' : 'text-slate-400 hover:text-white'}`}
        >
          Inicio
        </span>
        <span
          onClick={() => navigate('/cliente/trabajos')}
          className={`cursor-pointer transition-colors ${isActive('/cliente/trabajos') ? 'border-b-2 border-blue-400 pb-1' : 'text-slate-400 hover:text-white'}`}
        >
          Mis trabajos
        </span>
        <span
          onClick={() => navigate('/cliente/alertas')}
          className="text-slate-400 hover:text-white cursor-pointer relative transition-colors"
        >
          Alertas
          <span className="absolute -top-2 -right-3 bg-red-500 text-[9px] px-1.5 py-0.5 rounded-full ring-2 ring-[#0f172a]">2</span>
        </span>
        <div className="ml-4 flex items-center gap-3 pl-6 border-l border-slate-700">
          <span className="text-slate-300 font-bold">{user?.nombre || 'Usuario'}</span>
          <button
            onClick={cerrarSesion}
            className="bg-red-500/10 text-red-400 px-3 py-1.5 rounded-xl border border-red-500/20 text-xs font-bold hover:bg-red-500 transition-all"
          >
            Cerrar sesión
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;