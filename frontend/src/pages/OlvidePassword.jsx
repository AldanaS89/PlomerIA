const OlvidePassword = () => {
  const [email, setEmail] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Tus rutas diferencian usuario/plomero, podrías necesitar un selector o probar ambos
      await api.post('/usuarios/olvide-password', { email });
      alert("Si el correo existe, recibirás un link de recuperación.");
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6 font-sans">
      <div className="bg-white p-10 rounded-[2.5rem] shadow-xl w-full max-w-md text-center border border-slate-100">
        <div className="text-4xl mb-4">🔑</div>
        <h2 className="text-2xl font-black text-slate-800 mb-2">Recuperar acceso</h2>
        <p className="text-slate-400 text-sm mb-8">Te enviaremos un código para restablecer tu contraseña.</p>
        <form onSubmit={handleSubmit}>
          <input 
            type="email" 
            placeholder="Ingresá tu email" 
            className="w-full p-4 bg-slate-50 border border-slate-200 rounded-2xl mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
            onChange={(e) => setEmail(e.target.value)}
          />
          <button className="w-full bg-blue-600 text-white font-black py-4 rounded-2xl shadow-lg shadow-blue-100 hover:bg-blue-700 transition-all uppercase text-xs tracking-widest">
            Enviar link de reset
          </button>
        </form>
      </div>
    </div>
  );
};