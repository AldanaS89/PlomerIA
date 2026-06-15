// src/pages/ClienteMisTrabajos.jsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import Navbar from '../components/Navbar';

const estadoConfig = {
  pendiente:  { label: 'Pendiente',  cls: 'bg-amber-100 text-amber-700' },
  aceptado:   { label: 'Aceptado',   cls: 'bg-blue-100 text-blue-700' },
  completado: { label: 'Completado', cls: 'bg-emerald-100 text-emerald-700' },
  rechazado:  { label: 'Rechazado',  cls: 'bg-red-100 text-red-700' },
};

export default function ClienteMisTrabajos() {
  const navigate = useNavigate();
  const [solicitudes, setSolicitudes] = useState([]);
  const [cargando,    setCargando]    = useState(true);

  useEffect(() => {
    api.get('/usuarios/perfil')
      .then(() => api.get('/solicitudes/mis-solicitudes'))
      .then((res) => setSolicitudes(Array.isArray(res.data) ? res.data : []))
      .catch(() => setSolicitudes([]))
      .finally(() => setCargando(false));
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 pb-20">
      <Navbar />
      <main className="max-w-2xl mx-auto mt-16 px-4">
        <h1 className="text-3xl font-black text-slate-900 mb-2">Mis trabajos</h1>
        <p className="text-slate-400 mb-8">Historial de todas tus solicitudes.</p>

        {cargando && (
          <div className="space-y-3">
            {[1,2,3].map((i) => (
              <div key={i} className="bg-white rounded-2xl h-24 animate-pulse border border-slate-100"/>
            ))}
          </div>
        )}

        {!cargando && solicitudes.length === 0 && (
          <div className="text-center py-20">
            <div className="text-5xl mb-4">📋</div>
            <p className="text-slate-400 font-medium">Todavía no hiciste ninguna solicitud</p>
            <button
              onClick={() => navigate('/cliente')}
              className="mt-6 bg-blue-600 text-white px-6 py-3 rounded-2xl font-bold text-sm hover:bg-blue-700 transition-all"
            >
              Buscar un plomero →
            </button>
          </div>
        )}

        <div className="space-y-4">
          {solicitudes.map((s) => {
            const est = estadoConfig[s.estado?.toLowerCase()] ?? { label: s.estado, cls: 'bg-slate-100 text-slate-600' };
            return (
              <div key={s.id_solicitud} className="bg-white rounded-[2rem] border border-slate-100 p-6 shadow-sm">
                <div className="flex items-start justify-between mb-3">
                  <span className="font-black text-slate-800">Solicitud #{s.id_solicitud}</span>
                  <span className={`text-xs font-bold px-3 py-1 rounded-full ${est.cls}`}>{est.label}</span>
                </div>
                <p className="text-sm text-slate-500 mb-3 line-clamp-2">"{s.descripcion_raw}"</p>
                <div className="flex flex-wrap gap-3 text-xs text-slate-400">
                  {s.localidad_evento && (
                    <span>📍 {s.localidad_evento}</span>
                  )}
                  {s.fecha && (
                    <span>🕐 {new Date(s.fecha).toLocaleDateString('es-AR')}</span>
                  )}
                  {s.nombre_plomero && (
                    <span className="text-blue-500 font-bold">👷 {s.nombre_plomero}</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </main>
    </div>
  );
}