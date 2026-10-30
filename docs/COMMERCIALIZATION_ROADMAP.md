# SACL / Orquestador — Roadmap de MVP comercial, primera venta y evolución de producto

**Propuesta operativa 2026-10-14 · NO implica autorización de implementación o cambio de alcance congelado.**

## Posicionamiento y meta
Infraestructura de ejecución gobernada para acelerar los otros productos. Primer usuario comercial es SolidBit internamente; NO afirmar que es SaaS listo para terceros.

**Cliente inicial:** Primero: SolidBit como operador interno. Futuro hipotético: pequeños equipos de ingeniería/agencias que requieren agentes auditables en entornos Windows.

**Problema comprado:** Reducir supervisión manual y errores de ejecución de agentes, sin permitir cambios destructivos, accesos o merges no autorizados.

**Oferta a validar:** Fase inicial: herramienta interna de productividad; etapa comercial posterior posible: instalación/autogestión y soporte para equipos aprobados. SaaS hospedado NO es objetivo obligatorio de V1.

## Fuentes canónicas existentes (leer antes de trabajar)
- `DECISION_BASELINE.md`
- `docs/COMMERCIAL_MVP_EXECUTION_PLAN.md`
- `docs/ITERATION_STATE.md`
- `PR #3 e issues #2/#4/#5/#6`

**Lo que ya sabemos / validación pendiente:** Baseline dice IMPLEMENTATION_AUTHORIZED=NO; conservar prioridad de decisiones soberanas, políticas fail-closed, Graph-P/Graph-H, SQLite WAL, Gmail transport, zero-idle-LLM, legado intacto y paridad Windows 18/18 pendiente. No activar implementación sin autorización explícita.

## Roadmap por puertas (sin porcentajes inventados)
### S0 — Autoridad y reconciliación
**Qué hacer:** Revisar constitución y PR #3, alertas CodeQL, issues #2/#4/#5/#6; documentar decisiones abiertas, permisos actuales y diferencia entre V1 especificada y V1 efectivamente implementada.

**Puerta de salida / Definition of Done:** Matriz autoridad por operación, documentos sin contradicciones, lista de bloqueos del GO operativo; NO saltarse IMPLEMENTATION_AUTHORIZED=NO.

**Evidencia mínima:** issue/PR, SHA, prueba E2E o manual vinculada, responsable y GO/NO-GO. 

### S1 — V1 local gobernada (solo autorizada)
**Qué hacer:** Una vez autorizado: validar policy engine, gateway cero ejecución, registry, SQLite WAL, Graph-P idle, Graph-H worktree, cancelación, idempotencia, auditoría y recuperación.

**Puerta de salida / Definition of Done:** Tests deterministas de aislamiento, locks, STOP.ps1, reinicios, packages inválidos y cero merge/prod en V1.

**Evidencia mínima:** issue/PR, SHA, prueba E2E o manual vinculada, responsable y GO/NO-GO. 

### S2 — Certificación y paridad
**Qué hacer:** Certificar en host Windows aprobado los 18 componentes y E2E; comparar con orquestador legado, evidencias SHA/runId, no reemplazar legado antes de GO.

**Puerta de salida / Definition of Done:** 18/18 PASS verificables, seguridad y recuperación certificadas, auditoría de permisos, aprobación expresa de transición.

**Evidencia mínima:** issue/PR, SHA, prueba E2E o manual vinculada, responsable y GO/NO-GO. 

### S3 — Productividad interna
**Qué hacer:** Piloto exclusivo dentro de SolidBit sobre proyectos autorizados de prueba; medir tiempo de wave, tasa PASS, reintentos, intervención humana, costo por resultado y incidentes.

**Puerta de salida / Definition of Done:** Ahorro neto y confiabilidad demostrables durante múltiples waves, sin violaciones de seguridad ni pérdida de trabajo.

**Evidencia mínima:** issue/PR, SHA, prueba E2E o manual vinculada, responsable y GO/NO-GO. 

### S4 — Paquete para terceros (hipótesis)
**Qué hacer:** Descubrir interés de equipos externos; evaluar modelo licencia self-hosted + instalación/capacitación/soporte, limitaciones de proveedor de agentes y transporte Gmail.

**Puerta de salida / Definition of Done:** Primer piloto externo autorizado y pagado, guía de instalación, soporte, modelo de amenazas, licencias y límite de responsabilidad.

**Evidencia mínima:** issue/PR, SHA, prueba E2E o manual vinculada, responsable y GO/NO-GO. 

### S5 — SaaS separado y opcional
**Qué hacer:** Sólo con demanda: ADR de aislamiento, tenancy, secretos, facturación, observabilidad, regiones/privacidad y ejecución remota; no trasladar el V1 local inseguramente a cloud.

**Puerta de salida / Definition of Done:** Puertas de seguridad multi-tenant independientes, permisos y límites de costos, cliente repetible, métricas de margen y controles operativos aprobados.

**Evidencia mínima:** issue/PR, SHA, prueba E2E o manual vinculada, responsable y GO/NO-GO. 

## Exclusiones y control de alcance
No habilitar producción remota, GitHub merges, ejecución no autorizada ni migración del orquestador legado por conveniencia comercial. Venta externa secundaria frente a monetización de SolidPOS/WhatsApp/Ecommerce.

## Métricas para decidir la siguiente etapa
Waves PASS, minutos recuperados por wave, cero acciones no autorizadas, % certificación 18/18 con evidencias, tasa de recuperación, costo por tarea y adopción interna.

## Cómo usar este roadmap y el registro horario
- Este documento **complementa**, jamás reemplaza silenciosamente, las fuentes canónicas listadas. Ante conflicto: instrucciones explícitas del PO > decisiones constitucionales/contratos aprobados > evidencia GitHub actual > este plan propuesto. Cualquier cambio estratégico/contractual pasa por aprobación/ADR.
- Al inicio de cada iteración: leer este documento, las fuentes y `docs/ITERATION_STATE.md` si existe; revisar HEAD, PR, issues, CI y cambios humanos ocurridos tras el checkpoint.
- Ejecutar ciclo íntegro **dentro de la misma sesión**: reconciliar → seleccionar un P0/P1 del gate actual → diseñar mínimo → implementar sólo lo autorizado → probar → corregir → registrar evidencia → preparar próximo slice. No esperar otra hora después de planear.
- Al terminar: actualizar checkpoint append-only (ID UTC, rama/SHA, decisión, trabajo humano descubierto, requisito, pruebas y resultado real, links PR/CI, bloqueo, avance con denominador o N/D, siguiente trabajo) y hacer commit si hay permiso. Si falla escribir: declarar `CHECKPOINT NO PERSISTIDO`, dar contenido recuperable y seguir trabajo independiente; no apagar automatización por bloqueos transitorios.
- Prohibido inventar funciones terminadas, pruebas, porcentajes o ventas. Una suite CI verde no equivale a aceptación comercial ni a aprobación de despliegue. Cambios en ramas aisladas; no force-push, merge, producción, accesos reales, secretos, gastos o despliegue sin autoridad del PO.

## Indicadores y puertas de negocio
- Etapas: `DEV` → `MVP_CANDIDATE` → `DEMO_READY` → `PILOT_AUTHORIZED` → `FIRST_PAID` → `REPEATABLE` → `SAAS_EVALUATION` (SACL usa primero `INTERNAL_GO` y `INTERNAL_VALUE`). No marcar avance por volumen de tickets o commits.
- Para cada salida anotar: cliente/arquetipo, caso de negocio, prueba automatizada + humana, evidencia SHA/PR, decisión GO/NO-GO, entregable comercial, dependencia humana y métrica real.
- Trabajo comercial desde la primera etapa: identificar demanda ACTIVA, guion de demo, contactos calificados, hipótesis de precios a validar, propuesta/alcance, objeciones, soporte, privacidad, impuestos y pagos aplicables. La IA puede preparar materiales y propuestas; contacto, publicación, contratación y pagos necesitan la decisión/autoridad correspondientes.
- Revisar el avance comercial semanalmente. Priorizar entrega real de valor y clientes pagadores antes de arquitectura SaaS; no prometer rentabilidad sin costos reales y facturación.

## Primer ciclo a realizar en GitHub
1. Conciliar este documento con el HEAD actual y con los PR abiertos, preservando el trabajo humano paralelo.
2. Construir matriz `REQUIREMENT | CURRENT PROOF | P0/P1 | TEST | COMMERCIAL GATE | OWNER | LINK`, sin declarar porcentajes N/D como cero.
3. Seleccionar el P0 permitido más cercano a `DEMO_READY` o `FIRST_PAID`; ejecutar cambios/pruebas autorizadas en este mismo ciclo. Si hay un bloqueo de autoridad, avanzar trabajo permitido de demo, QA, documentación o propuesta.
4. Registrar el checkpoint sin usar métricas estimadas como hechos.
