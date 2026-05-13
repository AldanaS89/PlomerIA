// src/pages/ClienteAlertas.jsx
import Navbar from '../components/Navbar';

export default function ClienteAlertas() {
  return (
    <div className="min-h-screen bg-slate-50 pb-20">
      <Navbar />
      <main className="max-w-2xl mx-auto mt-16 px-4">
        <h1 className="text-3xl font-black text-slate-900 mb-2">Alertas</h1>
        <p className="text-slate-400 mb-8">Notificaciones de tus solicitudes.</p>
        <div className="text-center py-20">
          <div className="text-5xl mb-4">🔔</div>
          <p className="text-slate-400 font-medium">No tenés alertas nuevas</p>
        </div>
      </main>
    </div>
  );
}