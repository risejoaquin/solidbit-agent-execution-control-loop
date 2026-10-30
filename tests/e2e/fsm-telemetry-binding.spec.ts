import { test, expect } from '@playwright/test';

/**
 * Suite de Verificación End-to-End (E2E)
 * Mapeo Event-Driven entre Daemon Antigravity / SACL y App Shell React UIX
 *
 * Flujo auditado:
 * 1. Navegación e hidratación de App Shell continuo (#persistent-telemetry-drawer).
 * 2. Inyección determinista de eventos terminales FSM (Agent: Vega, Status: PASS, Commit: b9a448f9).
 * 3. Aserción de mutación inmutable: nodo pintado en verde y commit visible en < 2000ms.
 * 4. Trazabilidad de compuertas/acciones humanas: disparo de RPC con headers de contexto inyectados.
 */
test.describe('FSM Telemetry & Event Binding E2E Suite', () => {
  test('E2E: React UIX binds deterministically to FSM SSE event loop and emits side-effects', async ({
    page,
  }) => {
    // 1. Mock de rutas operativas para garantizar determinismo estricto
    await page.route('**/api/orchestrator/context', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          active_project: { name: 'SolidPos', branch: 'worktrees/scheduler', path: 'C:/SolidPos' },
          jira_backlog: [],
        }),
      });
    });

    await page.route('**/api/projects', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          projects: [
            {
              id: 'solidpos',
              name: 'SolidPos',
              path: 'C:/SolidPos',
              branch: 'worktrees/scheduler',
              is_active: true,
            },
          ],
        }),
      });
    });

    await page.route('**/api/agents/fleet', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          active_agents: [
            {
              id: 'vega',
              name: 'Vega',
              role: 'Backend Invariant Specialist',
              status: 'En espera',
              color: 'zinc',
            },
          ],
        }),
      });
    });

    await page.route('**/api/github/commits*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          commits: [
            {
              sha: 'init1234',
              message: 'Initial baseline commit',
              author: 'Joaquin',
              time: '10:00:00',
            },
          ],
        }),
      });
    });

    await page.route('**/api/db/rows*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ rows: [] }),
      });
    });

    await page.route('**/api/gates/pending', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ count: 0, gates: [] }),
      });
    });

    // Mock para /api/actions/execute respondiendo éxito
    await page.route('**/api/actions/execute', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          execution_id: 'EXEC-TEST-001',
          status: 'COMPLETED',
          message: 'Worktrees liberados con éxito.',
        }),
      });
    });

    // Paso 1: Navegar a la vista principal de la UI
    const targetUrl = process.env.BASE_URL || 'http://localhost:5173';
    await page.goto(targetUrl);

    // Verificar que el drawer persistente de telemetría está montado
    const drawer = page.locator('#persistent-telemetry-drawer');
    await expect(drawer).toBeVisible({ timeout: 5000 });

    // Paso 2: Interceptar o inyectar el payload tipado simulando estado terminal del agente
    const terminalPayload = {
      agent: 'Vega',
      status: 'PASS',
      commit: 'b9a448f9',
      message: 'Invariantes de contrato DR-INV-001 y DR-PAY-001 verificados al 100%',
    };

    const startTime = Date.now();

    // Inyección de evento tipado mediante Event Sourcing hook expuesto en el cliente
    await page.evaluate((payload) => {
      if (typeof (window as any).__INJECT_FSM_EVENT__ === 'function') {
        (window as any).__INJECT_FSM_EVENT__(payload);
      } else {
        window.dispatchEvent(new CustomEvent('fsm-event', { detail: payload }));
      }
    }, terminalPayload);

    // Paso 3: Realizar aserción en el DOM de PersistentTelemetryDrawer
    // a) El nodo se pinta en verde (clase emerald y badge PASS)
    const vegaNode = drawer.locator('[data-testid="telemetry-agent-vega"]');
    await expect(vegaNode).toBeVisible({ timeout: 2000 });
    await expect(vegaNode).toHaveClass(/border-emerald-500|bg-emerald-950/, { timeout: 2000 });

    const vegaStatus = drawer.locator('[data-testid="agent-status-vega"]');
    await expect(vegaStatus).toContainText('PASS', { timeout: 2000 });

    // b) Muestra el commit SHA en el drawer
    const commitShaLocator = drawer.locator('[data-testid="telemetry-commit-sha"]').first();
    await expect(commitShaLocator).toContainText('b9a448f', { timeout: 2000 });

    const elapsed = Date.now() - startTime;
    expect(elapsed).toBeLessThan(2000);

    // Paso 4: Simular clic en botón de acción humana y verificar que la petición HTTP
    // sale hacia el Daemon con el payload y headers de contexto de inyección obligatorios
    const [request] = await Promise.all([
      page.waitForRequest((req) => req.url().includes('/api/actions/execute') && req.method() === 'POST'),
      drawer.locator('[data-testid="btn-action-release"]').click(),
    ]);

    // Aserción del payload RPC
    const requestBody = request.postDataJSON();
    expect(requestBody.action).toBe('release_worktree');
    expect(requestBody.context).toBeDefined();
    expect(requestBody.context.git_branch).toBe('worktrees/scheduler');
    expect(requestBody.context.worktree_path).toBeDefined();
    expect(requestBody.context.commit_sha).toBeDefined();

    // Aserción de los headers de inyección de sandbox
    const headers = request.headers();
    expect(headers['x-git-branch']).toBe('worktrees/scheduler');
    expect(headers['x-worktree-path']).toBeDefined();
    expect(headers['x-commit-sha']).toBeDefined();
  });
});
