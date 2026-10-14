# SACL S0 — Matriz de certificación y revisión de seguridad

**Fecha:** 2026-10-14 · **Tipo:** documentación de diseño y recuperación de evidencia, no certificado.
**Referencia de código:** `AC-CONT@d0429459b9caf13d1941b514371847a48409b1ad`.
**Autoridad:** `DECISION_BASELINE.md`; `IMPLEMENTATION_AUTHORIZED=NO`; **GO operativo: NO**.
**Fuentes:** `docs/CURRENT_ORCHESTRATOR_COMPATIBILITY_MATRIX.md`, `docs/E2E_CERTIFICATION_PLAN.md`, `docs/certification/SACL_S0_OPERATION_AUTHORITY_TEST_REGISTER_2026-10-14.md`, issues #2/#4/#5/#6, PR #3/#7.

## Matriz 18/18 — cobertura propuesta, no pruebas ejecutadas

Los identificadores TEST son los pasos del plan E2E; AUTH son escenarios **diseñados** y no ejecutados. Una correspondencia no acredita cobertura ni certificación.

| Componente | E2E propuesto | Negativos propuestos | Evidencia adicional requerida |
|---|---|---|---|
| C01 Worktrees | TEST-03/04 | AUTH-04/09 | Registro Git y checkout primario intacto |
| C02 Dirty-root | TEST-04 | AUTH-04/09 | Sentinela + hash antes/después; halt |
| C03 Preflight | TEST-01/02 | — | CLI/rutas y rechazo fail-closed |
| C04 Worker | TEST-05 | AUTH-02 | Identidad, worktree validado y no-spawn |
| C05 Prompt governance | TEST-02/08 | AUTH-03 | Headers preservados y no autoautorización |
| C06 DAG/concurrencia | TEST-05 | — | Dependencias y un mutador por proyecto |
| C07 Estado/PID | TEST-06 | AUTH-10/11 | PID, imagen y hora; reciclado rechazado |
| C08 Extracción de resultados | TEST-08 | AUTH-12 | Regex/fallback y propagación de fallo Git |
| C09 Colisiones | TEST-08 | AUTH-12 | Colisión bloquea integración |
| C10 STOP/timeout | TEST-07 | AUTH-10/11 | Timeout no mata; STOP verifica identidad |
| C11 Supervisor singleton | TEST-05 | — | Lease único, reinicio seguro |
| C12 Monitor | TEST-06 (parcial) | — | Lectura sin mutación |
| C13 Autorización | TEST-04/08 (parcial) | AUTH-01..09 | Intersección de políticas y grants vinculados |
| C14 Wave ZIP | TEST-02 | AUTH-01..03 | Manifest/job_id/registro confiable |
| C15 E2E | TEST-01..08 | AUTH-04/09..12 | Ocho pasos en Windows aislado autorizado |
| C16 Taxonomía de riesgos | TEST-08 (parcial) | AUTH-05/08 | Riesgos clasificados y auditables |
| C17 Transporte Gmail | **No cubierto por mocks E2E** | AUTH-01 | Ensayo separado autorizado de transport-only, OAuth2/historyId y reconciliación |
| C18 Operaciones remotas | TEST-08 (política parcial) | AUTH-05/08 | Hard deny sin mutación real de sistemas externos |

**Conteos con denominador:** 18/18 capacidades inventariadas; **0/18 certificados de host Windows aceptados en la evidencia inspeccionada**. Esto no representa porcentaje de implementación; progreso funcional = **N/D**. Ocho pasos E2E están definidos, pero no se ejecutaron en esta iteración.

## Seguridad — clasificación de CodeQL, issue #4

El workflow CodeQL `SUCCESS` de PR #3 en SHA `d0429459` (run 38520855325) **no prueba que no existan alertas**. Inventario real de Code Scanning: **UNKNOWN** (no accesible desde el conector utilizado). No inventar IDs, severidades ni conteos.

Para cada alerta real registrar: `alert_number, rule_id, severity, state, introduced_sha, current_sha, path, line, dataflow, impact, classification, reviewer, reviewed_at_utc, linked_issue, regression_test, retest_sha`. Clasificar hallazgos P0/P1 que comprometan autoridad, integridad, aislamiento o acciones irreversibles como bloqueantes de GO; los falsos positivos requieren justificación y revisión humana. Incluso una lista vacía necesita evidencia explícita de consulta.

## Revisión humana del PR #3 — issue #5

Comprobar diff y tests de `src/sacl/worker/worktree.py`, `src/sacl/workspace/manager.py` y llamadas de worker: fallos Git fail-closed, rechazo de carpetas ajenas y symlinks, prohibición de borrado recursivo y fallback mkdir, raíz dirty intacta, mock_mode explícito, proceso sólo tras validación, PID/name/start-time, no merges ni producción. Conservar SHA, hallazgos, revisor y decisión; este documento **no aprueba** el PR.

## Contrato de evidencia para certificación Windows — issue #6

**Prerequisitos:** revisión humana PR #3; alertas #4 clasificadas; permiso expreso de host; sandbox y backups; legado en solo lectura; CI por SHA comprobado. Cada caso requiere `component_id, case_id, sacl_sha, legacy_snapshot_sha, windows_build, isolated_root, fixture_sha256, operator, reviewer, start_utc, end_utc, expected, actual, side_effects_before_after, artifact_path, artifact_sha256, result, approval_reference`.

Un caso sin ejecución host real, sin side-effect proof o con solo mock CI es `NOT_CERTIFIED`. La compatibilidad C17 requiere pruebas separadas autorizadas; la suite de ocho pasos no cubre Gmail real. No archivar legado sin GO adicional.

## Valor interno antes de comercialización

Tras GO operativo explícito, medir waves de prueba con `wave_id, sha, human_minutes_baseline, human_minutes_sacl, elapsed_minutes, pass_fail, retries, interventions, incidents, observed_cost`. El ahorro neto se calcula sobre tareas comparables y resultados aceptados; no se presume. Licencia para terceros y SaaS son hipótesis posteriores, no V1 acreditada.

## Próximas puertas

1. Issue #4: inventario y clasificación reales de CodeQL por revisor autorizado.
2. Issue #5: revisión humana del hardening PR #3.
3. Issue #6: autorización y certificación host Windows 18/18 + E2E, con evidencia firmada.
4. Sólo tras GO: piloto interno medido; sin transición de legado, merge, deploy ni operación externa automática.
