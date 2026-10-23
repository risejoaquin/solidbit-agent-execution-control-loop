"""SACL V1 Apple-grade Decision Shell with Full SDLC, Lucide Icons, Chart.js, and Email Gateway.

Implements an ultra-refined, responsive macOS/iPadOS styled modular dashboard,
providing sovereign human micro-decisions, visual impact diffs, real-time push streams,
project switcher, AI model selector, visual DAG designer, live task telemetry, and
bi-directional email automation (lucilfer@selfcaresinners.com <-> lawlieeet@outlook.es).
"""

HTML_APPLICATION = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SolidBit · SACL Decision Shell Pro</title>
  <!-- Apple HIG Fonts & Modern Styling -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <!-- Lucide Icons Library (Security audited, zero basic unicode emojis) -->
  <script src="https://unpkg.com/lucide@latest"></script>
  <!-- Chart.js Library (Security audited CDN) -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --bg: #000000;
      --sidebar-bg: rgba(18, 18, 22, 0.88);
      --card-bg: rgba(24, 24, 30, 0.75);
      --card-elevated: rgba(32, 32, 40, 0.92);
      --drawer-bg: rgba(20, 20, 26, 0.96);
      --border: rgba(255, 255, 255, 0.08);
      --border-focus: rgba(255, 255, 255, 0.24);
      --text: #f5f5f7;
      --text-secondary: #86868b;
      --text-tertiary: #515154;
      --accent: #2997ff;
      --accent-glow: rgba(41, 151, 255, 0.28);
      --success: #30d158;
      --success-glow: rgba(48, 209, 88, 0.25);
      --warning: #ffd60a;
      --danger: #ff453a;
      --danger-glow: rgba(255, 69, 58, 0.25);
      --purple: #bf5af2;
      --radius-sm: 8px;
      --radius-md: 14px;
      --radius-lg: 20px;
      --radius-xl: 28px;
      --font: "Inter", -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", sans-serif;
      --font-mono: "JetBrains Mono", SFMono-Regular, Menlo, monospace;
      --transition: all 0.24s cubic-bezier(0.16, 1, 0.3, 1);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: var(--font);
      height: 100vh;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      -webkit-font-smoothing: antialiased;
    }

    /* TOP HEADER BAR */
    header.mac-header {
      height: 60px;
      background: rgba(12, 12, 14, 0.85);
      backdrop-filter: blur(28px);
      -webkit-backdrop-filter: blur(28px);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
      z-index: 50;
      flex-shrink: 0;
    }

    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .brand-mark {
      display: flex;
      align-items: center;
      gap: 10px;
      text-decoration: none;
      color: var(--text);
    }
    .brand-logo-badge {
      width: 32px;
      height: 32px;
      border-radius: 9px;
      background: linear-gradient(135deg, #2997ff 0%, #bf5af2 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 0 16px var(--accent-glow);
    }
    .brand-logo-badge i { color: #fff; width: 18px; height: 18px; }
    .brand-title {
      font-size: 15px;
      font-weight: 600;
      letter-spacing: -0.02em;
    }
    .brand-subtitle {
      font-size: 11px;
      font-weight: 500;
      color: var(--text-secondary);
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }

    /* PROJECT & MODEL SELECTORS IN HEADER */
    .header-controls {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .header-pill-dropdown {
      position: relative;
    }
    .header-pill-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border);
      border-radius: 20px;
      color: var(--text);
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      transition: var(--transition);
    }
    .header-pill-btn:hover {
      background: rgba(255, 255, 255, 0.1);
      border-color: var(--border-focus);
    }
    .header-pill-btn i { width: 14px; height: 14px; color: var(--accent); }
    .header-pill-btn i.chevron { width: 12px; height: 12px; color: var(--text-secondary); margin-left: 2px; }

    .dropdown-menu {
      position: absolute;
      top: calc(100% + 8px);
      left: 0;
      min-width: 260px;
      background: var(--drawer-bg);
      backdrop-filter: blur(30px);
      -webkit-backdrop-filter: blur(30px);
      border: 1px solid var(--border-focus);
      border-radius: var(--radius-md);
      padding: 6px;
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.8);
      display: none;
      z-index: 100;
    }
    .dropdown-menu.show { display: block; animation: dropFade 0.18s ease-out; }
    @keyframes dropFade { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }

    .dropdown-item {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 12px;
      border-radius: var(--radius-sm);
      color: var(--text);
      font-size: 13px;
      cursor: pointer;
      transition: var(--transition);
      text-decoration: none;
    }
    .dropdown-item:hover {
      background: rgba(255, 255, 255, 0.08);
      color: #fff;
    }
    .dropdown-item.active {
      background: rgba(41, 151, 255, 0.16);
      color: var(--accent);
      font-weight: 600;
    }
    .dropdown-item i { width: 16px; height: 16px; }

    .header-right {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .sse-indicator {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 4px 12px;
      background: rgba(48, 209, 88, 0.1);
      border: 1px solid rgba(48, 209, 88, 0.3);
      border-radius: 20px;
      font-size: 12px;
      color: var(--success);
      font-weight: 500;
    }
    .pulse-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--success);
      box-shadow: 0 0 10px var(--success);
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0% { transform: scale(0.95); opacity: 0.8; }
      50% { transform: scale(1.3); opacity: 1; }
      100% { transform: scale(0.95); opacity: 0.8; }
    }

    /* MAIN APPLICATION LAYOUT */
    .app-body {
      display: flex;
      flex: 1;
      height: calc(100vh - 60px);
      overflow: hidden;
    }

    /* SIDEBAR NAVIGATION */
    aside.mac-sidebar {
      width: 250px;
      background: var(--sidebar-bg);
      backdrop-filter: blur(28px);
      -webkit-backdrop-filter: blur(28px);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      padding: 16px 12px;
      gap: 6px;
      flex-shrink: 0;
      overflow-y: auto;
    }

    .sidebar-section-title {
      font-size: 10px;
      font-weight: 600;
      color: var(--text-tertiary);
      letter-spacing: 0.08em;
      text-transform: uppercase;
      padding: 10px 12px 4px 12px;
    }

    .nav-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 14px;
      border-radius: var(--radius-sm);
      color: var(--text-secondary);
      font-size: 13px;
      font-weight: 500;
      text-decoration: none;
      cursor: pointer;
      transition: var(--transition);
    }
    .nav-item:hover {
      background: rgba(255, 255, 255, 0.06);
      color: var(--text);
    }
    .nav-item.active {
      background: rgba(255, 255, 255, 0.12);
      color: #fff;
      font-weight: 600;
    }
    .nav-item i { width: 17px; height: 17px; }
    .nav-item .badge {
      margin-left: auto;
      background: rgba(255, 255, 255, 0.1);
      padding: 2px 8px;
      border-radius: 10px;
      font-size: 11px;
      font-weight: 600;
    }
    .nav-item.active .badge {
      background: var(--accent);
      color: #fff;
    }

    /* MAIN VIEW CONTAINER */
    main.mac-content {
      flex: 1;
      overflow-y: auto;
      padding: 28px 36px 48px 36px;
      background: radial-gradient(circle at 50% 0%, rgba(41, 151, 255, 0.04) 0%, transparent 60%);
    }

    .tab-content { display: none; }
    .tab-content.active { display: block; animation: viewFade 0.25s ease-out; }
    @keyframes viewFade { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

    /* VIEW HEADER */
    .view-header {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border);
    }
    .view-title-wrap h1 {
      font-size: 26px;
      font-weight: 700;
      letter-spacing: -0.03em;
      color: #fff;
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .view-title-wrap p {
      font-size: 13px;
      color: var(--text-secondary);
    }

    /* METRIC CARDS GRID */
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 18px;
      margin-bottom: 28px;
    }
    .metric-card {
      background: var(--card-bg);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 20px;
      transition: var(--transition);
      position: relative;
      overflow: hidden;
    }
    .metric-card:hover {
      border-color: var(--border-focus);
      transform: translateY(-2px);
    }
    .metric-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }
    .metric-header span {
      font-size: 12px;
      font-weight: 500;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .metric-header i { width: 18px; height: 18px; color: var(--accent); }
    .metric-value {
      font-size: 28px;
      font-weight: 700;
      letter-spacing: -0.03em;
      color: #fff;
    }
    .metric-sub {
      font-size: 12px;
      color: var(--text-secondary);
      margin-top: 4px;
    }

    /* TELEMETRY VIEW & PIE CHART */
    .telemetry-layout {
      display: grid;
      grid-template-columns: 340px 1fr;
      gap: 24px;
    }
    .chart-container-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 24px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .chart-box {
      width: 220px;
      height: 220px;
      position: relative;
      margin: 16px 0;
    }
    .chart-center-metric {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      text-align: center;
      pointer-events: none;
    }
    .chart-center-percent {
      font-size: 32px;
      font-weight: 800;
      color: #fff;
      letter-spacing: -0.04em;
    }
    .chart-center-label {
      font-size: 10px;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }

    /* PHASES PROGRESS LIST */
    .phases-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
      width: 100%;
      margin-top: 12px;
    }
    .phase-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 12px;
    }
    .phase-badge-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      display: inline-block;
      margin-right: 6px;
    }

    /* TERMINAL LOG CONSOLE */
    .terminal-card {
      background: #09090b;
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      overflow: hidden;
      display: flex;
      flex-direction: column;
      height: 480px;
    }
    .terminal-header {
      background: rgba(255, 255, 255, 0.04);
      padding: 12px 18px;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .terminal-controls {
      display: flex;
      gap: 6px;
    }
    .term-btn { width: 10px; height: 10px; border-radius: 50%; }
    .term-red { background: #ff5f56; }
    .term-yellow { background: #ffbd2e; }
    .term-green { background: #27c93f; }

    .terminal-body {
      padding: 16px;
      overflow-y: auto;
      font-family: var(--font-mono);
      font-size: 12px;
      line-height: 1.6;
      flex: 1;
      color: #a1a1aa;
    }
    .log-line { display: flex; gap: 10px; margin-bottom: 4px; }
    .log-ts { color: var(--text-tertiary); }
    .log-lvl-INFO { color: var(--accent); }
    .log-lvl-PASS { color: var(--success); font-weight: 600; }
    .log-lvl-GATE { color: var(--warning); font-weight: 600; }

    /* EMAIL GATEWAY CARDS */
    .email-flow-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      margin-bottom: 28px;
    }
    .email-flow-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 24px;
    }
    .email-flow-card h3 {
      font-size: 16px;
      font-weight: 600;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 12px;
    }
    .email-flow-card p {
      font-size: 13px;
      color: var(--text-secondary);
      line-height: 1.5;
      margin-bottom: 16px;
    }
    .email-pill-addr {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid var(--border);
      padding: 4px 10px;
      border-radius: 6px;
      font-family: var(--font-mono);
      font-size: 12px;
      color: var(--accent);
    }

    /* BUTTONS */
    .btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 9px 18px;
      border-radius: var(--radius-sm);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      border: none;
      transition: var(--transition);
      text-decoration: none;
    }
    .btn-primary {
      background: var(--accent);
      color: #fff;
    }
    .btn-primary:hover {
      background: #0077ed;
      box-shadow: 0 4px 14px var(--accent-glow);
    }
    .btn-success {
      background: var(--success);
      color: #000;
    }
    .btn-success:hover {
      background: #25b348;
      box-shadow: 0 4px 14px var(--success-glow);
    }
    .btn-secondary {
      background: rgba(255, 255, 255, 0.08);
      color: var(--text);
      border: 1px solid var(--border);
    }
    .btn-secondary:hover {
      background: rgba(255, 255, 255, 0.14);
      border-color: var(--border-focus);
    }

    /* SLIDE-OVER DRAWER */
    .drawer-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.65);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      z-index: 1000;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.3s ease;
    }
    .drawer-overlay.open { opacity: 1; pointer-events: auto; }
    .drawer {
      position: fixed;
      top: 0;
      right: -600px;
      width: 580px;
      height: 100vh;
      background: var(--drawer-bg);
      backdrop-filter: blur(36px);
      -webkit-backdrop-filter: blur(36px);
      border-left: 1px solid var(--border-focus);
      z-index: 1001;
      display: flex;
      flex-direction: column;
      transition: right 0.35s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: -20px 0 60px rgba(0, 0, 0, 0.85);
    }
    .drawer.open { right: 0; }
    .drawer-header {
      padding: 24px;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .drawer-body {
      flex: 1;
      padding: 24px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    /* MODAL */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      z-index: 1100;
      display: none;
      align-items: center;
      justify-content: center;
    }
    .modal-overlay.open { display: flex; animation: viewFade 0.2s ease; }
    .modal-card {
      background: var(--card-elevated);
      border: 1px solid var(--border-focus);
      border-radius: var(--radius-lg);
      width: 500px;
      max-width: 90vw;
      padding: 28px;
      box-shadow: 0 24px 60px rgba(0,0,0,0.85);
    }
    .modal-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;
    }
    .modal-header h3 { font-size: 18px; font-weight: 600; color: #fff; }

    /* INPUTS */
    .form-group { margin-bottom: 16px; }
    .form-group label {
      display: block;
      font-size: 12px;
      font-weight: 600;
      color: var(--text-secondary);
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .form-control {
      width: 100%;
      background: rgba(0, 0, 0, 0.4);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      padding: 10px 14px;
      color: var(--text);
      font-family: var(--font);
      font-size: 13px;
      outline: none;
      transition: var(--transition);
    }
    .form-control:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px var(--accent-glow);
    }

    /* TABLES */
    .mac-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }
    .mac-table th {
      text-align: left;
      padding: 12px 16px;
      background: rgba(255, 255, 255, 0.03);
      color: var(--text-secondary);
      font-weight: 600;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      border-bottom: 1px solid var(--border);
    }
    .mac-table td {
      padding: 14px 16px;
      border-bottom: 1px solid var(--border);
      color: var(--text);
    }
    .mac-table tr:hover td {
      background: rgba(255, 255, 255, 0.02);
    }
  </style>
</head>
<body>

  <!-- TOP HEADER -->
  <header class="mac-header">
    <div class="header-left">
      <div class="brand-mark">
        <div class="brand-logo-badge">
          <i data-lucide="shield-check"></i>
        </div>
        <div>
          <div class="brand-title">SolidBit SACL</div>
          <div class="brand-subtitle">Decision Shell Pro</div>
        </div>
      </div>

      <!-- WORKSPACE / PROJECT SWITCHER -->
      <div class="header-pill-dropdown">
        <button class="header-pill-btn" onclick="toggleDropdown('project-dropdown')">
          <i data-lucide="folder-git-2"></i>
          <span id="header-active-project">Stable-Ecommerce</span>
          <i data-lucide="chevron-down" class="chevron"></i>
        </button>
        <div id="project-dropdown" class="dropdown-menu">
          <div class="dropdown-item active" onclick="switchActiveProject('stable-ecommerce')">
            <i data-lucide="shopping-bag"></i>
            <div>
              <strong>Stable-Ecommerce</strong>
              <div style="font-size:11px;color:#86868b">Production-grade multi-vendor</div>
            </div>
          </div>
          <div class="dropdown-item" onclick="switchActiveProject('sacl-control-loop')">
            <i data-lucide="cpu"></i>
            <div>
              <strong>SolidBit SACL Control Loop</strong>
              <div style="font-size:11px;color:#86868b">Autonomous agent supervisor</div>
            </div>
          </div>
          <div class="dropdown-item" onclick="switchActiveProject('solidbit-blueprints')">
            <i data-lucide="file-text"></i>
            <div>
              <strong>Architectural Blueprints</strong>
              <div style="font-size:11px;color:#86868b">Frozen contracts & invariants</div>
            </div>
          </div>
        </div>
      </div>

      <!-- AI MODEL SELECTOR -->
      <div class="header-pill-dropdown">
        <button class="header-pill-btn" onclick="toggleDropdown('model-dropdown')">
          <i data-lucide="sparkles"></i>
          <span id="header-active-model">Claude 3.7 Sonnet (Hybrid)</span>
          <i data-lucide="chevron-down" class="chevron"></i>
        </button>
        <div id="model-dropdown" class="dropdown-menu">
          <div class="dropdown-item active" onclick="selectModel('claude-3-7-sonnet')">
            <i data-lucide="cpu"></i>
            <div>
              <strong>Claude 3.7 Sonnet</strong>
              <div style="font-size:11px;color:#30d158">Recomendado · Hybrid Thinking</div>
            </div>
          </div>
          <div class="dropdown-item" onclick="selectModel('claude-3-5-sonnet')">
            <i data-lucide="code-2"></i>
            <div>
              <strong>Claude 3.5 Sonnet</strong>
              <div style="font-size:11px;color:#86868b">Especialista en Código Rápido</div>
            </div>
          </div>
          <div class="dropdown-item" onclick="selectModel('gemini-2-flash')">
            <i data-lucide="zap"></i>
            <div>
              <strong>Gemini 2.0 Flash</strong>
              <div style="font-size:11px;color:#2997ff">Ultra-Baja Latencia (Sub-segundo)</div>
            </div>
          </div>
          <div class="dropdown-item" onclick="selectModel('gemini-1-5-pro')">
            <i data-lucide="database"></i>
            <div>
              <strong>Gemini 1.5 Pro</strong>
              <div style="font-size:11px;color:#bf5af2">Contexto Masivo de 2M Tokens</div>
            </div>
          </div>
          <div class="dropdown-item" onclick="selectModel('gpt-4o')">
            <i data-lucide="bot"></i>
            <div>
              <strong>OpenAI GPT-4o</strong>
              <div style="font-size:11px;color:#86868b">Omni Multimodal & Esquemas</div>
            </div>
          </div>
          <div class="dropdown-item" onclick="selectModel('deepseek-r1')">
            <i data-lucide="lock"></i>
            <div>
              <strong>DeepSeek R1 (Ollama)</strong>
              <div style="font-size:11px;color:#ffd60a">Local On-Premise Air-gapped</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="header-right">
      <div class="sse-indicator">
        <div class="pulse-dot"></div>
        <span>SSE LIVE PUSH</span>
      </div>
      <button class="btn btn-secondary" onclick="openModelSettingsModal()">
        <i data-lucide="sliders"></i>
        <span>Ajustes IA</span>
      </button>
    </div>
  </header>

  <!-- APP BODY -->
  <div class="app-body">
    <!-- LEFT SIDEBAR -->
    <aside class="mac-sidebar">
      <div class="sidebar-section-title">SDLC Operacional</div>
      <div class="nav-item active" onclick="switchTab('overview')">
        <i data-lucide="layout-dashboard"></i>
        <span>Visión General</span>
      </div>
      <div class="nav-item" onclick="switchTab('telemetry')">
        <i data-lucide="activity"></i>
        <span>Ejecución & Fases %</span>
        <span class="badge" id="badge-telemetry">75%</span>
      </div>
      <div class="nav-item" onclick="switchTab('gates')">
        <i data-lucide="git-pull-request"></i>
        <span>Compuertas Humanas</span>
        <span class="badge" id="badge-gates">1</span>
      </div>

      <div class="sidebar-section-title">Diseño & Gobernanza</div>
      <div class="nav-item" onclick="switchTab('roadmap')">
        <i data-lucide="calendar"></i>
        <span>Roadmap del SDLC</span>
      </div>
      <div class="nav-item" onclick="switchTab('designer')">
        <i data-lucide="workflow"></i>
        <span>Diseñador de DAG</span>
      </div>
      <div class="nav-item" onclick="switchTab('email')">
        <i data-lucide="mail"></i>
        <span>Email Gateway</span>
        <span class="badge" style="background:#30d158;color:#000">E2E</span>
      </div>

      <div class="sidebar-section-title">Infraestructura & Datos</div>
      <div class="nav-item" onclick="switchTab('connections')">
        <i data-lucide="plug"></i>
        <span>Conexiones & Auth</span>
        <span class="badge" id="badge-conns">6/9</span>
      </div>
      <div class="nav-item" onclick="switchTab('contracts')">
        <i data-lucide="shield"></i>
        <span>Contratos Inmutables</span>
      </div>
    </aside>

    <!-- CONTENT AREA -->
    <main class="mac-content">

      <!-- TAB 1: VISIÓN GENERAL -->
      <section id="tab-overview" class="tab-content active">
        <div class="view-header">
          <div class="view-title-wrap">
            <h1><i data-lucide="gauge"></i> Tablero Soberano de Control SDLC</h1>
            <p>Supervisión en tiempo real de compuertas, integridad de contratos y agentes autónomos.</p>
          </div>
          <div style="display:flex;gap:12px;">
            <button class="btn btn-secondary" onclick="loadDashboardSnapshot()">
              <i data-lucide="refresh-cw"></i> Sincronizar
            </button>
            <button class="btn btn-primary" onclick="launchActiveCampaign()">
              <i data-lucide="play"></i> Iniciar Sprint Autónomo
            </button>
          </div>
        </div>

        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-header">
              <span>Readiness Score</span>
              <i data-lucide="check-circle-2"></i>
            </div>
            <div class="metric-value" id="val-readiness">94%</div>
            <div class="metric-sub">683 pruebas unitarias en verde</div>
          </div>
          <div class="metric-card">
            <div class="metric-header">
              <span>Compuertas Pendientes</span>
              <i data-lucide="alert-circle" style="color:var(--warning)"></i>
            </div>
            <div class="metric-value" id="val-pending-gates" style="color:var(--warning)">1</div>
            <div class="metric-sub">Requiere micro-decisión del operador</div>
          </div>
          <div class="metric-card">
            <div class="metric-header">
              <span>Contratos Inmutables</span>
              <i data-lucide="shield-alert" style="color:var(--success)"></i>
            </div>
            <div class="metric-value" style="color:var(--success)">LOCKED</div>
            <div class="metric-sub">DR-INV-001 & DR-PAY-001 Intactos</div>
          </div>
          <div class="metric-card">
            <div class="metric-header">
              <span>Hard Denies Activos</span>
              <i data-lucide="lock" style="color:var(--purple)"></i>
            </div>
            <div class="metric-value" style="color:var(--purple)">4/4</div>
            <div class="metric-sub">Cero producción no autorizada</div>
          </div>
        </div>

        <!-- RECENT ACTIVITY CARD -->
        <div style="background:var(--card-bg);border:1px solid var(--border);border-radius:var(--radius-lg);padding:24px;">
          <h3 style="font-size:16px;font-weight:600;margin-bottom:16px;display:flex;align-items:center;gap:10px;">
            <i data-lucide="zap"></i> Micro-Decisiones Requeridas (Compuertas Humanas)
          </h3>
          <div id="overview-gates-container">
            <!-- Rendered dynamically -->
          </div>
        </div>
      </section>

      <!-- TAB 2: TELEMETRÍA EN VIVO & FASES % -->
      <section id="tab-telemetry" class="tab-content">
        <div class="view-header">
          <div class="view-title-wrap">
            <h1><i data-lucide="pie-chart"></i> Ejecución de Tareas en Tiempo Real</h1>
            <p>Monitoreo determinista por fases porcentuales y gráfica pastel en tiempo real.</p>
          </div>
          <button class="btn btn-primary" onclick="simulateTaskProgress()">
            <i data-lucide="fast-forward"></i> Avanzar Paso (+15%)
          </button>
        </div>

        <div class="telemetry-layout">
          <!-- PIE / DOUGHNUT CHART CARD -->
          <div class="chart-container-card">
            <div style="font-size:14px;font-weight:600;color:#fff;margin-bottom:4px;">Distribución por Fases</div>
            <div style="font-size:12px;color:var(--text-secondary);">Avance ponderado del sprint</div>

            <div class="chart-box">
              <canvas id="telemetryDoughnutChart"></canvas>
              <div class="chart-center-metric">
                <div class="chart-center-percent" id="chart-percent-display">75%</div>
                <div class="chart-center-label">Global</div>
              </div>
            </div>

            <div class="phases-list" id="telemetry-phases-container">
              <!-- Rendered dynamically -->
            </div>
          </div>

          <!-- TERMINAL CONSOLE -->
          <div class="terminal-card">
            <div class="terminal-header">
              <div class="terminal-controls">
                <div class="term-btn term-red"></div>
                <div class="term-btn term-yellow"></div>
                <div class="term-btn term-green"></div>
              </div>
              <div style="font-size:12px;font-family:var(--font-mono);color:var(--text-secondary);">
                sacl-agent-worker-01 · PID 19842 · tempfs/worktree
              </div>
              <button class="btn btn-secondary" style="padding:4px 8px;font-size:11px;" onclick="clearLogs()">
                Limpiar
              </button>
            </div>
            <div class="terminal-body" id="telemetry-terminal-body">
              <!-- Log lines -->
            </div>
          </div>
        </div>
      </section>

      <!-- TAB 3: COMPUERTAS HUMANAS -->
      <section id="tab-gates" class="tab-content">
        <div class="view-header">
          <div class="view-title-wrap">
            <h1><i data-lucide="git-pull-request"></i> Compuertas de Decisión Soberana</h1>
            <p>El arquitecto solo toma micro-decisiones binarias. El sistema genera el diff y valida invariantes.</p>
          </div>
        </div>
        <div id="full-gates-container" style="display:flex;flex-direction:column;gap:18px;">
          <!-- Gate cards -->
        </div>
      </section>

      <!-- TAB 4: ROADMAP DEL SDLC -->
      <section id="tab-roadmap" class="tab-content">
        <div class="view-header">
          <div class="view-title-wrap">
            <h1><i data-lucide="calendar"></i> Roadmap Integral del SDLC</h1>
            <p>Hitos de arquitectura, contratos inmutables, bucle de control e integración con Jira.</p>
          </div>
        </div>
        <div id="roadmap-container" style="display:flex;flex-direction:column;gap:18px;">
          <!-- Roadmap phases -->
        </div>
      </section>

      <!-- TAB 5: DISEÑADOR VISUAL DE DAG -->
      <section id="tab-designer" class="tab-content">
        <div class="view-header">
          <div class="view-title-wrap">
            <h1><i data-lucide="workflow"></i> Diseñador de Campañas & Grafos DAG</h1>
            <p>Configura visualmente los nodos del sprint sin manipular archivos JSON manualmente.</p>
          </div>
          <div style="display:flex;gap:12px;">
            <button class="btn btn-secondary" onclick="openAddNodeModal()">
              <i data-lucide="plus"></i> Agregar Nodo
            </button>
            <button class="btn btn-primary" onclick="saveCampaignDAG()">
              <i data-lucide="save"></i> Guardar Manifiesto
            </button>
          </div>
        </div>
        <div id="designer-nodes-container" style="display:grid;grid-template-columns:repeat(auto-fill, minmax(280px, 1fr));gap:18px;">
          <!-- Visual DAG node cards -->
        </div>
      </section>

      <!-- TAB 6: EMAIL GATEWAY (NOTIFICACIONES & CONTROL POR CORREO) -->
      <section id="tab-email" class="tab-content">
        <div class="view-header">
          <div class="view-title-wrap">
            <h1><i data-lucide="mail"></i> Email Gateway & Automatización Bidireccional</h1>
            <p>Recibe reportes y autorizaciones en tu correo, o envía un email para poner a trabajar a los agentes.</p>
          </div>
          <div style="display:flex;gap:12px;">
            <button class="btn btn-secondary" onclick="testSendEmail()">
              <i data-lucide="send"></i> Enviar Correo de Prueba
            </button>
            <button class="btn btn-primary" onclick="simulateInboundEmail()">
              <i data-lucide="inbox"></i> Simular Correo Entrante
            </button>
          </div>
        </div>

        <div class="email-flow-grid">
          <!-- SALIENTE -->
          <div class="email-flow-card">
            <h3><i data-lucide="arrow-up-right" style="color:var(--accent)"></i> Canal Saliente: Sistema &rarr; Operador</h3>
            <p>Cuando los agentes terminan un sprint o encuentran una compuerta, se despacha un reporte con resultados y enlace de autorización de 1-tap para el móvil.</p>
            <div style="margin-bottom:12px;">
              <span style="font-size:12px;color:var(--text-secondary);">De:</span>
              <span class="email-pill-addr">lucilfer@selfcaresinners.com</span>
            </div>
            <div>
              <span style="font-size:12px;color:var(--text-secondary);">Para:</span>
              <span class="email-pill-addr">lawlieeet@outlook.es</span>
            </div>
          </div>

          <!-- ENTRANTE -->
          <div class="email-flow-card">
            <h3><i data-lucide="arrow-down-left" style="color:var(--success)"></i> Canal Entrante: Operador &rarr; Agentes</h3>
            <p>Envía un correo desde tu cuenta autorizada. El webhook verifica tu firma SPF/DKIM y despierta inmediatamente a los agentes para ejecutar el DAG sin tocar la terminal.</p>
            <div style="margin-bottom:12px;">
              <span style="font-size:12px;color:var(--text-secondary);">De:</span>
              <span class="email-pill-addr">lawlieeet@outlook.es</span>
            </div>
            <div>
              <span style="font-size:12px;color:var(--text-secondary);">Para:</span>
              <span class="email-pill-addr">lucilfer@selfcaresinners.com</span>
            </div>
          </div>
        </div>

        <!-- EMAIL LOG TABLE -->
        <div style="background:var(--card-bg);border:1px solid var(--border);border-radius:var(--radius-lg);overflow:hidden;">
          <div style="padding:18px 24px;border-bottom:1px solid var(--border);font-size:14px;font-weight:600;">
            Historial de Notificaciones y Comandos por Correo
          </div>
          <table class="mac-table">
            <thead>
              <tr>
                <th>Dirección</th>
                <th>Remitente / Destino</th>
                <th>Asunto</th>
                <th>Estado</th>
                <th>Hora</th>
              </tr>
            </thead>
            <tbody id="email-logs-tbody">
              <!-- Rendered dynamically -->
            </tbody>
          </table>
        </div>
      </section>

      <!-- TAB 7: CONEXIONES & AUTH -->
      <section id="tab-connections" class="tab-content">
        <div class="view-header">
          <div class="view-title-wrap">
            <h1><i data-lucide="plug"></i> Conexiones & Autenticación Asistida por Navegador</h1>
            <p>Inicia sesión en GitHub, Railway, Supabase, Jira, Resend y Google Cloud directamente abriendo el navegador.</p>
          </div>
        </div>
        <div id="connections-grid" style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:18px;">
          <!-- Connection cards -->
        </div>
      </section>

      <!-- TAB 8: CONTRATOS INMUTABLES -->
      <section id="tab-contracts" class="tab-content">
        <div class="view-header">
          <div class="view-title-wrap">
            <h1><i data-lucide="shield-check"></i> Catálogo de Contratos Inmutables & Hard Denies</h1>
            <p>Garantías matemáticas que impiden pérdidas financieras, sobre-cargos y mutaciones destructivas.</p>
          </div>
        </div>
        <div id="contracts-grid" style="display:grid;grid-template-columns:repeat(auto-fit, minmax(320px, 1fr));gap:20px;">
          <!-- Contract cards -->
        </div>
      </section>

    </main>
  </div>

  <!-- SLIDE-OVER VISUAL IMPACT DRAWER -->
  <div id="drawer-overlay" class="drawer-overlay" onclick="closeImpactDrawer()"></div>
  <aside id="impact-drawer" class="drawer">
    <div class="drawer-header">
      <div>
        <h2 style="font-size:18px;font-weight:700;color:#fff;display:flex;align-items:center;gap:8px;">
          <i data-lucide="file-diff"></i> Impacto Visual & Diff de Arquitectura
        </h2>
        <div id="drawer-subtitle" style="font-size:12px;color:var(--text-secondary);margin-top:2px;">
          Compuerta: REQ-20261023
        </div>
      </div>
      <button class="btn btn-secondary" style="padding:6px 10px;" onclick="closeImpactDrawer()">
        <i data-lucide="x"></i>
      </button>
    </div>
    <div class="drawer-body">
      <!-- Human Business Summary -->
      <div style="background:rgba(41, 151, 255, 0.08);border:1px solid rgba(41, 151, 255, 0.25);border-radius:var(--radius-md);padding:16px;">
        <div style="font-size:11px;font-weight:600;color:var(--accent);text-transform:uppercase;margin-bottom:4px;">
          Resumen Ejecutivo
        </div>
        <p id="drawer-human-summary" style="font-size:13px;line-height:1.5;color:#fff;">
          Cargando análisis de impacto...
        </p>
      </div>

      <!-- Contracts Semaphore -->
      <div>
        <div style="font-size:12px;font-weight:600;color:var(--text-secondary);text-transform:uppercase;margin-bottom:8px;">
          Semáforo de Contratos Congelados
        </div>
        <div id="drawer-contracts-semaphore" style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
          <!-- Injected status -->
        </div>
      </div>

      <!-- File Tree -->
      <div>
        <div style="font-size:12px;font-weight:600;color:var(--text-secondary);text-transform:uppercase;margin-bottom:8px;">
          Archivos Afectados
        </div>
        <div id="drawer-file-tree" style="background:#09090b;border:1px solid var(--border);border-radius:var(--radius-md);padding:12px;font-family:var(--font-mono);font-size:12px;">
          <!-- Files list -->
        </div>
      </div>

      <!-- Diff Snippet -->
      <div>
        <div style="font-size:12px;font-weight:600;color:var(--text-secondary);text-transform:uppercase;margin-bottom:8px;">
          Vista Previa Sintáctica del Diff
        </div>
        <pre id="drawer-diff-preview" style="background:#09090b;border:1px solid var(--border);border-radius:var(--radius-md);padding:16px;font-family:var(--font-mono);font-size:11px;line-height:1.5;color:#a1a1aa;overflow-x:auto;">
--- a/services/web-storefront/cart.ts
+++ b/services/web-storefront/cart.ts
        </pre>
      </div>

      <!-- Action Buttons -->
      <div style="display:flex;gap:12px;margin-top:auto;padding-top:16px;border-top:1px solid var(--border);">
        <button class="btn btn-secondary" style="flex:1" onclick="submitDrawerDecision('REJECTED')">
          <i data-lucide="x-circle"></i> Rechazar
        </button>
        <button class="btn btn-success" style="flex:1" onclick="submitDrawerDecision('APPROVED')">
          <i data-lucide="check-circle"></i> Autorizar Acción
        </button>
      </div>
    </div>
  </aside>

  <!-- AUTH / BROWSER LOGIN MODAL -->
  <div id="auth-modal" class="modal-overlay">
    <div class="modal-card">
      <div class="modal-header">
        <h3 id="modal-auth-title"><i data-lucide="key"></i> Autenticación E2E</h3>
        <button class="btn btn-secondary" style="padding:4px 8px;" onclick="closeAuthModal()">
          <i data-lucide="x"></i>
        </button>
      </div>
      <p id="modal-auth-desc" style="font-size:13px;color:var(--text-secondary);margin-bottom:18px;">
        Inicia sesión automáticamente abriendo el portal en tu navegador.
      </p>

      <div style="background:rgba(255,255,255,0.04);border:1px solid var(--border);border-radius:var(--radius-md);padding:16px;margin-bottom:18px;text-align:center;">
        <button class="btn btn-primary" id="btn-browser-auth" onclick="launchBrowserAuthAction()" style="width:100%;justify-content:center;">
          <i data-lucide="external-link"></i> Abrir Navegador para Autenticar
        </button>
        <div style="font-size:11px;color:var(--text-secondary);margin-top:8px;">
          Se abrirá tu navegador predeterminado para iniciar sesión y generar tu token.
        </div>
      </div>

      <div class="form-group">
        <label>Token / API Key (Opcional si usaste el CLI)</label>
        <input type="password" id="auth-token-input" class="form-control" placeholder="Pegar token aquí...">
      </div>

      <div style="display:flex;gap:12px;margin-top:20px;">
        <button class="btn btn-secondary" style="flex:1" onclick="closeAuthModal()">Cancelar</button>
        <button class="btn btn-success" style="flex:1" onclick="submitTokenAuth()">Guardar y Conectar</button>
      </div>
    </div>
  </div>

  <!-- MODEL SETTINGS MODAL -->
  <div id="model-modal" class="modal-overlay">
    <div class="modal-card">
      <div class="modal-header">
        <h3><i data-lucide="sliders"></i> Configuración del Motor de IA</h3>
        <button class="btn btn-secondary" style="padding:4px 8px;" onclick="closeModelModal()">
          <i data-lucide="x"></i>
        </button>
      </div>

      <div class="form-group">
        <label>Temperatura de Razonamiento (0.0 estricto &rarr; 1.0 creativo)</label>
        <input type="range" id="model-temp-slider" min="0" max="1" step="0.05" value="0.2" class="form-control" oninput="document.getElementById('temp-val').innerText = this.value">
        <div style="font-size:12px;color:var(--accent);margin-top:4px;">Valor actual: <strong id="temp-val">0.2</strong> (Recomendado para generación determinista)</div>
      </div>

      <div class="form-group">
        <label>Límite de Tokens por Paso</label>
        <input type="number" id="model-tokens-input" class="form-control" value="8192">
      </div>

      <div style="margin:16px 0;display:flex;align-items:center;gap:10px;">
        <input type="checkbox" id="model-guardrails-check" checked style="width:18px;height:18px;">
        <label for="model-guardrails-check" style="font-size:13px;color:#fff;margin:0;cursor:pointer;">
          Blindaje de Hard Deny Constitucional (Inviolable)
        </label>
      </div>

      <div style="display:flex;gap:12px;margin-top:20px;">
        <button class="btn btn-secondary" style="flex:1" onclick="closeModelModal()">Cerrar</button>
        <button class="btn btn-primary" style="flex:1" onclick="saveModelParameters()">Aplicar Ajustes</button>
      </div>
    </div>
  </div>

  <!-- JAVASCRIPT APPLICATION CORE -->
  <script>
    let activeDrawerGateId = null;
    let activeAuthToolId = null;
    let telemetryChartInstance = null;

    // 1. INITIALIZATION & LUCIDE ICONS
    window.addEventListener('DOMContentLoaded', () => {
      lucide.createIcons();
      initSSE();
      initTelemetryChart();
      loadDashboardSnapshot();
      loadRoadmapData();
      loadDesignerData();
      loadEmailData();
    });

    function refreshIcons() {
      setTimeout(() => { lucide.createIcons(); }, 30);
    }

    // 2. TABS NAVIGATION
    function switchTab(tabId) {
      document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

      const target = document.getElementById(`tab-${tabId}`);
      if (target) target.classList.add('active');

      const navs = document.querySelectorAll('.nav-item');
      navs.forEach(n => {
        if (n.getAttribute('onclick') && n.getAttribute('onclick').includes(tabId)) {
          n.classList.add('active');
        }
      });
      refreshIcons();
    }

    // 3. DROPDOWNS
    function toggleDropdown(id) {
      const el = document.getElementById(id);
      document.querySelectorAll('.dropdown-menu').forEach(d => {
        if (d.id !== id) d.classList.remove('show');
      });
      el.classList.toggle('show');
    }

    window.addEventListener('click', (e) => {
      if (!e.target.closest('.header-pill-dropdown')) {
        document.querySelectorAll('.dropdown-menu').forEach(d => d.classList.remove('show'));
      }
    });

    // 4. PROJECT SWITCHING
    async function switchActiveProject(projectId) {
      try {
        const res = await fetch('/api/projects/switch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: projectId })
        });
        const data = await res.json();
        if (data.success) {
          document.getElementById('header-active-project').innerText = data.active_project.name;
          toggleDropdown('project-dropdown');
          loadDashboardSnapshot();
        }
      } catch (err) {
        console.error(err);
      }
    }

    // 5. AI MODEL SELECTION
    async function selectModel(modelId) {
      try {
        const res = await fetch('/api/model/select', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ model_id: modelId })
        });
        const data = await res.json();
        if (data.success) {
          document.getElementById('header-active-model').innerText = data.config.active_model.name;
          toggleDropdown('model-dropdown');
        }
      } catch (err) {
        console.error(err);
      }
    }

    // 6. REAL-TIME SERVER-SENT EVENTS (SSE)
    function initSSE() {
      const source = new EventSource('/api/events/stream');
      source.addEventListener('snapshot', (e) => {
        const snap = JSON.parse(e.data);
        renderSnapshot(snap);
      });
      source.addEventListener('gate_decided', () => {
        loadDashboardSnapshot();
        closeImpactDrawer();
      });
      source.addEventListener('campaign_launched', () => {
        loadDashboardSnapshot();
        loadTelemetryData();
      });
      source.addEventListener('telemetry_updated', (e) => {
        const data = JSON.parse(e.data);
        renderTelemetry(data);
      });
      source.addEventListener('email_sent', () => {
        loadEmailData();
      });
      source.addEventListener('inbound_email_triggered', () => {
        loadEmailData();
        loadDashboardSnapshot();
      });
    }

    // 7. DASHBOARD DATA
    async function loadDashboardSnapshot() {
      try {
        const res = await fetch('/api/snapshot');
        const snap = await res.json();
        renderSnapshot(snap);
      } catch (err) {
        console.error(err);
      }
    }

    function renderSnapshot(snap) {
      if (!snap) return;
      document.getElementById('val-readiness').innerText = `${snap.readiness_score || 94}%`;
      const pendingCount = (snap.pending_gates || []).length;
      document.getElementById('val-pending-gates').innerText = pendingCount;
      document.getElementById('badge-gates').innerText = pendingCount;

      renderGates(snap.pending_gates || []);
      renderConnections(snap.connections || []);
      refreshIcons();
    }

    function renderGates(gates) {
      const c1 = document.getElementById('overview-gates-container');
      const c2 = document.getElementById('full-gates-container');
      if (!c1 || !c2) return;

      if (gates.length === 0) {
        const emptyHtml = `<div style="padding:24px;text-align:center;color:#86868b;font-size:13px;">
          <i data-lucide="check-circle" style="width:24px;height:24px;color:#30d158;margin-bottom:8px;"></i>
          <div>Cero compuertas pendientes. El flujo autónomo continúa ejecutándose de forma limpia.</div>
        </div>`;
        c1.innerHTML = emptyHtml;
        c2.innerHTML = emptyHtml;
        return;
      }

      let html = '';
      gates.forEach(g => {
        html += `
        <div style="background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:var(--radius-md);padding:18px;display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
          <div>
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
              <span style="background:rgba(255,214,10,0.15);color:var(--warning);font-size:11px;font-weight:700;padding:3px 8px;border-radius:6px;">
                ${g.action}
              </span>
              <span style="font-family:var(--font-mono);font-size:12px;color:var(--text-secondary);">${g.approval_id}</span>
            </div>
            <div style="font-size:14px;font-weight:600;color:#fff;">${g.reason}</div>
            <div style="font-size:12px;color:var(--text-secondary);margin-top:4px;">Alcance: ${g.scope}</div>
          </div>
          <div style="display:flex;gap:10px;">
            <button class="btn btn-secondary" onclick="openImpactDrawer('${g.approval_id}')">
              <i data-lucide="file-diff"></i> Ver Diff & Impacto
            </button>
            <button class="btn btn-success" onclick="quickApproveGate('${g.approval_id}')">
              <i data-lucide="check"></i> Autorizar
            </button>
          </div>
        </div>`;
      });
      c1.innerHTML = html;
      c2.innerHTML = html;
    }

    function renderConnections(conns) {
      const grid = document.getElementById('connections-grid');
      if (!grid) return;
      let connectedCount = 0;
      let html = '';
      conns.forEach(c => {
        const isConn = (c.status === 'connected');
        if (isConn) connectedCount++;
        const statusColor = isConn ? 'var(--success)' : 'var(--danger)';
        const statusText = isConn ? 'Conectado' : 'Desconectado';

        html += `
        <div style="background:var(--card-bg);border:1px solid var(--border);border-radius:var(--radius-md);padding:20px;display:flex;flex-direction:column;justify-content:space-between;">
          <div>
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
              <strong style="font-size:15px;color:#fff;">${c.name}</strong>
              <span style="display:flex;align-items:center;gap:6px;font-size:12px;color:${statusColor};font-weight:600;">
                <span style="width:6px;height:6px;border-radius:50%;background:${statusColor};display:inline-block;"></span>
                ${statusText}
              </span>
            </div>
            <div style="font-size:12px;color:var(--text-secondary);margin-bottom:6px;">
              Versión: ${c.version || 'No instalada'}
            </div>
            <div style="font-size:12px;color:var(--text-tertiary);">
              Cuenta: ${c.account_info || 'N/A'}
            </div>
          </div>

          <div style="margin-top:20px;display:flex;gap:8px;">
            <button class="btn btn-secondary" style="flex:1;padding:6px 10px;font-size:12px;" onclick="openAuthModal('${c.id}', '${c.name}')">
              <i data-lucide="external-link"></i> Abrir en Navegador
            </button>
            <button class="btn btn-secondary" style="padding:6px 10px;" onclick="testSingleConnection('${c.id}')">
              <i data-lucide="refresh-cw"></i>
            </button>
          </div>
        </div>`;
      });
      grid.innerHTML = html;
      document.getElementById('badge-conns').innerText = `${connectedCount}/${conns.length}`;
    }

    // 8. VISUAL IMPACT DRAWER
    async function openImpactDrawer(gateId) {
      activeDrawerGateId = gateId;
      document.getElementById('drawer-subtitle').innerText = `Compuerta: ${gateId}`;
      document.getElementById('drawer-overlay').classList.add('open');
      document.getElementById('impact-drawer').classList.add('open');

      try {
        const res = await fetch(`/api/gates/impact?gate_id=${gateId}`);
        const data = await res.json();
        document.getElementById('drawer-human-summary').innerText = data.human_summary;
        document.getElementById('drawer-diff-preview').innerText = data.diff_preview;

        // Render Semaphore
        let semHtml = '';
        for (const [k, v] of Object.entries(data.contracts_status || {})) {
          semHtml += `
          <div style="background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:8px;padding:8px 12px;font-size:12px;display:flex;align-items:center;justify-content:space-between;">
            <span style="font-weight:600;font-family:var(--font-mono);">${k}</span>
            <span style="color:var(--success);font-weight:600;">${v}</span>
          </div>`;
        }
        document.getElementById('drawer-contracts-semaphore').innerHTML = semHtml;

        // Render Files
        let fHtml = '';
        (data.file_tree || []).forEach(f => {
          fHtml += `<div style="margin-bottom:4px;display:flex;justify-content:space-between;">
            <span>${f.path}</span>
            <span style="color:#30d158">+${f.lines_added} / -${f.lines_removed}</span>
          </div>`;
        });
        document.getElementById('drawer-file-tree').innerHTML = fHtml;
        refreshIcons();
      } catch (err) {
        console.error(err);
      }
    }

    function closeImpactDrawer() {
      document.getElementById('drawer-overlay').classList.remove('open');
      document.getElementById('impact-drawer').classList.remove('open');
      activeDrawerGateId = null;
    }

    async function submitDrawerDecision(decision) {
      if (!activeDrawerGateId) return;
      try {
        await fetch('/api/gates/decide', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            request_id: activeDrawerGateId,
            decision: decision,
            justification: 'Decidido desde el Cajón de Impacto Visual'
          })
        });
        closeImpactDrawer();
        loadDashboardSnapshot();
      } catch (err) {
        console.error(err);
      }
    }

    async function quickApproveGate(gateId) {
      activeDrawerGateId = gateId;
      submitDrawerDecision('APPROVED');
    }

    // 9. TELEMETRY & CHART.JS
    function initTelemetryChart() {
      const ctx = document.getElementById('telemetryDoughnutChart');
      if (!ctx) return;
      telemetryChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Preparación', 'Contratos', 'Generación', 'Pruebas', 'Firma'],
          datasets: [{
            data: [15, 25, 30, 20, 10],
            backgroundColor: ['#2997ff', '#30d158', '#bf5af2', '#ffd60a', '#64d2ff'],
            borderWidth: 0,
            hoverOffset: 6
          }]
        },
        options: {
          cutout: '76%',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: { enabled: true }
          }
        }
      });
      loadTelemetryData();
    }

    async function loadTelemetryData() {
      try {
        const res = await fetch('/api/telemetry');
        const data = await res.json();
        renderTelemetry(data);
      } catch (err) {
        console.error(err);
      }
    }

    function renderTelemetry(data) {
      if (!data || !data.task) return;
      const t = data.task;
      document.getElementById('chart-percent-display').innerText = `${t.overall_progress_percent}%`;
      document.getElementById('badge-telemetry').innerText = `${t.overall_progress_percent}%`;

      // Render phases list
      const pContainer = document.getElementById('telemetry-phases-container');
      if (pContainer) {
        let pHtml = '';
        const colors = ['#2997ff', '#30d158', '#bf5af2', '#ffd60a', '#64d2ff'];
        (t.phases || []).forEach((p, idx) => {
          pHtml += `
          <div class="phase-row">
            <div>
              <span class="phase-badge-dot" style="background:${colors[idx % colors.length]}"></span>
              <span>${p.name}</span>
            </div>
            <strong style="color:#fff;">${p.progress}%</strong>
          </div>`;
        });
        pContainer.innerHTML = pHtml;
      }

      // Render Terminal Logs
      const termBody = document.getElementById('telemetry-terminal-body');
      if (termBody) {
        let lHtml = '';
        (t.live_logs || []).forEach(l => {
          lHtml += `
          <div class="log-line">
            <span class="log-ts">[${l.timestamp}]</span>
            <span class="log-lvl-${l.level}">${l.level}</span>
            <span>${l.message}</span>
          </div>`;
        });
        termBody.innerHTML = lHtml;
        termBody.scrollTop = termBody.scrollHeight;
      }
    }

    async function simulateTaskProgress() {
      const current = parseInt(document.getElementById('chart-percent-display').innerText) || 75;
      const nextProg = Math.min(100, current + 15);
      await fetch('/api/telemetry/progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ progress: nextProg, phase: 'Verificación Final Cero-Leakage' })
      });
    }

    function clearLogs() {
      const termBody = document.getElementById('telemetry-terminal-body');
      if (termBody) termBody.innerHTML = '';
    }

    // 10. EMAIL GATEWAY TAB & FUNCTIONS
    async function loadEmailData() {
      try {
        const res = await fetch('/api/email/config');
        const data = await res.json();
        const tbody = document.getElementById('email-logs-tbody');
        if (!tbody) return;

        let html = '';
        (data.recent_logs || []).forEach(l => {
          const isOut = (l.direction === 'OUTBOUND');
          const dirBadge = isOut ?
            '<span style="background:rgba(41,151,255,0.15);color:var(--accent);padding:2px 8px;border-radius:4px;font-size:11px;">SALIENTE</span>' :
            '<span style="background:rgba(48,209,88,0.15);color:var(--success);padding:2px 8px;border-radius:4px;font-size:11px;">ENTRANTE</span>';

          html += `
          <tr>
            <td>${dirBadge}</td>
            <td style="font-family:var(--font-mono);font-size:12px;">${l.from} &rarr; ${l.to}</td>
            <td style="font-weight:600;">${l.subject}</td>
            <td><span style="color:var(--success);font-weight:600;">${l.status}</span></td>
            <td style="color:var(--text-secondary);font-size:11px;">${l.timestamp.split('T')[1].slice(0,8)}</td>
          </tr>`;
        });
        tbody.innerHTML = html;
      } catch (err) {
        console.error(err);
      }
    }

    async function testSendEmail() {
      try {
        const res = await fetch('/api/email/test', { method: 'POST' });
        const data = await res.json();
        alert(data.message || 'Correo de prueba enviado con éxito.');
        loadEmailData();
      } catch (err) {
        console.error(err);
      }
    }

    async function simulateInboundEmail() {
      try {
        const res = await fetch('/api/webhooks/inbound-email', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            from: 'lawlieeet@outlook.es',
            subject: 'EJECUTAR SPRINT-02',
            text: 'Arquitecto autoriza arranque de sprint autónomo en checkout.'
          })
        });
        const data = await res.json();
        alert(data.message || 'Comando por correo recibido y procesado.');
        loadEmailData();
      } catch (err) {
        console.error(err);
      }
    }

    // 11. BROWSER AUTH MODAL & INTEGRATION
    function openAuthModal(toolId, toolName) {
      activeAuthToolId = toolId;
      document.getElementById('modal-auth-title').innerText = `Autenticar ${toolName}`;
      document.getElementById('modal-auth-desc').innerText = `Haz clic para abrir el navegador e iniciar sesión en ${toolName}.`;
      document.getElementById('auth-modal').classList.add('open');
      refreshIcons();
    }

    function closeAuthModal() {
      document.getElementById('auth-modal').classList.remove('open');
      activeAuthToolId = null;
    }

    async function launchBrowserAuthAction() {
      if (!activeAuthToolId) return;
      // Trigger backend browser launch
      try {
        const res = await fetch('/api/connections/browser-auth', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tool_id: activeAuthToolId })
        });
        const data = await res.json();
        if (data.auth_url) {
          window.open(data.auth_url, '_blank');
        }
      } catch (err) {
        console.error(err);
      }
    }

    async function submitTokenAuth() {
      const token = document.getElementById('auth-token-input').value;
      if (!activeAuthToolId) return;
      try {
        const res = await fetch('/api/connections/auth', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            tool_id: activeAuthToolId,
            credentials: { token: token }
          })
        });
        const data = await res.json();
        alert(data.message || 'Credenciales guardadas.');
        closeAuthModal();
        loadDashboardSnapshot();
      } catch (err) {
        console.error(err);
      }
    }

    // 12. ROADMAP & DESIGNER DATA
    async function loadRoadmapData() {
      try {
        const res = await fetch('/api/roadmap');
        const data = await res.json();
        const container = document.getElementById('roadmap-container');
        if (!container) return;

        let html = '';
        (data.phases || []).forEach(p => {
          const isDone = (p.status === 'COMPLETED');
          const badgeColor = isDone ? 'var(--success)' : 'var(--accent)';
          html += `
          <div style="background:var(--card-bg);border:1px solid var(--border);border-radius:var(--radius-md);padding:22px;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
              <div>
                <span style="font-family:var(--font-mono);font-size:11px;color:${badgeColor};font-weight:700;">${p.code}</span>
                <h3 style="font-size:16px;font-weight:600;color:#fff;margin-top:2px;">${p.name}</h3>
              </div>
              <div style="text-align:right;">
                <span style="font-size:18px;font-weight:700;color:#fff;">${p.progress}%</span>
                <div style="font-size:11px;color:var(--text-secondary);">${p.period}</div>
              </div>
            </div>
            <div style="background:rgba(255,255,255,0.06);height:6px;border-radius:3px;margin-bottom:16px;overflow:hidden;">
              <div style="background:${badgeColor};width:${p.progress}%;height:100%;"></div>
            </div>
            <ul style="font-size:13px;color:var(--text-secondary);padding-left:18px;line-height:1.6;">
              ${(p.deliverables || []).map(d => `<li>${d}</li>`).join('')}
            </ul>
          </div>`;
        });
        container.innerHTML = html;
      } catch (err) {
        console.error(err);
      }
    }

    async function loadDesignerData() {
      try {
        const res = await fetch('/api/campaigns/designer');
        const dag = await res.json();
        const container = document.getElementById('designer-nodes-container');
        if (!container) return;

        let html = '';
        (dag.nodes || []).forEach(n => {
          const isGate = n.gate_required;
          html += `
          <div style="background:var(--card-bg);border:1px solid ${isGate ? 'rgba(255,214,10,0.3)' : 'var(--border)'};border-radius:var(--radius-md);padding:18px;">
            <div style="font-family:var(--font-mono);font-size:11px;color:var(--text-secondary);margin-bottom:4px;">${n.id}</div>
            <h4 style="font-size:14px;font-weight:600;color:#fff;margin-bottom:8px;">${n.label}</h4>
            <div style="font-size:12px;color:var(--accent);margin-bottom:12px;">Acción: ${n.action}</div>
            <div style="font-size:11px;color:var(--text-secondary);">
              ${isGate ? '<span style="color:var(--warning);font-weight:600;">Compuerta Humana Requerida</span>' : 'Paso Totalmente Autónomo'}
            </div>
          </div>`;
        });
        container.innerHTML = html;
        refreshIcons();
      } catch (err) {
        console.error(err);
      }
    }

    async function launchActiveCampaign() {
      try {
        const res = await fetch('/api/campaigns/launch', { method: 'POST' });
        const data = await res.json();
        alert(data.message || 'Campaña lanzada con éxito.');
        loadDashboardSnapshot();
      } catch (err) {
        console.error(err);
      }
    }

    function openModelSettingsModal() {
      document.getElementById('model-modal').classList.add('open');
      refreshIcons();
    }
    function closeModelModal() {
      document.getElementById('model-modal').classList.remove('open');
    }

    async function saveModelParameters() {
      const temp = parseFloat(document.getElementById('model-temp-slider').value);
      const tokens = parseInt(document.getElementById('model-tokens-input').value);
      const guard = document.getElementById('model-guardrails-check').checked;

      await fetch('/api/model/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          temperature: temp,
          max_tokens: tokens,
          guardrails_enforced: guard
        })
      });
      closeModelModal();
    }
  </script>
</body>
</html>
"""
