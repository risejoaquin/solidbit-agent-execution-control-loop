# SACL — ChatGPT + GitHub / rama AC-CONT

Fecha de inicio: 2026-10-13. Rama de trabajo persistente: `AC-CONT`.

## Alcance

Este flujo permite desarrollar, probar, depurar y revisar el código de SACL
directamente mediante las herramientas de GitHub. GitHub es el entorno de
desarrollo y control de versiones; GitHub Actions es el entorno CI. No se
requiere el orquestador local para modificar este repositorio mediante ChatGPT.

**No sustituye la arquitectura operativa congelada de SACL V1.**
Se conservan Gmail/PubSub como transporte, Graph-P, Graph-H, SQLite,
worktrees, aprobación humana y el orquestador heredado.

## Etapas

1. **Plan:** registrar defectos y tareas en Issues, referenciando evidencias.
2. **Code:** crear cambios exclusivamente en `AC-CONT`, con commits pequeños.
3. **Check:** en cada push, ejecutar tests y validación en GitHub Actions.
4. **Review:** abrir y mantener draft PR de `AC-CONT` a la rama predeterminada.
5. **Gate:** no hacer merge hasta revisar pruebas y recibir autorización específica.
6. **Release:** sin conexión a Railway, producción, Gmail real ni `agy.exe` en CI.

## Herramientas

- Codespaces: `.devcontainer/devcontainer.json` configura Python 3.11.
- Actions: `.github/workflows/ci.yml` ejecuta suite completa en Ubuntu/Windows.
- Dependabot: actualizaciones semanales, sin auto-merge.
- CODEOWNERS y plantillas: trazabilidad del backlog y PR.
- Projects, CodeQL default setup y Rulesets: configuración adicional de GitHub
  pendiente de activación según permisos y decisión de gobernanza.
  Los archivos CODEOWNERS/Dependabot/plantillas se aplican plenamente al
  integrarse en la rama predeterminada.

## Seguridad del flujo

La autorización para que ChatGPT escriba cambios a `AC-CONT` es
**independiente** de las autorizaciones que necesitaría el runtime SACL.
El contrato `implementation_authorized=false` permanece congelado,
no se invocan ejecutores reales y GitHub Actions solo obtiene `contents: read`.
No se alteran políticas de producción, reglas del repositorio ni credenciales.
El análisis de seguridad E2E y paridad con el orquestador heredado sigue siendo
obligatorio antes de cualquier puesta en funcionamiento.

## Comandos en Codespaces

```bash
python -m pytest tests/governance -q
python -m pytest tests --tb=short -ra
python -m compileall -q src/sacl tests
```

## Entrega inicial SACL-CI-001

- Añadir infraestructura de GitHub sin editar el runtime existente.
- Comprobar runs reales de Actions en `AC-CONT` y draft PR.
- Mantener registro de fallos y su remediación en Issues/commits.
