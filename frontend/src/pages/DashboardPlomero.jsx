import { useState, useEffect } from 'react';
import api from '../services/api';
import Navbar from '../components/Navbar';
import { MapPin, AlertTriangle, Check, X } from 'lucide-react';

const DashboardPlomero = () => {
  const [solicitudes, setSolicitudes] = useState([]);

  useEffect(() => {
    const fetchSolicitudes = async () => {
      const res = await api.get('/solicitudes/plomero/me'); // Tu endpoint de "Mis Solicitudes"
      setSolicitudes(res.data);
    };
    fetchSolicitudes();
  }, []);

  const responder = async (id, accion) => {
    try {
      await api.patch(`/solicitudes/${id}/responder?accion=${accion}`);
      setSolicitudes(solicitudes.filter(s => s.id_solicitud !== id));
      alert(accion === 'aceptar' ? "Trabajo aceptado" : "Rechazado");
    } catch (err) {
      alert("Error al responder");
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar usuario="Carlos Mendoza" />
      <div className="max-w-xl mx-auto mt-12 px-4">
        <h2 className="text-2xl font-black mb-8 text-center">Solicitudes entrantes</h2>
        {solicitudes.map(sol => (
          <div key={sol.id_solicitud} className="bg-white border-2 border-red-50 rounded-[2.5rem] p-8 shadow-xl mb-6">
            <div className="flex gap-2 mb-4">
              <span className="bg-red-50 text-red-500 text-[10px] font-black px-3 py-1 rounded-full uppercase">Urgente</span>
            </div>
            <p className="text-slate-600 mb-6 text-sm">{sol.descripcion_raw}</p>
            <div className="grid grid-cols-2 gap-4">
              <button onClick={() => responder(sol.id_solicitud, 'rechazar')} className="border-2 border-slate-100 text-slate-400 font-bold py-3 rounded-2xl">Rechazar</button>
              <button onClick={() => responder(sol.id_solicitud, 'aceptar')} className="bg-emerald-500 text-white font-bold py-3 rounded-2xl">Aceptar trabajo</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DashboardPlomero;