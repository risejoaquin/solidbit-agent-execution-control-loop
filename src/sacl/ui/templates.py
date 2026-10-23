"""SACL V1 Modular Apple-grade Decision Shell with SSE, Impact Drawer, and E2E Auth.

Implements an ultra-refined, responsive macOS/iPadOS styled modular dashboard,
providing sovereign human micro-decisions, visual impact diffs, SSE live streams,
and E2E technology authentication wizards.
"""

HTML_APPLICATION = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SolidBit · SACL Decision Shell Pro</title>
  <style>
    :root {
      --bg: #000000;
      --sidebar-bg: rgba(18, 18, 22, 0.82);
      --card-bg: rgba(24, 24, 30, 0.72);
      --card-elevated: rgba(32, 32, 40, 0.9);
      --drawer-bg: rgba(20, 20, 26, 0.95);
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
        radial-gradient(circle at 60% 0%, rgba(41, 151, 255, 0.08), transparent 45%),
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

    /* MAIN CONTENT */
    main {
      flex: 1;
      overflow-y: auto;
      padding: 28px 36px 80px 36px;
      position: relative;
    }

    /* TOP BAR */
    .top-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
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
    .sse-indicator {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      color: var(--green);
      background: rgba(48, 209, 88, 0.1);
      padding: 3px 9px;
      border-radius: 6px;
      border: 1px solid rgba(48, 209, 88, 0.2);
    }

    /* Segmented Control */
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
      margin-bottom: 24px;
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

    /* MODULES */
    .view-module {
      display: none;
      animation: fadeIn 0.2s ease-in-out;
    }
    .view-module.active { display: block; }
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
    .frosted-card:hover { border-color: var(--border-focus); }

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

    /* GATE CARDS */
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

    /* CONNECTIONS GRID */
    .connections-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
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
    .status-dot { width: 8px; height: 8px; border-radius: 50%; }
    .status-dot.connected { background: var(--green); box-shadow: 0 0 8px var(--green); }
    .status-dot.degraded { background: var(--orange); box-shadow: 0 0 8px var(--orange); }
    .status-dot.disconnected { background: var(--red); box-shadow: 0 0 8px var(--red); }

    /* SLIDE-OVER DRAWER (VISUAL IMPACT & DIFF) */
    .drawer-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.6);
      backdrop-filter: blur(8px);
      z-index: 1000;
      display: none;
      justify-content: flex-end;
    }
    .drawer-overlay.visible { display: flex; }
    .drawer-panel {
      width: 580px;
      background: var(--drawer-bg);
      border-left: 1px solid var(--border);
      height: 100%;
      padding: 32px;
      overflow-y: auto;
      box-shadow: -10px 0 40px rgba(0, 0, 0, 0.8);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      animation: slideIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes slideIn {
      from { transform: translateX(100%); }
      to { transform: translateX(0); }
    }
    .diff-block {
      background: rgba(0, 0, 0, 0.6);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 12px;
      line-height: 1.5;
      color: #a6accd;
      white-space: pre-wrap;
      overflow-x: auto;
    }
    .diff-add { color: var(--green); }
    .diff-del { color: var(--red); }

    /* AUTH MODAL */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(10px);
      z-index: 1100;
      display: none;
      align-items: center;
      justify-content: center;
    }
    .modal-overlay.visible { display: flex; }
    .modal-box {
      width: 440px;
      background: var(--card-elevated);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 28px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.9);
    }
    .input-field {
      width: 100%;
      background: rgba(0,0,0,0.5);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 10px 14px;
      color: #fff;
      font-family: var(--font);
      font-size: 13px;
      margin: 12px 0 16px 0;
      outline: none;
    }
    .input-field:focus { border-color: var(--accent); }

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
      z-index: 1200;
    }
    .toast.visible { transform: translateY(0); opacity: 1; }
  </style>
</head>
<body>

  <!-- SIDEBAR -->
  <aside>
    <div>
      <div class="brand">
        <div class="brand-mark">S</div>
        <div>
          <div class="brand-title">SolidBit SACL</div>
          <div style="font-size: 11px; color: var(--text-secondary);">Control Shell Pro</div>
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
          <span>🔌 Tecnologías & Auth</span>
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
        <div class="sse-indicator">
          <div class="pulse-dot"></div>
          <span>SSE LIVE PUSH</span>
        </div>
      </div>
      <div style="display: flex; gap: 12px; align-items: center;">
        <button class="btn btn-primary" onclick="launchCampaignModal()" style="padding: 6px 14px; font-size: 12px;">
          🚀 Iniciar Campaña / Sprint
        </button>
        <div class="segmented-control">
          <button class="segment-btn active" onclick="setMode('simple')">Simple</button>
          <button class="segment-btn" onclick="setMode('technical')">Technical</button>
          <button class="segment-btn" onclick="setMode('audit')">Audit</button>
        </div>
      </div>
    </div>

    <!-- Safety Banner -->
    <div class="safety-banner">
      <div style="display: flex; align-items: center; gap: 10px;">
        <div class="pulse-dot"></div>
        <span><strong>Safety Guardrails Activo:</strong> Sandboxed execution loop; non-blocking human approval.</span>
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
          <div class="metric-sub">Procesos seguros en reposo</div>
        </div>
      </div>

      <div class="section-header" style="margin-bottom: 14px;">
        <div>
          <div style="font-size: 16px; font-weight: 600;">Micro-Decisiones Inmediatas</div>
          <div style="font-size: 12px; color: var(--text-secondary);">Decisiones atómicas sin fricción técnica para el operador.</div>
        </div>
      </div>
      <div id="dash-gates-container"></div>
    </div>

    <!-- MODULE 2: GATES -->
    <div id="module-gates" class="view-module">
      <div class="section-header" style="margin-bottom: 14px;">
        <div>
          <div style="font-size: 16px; font-weight: 600;">Centro Soberano de Micro-Decisiones</div>
          <div style="font-size: 12px; color: var(--text-secondary);">Inspección visual de diffs, verificación de contratos e impacto antes de autorizar.</div>
        </div>
      </div>
      <div id="gates-full-list"></div>
    </div>

    <!-- MODULE 3: CAMPAIGNS & DAG -->
    <div id="module-campaigns" class="view-module">
      <div class="section-header" style="margin-bottom: 14px;">
        <div>
          <div style="font-size: 16px; font-weight: 600;">Topological DAG & Workorders</div>
          <div style="font-size: 12px; color: var(--text-secondary);">Fases A a F organizadas con dependencias y ownership de rutas.</div>
        </div>
        <button class="btn btn-primary" onclick="launchCampaignModal()" style="font-size: 12px;">+ Nueva Ejecución</button>
      </div>
      <div style="display: flex; flex-direction: column; gap: 10px;" id="dag-workorders-list"></div>
    </div>

    <!-- MODULE 4: CONNECTIONS & AUTH -->
    <div id="module-connections" class="view-module">
      <div class="section-header" style="margin-bottom: 14px;">
        <div>
          <div style="font-size: 16px; font-weight: 600;">Tecnologías & Inicio de Sesión E2E</div>
          <div style="font-size: 12px; color: var(--text-secondary);">Herramientas locales autenticadas y verificación integral con 1 clic.</div>
        </div>
        <button class="btn btn-secondary" onclick="loadConnections()" style="font-size: 12px;">⟳ Re-verificar Todo</button>
      </div>
      <div class="connections-grid" id="connections-full-grid"></div>
    </div>

    <!-- MODULE 5: RECOVERY -->
    <div id="module-recovery" class="view-module">
      <div class="frosted-card" id="recovery-status-card">Cargando estado de recuperación...</div>
    </div>

    <!-- MODULE 6: EVIDENCE -->
    <div id="module-evidence" class="view-module">
      <div class="frosted-card" id="evidence-container">Cargando evidencias...</div>
    </div>

    <!-- MODULE 7: CONTRACTS -->
    <div id="module-contracts" class="view-module">
      <div id="contracts-container"></div>
    </div>

    <!-- MODULE 8: DB INSPECTOR -->
    <div id="module-db" class="view-module">
      <div class="frosted-card" id="db-stats-container">Cargando estadísticas de base de datos...</div>
    </div>

  </main>

  <!-- VISUAL IMPACT & DIFF DRAWER -->
  <div class="drawer-overlay" id="impact-drawer">
    <div class="drawer-panel">
      <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; padding-bottom: 14px; border-bottom: 1px solid var(--border);">
          <div>
            <div style="font-size: 17px; font-weight: 700;" id="drawer-action-title">DEPLOY_STAGING_PREVIEW</div>
            <div style="font-size: 12px; color: var(--text-secondary);" id="drawer-req-id">REQ-SAMPLE</div>
          </div>
          <button class="btn btn-secondary" onclick="closeDrawer()" style="padding: 6px 12px;">✕ Cerrar</button>
        </div>

        <!-- Human Summary -->
        <div style="background: rgba(41, 151, 255, 0.1); border: 1px solid rgba(41, 151, 255, 0.25); border-radius: 12px; padding: 14px; margin-bottom: 20px;">
          <div style="font-size: 12px; font-weight: 600; color: var(--accent); margin-bottom: 4px;">RESUMEN DE NEGOCIO (SIN JERGA)</div>
          <p style="font-size: 13px; color: #fff; line-height: 1.5;" id="drawer-human-summary"></p>
        </div>

        <!-- Contract Semaphores -->
        <div style="margin-bottom: 20px;">
          <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 8px;">Semáforo de Contratos Congelados</div>
          <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;" id="drawer-contracts-grid"></div>
        </div>

        <!-- File Tree -->
        <div style="margin-bottom: 20px;">
          <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 8px;">Archivos Afectados</div>
          <div style="background: rgba(0,0,0,0.4); border: 1px solid var(--border); border-radius: 10px; padding: 10px;" id="drawer-file-tree"></div>
        </div>

        <!-- Diff Viewer -->
        <div>
          <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; color: var(--text-secondary); margin-bottom: 8px;">Diff Visual de Cambios</div>
          <div class="diff-block" id="drawer-diff-preview"></div>
        </div>
      </div>

      <!-- Drawer Actions -->
      <div style="padding-top: 20px; border-top: 1px solid var(--border); display: flex; gap: 10px; margin-top: 20px;">
        <button class="btn btn-primary" id="drawer-btn-approve" style="flex: 1; justify-content: center;">✓ Autorizar Acción</button>
        <button class="btn btn-secondary" id="drawer-btn-mobile" style="justify-content: center;">📱 Notificar Móvil</button>
        <button class="btn btn-danger" id="drawer-btn-reject" style="justify-content: center;">✕ Rechazar</button>
      </div>
    </div>
  </div>

  <!-- E2E AUTH MODAL -->
  <div class="modal-overlay" id="auth-modal">
    <div class="modal-box">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <h3 style="font-size: 16px; font-weight: 700;" id="auth-modal-title">Conectar Tecnología</h3>
        <button class="btn btn-secondary" onclick="closeAuthModal()" style="padding: 4px 10px;">✕</button>
      </div>
      <p style="font-size: 12px; color: var(--text-secondary); margin-bottom: 12px;" id="auth-modal-desc">
        Configura o valida tus credenciales locales para habilitar acceso seguro al orquestador.
      </p>
      <input type="password" id="auth-token-input" class="input-field" placeholder="Token, API Key o PAT..." />
      <div style="display: flex; gap: 10px; justify-content: flex-end;">
        <button class="btn btn-secondary" onclick="closeAuthModal()">Cancelar</button>
        <button class="btn btn-primary" onclick="submitAuth()">Guardar y Conectar E2E</button>
      </div>
    </div>
  </div>

  <div class="toast" id="toast">Operación ejecutada con éxito.</div>

  <script>
    let activeModule = 'dashboard';
    let currentMode = 'simple';
    let selectedAuthTool = null;
    let activeDrawerReqId = null;

    // SSE ENGINE
    function initSSE() {
      try {
        const es = new EventSource('/api/events/stream');
        es.addEventListener('snapshot', (e) => {
          const data = JSON.parse(e.data);
          updateDashboardUI(data);
        });
        es.addEventListener('gate_decided', (e) => {
          showToast('Decision Gate actualizado en tiempo real.');
          refreshSnapshot();
        });
        es.addEventListener('campaign_launched', (e) => {
          showToast('Campaña iniciada exitosamente.');
          refreshSnapshot();
        });
        es.addEventListener('connection_updated', (e) => {
          showToast('Conexión actualizada.');
          loadConnections();
        });
      } catch (err) {
        console.warn('SSE fallback to polling:', err);
      }
    }

    function switchModule(modId) {
      activeModule = modId;
      document.querySelectorAll('.nav-list .nav-item').forEach(item => item.classList.remove('active'));
      const map = ['dashboard', 'gates', 'campaigns', 'connections', 'recovery', 'evidence', 'contracts', 'db'];
      const idx = map.indexOf(modId);
      const items = document.querySelectorAll('.nav-list .nav-item');
      if (idx !== -1 && items[idx]) items[idx].classList.add('active');

      document.querySelectorAll('.view-module').forEach(m => m.classList.remove('active'));
      const target = document.getElementById('module-' + modId);
      if (target) target.classList.add('active');

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
            justification: 'Autorizado vía SACL Decision Shell Pro'
          })
        });
        const res = await resp.json();
        if (res.success) {
          showToast(`Gate ${decision}: ${res.message}`);
          closeDrawer();
          refreshSnapshot();
        } else {
          showToast(`Error: ${res.message}`);
        }
      } catch (err) {
        showToast(`Fallo de conexión: ${err.message}`);
      }
    }

    async function openImpactDrawer(requestId) {
      activeDrawerReqId = requestId;
      try {
        const resp = await fetch('/api/gates/impact?request_id=' + encodeURIComponent(requestId));
        const data = await resp.json();

        document.getElementById('drawer-action-title').textContent = data.action;
        document.getElementById('drawer-req-id').textContent = data.request_id;
        document.getElementById('drawer-human-summary').textContent = data.human_summary;

        // Contracts Grid
        const cGrid = document.getElementById('drawer-contracts-grid');
        cGrid.innerHTML = Object.entries(data.contracts_status || {}).map(([k, v]) => `
          <div style="background: rgba(255,255,255,0.04); padding: 8px 10px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
            <strong style="color: var(--accent);">${k}</strong>
            <span class="tag" style="background: rgba(48,209,88,0.15); color: var(--green);">${v}</span>
          </div>
        `).join('');

        // File Tree
        const fTree = document.getElementById('drawer-file-tree');
        fTree.innerHTML = (data.file_tree || []).map(f => `
          <div style="display: flex; justify-content: space-between; font-size: 11px; padding: 4px 0; border-bottom: 1px solid rgba(255,255,255,0.04);">
            <code>${f.path}</code>
            <div><span style="color: var(--green);">+${f.lines_added}</span> <span style="color: var(--red);">-${f.lines_removed}</span></div>
          </div>
        `).join('');

        // Diff
        document.getElementById('drawer-diff-preview').textContent = data.diff_preview;

        // Button events
        document.getElementById('drawer-btn-approve').onclick = () => submitGate(requestId, 'APPROVED');
        document.getElementById('drawer-btn-reject').onclick = () => submitGate(requestId, 'REJECTED');
        document.getElementById('drawer-btn-mobile').onclick = () => notifyMobile(requestId);

        document.getElementById('impact-drawer').classList.add('visible');
      } catch (e) {
        console.error(e);
      }
    }

    function closeDrawer() {
      document.getElementById('impact-drawer').classList.remove('visible');
    }

    async function notifyMobile(requestId) {
      try {
        const resp = await fetch('/api/gates/notify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ request_id: requestId, channel: 'resend' })
        });
        const res = await resp.json();
        showToast(res.message);
      } catch (e) {
        showToast('Error enviando notificación');
      }
    }

    function openAuthModal(toolId, toolName) {
      selectedAuthTool = toolId;
      document.getElementById('auth-modal-title').textContent = 'Autenticar ' + toolName;
      document.getElementById('auth-token-input').value = '';
      document.getElementById('auth-modal').classList.add('visible');
    }

    function closeAuthModal() {
      document.getElementById('auth-modal').classList.remove('visible');
      selectedAuthTool = null;
    }

    async function submitAuth() {
      if (!selectedAuthTool) return;
      const token = document.getElementById('auth-token-input').value.trim();
      try {
        const resp = await fetch('/api/connections/auth', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tool_id: selectedAuthTool, credentials: { token: token } })
        });
        const res = await resp.json();
        showToast(res.message);
        closeAuthModal();
        loadConnections();
      } catch (e) {
        showToast('Error al conectar');
      }
    }

    async function launchCampaignModal() {
      if (!confirm('¿Desea iniciar la ejecución de la campaña preparada con verificación automática de preflight?')) return;
      try {
        const resp = await fetch('/api/campaigns/launch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ campaign_id: 'SACL_ORCHESTRATOR_IMPLEMENTATION_CAMPAIGN_v1_PREPARED' })
        });
        const res = await resp.json();
        showToast(res.message);
        refreshSnapshot();
      } catch (e) {
        showToast('Fallo al lanzar campaña');
      }
    }

    async function refreshSnapshot() {
      try {
        const resp = await fetch('/api/snapshot?mode=' + currentMode);
        const data = await resp.json();
        updateDashboardUI(data);
      } catch (e) {
        console.error(e);
      }
    }

    function updateDashboardUI(data) {
      document.getElementById('top-project-name').textContent = data.active_project;
      document.getElementById('top-campaign-name').textContent = data.active_campaign;
      document.getElementById('dash-readiness').textContent = data.readiness_score + '%';
      document.getElementById('dash-campaign').textContent = data.active_campaign;
      document.getElementById('dash-gates').textContent = data.pending_gates.length;
      document.getElementById('dash-agents').textContent = data.agents.length;

      const badge = document.getElementById('sidebar-gates-badge');
      if (data.pending_gates.length > 0) {
        badge.textContent = data.pending_gates.length;
        badge.style.display = 'inline-block';
      } else {
        badge.style.display = 'none';
      }

      renderGates(data.pending_gates);
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
            <button class="btn btn-secondary" onclick="openImpactDrawer('${g.request_id}')">
              🔍 Ver Impacto & Diff
            </button>
            <button class="btn btn-secondary" onclick="notifyMobile('${g.request_id}')">
              📱 Enviar a mi Móvil
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
          <div style="display: flex; align-items: center; justify-content: space-between; padding: 14px 18px; background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px;">
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
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 14px; padding-top: 10px; border-top: 1px solid var(--border);">
              <span style="font-size: 10px; color: var(--text-tertiary); text-transform: uppercase;">${c.status}</span>
              <div style="display: flex; gap: 6px;">
                <button class="btn btn-secondary" onclick="testConnection('${c.id}')" style="padding: 3px 8px; font-size: 11px;">Test</button>
                <button class="btn btn-primary" onclick="openAuthModal('${c.id}', '${c.name}')" style="padding: 3px 8px; font-size: 11px;">Conectar E2E</button>
              </div>
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
          <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
            <thead>
              <tr style="text-align: left; border-bottom: 1px solid var(--border);">
                <th style="padding: 8px;">Archivo de Evidencia</th>
                <th style="padding: 8px;">Tipo</th>
                <th style="padding: 8px;">Tamaño</th>
                <th style="padding: 8px;">Acción</th>
              </tr>
            </thead>
            <tbody>
              ${data.files.map(f => `
                <tr style="border-bottom: 1px solid var(--border);">
                  <td style="padding: 8px;"><strong>${f.name}</strong></td>
                  <td style="padding: 8px;"><code>${f.type}</code></td>
                  <td style="padding: 8px;">${f.size_bytes} B</td>
                  <td style="padding: 8px;"><button class="btn btn-secondary" onclick="viewReport('${f.name}')" style="padding: 3px 8px; font-size: 11px;">Ver Contenido</button></td>
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

    // Startup
    initSSE();
    refreshSnapshot();
  </script>
</body>
</html>
"""
