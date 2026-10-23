"""SACL V1 Modular Apple-grade Decision Shell HTML/CSS/JS Application.

Implements an ultra-refined, responsive macOS/iPadOS styled modular dashboard,
providing sovereign human micro-decisions and full system observability.
"""

HTML_APPLICATION = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SolidBit · SACL Decision Shell</title>
  <style>
    :root {
      --bg: #000000;
      --sidebar-bg: rgba(18, 18, 22, 0.75);
      --card-bg: rgba(24, 24, 30, 0.7);
      --card-elevated: rgba(32, 32, 40, 0.85);
      --border: rgba(255, 255, 255, 0.08);
      --border-focus: rgba(255, 255, 255, 0.22);
      --text: #f5f5f7;
      --text-secondary: #86868b;
      --text-tertiary: #515154;
      --accent: #2997ff;
      --accent-hover: #0077ed;
      --accent-glow: rgba(41, 151, 255, 0.25);
      --green: #30d158;
      --green-glow: rgba(48, 209, 88, 0.25);
      --orange: #ff9f0a;
      --orange-glow: rgba(255, 159, 10, 0.25);
      --red: #ff453a;
      --red-glow: rgba(255, 69, 58, 0.25);
      --purple: #bf5af2;
      --font: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", Roboto, sans-serif;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: var(--font);
      -webkit-font-smoothing: antialiased;
      line-height: 1.45;
      overflow-x: hidden;
      display: flex;
      height: 100vh;
      background-image: 
        radial-gradient(circle at 60% 0%, rgba(41, 151, 255, 0.07), transparent 40%),
        radial-gradient(circle at 10% 30%, rgba(191, 90, 242, 0.04), transparent 30%);
    }

    /* SIDEBAR */
    aside {
      width: 250px;
      min-width: 250px;
      background: var(--sidebar-bg);
      backdrop-filter: blur(30px);
      -webkit-backdrop-filter: blur(30px);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 24px 14px;
      user-select: none;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 0 10px 24px 10px;
      border-bottom: 1px solid var(--border);
    }
    .brand-mark {
      width: 32px;
      height: 32px;
      border-radius: 9px;
      background: linear-gradient(135deg, #2997ff, #bf5af2);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 15px;
      color: #fff;
      box-shadow: 0 4px 14px rgba(41, 151, 255, 0.3);
    }
    .brand-title {
      font-size: 15px;
      font-weight: 600;
      letter-spacing: -0.02em;
    }

    .nav-group-title {
      font-size: 10px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-tertiary);
      padding: 16px 12px 6px 12px;
    }
    .nav-list {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 3px;
    }
    .nav-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 9px 12px;
      border-radius: 10px;
      font-size: 13px;
      font-weight: 500;
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .nav-item:hover {
      color: var(--text);
      background: rgba(255, 255, 255, 0.05);
    }
    .nav-item.active {
      color: var(--text);
      background: rgba(255, 255, 255, 0.12);
      font-weight: 600;
    }
    .nav-badge {
      font-size: 10px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 12px;
      background: rgba(255, 159, 10, 0.2);
      color: var(--orange);
      border: 1px solid rgba(255, 159, 10, 0.35);
    }

    /* MAIN CONTENT AREA */
    main {
      flex: 1;
      overflow-y: auto;
      padding: 28px 36px 80px 36px;
    }

    /* TOP BAR */
    .top-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 26px;
    }
    .top-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .project-pill {
      font-size: 12px;
      font-weight: 600;
      padding: 4px 12px;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.08);
      color: var(--text);
      border: 1px solid var(--border);
    }

    /* Apple Segmented Control */
    .segmented-control {
      background: rgba(255, 255, 255, 0.06);
      padding: 3px;
      border-radius: 10px;
      display: flex;
      gap: 2px;
      border: 1px solid var(--border);
    }
    .segment-btn {
      background: transparent;
      border: none;
      color: var(--text-secondary);
      font-family: var(--font);
      font-size: 12px;
      font-weight: 500;
      padding: 6px 14px;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .segment-btn:hover { color: var(--text); }
    .segment-btn.active {
      background: rgba(255, 255, 255, 0.16);
      color: var(--text);
      box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    }

    /* Safety Shield Banner */
    .safety-banner {
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: linear-gradient(90deg, rgba(48, 209, 88, 0.08), rgba(41, 151, 255, 0.04));
      border: 1px solid rgba(48, 209, 88, 0.2);
      border-radius: 14px;
      padding: 12px 18px;
      margin-bottom: 26px;
      backdrop-filter: blur(20px);
      font-size: 12px;
    }
    .pulse-dot {
      width: 8px; height: 8px; border-radius: 50%;
      background: var(--green);
      box-shadow: 0 0 10px var(--green);
      animation: pulse 2s infinite ease-in-out;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.5; transform: scale(0.85); }
    }
    .safety-tags { display: flex; gap: 8px; }
    .tag {
      font-size: 11px;
      font-weight: 600;
      padding: 3px 9px;
      border-radius: 6px;
      background: rgba(48, 209, 88, 0.12);
      color: var(--green);
      border: 1px solid rgba(48, 209, 88, 0.25);
    }

    /* MODULE CONTAINERS */
    .view-module {
      display: none;
      animation: fadeIn 0.2s ease-in-out;
    }
    .view-module.active {
      display: block;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* CARDS */
    .frosted-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 22px;
      backdrop-filter: blur(24px);
      margin-bottom: 20px;
      transition: all 0.2s ease;
    }
    .frosted-card:hover {
      border-color: var(--border-focus);
    }

    /* METRICS GRID */
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-bottom: 24px;
    }
    .metric-title {
      font-size: 11px;
      font-weight: 500;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.06em;
      margin-bottom: 6px;
    }
    .metric-value {
      font-size: 26px;
      font-weight: 700;
      letter-spacing: -0.03em;
    }
    .metric-sub {
      font-size: 12px;
      color: var(--text-secondary);
      margin-top: 4px;
    }

    /* SECTION HEADERS */
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }
    .section-title {
      font-size: 16px;
      font-weight: 600;
      letter-spacing: -0.01em;
    }
    .section-sub {
      font-size: 12px;
      color: var(--text-secondary);
    }

    /* DECISION GATE CARD */
    .gate-card {
      background: var(--card-elevated);
      border: 1px solid rgba(255, 159, 10, 0.35);
      border-radius: 18px;
      padding: 24px;
      margin-bottom: 16px;
      backdrop-filter: blur(30px);
      box-shadow: 0 8px 32px rgba(255, 159, 10, 0.08);
      position: relative;
      overflow: hidden;
    }
    .gate-card::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0; height: 3px;
      background: linear-gradient(90deg, var(--orange), var(--red));
    }
    .risk-badge {
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 0.06em;
      padding: 3px 9px;
      border-radius: 6px;
      text-transform: uppercase;
    }
    .risk-badge.high { background: rgba(255, 69, 58, 0.15); color: var(--red); border: 1px solid rgba(255, 69, 58, 0.3); }
    .risk-badge.medium { background: rgba(255, 159, 10, 0.15); color: var(--orange); border: 1px solid rgba(255, 159, 10, 0.3); }
    .risk-badge.low { background: rgba(48, 209, 88, 0.15); color: var(--green); border: 1px solid rgba(48, 209, 88, 0.3); }

    /* BUTTONS */
    .btn {
      font-family: var(--font);
      font-size: 13px;
      font-weight: 600;
      padding: 9px 18px;
      border-radius: 10px;
      border: none;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .btn:active { transform: scale(0.97); }
    .btn-primary {
      background: var(--accent);
      color: #fff;
      box-shadow: 0 4px 14px var(--accent-glow);
    }
    .btn-primary:hover { background: var(--accent-hover); }
    .btn-secondary {
      background: rgba(255, 255, 255, 0.08);
      color: var(--text);
      border: 1px solid var(--border);
    }
    .btn-secondary:hover { background: rgba(255, 255, 255, 0.14); }
    .btn-danger {
      background: rgba(255, 69, 58, 0.12);
      color: var(--red);
      border: 1px solid rgba(255, 69, 58, 0.25);
    }
    .btn-danger:hover { background: rgba(255, 69, 58, 0.2); }

    /* CONNECTIONS GRID */
    .connections-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
    }
    .conn-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .status-dot {
      width: 8px; height: 8px; border-radius: 50%;
    }
    .status-dot.connected { background: var(--green); box-shadow: 0 0 8px var(--green); }
    .status-dot.degraded { background: var(--orange); box-shadow: 0 0 8px var(--orange); }
    .status-dot.disconnected { background: var(--red); box-shadow: 0 0 8px var(--red); }

    /* DAG WORKORDERS LIST */
    .dag-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .dag-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 18px;
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
    }

    /* TABLE */
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      text-align: left;
    }
    th {
      background: rgba(255, 255, 255, 0.03);
      color: var(--text-secondary);
      font-weight: 500;
      padding: 12px 16px;
      border-bottom: 1px solid var(--border);
      text-transform: uppercase;
      font-size: 11px;
    }
    td {
      padding: 12px 16px;
      border-bottom: 1px solid var(--border);
    }

    /* TOAST */
    .toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: var(--card-elevated);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 12px 20px;
      border-radius: 12px;
      box-shadow: 0 8px 30px rgba(0,0,0,0.6);
      backdrop-filter: blur(20px);
      font-size: 13px;
      transform: translateY(100px);
      opacity: 0;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      z-index: 999;
    }
    .toast.visible { transform: translateY(0); opacity: 1; }
  </style>
</head>
<body>

  <!-- MODULAR SIDEBAR -->
  <aside>
    <div>
      <div class="brand">
        <div class="brand-mark">S</div>
        <div>
          <div class="brand-title">SolidBit SACL</div>
          <div style="font-size: 11px; color: var(--text-secondary);">Control Shell v1.0</div>
        </div>
      </div>

      <div class="nav-group-title">Navegación</div>
      <ul class="nav-list">
        <li class="nav-item active" onclick="switchModule('dashboard')">
          <span>📊 Dashboard General</span>
        </li>
        <li class="nav-item" onclick="switchModule('gates')">
          <span>🛡️ Decision Gates</span>
          <span class="nav-badge" id="sidebar-gates-badge" style="display: none;">0</span>
        </li>
        <li class="nav-item" onclick="switchModule('campaigns')">
          <span>⚡ Campañas & DAG</span>
        </li>
        <li class="nav-item" onclick="switchModule('connections')">
          <span>🔌 Tecnologías & CLIs</span>
        </li>
      </ul>

      <div class="nav-group-title">Gobernanza & Auditoría</div>
      <ul class="nav-list">
        <li class="nav-item" onclick="switchModule('recovery')">
          <span>🩺 Centro de Recuperación</span>
        </li>
        <li class="nav-item" onclick="switchModule('evidence')">
          <span>📜 Evidencias & Reportes</span>
        </li>
        <li class="nav-item" onclick="switchModule('contracts')">
          <span>⚖️ Contratos Congelados</span>
        </li>
        <li class="nav-item" onclick="switchModule('db')">
          <span>🗄️ Inspector SQLite</span>
        </li>
      </ul>
    </div>

    <div style="padding: 12px; border-top: 1px solid var(--border); font-size: 11px; color: var(--text-tertiary);">
      Zero-unauthorized-deploy guardrails activos.
    </div>
  </aside>

  <!-- MAIN VIEWPORT -->
  <main>
    <!-- Top Bar -->
    <div class="top-bar">
      <div class="top-left">
        <span class="project-pill" id="top-project-name">Stable-Ecommerce</span>
        <span style="font-size: 12px; color: var(--text-secondary);" id="top-campaign-name">Productization V1</span>
      </div>
      <div class="segmented-control">
        <button class="segment-btn active" onclick="setMode('simple')">Simple</button>
        <button class="segment-btn" onclick="setMode('technical')">Technical</button>
        <button class="segment-btn" onclick="setMode('audit')">Audit</button>
      </div>
    </div>

    <!-- Safety Banner -->
    <div class="safety-banner">
      <div style="display: flex; align-items: center; gap: 10px;">
        <div class="pulse-dot"></div>
        <span><strong>Safety Guardrails Activo:</strong> Loop sandboxed sin mutación a producción.</span>
      </div>
      <div class="safety-tags">
        <span class="tag">PROD DEPLOY: BLOCKED</span>
        <span class="tag">RULESETS: LOCKED</span>
      </div>
    </div>

    <!-- MODULE 1: DASHBOARD -->
    <div id="module-dashboard" class="view-module active">
      <div class="metrics-grid">
        <div class="frosted-card">
          <div class="metric-title">System Readiness</div>
          <div class="metric-value" id="dash-readiness" style="color: var(--green);">--%</div>
          <div class="metric-sub">Ecosistema validado</div>
        </div>
        <div class="frosted-card">
          <div class="metric-title">Active Campaign</div>
          <div class="metric-value" id="dash-campaign" style="font-size: 18px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">--</div>
          <div class="metric-sub">DAG de 9 workorders</div>
        </div>
        <div class="frosted-card">
          <div class="metric-title">Decision Gates</div>
          <div class="metric-value" id="dash-gates" style="color: var(--orange);">0</div>
          <div class="metric-sub">Requiere micro-decisión</div>
        </div>
        <div class="frosted-card">
          <div class="metric-title">Agent Fleet</div>
          <div class="metric-value" id="dash-agents">0</div>
          <div class="metric-sub">Procesos en reposo seguro</div>
        </div>
      </div>

      <div class="section-header">
        <div>
          <div class="section-title">Micro-Decisiones Inmediatas</div>
          <div class="section-sub">Decisiones predefinidas sin bloqueo técnico para el operador.</div>
        </div>
      </div>
      <div id="dash-gates-container"></div>
    </div>

    <!-- MODULE 2: GATES -->
    <div id="module-gates" class="view-module">
      <div class="section-header">
        <div>
          <div class="section-title">Centro Soberano de Micro-Decisiones</div>
          <div class="section-sub">Acciones precalificadas por la arquitectura que exigen consentimiento humano.</div>
        </div>
      </div>
      <div id="gates-full-list"></div>
    </div>

    <!-- MODULE 3: CAMPAIGNS & DAG -->
    <div id="module-campaigns" class="view-module">
      <div class="section-header">
        <div>
          <div class="section-title">Topological DAG & Workorders</div>
          <div class="section-sub">Flujo de fases A a F con dependencias y ownership de rutas.</div>
        </div>
      </div>
      <div class="dag-list" id="dag-workorders-list"></div>
    </div>

    <!-- MODULE 4: CONNECTIONS -->
    <div id="module-connections" class="view-module">
      <div class="section-header">
        <div>
          <div class="section-title">Tecnologías & CLIs Conectadas</div>
          <div class="section-sub">Herramientas locales del desarrollador y servicios cloud integrados.</div>
        </div>
        <button class="btn btn-secondary" onclick="loadConnections()">⟳ Re-verificar Todo</button>
      </div>
      <div class="connections-grid" id="connections-full-grid"></div>
    </div>

    <!-- MODULE 5: RECOVERY -->
    <div id="module-recovery" class="view-module">
      <div class="section-header">
        <div>
          <div class="section-title">Centro de Recuperación & Crash Consistency</div>
          <div class="section-sub">Detección de corridas interrumpidas, limpieza de locks y reanudación segura.</div>
        </div>
      </div>
      <div class="frosted-card" id="recovery-status-card">
        Cargando estado de recuperación...
      </div>
    </div>

    <!-- MODULE 6: EVIDENCE -->
    <div id="module-evidence" class="view-module">
      <div class="section-header">
        <div>
          <div class="section-title">Centro de Evidencias & Auditoría</div>
          <div class="section-sub">Paquetes de auditoría generados, diffs y digests criptográficos SHA-256.</div>
        </div>
      </div>
      <div class="frosted-card" id="evidence-container">
        Cargando evidencias...
      </div>
    </div>

    <!-- MODULE 7: CONTRACTS -->
    <div id="module-contracts" class="view-module">
      <div class="section-header">
        <div>
          <div class="section-title">Contratos Congelados & Políticas SDLC</div>
          <div class="section-sub">Invariantes inviolables (DR-INV-001, DR-PAY-001) y 6 Gates obligatorios.</div>
        </div>
      </div>
      <div id="contracts-container"></div>
    </div>

    <!-- MODULE 8: DB INSPECTOR -->
    <div id="module-db" class="view-module">
      <div class="section-header">
        <div>
          <div class="section-title">Inspector de Base de Datos Operacional (SQLite WAL)</div>
          <div class="section-sub">Métricas de almacenamiento y registros inmutables de auditoría en sacl_ops.db.</div>
        </div>
      </div>
      <div class="frosted-card" id="db-stats-container">
        Cargando estadísticas de base de datos...
      </div>
    </div>

  </main>

  <div class="toast" id="toast">Operación ejecutada con éxito.</div>

  <script>
    let activeModule = 'dashboard';
    let currentMode = 'simple';

    function switchModule(modId) {
      activeModule = modId;
      document.querySelectorAll('.nav-item').forEach((item, idx) => {
        item.classList.remove('active');
      });
      // highlight active sidebar
      const navItems = document.querySelectorAll('.nav-list .nav-item');
      const map = ['dashboard', 'gates', 'campaigns', 'connections', 'recovery', 'evidence', 'contracts', 'db'];
      const targetIdx = map.indexOf(modId);
      if (targetIdx !== -1 && navItems[targetIdx]) {
        navItems[targetIdx].classList.add('active');
      }

      document.querySelectorAll('.view-module').forEach(m => m.classList.remove('active'));
      const activeEl = document.getElementById('module-' + modId);
      if (activeEl) activeEl.classList.add('active');

      // Trigger module loader
      if (modId === 'campaigns') loadCampaigns();
      if (modId === 'connections') loadConnections();
      if (modId === 'recovery') loadRecovery();
      if (modId === 'evidence') loadEvidence();
      if (modId === 'contracts') loadContracts();
      if (modId === 'db') loadDB();
    }

    function setMode(mode) {
      currentMode = mode;
      document.querySelectorAll('.segment-btn').forEach(btn => {
        btn.classList.toggle('active', btn.textContent.toLowerCase() === mode);
      });
      refreshSnapshot();
    }

    function showToast(msg) {
      const toast = document.getElementById('toast');
      toast.textContent = msg;
      toast.classList.add('visible');
      setTimeout(() => toast.classList.remove('visible'), 3200);
    }

    async function submitGate(requestId, decision) {
      try {
        const resp = await fetch('/api/gates/decide', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            request_id: requestId,
            decision: decision,
            justification: 'Autorizado vía SACL Modular Decision Shell'
          })
        });
        const res = await resp.json();
        if (res.success) {
          showToast(`Gate ${decision}: ${res.message}`);
          refreshSnapshot();
        } else {
          showToast(`Error: ${res.message}`);
        }
      } catch (err) {
        showToast(`Fallo de conexión: ${err.message}`);
      }
    }

    async function refreshSnapshot() {
      try {
        const resp = await fetch('/api/snapshot?mode=' + currentMode);
        const data = await resp.json();

        // Top bar & metrics
        document.getElementById('top-project-name').textContent = data.active_project;
        document.getElementById('top-campaign-name').textContent = data.active_campaign;
        document.getElementById('dash-readiness').textContent = data.readiness_score + '%';
        document.getElementById('dash-campaign').textContent = data.active_campaign;
        document.getElementById('dash-gates').textContent = data.pending_gates.length;
        document.getElementById('dash-agents').textContent = data.agents.length;

        // Sidebar badge
        const badge = document.getElementById('sidebar-gates-badge');
        if (data.pending_gates.length > 0) {
          badge.textContent = data.pending_gates.length;
          badge.style.display = 'inline-block';
        } else {
          badge.style.display = 'none';
        }

        // Render gates
        renderGates(data.pending_gates);
      } catch (e) {
        console.error('Error fetching snapshot:', e);
      }
    }

    function renderGates(gates) {
      const dashContainer = document.getElementById('dash-gates-container');
      const fullList = document.getElementById('gates-full-list');

      if (!gates || gates.length === 0) {
        const emptyHtml = `
          <div class="frosted-card" style="text-align: center; color: var(--text-secondary); padding: 36px;">
            ✓ <strong>Cero puertas de decisión pendientes.</strong> El orquestador opera sin cuellos de botella humanos.
          </div>
        `;
        dashContainer.innerHTML = emptyHtml;
        fullList.innerHTML = emptyHtml;
        return;
      }

      const html = gates.map(g => `
        <div class="gate-card">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 10px;">
              <span class="risk-badge ${g.risk_level.toLowerCase()}">${g.risk_level} RISK</span>
              <strong style="font-size: 16px;">${g.action}</strong>
              <code style="font-size: 12px; background: rgba(0,0,0,0.4); padding: 2px 7px; border-radius: 5px; color: var(--text-secondary);">${g.scope}</code>
            </div>
            <span style="font-size: 11px; color: var(--text-tertiary);">Job: ${g.job_id}</span>
          </div>
          <p style="font-size: 13px; color: var(--text); margin-bottom: 16px;">
            ${g.evidence_summary}
          </p>
          <div style="display: flex; gap: 10px; padding-top: 14px; border-top: 1px solid var(--border);">
            <button class="btn btn-primary" onclick="submitGate('${g.request_id}', 'APPROVED')">
              ✓ Autorizar Acción
            </button>
            <button class="btn btn-secondary" onclick="showToast('Solicitado informe técnico y diff de pruebas...')">
              ⟳ Solicitar Más Evidencia
            </button>
            <button class="btn btn-danger" onclick="submitGate('${g.request_id}', 'REJECTED')">
              ✕ Rechazar / Pausa Segura
            </button>
          </div>
        </div>
      `).join('');

      dashContainer.innerHTML = html;
      fullList.innerHTML = html;
    }

    async function loadCampaigns() {
      try {
        const resp = await fetch('/api/campaigns');
        const data = await resp.json();
        const list = document.getElementById('dag-workorders-list');
        list.innerHTML = data.workorders.map(w => `
          <div class="dag-item">
            <div>
              <div style="display: flex; align-items: center; gap: 8px;">
                <span class="tag" style="background: rgba(255,255,255,0.08); color: #fff;">${w.phase}</span>
                <strong>${w.id}</strong>
                <span style="font-size: 13px; color: var(--text);">${w.title}</span>
              </div>
              <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">
                Agente asignado: <code>${w.agent}</code> | Rutas: <code>${(w.owned_paths || []).join(', ') || 'N/A'}</code>
              </div>
            </div>
            <div>
              <span class="tag" style="background: rgba(48, 209, 88, 0.15); color: var(--green);">${w.status}</span>
            </div>
          </div>
        `).join('');
      } catch (e) {
        console.error(e);
      }
    }

    async function loadConnections() {
      try {
        const resp = await fetch('/api/connections');
        const data = await resp.json();
        const grid = document.getElementById('connections-full-grid');
        grid.innerHTML = data.connections.map(c => `
          <div class="conn-card">
            <div>
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <strong style="font-size: 13px;">${c.name}</strong>
                <div class="status-dot ${c.status}"></div>
              </div>
              <div style="font-size: 11px; color: var(--text-secondary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                ${c.version || c.error_message || 'Verificado'}
              </div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px; padding-top: 8px; border-top: 1px solid var(--border);">
              <span style="font-size: 10px; color: var(--text-tertiary); text-transform: uppercase;">${c.status}</span>
              <button class="btn btn-secondary" onclick="testConnection('${c.id}')" style="padding: 3px 8px; font-size: 10px;">Test</button>
            </div>
          </div>
        `).join('');
      } catch (e) {
        console.error(e);
      }
    }

    async function testConnection(toolId) {
      try {
        const resp = await fetch('/api/connections/test', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tool_id: toolId })
        });
        const res = await resp.json();
        showToast(res.success ? `Conexión a ${toolId} verificada.` : `Error: ${res.connection.error_message}`);
        loadConnections();
      } catch (e) {
        showToast('Error al probar conexión');
      }
    }

    async function loadRecovery() {
      try {
        const resp = await fetch('/api/recovery');
        const data = await resp.json();
        document.getElementById('recovery-status-card').innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
            <strong style="font-size: 15px;">Estado de Consistencia Operativa</strong>
            <span class="tag" style="background: rgba(48, 209, 88, 0.15); color: var(--green);">${data.classification}</span>
          </div>
          <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 14px;">
            ${data.recommended_action}
          </p>
          <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; font-size: 12px;">
            <div style="background: rgba(255,255,255,0.04); padding: 10px; border-radius: 8px;">
              <div style="color: var(--text-secondary);">Corridas Interrumpidas</div>
              <div style="font-size: 16px; font-weight: 700; color: #fff;">${data.interrupted_runs.length}</div>
            </div>
            <div style="background: rgba(255,255,255,0.04); padding: 10px; border-radius: 8px;">
              <div style="color: var(--text-secondary);">Leases Activos</div>
              <div style="font-size: 16px; font-weight: 700; color: #fff;">${data.active_leases_count}</div>
            </div>
            <div style="background: rgba(255,255,255,0.04); padding: 10px; border-radius: 8px;">
              <div style="color: var(--text-secondary);">Dirty Root Prevention</div>
              <div style="font-size: 16px; font-weight: 700; color: var(--green);">ACTIVA</div>
            </div>
          </div>
        `;
      } catch (e) {
        console.error(e);
      }
    }

    async function loadEvidence() {
      try {
        const resp = await fetch('/api/evidence');
        const data = await resp.json();
        const container = document.getElementById('evidence-container');
        if (!data.files || data.files.length === 0) {
          container.innerHTML = '<div style="color: var(--text-secondary);">No hay paquetes de evidencia generados aún.</div>';
          return;
        }
        container.innerHTML = `
          <table>
            <thead>
              <tr><th>Archivo de Evidencia</th><th>Tipo</th><th>Tamaño</th><th>Acción</th></tr>
            </thead>
            <tbody>
              ${data.files.map(f => `
                <tr>
                  <td><strong>${f.name}</strong></td>
                  <td><code>${f.type}</code></td>
                  <td>${f.size_bytes} B</td>
                  <td><button class="btn btn-secondary" onclick="viewReport('${f.name}')" style="padding: 3px 8px; font-size: 11px;">Ver Contenido</button></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        `;
      } catch (e) {
        console.error(e);
      }
    }

    async function viewReport(name) {
      try {
        const resp = await fetch('/api/evidence/view?file=' + encodeURIComponent(name));
        const res = await resp.json();
        if (res.found) {
          alert(`Reporte: ${res.name}\\nSHA-256: ${res.sha256}\\n\\n${res.content.substring(0, 500)}...`);
        }
      } catch (e) {}
    }

    async function loadContracts() {
      try {
        const resp = await fetch('/api/contracts');
        const data = await resp.json();
        const container = document.getElementById('contracts-container');
        container.innerHTML = `
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin-bottom: 24px;">
            ${data.contracts.map(c => `
              <div class="frosted-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                  <strong style="color: var(--accent);">${c.id}</strong>
                  <span class="tag" style="background: rgba(48,209,88,0.15); color: var(--green);">${c.status}</span>
                </div>
                <div style="font-size: 14px; font-weight: 600; margin-bottom: 4px;">${c.title}</div>
                <p style="font-size: 12px; color: var(--text-secondary);">${c.description}</p>
              </div>
            `).join('')}
          </div>
          <div class="frosted-card">
            <h4 style="font-size: 14px; font-weight: 600; margin-bottom: 12px;">Mandatory SDLC Decision Gates (0 a 5)</h4>
            <div style="display: flex; flex-direction: column; gap: 8px; font-size: 12px;">
              ${data.decision_gates.map(g => `
                <div style="display: flex; gap: 12px; padding: 8px 12px; background: rgba(255,255,255,0.03); border-radius: 8px;">
                  <strong style="color: var(--orange);">${g.id}</strong>
                  <div><strong>${g.name}:</strong> <span style="color: var(--text-secondary);">${g.rule}</span></div>
                </div>
              `).join('')}
            </div>
          </div>
        `;
      } catch (e) {
        console.error(e);
      }
    }

    async function loadDB() {
      try {
        const resp = await fetch('/api/db/stats');
        const data = await resp.json();
        const container = document.getElementById('db-stats-container');
        const tables = Object.entries(data.tables || {});
        container.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <strong style="font-size: 14px;">Estado de Almacenamiento: ${data.status}</strong>
            <span class="tag">${data.total_records} Registros Totales</span>
          </div>
          <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;">
            ${tables.map(([t, count]) => `
              <div style="background: rgba(255,255,255,0.04); padding: 12px; border-radius: 10px; border: 1px solid var(--border);">
                <div style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase;">${t}</div>
                <div style="font-size: 18px; font-weight: 700; color: #fff; margin-top: 4px;">${count}</div>
              </div>
            `).join('')}
          </div>
        `;
      } catch (e) {
        console.error(e);
      }
    }

    // Auto-refresh snapshot every 4s
    refreshSnapshot();
    setInterval(refreshSnapshot, 4000);
  </script>
</body>
</html>
"""
