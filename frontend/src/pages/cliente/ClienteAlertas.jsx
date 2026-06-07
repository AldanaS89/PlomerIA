// import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
// import { Bell, CheckCircle } from 'lucide-react'
// import ClienteLayout from '../../components/cliente/ClienteLayout'
// // import { getAlertas } from '../../services/clienteService'
// import api from '../../services/api'

// export default function ClienteAlertas() {
//   const qc = useQueryClient()
//   const { data: alertas = [], isLoading } = useQuery({
//     queryKey: ['alertas'],
//     queryFn: getAlertas,
//   })

//   const marcarLeida = useMutation({
//     mutationFn: (id) => api.patch(`/cliente/alertas/${id}/leida`),
//     onSuccess: () => qc.invalidateQueries({ queryKey: ['alertas'] }),
//   })

//   return (
//     <ClienteLayout>
//       <div className="max-w-2xl mx-auto px-4 py-8">
//         <h1 className="font-display text-2xl font-bold text-slate-800 mb-6">Alertas</h1>

//         {isLoading && (
//           <div className="space-y-3">
//             {[1, 2].map((i) => (
//               <div key={i} className="bg-white rounded-2xl border border-slate-200 h-16 animate-pulse" />
//             ))}
//           </div>
//         )}

//         {!isLoading && alertas.length === 0 && (
//           <div className="flex flex-col items-center justify-center py-16 text-slate-400">
//             <Bell className="w-12 h-12 mb-3 opacity-30" />
//             <p className="text-sm">No tenés alertas nuevas</p>
//           </div>
//         )}

//         {!isLoading && alertas.map((a) => (
//           <div
//             key={a.id}
//             className={`bg-white rounded-2xl border p-4 mb-3 shadow-sm flex items-start gap-3 ${
//               a.leida ? 'border-slate-200 opacity-60' : 'border-brand-200'
//             }`}
//           >
//             <Bell className={`w-5 h-5 mt-0.5 shrink-0 ${a.leida ? 'text-slate-300' : 'text-brand-500'}`} />
//             <div className="flex-1 min-w-0">
//               <p className="text-sm text-slate-800">{a.mensaje}</p>
//               <p className="text-xs text-slate-400 mt-0.5">{a.fecha}</p>
//             </div>
//             {!a.leida && (
//               <button
//                 onClick={() => marcarLeida.mutate(a.id)}
//                 className="text-slate-400 hover:text-emerald-500 transition-colors"
//                 title="Marcar como leída"
//               >
//                 <CheckCircle className="w-5 h-5" />
//               </button>
//             )}
//           </div>
//         ))}
//       </div>
//     </ClienteLayout>
//   )
// }
