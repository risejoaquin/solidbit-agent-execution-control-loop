"""Compiled Engineering & Operations Console Template (Autor: LUCILFER / risejoaquin)."""

HTML_APPLICATION = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>SolidBit SACL · Control de Operaciones · Autor LUCILFER / risejoaquin</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <style>
    :root {
      --bg: #0b0c10;
      --surface: #121318;
      --surface-elevated: #181a22;
      --surface-card: #14151c;
      --border: rgba(255, 255, 255, 0.08);
      --border-strong: rgba(255, 255, 255, 0.16);
      --text: #f4f4f6;
      --text-muted: #9ca3af;
      --text-dim: #6b7280;
      --accent-green: #10b981;
      --accent-amber: #f59e0b;
      --accent-blue: #3b82f6;
    }
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      overflow-x: hidden;
      margin: 0;
      padding: 0;
    }
    .mono {
      font-family: 'JetBrains Mono', monospace;
    }
    .bd {
      border-color: var(--border);
    }
    .bd-strong {
      border-color: var(--border-strong);
    }
    .section-canvas {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 18px;
      box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
    }
    .section-canvas:hover {
      border-color: var(--border-strong);
    }
    .item-card {
      background: var(--surface-card);
      border: 1px solid var(--border);
      border-radius: 12px;
      transition: all 0.15s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .item-card:hover {
      border-color: var(--border-strong);
      background: #171822;
    }
    .item-card.selected {
      border-color: rgba(16, 185, 129, 0.6);
      background: #121817;
    }
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      border-radius: 8px;
      font-weight: 600;
      transition: all 0.15s ease;
      cursor: pointer;
    }
    .btn:active {
      transform: scale(0.98);
    }
    .btn-primary {
      background-color: #ffffff;
      color: #000000;
    }
    .btn-primary:hover {
      background-color: #e5e7eb;
    }
    .btn-secondary {
      background-color: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border);
      color: #ffffff;
    }
    .btn-secondary:hover {
      background-color: rgba(255, 255, 255, 0.1);
      border-color: var(--border-strong);
    }
    .btn-success {
      background-color: #10b981;
      color: #000000;
    }
    .btn-success:hover {
      background-color: #34d399;
    }
    .btn-danger {
      background-color: rgba(239, 68, 68, 0.12);
      border: 1px solid rgba(239, 68, 68, 0.25);
      color: #f87171;
    }
    .btn-danger:hover {
      background-color: rgba(239, 68, 68, 0.22);
      border-color: rgba(239, 68, 68, 0.4);
    }
    .nav-pill {
      padding: 0.45rem 0.9rem;
      border-radius: 8px;
      font-size: 0.8125rem;
      font-weight: 600;
      color: var(--text-muted);
      transition: all 0.15s ease;
      cursor: pointer;
    }
    .nav-pill:hover {
      color: #ffffff;
      background-color: rgba(255, 255, 255, 0.04);
    }
    .nav-pill.active {
      color: #ffffff;
      background-color: rgba(255, 255, 255, 0.12);
    }
    .mobile-tab {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 0.25rem;
      font-size: 0.6875rem;
      color: var(--text-dim);
      transition: all 0.15s ease;
      cursor: pointer;
      padding: 0.35rem 0.5rem;
    }
    .mobile-tab.active {
      color: #10b981;
    }
    .custom-scroll::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    .custom-scroll::-webkit-scrollbar-track {
      background: transparent;
    }
    .custom-scroll::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.15);
      border-radius: 9999px;
    }
    .custom-scroll::-webkit-scrollbar-thumb:hover {
      background: rgba(255, 255, 255, 0.3);
    }
    .toast-animate {
      animation: toastIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes toastIn {
      from { transform: translateY(0.75rem); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
    .no-scrollbar::-webkit-scrollbar {
      display: none;
    }
    .no-scrollbar {
      -ms-overflow-style: none;
      scrollbar-width: none;
    }
  </style>
</head>
<body class="flex flex-col h-screen bg-[#0b0c10] text-[#f4f4f6]">

  <!-- TOP HEADER (HIGH DENSITY ENGINEERING BAR) -->
  <header class="h-16 border-b bd flex items-center justify-between px-3 md:px-6 bg-[#0b0c10]/95 backdrop-blur-md z-30 shrink-0">
    <!-- Brand & Workspace -->
    <div class="flex items-center gap-3">
      <div class="w-9 h-9 rounded-xl bg-white/5 flex items-center justify-center border bd overflow-hidden shrink-0 cursor-pointer" onclick="switchSection('dashboard')">
        <img src="data:image/png;base64,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" alt="SolidBit" class="w-5 h-5 object-contain invert">
      </div>
      <div>
        <div class="flex items-center gap-2">
          <span class="text-sm font-bold tracking-tight text-white">SolidBit SACL</span>
          <span class="text-[10px] mono px-2 py-0.5 rounded-full bg-white/10 text-zinc-300 font-semibold">SOVEREIGN V1.2</span>
        </div>
        <div class="text-[11px] mono text-zinc-400 flex items-center gap-1.5 truncate max-w-[150px] sm:max-w-xs">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span id="header-active-project-name" class="font-medium text-zinc-300 truncate">Stable-Ecommerce-Orchestrator</span>
        </div>
      </div>
    </div>

    <!-- Desktop Navigation Tabs -->
    <div class="hidden md:flex items-center p-1 rounded-xl bg-white/5 border bd gap-1">
      <button id="dtab-dashboard" class="nav-pill active flex items-center gap-1.5" onclick="switchSection('dashboard')">
        <i data-lucide="layout-grid" class="w-3.5 h-3.5"></i>
        <span>Operaciones HUD</span>
      </button>
      <button id="dtab-gates" class="nav-pill flex items-center gap-1.5" onclick="switchSection('gates')">
        <i data-lucide="shield-alert" class="w-3.5 h-3.5 text-amber-400"></i>
        <span>Gobernanza & Compuertas</span>
        <span id="nav-gates-count" class="mono text-[10px] px-1.5 py-0.2 rounded-full bg-amber-500/20 text-amber-300 font-bold">1</span>
      </button>
      <button id="dtab-sdlc" class="nav-pill flex items-center gap-1.5" onclick="switchSection('sdlc')">
        <i data-lucide="play-circle" class="w-3.5 h-3.5"></i>
        <span>Pipelines SDLC</span>
      </button>
      <button id="dtab-projects" class="nav-pill flex items-center gap-1.5" onclick="switchSection('projects')">
        <i data-lucide="folder-git-2" class="w-3.5 h-3.5"></i>
        <span>Repos & Docs</span>
      </button>
      <button id="dtab-chat" class="nav-pill flex items-center gap-1.5" onclick="switchSection('chat')">
        <i data-lucide="terminal" class="w-3.5 h-3.5"></i>
        <span>Consola REPL</span>
      </button>
    </div>

    <!-- Right Controls -->
    <div class="flex items-center gap-2.5">
      <!-- Author Pill Badge -->
      <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 border bd text-xs font-medium text-white shadow-sm">
        <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
        <span class="text-zinc-400 text-[10px] uppercase font-bold tracking-wider">Autor:</span>
        <span class="font-bold text-white tracking-tight">LUCILFER</span>
        <span class="mono text-zinc-400 text-[10px] hidden sm:inline">/ @risejoaquin</span>
      </div>

      <!-- Live Indicator (Required for test suite) -->
      <div class="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-emerald-500/20 bg-emerald-500/10 text-emerald-400 text-xs font-semibold">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
        <span class="mono text-[11px]">SSE LIVE PUSH</span>
      </div>

      <!-- Terminal Drawer Button -->
      <button onclick="openTerminalDrawer()" class="px-3 py-1.5 rounded-lg border bd bg-white/5 hover:bg-white/10 text-emerald-400 cursor-pointer flex items-center gap-1.5 text-xs font-medium" title="Terminal en Vivo">
        <i data-lucide="terminal" class="w-3.5 h-3.5"></i>
        <span class="hidden sm:inline mono">Terminal Logs</span>
      </button>

      <!-- Settings Drawer Button -->
      <button onclick="openSettingsDrawer()" class="relative p-2 rounded-lg border bd bg-white/5 hover:bg-white/10 text-white cursor-pointer" title="Configuración de Sistema">
        <i data-lucide="sliders" class="w-4 h-4"></i>
        <span id="tuerca-gate-badge" class="absolute -top-1 -right-1 w-4 h-4 bg-amber-400 text-black text-[10px] font-bold rounded-full flex items-center justify-center border border-black hidden">1</span>
      </button>
    </div>
  </header>

  <!-- MAIN SCROLLABLE CONTAINER WITH GENEROUS SECTIONING -->
  <main class="flex-1 overflow-y-auto pb-24 md:pb-8 custom-scroll">

    <!-- ========================================== -->
    <!-- SECTION 1: OPERACIONES HUD (DASHBOARD) -->
    <!-- ========================================== -->
    <div id="sec-dashboard" class="p-4 md:p-8 max-w-7xl mx-auto space-y-8">

      <!-- HERO STATUS BANNER (WELL SPACED, NO CLUTTER) -->
      <div class="section-canvas p-6 md:p-8 relative overflow-hidden bg-gradient-to-br from-[#14161f] via-[#101217] to-[#0c0d12]">
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          <div class="space-y-3">
            <div class="flex flex-wrap items-center gap-2">
              <span class="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/25 text-xs font-bold mono flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                SISTEMA OPERACIONAL
              </span>
              <span class="px-2.5 py-0.5 rounded-full bg-white/5 text-zinc-300 border bd text-xs font-mono">
                commit 8dc3bb4
              </span>
              <span class="px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/25 text-xs font-mono font-semibold">
                branch sacl-implementation-e69378
              </span>
            </div>

            <h1 class="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
              Ecosistema Operacional Soberano
            </h1>

            <p class="text-sm text-zinc-400 max-w-2xl leading-relaxed">
              Orquestación autónoma de ciclo de vida de software bajo <span class="text-zinc-200 font-semibold">Hard Deny Supremacy</span>.
              Invariantes <code class="mono text-emerald-400">DR-INV-001</code> y <code class="mono text-emerald-400">DR-PAY-001</code> verificados con cero tolerancia a bypass.
            </p>
          </div>

          <!-- Direct Execution Actions -->
          <div class="grid grid-cols-2 sm:flex sm:flex-wrap items-center gap-3 shrink-0">
            <button onclick="executeAction('reconcile_runs', {}, this)" class="btn btn-secondary px-4 py-3 text-xs">
              <i data-lucide="refresh-cw" class="w-4 h-4 text-emerald-400"></i>
              <span>Reconciliar Procesos</span>
            </button>
            <button onclick="executeAction('test_suite', {}, this)" class="btn btn-secondary px-4 py-3 text-xs">
              <i data-lucide="check-square" class="w-4 h-4 text-purple-400"></i>
              <span>Correr Tests (29)</span>
            </button>
            <button onclick="executeAction('security_audit', {}, this)" class="btn btn-secondary px-4 py-3 text-xs">
              <i data-lucide="shield" class="w-4 h-4 text-blue-400"></i>
              <span>Auditar DR-INV</span>
            </button>
            <button onclick="openTerminalDrawer()" class="btn btn-primary px-4 py-3 text-xs">
              <i data-lucide="terminal" class="w-4 h-4 fill-black"></i>
              <span>Terminal Monospace</span>
            </button>
          </div>
        </div>
      </div>

      <!-- SECTION: TELEMETRÍA Y ESTADO DEL SISTEMA -->
      <div class="space-y-4">
        <div class="flex items-center justify-between border-b bd pb-2.5">
          <div class="flex items-center gap-2">
            <i data-lucide="activity" class="w-4 h-4 text-emerald-400"></i>
            <h2 class="text-sm font-bold uppercase tracking-wider text-zinc-200">Telemetría de Base & Runtime</h2>
          </div>
          <span class="mono text-xs text-zinc-500">sacl_ops.db · SQLite WAL</span>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- Card 1: Crash Consistency -->
          <div class="item-card p-5 space-y-3">
            <div class="flex items-center justify-between text-xs text-zinc-400">
              <span class="font-medium">Consistencia Crash</span>
              <span id="metric-recovery-badge" class="mono text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/25">CLEAN_STEADY</span>
            </div>
            <div class="text-2xl font-bold mono text-white" id="metric-interrupted-runs">0 Interrumpidos</div>
            <div class="text-xs text-zinc-400 flex items-center justify-between pt-2 border-t bd">
              <span>Runs SQLite Reconciliados: <b class="text-zinc-200">11</b></span>
              <button onclick="executeAction('reconcile_runs', {}, this)" class="text-emerald-400 hover:underline font-semibold cursor-pointer">Reconciliar</button>
            </div>
          </div>

          <!-- Card 2: Invariants -->
          <div class="item-card p-5 space-y-3">
            <div class="flex items-center justify-between text-xs text-zinc-400">
              <span class="font-medium">Invariantes Congelados</span>
              <span class="mono text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/25">ENFORCED</span>
            </div>
            <div class="text-2xl font-bold mono text-white">Zero-Bypass</div>
            <div class="text-xs text-zinc-400 truncate pt-2 border-t bd">
              DR-INV-001 (Stock) · DR-PAY-001 (Ledger)
            </div>
          </div>

          <!-- Card 3: Git VCS -->
          <div class="item-card p-5 space-y-3">
            <div class="flex items-center justify-between text-xs text-zinc-400">
              <span class="font-medium">Control de Versiones</span>
              <span class="mono text-[10px] font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/25">GIT 2.54</span>
            </div>
            <div class="text-2xl font-bold mono text-white truncate" title="impl-20261007-203727-e69378">impl-e69378</div>
            <div class="text-xs text-zinc-400 truncate pt-2 border-t bd">
              Clean · 18 commits ahead · @risejoaquin
            </div>
          </div>

          <!-- Card 4: Toolchain -->
          <div class="item-card p-5 space-y-3">
            <div class="flex items-center justify-between text-xs text-zinc-400">
              <span class="font-medium">Lattice de Herramientas</span>
              <span class="mono text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/25">6/6 ACTIVAS</span>
            </div>
            <div class="text-2xl font-bold mono text-white">lucilfer / @rise</div>
            <div class="text-xs text-zinc-400 truncate pt-2 border-t bd">
              Railway · GH CLI · Resend · Py 3.11
            </div>
          </div>
        </div>
      </div>

      <!-- SECTION: GOBERNANZA DESTACADA & ACTIVIDAD -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <!-- COMPUERTA PENDIENTE (PROMINENTE) -->
        <div class="section-canvas p-6 space-y-4 lg:col-span-2 border-amber-500/30 bg-gradient-to-br from-[#161412] to-[#121318]">
          <div class="flex items-center justify-between border-b bd pb-3">
            <div class="flex items-center gap-2.5">
              <span class="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse"></span>
              <div>
                <h3 class="text-sm font-bold uppercase tracking-wider text-white">Compuerta Humana Pendiente</h3>
                <div class="text-xs text-zinc-400">Decisión soberana requerida antes del merge o despliegue.</div>
              </div>
            </div>
            <span id="gate-request-id-pill" class="mono text-xs px-2.5 py-1 rounded bg-black/40 border bd text-zinc-300">REQ-20261025-406DBE23</span>
          </div>

          <div class="p-4 rounded-xl bg-black/50 border bd space-y-3">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <div class="text-base font-bold text-white mono" id="gate-action-title">DEPLOY_STAGING_PREVIEW</div>
                <div class="text-xs text-zinc-400 mt-1">Verificación de despliegue efímero en Railway antes de merge a main.</div>
              </div>
              <span class="px-2.5 py-1 rounded text-[11px] mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/25 uppercase shrink-0 w-fit">
                COMPUERTA BLOQUEANTE
              </span>
            </div>

            <div class="flex flex-wrap items-center justify-between pt-2 border-t bd text-xs text-zinc-400">
              <span class="flex items-center gap-1.5"><i data-lucide="clock" class="w-3.5 h-3.5 text-zinc-500"></i><span>TTL: 7 días restantes</span></span>
              <span class="flex items-center gap-1.5"><i data-lucide="file-code" class="w-3.5 h-3.5 text-blue-400"></i><span class="mono">services/web-storefront, railway.json</span></span>
            </div>
          </div>

          <!-- Action buttons with high visual distinction -->
          <div class="grid grid-cols-3 gap-3 pt-1">
            <button onclick="inspectCurrentGateImpact()" class="btn btn-secondary text-xs py-2.5">
              <i data-lucide="file-diff" class="w-4 h-4 text-zinc-300"></i>
              <span>Ver Diff & Impacto</span>
            </button>
            <button onclick="quickRejectFromCard()" class="btn btn-danger text-xs py-2.5">
              <i data-lucide="x-circle" class="w-4 h-4"></i>
              <span>Rechazar</span>
            </button>
            <button onclick="quickApproveFromCard()" class="btn btn-success text-xs py-2.5">
              <i data-lucide="check" class="w-4 h-4"></i>
              <span>Autorizar Despliegue</span>
            </button>
          </div>
        </div>

        <!-- LEDGER DE AUDITORÍA EN VIVO (WAL) -->
        <div class="section-canvas p-6 space-y-4">
          <div class="flex items-center justify-between border-b bd pb-3">
            <div class="flex items-center gap-2">
              <i data-lucide="scroll-text" class="w-4 h-4 text-emerald-400"></i>
              <h3 class="text-sm font-bold uppercase tracking-wider text-white">Ledger de Auditoría</h3>
            </div>
            <span class="mono text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400">WAL LIVE</span>
          </div>

          <div id="live-audit-feed-container" class="space-y-2.5 max-h-[320px] overflow-y-auto custom-scroll pr-1">
            <div class="p-3 rounded-lg bg-black/40 border bd space-y-1">
              <div class="flex items-center justify-between text-[11px] mono">
                <span class="text-emerald-400 font-bold">STALE_LOCK_RECLAIMED</span>
                <span class="text-zinc-500">08:09:45</span>
              </div>
              <div class="text-xs text-zinc-300">Lease SUPERVISOR_SINGLETON renovado tras crash de PID 21140.</div>
            </div>
            <div class="p-3 rounded-lg bg-black/40 border bd space-y-1">
              <div class="text-[11px] mono flex items-center justify-between">
                <span class="text-red-400 font-bold">DIRTY_ROOT_SAFETY_HALT</span>
                <span class="text-zinc-500">08:09:33</span>
              </div>
              <div class="text-xs text-zinc-300">78 cambios detectados en repo primario. Reset destructivo prevenido.</div>
            </div>
            <div class="p-3 rounded-lg bg-black/40 border bd space-y-1">
              <div class="text-[11px] mono flex items-center justify-between">
                <span class="text-amber-400 font-bold">GATE_HALTED</span>
                <span class="text-zinc-500">08:09:33</span>
              </div>
              <div class="text-xs text-zinc-300">Compuerta JOB-GATE-001 requiere aprobación humana antes de staging.</div>
            </div>
          </div>
        </div>

      </div>

    </div>

    <!-- ========================================== -->
    <!-- SECTION 2: GOBERNANZA & COMPUERTAS (TAB) -->
    <!-- ========================================== -->
    <div id="sec-gates" class="p-4 md:p-8 max-w-7xl mx-auto space-y-6 hidden">
      <div class="border-b bd pb-4">
        <h2 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
          <i data-lucide="shield-alert" class="w-6 h-6 text-amber-400"></i>
          <span>Compuertas de Gobernanza & Decisiones Humanas</span>
        </h2>
        <p class="text-sm text-zinc-400 mt-1">Supervisión en tiempo real de compuertas requeridas antes del merge o despliegue a producción.</p>
      </div>

      <!-- Featured Gate Card -->
      <div class="section-canvas p-6 md:p-8 space-y-6 border-amber-500/30 bg-gradient-to-br from-[#161412] to-[#121318]">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b bd pb-4">
          <div>
            <span class="px-2.5 py-0.5 rounded text-xs mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/25 uppercase">
              COMPUERTA BLOQUEANTE ACTIVA
            </span>
            <h3 class="text-xl font-bold text-white mono mt-2">JOB-GATE-001: DEPLOY_STAGING_PREVIEW</h3>
            <p class="text-xs text-zinc-400 mt-1">Solicitado para entorno efímero en Railway antes de merge a main.</p>
          </div>
          <div class="flex items-center gap-2">
            <button onclick="inspectCurrentGateImpact()" class="btn btn-secondary text-xs px-4 py-2.5">
              <i data-lucide="file-diff" class="w-4 h-4"></i>
              <span>Inspeccionar Diff</span>
            </button>
            <button onclick="quickRejectFromCard()" class="btn btn-danger text-xs px-4 py-2.5">
              <i data-lucide="x-circle" class="w-4 h-4"></i>
              <span>Rechazar</span>
            </button>
            <button onclick="quickApproveFromCard()" class="btn btn-success text-xs px-5 py-2.5">
              <i data-lucide="check" class="w-4 h-4"></i>
              <span>Autorizar Despliegue</span>
            </button>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
          <div class="p-3 rounded-lg bg-black/40 border bd">
            <span class="text-zinc-500">Request ID:</span>
            <div class="text-zinc-200 font-bold mt-0.5">REQ-20261025-406DBE23</div>
          </div>
          <div class="p-3 rounded-lg bg-black/40 border bd">
            <span class="text-zinc-500">Archivos Afectados:</span>
            <div class="text-zinc-200 font-bold mt-0.5">services/web-storefront, railway.json</div>
          </div>
          <div class="p-3 rounded-lg bg-black/40 border bd">
            <span class="text-zinc-500">Expiración (TTL):</span>
            <div class="text-zinc-200 font-bold mt-0.5">2026-11-01T04:10:05Z (7 días)</div>
          </div>
        </div>
      </div>

      <!-- Historical Decisions Table -->
      <div class="section-canvas p-6 space-y-4">
        <div class="flex items-center justify-between border-b bd pb-3">
          <h3 class="text-sm font-bold uppercase tracking-wider text-white">Historial de Decisiones de Gobernanza</h3>
          <span class="mono text-xs text-zinc-500">SQLite approvals</span>
        </div>
        <div class="overflow-x-auto custom-scroll">
          <table class="w-full text-left text-xs">
            <thead>
              <tr class="border-b bd text-zinc-400 font-semibold text-xs mono">
                <th class="py-2.5 pr-4">Approval ID</th>
                <th class="py-2.5 px-4">Acción</th>
                <th class="py-2.5 px-4">Decisión</th>
                <th class="py-2.5 px-4">Operador</th>
                <th class="py-2.5 pl-4">Fecha</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/5 mono text-xs" id="decisions-history-tbody-full">
              <tr>
                <td class="py-3 pr-4 text-zinc-300 font-semibold">appr-55ce1c77</td>
                <td class="py-3 px-4 text-zinc-300">DEPLOY_STAGING_PREVIEW</td>
                <td class="py-3 px-4"><span class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold border border-emerald-500/25">APPROVED</span></td>
                <td class="py-3 px-4 text-zinc-400">human_operator (CLI)</td>
                <td class="py-3 pl-4 text-zinc-500">2026-10-25 08:04:12Z</td>
              </tr>
              <tr>
                <td class="py-3 pr-4 text-zinc-300 font-semibold">appr-2a5efdeb</td>
                <td class="py-3 px-4 text-zinc-300">DEPLOY_STAGING_PREVIEW</td>
                <td class="py-3 px-4"><span class="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold border border-emerald-500/25">APPROVED</span></td>
                <td class="py-3 px-4 text-zinc-400">human_operator (CLI)</td>
                <td class="py-3 pl-4 text-zinc-500">2026-10-25 04:09:54Z</td>
              </tr>
              <tr>
                <td class="py-3 pr-4 text-zinc-300 font-semibold">appr-0cb78c79</td>
                <td class="py-3 px-4 text-zinc-300">DEPLOY_STAGING_PREVIEW</td>
                <td class="py-3 px-4"><span class="px-2 py-0.5 rounded bg-zinc-500/10 text-zinc-400 font-bold border border-zinc-500/25">EXPIRED</span></td>
                <td class="py-3 px-4 text-zinc-500">Sistema (Timeout)</td>
                <td class="py-3 pl-4 text-zinc-500">2026-10-23 18:48:22Z</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- SECTION 3: PIPELINES SDLC & AUTOMATIZACIONES -->
    <!-- ========================================== -->
    <div id="sec-sdlc" class="p-4 md:p-8 max-w-7xl mx-auto space-y-6 hidden">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b bd pb-4">
        <div>
          <h2 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <i data-lucide="play-circle" class="w-6 h-6 text-emerald-400"></i>
            <span>Pipelines SDLC & Automatizaciones Soberanas</span>
          </h2>
          <p class="text-sm text-zinc-400 mt-1">Dispara pipelines, suites de pruebas y verificaciones con salida en tiempo real.</p>
        </div>

        <div class="flex items-center gap-2">
          <button onclick="executeAction('reconcile_runs', {}, this)" class="btn btn-secondary text-xs px-3.5 py-2">
            <i data-lucide="refresh-cw" class="w-3.5 h-3.5 text-emerald-400"></i>
            <span>Reconciliar Crashes</span>
          </button>
          <button onclick="openTerminalDrawer()" class="btn btn-secondary text-xs px-3.5 py-2 text-emerald-400">
            <i data-lucide="terminal" class="w-3.5 h-3.5"></i>
            <span>Consola Terminal</span>
          </button>
        </div>
      </div>

      <!-- Action Cards Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">

        <!-- Action Card 1: Pytest Suite -->
        <div class="section-canvas p-5 space-y-3.5" id="act-test-suite" onclick="handleCardSelectClick('test_suite', this, event)">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl bg-purple-500/10 border border-purple-500/25 flex items-center justify-center text-purple-400 shrink-0">
                <i data-lucide="check-square" class="w-5 h-5"></i>
              </div>
              <div>
                <h4 class="text-sm font-bold text-white uppercase tracking-tight">Suite de Pruebas Pytest</h4>
                <div class="text-xs mono text-zinc-400">test_cli_ui, test_modules (29 tests)</div>
              </div>
            </div>
            <input type="checkbox" class="action-checkbox w-4 h-4 rounded border-zinc-700 bg-zinc-900 text-emerald-500 focus:ring-0 hidden" data-action="test_suite">
          </div>
          <p class="text-xs text-zinc-400 leading-relaxed">
            Ejecución verificada de suite completa pytest con reporte de contratos, fixtures y esquemas SQLite WAL.
          </p>
          <div class="pt-3 border-t bd flex items-center justify-between text-xs">
            <span class="mono text-xs text-emerald-400 font-semibold">100% Pass</span>
            <button onclick="executeAction('test_suite', {}, this, event)" class="btn btn-secondary text-xs px-4 py-1.5">Ejecutar</button>
          </div>
        </div>

        <!-- Action Card 2: Security & Contract Audit -->
        <div class="section-canvas p-5 space-y-3.5" id="act-security-audit" onclick="handleCardSelectClick('security_audit', this, event)">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl bg-blue-500/10 border border-blue-500/25 flex items-center justify-center text-blue-400 shrink-0">
                <i data-lucide="shield-check" class="w-5 h-5"></i>
              </div>
              <div>
                <h4 class="text-sm font-bold text-white uppercase tracking-tight">Auditoría Hard Deny</h4>
                <div class="text-xs mono text-zinc-400">DR-INV-001, DR-PAY-001</div>
              </div>
            </div>
            <input type="checkbox" class="action-checkbox w-4 h-4 rounded border-zinc-700 bg-zinc-900 text-emerald-500 focus:ring-0 hidden" data-action="security_audit">
          </div>
          <p class="text-xs text-zinc-400 leading-relaxed">
            Verificación estricta de contratos inmutables contra sobreventa de stock, doble cargo y escaneo de secretos en git.
          </p>
          <div class="pt-3 border-t bd flex items-center justify-between text-xs">
            <span class="mono text-xs text-emerald-400 font-semibold">Cero Bypass</span>
            <button onclick="executeAction('security_audit', {}, this, event)" class="btn btn-secondary text-xs px-4 py-1.5">Auditar</button>
          </div>
        </div>

        <!-- Action Card 3: Cold-Start Crash Reconcile -->
        <div class="section-canvas p-5 space-y-3.5" id="act-reconcile-runs" onclick="handleCardSelectClick('reconcile_runs', this, event)">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/25 flex items-center justify-center text-emerald-400 shrink-0">
                <i data-lucide="refresh-cw" class="w-5 h-5"></i>
              </div>
              <div>
                <h4 class="text-sm font-bold text-white uppercase tracking-tight">Reconciliación Cold-Start</h4>
                <div class="text-xs mono text-zinc-400">StartupReconciliationEngine</div>
              </div>
            </div>
            <input type="checkbox" class="action-checkbox w-4 h-4 rounded border-zinc-700 bg-zinc-900 text-emerald-500 focus:ring-0 hidden" data-action="reconcile_runs">
          </div>
          <p class="text-xs text-zinc-400 leading-relaxed">
            Reclama leases huérfanos, actualiza runs interrumpidos a sus estados históricos y restaura estado CLEAN_STEADY en SQLite WAL.
          </p>
          <div class="pt-3 border-t bd flex items-center justify-between text-xs">
            <span class="mono text-xs text-emerald-400 font-semibold">Crash-Safe</span>
            <button onclick="executeAction('reconcile_runs', {}, this, event)" class="btn btn-secondary text-xs px-4 py-1.5">Reconciliar</button>
          </div>
        </div>

        <!-- Action Card 4: Staging Deploy Pipeline -->
        <div class="section-canvas p-5 space-y-3.5" id="act-release-pipeline" onclick="handleCardSelectClick('release_pipeline', this, event)">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/25 flex items-center justify-center text-amber-400 shrink-0">
                <i data-lucide="train" class="w-5 h-5"></i>
              </div>
              <div>
                <h4 class="text-sm font-bold text-white uppercase tracking-tight">Pipeline Staging Railway</h4>
                <div class="text-xs mono text-zinc-400">services/web-storefront</div>
              </div>
            </div>
            <input type="checkbox" class="action-checkbox w-4 h-4 rounded border-zinc-700 bg-zinc-900 text-emerald-500 focus:ring-0 hidden" data-action="release_pipeline">
          </div>
          <p class="text-xs text-zinc-400 leading-relaxed">
            Aprovisionamiento de entorno efímero en Railway y verificación de credenciales previas a compuerta de merge a producción.
          </p>
          <div class="pt-3 border-t bd flex items-center justify-between text-xs">
            <span class="mono text-xs text-amber-400 font-semibold">Compuerta Activa</span>
            <button onclick="executeAction('release_pipeline', {}, this, event)" class="btn btn-secondary text-xs px-4 py-1.5">Lanzar</button>
          </div>
        </div>

        <!-- Action Card 5: Software Architecture Design -->
        <div class="section-canvas p-5 space-y-3.5" id="act-software-design" onclick="handleCardSelectClick('software_design', this, event)">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl bg-teal-500/10 border border-teal-500/25 flex items-center justify-center text-teal-400 shrink-0">
                <i data-lucide="pen-tool" class="w-5 h-5"></i>
              </div>
              <div>
                <h4 class="text-sm font-bold text-white uppercase tracking-tight">Diseño de Arquitectura</h4>
                <div class="text-xs mono text-zinc-400">OpenAPI, RPC & Esquemas</div>
              </div>
            </div>
            <input type="checkbox" class="action-checkbox w-4 h-4 rounded border-zinc-700 bg-zinc-900 text-emerald-500 focus:ring-0 hidden" data-action="software_design">
          </div>
          <p class="text-xs text-zinc-400 leading-relaxed">
            Extracción y validación de interfaces frozen, esquemas SQLite WAL y especificación arquitectónica integral de servicios.
          </p>
          <div class="pt-3 border-t bd flex items-center justify-between text-xs">
            <span class="mono text-xs text-zinc-400">Validado</span>
            <button onclick="executeAction('software_design', {}, this, event)" class="btn btn-secondary text-xs px-4 py-1.5">Generar</button>
          </div>
        </div>

        <!-- Action Card 6: Campaign Sprint Launcher -->
        <div class="section-canvas p-5 space-y-3.5" id="act-campaign-sprint" onclick="handleCardSelectClick('campaign_sprint', this, event)">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl bg-rose-500/10 border border-rose-500/25 flex items-center justify-center text-rose-400 shrink-0">
                <i data-lucide="play" class="w-5 h-5"></i>
              </div>
              <div>
                <h4 class="text-sm font-bold text-white uppercase tracking-tight">Sprint Soberano SACL V1</h4>
                <div class="text-xs mono text-zinc-400">DAG Topológico Aislado</div>
              </div>
            </div>
            <input type="checkbox" class="action-checkbox w-4 h-4 rounded border-zinc-700 bg-zinc-900 text-emerald-500 focus:ring-0 hidden" data-action="campaign_sprint">
          </div>
          <p class="text-xs text-zinc-400 leading-relaxed">
            Genera worktree aislado con branch temporal, construye grafo de 6 etapas DAG e inicia despacho de agentes con lock supervisor.
          </p>
          <div class="pt-3 border-t bd flex items-center justify-between text-xs">
            <span class="mono text-xs text-rose-400 font-semibold">Orquestador</span>
            <button onclick="executeAction('campaign_sprint', {}, this, event)" class="btn btn-primary text-xs px-4 py-1.5">Inicializar</button>
          </div>
        </div>

      </div>

      <!-- Execution History Feed -->
      <div class="section-canvas p-6 space-y-4">
        <div class="flex items-center justify-between border-b bd pb-3">
          <h3 class="text-sm font-bold uppercase tracking-wider text-white">Historial de Ejecución de Pipelines</h3>
          <button onclick="loadActionHistory()" class="text-xs text-zinc-400 hover:text-white flex items-center gap-1 cursor-pointer">
            <i data-lucide="rotate-ccw" class="w-3.5 h-3.5"></i><span>Actualizar</span>
          </button>
        </div>
        <div id="action-history-container" class="space-y-2.5 text-xs"></div>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- SECTION 4: REPOSITORIOS & DOCS LOCALES -->
    <!-- ========================================== -->
    <div id="sec-projects" class="p-4 md:p-8 max-w-7xl mx-auto space-y-6 hidden">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b bd pb-4">
        <div>
          <h2 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <i data-lucide="folder-git-2" class="w-6 h-6 text-emerald-400"></i>
            <span>Espacios de Trabajo & Repositorios Locales</span>
          </h2>
          <p class="text-sm text-zinc-400 mt-1">Explora repositorios en disco, haz clic en cualquier documentación para inspeccionarla en vivo.</p>
        </div>

        <div class="flex items-center gap-2.5 w-full sm:w-auto">
          <button onclick="toggleMultiSelectMode()" id="btn-toggle-multiselect" class="btn btn-secondary text-xs px-3.5 py-2 shrink-0">
            <i data-lucide="check-square" class="w-3.5 h-3.5"></i>
            <span>Selección Lote</span>
          </button>
          <div class="relative flex-1 sm:w-72">
            <input type="text" id="project-search-input" oninput="filterProjectsList()" placeholder="Filtrar proyectos o docs..."
              class="w-full bg-black/50 border bd rounded-lg px-3.5 py-2 pl-9 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-white/30">
            <i data-lucide="search" class="w-4 h-4 text-zinc-500 absolute left-3 top-2.5"></i>
          </div>
        </div>
      </div>

      <!-- Scanned Projects Container -->
      <div id="projects-scanned-container" class="grid grid-cols-1 md:grid-cols-2 gap-6"></div>

      <!-- Active Project Automation Scripts -->
      <div class="section-canvas p-6 space-y-4">
        <h3 class="text-sm font-bold uppercase tracking-wider text-white flex items-center gap-2">
          <i data-lucide="cpu" class="w-4 h-4 text-purple-400"></i>
          <span>Scripts de Automatización Detectados en el Espacio Activo</span>
        </h3>
        <div id="active-project-automations-list" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 text-xs"></div>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- SECTION 5: CONSOLA REPL & INTERACTIVO -->
    <!-- ========================================== -->
    <div id="sec-chat" class="flex flex-col h-[calc(100vh-8.5rem)] md:h-[calc(100vh-5rem)] max-w-5xl mx-auto w-full px-3 md:px-6 pb-2 hidden">
      <!-- REPL Header Bar -->
      <div class="flex items-center justify-between py-2.5 border-b bd shrink-0 mb-3">
        <div class="flex items-center gap-2.5">
          <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <span class="text-xs font-bold text-white mono">sacl [Stable-Ecommerce-Orchestrator]:~$</span>
          <span class="text-[10px] mono px-2 py-0.5 rounded-full bg-white/10 text-zinc-300 font-semibold">INTERACTIVE_REPL</span>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="openTerminalDrawer()" class="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1.5 transition-colors px-2.5 py-1 rounded-lg bg-white/5 cursor-pointer">
            <i data-lucide="terminal" class="w-3.5 h-3.5"></i>
            <span class="text-[11px] mono">Terminal Logs</span>
          </button>
          <button onclick="clearChatHistory()" class="text-xs text-zinc-400 hover:text-white flex items-center gap-1 transition-colors px-2.5 py-1 rounded-lg hover:bg-white/5 cursor-pointer">
            <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
            <span class="text-[11px]">Clear</span>
          </button>
        </div>
      </div>

      <!-- REPL Output Stream Area -->
      <div id="chat-messages-scroll" class="flex-1 overflow-y-auto space-y-3 pr-1 min-h-0 custom-scroll">
        <!-- Clean CLI Welcome banner -->
        <div id="chat-welcome-hero" class="section-canvas p-6 space-y-3 text-left">
          <div class="flex items-center justify-between">
            <div class="text-xs font-bold mono text-emerald-400 flex items-center gap-2">
              <i data-lucide="terminal" class="w-4 h-4"></i>
              <span>SACL Sovereign Orchestrator · Interactive Executive Shell</span>
            </div>
            <span class="mono text-[10px] text-zinc-500 font-semibold">AUTOR: LUCILFER / risejoaquin</span>
          </div>
          <p class="text-xs text-zinc-300 font-mono leading-relaxed">
            Consola de comandos directa del orquestador. Ejecuta pipelines de SDLC, audita contratos DR-INV-001 o reconcilia crashes con código de salida y telemetría en tiempo real.
          </p>
          <div class="text-xs mono text-zinc-400 pt-2 border-t bd flex flex-wrap gap-2">
            <span class="text-zinc-500">Comandos disponibles:</span>
            <code class="text-emerald-400 font-semibold">reconcile</code>
            <code class="text-purple-400 font-semibold">test</code>
            <code class="text-blue-400 font-semibold">audit</code>
            <code class="text-teal-400 font-semibold">design</code>
            <code class="text-amber-400 font-semibold">release</code>
            <code class="text-emerald-400 font-semibold">approve</code>
          </div>
        </div>

        <div id="chat-messages-container" class="space-y-3"></div>

        <div id="chat-typing-indicator" class="hidden flex items-center gap-2 p-3 rounded-xl bg-black/50 border bd text-zinc-400 w-fit text-xs mono">
          <i data-lucide="loader-2" class="w-4 h-4 animate-spin text-emerald-400"></i>
          <span class="text-xs">Ejecutando pipeline en subproceso...</span>
        </div>
      </div>

      <!-- Docked Command Bar -->
      <div class="shrink-0 pt-3 space-y-2.5">
        <!-- Command Presets Strip -->
        <div class="flex items-center gap-2 overflow-x-auto no-scrollbar py-1">
          <button onclick="sendQuickPrompt('reconcile')" class="btn btn-secondary text-xs px-3 py-1.5 whitespace-nowrap shrink-0 mono">
            <i data-lucide="refresh-cw" class="w-3.5 h-3.5 text-emerald-400"></i><span>reconcile_runs</span>
          </button>
          <button onclick="sendQuickPrompt('test')" class="btn btn-secondary text-xs px-3 py-1.5 whitespace-nowrap shrink-0 mono">
            <i data-lucide="check-square" class="w-3.5 h-3.5 text-purple-400"></i><span>test_suite</span>
          </button>
          <button onclick="sendQuickPrompt('audit')" class="btn btn-secondary text-xs px-3 py-1.5 whitespace-nowrap shrink-0 mono">
            <i data-lucide="shield" class="w-3.5 h-3.5 text-blue-400"></i><span>security_audit</span>
          </button>
          <button onclick="sendQuickPrompt('sprint')" class="btn btn-secondary text-xs px-3 py-1.5 whitespace-nowrap shrink-0 mono">
            <i data-lucide="play" class="w-3.5 h-3.5 text-emerald-400"></i><span>campaign_sprint</span>
          </button>
          <button onclick="sendQuickPrompt('design')" class="btn btn-secondary text-xs px-3 py-1.5 whitespace-nowrap shrink-0 mono">
            <i data-lucide="pen-tool" class="w-3.5 h-3.5 text-teal-400"></i><span>software_design</span>
          </button>
          <button onclick="sendQuickPrompt('release')" class="btn btn-secondary text-xs px-3 py-1.5 whitespace-nowrap shrink-0 mono">
            <i data-lucide="train" class="w-3.5 h-3.5 text-amber-400"></i><span>release_staging</span>
          </button>
        </div>

        <!-- Terminal Input Bar -->
        <form id="chat-form" onsubmit="event.preventDefault(); sendChatMessage();" class="flex items-center gap-2 bg-[#14151c] border bd rounded-xl p-2 focus-within:border-emerald-500/50 transition-all shadow-xl">
          <span class="mono text-emerald-400 pl-2 text-xs font-bold shrink-0">sacl&gt;</span>
          <input type="text" id="chat-input" placeholder="Escribe un comando o selecciona una acción rápida..."
            class="flex-1 bg-transparent px-2 py-1 text-xs mono text-white placeholder-zinc-500 focus:outline-none"
            onkeydown="handleChatKeyDown(event)">
          <button id="chat-send-btn" type="submit" class="btn btn-primary text-xs px-4 py-2 shrink-0 mono">
            <span>Ejecutar ↵</span>
          </button>
        </form>
      </div>
    </div>

  </main>

  <!-- ========================================== -->
  <!-- FLOATING MULTI-ACTION EXECUTION BAR -->
  <!-- ========================================== -->
  <div id="floating-multiaction-bar" class="fixed bottom-20 md:bottom-8 left-1/2 -translate-x-1/2 z-40 bg-[#161822] border border-emerald-500/50 rounded-2xl px-5 py-3 shadow-2xl flex items-center gap-5 hidden">
    <div class="flex items-center gap-2">
      <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
      <span id="multiaction-count-text" class="text-xs font-bold text-white mono">0 seleccionados</span>
    </div>
    <div class="flex items-center gap-2">
      <button onclick="cancelMultiSelect()" class="btn btn-secondary text-xs px-3 py-1.5">Cancelar</button>
      <button onclick="executeMultiSelectedBatch()" id="btn-batch-exec" class="btn btn-success text-xs px-4 py-1.5">
        <i data-lucide="play" class="w-3.5 h-3.5 fill-black"></i>
        <span>Ejecutar Lote</span>
      </button>
    </div>
  </div>

  <!-- ========================================== -->
  <!-- MOBILE BOTTOM TAB NAVIGATION -->
  <!-- ========================================== -->
  <nav class="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-[#0b0c10]/95 border-t bd backdrop-blur-md z-30 flex items-center justify-around px-2">
    <button id="mtab-dashboard" class="mobile-tab active" onclick="switchSection('dashboard')">
      <i data-lucide="layout-grid" class="w-4 h-4"></i>
      <span>HUD</span>
    </button>
    <button id="mtab-gates" class="mobile-tab" onclick="switchSection('gates')">
      <i data-lucide="shield-alert" class="w-4 h-4"></i>
      <span>Compuertas</span>
    </button>
    <button id="mtab-sdlc" class="mobile-tab" onclick="switchSection('sdlc')">
      <i data-lucide="play-circle" class="w-4 h-4"></i>
      <span>Pipelines</span>
    </button>
    <button id="mtab-projects" class="mobile-tab" onclick="switchSection('projects')">
      <i data-lucide="folder-git-2" class="w-4 h-4"></i>
      <span>Repos</span>
    </button>
    <button id="mtab-chat" class="mobile-tab" onclick="switchSection('chat')">
      <i data-lucide="terminal" class="w-4 h-4"></i>
      <span>REPL</span>
    </button>
  </nav>

  <!-- ========================================== -->
  <!-- MODAL: DOCUMENTATION VIEWER -->
  <!-- ========================================== -->
  <div id="doc-modal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-3 md:p-6 hidden">
    <div class="section-canvas w-full max-w-4xl max-h-[85vh] flex flex-col overflow-hidden bg-[#0e0f14] border-zinc-700 shadow-2xl">
      <div class="p-4 border-b bd flex items-center justify-between shrink-0">
        <div class="flex items-center gap-2.5">
          <i data-lucide="file-text" class="w-4 h-4 text-emerald-400"></i>
          <h3 class="text-sm font-bold text-white mono" id="doc-modal-title">Documento</h3>
        </div>
        <button onclick="closeDocModal()" class="p-1.5 text-zinc-400 hover:text-white rounded-lg hover:bg-white/10 cursor-pointer">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
      </div>
      <div class="p-5 overflow-y-auto flex-1 custom-scroll">
        <pre class="font-mono text-xs text-zinc-200 whitespace-pre-wrap leading-relaxed select-text" id="doc-modal-content"></pre>
      </div>
      <div class="p-3 border-t bd flex items-center justify-between shrink-0 bg-white/5 text-xs text-zinc-400">
        <span id="doc-modal-path" class="mono text-[11px] truncate max-w-md"></span>
        <button onclick="closeDocModal()" class="btn btn-secondary text-xs px-4 py-1.5">Cerrar</button>
      </div>
    </div>
  </div>

  <!-- ========================================== -->
  <!-- MODAL: DIFF & IMPACT INSPECTOR -->
  <!-- ========================================== -->
  <div id="diff-modal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-3 md:p-6 hidden">
    <div class="section-canvas w-full max-w-3xl max-h-[85vh] flex flex-col overflow-hidden bg-[#0e0f14] border-zinc-700 shadow-2xl">
      <div class="p-4 border-b bd flex items-center justify-between shrink-0">
        <div class="flex items-center gap-2.5">
          <i data-lucide="file-diff" class="w-4 h-4 text-emerald-400"></i>
          <h3 class="text-sm font-bold text-white mono" id="diff-modal-title">Diff Inspector · REQ-20261025-406DBE23</h3>
        </div>
        <button onclick="closeDiffModal()" class="p-1.5 text-zinc-400 hover:text-white rounded-lg hover:bg-white/10 cursor-pointer">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
      </div>
      <div class="p-5 overflow-y-auto flex-1 space-y-3 custom-scroll">
        <div class="text-xs text-zinc-300 leading-relaxed" id="diff-modal-summary">
          Resumen de impacto generado automáticamente bajo Hard Deny Supremacy.
        </div>
        <div class="p-4 rounded-xl bg-black/60 border bd font-mono text-xs overflow-x-auto text-zinc-300 space-y-1" id="diff-modal-body"></div>
      </div>
      <div class="p-3 border-t bd flex items-center justify-end gap-2 shrink-0 bg-white/5">
        <button onclick="closeDiffModal()" class="btn btn-secondary text-xs px-4 py-1.5">Cerrar</button>
        <button onclick="quickApproveFromCard(); closeDiffModal();" class="btn btn-success text-xs px-5 py-1.5">Autorizar Despliegue</button>
      </div>
    </div>
  </div>

  <!-- ========================================== -->
  <!-- DRAWER: TERMINAL LOGS OVERLAY -->
  <!-- ========================================== -->
  <div id="terminal-drawer" class="fixed inset-y-0 right-0 w-full sm:w-[600px] bg-[#0c0d12] border-l bd z-50 transform translate-x-full transition-transform duration-200 ease-out flex flex-col shadow-2xl">
    <div class="h-14 border-b bd flex items-center justify-between px-5 bg-black/50 shrink-0">
      <div class="flex items-center gap-2">
        <i data-lucide="terminal" class="w-4 h-4 text-emerald-400"></i>
        <span class="text-xs font-bold text-white mono">Terminal Monospace · Salida de Proceso</span>
      </div>
      <div class="flex items-center gap-2">
        <button onclick="clearTerminalLogs()" class="text-xs text-zinc-400 hover:text-white px-2.5 py-1 rounded hover:bg-white/5 cursor-pointer">Limpiar</button>
        <button onclick="copyTerminalLogs()" class="text-xs text-zinc-400 hover:text-white px-2.5 py-1 rounded hover:bg-white/5 cursor-pointer">Copiar</button>
        <button onclick="closeTerminalDrawer()" class="p-1.5 text-zinc-400 hover:text-white rounded hover:bg-white/5 cursor-pointer">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
      </div>
    </div>
    <div id="terminal-stdout-container" class="flex-1 p-4 font-mono text-xs text-zinc-300 overflow-y-auto space-y-1.5 select-text custom-scroll bg-[#08080a]">
      <div class="text-zinc-500">[INIT] Consola de ejecución soberana lista. Aguardando procesos...</div>
    </div>
  </div>

  <!-- ========================================== -->
  <!-- DRAWER: SETTINGS & TOOLCHAIN OVERVIEW -->
  <!-- ========================================== -->
  <div id="settings-drawer" class="fixed inset-y-0 right-0 w-full sm:w-[420px] bg-[#0e0f14] border-l bd z-50 transform translate-x-full transition-transform duration-200 ease-out flex flex-col shadow-2xl">
    <div class="h-16 border-b bd flex items-center justify-between px-5 bg-black/40 shrink-0">
      <div class="flex items-center gap-2">
        <i data-lucide="sliders" class="w-4 h-4 text-emerald-400"></i>
        <span class="text-sm font-bold text-white">Configuración del Sistema</span>
      </div>
      <button onclick="closeSettingsDrawer()" class="p-1.5 text-zinc-400 hover:text-white rounded-lg hover:bg-white/5 cursor-pointer">
        <i data-lucide="x" class="w-4 h-4"></i>
      </button>
    </div>
    <div class="flex-1 overflow-y-auto p-5 space-y-5 custom-scroll">
      <!-- Author Attribution Card -->
      <div class="section-canvas p-5 space-y-2.5">
        <div class="text-[10px] uppercase font-bold tracking-wider text-zinc-400">Autoría & Soberanía</div>
        <div class="text-base font-bold text-white">LUCILFER / risejoaquin</div>
        <div class="text-xs text-zinc-400">Cuenta GitHub activa: <span class="mono text-emerald-400 font-semibold">@risejoaquin</span></div>
        <div class="text-xs text-zinc-400">Email Resend: <span class="mono text-zinc-300">lucilfer@selfcaresinners.com</span></div>
      </div>

      <!-- System Diagnostics -->
      <div class="space-y-2.5">
        <div class="text-xs font-bold uppercase tracking-wider text-zinc-400">Estado de Runtime</div>
        <div class="p-4 rounded-xl bg-black/40 border bd space-y-2 text-xs font-mono">
          <div class="flex justify-between"><span class="text-zinc-500">Python:</span><span class="text-zinc-300">3.11.9 (win32)</span></div>
          <div class="flex justify-between"><span class="text-zinc-500">Node.js:</span><span class="text-zinc-300">v24.14.0</span></div>
          <div class="flex justify-between"><span class="text-zinc-500">Base SQLite:</span><span class="text-emerald-400">sacl_ops.db (WAL)</span></div>
          <div class="flex justify-between"><span class="text-zinc-500">Crash State:</span><span id="drawer-crash-state" class="text-emerald-400 font-bold">CLEAN_STEADY</span></div>
        </div>
      </div>

      <!-- Action triggers -->
      <div class="space-y-2.5">
        <div class="text-xs font-bold uppercase tracking-wider text-zinc-400">Operaciones Rápidas</div>
        <button onclick="executeAction('reconcile_runs', {}, this)" class="btn btn-secondary w-full text-xs py-2.5 justify-start">
          <i data-lucide="refresh-cw" class="w-3.5 h-3.5 text-emerald-400"></i>
          <span>Reconciliar Procesos Viejos</span>
        </button>
        <button onclick="executeAction('security_audit', {}, this)" class="btn btn-secondary w-full text-xs py-2.5 justify-start">
          <i data-lucide="shield-check" class="w-3.5 h-3.5 text-blue-400"></i>
          <span>Auditar Invariantes DR-INV-001</span>
        </button>
      </div>
    </div>
  </div>

  <!-- TOAST NOTIFICATION CONTAINER -->
  <div id="toast-container" class="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none"></div>

  <!-- JAVASCRIPT APPLICATION CORE -->
  <script>
    const API_BASE = window.location.origin;
    let currentSection = 'dashboard';
    let isMultiSelectActive = false;
    let selectedActions = new Set();
    let allProjects = [];
    let currentGateRequestId = 'REQ-20261025-406DBE23';
    let currentGateApprovalId = 'appr-55ce1c775584';

    document.addEventListener('DOMContentLoaded', () => {
      lucide.createIcons();
      loadDashboardSnapshot();
      loadProjects();
      loadChatHistory();
      loadActionHistory();
      initSSE();
    });

    // ==========================================
    // NAVIGATION SWITCHER
    // ==========================================
    function switchSection(secId) {
      currentSection = secId;
      ['dashboard', 'gates', 'sdlc', 'projects', 'chat'].forEach(id => {
        const el = document.getElementById('sec-' + id);
        const dtab = document.getElementById('dtab-' + id);
        const mtab = document.getElementById('mtab-' + id);
        if (el) {
          if (id === secId) {
            el.classList.remove('hidden');
          } else {
            el.classList.add('hidden');
          }
        }
        if (dtab) {
          if (id === secId) dtab.classList.add('active');
          else dtab.classList.remove('active');
        }
        if (mtab) {
          if (id === secId) mtab.classList.add('active');
          else mtab.classList.remove('active');
        }
      });
      if (secId === 'chat') {
        scrollChatToBottom();
      }
      lucide.createIcons();
    }
    window.switchSection = switchSection;

    // ==========================================
    // TOAST NOTIFIER
    // ==========================================
    function showToast(msg, type = 'info') {
      const container = document.getElementById('toast-container');
      if (!container) return;
      const toast = document.createElement('div');
      const borderCol = type === 'success' ? 'border-emerald-500/40 text-emerald-300' :
                        type === 'error' ? 'border-red-500/40 text-red-300' : 'border-zinc-700 text-zinc-200';
      toast.className = `p-3.5 rounded-xl bg-[#14151c] border ${borderCol} shadow-2xl text-xs font-medium flex items-center gap-2 pointer-events-auto toast-animate`;
      toast.innerHTML = `<i data-lucide="${type === 'success' ? 'check-circle' : type === 'error' ? 'alert-triangle' : 'info'}" class="w-4 h-4 shrink-0"></i><span>${msg}</span>`;
      container.appendChild(toast);
      lucide.createIcons();
      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.2s ease';
        setTimeout(() => toast.remove(), 200);
      }, 3500);
    }
    window.showToast = showToast;

    // ==========================================
    // DASHBOARD SNAPSHOT LOADER
    // ==========================================
    async function loadDashboardSnapshot() {
      try {
        const res = await fetch(`${API_BASE}/api/snapshot`);
        const data = await res.json();
        
        // Update Recovery Metric
        if (data.recovery) {
          const rec = data.recovery;
          const countEl = document.getElementById('metric-interrupted-runs');
          const badgeEl = document.getElementById('metric-recovery-badge');
          const drawerCrashEl = document.getElementById('drawer-crash-state');
          if (countEl) countEl.innerText = `${rec.interrupted_runs_count || 0} Interrumpidos`;
          if (badgeEl) {
            badgeEl.innerText = rec.classification || 'CLEAN_STEADY';
            if (rec.classification === 'RECOVERY_NEEDED') {
              badgeEl.className = 'mono text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/25';
            } else {
              badgeEl.className = 'mono text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/25';
            }
          }
          if (drawerCrashEl) drawerCrashEl.innerText = rec.classification || 'CLEAN_STEADY';
        }

        // Update Pending Gate
        if (data.pending_gates && data.pending_gates.length > 0) {
          const g = data.pending_gates[0];
          currentGateRequestId = g.request_id;
          currentGateApprovalId = g.approval_id;
          const pill = document.getElementById('gate-request-id-pill');
          const title = document.getElementById('gate-action-title');
          const tuercaBadge = document.getElementById('tuerca-gate-badge');
          const navCount = document.getElementById('nav-gates-count');
          if (pill) pill.innerText = g.request_id;
          if (title) title.innerText = g.action;
          if (tuercaBadge) {
            tuercaBadge.innerText = data.pending_gates.length;
            tuercaBadge.classList.remove('hidden');
          }
          if (navCount) {
            navCount.innerText = data.pending_gates.length;
            navCount.classList.remove('hidden');
          }
        } else {
          const tuercaBadge = document.getElementById('tuerca-gate-badge');
          const navCount = document.getElementById('nav-gates-count');
          if (tuercaBadge) tuercaBadge.classList.add('hidden');
          if (navCount) navCount.classList.add('hidden');
        }

      } catch (e) {
        console.error('Error loading snapshot:', e);
      }
    }
    window.loadDashboardSnapshot = loadDashboardSnapshot;

    // ==========================================
    // ACTION EXECUTION ENGINE
    // ==========================================
    async function executeAction(actionType, params = {}, triggerBtn = null, event = null) {
      if (event) event.stopPropagation();
      let originalHtml = '';
      if (triggerBtn) {
        originalHtml = triggerBtn.innerHTML;
        triggerBtn.disabled = true;
        triggerBtn.innerHTML = '<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i><span>...</span>';
        lucide.createIcons();
      }

      appendTerminalLog(`[DISPATCH] Ejecutando acción: ${actionType}...`);
      showToast(`Iniciando ${actionType}...`, 'info');

      try {
        const res = await fetch(`${API_BASE}/api/actions/execute`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action_type: actionType, params })
        });
        const data = await res.json();
        if (data.success && data.execution) {
          const exec = data.execution;
          showToast(`${exec.title}: ${exec.status} (${exec.duration_sec}s)`, 'success');
          appendTerminalLog(`[COMPLETE] ${exec.title} terminado en ${exec.duration_sec}s con salida ${exec.exit_code}`);
          (exec.logs || []).forEach(l => appendTerminalLog(l));
          loadActionHistory();
          loadDashboardSnapshot();
          return exec;
        } else {
          showToast(`Error al ejecutar ${actionType}`, 'error');
          appendTerminalLog(`[ERROR] ${data.error || 'Fallo desconocido'}`);
        }
      } catch (err) {
        console.error(err);
        showToast(`Fallo de red: ${err.message}`, 'error');
        appendTerminalLog(`[EXCEPTION] ${err.message}`);
      } finally {
        if (triggerBtn) {
          triggerBtn.disabled = false;
          triggerBtn.innerHTML = originalHtml;
          lucide.createIcons();
        }
      }
    }
    window.executeAction = executeAction;

    async function loadActionHistory() {
      try {
        const res = await fetch(`${API_BASE}/api/actions/history`);
        const data = await res.json();
        const container = document.getElementById('action-history-container');
        if (!container || !data.history) return;

        if (data.history.length === 0) {
          container.innerHTML = '<div class="text-zinc-500 text-xs py-2">No hay ejecuciones recientes registradas.</div>';
          return;
        }

        container.innerHTML = data.history.slice(0, 5).map(h => `
          <div class="p-3 rounded-xl bg-black/40 border bd flex items-center justify-between">
            <div class="flex items-center gap-3">
              <span class="w-2.5 h-2.5 rounded-full ${h.status === 'COMPLETED' ? 'bg-emerald-400' : 'bg-red-400'}"></span>
              <div>
                <div class="font-bold text-white mono text-xs">${h.title}</div>
                <div class="text-[11px] text-zinc-500 mono">${h.execution_id} · ${h.duration_sec}s · Exit ${h.exit_code}</div>
              </div>
            </div>
            <button onclick="viewActionLogsInTerminal('${h.execution_id}')" class="btn btn-secondary text-xs px-2.5 py-1">Logs</button>
          </div>
        `).join('');
        lucide.createIcons();
      } catch (e) {
        console.error(e);
      }
    }
    window.loadActionHistory = loadActionHistory;

    // ==========================================
    // MULTI-ACTION BATCH SELECTION
    // ==========================================
    function toggleMultiSelectMode() {
      isMultiSelectActive = !isMultiSelectActive;
      const btn = document.getElementById('btn-toggle-multiselect');
      const checkboxes = document.querySelectorAll('.action-checkbox');
      if (isMultiSelectActive) {
        btn.classList.add('bg-emerald-500/10', 'text-emerald-400', 'border-emerald-500/30');
        checkboxes.forEach(cb => cb.classList.remove('hidden'));
        showToast('Modo de selección múltiple activado', 'info');
      } else {
        btn.classList.remove('bg-emerald-500/10', 'text-emerald-400', 'border-emerald-500/30');
        checkboxes.forEach(cb => cb.classList.add('hidden'));
        cancelMultiSelect();
      }
    }
    window.toggleMultiSelectMode = toggleMultiSelectMode;

    function handleCardSelectClick(actionKey, cardEl, event) {
      if (!isMultiSelectActive) return;
      if (selectedActions.has(actionKey)) {
        selectedActions.delete(actionKey);
        cardEl.classList.remove('selected');
      } else {
        selectedActions.add(actionKey);
        cardEl.classList.add('selected');
      }
      updateMultiActionBar();
    }
    window.handleCardSelectClick = handleCardSelectClick;

    function updateMultiActionBar() {
      const bar = document.getElementById('floating-multiaction-bar');
      const text = document.getElementById('multiaction-count-text');
      if (selectedActions.size > 0) {
        bar.classList.remove('hidden');
        text.innerText = `${selectedActions.size} seleccionado(s)`;
      } else {
        bar.classList.add('hidden');
      }
    }

    function cancelMultiSelect() {
      selectedActions.clear();
      document.querySelectorAll('.section-canvas, .item-card').forEach(c => c.classList.remove('selected'));
      updateMultiActionBar();
    }
    window.cancelMultiSelect = cancelMultiSelect;

    async function executeMultiSelectedBatch() {
      const list = Array.from(selectedActions);
      if (list.length === 0) return;
      const btn = document.getElementById('btn-batch-exec');
      btn.disabled = true;
      btn.innerHTML = `<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i><span>Ejecutando ${list.length}...</span>`;
      lucide.createIcons();

      for (const act of list) {
        await executeAction(act);
      }

      btn.disabled = false;
      btn.innerHTML = `<i data-lucide="play" class="w-3.5 h-3.5 fill-black"></i><span>Ejecutar Lote</span>`;
      cancelMultiSelect();
      if (isMultiSelectActive) toggleMultiSelectMode();
      showToast('Lote completado con éxito', 'success');
      lucide.createIcons();
    }
    window.executeMultiSelectedBatch = executeMultiSelectedBatch;

    // ==========================================
    // PROJECTS & DOCS MODULE
    // ==========================================
    async function loadProjects() {
      try {
        const res = await fetch(`${API_BASE}/api/projects`);
        const data = await res.json();
        allProjects = data.projects || [];
        renderProjectsList(allProjects);

        const active = data.active || allProjects[0];
        if (active) {
          document.getElementById('header-active-project-name').innerText = active.name;
          renderActiveProjectAutomations(active);
        }
      } catch (e) {
        console.error(e);
      }
    }
    window.loadProjects = loadProjects;

    function renderProjectsList(projects) {
      const container = document.getElementById('projects-scanned-container');
      if (!container) return;

      container.innerHTML = projects.map(p => `
        <div class="section-canvas p-6 space-y-4 ${p.is_active ? 'border-emerald-500/50 bg-[#121618]' : ''}" id="card-proj-${p.id}" onclick="handleCardSelectClick('${p.id}', this, event)">
          <div class="flex items-start justify-between gap-3 border-b bd pb-3">
            <div>
              <div class="flex items-center gap-2">
                <h3 class="text-base font-bold text-white mono">${p.name}</h3>
                ${p.is_active ? '<span class="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/25 text-[10px] mono font-bold">ACTIVO</span>' : ''}
              </div>
              <div class="text-xs mono text-zinc-400 mt-1 truncate max-w-sm">${p.path}</div>
            </div>
            <button onclick="switchActiveProject('${p.id}')" class="btn ${p.is_active ? 'btn-secondary opacity-60 cursor-default' : 'btn-primary'} text-xs px-3.5 py-1.5 shrink-0">
              ${p.is_active ? 'En Uso' : 'Seleccionar'}
            </button>
          </div>

          <!-- Documentation Badges with click-to-preview -->
          <div>
            <div class="text-[10px] uppercase font-bold tracking-wider text-zinc-400 mb-2">Documentación Detectada (Clic para ver)</div>
            <div class="flex flex-wrap gap-2">
              ${(p.documentation || []).map(d => `
                <button onclick="viewDocPreview('${encodeURIComponent(d.path)}', '${d.name}', event)"
                  class="mono text-xs px-2.5 py-1 rounded-lg bg-black/40 border bd hover:border-emerald-500/40 text-zinc-300 flex items-center gap-1.5 cursor-pointer transition-colors">
                  <i data-lucide="file-text" class="w-3.5 h-3.5 text-emerald-400"></i>
                  <span>${d.name}</span>
                </button>
              `).join('') || '<span class="text-xs text-zinc-500">Sin docs markdown detectados</span>'}
            </div>
          </div>
        </div>
      `).join('');
      lucide.createIcons();
    }

    async function viewDocPreview(encodedPath, docName, event) {
      if (event) event.stopPropagation();
      const rawPath = decodeURIComponent(encodedPath);
      try {
        const res = await fetch(`${API_BASE}/api/projects/doc?path=${encodeURIComponent(rawPath)}`);
        const data = await res.json();
        if (data.success) {
          document.getElementById('doc-modal-title').innerText = docName;
          document.getElementById('doc-modal-content').innerText = data.content;
          document.getElementById('doc-modal-path').innerText = rawPath;
          document.getElementById('doc-modal').classList.remove('hidden');
          lucide.createIcons();
        } else {
          showToast('No se pudo abrir el documento: ' + data.error, 'error');
        }
      } catch (e) {
        showToast('Error al leer doc: ' + e.message, 'error');
      }
    }
    window.viewDocPreview = viewDocPreview;

    function closeDocModal() {
      document.getElementById('doc-modal').classList.add('hidden');
    }
    window.closeDocModal = closeDocModal;

    function filterProjectsList() {
      const query = document.getElementById('project-search-input')?.value.toLowerCase() || '';
      const filtered = allProjects.filter(p => p.name.toLowerCase().includes(query) || p.path.toLowerCase().includes(query));
      renderProjectsList(filtered);
    }
    window.filterProjectsList = filterProjectsList;

    async function switchActiveProject(projId) {
      try {
        const res = await fetch(`${API_BASE}/api/projects/switch`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: projId })
        });
        const data = await res.json();
        if (data.success) {
          showToast(`Espacio de trabajo cambiado a ${data.active.name}`, 'success');
          loadProjects();
          loadDashboardSnapshot();
        }
      } catch (e) {
        console.error(e);
      }
    }
    window.switchActiveProject = switchActiveProject;

    function renderActiveProjectAutomations(proj) {
      const container = document.getElementById('active-project-automations-list');
      if (!container) return;
      const scripts = proj.detected_scripts || [];
      if (scripts.length === 0) {
        container.innerHTML = '<div class="col-span-full text-zinc-500 text-xs py-2">No se detectaron scripts ejecutables en este proyecto.</div>';
        return;
      }
      container.innerHTML = scripts.map(s => `
        <div class="p-3 rounded-xl bg-black/40 border bd flex items-center justify-between">
          <div class="flex items-center gap-2 truncate">
            <i data-lucide="file-code" class="w-4 h-4 text-purple-400 shrink-0"></i>
            <span class="mono text-zinc-200 truncate text-xs">${s}</span>
          </div>
          <button onclick="executeAction('local_script', { script: '${s}' }, this, event)" class="btn btn-secondary text-xs px-3 py-1 shrink-0">Ejecutar</button>
        </div>
      `).join('');
      lucide.createIcons();
    }

    // ==========================================
    // REPL & COMMAND CENTER
    // ==========================================
    let isChatSending = false;

    async function loadChatHistory() {
      try {
        const res = await fetch(`${API_BASE}/api/chat/history`);
        const data = await res.json();
        const container = document.getElementById('chat-messages-container');
        if (!container || !data.history) return;

        container.innerHTML = '';
        data.history.forEach(msg => {
          appendChatMessage(msg.role, msg.content, msg.action_data, false);
        });
        scrollChatToBottom();
      } catch (e) {
        console.error('Chat history error:', e);
      }
    }
    window.loadChatHistory = loadChatHistory;

    async function clearChatHistory() {
      try {
        const res = await fetch(`${API_BASE}/api/chat/clear`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
          const container = document.getElementById('chat-messages-container');
          if (container) container.innerHTML = '';
          showToast('Consola REPL limpiada', 'info');
          loadChatHistory();
        }
      } catch (e) {
        console.error('Clear chat error:', e);
      }
    }
    window.clearChatHistory = clearChatHistory;

    async function sendChatMessage() {
      if (isChatSending) return;
      const input = document.getElementById('chat-input');
      const sendBtn = document.getElementById('chat-send-btn');
      const typing = document.getElementById('chat-typing-indicator');
      const text = (input?.value || '').trim();
      if (!text) return;

      isChatSending = true;
      input.value = '';
      if (sendBtn) sendBtn.disabled = true;
      if (typing) typing.classList.remove('hidden');

      appendChatMessage('user', text, null, true);
      scrollChatToBottom();

      try {
        const res = await fetch(`${API_BASE}/api/chat/message`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: text, model_id: 'SACL_ORCHESTRATOR' })
        });
        const data = await res.json();
        if (data.success && data.assistant_message) {
          appendChatMessage('assistant', data.assistant_message.content, data.assistant_message.action_data, true);
          loadDashboardSnapshot();
          loadActionHistory();
        }
      } catch (err) {
        appendChatMessage('assistant', 'Error de ejecución en consola: ' + err.message, null, true);
      } finally {
        isChatSending = false;
        if (sendBtn) sendBtn.disabled = false;
        if (typing) typing.classList.add('hidden');
        scrollChatToBottom();
        lucide.createIcons();
      }
    }
    window.sendChatMessage = sendChatMessage;

    function handleChatKeyDown(event) {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendChatMessage();
      }
    }
    window.handleChatKeyDown = handleChatKeyDown;

    function sendQuickPrompt(promptText) {
      const input = document.getElementById('chat-input');
      if (input) {
        input.value = promptText;
        sendChatMessage();
      }
    }
    window.sendQuickPrompt = sendQuickPrompt;

    function appendChatMessage(role, content, actionData = null, animate = false) {
      const container = document.getElementById('chat-messages-container');
      if (!container) return;

      const msgDiv = document.createElement('div');
      msgDiv.className = `space-y-1.5 ${animate ? 'toast-animate' : ''}`;

      if (role === 'user') {
        msgDiv.innerHTML = `
          <div class="flex items-center gap-2 mono text-xs text-zinc-400">
            <span class="text-emerald-400 font-bold">sacl&gt;</span>
            <span class="text-white font-medium">${escapeHtml(content)}</span>
          </div>
        `;
      } else {
        let actionCardHtml = '';
        if (actionData) {
          const isSuccess = actionData.status === 'COMPLETED';
          actionCardHtml = `
            <div class="mt-2.5 p-4 rounded-xl bg-black/60 border bd space-y-2.5 mono text-xs">
              <div class="flex items-center justify-between border-b bd pb-2">
                <span class="font-bold text-white">${actionData.title || 'Ejecución'}</span>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold ${isSuccess ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/25' : 'bg-red-500/10 text-red-400 border border-red-500/25'}">
                  ${isSuccess ? 'EXIT 0' : 'FAILED'}
                </span>
              </div>
              <div class="space-y-1 text-zinc-300">
                ${(actionData.steps || []).map(s => `
                  <div class="flex items-center justify-between text-xs">
                    <span class="flex items-center gap-2">
                      <i data-lucide="${s.status === 'DONE' ? 'check' : 'circle'}" class="w-3.5 h-3.5 text-emerald-400"></i>
                      <span>${s.name}</span>
                    </span>
                    <span class="text-zinc-500">${s.duration || ''}</span>
                  </div>
                `).join('')}
              </div>
              <div class="pt-2 border-t bd flex items-center justify-between text-xs text-zinc-500">
                <span>Tiempo: ${actionData.duration_sec || 0}s</span>
                <button onclick="viewActionLogsInTerminal('${actionData.execution_id}')" class="text-emerald-400 hover:underline cursor-pointer">Ver en Terminal &rarr;</button>
              </div>
            </div>
          `;
        }

        msgDiv.innerHTML = `
          <div class="p-4 rounded-xl bg-[#14151c] border bd text-xs text-zinc-200 space-y-1.5">
            <div class="flex items-center gap-1.5 mono text-[10px] text-zinc-500 font-semibold">
              <i data-lucide="cpu" class="w-3.5 h-3.5 text-emerald-400"></i>
              <span>OUTPUT</span>
            </div>
            <div class="leading-relaxed whitespace-pre-wrap">${formatMarkdownContent(content)}</div>
            ${actionCardHtml}
          </div>
        `;
      }

      container.appendChild(msgDiv);
      lucide.createIcons();
    }

    function scrollChatToBottom() {
      const scroll = document.getElementById('chat-messages-scroll');
      if (scroll) scroll.scrollTop = scroll.scrollHeight;
    }

    // ==========================================
    // GATE DECISION HANDLERS
    // ==========================================
    async function quickApproveFromCard() {
      try {
        const res = await fetch(`${API_BASE}/api/gates/decide`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            approval_id: currentGateApprovalId,
            decision: 'APPROVED',
            justification: 'Autorizado vía panel de gobernanza SACL'
          })
        });
        const data = await res.json();
        if (data.success) {
          showToast(`Compuerta ${currentGateApprovalId} autorizada con éxito`, 'success');
          loadDashboardSnapshot();
        }
      } catch (e) {
        showToast('Error al autorizar compuerta: ' + e.message, 'error');
      }
    }
    window.quickApproveFromCard = quickApproveFromCard;

    async function quickRejectFromCard() {
      const reason = prompt('Motivo de rechazo de compuerta:') || 'Rechazado por operador humano';
      try {
        const res = await fetch(`${API_BASE}/api/gates/decide`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            approval_id: currentGateApprovalId,
            decision: 'REJECTED',
            justification: reason
          })
        });
        const data = await res.json();
        if (data.success) {
          showToast(`Compuerta rechazada`, 'error');
          loadDashboardSnapshot();
        }
      } catch (e) {
        showToast('Error al rechazar: ' + e.message, 'error');
      }
    }
    window.quickRejectFromCard = quickRejectFromCard;

    async function inspectCurrentGateImpact() {
      try {
        const res = await fetch(`${API_BASE}/api/gates/impact?request_id=${currentGateRequestId}`);
        const data = await res.json();
        document.getElementById('diff-modal-title').innerText = `Impacto de Compuerta · ${currentGateRequestId}`;
        document.getElementById('diff-modal-summary').innerText = data.human_summary || 'Sin resumen';
        document.getElementById('diff-modal-body').innerHTML = `
          <div class="text-emerald-400 font-bold">--- a/railway.json</div>
          <div class="text-emerald-400 font-bold">+++ b/railway.json</div>
          <div class="text-zinc-500">@@ -12,6 +12,8 @@</div>
          <div>  "deploy": {</div>
          <div class="text-emerald-400 font-semibold bg-emerald-500/10 px-1 py-0.5 rounded">+   "previewEnv": "pr-staging",</div>
          <div class="text-emerald-400 font-semibold bg-emerald-500/10 px-1 py-0.5 rounded">+   "invariantsCheck": "enforced"</div>
          <div>  }</div>
          <div class="mt-3 text-zinc-400 border-t bd pt-2"># Contratos auditados: DR-INV-001 (OK), DR-PAY-001 (OK)</div>
        `;
        document.getElementById('diff-modal').classList.remove('hidden');
        lucide.createIcons();
      } catch (e) {
        showToast('Error al inspeccionar impacto: ' + e.message, 'error');
      }
    }
    window.inspectCurrentGateImpact = inspectCurrentGateImpact;

    function closeDiffModal() {
      document.getElementById('diff-modal').classList.add('hidden');
    }
    window.closeDiffModal = closeDiffModal;

    // ==========================================
    // TERMINAL DRAWER CONTROLS
    // ==========================================
    function openTerminalDrawer() {
      document.getElementById('terminal-drawer').classList.remove('translate-x-full');
    }
    window.openTerminalDrawer = openTerminalDrawer;

    function closeTerminalDrawer() {
      document.getElementById('terminal-drawer').classList.add('translate-x-full');
    }
    window.closeTerminalDrawer = closeTerminalDrawer;

    function clearTerminalLogs() {
      const c = document.getElementById('terminal-stdout-container');
      if (c) c.innerHTML = '<div class="text-zinc-500">[CLEAR] Consola limpiada.</div>';
    }
    window.clearTerminalLogs = clearTerminalLogs;

    function copyTerminalLogs() {
      const c = document.getElementById('terminal-stdout-container');
      if (c) {
        navigator.clipboard.writeText(c.innerText);
        showToast('Logs copiados al portapapeles', 'success');
      }
    }
    window.copyTerminalLogs = copyTerminalLogs;

    function appendTerminalLog(line) {
      const c = document.getElementById('terminal-stdout-container');
      if (!c) return;
      const d = document.createElement('div');
      let col = 'text-zinc-300';
      if (line.includes('[SUCCESS]') || line.includes('PASSED')) col = 'text-emerald-400';
      else if (line.includes('[ERROR]') || line.includes('[EXCEPTION]') || line.includes('FAILED')) col = 'text-red-400';
      else if (line.includes('[WARN]')) col = 'text-amber-400';
      else if (line.includes('[CONFIG]') || line.includes('[SECURITY]')) col = 'text-blue-400';
      d.className = `${col} font-mono text-xs leading-relaxed`;
      d.innerText = line;
      c.appendChild(d);
      c.scrollTop = c.scrollHeight;
    }

    function viewActionLogsInTerminal(execId) {
      openTerminalDrawer();
      appendTerminalLog(`--- Mostrando logs de ejecución: ${execId} ---`);
    }
    window.viewActionLogsInTerminal = viewActionLogsInTerminal;

    // ==========================================
    // SETTINGS DRAWER CONTROLS
    // ==========================================
    function openSettingsDrawer() {
      document.getElementById('settings-drawer').classList.remove('translate-x-full');
    }
    window.openSettingsDrawer = openSettingsDrawer;

    function closeSettingsDrawer() {
      document.getElementById('settings-drawer').classList.add('translate-x-full');
    }
    window.closeSettingsDrawer = closeSettingsDrawer;

    // ==========================================
    // SSE INITIALIZER
    // ==========================================
    function initSSE() {
      try {
        const evtSource = new EventSource(`${API_BASE}/api/events/stream`);
        evtSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'GATE_REQUESTED') {
              showToast(`Nueva compuerta: ${data.action}`, 'info');
              loadDashboardSnapshot();
            } else if (data.type === 'ACTION_COMPLETED') {
              loadActionHistory();
            }
          } catch (e) {}
        };
      } catch (e) {
        console.warn('SSE fallback to polling');
      }
    }

    function escapeHtml(str) {
      return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function formatMarkdownContent(str) {
      return escapeHtml(str)
        .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>')
        .replace(/`([^`]+)`/g, '<code class="mono px-1 py-0.5 rounded bg-black/50 text-emerald-400">$1</code>');
    }
  </script>
</body>
</html>"""
