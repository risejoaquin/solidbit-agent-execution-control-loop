# SolidBit SACL — Plan de ejecución hacia MVP comercial

> **Plan operativo con trazabilidad a código (corte 2026-10-14):** consultar [ROADMAP_MVP_COMERCIAL_CODE_AUDITADO_2026-10-14.md](ROADMAP_MVP_COMERCIAL_CODE_AUDITADO_2026-10-14.md) antes de elegir tareas. Ese documento añade inventario de código, backlog P0/P1, ruta crítica, riesgos y gates de aceptación. El presente plan general es una referencia histórica y no acredita comercialización. Nunca convertir CI o simulaciones en GO; no merge/deploy sin autorización.

Fecha base: 2026-10-13. Documento de dirección, **no** certificación de funcionalidades existentes.

## Objetivo y límite
Orquestador V1 confiable que ejecuta waves de agentes y recupera control operacional; no confundir con POS/ecommerce.

## Etapas / sprints (secuencia orientativa; basar fechas en evidencia)
### Etapa 0
S0 Reconciliar decisiones: DECISION_BASELINE, IMPLEMENTATION_AUTHORIZED=NO, paridad de orquestador legado, estado AC-CONT.
**Salida:** PR revisable, CI y evidencia por casos de aceptación; no asignar porcentaje sin prueba.

### Etapa 1
S1 Control plane: registry, validación de paquetes, política de privilegio mínimo, SQLite WAL, event log y autorización humana explícita.
**Salida:** PR revisable, CI y evidencia por casos de aceptación; no asignar porcentaje sin prueba.

### Etapa 2
S2 Execution plane: Graph-P idle sin tokens, Graph-H DAG por wave, leases, concurrency por proyecto, worktrees y stop switch.
**Salida:** PR revisable, CI y evidencia por casos de aceptación; no asignar porcentaje sin prueba.

### Etapa 3
S3 Recuperación: crash/restart, at-least-once transport + idempotencia, retry bounded, heartbeats, lock recovery y evidencia inmutable.
**Salida:** PR revisable, CI y evidencia por casos de aceptación; no asignar porcentaje sin prueba.

### Etapa 4
S4 Certificación: E2E de waves locales, paquetes maliciosos, compatibilidad legado, audit trail y GO/NO-GO para uso real.
**Salida:** PR revisable, CI y evidencia por casos de aceptación; no asignar porcentaje sin prueba.

## Criterio de aceptación comercial
Probar garantías fail-closed, respeto de autorización congelada, cero merges/prod no autorizados, persistencia/reinicio, aislamiento entre proyectos y paridad E2E.

## Contrato de cada iteración horaria
1. Leer este plan, README, documentación constitucional/AGENTS y PRs/CI recientes. Resolver conflictos a favor de decisiones del Product Owner y contratos aprobados.
2. Inspeccionar código y tests; establecer brecha verificable sin inferir que README=implementación; consultar resultados del último ciclo y evitar repetición.
3. Tomar máximo un slice vertical P0/P1 capaz de dejar código, pruebas y evidencia en la misma iteración. Si bloqueado, avanzar en un slice independiente.
4. Codificar **sólo en rama de trabajo**; correr tests unitarios, integración, contratos y E2E cuando aplique; verificar GitHub Actions. No usar proveedores reales mientras desarrollo local/CI baste.
5. Registrar matriz de trazabilidad requisito → issue → commit/PR → prueba → resultado → evidencia; fallos nunca se contabilizan como éxito.
6. Publicar reporte Markdown en PR con Gantt de etapas, % demostrado y % no demostrado; cada porcentaje debe explicar denominador y pruebas de aceptación, no líneas de código, commits o tickets cerrados.
7. Detener modificaciones riesgosas si requiere aprobación, secretos, gastos o producción; documentar exactamente qué requiere intervención humana. Preparar siguiente slice.

## Gobernanza innegociable
- No merge, deploy, cambio de producción, ejecución sobre datos reales, rotación de secretos ni gasto sin autorización expresa.
- No sobrescribir decisiones explícitas, modelos de respuesta congelados o funcionalidades probadas para simplificar el desarrollo.
- Separar documentación de pruebas ejecutadas y de pruebas previstas; marcar cada evidencia con SHA y fecha.
- Prohibido atribuir a un ciclo horario la capacidad de retomar un chat específico: el estado oficial es GitHub (archivos, PR, issues, Actions).
- Si hay ejecuciones concurrentes, no pisar ramas ni cambios: serializar las escrituras por repo.

## Medición
Para cada requisito crítico mantener peso, criterio de aceptación, prueba automatizada/E2E, estado y SHA. `avance_validado = suma(pesos de criterios aprobados con evidencia) / suma(pesos totales del MVP)`. Desconocido != 0%; reportar **N/D** si no está inventariada la matriz. Mostrar también defectos P0/P1 abiertos, CI verde/rojo, riesgos y bloqueo GO/NO-GO.

## Rama de desarrollo de referencia
`AC-CONT`. Nunca escribir sobre `main` salvo autorización y política existente; si la rama aquí indicada es `main`, crear primero rama dedicada de feature/plan.
