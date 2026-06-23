# services/notificacion_service.py
"""
Responsabilidad única: notificar a plomeros sobre nuevas solicitudes.
Si mañana queremos agregar push notifications o SMS, solo tocamos este archivo.
"""
from utils.email import enviar_solicitud_plomero

class NotificacionService:
    """
    Patrón Strategy implícito: en el futuro se puede inyectar
    otro canal (SMS, push) sin tocar SolicitudService.
    """
    def notificar_plomeros(
        self,
        plomeros: list,
        solicitud_id: int,
        descripcion: str,
        diagnostico: dict,
    ) -> int:
        """
        Notifica a cada plomero y devuelve cuántos fueron notificados.
        Los errores individuales no detienen el proceso.
        """
        notificados = 0
        for plomero in plomeros:
            try:
                enviar_solicitud_plomero(
                    plomero_email   = plomero.email,
                    plomero_nombre  = plomero.nombre,
                    solicitud_id    = solicitud_id,
                    descripcion     = descripcion,
                    diagnostico     = diagnostico["etiqueta_ia"],
                    urgencia        = diagnostico["urgencia_ia"],
                    presupuesto_min = diagnostico["presupuesto_min"],
                    presupuesto_max = diagnostico["presupuesto_max"],
                )
                notificados += 1
            except Exception as e:
                print(f"[NotificacionService] Error notificando {plomero.email}: {e}")
        return notificados

# Instancia singleton — se importa desde otros services
notificacion_service = NotificacionService()