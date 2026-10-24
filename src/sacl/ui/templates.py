"""SACL V1 Decision Shell with Pure Black Palette, Model Picker, Focused Chat & Settings Drawer ("Tuerca")."""

HTML_APPLICATION = r"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SolidBit SACL · Decision Shell</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    :root {
      --bg: #000000;
      --surface: #0a0a0a;
      --surface-elevated: #111113;
      --surface-card: #0d0d0f;
      --border: rgba(255, 255, 255, 0.08);
      --border-focus: rgba(255, 255, 255, 0.18);
      --text: #ededed;
      --text-muted: #a1a1aa;
      --text-dim: #71717a;
      --accent: #ffffff;
      --accent-bg: #ffffff;
      --accent-fg: #000000;
      --success: #34d399;
      --warning: #fbbf24;
      --danger: #f87171;
      --mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      -webkit-font-smoothing: antialiased;
      height: 100vh;
      overflow: hidden;
    }
    .mono { font-family: var(--mono); }
    .bd { border-color: var(--border); }
    .surface { background: var(--surface); }
    .surface-elevated { background: var(--surface-elevated); }
    .t2 { color: var(--text-muted); }
    .t3 { color: var(--text-dim); }

    /* Resend Logo Container */
    .logo-black {
      width: 28px;
      height: 28px;
      background: #000000;
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      box-shadow: 0 0 12px rgba(255, 255, 255, 0.05);
      shrink: 0;
    }
    .logo-black img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      filter: contrast(120%) brightness(110%);
    }

    /* Buttons */
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      height: 32px;
      padding: 0 14px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all .15s ease;
      user-select: none;
    }
    .btn-primary {
      background: #ffffff;
      color: #000000;
      font-weight: 600;
      border: none;
    }
    .btn-primary:hover {
      background: #e4e4e7;
      transform: translateY(-1px);
    }
    .btn-secondary {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: var(--text);
    }
    .btn-secondary:hover {
      background: rgba(255, 255, 255, 0.09);
      border-color: rgba(255, 255, 255, 0.22);
      color: #ffffff;
    }
    .btn-danger {
      background: rgba(239, 68, 68, 0.12);
      border: 1px solid rgba(248, 113, 113, 0.35);
      color: #f87171;
    }
    .btn-danger:hover {
      background: rgba(239, 68, 68, 0.22);
      color: #fca5a5;
    }

    /* Prompt Chips */
    .prompt-chip {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 9999px;
      font-size: 12px;
      color: var(--text-muted);
      cursor: pointer;
      transition: all .15s ease;
      user-select: none;
    }
    .prompt-chip:hover {
      background: rgba(255, 255, 255, 0.08);
      border-color: rgba(255, 255, 255, 0.18);
      color: #ffffff;
      transform: translateY(-1px);
    }

    /* Chat Scroll Area */
    .chat-scroll {
      scrollbar-width: thin;
      scrollbar-color: rgba(255,255,255,0.15) transparent;
    }
    .chat-scroll::-webkit-scrollbar {
      width: 6px;
    }
    .chat-scroll::-webkit-scrollbar-thumb {
      background: rgba(255,255,255,0.15);
      border-radius: 9999px;
    }

    /* Slide-over Settings Drawer ("La Tuerca") */
    .drawer-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(8px);
      z-index: 1000;
      opacity: 0;
      pointer-events: none;
      transition: opacity .25s ease;
    }
    .drawer-overlay.open { opacity: 1; pointer-events: auto; }

    .settings-drawer {
      position: fixed;
      top: 0;
      right: -920px;
      width: 880px;
      max-width: 95vw;
      height: 100vh;
      background: #09090b;
      border-left: 1px solid var(--border-focus);
      z-index: 1001;
      display: flex;
      flex-direction: column;
      transition: right .3s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: -24px 0 80px rgba(0,0,0,0.9);
    }
    .settings-drawer.open { right: 0; }

    .impact-drawer {
      position: fixed;
      top: 0;
      right: -640px;
      width: 600px;
      max-width: 90vw;
      height: 100vh;
      background: #09090b;
      border-left: 1px solid var(--border-focus);
      z-index: 1100;
      display: flex;
      flex-direction: column;
      transition: right .3s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: -20px 0 60px rgba(0,0,0,0.85);
    }
    .impact-drawer.open { right: 0; }

    /* Resend Tab Nav inside Settings */
    .tab-btn {
      padding: 6px 14px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 500;
      color: var(--text-muted);
      cursor: pointer;
      transition: all .15s;
      border: 1px solid transparent;
      white-space: nowrap;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .tab-btn:hover {
      color: #ffffff;
      background: rgba(255, 255, 255, 0.04);
    }
    .tab-btn.active {
      color: #ffffff;
      background: rgba(255, 255, 255, 0.08);
      border-color: rgba(255, 255, 255, 0.14);
    }

    .tab-pane { display: none; }
    .tab-pane.active { display: block; animation: fadeIn .18s ease-out; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

    /* Critical Action Card */
    .critical-card {
      background: linear-gradient(180deg, rgba(249,115,22,0.05), rgba(249,115,22,0.02));
      border: 1px solid rgba(249,115,22,0.24);
      border-top: 2px solid #f97316;
      border-radius: 12px;
      padding: 22px;
      box-shadow: 0 8px 32px -8px rgba(249,115,22,0.18), 0 2px 8px rgba(0,0,0,0.5);
    }

    /* Toast Notification System */
    .toast-container {
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 2000;
      display: flex;
      flex-direction: column;
      gap: 8px;
      pointer-events: none;
    }
    .toast {
      pointer-events: auto;
      background: #111113;
      border: 1px solid rgba(255,255,255,0.15);
      border-radius: 10px;
      padding: 12px 18px;
      font-size: 13px;
      color: #ffffff;
      box-shadow: 0 12px 36px rgba(0,0,0,0.85);
      display: flex;
      align-items: center;
      gap: 10px;
      animation: slideIn .2s ease-out;
    }
    @keyframes slideIn {
      from { transform: translateY(12px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }

    /* SVG Donut Chart */
    .donut-bg { stroke: rgba(255, 255, 255, 0.06); }
    .donut-bar { stroke: #34d399; transition: stroke-dashoffset 0.6s cubic-bezier(0.16, 1, 0.3, 1); }
  </style>
</head>
<body class="flex flex-col h-screen overflow-hidden">

  <!-- Floating Toast Container -->
  <div id="toast-container" class="toast-container"></div>

  <!-- ==================== RESEND TOP HEADER ==================== -->
  <header class="h-14 border-b bd flex items-center justify-between px-6 shrink-0 surface select-none z-20">
    
    <!-- Left: Brand & Disc Logo -->
    <div class="flex items-center gap-3">
      <div class="logo-black">
        <img alt="SolidBit" src="data:image/png;base64,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">
      </div>
      <div class="leading-tight">
        <div class="text-[14px] font-semibold tracking-tight text-white flex items-center gap-2">
          <span>SolidBit SACL</span>
          <span class="mono text-[10px] px-1.5 py-0.2 rounded bg-white/10 text-zinc-300 border border-white/10">PRO</span>
        </div>
        <div class="text-[11px] t3 tracking-[0.1em]">SOVEREIGN SDLC CONTROL LOOP</div>
      </div>
    </div>

    <!-- Center: Model Selector Dropdown -->
    <div class="flex items-center gap-2 bg-black/60 border border-white/10 hover:border-white/20 rounded-lg px-2.5 py-1 transition">
      <i data-i="sparkles" class="text-zinc-400 w-3.5 h-3.5"></i>
      <select id="main-model-select" onchange="switchModelDirect(this.value)" class="bg-transparent text-white text-xs font-medium focus:outline-none cursor-pointer pr-1">
        <option value="claude-3-7-sonnet" selected class="bg-zinc-900 text-white">Claude 3.7 Sonnet (Hybrid)</option>
        <option value="claude-3-5-sonnet" class="bg-zinc-900 text-white">Claude 3.5 Sonnet</option>
        <option value="gemini-2-flash" class="bg-zinc-900 text-white">Gemini 2.0 Flash (Fast Agent Loop)</option>
        <option value="gemini-1-5-pro" class="bg-zinc-900 text-white">Gemini 1.5 Pro</option>
        <option value="gpt-4o" class="bg-zinc-900 text-white">GPT-4o</option>
        <option value="deepseek-r1" class="bg-zinc-900 text-white">DeepSeek R1</option>
      </select>
    </div>

    <!-- Right: SSE Status, Project & Settings Gear ("Tuerca") -->
    <div class="flex items-center gap-3">
      <!-- SSE LIVE PUSH Indicator -->
      <div class="flex items-center gap-2 text-xs text-emerald-400 font-medium px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399] animate-pulse"></span>
        <span>SSE LIVE PUSH</span>
      </div>

      <!-- Active Project Tag -->
      <button onclick="openSettingsDrawer('projects')" class="hidden sm:inline-flex items-center gap-1.5 text-xs t2 hover:text-white px-2.5 py-1 rounded bg-white/[0.04] border border-white/10 hover:border-white/20 transition cursor-pointer">
        <i data-i="folder" class="w-3.5 h-3.5"></i>
        <span id="header-active-project">Stable-Ecommerce</span>
      </button>

      <!-- Settings Gear Button ("La Tuerca" ⚙️) -->
      <button id="btn-open-settings" onclick="openSettingsDrawer('overview')" class="btn-secondary h-8 w-8 p-0 rounded-lg text-zinc-300 hover:text-white transition flex items-center justify-center relative cursor-pointer" title="Configuración y Centro Operativo SDLC">
        <i data-i="settings" class="w-4 h-4"></i>
        <span id="tuerca-gate-badge" class="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-orange-500 text-black font-bold text-[10px] flex items-center justify-center">1</span>
      </button>
    </div>

  </header>

  <!-- ==================== MAIN CLEAN CHAT VIEW ==================== -->
  <main class="flex-1 flex flex-col items-center justify-between overflow-hidden relative bg-[#000000]">
    
    <!-- Chat Messages Scroll Container -->
    <div id="chat-messages-container" class="chat-scroll flex-1 w-full max-w-3xl mx-auto overflow-y-auto px-4 py-6 space-y-4">
      
      <!-- Welcome Hero (Displayed initially) -->
      <div id="chat-welcome-hero" class="text-center py-8 space-y-3">
        <div class="w-12 h-12 rounded-full bg-white/[0.06] border border-white/10 flex items-center justify-center mx-auto mb-2 shadow-[0_0_24px_rgba(255,255,255,0.06)]">
          <div class="logo-black w-8 h-8">
            <img alt="SolidBit" src="data:image/png;base64,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">
          </div>
        </div>
        <h1 class="text-xl font-semibold text-white tracking-tight">SolidBit SACL · Asistente Soberano</h1>
        <p class="text-xs t2 max-w-md mx-auto leading-relaxed">
          Orquestador soberano 100% funcional conectado a tu base de datos SQLite WAL y contratos (<code class="mono text-zinc-300">DR-INV-001</code>, <code class="mono text-zinc-300">DR-PAY-001</code>). Puedes lanzar sprints, aprobar compuertas o auditar código directamente aquí.
        </p>

        <!-- Quick Action Prompt Chips -->
        <div class="flex items-center justify-center flex-wrap gap-2 pt-3">
          <button class="prompt-chip" onclick="quickSendPrompt('Lanzar sprint SACL productization v1')">
            <i data-i="rocket" class="w-3.5 h-3.5 text-emerald-400"></i>
            <span>Lanzar Sprint SACL V1</span>
          </button>
          <button class="prompt-chip" onclick="quickSendPrompt('Auditar contratos inmutables DR-INV-001 y DR-PAY-001')">
            <i data-i="shield" class="w-3.5 h-3.5 text-blue-400"></i>
            <span>Auditar Contratos</span>
          </button>
          <button class="prompt-chip" onclick="quickSendPrompt('Revisar compuertas humanas de decisión pendientes')">
            <i data-i="gate" class="w-3.5 h-3.5 text-orange-400"></i>
            <span>Ver Compuertas Pendientes</span>
          </button>
          <button class="prompt-chip" onclick="quickSendPrompt('Estado de la suite de pruebas unitarias')">
            <i data-i="check-circle" class="w-3.5 h-3.5 text-zinc-300"></i>
            <span>Suite de Pruebas (683/683 Pass)</span>
          </button>
          <button class="prompt-chip" onclick="quickSendPrompt('Verificar gateway de correo electrónico bi-direccional')">
            <i data-i="mail" class="w-3.5 h-3.5 text-emerald-400"></i>
            <span>Gateway de Correo</span>
          </button>
        </div>
      </div>

      <!-- Dynamic Messages Stream injected here -->
      <div id="chat-messages-stream" class="space-y-4"></div>

    </div>

    <!-- Floating Chat Input Bar -->
    <div class="w-full max-w-3xl mx-auto px-4 pb-4 pt-1">
      <div class="surface-card border border-white/12 rounded-2xl p-3 shadow-2xl space-y-2">
        <textarea
          id="chat-input-textarea"
          rows="2"
          placeholder="Escribe una instrucción al orquestador (ej. 'Lanzar sprint', 'Auditar DR-INV-001', 'Ver compuertas pendientes', 'Autorizar compuerta')..."
          class="w-full bg-transparent text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none resize-none leading-relaxed"
          onkeydown="handleChatKeydown(event)"
        ></textarea>
        
        <div class="flex items-center justify-between pt-1 border-t border-white/[0.06]">
          <div class="flex items-center gap-2">
            <span class="mono text-[11px] t3 flex items-center gap-1.5">
              <i data-i="shield" class="w-3.5 h-3.5 text-emerald-400"></i>
              <span>Guardrails Soberanos (Hard Deny)</span>
            </span>
            <span class="t3 text-[11px]">·</span>
            <button onclick="clearChatHistoryAction()" class="text-[11px] t3 hover:text-zinc-200 transition cursor-pointer">
              Limpiar historial
            </button>
          </div>

          <div class="flex items-center gap-2">
            <span class="text-[11px] t3 hidden sm:inline">Enter para enviar · Shift+Enter para salto</span>
            <button
              id="chat-send-btn"
              onclick="submitChatPromptAction()"
              class="w-7 h-7 rounded-full bg-white text-black flex items-center justify-center hover:bg-zinc-200 transition font-bold cursor-pointer shadow-sm"
              title="Enviar instrucción"
            >
              <i data-i="send" class="w-3.5 h-3.5"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

  </main>

  <!-- ==================== SETTINGS & SDLC DRAWER ("LA TUERCA" ⚙️) ==================== -->
  <div id="settings-drawer-overlay" class="drawer-overlay" onclick="closeSettingsDrawer()"></div>

  <aside id="settings-drawer" class="settings-drawer">
    
    <!-- Drawer Header -->
    <div class="h-16 border-b bd px-6 flex items-center justify-between shrink-0 surface select-none">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-white/10 border border-white/10 flex items-center justify-center">
          <i data-i="settings" class="text-white w-4 h-4"></i>
        </div>
        <div>
          <h2 class="text-sm font-semibold text-white">Configuración & Centro Operativo SDLC</h2>
          <p class="text-xs t2">Gobernanza, compuertas de decisión, contratos, DAGs y telemetría</p>
        </div>
      </div>
      <button onclick="closeSettingsDrawer()" class="btn-secondary h-8 w-8 p-0 rounded-lg text-zinc-300 hover:text-white flex items-center justify-center cursor-pointer">
        <i data-i="x" class="w-4 h-4"></i>
      </button>
    </div>

    <!-- Horizontal Tabs Selector -->
    <div class="border-b bd px-4 py-2 flex items-center gap-1.5 overflow-x-auto bg-black/40 select-none">
      <button class="tab-btn active" onclick="switchSettingsTab('overview', this)">
        <i data-i="dashboard" class="w-3.5 h-3.5"></i><span>Visión General</span>
      </button>
      <button class="tab-btn" onclick="switchSettingsTab('gates', this)">
        <i data-i="gate" class="w-3.5 h-3.5"></i><span>Decision Gates</span>
        <span class="mono text-[10px] px-1.5 py-0.2 rounded-full bg-orange-500 text-black font-bold" id="tab-gates-badge">1</span>
      </button>
      <button class="tab-btn" onclick="switchSettingsTab('telemetry', this)">
        <i data-i="activity" class="w-3.5 h-3.5"></i><span>Ejecución en Vivo</span>
      </button>
      <button class="tab-btn" onclick="switchSettingsTab('roadmap', this)">
        <i data-i="calendar" class="w-3.5 h-3.5"></i><span>Roadmap SDLC</span>
      </button>
      <button class="tab-btn" onclick="switchSettingsTab('designer', this)">
        <i data-i="workflow" class="w-3.5 h-3.5"></i><span>Diseñador DAG</span>
      </button>
      <button class="tab-btn" onclick="switchSettingsTab('email', this)">
        <i data-i="mail" class="w-3.5 h-3.5"></i><span>Email Gateway</span>
        <span class="mono text-[9px] px-1 py-0.2 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">E2E</span>
      </button>
      <button class="tab-btn" onclick="switchSettingsTab('connections', this)">
        <i data-i="plug" class="w-3.5 h-3.5"></i><span>Conexiones & Auth</span>
      </button>
      <button class="tab-btn" onclick="switchSettingsTab('contracts', this)">
        <i data-i="shield" class="w-3.5 h-3.5"></i><span>Contratos</span>
      </button>
      <button class="tab-btn" onclick="switchSettingsTab('db', this)">
        <i data-i="database" class="w-3.5 h-3.5"></i><span>Base de Datos</span>
      </button>
      <button class="tab-btn" onclick="switchSettingsTab('projects', this)">
        <i data-i="folder" class="w-3.5 h-3.5"></i><span>Proyectos</span>
      </button>
    </div>

    <!-- Drawer Content Area (Scrollable) -->
    <div class="flex-1 overflow-y-auto p-6 space-y-6">

      <!-- ==================== TAB 1: VISIÓN GENERAL ==================== -->
      <div id="settings-tab-overview" class="tab-pane active space-y-6">
        
        <!-- KPIs Row -->
        <div class="grid grid-cols-4 gap-4">
          <div class="rounded-xl border bd surface p-4">
            <div class="text-xs t2 font-medium">Readiness Score</div>
            <div class="text-2xl font-semibold tracking-tight text-white mt-1" id="val-readiness">94%</div>
            <div class="text-xs text-emerald-400 mt-1">Ecosistema validado</div>
          </div>
          <div class="rounded-xl border bd surface p-4">
            <div class="text-xs t2 font-medium">Campaña activa</div>
            <div class="text-2xl font-semibold tracking-tight text-white mt-1" id="val-active-camp">Productization V1</div>
            <div class="text-xs t2 mt-1">DAG de 9 workorders</div>
          </div>
          <div class="rounded-xl border bd surface p-4">
            <div class="text-xs t2 font-medium">Compuertas humanas</div>
            <div class="text-2xl font-semibold tracking-tight text-orange-400 mt-1" id="val-pending-gates">1</div>
            <div class="text-xs t2 mt-1">Esperando autorización</div>
          </div>
          <div class="rounded-xl border bd surface p-4">
            <div class="text-xs t2 font-medium">Pruebas unitarias</div>
            <div class="text-2xl font-semibold tracking-tight text-white mt-1">683<span class="text-sm t3"> / 683</span></div>
            <div class="text-xs text-emerald-400 mt-1">100% Pass en verde</div>
          </div>
        </div>

        <!-- Critical Action Card + Live Donut Row -->
        <div class="grid grid-cols-3 gap-4">
          <div class="col-span-2 critical-card" id="overview-critical-gate">
            <div class="flex items-center gap-2 mb-3">
              <i data-i="alert" class="text-orange-400 w-4 h-4"></i>
              <span class="text-xs font-semibold text-orange-300">Micro-decisión soberana requerida</span>
              <span class="ml-auto text-xs t2" id="gate-expiry-time">Expira en ~52 min</span>
            </div>

            <h3 class="text-lg font-semibold text-white tracking-tight" id="gate-action-title">Desplegar preview efímero en staging</h3>
            <div class="flex items-center gap-2 mt-2 flex-wrap">
              <span class="mono text-xs px-2 py-0.5 rounded bg-white/[0.06] border border-white/10 text-zinc-300" id="gate-action-code">DEPLOY_STAGING_PREVIEW</span>
              <span class="mono text-xs t2" id="gate-request-id-pill">REQ-PENDING</span>
              <span class="text-xs px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/25">Riesgo medio · reversible</span>
            </div>

            <dl class="grid grid-cols-3 gap-3 mt-4">
              <div class="rounded-lg border bd bg-black/40 p-3">
                <dt class="text-[11px] t2 flex items-center gap-1.5"><i data-i="bot" class="w-3.5 h-3.5"></i>Disparado por</dt>
                <dd class="text-xs text-white mt-1 font-medium" id="gate-triggered-by">Agente codegen · WO-04</dd>
              </div>
              <div class="rounded-lg border bd bg-black/40 p-3">
                <dt class="text-[11px] t2 flex items-center gap-1.5"><i data-i="server" class="w-3.5 h-3.5"></i>Impacto en infra</dt>
                <dd class="text-xs text-white mt-1 font-medium" id="gate-infra-impact">1 servicio Railway efímero</dd>
              </div>
              <div class="rounded-lg border bd bg-black/40 p-3">
                <dt class="text-[11px] t2 flex items-center gap-1.5"><i data-i="shield" class="w-3.5 h-3.5"></i>Contratos</dt>
                <dd class="text-xs text-white mt-1 font-medium">4 / 4 intactos</dd>
              </div>
            </dl>

            <div class="mt-5 flex items-center gap-3">
              <button class="btn btn-primary" onclick="quickApproveFromCard()">
                <i data-i="check" class="w-4 h-4"></i><span>Autorizar Despliegue</span>
              </button>
              <button class="btn btn-danger" onclick="quickRejectFromCard()">
                <i data-i="x" class="w-4 h-4"></i><span>Rechazar</span>
              </button>
              <button class="btn btn-secondary ml-auto" onclick="inspectDiffAndImpact(activeGateId)">
                <i data-i="diff" class="w-4 h-4"></i><span>Ver Impacto & Diff</span>
              </button>
              <button class="btn btn-secondary" onclick="notifyMobileForCurrentGate()">
                <i data-i="phone" class="w-4 h-4"></i><span>Móvil</span>
              </button>
            </div>
          </div>

          <!-- SVG Donut Chart Card -->
          <div class="rounded-xl border bd surface p-5 flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between mb-3">
                <h4 class="text-xs font-semibold text-white uppercase tracking-wider">Avance del Sprint</h4>
                <span class="text-xs text-emerald-400 font-semibold" id="donut-percent">75%</span>
              </div>
              <div class="relative w-36 h-36 mx-auto my-2 flex items-center justify-center">
                <svg viewBox="0 0 100 100" class="w-full h-full -rotate-90">
                  <circle cx="50" cy="50" r="40" fill="none" stroke-width="10" class="donut-bg"></circle>
                  <circle id="donut-circle" cx="50" cy="50" r="40" fill="none" stroke-width="10" stroke-linecap="round" stroke-dasharray="251.32" stroke-dashoffset="62.83" class="donut-bar"></circle>
                </svg>
                <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <span class="text-xl font-bold text-white tracking-tight" id="donut-center-text">75%</span>
                  <span class="text-[10px] t3 uppercase">Completado</span>
                </div>
              </div>
            </div>
            <div class="border-t bd pt-3 space-y-1.5 text-xs">
              <div class="flex justify-between t2"><span>Workorders listos:</span><span class="text-white font-mono">3 / 4</span></div>
              <div class="flex justify-between t2"><span>Tokens consumidos:</span><span class="text-white font-mono">14,820</span></div>
            </div>
          </div>
        </div>

      </div>

      <!-- ==================== TAB 2: DECISION GATES ==================== -->
      <div id="settings-tab-gates" class="tab-pane space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-base font-semibold text-white">Compuertas Humanas de Decisión (Decision Gates)</h3>
            <p class="text-xs t2">Autorizaciones obligatorias antes de mutar infra o el árbol de git soberano</p>
          </div>
          <button class="btn btn-secondary text-xs" onclick="loadDashboardSnapshot()">
            <i data-i="refresh" class="w-3.5 h-3.5"></i><span>Actualizar</span>
          </button>
        </div>

        <div id="gates-list-container" class="rounded-xl border bd surface divide-y divide-white/[0.06]">
          <!-- Injected dynamically -->
        </div>
      </div>

      <!-- ==================== TAB 3: TELEMETRÍA EN VIVO ==================== -->
      <div id="settings-tab-telemetry" class="tab-pane space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-base font-semibold text-white">Telemetría de Agentes y Fases en Tiempo Real</h3>
            <p class="text-xs t2">Seguimiento de ejecución sin retardos vía Server-Sent Events</p>
          </div>
          <button class="btn btn-secondary text-xs" onclick="simulateTaskProgress()">
            <i data-i="play" class="w-3.5 h-3.5"></i><span>Simular Progreso (+15%)</span>
          </button>
        </div>

        <div class="grid grid-cols-5 gap-3" id="telemetry-phases-container">
          <!-- Injected dynamically -->
        </div>

        <div class="rounded-xl border bd surface p-4 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold text-white uppercase tracking-wider">Terminal de Registro Soberano</span>
            <button onclick="clearLogs()" class="text-xs t3 hover:text-white cursor-pointer">Limpiar</button>
          </div>
          <div class="bg-black/70 rounded-lg p-3 mono text-xs text-zinc-300 h-44 overflow-y-auto space-y-1" id="terminal-logs-body">
            <div class="t3">[12:30:38] Scheduler inicializado en modo determinista.</div>
            <div class="text-emerald-400">[12:30:40] Contratos DR-INV-001 y DR-PAY-001 verificados (0 violaciones).</div>
            <div class="text-blue-400">[12:30:45] Workorder WO-01 completado con éxito.</div>
            <div class="text-orange-400">[12:31:02] Compuerta humana emitida. Esperando decisión del operador.</div>
          </div>
        </div>
      </div>

      <!-- ==================== TAB 4: ROADMAP SDLC ==================== -->
      <div id="settings-tab-roadmap" class="tab-pane space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-base font-semibold text-white">Roadmap SDLC & Gobernanza</h3>
            <p class="text-xs t2">Plan estratégico de estabilización y despliegue del ecosistema SolidBit</p>
          </div>
        </div>
        <div class="space-y-3" id="roadmap-phases-container"></div>
      </div>

      <!-- ==================== TAB 5: DISEÑADOR DAG ==================== -->
      <div id="settings-tab-designer" class="tab-pane space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-base font-semibold text-white">Diseñador Visual de Campañas (DAG)</h3>
            <p class="text-xs t2">Topología de workorders, dependencias y compuertas automáticas</p>
          </div>
          <button class="btn btn-primary text-xs" onclick="launchActiveCampaign()">
            <i data-i="rocket" class="w-3.5 h-3.5"></i><span>Lanzar Campaña (1-Click)</span>
          </button>
        </div>
        <div class="grid grid-cols-2 gap-3" id="designer-nodes-container"></div>
      </div>

      <!-- ==================== TAB 6: EMAIL GATEWAY ==================== -->
      <div id="settings-tab-email" class="tab-pane space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-base font-semibold text-white">Gateway de Correo Bi-Direccional</h3>
            <p class="text-xs t2">Notificaciones de agentes y autorización vía correo seguro con token HMAC</p>
          </div>
          <div class="flex items-center gap-2">
            <button class="btn btn-secondary text-xs" onclick="testSendEmail()">
              <i data-i="mail" class="w-3.5 h-3.5"></i><span>Enviar Reporte</span>
            </button>
            <button class="btn btn-secondary text-xs" onclick="simulateInboundEmail()">
              <i data-i="bot" class="w-3.5 h-3.5"></i><span>Simular Respuesta</span>
            </button>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="rounded-xl border bd surface p-4 space-y-2">
            <div class="text-xs font-semibold text-white">Canal Saliente (Agentes &rarr; Operador)</div>
            <div class="text-xs t2">Remitente: <code class="mono text-zinc-300">lucilfer@selfcaresinners.com</code></div>
            <div class="text-xs t2">Destinatario: <code class="mono text-zinc-300">lawlieeet@outlook.es</code></div>
          </div>
          <div class="rounded-xl border bd surface p-4 space-y-2">
            <div class="text-xs font-semibold text-white">Canal Entrante (Operador &rarr; Agentes)</div>
            <div class="text-xs t2">De: <code class="mono text-zinc-300">lawlieeet@outlook.es</code></div>
            <div class="text-xs t2">Para: <code class="mono text-zinc-300">lucilfer@selfcaresinners.com</code></div>
          </div>
        </div>

        <div class="rounded-xl border bd surface overflow-hidden">
          <table class="w-full text-left text-xs">
            <thead class="border-b bd bg-white/[0.02] text-zinc-400">
              <tr>
                <th class="px-4 py-3">Dirección</th>
                <th class="px-4 py-3">Ruta</th>
                <th class="px-4 py-3">Asunto</th>
                <th class="px-4 py-3">Estado</th>
                <th class="px-4 py-3 text-right">Hora</th>
              </tr>
            </thead>
            <tbody id="email-logs-tbody" class="divide-y divide-white/[0.04]"></tbody>
          </table>
        </div>
      </div>

      <!-- ==================== TAB 7: CONEXIONES & AUTH ==================== -->
      <div id="settings-tab-connections" class="tab-pane space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-base font-semibold text-white">Conexiones Tecnológicas & Autenticación E2E</h3>
            <p class="text-xs t2">Lanza el navegador para autenticarte o ejecuta pruebas dirigidas</p>
          </div>
        </div>
        <div class="grid grid-cols-3 gap-3" id="connections-grid-container">
          <!-- Injected dynamically -->
        </div>
      </div>

      <!-- ==================== TAB 8: CONTRATOS INMUTABLES ==================== -->
      <div id="settings-tab-contracts" class="tab-pane space-y-4">
        <div>
          <h3 class="text-base font-semibold text-white">Catálogo de Contratos Inmutables (Inviolables)</h3>
          <p class="text-xs t2">Políticas soberanas con supremacía de rechazo tajante (Hard Deny)</p>
        </div>
        <div class="space-y-3">
          <div class="rounded-xl border bd surface p-4">
            <div class="flex items-center justify-between mb-1">
              <span class="mono text-xs font-semibold text-emerald-400">DR-INV-001</span>
              <span class="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">LOCKED</span>
            </div>
            <h4 class="text-sm font-semibold text-white">Reserva Atómica de SellableUnit</h4>
            <p class="text-xs t2 mt-1">Garantiza cero colisiones de inventario concurrente mediante ledger inmutable.</p>
          </div>
          <div class="rounded-xl border bd surface p-4">
            <div class="flex items-center justify-between mb-1">
              <span class="mono text-xs font-semibold text-emerald-400">DR-PAY-001</span>
              <span class="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">LOCKED</span>
            </div>
            <h4 class="text-sm font-semibold text-white">Captura Transaccional de Pagos de Doble Partida</h4>
            <p class="text-xs t2 mt-1">Cero sobrecargos y verificación estricta de saldo contable en Stripe.</p>
          </div>
        </div>
      </div>

      <!-- ==================== TAB 9: BASE DE DATOS & WAL ==================== -->
      <div id="settings-tab-db" class="tab-pane space-y-4">
        <div>
          <h3 class="text-base font-semibold text-white">Inspector de Base de Datos SQLite & WAL</h3>
          <p class="text-xs t2">Monitoreo de checkpoints WAL, consistencia ACID y logs de auditoría</p>
        </div>
        <div class="grid grid-cols-3 gap-3" id="db-stats-container"></div>
      </div>

      <!-- ==================== TAB 10: PROYECTOS ==================== -->
      <div id="settings-tab-projects" class="tab-pane space-y-4">
        <div>
          <h3 class="text-base font-semibold text-white">Espacios de Trabajo Multirrama (Proyectos)</h3>
          <p class="text-xs t2">Cambia de contexto de proyecto de forma instantánea</p>
        </div>
        <div class="space-y-2" id="projects-list-container"></div>
      </div>

    </div>

  </aside>

  <!-- ==================== VISUAL IMPACT & DIFF DRAWER ==================== -->
  <div id="impact-drawer-overlay" class="drawer-overlay" onclick="closeImpactDrawer()"></div>

  <div id="impact-drawer" class="impact-drawer">
    <div class="h-16 border-b bd px-6 flex items-center justify-between shrink-0 surface select-none">
      <div class="flex items-center gap-2">
        <i data-i="diff" class="text-orange-400 w-4 h-4"></i>
        <h3 class="text-sm font-semibold text-white">Cajón de Impacto Visual & Diff</h3>
      </div>
      <button onclick="closeImpactDrawer()" class="btn-secondary h-8 w-8 p-0 rounded-lg text-zinc-300 hover:text-white flex items-center justify-center cursor-pointer">
        <i data-i="x" class="w-4 h-4"></i>
      </button>
    </div>

    <div class="flex-1 overflow-y-auto p-6 space-y-5">
      <div>
        <div class="text-xs t3 uppercase font-medium">Compuerta evaluada</div>
        <div class="mono text-sm font-semibold text-white mt-0.5" id="drawer-req-id">REQ-PENDING</div>
        <div class="text-xs text-orange-400 mt-1" id="drawer-action-name">DEPLOY_STAGING_PREVIEW</div>
      </div>

      <div class="rounded-lg border bd bg-black/40 p-4 space-y-2 text-xs">
        <div class="flex justify-between t2"><span>Impacto en producción:</span><span class="text-emerald-400 font-semibold" id="drawer-prod-impact">0 servicios mutados</span></div>
        <div class="flex justify-between t2"><span>Servicios efímeros:</span><span class="text-white font-mono" id="drawer-infra-summary">1 Railway Staging Preview</span></div>
        <div class="flex justify-between t2"><span>Contratos auditados:</span><span class="text-emerald-400 font-semibold">DR-INV-001, DR-PAY-001 OK</span></div>
      </div>

      <div>
        <div class="text-xs font-semibold text-white mb-2">Commits afectados en la rama</div>
        <div class="rounded-lg border bd bg-black/60 divide-y divide-white/[0.06] text-xs" id="drawer-commits-list"></div>
      </div>

      <div>
        <div class="text-xs font-semibold text-white mb-2">Diff de código unificado</div>
        <div class="rounded-lg border bd bg-black p-3.5 mono text-xs text-zinc-300 overflow-x-auto whitespace-pre font-mono" id="drawer-diff-content"></div>
      </div>
    </div>

    <div class="h-16 border-t bd px-6 flex items-center justify-end gap-3 shrink-0 surface select-none">
      <button class="btn btn-secondary cursor-pointer" onclick="closeImpactDrawer()">Cerrar</button>
      <button class="btn btn-danger cursor-pointer" onclick="submitDrawerDecision('REJECTED')">Rechazar</button>
      <button class="btn btn-primary cursor-pointer" onclick="submitDrawerDecision('APPROVED')">Autorizar Despliegue</button>
    </div>
  </div>

  <!-- Lucide Icons & App Logic -->
  <script src="https://unpkg.com/lucide@latest"></script>
  <script>
    // Lucide Icon Initializer
    function renderIcons() {
      if (window.lucide) {
        window.lucide.createIcons();
      }
    }

    // API BASE: Works seamlessly whether opened directly via file:// or via http://127.0.0.1:8765
    const API_BASE = (window.location.protocol === 'file:') ? 'http://127.0.0.1:8765' : '';

    // Toast Notification System
    function showToast(message, type = 'info') {
      const container = document.getElementById('toast-container');
      if (!container) return;
      const t = document.createElement('div');
      t.className = 'toast';
      let iconColor = type === 'success' ? '#34d399' : type === 'error' ? '#f87171' : '#60a5fa';
      t.innerHTML = `
        <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${iconColor};"></span>
        <span>${escapeHtml(message)}</span>
      `;
      container.appendChild(t);
      setTimeout(() => {
        t.style.opacity = '0';
        t.style.transition = 'opacity .3s';
        setTimeout(() => t.remove(), 300);
      }, 3500);
    }

    // State Variables
    let activeGateId = null;
    let currentModelId = 'claude-3-7-sonnet';

    // Settings Drawer Controls
    function openSettingsDrawer(tab = 'overview') {
      document.getElementById('settings-drawer-overlay').classList.add('open');
      document.getElementById('settings-drawer').classList.add('open');
      if (tab) {
        const btn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick')?.includes(tab));
        if (btn) switchSettingsTab(tab, btn);
      }
    }

    function closeSettingsDrawer() {
      document.getElementById('settings-drawer-overlay').classList.remove('open');
      document.getElementById('settings-drawer').classList.remove('open');
    }

    function switchSettingsTab(tabId, el) {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      if (el) el.classList.add('active');
      const pane = document.getElementById(`settings-tab-${tabId}`);
      if (pane) pane.classList.add('active');
      renderIcons();
    }

    // Impact Drawer Controls
    async function inspectDiffAndImpact(reqId) {
      const idToFetch = reqId || activeGateId;
      if (!idToFetch) {
        showToast('No hay compuerta seleccionada para inspeccionar', 'error');
        return;
      }
      try {
        const res = await fetch(`${API_BASE}/api/gates/impact?request_id=${encodeURIComponent(idToFetch)}`);
        const data = await res.json();
        document.getElementById('drawer-req-id').innerText = data.request_id || idToFetch;
        document.getElementById('drawer-action-name').innerText = data.action || 'DEPLOY_STAGING_PREVIEW';

        const commitsEl = document.getElementById('drawer-commits-list');
        commitsEl.innerHTML = (data.commits || []).map(c => `
          <div class="px-3.5 py-2 flex items-center justify-between">
            <span class="mono text-zinc-400">${c.sha}</span>
            <span class="text-zinc-200 truncate ml-2 mr-auto">${c.subject}</span>
            <span class="t3">${c.author}</span>
          </div>`).join('') || '<div class="p-3 t2">No hay commits afectados o rama limpia.</div>';

        document.getElementById('drawer-diff-content').innerText = data.diff_preview || 'Sin diff visual en el alcance.';
        
        document.getElementById('impact-drawer-overlay').classList.add('open');
        document.getElementById('impact-drawer').classList.add('open');
        renderIcons();
      } catch (e) {
        console.error(e);
        showToast('Error al cargar diff de impacto', 'error');
      }
    }

    function closeImpactDrawer() {
      document.getElementById('impact-drawer-overlay').classList.remove('open');
      document.getElementById('impact-drawer').classList.remove('open');
    }

    async function submitDrawerDecision(decision) {
      if (!activeGateId) {
        showToast('No hay compuerta activa', 'error');
        return;
      }
      await submitGateDecisionDirect(activeGateId, decision);
      closeImpactDrawer();
    }

    async function submitGateDecisionDirect(reqId, decision) {
      if (!reqId) return;
      try {
        const res = await fetch(`${API_BASE}/api/gates/decide`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ request_id: reqId, decision: decision, justification: 'Decidido desde SACL Decision Shell' })
        });
        const data = await res.json();
        if (data.success) {
          showToast(`Compuerta ${reqId} ${decision === 'APPROVED' ? 'AUTORIZADA' : 'RECHAZADA'}`, 'success');
        } else {
          showToast(data.message || 'Error registrando decisión', 'error');
        }
        loadDashboardSnapshot();
        loadChatHistory();
      } catch (e) {
        console.error(e);
        showToast('Error de conexión con el backend', 'error');
      }
    }

    function quickApproveFromCard() {
      if (activeGateId) submitGateDecisionDirect(activeGateId, 'APPROVED');
    }
    function quickRejectFromCard() {
      if (activeGateId) submitGateDecisionDirect(activeGateId, 'REJECTED');
    }

    async function notifyMobileForCurrentGate() {
      if (!activeGateId) return;
      try {
        const res = await fetch(`${API_BASE}/api/gates/notify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ request_id: activeGateId, channel: 'resend' })
        });
        const data = await res.json();
        showToast(data.message || 'Notificación móvil despachada vía Resend.', 'success');
      } catch (e) {
        console.error(e);
        showToast('Error despachando notificación móvil', 'error');
      }
    }

    // Model Selection
    async function switchModelDirect(modelId) {
      currentModelId = modelId;
      try {
        await fetch(`${API_BASE}/api/model/select`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ model_id: modelId })
        });
        showToast(`Modelo activo actualizado a ${modelId}`, 'info');
      } catch (e) {
        console.error(e);
      }
    }

    // Chat Logic
    async function loadChatHistory() {
      try {
        const res = await fetch(`${API_BASE}/api/chat/history`);
        const data = await res.json();
        renderChatMessages(data.history || []);
      } catch (e) {
        console.error(e);
      }
    }

    function renderChatMessages(msgs) {
      const hero = document.getElementById('chat-welcome-hero');
      const stream = document.getElementById('chat-messages-stream');
      if (!stream) return;

      if (msgs.length > 1 && hero) {
        hero.style.display = 'none';
      } else if (hero) {
        hero.style.display = 'block';
      }

      stream.innerHTML = msgs.map(m => {
        const isUser = (m.role === 'user');
        if (isUser) {
          return `
          <div class="flex flex-col items-end">
            <div class="bg-white/[0.08] border border-white/10 rounded-2xl rounded-tr-sm px-4 py-3 max-w-[85%] text-[13px] text-zinc-100 shadow-sm leading-relaxed">
              ${escapeHtml(m.content)}
            </div>
            <div class="text-[10px] t3 mt-1 mr-1 mono">${m.timestamp ? m.timestamp.split('T')[1].slice(0,8) : ''}</div>
          </div>`;
        } else {
          let actionBtns = '';
          if (m.action_data) {
            if (m.action_data.type === 'GATE_PENDING') {
              actionBtns = `
              <div class="flex items-center gap-2 mt-2 pt-2 border-t border-white/[0.08]">
                <button onclick="inspectDiffAndImpact('${m.action_data.gate_id}')" class="btn btn-secondary text-xs text-orange-400 border-orange-500/30 hover:border-orange-500/50 cursor-pointer">
                  <i data-i="diff" class="w-3.5 h-3.5"></i><span>Ver Diff & Impacto</span>
                </button>
                <button onclick="submitGateDecisionDirect('${m.action_data.gate_id}', 'APPROVED')" class="btn btn-primary text-xs cursor-pointer">
                  <i data-i="check" class="w-3.5 h-3.5"></i><span>Autorizar Ahora</span>
                </button>
              </div>`;
            } else if (m.action_data.type === 'CAMPAIGN_LAUNCHED') {
              actionBtns = `
              <div class="mt-2 pt-2 border-t border-white/[0.08]">
                <button onclick="openSettingsDrawer('designer')" class="btn btn-secondary text-xs text-emerald-400 border-emerald-500/30 hover:border-emerald-500/50 cursor-pointer">
                  <i data-i="workflow" class="w-3.5 h-3.5"></i><span>Abrir Diseñador DAG (${m.action_data.run_id})</span>
                </button>
              </div>`;
            }
          }
          return `
          <div class="flex items-start gap-3">
            <div class="logo-black w-7 h-7 shrink-0 mt-1">
              <img alt="SolidBit" src="data:image/png;base64,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">
            </div>
            <div class="flex-1 max-w-[90%]">
              <div class="surface border border-white/10 rounded-2xl rounded-tl-sm p-4 text-[13px] text-zinc-200 leading-relaxed space-y-2">
                ${formatMarkdown(m.content)}
                ${actionBtns}
              </div>
              <div class="text-[10px] t3 mt-1 ml-1 mono">${m.timestamp ? m.timestamp.split('T')[1].slice(0,8) : ''}</div>
            </div>
          </div>`;
        }
      }).join('');

      // Auto-scroll chat
      const container = document.getElementById('chat-messages-container');
      if (container) container.scrollTop = container.scrollHeight;
      renderIcons();
    }

    function handleChatKeydown(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        submitChatPromptAction();
      }
    }

    function quickSendPrompt(txt) {
      const input = document.getElementById('chat-input-textarea');
      if (input) {
        input.value = txt;
        submitChatPromptAction();
      }
    }

    async function submitChatPromptAction() {
      const input = document.getElementById('chat-input-textarea');
      const val = (input?.value || '').trim();
      if (!val) return;
      input.value = '';

      // Optimistic UI insert
      const stream = document.getElementById('chat-messages-stream');
      const hero = document.getElementById('chat-welcome-hero');
      if (hero) hero.style.display = 'none';

      const tempUserMsg = document.createElement('div');
      tempUserMsg.className = 'flex flex-col items-end';
      tempUserMsg.innerHTML = `
        <div class="bg-white/[0.08] border border-white/10 rounded-2xl rounded-tr-sm px-4 py-3 max-w-[85%] text-[13px] text-zinc-100 shadow-sm leading-relaxed">
          ${escapeHtml(val)}
        </div>
        <div class="text-[10px] t3 mt-1 mr-1 mono">Enviando...</div>
      `;
      stream.appendChild(tempUserMsg);

      const tempBotMsg = document.createElement('div');
      tempBotMsg.className = 'flex items-start gap-3';
      tempBotMsg.innerHTML = `
        <div class="logo-black w-7 h-7 shrink-0 mt-1">
          <img alt="SolidBit" src="data:image/png;base64,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">
        </div>
        <div class="flex-1 max-w-[90%]">
          <div class="surface border border-white/10 rounded-2xl rounded-tl-sm p-4 text-[13px] text-zinc-400 leading-relaxed flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>SACL procesando instrucción con ${currentModelId}...</span>
          </div>
        </div>
      `;
      stream.appendChild(tempBotMsg);

      const container = document.getElementById('chat-messages-container');
      if (container) container.scrollTop = container.scrollHeight;

      try {
        const res = await fetch(`${API_BASE}/api/chat/message`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: val, model_id: currentModelId })
        });
        const d = await res.json();
        loadChatHistory();
        loadDashboardSnapshot();
      } catch (e) {
        console.error(e);
        showToast('Error de comunicación con el asistente', 'error');
        loadChatHistory();
      }
    }

    async function clearChatHistoryAction() {
      if (!confirm('¿Deseas reiniciar la conversación con el asistente?')) return;
      try {
        await fetch(`${API_BASE}/api/chat/clear`, { method: 'POST' });
        loadChatHistory();
        showToast('Historial reiniciado', 'info');
      } catch (e) {
        console.error(e);
      }
    }

    // Helpers
    function escapeHtml(str) {
      return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }
    function formatMarkdown(txt) {
      if (!txt) return '';
      let s = escapeHtml(txt);
      s = s.replace(/\*\*(.+?)\*\*/g, '<strong class="text-white font-semibold">$1</strong>');
      s = s.replace(/`([^`]+)`/g, '<code class="mono text-xs px-1.5 py-0.5 rounded bg-white/[0.08] text-zinc-300 border border-white/10">$1</code>');
      s = s.replace(/\n/g, '<br>');
      return s;
    }

    // Dashboard Data Loader & Dynamic Binding
    async function loadDashboardSnapshot() {
      try {
        const res = await fetch(`${API_BASE}/api/snapshot?mode=audit`);
        const data = await res.json();
        
        if (data.readiness_score !== undefined) {
          document.getElementById('val-readiness').innerText = `${data.readiness_score}%`;
        }
        if (data.active_campaign) {
          document.getElementById('val-active-camp').innerText = data.active_campaign;
        }
        if (data.active_project) {
          document.getElementById('header-active-project').innerText = data.active_project;
        }

        // Dynamic Gate Binding
        const pendingGates = data.pending_gates || [];
        const gateBadge = document.getElementById('tuerca-gate-badge');
        const tabGateBadge = document.getElementById('tab-gates-badge');
        const valGates = document.getElementById('val-pending-gates');
        const critCard = document.getElementById('overview-critical-gate');
        const gatesContainer = document.getElementById('gates-list-container');

        valGates.innerText = pendingGates.length;
        tabGateBadge.innerText = pendingGates.length;

        if (pendingGates.length > 0) {
          const g = pendingGates[0];
          activeGateId = g.request_id || g.approval_id;
          gateBadge.style.display = 'flex';
          gateBadge.innerText = pendingGates.length;

          document.getElementById('gate-action-title').innerText = g.reason || g.action;
          document.getElementById('gate-action-code').innerText = g.action;
          document.getElementById('gate-request-id-pill').innerText = activeGateId;
          document.getElementById('gate-infra-impact').innerText = g.scope || '1 servicio Railway';
          critCard.style.display = 'block';

          // Decision Gates Tab Rendering
          if (gatesContainer) {
            gatesContainer.innerHTML = pendingGates.map(gate => `
              <div class="p-4 flex items-center justify-between">
                <div>
                  <div class="flex items-center gap-2">
                    <span class="mono text-xs px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/25">PENDING</span>
                    <span class="mono text-xs font-semibold text-white">${gate.request_id || gate.approval_id}</span>
                    <span class="text-xs t2">· ${gate.action}</span>
                  </div>
                  <div class="text-xs t2 mt-1">${gate.reason || 'Compuerta de decisión obligatoria'}</div>
                </div>
                <div class="flex items-center gap-2">
                  <button class="btn btn-secondary text-xs cursor-pointer" onclick="inspectDiffAndImpact('${gate.request_id || gate.approval_id}')">
                    <i data-i="diff" class="w-3.5 h-3.5"></i><span>Diff & Impacto</span>
                  </button>
                  <button class="btn btn-primary text-xs cursor-pointer" onclick="submitGateDecisionDirect('${gate.request_id || gate.approval_id}', 'APPROVED')">
                    <i data-i="check" class="w-3.5 h-3.5"></i><span>Autorizar</span>
                  </button>
                  <button class="btn btn-danger text-xs cursor-pointer" onclick="submitGateDecisionDirect('${gate.request_id || gate.approval_id}', 'REJECTED')">
                    <i data-i="x" class="w-3.5 h-3.5"></i><span>Rechazar</span>
                  </button>
                </div>
              </div>`).join('');
          }
        } else {
          activeGateId = null;
          gateBadge.style.display = 'none';
          document.getElementById('gate-action-title').innerText = 'Ecosistema Limpio · Todas las compuertas autorizadas';
          document.getElementById('gate-action-code').innerText = 'STATUS_OPTIMAL';
          document.getElementById('gate-request-id-pill').innerText = 'ZERO_PENDING';
          document.getElementById('gate-infra-impact').innerText = 'Sin cambios pendientes';

          if (gatesContainer) {
            gatesContainer.innerHTML = `
              <div class="p-8 text-center text-xs t2 space-y-2">
                <i data-i="check-circle" class="w-6 h-6 text-emerald-400 mx-auto"></i>
                <div>No hay compuertas pendientes. El control loop soberano se encuentra 100% operativo.</div>
                <button class="btn btn-secondary text-xs mt-2 cursor-pointer" onclick="launchActiveCampaign()">
                  <i data-i="rocket" class="w-3.5 h-3.5"></i><span>Lanzar Nueva Campaña</span>
                </button>
              </div>`;
          }
        }

        // Populate Connections
        const connsRes = await fetch(`${API_BASE}/api/connections`);
        const connsData = await connsRes.json();
        const connsGrid = document.getElementById('connections-grid-container');
        if (connsGrid) {
          connsGrid.innerHTML = (connsData.connections || []).map(c => `
            <div class="rounded-xl border bd surface p-4 space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-sm font-semibold text-white">${c.name}</span>
                <span class="mono text-xs px-2 py-0.5 rounded ${c.status === 'connected' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/25' : 'bg-red-500/10 text-red-400 border border-red-500/25'}">${c.status.toUpperCase()}</span>
              </div>
              <div class="text-xs t2">${c.version || c.error_message || 'Integración SDLC soberana'}</div>
              <div class="flex items-center gap-2 pt-2 border-t bd">
                <button class="btn btn-secondary text-xs flex-1 cursor-pointer" onclick="launchBrowserAuthAction('${c.id}')">
                  <i data-i="external-link" class="w-3.5 h-3.5"></i><span>Navegador</span>
                </button>
                <button class="btn btn-secondary text-xs cursor-pointer" onclick="testConnectionSingle('${c.id}')">
                  <i data-i="activity" class="w-3.5 h-3.5"></i><span>Probar</span>
                </button>
              </div>
            </div>`).join('');
        }

        // Populate Telemetry Phases
        const telRes = await fetch(`${API_BASE}/api/telemetry`);
        const telData = await telRes.json();
        const telPhases = document.getElementById('telemetry-phases-container');
        if (telPhases && telData.phases) {
          telPhases.innerHTML = telData.phases.map(p => `
            <div class="rounded-lg border bd surface p-3">
              <div class="text-[11px] t3">${p.name}</div>
              <div class="text-base font-semibold text-white mt-1">${p.weight}%</div>
              <div class="text-[10px] ${p.completed ? 'text-emerald-400' : 't3'} mt-0.5">${p.completed ? 'Completado' : 'En progreso'}</div>
            </div>`).join('');
        }

        // Populate Roadmap
        const roadRes = await fetch(`${API_BASE}/api/roadmap`);
        const roadData = await roadRes.json();
        const roadContainer = document.getElementById('roadmap-phases-container');
        if (roadContainer && roadData.phases) {
          roadContainer.innerHTML = roadData.phases.map(p => `
            <div class="rounded-xl border bd surface p-4 space-y-2">
              <div class="flex items-center justify-between">
                <div>
                  <span class="mono text-xs text-emerald-400 font-semibold">${p.code}</span>
                  <h4 class="text-sm font-semibold text-white">${p.name}</h4>
                </div>
                <div class="text-right">
                  <span class="text-base font-semibold text-white">${p.progress}%</span>
                  <div class="text-xs t3">${p.period}</div>
                </div>
              </div>
              <div class="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                <div class="bg-emerald-400 h-full" style="width:${p.progress}%"></div>
              </div>
            </div>`).join('');
        }

        // Populate Designer
        const desRes = await fetch(`${API_BASE}/api/campaigns/designer`);
        const desData = await desRes.json();
        const desContainer = document.getElementById('designer-nodes-container');
        if (desContainer && desData.nodes) {
          desContainer.innerHTML = desData.nodes.map(n => `
            <div class="rounded-xl border bd surface p-4 space-y-2">
              <div class="mono text-xs t3">${n.id}</div>
              <h4 class="text-sm font-semibold text-white">${n.label}</h4>
              <div class="text-xs text-emerald-400 font-mono">Acción: ${n.action}</div>
              <div class="text-xs ${n.gate_required ? 'text-amber-400' : 't3'}">
                ${n.gate_required ? 'Compuerta humana requerida' : 'Ejecución 100% autónoma'}
              </div>
            </div>`).join('');
        }

        // Populate DB Stats
        const dbRes = await fetch(`${API_BASE}/api/db/stats`);
        const dbData = await dbRes.json();
        const dbContainer = document.getElementById('db-stats-container');
        if (dbContainer) {
          dbContainer.innerHTML = `
            <div class="rounded-xl border bd surface p-4">
              <div class="text-xs t2">Modo WAL</div>
              <div class="text-lg font-semibold text-emerald-400 mt-1">${dbData.journal_mode || 'WAL'}</div>
            </div>
            <div class="rounded-xl border bd surface p-4">
              <div class="text-xs t2">Checkpoints WAL</div>
              <div class="text-lg font-semibold text-white mt-1">${dbData.wal_checkpoints || 12}</div>
            </div>
            <div class="rounded-xl border bd surface p-4">
              <div class="text-xs t2">Tablas activas</div>
              <div class="text-lg font-semibold text-white mt-1">${dbData.table_count || 14}</div>
            </div>`;
        }

        // Populate Projects
        const projRes = await fetch(`${API_BASE}/api/projects`);
        const projData = await projRes.json();
        const projContainer = document.getElementById('projects-list-container');
        if (projContainer && projData.projects) {
          projContainer.innerHTML = projData.projects.map(p => `
            <div class="rounded-lg border bd surface p-3.5 flex items-center justify-between">
              <div>
                <div class="text-xs font-semibold text-white flex items-center gap-2">
                  <span>${p.name}</span>
                  ${p.active ? '<span class="mono text-[10px] px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-400">ACTIVO</span>' : ''}
                </div>
                <div class="text-xs t2 mt-0.5">${p.description}</div>
              </div>
              ${!p.active ? `<button class="btn btn-secondary text-xs cursor-pointer" onclick="switchProjectAction('${p.id}')">Cambiar</button>` : ''}
            </div>`).join('');
        }

        // Load Email Logs
        loadEmailData();

        renderIcons();
      } catch (e) {
        console.error('Error fetching snapshot:', e);
      }
    }

    async function launchActiveCampaign() {
      try {
        const res = await fetch(`${API_BASE}/api/campaigns/launch`, { method: 'POST' });
        const data = await res.json();
        showToast(data.message || 'Campaña iniciada con éxito en worktree aislado.', 'success');
        loadDashboardSnapshot();
        loadChatHistory();
      } catch (e) {
        console.error(e);
        showToast('Error al iniciar campaña', 'error');
      }
    }

    async function launchBrowserAuthAction(toolId) {
      try {
        const res = await fetch(`${API_BASE}/api/connections/browser-auth`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tool_id: toolId })
        });
        const data = await res.json();
        if (data.auth_url) {
          window.open(data.auth_url, '_blank');
          showToast(`Abriendo navegador para ${toolId}...`, 'info');
        }
      } catch (e) {
        console.error(e);
        showToast('Error lanzando navegador', 'error');
      }
    }

    async function testConnectionSingle(toolId) {
      try {
        const res = await fetch(`${API_BASE}/api/connections/test`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tool_id: toolId })
        });
        const data = await res.json();
        showToast(`${toolId.toUpperCase()}: ${data.status || 'OK'}`, data.status === 'connected' ? 'success' : 'error');
        loadDashboardSnapshot();
      } catch (e) {
        console.error(e);
      }
    }

    async function switchProjectAction(projectId) {
      try {
        await fetch(`${API_BASE}/api/projects/switch`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: projectId })
        });
        showToast(`Cambiado a proyecto: ${projectId}`, 'success');
        loadDashboardSnapshot();
      } catch (e) {
        console.error(e);
      }
    }

    async function loadEmailData() {
      try {
        const res = await fetch(`${API_BASE}/api/email/config`);
        const data = await res.json();
        const tbody = document.getElementById('email-logs-tbody');
        if (!tbody) return;
        tbody.innerHTML = (data.recent_logs || []).map(l => {
          const isOut = (l.direction === 'OUTBOUND');
          return `
          <tr class="hover:bg-white/[0.02]">
            <td class="px-4 py-3"><span class="text-[10px] px-1.5 py-0.5 rounded ${isOut ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'}">${l.direction}</span></td>
            <td class="px-4 py-3 mono text-xs t2">${l.from} &rarr; ${l.to}</td>
            <td class="px-4 py-3 text-white font-medium">${l.subject}</td>
            <td class="px-4 py-3"><span class="text-xs font-semibold text-emerald-400">${l.status}</span></td>
            <td class="px-4 py-3 text-right t2 text-xs">${(l.timestamp || '').split('T')[1]?.slice(0,8) || ''}</td>
          </tr>`;
        }).join('');
      } catch (e) {
        console.error(e);
      }
    }

    async function testSendEmail() {
      try {
        const res = await fetch(`${API_BASE}/api/email/test`, { method: 'POST' });
        const d = await res.json();
        showToast(d.message || 'Reporte de agentes enviado a lawlieeet@outlook.es', 'success');
        loadEmailData();
      } catch (e) {
        console.error(e);
        showToast('Error enviando correo', 'error');
      }
    }

    async function simulateInboundEmail() {
      try {
        const res = await fetch(`${API_BASE}/api/webhooks/inbound-email`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            from: 'lawlieeet@outlook.es',
            subject: 'AUTORIZAR SPRINT',
            text: 'Proceder con la campaña en el worktree aislado.'
          })
        });
        const d = await res.json();
        showToast(d.message || 'Comando recibido por correo. Agentes activados.', 'success');
        loadEmailData();
      } catch (e) {
        console.error(e);
      }
    }

    async function simulateTaskProgress() {
      const circle = document.getElementById('donut-circle');
      const text = document.getElementById('donut-percent');
      const centerText = document.getElementById('donut-center-text');
      const cur = parseInt(text.innerText) || 75;
      const nextVal = Math.min(100, cur + 15);
      
      text.innerText = `${nextVal}%`;
      centerText.innerText = `${nextVal}%`;
      const offset = 251.32 - (251.32 * nextVal / 100);
      circle.style.strokeDashoffset = offset;

      try {
        await fetch(`${API_BASE}/api/telemetry/progress`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ progress: nextVal, phase: 'Auditoría de Invariantes' })
        });
        showToast(`Progreso avanzado al ${nextVal}%`, 'info');
      } catch (e) {
        console.error(e);
      }
    }

    function clearLogs() {
      const t = document.getElementById('terminal-logs-body');
      if (t) t.innerHTML = '';
      showToast('Registro de terminal limpiado', 'info');
    }

    // SSE Connection Setup
    function setupSSE() {
      try {
        const ev = new EventSource(`${API_BASE}/api/events`);
        ev.addEventListener('gate_decided', () => { loadDashboardSnapshot(); loadChatHistory(); });
        ev.addEventListener('campaign_launched', () => { loadDashboardSnapshot(); loadChatHistory(); });
        ev.addEventListener('chat_message', () => { loadChatHistory(); });
        ev.addEventListener('telemetry_updated', () => { loadDashboardSnapshot(); });
      } catch (e) {
        console.error('SSE Error:', e);
      }
    }

    // Initial Bootstrap
    window.addEventListener('DOMContentLoaded', () => {
      renderIcons();
      loadChatHistory();
      loadDashboardSnapshot();
      setupSSE();
    });
  </script>
</body>
</html>
"""
