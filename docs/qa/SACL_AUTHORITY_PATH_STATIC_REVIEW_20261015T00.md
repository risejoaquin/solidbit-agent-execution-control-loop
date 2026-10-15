# SACL S0 — revisión estática de ruta de autorización (solo documentación)

- **Run:** SACL-20261015T00
- **Fecha UTC de inspección:** 2026-10-15T07:31:35.268Z
- **Base inspeccionada:** `AC-CONT@d0429459b9caf13d1941b514371847a48409b1ad`
- **Autoridad:** `IMPLEMENTATION_AUTHORIZED=NO` según `DECISION_BASELINE.md`.
- **Veredicto:** evidencia de lectura y comprobación estática, **no** certificación de ejecución ni vulnerabilidad confirmada.

## Resultado reproducible de lectura estructural

Se evaluaron nueve predicados de texto sobre cinco blobs inmutables del SHA base: **9/9 PASS**. Comando equivalente: lectura de archivos GitHub por SHA y comprobaciones de cadenas/IDs en JavaScript, sin importar ni ejecutar módulos Python.

1. La matriz de compatibilidad contiene exactamente 18 filas numeradas únicas.
2. Los IDs abarcan 1–18 sin saltos.
3. Las 18 filas incluyen referencia documental de evidencia (esto **no** prueba paridad operativa).
4. `GraphPSupervisor` construye un `JobDispatcher` por defecto.
5. La llamada de construcción predeterminada no inyecta explícitamente `policy_engine`.
6. `_resolve_target_repo_path` evalúa primero `metadata.target_repo_path` y luego el resolvedor del proyecto.
7. `JobDispatcher.__init__` permite `policy_engine=None`.
8. Existe `PermissionLattice.evaluate`.
9. El default `HardPolicyEngine` declara `github_merge=True` como denegación.

**Archivos y blob SHA:**
- `docs/CURRENT_ORCHESTRATOR_COMPATIBILITY_MATRIX.md`: `d3cca3fa9797d2164bd343e77d2761d1ec5abb33`
- `src/sacl/supervisor/graph_p.py`: `05d159724942e7a39b8da296c32ee862ecd490b7`
- `src/sacl/supervisor/dispatcher.py`: `5d7cc7b9c976e0422086470fe0ea0d03e1717760`
- `src/sacl/policy/hard_policy.py`: `64e6a668df4f8b0c2ba09bc0857e2650937b785d`
- `src/sacl/policy/lattice.py`: `1ecd710d5e5778e47d8830730e00b77ee30216cd`

## Brecha S0-NEG-01 — demostrar el enforcement efectivo

En `graph_p.py`, `self.dispatcher = dispatcher or JobDispatcher(...)` no pasa `policy_engine`; en `dispatcher.py` el constructor acepta el motor como opcional. La inspección de `dispatch_job` no encontró una invocación explícita de la lattice antes de preparar el run y entregar el contexto al launcher. En `_resolve_target_repo_path`, la metadata de trabajo antecede al resolvedor/registro y hay fallback a `Path.cwd()`.

Esto es una **brecha de trazabilidad** entre el contrato constitucional de raíz confiable y el camino predeterminado; no se ha demostrado que entradas externas puedan alcanzar esa metadata, que un launcher real sea invocado sin otros guardas, ni que exista una vulnerabilidad explotable. No modificar código sin autorización expresa.

## Pruebas negativas requeridas cuando se autoricen

| Caso | Entrada simulada | Criterio de PASS | Estado |
|---|---|---|---|
| S0-NEG-01A | Job QUEUED con `metadata.target_repo_path` fuera del Project Registry | Denegación antes de crear run, lease liberado, audit event sin secretos | NO EJECUTADA |
| S0-NEG-01B | Job sin proyecto válido, fallback de `Path.cwd()` | Denegación fail-closed; no ejecución en checkout primario | NO EJECUTADA |
| S0-NEG-01C | Graph-P con dispatcher por defecto y sin aprobación bounded | Denegación de mutación, cero launcher calls | NO EJECUTADA |
| S0-NEG-01D | Aprobación válida de una operación, solicitud de otra | Denegación de ampliación de permisos | NO EJECUTADA |

## Gates y evidencia externa

- Inventario de matriz: **18/18 filas documentadas**. **Paridad host Windows: 0/18 acreditadas en este ciclo**; no se reinterpretan como pruebas fallidas.
- GitHub Actions CI para SHA base: [run 38520855350](https://github.com/risejoaquin/solidbit-agent-execution-control-loop/actions/runs/38520855350), SUCCESS; CodeQL [38520855325](https://github.com/risejoaquin/solidbit-agent-execution-control-loop/actions/runs/38520855325), SUCCESS.
- La lista de alertas CodeQL no pudo consultarse: endpoint no expuesto por el conector. [Issue #4](https://github.com/risejoaquin/solidbit-agent-execution-control-loop/issues/4) pendiente de revisión humana.
- [Issue #6](https://github.com/risejoaquin/solidbit-agent-execution-control-loop/issues/6): host Windows y paridad real 18/18 requieren autorización/infraestructura; E2E mock no certifica operación real.
- PR #3, #7, #8 y #9 siguen Draft. No se alteraron contratos, código, legacy, permisos ni producción.

## Siguiente trabajo permitido

Documentar casos negativos con mapeo a tests existentes, revisar CodeQL por el PO en Security, y preparar acta de certificación Windows sin ejecutarla hasta que haya host y autorización. El `INTERNAL_GO` permanece **NO-GO**.
