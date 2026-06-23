import { Star } from 'lucide-react';
import { useState } from 'react';

const ModalCalificacion = ({ plomeroNombre, onEnviar }) => {
  const [rating, setRating] = useState(0);
  const [hover, setHover] = useState(0);

  return (
    <div className="bg-white p-8 rounded-[2.5rem] shadow-2xl max-w-sm w-full text-center border border-slate-100">
      <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4 text-3xl">
        ⭐
      </div>
      <h3 className="text-xl font-bold text-slate-800">¿Cómo fue el servicio?</h3>
      <p className="text-slate-400 text-sm mb-6">Tu reseña ayuda a {plomeroNombre} y a la comunidad.</p>
      
      {/* Estrellas Interactivas */}
      <div className="flex justify-center gap-2 mb-6">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            onMouseEnter={() => setHover(star)}
            onMouseLeave={() => setHover(0)}
            onClick={() => setRating(star)}
          >
            <Star 
              size={32} 
              fill={(hover || rating) >= star ? "#fbbf24" : "none"} 
              className={(hover || rating) >= star ? "text-amber-400" : "text-slate-200"}
            />
          </button>
        ))}
      </div>

      <textarea 
        placeholder="Contanos un poco más (opcional)..."
        className="w-full bg-slate-50 border border-slate-100 rounded-2xl p-4 text-sm mb-6 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      <button 
        onClick={() => onEnviar(rating)}
        disabled={rating === 0}
        className={`w-full py-4 rounded-2xl font-bold transition-all ${
          rating > 0 ? 'bg-blue-600 text-white shadow-lg shadow-blue-200' : 'bg-slate-100 text-slate-400 cursor-not-allowed'
        }`}
      >
        Enviar reseña
      </button>
    </div>
  );
};