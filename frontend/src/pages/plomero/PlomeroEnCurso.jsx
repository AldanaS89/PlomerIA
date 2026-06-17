// import { useQuery } from '@tanstack/react-query'
// import { PlayCircle, MapPin, Phone } from 'lucide-react'
// import PlomeroLayout from '../../components/plomero/PlomeroLayout'
// import { getTrabajosEnCurso } from '../../services/plomeroService'

// export default function PlomeroEnCurso() {
//   const { data: trabajos = [], isLoading } = useQuery({
//     queryKey: ['trabajos-en-curso'],
//     queryFn: getTrabajosEnCurso,
//   })

//   return (
//     <PlomeroLayout>
//       <div className="max-w-2xl mx-auto px-4 py-8">
//         <h1 className="font-display text-2xl font-bold text-slate-800 mb-6">
//           Trabajos en curso
//         </h1>

//         {isLoading && (
//           <div className="space-y-4">
//             {[1, 2].map((i) => (
//               <div key={i} className="bg-white rounded-2xl border border-slate-200 h-32 animate-pulse" />
//             ))}
//           </div>
//         )}

//         {!isLoading && trabajos.length === 0 && (
//           <div className="flex flex-col items-center justify-center py-16 text-slate-400">
//             <PlayCircle className="w-12 h-12 mb-3 opacity-30" />
//             <p className="text-sm">No tenés trabajos en curso</p>
//           </div>
//         )}

//         {!isLoading && trabajos.map((t) => (
//           <div key={t.id} className="bg-white rounded-2xl border border-slate-200 p-5 mb-4 shadow-sm">
//             <div className="flex items-start justify-between mb-3">
//               <div>
//                 <p className="font-semibold text-slate-800">{t.tipo}</p>
//                 <p className="text-sm text-slate-500 flex items-center gap-1 mt-0.5">
//                   <MapPin className="w-3.5 h-3.5" /> {t.direccion}
//                 </p>
//               </div>
//               <span className="text-xs bg-emerald-100 text-emerald-700 font-semibold px-2.5 py-1 rounded-full">
//                 En curso
//               </span>
//             </div>
//             <p className="text-sm text-slate-600 mb-4">"{t.descripcion}"</p>
//             {t.clienteTelefono && (
//               <a
//                 href={`tel:${t.clienteTelefono}`}
//                 className="flex items-center gap-2 text-sm text-brand-600 font-medium hover:underline"
//               >
//                 <Phone className="w-4 h-4" /> Llamar al cliente
//               </a>
//             )}
//           </div>
//         ))}
//       </div>
//     </PlomeroLayout>
//   )
// }
