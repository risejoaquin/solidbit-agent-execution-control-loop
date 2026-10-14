# SACL S0 — Revisión de fronteras de confianza en recuperación Graph-P

**Fecha:** 2026-10-14 · **Base de código inspeccionada:** `AC-CONT@d0429459b9caf13d1941b514371847a48409b1ad` (PR #3, Draft).  
**Clasificación:** revisión estática documental; **NO** vulnerabilidad explotable demostrada, **NO** pruebas runtime, **NO** aprobación.  
**Autoridad:** `DECISION_BASELINE.md` y contratos congelados; `IMPLEMENTATION_AUTHORIZED=NO`; GO operativo = NO.

## Observación TB-01 — Adaptador de vida de proceso inyectado

**Archivo:** `src/sacl/supervisor/graph_p.py`, `GraphPSupervisor.__init__` y `_is_recovery_worker_alive`.

**Evidencia del código:** el constructor acepta `process_checker` como callback opcional; establece `_use_canonical_recovery_identity = process_checker is None`. Si el callback suministrado devuelve `True`, `_is_recovery_worker_alive` devuelve `True` antes de inspeccionar el nombre de la imagen y la hora de inicio del PID. En la ruta predeterminada, en cambio, exige `recorded_start_time` e invoca `inspect_process` para validar la identidad de tres factores.

**Lectura:** es un bypass deliberado para adaptadores confiables de pruebas/host; no es por sí mismo una falla demostrada. **Riesgo condicional** si una entrada no confiable o configuración de runtime pudiera inyectar ese callback. La ruta predeterminada parece fail-closed para PID reciclado, pero su certificación real sigue pendiente.

**Decisión de revisión requerida:** demostrar con búsqueda de callsites y configuración de arranque que un paquete, manifest, mensaje Gmail, CLI no confiable o plugin no puede suministrar `process_checker`; identificar responsables de los adaptadores confiables. No modificar el contrato congelado sin ADR.

## Observación TB-02 — Error de comprobación dirty-root durante recuperación

**Archivo:** `src/sacl/supervisor/graph_p.py`, `reconcile_startup`, fase 2.1.

**Evidencia del código:** si existe `dispatcher.clean_root_checker`, el supervisor bloquea la recuperación cuando devuelve `is_clean=False`. Sin embargo, el bloque que invoca ese checker captura `Exception` y ejecuta `pass`; tras una excepción, continúa a la fase de inspección de workers y reconciliación de entregables.

**Lectura:** **posible incumplimiento de fail-closed** bajo un fallo del checker (p. ej. error Git o I/O). No se observó aquí ejecución de agentes nuevos ni mutación del checkout, y no se ha reproducido impacto; debe comprobarse la consecuencia efectiva en estados, locks y evidencias. Es una **hipótesis P1 para revisión**, no un defecto certificado.

**Decisión de revisión requerida:** especificar comportamiento seguro ante error del checker, sin borrar, stashear, reiniciar procesos ni modificar trabajo humano; validar contra la regla Dirty-Root de la constitución y el comportamiento probado del legado antes de proponer corrección.

## Ensayos propuestos, NO ejecutados (requieren autorización de implementación)

| ID | Escenario aislado | Resultado esperado | Evidencia futura |
|---|---|---|---|
| TB-T01 | Ruta predeterminada, PID existente con hora de inicio distinta | No reconectar worker | PID/imagen/hora, transición y auditoría |
| TB-T02 | Ruta predeterminada, hora persistida ausente | No reconectar worker | Estado antes/después y ausencia de spawn |
| TB-T03 | Callback inyectado devuelve True con PID reciclado | Demostrar exactamente el alcance del bypass y que sólo es accesible a código confiable | Callsite, stack, configuración, test mock |
| TB-T04 | `clean_root_checker` devuelve dirty | Bloqueo y preservación del checkout | Hash de sentinela y registro de bloqueo |
| TB-T05 | `clean_root_checker` lanza excepción | Decisión fail-closed conforme a contrato, sin acciones destructivas | Error, estados, locks, archivos intactos |
| TB-T06 | `clean_root_checker` ausente | Acreditar que la ausencia está permitida por política o impedir recuperación insegura | Inicialización, autoridad de checker, resultado |

**Evidencia mínima futura:** SHA de código y fixture, Windows build, directorio temporal aislado, hash antes/después, runId, logs, estado SQLite, resultado, operador y revisor. `PASS` de CI con mocks no equivale a certificación Windows ni a permiso de uso real.

## Gate y trazabilidad

- **Issue #5 / PR #3:** revisión humana de TB-01/TB-02 y pruebas asociadas cuando estén autorizadas.
- **Issue #4:** inventario real de alertas CodeQL sigue **UNKNOWN**; CodeQL SUCCESS no equivale a cero alertas.
- **Issue #6:** paridad Windows 18/18 y ocho pasos E2E siguen sin acreditarse.
- **Riesgo actual:** clasificación provisional; severidad definitiva **N/D** sin reproducción, threat model y revisión.
- **GO operativo:** NO; legado intacto, sin merge, despliegue, producción, secretos, gastos ni transición.
- **Siguiente paso permitido ahora:** inspección documental de callsites y preparación de matriz de evidencia, sin activar runtime.

Este documento complementa la matriz 18/18 y el registro AUTH-01..12 existentes. No cambia políticas, contratos ni código.
