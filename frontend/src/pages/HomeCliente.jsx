import { useState } from 'react';
import api from '../services/api';
import Navbar from '../components/Navbar';

const HomeCliente = () => {
  const [desc, setDesc] = useState('');
  const [loading, setLoading] = useState(false);
  const [resultado, setResultado] = useState(null); // <--- NUEVO: Para guardar la respuesta

  const obtenerUbicacion = () => {
    return new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(
        (pos) => resolve(pos),
        (err) => reject(err),
        { timeout: 5000 }
      );
    });
  };

  const enviarPedido = async () => {
    setLoading(true);
    setResultado(null); // Limpiamos resultados anteriores
    try {
      let lat = -34.85; 
      let lon = -58.38;

      try {
        const pos = await obtenerUbicacion();
        lat = pos.coords.latitude;
        lon = pos.coords.longitude;
      } catch (e) { console.log("Usando ubicación default"); }

      const res = await api.post('/solicitudes/', {
        descripcion_raw: desc,
        localidad_evento: "Detección automática",
        latitud_evento: lat,
        longitud_evento: lon,
        solo_mujeres: false
      });

      // --- PASO CLAVE: Guardamos la respuesta en el estado ---
      setResultado(res.data); 
      setDesc('');
      
    } catch (err) {
      alert("Error al procesar la solicitud");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 pb-20">
      <Navbar usuario="María" />
      <main className="max-w-2xl mx-auto mt-16 px-4">
        <h1 className="text-4xl font-black text-slate-900 mb-2 text-center">¿Qué problema tenés?</h1>
        <p className="text-slate-400 mb-10 text-center">Nuestra IA encontrará al profesional ideal cerca tuyo.</p>

        {/* Input */}
        <div className="bg-white p-8 rounded-[2.5rem] shadow-sm border border-slate-100 mb-8">
          <textarea 
            value={desc}
            onChange={(e) => setDesc(e.target.value)}
            placeholder="Ej: Tengo una pérdida en el termotanque..."
            className="w-full h-32 p-5 bg-slate-50 border border-slate-100 rounded-3xl focus:outline-none resize-none"
          />
          <button 
            onClick={enviarPedido}
            disabled={loading || desc.length < 5}
            className="w-full mt-4 bg-[#0f172a] text-white py-4 rounded-2xl font-black uppercase text-xs tracking-widest hover:bg-blue-600 transition-all disabled:opacity-20"
          >
            {loading ? 'Buscando plomeros...' : 'Buscar profesionales →'}
          </button>
        </div>

        {/* --- LISTA DE RESULTADOS --- */}
        {resultado && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <h2 className="text-xl font-black text-slate-800 mb-4 ml-2">Plomeros recomendados</h2>
            <div className="space-y-4">
              {resultado.plomeros_sugeridos_detallados.map((plomero) => (
                <div key={plomero.id} className="bg-white p-6 rounded-[2rem] border border-slate-100 shadow-sm flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-14 h-14 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center text-2xl font-bold">
                      {plomero.nombre[0]}
                    </div>
                    <div>
                      <h3 className="font-black text-slate-800">{plomero.nombre}</h3>
                      <p className="text-xs text-slate-400 font-bold uppercase">{plomero.localidad}</p>
                      <div className="flex items-center gap-1 mt-1 text-amber-500">
                        <span className="text-xs font-black">⭐ {plomero.calificacion || "Nuevo"}</span>
                      </div>
                    </div>
                  </div>
                  <button className="bg-blue-600 text-white px-6 py-2 rounded-xl font-black text-[10px] uppercase shadow-lg shadow-blue-100">
                    Contactar
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default HomeCliente;