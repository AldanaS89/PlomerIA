import { useEffect, useState } from 'react';
import api from '../services/api';

const DashboardPlomero = () => {
  const [pedidos, setPedidos] = useState([]);
  const [loading, setLoading] = useState(true);

  // Cargar pedidos al inicio
  useEffect(() => {
    fetchPedidos();
  }, []);

  const fetchPedidos = async () => {
    try {
      const res = await api.get('/solicitudes/plomero/me');
      setPedidos(res.data);
    } catch (err) {
      console.error("Error al cargar pedidos", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAccion = async (idSolicitud, accion) => {
    try {
      // Coincide con tu @router.patch("/{id_solicitud}/responder")
      const res = await api.patch(`/solicitudes/${idSolicitud}/responder?accion=${accion}`);
      
      alert(res.data.mensaje);

      // Actualizamos la lista local: 
      // Si aceptó, marcamos como aceptado. Si rechazó, lo quitamos de la vista.
      if (accion === 'aceptar') {
        setPedidos(pedidos.map(p => 
          p.id_solicitud === idSolicitud ? { ...p, estado: 'aceptado' } : p
        ));
      } else {
        setPedidos(pedidos.filter(p => p.id_solicitud !== idSolicitud));
      }
    } catch (err) {
      alert(err.response?.data?.detail || "Error al procesar la solicitud");
    }
  };

  if (loading) return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-slate-50">
      <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
      <p className="font-black text-slate-400 uppercase tracking-widest text-xs">Buscando trabajos...</p>
    </div>
  );

  return (
    <div className="p-6 bg-slate-50 min-h-screen">
      <div className="max-w-4xl mx-auto">
        <header className="mb-10">
          <h1 className="text-3xl font-black text-slate-900 tracking-tighter">Panel de Trabajo</h1>
          <p className="text-slate-500 font-medium">Estas son las solicitudes que coinciden con tu perfil.</p>
        </header>

        {pedidos.length === 0 ? (
          <div className="bg-white p-12 rounded-[3rem] text-center border border-dashed border-slate-300">
            <p className="text-slate-400 font-bold uppercase tracking-widest text-sm">No hay solicitudes nuevas por ahora</p>
          </div>
        ) : (
          <div className="grid gap-6">
            {pedidos.map(p => (
              <div 
                key={p.id_solicitud} 
                className={`bg-white p-8 rounded-[2.5rem] shadow-sm border transition-all ${
                  p.estado === 'aceptado' ? 'border-emerald-200 bg-emerald-50/30' : 'border-slate-100'
                }`}
              >
                <div className="flex justify-between items-start mb-4">
                  <span className={`text-[10px] font-black px-4 py-1.5 rounded-full uppercase tracking-widest ${
                    p.estado === 'aceptado' ? 'bg-emerald-100 text-emerald-600' : 'bg-blue-100 text-blue-600'
                  }`}>
                    {p.estado === 'aceptado' ? '✅ Trabajo Tomado' : '⚡ Nuevo Pedido'}
                  </span>
                  <span className="text-[10px] font-bold text-slate-300 uppercase tracking-widest">
                    ID #{p.id_solicitud}
                  </span>
                </div>

                <h3 className="text-xl font-bold text-slate-800 mb-2 leading-tight">
                  {p.descripcion_raw}
                </h3>
                
                <div className="flex flex-wrap items-center gap-4 mt-6">
                  <div className="flex items-center gap-2 text-slate-500">
                    <span className="text-lg">📍</span>
                    <span className="text-xs font-bold uppercase tracking-tight">{p.localidad_evento}</span>
                  </div>
                </div>

                <div className="mt-8 pt-6 border-t border-slate-50 flex gap-3">
                  {p.estado !== 'aceptado' ? (
                    <>
                      <button 
                        onClick={() => handleAccion(p.id_solicitud, 'aceptar')}
                        className="flex-1 bg-[#0f172a] text-white py-4 rounded-2xl font-black text-xs uppercase tracking-widest hover:bg-emerald-600 transition-all shadow-lg shadow-slate-200"
                      >
                        Aceptar Trabajo
                      </button>
                      <button 
                        onClick={() => handleAccion(p.id_solicitud, 'rechazar')}
                        className="px-6 py-4 rounded-2xl font-black text-xs uppercase tracking-widest text-slate-400 hover:bg-red-50 hover:text-red-500 transition-all"
                      >
                        Ignorar
                      </button>
                    </>
                  ) : (
                    <div className="w-full text-center p-2 bg-emerald-100 text-emerald-700 rounded-xl font-black text-xs uppercase tracking-widest">
                      Ya estás asignado a este trabajo
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPlomero;