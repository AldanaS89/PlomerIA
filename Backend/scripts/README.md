# Scripts de PlomerIA

Utilidades para sembrar y reiniciar datos. Correr desde la carpeta `Backend`
con el venv activado: `python scripts/<nombre>.py`

## Maestro (todo de una)

| Script | Qué hace |
|--------|----------|
| `setup_demo.py` | **Borra toda la base y recarga** ficticios + agendas + antigüedad. Deja todo listo para una demo desde cero. ⚠️ Pierde las cuentas creadas. |

## Individuales

| Script | Qué hace | ¿Pierde cuentas? |
|--------|----------|------------------|
| `reset_db.py` | Borra **todas** las tablas y las recrea vacías. | Sí (todo) |
| `reset_trabajos.py` | Borra solo **solicitudes, mensajes, notificaciones, calificaciones, boletas** y libera agendas. | No (conserva cuentas) |
| `cargar_plomeros.py` | Carga los **plomeros ficticios** desde el JSON. | — |
| `simular_antiguedad.py` | Backdatea la **antigüedad** de los ficticios (desde marzo 2026). | — |
| `generar_agendas.py` | Genera **agendas** simuladas para los ficticios. | — |

## Recetas típicas

- **Demo desde cero:** `python scripts/setup_demo.py`  → después re-registrá tu cliente/plomero de prueba.
- **Probar el flujo de nuevo sin perder cuentas:** `python scripts/reset_trabajos.py`
- **Solo recargar ficticios** (base ya creada): `cargar_plomeros.py` → `simular_antiguedad.py` → `generar_agendas.py`
