// src/components/TerminosCondiciones.jsx
// Modal con las Bases y Condiciones de PlomerIA. Se abre desde el Login y los
// registros. Refleja las reglas REALES del sistema (reputación, cancelaciones,
// lenguaje, comisión, etc.) para que cliente y plomero las conozcan de antemano.
import { X } from "lucide-react";

function Seccion({ titulo, children }) {
  return (
    <div className="mb-5">
      <h3 className="text-sm font-black text-slate-800 mb-1.5">{titulo}</h3>
      <div className="text-[13px] text-slate-600 leading-relaxed space-y-1.5">{children}</div>
    </div>
  );
}

export default function TerminosCondiciones({ open, onClose }) {
  if (!open) return null;
  return (
    <div
      className="fixed inset-0 z-[2000] bg-black/50 flex items-center justify-center p-4 font-sans"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-3xl shadow-2xl w-full max-w-lg max-h-[85vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <h2 className="text-lg font-black text-slate-800">📄 Bases y Condiciones</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X size={20} />
          </button>
        </div>

        {/* Contenido scrolleable */}
        <div className="overflow-y-auto px-6 py-5">
          <p className="text-[13px] text-slate-500 mb-5">
            Al usar PlomerIA, clientes y profesionales aceptan estas reglas de
            convivencia. Las reglas valen igual para todos y buscan un trato
            justo y respetuoso entre las partes.
          </p>

          <Seccion titulo="1. Reputación y calificaciones">
            <p>
              Toda cuenta arranca con <b>5,0 estrellas</b>. Al finalizar un
              trabajo, cliente y profesional se califican mutuamente. La
              calificación es <b>bidireccional</b>: tu reputación depende de cómo
              te evalúa la otra parte.
            </p>
            <p>
              Tenés <b>48 horas</b> para calificar. Si no lo hacés en ese plazo,
              el sistema registra <b>5 estrellas automáticas</b> y cierra el
              trabajo (vale igual para cliente y profesional).
            </p>
          </Seccion>

          <Seccion titulo="2. Cancelaciones">
            <p>
              Cancelar un trabajo <b>ya aceptado</b> aplica una penalización en
              estrellas. La penalización es menor si avisaste por el chat y con
              anticipación, y mayor si cancelaste sin avisar o sobre la hora.
            </p>
            <p>
              Si acumulás <b>3 cancelaciones consecutivas</b> de trabajos ya
              aceptados, la cuenta se <b>suspende por 2 meses</b> y se reactiva
              automáticamente al cumplirse el plazo. Completar un trabajo sin
              cancelar reinicia el contador.
            </p>
          </Seccion>

          <Seccion titulo="3. Lenguaje y respeto">
            <p>
              El chat <b>censura automáticamente</b> las malas palabras (se
              muestran con asteriscos). El uso de lenguaje ofensivo genera un
              <b> aviso</b>; al <b>tercer</b> mensaje ofensivo la cuenta se
              <b> suspende por 1 mes</b>, con reactivación automática.
            </p>
          </Seccion>

          <Seccion titulo="4. Comisión de la plataforma (profesionales)">
            <p>
              Por cada trabajo facturado, el profesional deja una
              <b> comisión del 15%</b> a PlomerIA. El resto es su ganancia neta.
              El panel del profesional muestra la ganancia estimada ya con la
              comisión descontada.
            </p>
          </Seccion>

          <Seccion titulo="5. Boleta y cierre del trabajo (profesionales)">
            <p>
              El profesional <b>debe entregar la boleta</b> con el detalle de lo
              gastado (materiales) y lo cobrado (mano de obra). El cliente la ve
              en todo momento. <b>No se puede finalizar un trabajo sin cargar la
              boleta.</b>
            </p>
            <p>
              Si un trabajo queda <b>sin cerrar y su fecha ya pasó</b>, el
              profesional <b>no puede tomar nuevos trabajos</b> hasta finalizarlo
              y cargar su boleta. (Los trabajos futuros ya aceptados no se ven
              afectados.)
            </p>
          </Seccion>

          <Seccion titulo="6. Coordinación y reprogramación">
            <p>
              El chat se habilita mientras el trabajo está en curso. Para
              <b> reprogramar</b> el horario debe haber <b>comunicación previa</b>
              entre ambas partes por el chat: no se puede cambiar la fecha de
              forma unilateral.
            </p>
          </Seccion>

          <Seccion titulo="7. Urgencias">
            <p>
              En un pedido <b>urgente</b>, los profesionales tienen 30 minutos
              para responder; en un pedido normal, 3 horas. Si nadie acepta, el
              cliente puede volver a buscar otros profesionales o cancelar.
            </p>
          </Seccion>

          <Seccion titulo="8. Privacidad">
            <p>
              La dirección del cliente se muestra al profesional únicamente
              mientras debe ir al domicilio. Una vez finalizado el trabajo, la
              dirección deja de mostrarse.
            </p>
          </Seccion>

          <p className="text-[11px] text-slate-400 mt-4">
            PlomerIA — Documento de referencia del usuario. Las reglas pueden
            actualizarse; la versión vigente es la que figura en la aplicación.
          </p>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-100">
          <button
            onClick={onClose}
            className="w-full bg-[#0f172a] text-white font-black py-3 rounded-2xl uppercase text-xs tracking-[0.2em] hover:bg-blue-600 transition-all"
          >
            Entendido
          </button>
        </div>
      </div>
    </div>
  );
}
