# Diagramas — PlomerIA

Diagramas como código. Los de **Mermaid** se ven directo acá en GitHub; los de
**PlantUML** se generan pegando el archivo en
[plantuml.com](https://www.plantuml.com/plantuml) o con la extensión *PlantUML* de VS Code.
(Los Mermaid también se pueden editar/exportar en [mermaid.live](https://mermaid.live).)

| Diagrama | Qué muestra | Archivo |
|----------|-------------|---------|
| Casos de uso | Actores (Cliente, Profesional, Sistema/IA) y sus casos de uso | [`casos_de_uso.puml`](casos_de_uso.puml) |
| Clases (UML) | Entidades del dominio, enums y relaciones | [`diagrama_clases.puml`](diagrama_clases.puml) |
| Flujo de solicitud | Recorrido completo de una solicitud | [`flujo_solicitud.mmd`](flujo_solicitud.mmd) |
| Estados | Máquina de estados de la solicitud | [`estados_solicitud.mmd`](estados_solicitud.mmd) |

---

## Flujo de una solicitud

```mermaid
flowchart TD
    A([Cliente describe el problema]) --> B{IA: ¿problema válido?}
    B -- No --> A
    B -- Sí --> C[Diagnóstico + oficio + ¿urgencia? + presupuesto]
    C --> U{¿Es urgencia?}
    U -- Sí --> SOS[Solución inmediata: cerrar llave de paso]
    U -- No --> D
    SOS --> D[Filtrar 5 mejores: cercanía + puntuación + disponibilidad]
    D --> E[Cliente elige día/horario]
    E --> F[Invitaciones a profesionales]
    F --> G{¿Alguien acepta?}
    G -- No --> R{¿Quedan rondas? máx 3}
    R -- Sí --> D
    R -- No --> SR([SIN_RESPUESTA: reintentar luego])
    G -- Sí --> I[EN_PROGRESO: profesional asignado]
    I --> J[EN_CAMINO]
    J --> K[FINALIZADO → PENDIENTE_CALIFICACION]
    K --> L{¿Ambos calificaron en 72 h?}
    L -- Sí --> M([COMPLETADA])
    L -- No --> N[5★ automáticas] --> M
    I -. cancelación .-> P[Penalización al promedio]
    J -. cancelación .-> P
```

## Estados de la solicitud

```mermaid
stateDiagram-v2
    [*] --> PENDIENTE
    PENDIENTE --> EN_PROGRESO : un profesional acepta
    PENDIENTE --> PENDIENTE : reasignar (máx 3 rondas)
    PENDIENTE --> SIN_RESPUESTA : nadie acepta
    PENDIENTE --> CANCELADA
    EN_PROGRESO --> EN_CAMINO
    EN_PROGRESO --> REASIGNACION_PENDIENTE : el plomero cancela
    EN_PROGRESO --> CANCELADA
    EN_CAMINO --> PENDIENTE_CALIFICACION : finaliza
    EN_CAMINO --> REASIGNACION_PENDIENTE
    EN_CAMINO --> CANCELADA
    REASIGNACION_PENDIENTE --> PENDIENTE : vuelve a solicitar
    REASIGNACION_PENDIENTE --> CANCELADA
    PENDIENTE_CALIFICACION --> COMPLETADA : ambos califican (o 72h → 5★)
    SIN_RESPUESTA --> [*]
    CANCELADA --> [*]
    COMPLETADA --> [*]
```

> Casos de uso y clases están en PlantUML (`.puml`) porque Mermaid no tiene una
> notación nativa para esos diagramas. Pegá el archivo en plantuml.com para verlos.
