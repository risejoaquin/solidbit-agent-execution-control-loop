import { test, expect } from '@playwright/test';

/**
 * Suite E2E: Flujo KISS de Orquestación en 3 Fases (OrchestratorFlow)
 * 
 * Verifica el ciclo de vida lineal:
 * 1. Fase 1: Agente de Diseño (prompt o preset rápido, contratos congelados y compuerta).
 * 2. Fase 2: Agente de Implementación (visor de diff / lista limpia de archivos y aprobación).
 * 3. Fase 3: Agente de Despliegue (progreso claro de integración y confirmación final).
 */
test.describe('KISS OrchestratorFlow 3-Phase E2E Suite', () => {
  test('E2E: Complete linear flow from design prompt to autonomous validation and deploy', async ({
    page,
  }) => {
    await page.setViewportSize({ width: 1280, height: 800 });

    // Mock de contratos con estado FROZEN para activar la autonomía por contrato
    await page.route('**/api/contracts', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          contracts: [
            { id: 'DR-INV-001', title: 'Inventory Lock', status: 'FROZEN', enforcement: 'STRICT' },
            { id: 'DR-PAY-001', title: 'Ledger Atomicity', status: 'FROZEN', enforcement: 'STRICT' },
          ],
        }),
      });
    });

    // Mock de auditoría y propuesta de sprint
    await page.route('**/api/projects/audit-and-plan', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          plan: {
            title: 'Hardening de Invariantes & Idempotencia',
            waves: [{ wave_number: 1, parallel_agents: ['Atlas', 'Vega'] }],
          },
        }),
      });
    });

    // Mock de diffs de implementación
    await page.route('**/api/git/diff', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          files: [
            { file: 'src/sacl/state/invariants.py', additions: 32, deletions: 2, status: 'MODIFIED' },
            { file: 'src/sacl/ui/OrchestratorFlow.tsx', additions: 110, deletions: 5, status: 'MODIFIED' },
          ],
          raw_diff: '--- a/src/sacl/state/invariants.py\n+++ b/src/sacl/state/invariants.py\n+    # Atomic validation',
        }),
      });
    });

    // Mock de acciones de integración
    await page.route('**/api/actions/execute', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, message: 'Worktrees podados y sincronizados' }),
      });
    });

    const targetUrl = process.env.BASE_URL || 'http://localhost:5173';
    await page.goto(targetUrl);

    // 1. FASE 1: Verificar presencia del Stepper y del Agente de Diseño
    await expect(page.locator('text=Fase 1 · Agente de Diseño')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=¿Qué deseas construir o resolver hoy?')).toBeVisible();

    // Seleccionar una plantilla rápida
    const presetBtn = page.locator('button:has-text("Invariantes & Hardening")');
    if (await presetBtn.isVisible()) {
      await presetBtn.click();
    } else {
      await page.fill('textarea', 'Refactorizar invariantes con contratos');
      await page.click('button:has-text("Diseñar Sprint")');
    }

    // Verificar que se renderiza la propuesta generada
    await expect(page.locator('text=Propuesta de Diseño Generada')).toBeVisible({ timeout: 3000 });
    await expect(page.locator('text=Autonomía por Contrato')).toBeVisible();

    // 2. FASE 2: Avanzar a Fase 2 (Implementación)
    const approvePhase1Btn = page.locator('button:has-text("Aprobar Propuesta y Pasar a Implementación")');
    await approvePhase1Btn.click();

    await expect(page.locator('text=Fase 2 · Agente de Implementación')).toBeVisible({ timeout: 3000 });
    await expect(page.locator('text=Resultados del Código y Verificación')).toBeVisible();

    // Verificar que los archivos modificados son visibles
    await expect(page.locator('text=src/sacl/state/invariants.py')).toBeVisible();

    // Conmutar al visor de Diff
    await page.click('button:has-text("Visor de Diff")');
    await expect(page.locator('text=Atomic validation')).toBeVisible();

    // 3. FASE 3: Aprobar Implementación y Desplegar
    const approvePhase2Btn = page.locator('button:has-text("Aprobar Implementación y Desplegar")');
    await approvePhase2Btn.click();

    await expect(page.locator('text=Fase 3 · Agente de Despliegue & Integración')).toBeVisible({ timeout: 3000 });

    // Esperar finalización del despliegue exitoso
    await expect(page.locator('text=Cambios subidos e integrados correctamente')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=Iniciar Nuevo Flujo de Orquestación')).toBeVisible();
  });
});
