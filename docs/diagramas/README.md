# Diagramas — PlomerIA

Los diagramas se ven **renderizados** al abrir el enlace (no como código).

## Diagrama de flujo (por sub-flujo)

1. [Acceso, registro y recuperación de clave](0_flujo_acceso.drawio.svg)
2. [Búsqueda y solicitud (cliente)](1_flujo_busqueda_solicitud.svg)
3. [Ciclo de aceptación / reasignación](2_ciclo_aceptacion.drawio.svg)
4. [Trabajo, finalización y calificación](3_Trabajo_finalizacioin_calificacion.drawio.svg)
5. [Cancelación y penalidades](4_cancelacion_penalidades.drawio.svg)
6. [Panel del plomero](5_flujo_plomero.drawio.svg)
7. [Moderación de lenguaje y suspensiones](6_moderacion_lenguaje_suspension.drawio.svg)

## Otros diagramas

- 🏛️ [UML de clases](Diagrama_UML.drawio.svg) — Modelo de dominio: herencia, contrato abstracto, entidades y relaciones.
- 🧩 [Casos de uso](Casos_de_uso.drawio.svg) — Cliente, Plomero y Sistema/IA.

---

## Estados de la solicitud

Máquina de estados (se ve renderizada acá mismo en GitHub):

```mermaid
stateDiagram-v2
    [*] --> PENDIENTE
    PENDIENTE --> EN_PROGRESO : un profesional acepta
    PENDIENTE --> PENDIENTE : reasignar (máx 3 rondas)
    PENDIENTE --> SIN_RESPUESTA : nadie acepta o vence el plazo
    PENDIENTE --> CANCELADA
    EN_PROGRESO --> EN_CAMINO : 2 h antes del turno
    EN_PROGRESO --> REASIGNACION_PENDIENTE : el plomero cancela
    EN_PROGRESO --> CANCELADA
    EN_CAMINO --> PENDIENTE_CALIFICACION : finaliza (2 h después + boleta)
    EN_CAMINO --> REASIGNACION_PENDIENTE
    EN_CAMINO --> CANCELADA
    REASIGNACION_PENDIENTE --> PENDIENTE : vuelve a solicitar
    REASIGNACION_PENDIENTE --> CANCELADA
    PENDIENTE_CALIFICACION --> COMPLETADA : ambos califican (o 48 h → 5 estrellas)
    SIN_RESPUESTA --> [*]
    CANCELADA --> [*]
    COMPLETADA --> [*]
```
