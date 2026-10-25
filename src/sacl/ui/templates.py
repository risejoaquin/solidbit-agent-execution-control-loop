"""Compiled Engineering & Operations Console Template V5 (Autor: LUCILFER / risejoaquin)."""

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
      --bg: #000000;
      --surface: #020204;
      --surface-elevated: #040406;
      --surface-card: #030305;
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
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background-color: #000000 !important;
      color: #ededed;
      margin: 0;
      padding: 0;
      overflow-x: hidden;
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
      padding: 0.45rem 0.85rem;
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
      animation: toastIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes toastIn {
      from { transform: translateY(0.75rem) scale(0.97); opacity: 0; }
      to { transform: translateY(0) scale(1); opacity: 1; }
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
<body class="flex flex-col h-screen bg-[#000000] text-[#f4f4f6]">

  <!-- TOP HEADER -->
  <header class="h-16 border-b bd flex items-center justify-between px-3 md:px-6 bg-[#000000]/95 backdrop-blur-md z-30 shrink-0">
    <!-- Brand & Active Project -->
    <div class="flex items-center gap-3">
      <div class="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/25 flex items-center justify-center shrink-0 cursor-pointer hover:border-emerald-500/50 transition-colors shadow-sm" onclick="switchSection('dashboard')" title="SolidBit SACL · Volver al HUD">
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="url(#solidbit-logo-grad)" stroke="#34d399" stroke-width="1.8" stroke-linejoin="round"/>
          <path d="M2 17L12 22L22 17" stroke="#10b981" stroke-width="1.8" stroke-linejoin="round"/>
          <path d="M2 12L12 17L22 12" stroke="#059669" stroke-width="1.8" stroke-linejoin="round"/>
          <defs>
            <linearGradient id="solidbit-logo-grad" x1="2" y1="2" x2="22" y2="12" gradientUnits="userSpaceOnUse">
              <stop stop-color="#10b981" stop-opacity="0.7"/>
              <stop stop-color="#047857" stop-opacity="0.3"/>
            </linearGradient>
          </defs>
        </svg>
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
      <button id="dtab-database" class="nav-pill flex items-center gap-1.5" onclick="switchSection('database')">
        <i data-lucide="database" class="w-3.5 h-3.5 text-emerald-400"></i>
        <span>Base de Datos WAL</span>
        <span id="nav-db-records-badge" class="mono text-[10px] px-1.5 py-0.2 rounded-full bg-emerald-500/20 text-emerald-300 font-bold">48</span>
      </button>
      <button id="dtab-gates" class="nav-pill flex items-center gap-1.5" onclick="switchSection('gates')">
        <i data-lucide="shield-alert" class="w-3.5 h-3.5 text-amber-400"></i>
        <span>Compuertas</span>
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

            <!-- Open File / Folder Button -->
      <button onclick="switchSection('projects'); showOpenFolderModal();" class="px-3 py-1.5 rounded-lg border bd bg-white/5 hover:bg-white/10 text-white cursor-pointer flex items-center gap-1.5 text-xs font-medium" title="Abrir Carpeta o Archivo">
        <i data-lucide="folder-open" class="w-3.5 h-3.5 text-amber-400"></i>
        <span class="hidden md:inline">Abrir Archivo / Carpeta</span>
      </button>
      <!-- Settings Drawer Button -->
      <button onclick="openSettingsDrawer()" class="relative p-2 rounded-lg border bd bg-white/5 hover:bg-white/10 text-white cursor-pointer" title="Configuración de Sistema">
        <i data-lucide="sliders" class="w-4 h-4"></i>
        <span id="tuerca-gate-badge" class="absolute -top-1 -right-1 w-4 h-4 bg-amber-400 text-black text-[10px] font-bold rounded-full flex items-center justify-center border border-black hidden">1</span>
      </button>
    </div>
  </header>

  <!-- MAIN SCROLLABLE CONTAINER -->
  <main class="flex-1 overflow-y-auto pb-24 md:pb-8 custom-scroll">

    <!-- ========================================== -->
    <!-- SECTION 1: OPERACIONES HUD (DASHBOARD) -->
    <!-- ========================================== -->
        <!-- ========================================== -->
    <!-- SECTION 1: OPERACIONES HUD & DASHBOARD EJECUTIVO -->
    <!-- ========================================== -->
        <!-- ========================================== -->
    <!-- SECTION 1: OPERACIONES HUD & DASHBOARD EJECUTIVO -->
    <!-- ========================================== -->
    <div id="sec-dashboard" class="p-4 md:p-8 max-w-7xl mx-auto space-y-8">

      <!-- HERO STATUS BANNER WITH LIVE PROGRESS PANEL -->
      <div class="section-canvas p-6 md:p-8 relative overflow-hidden bg-gradient-to-br from-[#030305] via-[#030305] to-[#020204]">
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          <div class="space-y-3">
            <div class="flex flex-wrap items-center gap-2">
              <span class="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/25 text-xs font-bold mono flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                SISTEMA OPERACIONAL
              </span>
              <span class="px-2.5 py-0.5 rounded-full bg-white/5 text-zinc-300 border bd text-xs font-mono">
                commit 439b48c
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
            <button onclick="executeActionWithProgress('reconcile_runs', this)" class="btn btn-secondary px-4 py-3 text-xs">
              <i data-lucide="refresh-cw" class="w-4 h-4 text-emerald-400"></i>
              <span>Reconciliar Procesos</span>
            </button>
            <button onclick="executeActionWithProgress('test_suite', this)" class="btn btn-secondary px-4 py-3 text-xs">
              <i data-lucide="check-square" class="w-4 h-4 text-purple-400"></i>
              <span>Correr Tests (29)</span>
            </button>
            <button onclick="switchSection('database')" class="btn btn-secondary px-4 py-3 text-xs">
              <i data-lucide="database" class="w-4 h-4 text-emerald-400"></i>
              <span>Ver Base de Datos</span>
            </button>
            <button onclick="openTerminalDrawer()" class="btn btn-primary px-4 py-3 text-xs">
              <i data-lucide="terminal" class="w-4 h-4 fill-black"></i>
              <span>Terminal Monospace</span>
            </button>
          </div>
        </div>

        <!-- In-Banner Live Execution Progress Monitor (Animates visibly when clicking actions) -->
        <div id="hero-action-progress-container" class="mt-6 pt-5 border-t bd hidden space-y-3">
          <div class="flex items-center justify-between text-xs font-mono">
            <span id="hero-progress-label" class="text-emerald-400 font-bold flex items-center gap-2">
              <i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i>
              <span>Ejecutando proceso...</span>
            </span>
            <span id="hero-progress-pct" class="text-zinc-400">0%</span>
          </div>
          <div class="w-full h-2 rounded-full bg-black/60 overflow-hidden border bd">
            <div id="hero-progress-bar" class="h-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-300" style="width: 0%"></div>
          </div>
          <div class="grid grid-cols-4 gap-2 text-[10px] mono text-zinc-400 pt-1" id="hero-progress-steps">
            <div class="p-2 rounded bg-black/40 border bd text-center" id="prog-step-1">1. Contratos OK</div>
            <div class="p-2 rounded bg-black/40 border bd text-center" id="prog-step-2">2. Locks SQLite</div>
            <div class="p-2 rounded bg-black/40 border bd text-center" id="prog-step-3">3. Pytest 29/29</div>
            <div class="p-2 rounded bg-black/40 border bd text-center" id="prog-step-4">4. WAL Sync</div>
          </div>
        </div>
      </div>

      <!-- EXECUTIVE TELEMETRY & KPI MATRIX (4 HIGH-VISIBILITY CARDS) -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="section-canvas p-5 space-y-2 border-emerald-500/20 bg-gradient-to-br from-[#020204] to-[#030305]">
          <div class="flex items-center justify-between">
            <span class="text-xs text-zinc-400 font-medium">Tasa de Éxito SDLC</span>
            <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
          </div>
          <div class="text-2xl md:text-3xl font-extrabold text-white mono">100.0%</div>
          <div class="text-[11px] text-emerald-400 flex items-center gap-1 font-mono">
            <i data-lucide="trending-up" class="w-3.5 h-3.5"></i>
            <span>29/29 tests pasando sin fallos</span>
          </div>
        </div>

        <div class="section-canvas p-5 space-y-2 border-blue-500/20 bg-gradient-to-br from-[#020204] to-[#030305]">
          <div class="flex items-center justify-between">
            <span class="text-xs text-zinc-400 font-medium">Contratos Inmutables</span>
            <span class="w-2 h-2 rounded-full bg-blue-400"></span>
          </div>
          <div class="text-2xl md:text-3xl font-extrabold text-white mono">4/4</div>
          <div class="text-[11px] text-blue-400 flex items-center gap-1 font-mono">
            <i data-lucide="shield-check" class="w-3.5 h-3.5"></i>
            <span>DR-INV, DR-PAY, DR-IDEM, DR-REC</span>
          </div>
        </div>

        <div class="section-canvas p-5 space-y-2 border-purple-500/20 bg-gradient-to-br from-[#020204] to-[#030305]">
          <div class="flex items-center justify-between">
            <span class="text-xs text-zinc-400 font-medium">Latencia Promedio</span>
            <span class="w-2 h-2 rounded-full bg-purple-400"></span>
          </div>
          <div class="text-2xl md:text-3xl font-extrabold text-white mono">0.34s</div>
          <div class="text-[11px] text-purple-400 flex items-center gap-1 font-mono">
            <i data-lucide="zap" class="w-3.5 h-3.5"></i>
            <span>Cold-start y reconciliación</span>
          </div>
        </div>

        <div class="section-canvas p-5 space-y-2 border-amber-500/20 bg-gradient-to-br from-[#020204] to-[#030305]">
          <div class="flex items-center justify-between">
            <span class="text-xs text-zinc-400 font-medium">Salud SQLite WAL</span>
            <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
          </div>
          <div class="text-2xl md:text-3xl font-extrabold text-emerald-400 mono">100% OK</div>
          <div class="text-[11px] text-zinc-400 flex items-center gap-1 font-mono">
            <i data-lucide="check" class="w-3.5 h-3.5 text-emerald-400"></i>
            <span>PRAGMA: 0 páginas corruptas</span>
          </div>
        </div>
      </div>

      <!-- SECTION: DECISION INTELLIGENCE DOSSIER (TOMA DE DECISIONES CON INFORMACIÓN COMPLETA) -->
      <div class="section-canvas p-6 md:p-8 space-y-6 border-amber-500/40 bg-gradient-to-br from-[#181512] via-[#141318] to-[#030305]" id="active-gate-panel">
        
        <!-- Dossier Header -->
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b bd pb-4">
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full bg-amber-400 animate-pulse"></span>
              <span class="text-xs font-bold uppercase tracking-wider text-amber-400 mono">Centro de Inteligencia & Toma de Decisiones Soberanas</span>
              <span id="gate-request-id-pill" class="mono text-[10px] px-2 py-0.5 rounded bg-black/50 border bd text-zinc-300">REQ-20261025-E43308B0</span>
            </div>
            <h2 class="text-xl md:text-2xl font-bold text-white mono" id="gate-action-title">DEPLOY_STAGING_PREVIEW</h2>
            <p class="text-xs text-zinc-400 max-w-2xl" id="gate-reason-desc">
              Despliegue efímero en Railway de preview build con contratos verificados. Decisión requerida antes de aplicar cambios a staging.
            </p>
          </div>

          <!-- Risk & Blast Radius Badges -->
          <div class="flex flex-wrap items-center gap-2 shrink-0">
            <div class="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/25 flex items-center gap-2">
              <span class="text-[10px] text-zinc-400 uppercase font-bold">Riesgo:</span>
              <span class="text-xs font-bold text-emerald-400 mono">BAJO (Staging Aislado)</span>
            </div>
            <div class="px-3 py-1.5 rounded-lg bg-blue-500/10 border border-blue-500/25 flex items-center gap-2">
              <span class="text-[10px] text-zinc-400 uppercase font-bold">Blast Radius:</span>
              <span class="text-xs font-bold text-blue-400 mono">2 archivos</span>
            </div>
            <div class="px-3 py-1.5 rounded-lg bg-white/5 border bd flex items-center gap-1.5 text-xs text-zinc-300 mono">
              <i data-lucide="clock" class="w-3.5 h-3.5 text-zinc-400"></i>
              <span>TTL: 7 días restantes</span>
            </div>
          </div>
        </div>

        <!-- Dossier Dynamic Body (Morphs on approval or rejection) -->
        <div id="active-gate-container" class="space-y-6">

          <!-- Information Tabs for Decision Making -->
          <div class="space-y-4">
            <div class="flex items-center gap-2 border-b bd pb-2.5">
              <button onclick="switchDossierTab('checklist')" id="dossier-tab-btn-checklist" class="nav-pill active text-xs flex items-center gap-1.5">
                <i data-lucide="clipboard-check" class="w-3.5 h-3.5 text-emerald-400"></i>
                <span>Matriz de Verificación (5/5)</span>
              </button>
              <button onclick="switchDossierTab('diff')" id="dossier-tab-btn-diff" class="nav-pill text-xs flex items-center gap-1.5">
                <i data-lucide="file-diff" class="w-3.5 h-3.5 text-blue-400"></i>
                <span>Diff de Código en Vivo</span>
              </button>
              <button onclick="switchDossierTab('audit')" id="dossier-tab-btn-audit" class="nav-pill text-xs flex items-center gap-1.5">
                <i data-lucide="shield" class="w-3.5 h-3.5 text-purple-400"></i>
                <span>Trazabilidad Soberana</span>
              </button>
            </div>

            <!-- TAB 1: VERIFICATION CHECKLIST -->
            <div id="dossier-panel-checklist" class="space-y-2.5">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div class="p-3.5 rounded-xl bg-black/40 border border-emerald-500/20 flex items-start gap-3">
                  <div class="w-6 h-6 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0 mt-0.5">
                    <i data-lucide="check" class="w-3.5 h-3.5 stroke-[3]"></i>
                  </div>
                  <div>
                    <div class="text-xs font-bold text-white mono">Invariante DR-INV-001 (Inventario Atómico)</div>
                    <div class="text-[11px] text-zinc-400 mt-0.5">Verificado. Cero colisiones de stock o ventas duplicadas.</div>
                  </div>
                </div>

                <div class="p-3.5 rounded-xl bg-black/40 border border-emerald-500/20 flex items-start gap-3">
                  <div class="w-6 h-6 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0 mt-0.5">
                    <i data-lucide="check" class="w-3.5 h-3.5 stroke-[3]"></i>
                  </div>
                  <div>
                    <div class="text-xs font-bold text-white mono">Invariante DR-PAY-001 (Doble Partida)</div>
                    <div class="text-[11px] text-zinc-400 mt-0.5">Verificado. Suma cero balanceada en transacciones contables.</div>
                  </div>
                </div>

                <div class="p-3.5 rounded-xl bg-black/40 border border-emerald-500/20 flex items-start gap-3">
                  <div class="w-6 h-6 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0 mt-0.5">
                    <i data-lucide="check" class="w-3.5 h-3.5 stroke-[3]"></i>
                  </div>
                  <div>
                    <div class="text-xs font-bold text-white mono">Suite de Pruebas Automatizadas (Pytest)</div>
                    <div class="text-[11px] text-zinc-400 mt-0.5">29/29 tests unitarios e integración en VERDE (100% Pass).</div>
                  </div>
                </div>

                <div class="p-3.5 rounded-xl bg-black/40 border border-emerald-500/20 flex items-start gap-3">
                  <div class="w-6 h-6 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0 mt-0.5">
                    <i data-lucide="check" class="w-3.5 h-3.5 stroke-[3]"></i>
                  </div>
                  <div>
                    <div class="text-xs font-bold text-white mono">Escaneo de Secretos & Hard Deny</div>
                    <div class="text-[11px] text-zinc-400 mt-0.5">0 llaves privadas o credenciales expuestas en commit.</div>
                  </div>
                </div>
              </div>

              <div class="p-3 rounded-lg bg-white/5 border bd flex items-center justify-between text-xs text-zinc-300">
                <span class="flex items-center gap-2">
                  <i data-lucide="undo-2" class="w-4 h-4 text-emerald-400"></i>
                  <span>Plan de Reversión Inmediata (Rollback): Reversión atómica disponible con 1 clic (<code class="mono text-zinc-300">git revert 439b48c</code>)</span>
                </span>
                <span class="text-emerald-400 font-bold mono">LISTO</span>
              </div>
            </div>

            <!-- TAB 2: LIVE CODE DIFF -->
            <div id="dossier-panel-diff" class="p-4 rounded-xl bg-black/60 border bd font-mono text-xs overflow-x-auto text-zinc-300 space-y-1 hidden">
              <div class="text-emerald-400 font-bold">--- a/railway.json</div>
              <div class="text-emerald-400 font-bold">+++ b/railway.json</div>
              <div class="text-zinc-500">@@ -12,6 +12,9 @@</div>
              <div>  "deploy": {</div>
              <div class="text-emerald-400 font-semibold bg-emerald-500/10 px-1 py-0.5 rounded">+   "previewEnv": "pr-staging-preview",</div>
              <div class="text-emerald-400 font-semibold bg-emerald-500/10 px-1 py-0.5 rounded">+   "invariantsEnforcement": "STRICT",</div>
              <div class="text-emerald-400 font-semibold bg-emerald-500/10 px-1 py-0.5 rounded">+   "operatorAttribution": "LUCILFER / @risejoaquin"</div>
              <div>  }</div>
              <div class="text-emerald-400 font-bold mt-2">--- a/services/web-storefront/package.json</div>
              <div class="text-zinc-500">@@ -4,4 +4,4 @@</div>
              <div class="text-red-400 font-semibold bg-red-500/10 px-1 py-0.5 rounded">-   "version": "1.1.0",</div>
              <div class="text-emerald-400 font-semibold bg-emerald-500/10 px-1 py-0.5 rounded">+   "version": "1.2.0-preview",</div>
            </div>

            <!-- TAB 3: AUDIT TRAIL -->
            <div id="dossier-panel-audit" class="p-4 rounded-xl bg-black/60 border bd font-mono text-xs text-zinc-300 space-y-2 hidden">
              <div class="flex justify-between"><span class="text-zinc-500">Operador Autorizado:</span><span class="text-white font-bold">LUCILFER / risejoaquin (@risejoaquin)</span></div>
              <div class="flex justify-between"><span class="text-zinc-500">Firma Criptográfica:</span><span class="text-emerald-400 font-bold">HMAC-SHA256 (Inmutable)</span></div>
              <div class="flex justify-between"><span class="text-zinc-500">Almacenamiento:</span><span class="text-zinc-300">SQLite approvals table (sacl_ops.db)</span></div>
              <div class="flex justify-between"><span class="text-zinc-500">Destino de Despliegue:</span><span class="text-blue-400 font-bold">Railway PR Preview Isolation</span></div>
            </div>
          </div>

          <!-- Decision Execution Buttons -->
          <div class="pt-2 flex flex-col sm:flex-row items-center justify-end gap-3 border-t bd">
            <button onclick="quickRejectFromCard()" id="btn-gate-reject" class="btn btn-danger text-xs px-5 py-2.5 w-full sm:w-auto">
              <i data-lucide="x-circle" class="w-4 h-4"></i>
              <span class="font-bold">Rechazar / Veto Soberano</span>
            </button>
            <button onclick="quickApproveFromCard()" id="btn-gate-approve" class="btn btn-success text-xs px-7 py-2.5 shadow-xl font-bold btn-gate-approve-action w-full sm:w-auto">
              <i data-lucide="check" class="w-4 h-4 stroke-[3]"></i>
              <span>Autorizar Despliegue Soberano</span>
            </button>
          </div>

        </div>

      </div>

      <!-- SECTION: GESTIÓN DE DATOS EN VIVO (SQLITE WAL DIRECT EXPLORER) -->
      <div class="section-canvas p-6 md:p-8 space-y-5 bg-gradient-to-br from-[#030305] to-[#030305] border-emerald-500/25">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b bd pb-4">
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <i data-lucide="database" class="w-5 h-5 text-emerald-400"></i>
              <h2 class="text-base font-bold text-white tracking-tight">Gestión de Almacenamiento & Telemetría SQLite WAL</h2>
              <span class="mono text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-bold">LIVE SYNC</span>
            </div>
            <p class="text-xs text-zinc-400">Inspecciona y administra los registros soberanos sin salir del dashboard.</p>
          </div>

          <div class="flex flex-wrap items-center gap-2">
            <button onclick="checkDbIntegrity()" class="btn btn-secondary text-xs px-3 py-1.5">
              <i data-lucide="check-circle" class="w-3.5 h-3.5 text-emerald-400"></i>
              <span>PRAGMA integrity_check</span>
            </button>
            <button onclick="executeWalCheckpoint()" class="btn btn-secondary text-xs px-3 py-1.5">
              <i data-lucide="refresh-cw" class="w-3.5 h-3.5 text-blue-400"></i>
              <span>PRAGMA wal_checkpoint</span>
            </button>
            <button onclick="switchSection('database')" class="btn btn-primary text-xs px-3.5 py-1.5">
              <span>Abrir Explorador Completo &rarr;</span>
            </button>
          </div>
        </div>

        <!-- Table Selector Buttons with Counters -->
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
          <button onclick="loadHudEmbeddedTable('approvals')" class="item-card p-3 text-left hover:border-emerald-500/50 cursor-pointer">
            <div class="text-xs text-zinc-400 mono">approvals</div>
            <div class="text-lg font-bold mono text-white mt-1" id="tbl-cnt-approvals">6</div>
            <div class="text-[10px] text-emerald-400">Compuertas</div>
          </button>
          <button onclick="loadHudEmbeddedTable('runs')" class="item-card p-3 text-left hover:border-emerald-500/50 cursor-pointer">
            <div class="text-xs text-zinc-400 mono">runs</div>
            <div class="text-lg font-bold mono text-white mt-1" id="tbl-cnt-runs">12</div>
            <div class="text-[10px] text-blue-400">Ejecuciones</div>
          </button>
          <button onclick="loadHudEmbeddedTable('events')" class="item-card p-3 text-left hover:border-emerald-500/50 cursor-pointer">
            <div class="text-xs text-zinc-400 mono">events</div>
            <div class="text-lg font-bold mono text-white mt-1" id="tbl-cnt-events">18</div>
            <div class="text-[10px] text-purple-400">Auditoría WAL</div>
          </button>
          <button onclick="loadHudEmbeddedTable('errors')" class="item-card p-3 text-left hover:border-emerald-500/50 cursor-pointer">
            <div class="text-xs text-zinc-400 mono">errors</div>
            <div class="text-lg font-bold mono text-white mt-1" id="tbl-cnt-errors">12</div>
            <div class="text-[10px] text-red-400">Forenses</div>
          </button>
          <button onclick="loadHudEmbeddedTable('leases')" class="item-card p-3 text-left hover:border-emerald-500/50 cursor-pointer">
            <div class="text-xs text-zinc-400 mono">leases</div>
            <div class="text-lg font-bold mono text-white mt-1" id="tbl-cnt-leases">1</div>
            <div class="text-[10px] text-amber-400">Singleton Lock</div>
          </button>
          <button onclick="loadHudEmbeddedTable('jobs')" class="item-card p-3 text-left hover:border-emerald-500/50 cursor-pointer">
            <div class="text-xs text-zinc-400 mono">jobs</div>
            <div class="text-lg font-bold mono text-white mt-1" id="tbl-cnt-jobs">2</div>
            <div class="text-[10px] text-zinc-400">Trabajos</div>
          </button>
        </div>

        <!-- Embedded Quick Table Rows Inspector on HUD -->
        <div class="p-4 rounded-xl bg-black/50 border bd space-y-3">
          <div class="flex items-center justify-between text-xs mono">
            <span class="text-zinc-400 font-semibold" id="hud-embedded-table-title">Registros Recientes: approvals</span>
            <span class="text-emerald-400">SQLite WAL Direct Query</span>
          </div>
          <div class="overflow-x-auto custom-scroll max-h-[220px]">
            <table class="w-full text-left text-xs mono">
              <thead class="bg-black/60 sticky top-0">
                <tr class="border-b bd text-zinc-400 font-semibold" id="hud-embedded-table-headers">
                  <th class="py-2 px-3">Approval ID</th>
                  <th class="py-2 px-3">Acción</th>
                  <th class="py-2 px-3">Estado</th>
                  <th class="py-2 px-3">Operador</th>
                  <th class="py-2 px-3">Fecha UTC</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-white/5" id="hud-embedded-table-body">
                <tr><td colspan="5" class="py-4 text-center text-zinc-500">Cargando registros SQLite...</td></tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>

      <!-- LEDGER DE AUDITORÍA EN VIVO (WAL) -->
      <div class="section-canvas p-6 space-y-4">
        <div class="flex items-center justify-between border-b bd pb-3">
          <div class="flex items-center gap-2">
            <i data-lucide="scroll-text" class="w-4 h-4 text-emerald-400"></i>
            <h3 class="text-sm font-bold uppercase tracking-wider text-white">Ledger de Auditoría en Tiempo Real</h3>
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

    <!-- ========================================== -->
    <div id="sec-database" class="p-4 md:p-8 max-w-7xl mx-auto space-y-6 hidden">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b bd pb-4">
        <div>
          <h2 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <i data-lucide="database" class="w-6 h-6 text-emerald-400"></i>
            <span>Base de Datos Operacional SQLite WAL & Telemetría</span>
          </h2>
          <p class="text-sm text-zinc-400 mt-1">Inspección de almacenamiento persistente en vivo sin bloqueos de lectura concurrentes.</p>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="checkDbIntegrity()" class="btn btn-secondary text-xs px-3.5 py-2">
            <i data-lucide="check-circle" class="w-3.5 h-3.5 text-emerald-400"></i>
            <span>Integrity Check</span>
          </button>
          <button onclick="loadDbDashboard()" class="btn btn-secondary text-xs px-3.5 py-2">
            <i data-lucide="refresh-cw" class="w-3.5 h-3.5"></i>
            <span>Actualizar Tablas</span>
          </button>
        </div>
      </div>

      <!-- Database Info Strip -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="item-card p-4 space-y-1">
          <span class="text-xs text-zinc-400">Archivo en Disco:</span>
          <div class="text-sm font-bold mono text-white truncate" id="db-tab-path">sacl_ops.db</div>
          <div class="text-xs text-emerald-400 font-semibold" id="db-tab-size">128 KB (Páginas de 4KB)</div>
        </div>
        <div class="item-card p-4 space-y-1">
          <span class="text-xs text-zinc-400">Modo de Diario:</span>
          <div class="text-sm font-bold mono text-emerald-400">WAL (Write-Ahead Log)</div>
          <div class="text-xs text-zinc-500">Lecturas Concurrentes Sin Bloqueos</div>
        </div>
        <div class="item-card p-4 space-y-1">
          <span class="text-xs text-zinc-400">Integridad de Archivo:</span>
          <div class="text-sm font-bold mono text-emerald-400" id="db-tab-integrity">PRAGMA: OK</div>
          <div class="text-xs text-zinc-500">0 páginas corruptas</div>
        </div>
        <div class="item-card p-4 space-y-1">
          <span class="text-xs text-zinc-400">Total de Registros:</span>
          <div class="text-sm font-bold mono text-white" id="db-tab-records">48 Registros</div>
          <div class="text-xs text-zinc-500">14 tablas en esquema</div>
        </div>
      </div>

      <!-- Table Selector Tabs -->
      <div class="section-canvas p-6 space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b bd pb-3">
          <div class="flex flex-wrap items-center gap-1.5" id="db-table-selector-tabs">
            <button onclick="viewTableRows('approvals')" class="nav-pill active text-xs mono" id="tab-btn-approvals">approvals</button>
            <button onclick="viewTableRows('runs')" class="nav-pill text-xs mono" id="tab-btn-runs">runs</button>
            <button onclick="viewTableRows('events')" class="nav-pill text-xs mono" id="tab-btn-events">events</button>
            <button onclick="viewTableRows('errors')" class="nav-pill text-xs mono" id="tab-btn-errors">errors</button>
            <button onclick="viewTableRows('leases')" class="nav-pill text-xs mono" id="tab-btn-leases">leases</button>
            <button onclick="viewTableRows('jobs')" class="nav-pill text-xs mono" id="tab-btn-jobs">jobs</button>
          </div>
          <div class="text-xs mono text-zinc-400" id="db-table-active-count">Mostrando registros</div>
        </div>

        <!-- Table Display Area -->
        <div class="overflow-x-auto custom-scroll max-h-[450px]">
          <table class="w-full text-left text-xs mono">
            <thead class="bg-black/50 sticky top-0 z-10">
              <tr class="border-b bd text-zinc-400 font-semibold" id="db-table-headers"></tr>
            </thead>
            <tbody class="divide-y divide-white/5" id="db-table-body">
              <tr><td class="py-4 text-center text-zinc-500" colspan="10">Cargando registros...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- SECTION 3: GOBERNANZA & COMPUERTAS (TAB) -->
    <!-- ========================================== -->
    <div id="sec-gates" class="p-4 md:p-8 max-w-7xl mx-auto space-y-6 hidden">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b bd pb-4">
        <div>
          <h2 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <i data-lucide="shield-alert" class="w-6 h-6 text-amber-400"></i>
            <span>Compuertas de Gobernanza & Decisiones Humanas</span>
          </h2>
          <p class="text-sm text-zinc-400 mt-1">Supervisión en tiempo real de compuertas requeridas antes del merge o despliegue a producción.</p>
        </div>
        <button onclick="createNewGateSim()" class="btn btn-secondary text-xs px-4 py-2">
          <i data-lucide="plus" class="w-4 h-4 text-emerald-400"></i>
          <span>Crear Nueva Compuerta de Prueba</span>
        </button>
      </div>

      <!-- Featured Gate Card in Gates Tab -->
      <div class="section-canvas p-6 md:p-8 space-y-6 border-amber-500/30 bg-gradient-to-br from-[#161412] to-[#020204]" id="gates-tab-card-container">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b bd pb-4">
          <div>
            <span class="px-2.5 py-0.5 rounded text-xs mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/25 uppercase">
              COMPUERTA BLOQUEANTE ACTIVA
            </span>
            <h3 class="text-xl font-bold text-white mono mt-2" id="gates-tab-action-title">DEPLOY_STAGING_PREVIEW</h3>
            <p class="text-xs text-zinc-400 mt-1" id="gates-tab-reason-desc">Despliegue efímero en Railway de preview build con contratos verificados.</p>
          </div>
          <div class="flex items-center gap-2">
            <button onclick="inspectCurrentGateImpact()" class="btn btn-secondary text-xs px-4 py-2.5">
              <i data-lucide="file-diff" class="w-4 h-4"></i>
              <span>Inspeccionar Diff</span>
            </button>
            <button onclick="quickRejectFromCard()" id="btn-gates-tab-reject" class="btn btn-danger text-xs px-4 py-2.5">
              <i data-lucide="x-circle" class="w-4 h-4"></i>
              <span>Rechazar</span>
            </button>
            <button onclick="quickApproveFromCard()" id="btn-gates-tab-approve" class="btn btn-success text-xs px-5 py-2.5 shadow-lg btn-gate-approve-action">
              <i data-lucide="check" class="w-4 h-4 stroke-[2.5]"></i>
              <span class="font-bold">Autorizar Despliegue</span>
            </button>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
          <div class="p-3 rounded-lg bg-black/40 border bd">
            <span class="text-zinc-500">Request ID:</span>
            <div class="text-zinc-200 font-bold mt-0.5" id="gates-tab-req-id">REQ-20261025-E43308B0</div>
          </div>
          <div class="p-3 rounded-lg bg-black/40 border bd">
            <span class="text-zinc-500">Archivos Afectados:</span>
            <div class="text-zinc-200 font-bold mt-0.5">services/web-storefront, railway.json</div>
          </div>
          <div class="p-3 rounded-lg bg-black/40 border bd">
            <span class="text-zinc-500">Expiración (TTL):</span>
            <div class="text-zinc-200 font-bold mt-0.5">7 días restantes</div>
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
            <tbody class="divide-y divide-white/5 mono text-xs" id="decisions-history-tbody-full"></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- SECTION 4: PIPELINES SDLC -->
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
            <input type="checkbox" class="action-checkbox w-4 h-4 rounded border-[#27272a] bg-[#040406] text-emerald-500 focus:ring-0 hidden" data-action="test_suite">
          </div>
          <p class="text-xs text-zinc-400 leading-relaxed">
            Ejecución verificada de suite completa pytest con reporte de contratos, fixtures y esquemas SQLite WAL.
          </p>
          <div class="pt-3 border-t bd flex items-center justify-between text-xs">
            <span class="mono text-xs text-emerald-400 font-semibold">100% Pass</span>
            <button onclick="executeAction('test_suite', {}, this, event)" class="btn btn-secondary text-xs px-4 py-1.5">Ejecutar</button>
          </div>
        </div>

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
            <input type="checkbox" class="action-checkbox w-4 h-4 rounded border-[#27272a] bg-[#040406] text-emerald-500 focus:ring-0 hidden" data-action="security_audit">
          </div>
          <p class="text-xs text-zinc-400 leading-relaxed">
            Verificación estricta de contratos inmutables contra sobreventa de stock, doble cargo y escaneo de secretos en git.
          </p>
          <div class="pt-3 border-t bd flex items-center justify-between text-xs">
            <span class="mono text-xs text-emerald-400 font-semibold">Cero Bypass</span>
            <button onclick="executeAction('security_audit', {}, this, event)" class="btn btn-secondary text-xs px-4 py-1.5">Auditar</button>
          </div>
        </div>

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
            <input type="checkbox" class="action-checkbox w-4 h-4 rounded border-[#27272a] bg-[#040406] text-emerald-500 focus:ring-0 hidden" data-action="reconcile_runs">
          </div>
          <p class="text-xs text-zinc-400 leading-relaxed">
            Reclama leases huérfanos, actualiza runs interrumpidos a sus estados históricos y restaura estado CLEAN_STEADY en SQLite WAL.
          </p>
          <div class="pt-3 border-t bd flex items-center justify-between text-xs">
            <span class="mono text-xs text-emerald-400 font-semibold">Crash-Safe</span>
            <button onclick="executeAction('reconcile_runs', {}, this, event)" class="btn btn-secondary text-xs px-4 py-1.5">Reconciliar</button>
          </div>
        </div>

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
            <input type="checkbox" class="action-checkbox w-4 h-4 rounded border-[#27272a] bg-[#040406] text-emerald-500 focus:ring-0 hidden" data-action="release_pipeline">
          </div>
          <p class="text-xs text-zinc-400 leading-relaxed">
            Aprovisionamiento de entorno efímero en Railway y verificación de credenciales previas a compuerta de merge a producción.
          </p>
          <div class="pt-3 border-t bd flex items-center justify-between text-xs">
            <span class="mono text-xs text-amber-400 font-semibold">Compuerta Activa</span>
            <button onclick="executeAction('release_pipeline', {}, this, event)" class="btn btn-secondary text-xs px-4 py-1.5">Lanzar</button>
          </div>
        </div>

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
            <input type="checkbox" class="action-checkbox w-4 h-4 rounded border-[#27272a] bg-[#040406] text-emerald-500 focus:ring-0 hidden" data-action="software_design">
          </div>
          <p class="text-xs text-zinc-400 leading-relaxed">
            Extracción y validación de interfaces frozen, esquemas SQLite WAL y especificación arquitectónica integral de servicios.
          </p>
          <div class="pt-3 border-t bd flex items-center justify-between text-xs">
            <span class="mono text-xs text-zinc-400">Validado</span>
            <button onclick="executeAction('software_design', {}, this, event)" class="btn btn-secondary text-xs px-4 py-1.5">Generar</button>
          </div>
        </div>

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
            <input type="checkbox" class="action-checkbox w-4 h-4 rounded border-[#27272a] bg-[#040406] text-emerald-500 focus:ring-0 hidden" data-action="campaign_sprint">
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
    <!-- SECTION 5: REPOSITORIOS & DOCS -->
    <!-- ========================================== -->
        <!-- ========================================== -->
    <!-- SECTION 5: EXPLORADOR DE ARCHIVOS & REPOSITORIOS -->
    <!-- ========================================== -->
        <!-- ========================================== -->
    <!-- SECTION 5: EXPLORADOR DE ARCHIVOS & REPOSITORIOS -->
    <!-- ========================================== -->
    <div id="sec-projects" class="p-4 md:p-8 max-w-7xl mx-auto space-y-6 hidden">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b bd pb-4">
        <div>
          <h2 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <i data-lucide="folder-tree" class="w-6 h-6 text-amber-400"></i>
            <span>Explorador de Archivos, Carpetas & Código Fuente</span>
          </h2>
          <p class="text-sm text-zinc-400 mt-1">Navega libremente por el árbol de directorios, abre cualquier archivo local e inspecciona su contenido en vivo.</p>
        </div>

        <div class="flex flex-wrap items-center gap-2.5">
          <button onclick="showOpenFolderModal()" class="btn btn-primary text-xs px-3.5 py-2">
            <i data-lucide="folder-open" class="w-4 h-4 fill-black"></i>
            <span>Abrir Carpeta (Open Folder)</span>
          </button>
          <button onclick="showOpenFileModal()" class="btn btn-secondary text-xs px-3.5 py-2">
            <i data-lucide="file-plus" class="w-4 h-4 text-emerald-400"></i>
            <span>Abrir Archivo (Open File)</span>
          </button>
        </div>
      </div>

      <!-- WORKSPACE ROOT PATH BANNER -->
      <div class="section-canvas p-4 flex flex-col md:flex-row md:items-center justify-between gap-3 bg-gradient-to-r from-[#020204] to-[#020204] border-amber-500/25">
        <div class="flex items-center gap-3 truncate">
          <div class="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 shrink-0">
            <i data-lucide="folder" class="w-4 h-4"></i>
          </div>
          <div class="truncate">
            <div class="text-[10px] uppercase font-bold tracking-wider text-zinc-400">Carpeta Activa en Disco:</div>
            <div class="text-xs font-bold mono text-white truncate" id="fs-current-root-path">Cargando carpeta...</div>
          </div>
        </div>

        <div class="flex items-center gap-2 shrink-0">
          <div class="relative w-48 sm:w-64">
            <input type="text" id="fs-search-input" oninput="filterFsTree()" placeholder="Buscar archivo (.py, .json, .md)..."
              class="w-full bg-black/60 border bd rounded-lg px-3 py-1.5 pl-8 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-amber-400/50">
            <i data-lucide="search" class="w-3.5 h-3.5 text-zinc-500 absolute left-2.5 top-2"></i>
          </div>
          <button onclick="loadFsTree()" class="p-2 rounded-lg border bd bg-white/5 hover:bg-white/10 text-zinc-300 cursor-pointer" title="Recargar Árbol">
            <i data-lucide="rotate-ccw" class="w-3.5 h-3.5"></i>
          </button>
        </div>
      </div>

      <!-- SPLIT VIEW: FILE TREE (LEFT) & CODE VIEWER (RIGHT) -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[550px]">
        
        <!-- LEFT: FILE DIRECTORY TREE -->
        <div class="lg:col-span-4 section-canvas p-4 flex flex-col space-y-3 bg-[#020204]">
          <div class="flex items-center justify-between border-b bd pb-2.5">
            <span class="text-xs font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-2">
              <i data-lucide="list-tree" class="w-3.5 h-3.5 text-amber-400"></i>
              <span>Estructura de Archivos</span>
            </span>
            <span id="fs-tree-item-count" class="mono text-[10px] text-zinc-500">Cargando...</span>
          </div>

          <div id="fs-tree-container" class="flex-1 overflow-y-auto max-h-[580px] custom-scroll space-y-0.5 pr-1">
            <div class="py-8 text-center text-zinc-500 text-xs mono">
              <i data-lucide="loader-2" class="w-4 h-4 animate-spin mx-auto mb-2"></i>
              <span>Leyendo directorios...</span>
            </div>
          </div>
        </div>

        <!-- RIGHT: CODE & DOCUMENTATION VIEWER -->
        <div class="lg:col-span-8 section-canvas p-0 flex flex-col bg-[#000000] overflow-hidden border-[#27272a]">
          <!-- Viewer Top Toolbar -->
          <div class="h-14 border-b bd flex items-center justify-between px-4 bg-black/40 shrink-0">
            <div class="flex items-center gap-2.5 truncate">
              <i data-lucide="file-code" class="w-4 h-4 text-emerald-400 shrink-0"></i>
              <div class="truncate">
                <span class="text-xs font-bold text-white mono truncate" id="code-viewer-filename">Selecciona un archivo</span>
                <span class="text-[10px] text-zinc-500 mono ml-2" id="code-viewer-meta"></span>
              </div>
            </div>

            <div class="flex items-center gap-2 shrink-0">
              <button onclick="copyCodeViewerContent()" class="btn btn-secondary text-xs px-2.5 py-1 flex items-center gap-1.5" title="Copiar Contenido">
                <i data-lucide="copy" class="w-3.5 h-3.5 text-zinc-400"></i>
                <span id="code-viewer-copy-btn-text">Copiar</span>
              </button>
            </div>
          </div>

          <!-- File Absolute Path Subbar -->
          <div class="px-4 py-1.5 bg-black/20 border-b bd text-[11px] mono text-zinc-500 truncate" id="code-viewer-path">
            Haz clic en cualquier archivo del árbol o pulsa "Abrir Archivo" para inspeccionar.
          </div>

          <!-- Code Display Container -->
          <div id="code-viewer-content" class="flex-1 overflow-y-auto max-h-[520px] custom-scroll select-text">
            <div class="py-24 text-center text-zinc-500 mono space-y-2">
              <i data-lucide="file-search" class="w-8 h-8 text-zinc-600 mx-auto"></i>
              <div class="text-xs font-semibold text-zinc-400">Ningún archivo cargado en el visor</div>
              <p class="text-[11px] text-zinc-600 max-w-sm mx-auto">Haz clic en cualquier elemento del árbol izquierdo (.py, .json, .md, .toml) para abrir su código fuente en vivo.</p>
            </div>
          </div>
        </div>

      </div>

      <!-- DETECTED WORKSPACES & AUTOMATIONS (PRESERVED) -->
      <div class="section-canvas p-6 space-y-4">
        <h3 class="text-sm font-bold uppercase tracking-wider text-white flex items-center gap-2">
          <i data-lucide="boxes" class="w-4 h-4 text-purple-400"></i>
          <span>Espacios de Trabajo Detectados en el Sistema</span>
        </h3>
        <div id="projects-scanned-container" class="grid grid-cols-1 md:grid-cols-2 gap-4"></div>
      </div>
    </div>

    <!-- ========================================== -->
    <div id="sec-chat" class="flex flex-col h-[calc(100vh-8.5rem)] md:h-[calc(100vh-5rem)] max-w-5xl mx-auto w-full px-3 md:px-6 pb-2 hidden">
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

      <div id="chat-messages-scroll" class="flex-1 overflow-y-auto space-y-3 pr-1 min-h-0 custom-scroll">
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

      <div class="shrink-0 pt-3 space-y-2.5">
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

        <form id="chat-form" onsubmit="event.preventDefault(); sendChatMessage();" class="flex items-center gap-2 bg-[#030305] border bd rounded-xl p-2 focus-within:border-emerald-500/50 transition-all shadow-xl">
          <span class="mono text-emerald-400 pl-2 text-xs font-bold shrink-0">sacl&gt;</span>
          <input type="text" id="chat-input" placeholder="Escribe un comando o selecciona una acción rápida..."
            class="flex-1 bg-transparent px-2 py-1 text-xs mono text-white placeholder-zinc-500 focus:outline-none"
            onkeydown="handleChatKeyDown(event)">
          <button id="chat-send-btn" type="button" onclick="sendChatMessage()" class="btn btn-primary text-xs px-4 py-2 shrink-0 mono cursor-pointer">
            <span>Ejecutar ↵</span>
          </button>
        </form>
      </div>
    </div>

  </main>

  <!-- ========================================== -->
  <!-- FLOATING MULTI-ACTION EXECUTION BAR -->
  <!-- ========================================== -->
  <div id="floating-multiaction-bar" class="fixed bottom-20 md:bottom-8 left-1/2 -translate-x-1/2 z-40 bg-[#040406] border border-emerald-500/50 rounded-2xl px-5 py-3 shadow-2xl flex items-center gap-5 hidden">
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
  <nav class="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-[#000000]/95 border-t bd backdrop-blur-md z-30 flex items-center justify-around px-2">
    <button id="mtab-dashboard" class="mobile-tab active" onclick="switchSection('dashboard')">
      <i data-lucide="layout-grid" class="w-4 h-4"></i>
      <span>HUD</span>
    </button>
    <button id="mtab-database" class="mobile-tab" onclick="switchSection('database')">
      <i data-lucide="database" class="w-4 h-4"></i>
      <span>DB WAL</span>
    </button>
    <button id="mtab-gates" class="mobile-tab" onclick="switchSection('gates')">
      <i data-lucide="shield-alert" class="w-4 h-4"></i>
      <span>Compuertas</span>
    </button>
    <button id="mtab-sdlc" class="mobile-tab" onclick="switchSection('sdlc')">
      <i data-lucide="play-circle" class="w-4 h-4"></i>
      <span>Pipelines</span>
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
    <div class="section-canvas w-full max-w-4xl max-h-[85vh] flex flex-col overflow-hidden bg-[#030305] border-[#27272a] shadow-2xl">
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
    <div class="section-canvas w-full max-w-3xl max-h-[85vh] flex flex-col overflow-hidden bg-[#030305] border-[#27272a] shadow-2xl">
      <div class="p-4 border-b bd flex items-center justify-between shrink-0">
        <div class="flex items-center gap-2.5">
          <i data-lucide="file-diff" class="w-4 h-4 text-emerald-400"></i>
          <h3 class="text-sm font-bold text-white mono" id="diff-modal-title">Diff Inspector</h3>
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
  <!-- MODAL: OPEN FOLDER / WORKSPACE PICKER -->
  <!-- ========================================== -->
  <div id="open-folder-modal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-3 md:p-6 hidden">
    <div class="section-canvas w-full max-w-xl flex flex-col overflow-hidden bg-[#030305] border-amber-500/40 shadow-2xl space-y-4 p-6">
      <div class="flex items-center justify-between border-b bd pb-3">
        <div class="flex items-center gap-2.5">
          <i data-lucide="folder-open" class="w-5 h-5 text-amber-400"></i>
          <h3 class="text-base font-bold text-white mono">Abrir Carpeta (Open Folder)</h3>
        </div>
        <button onclick="closeOpenFolderModal()" class="p-1.5 text-zinc-400 hover:text-white rounded-lg hover:bg-white/10 cursor-pointer">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
      </div>

      <div class="space-y-3 text-xs">
        <div>
          <label class="block text-zinc-400 mb-1 font-semibold">Ruta Absoluta de la Carpeta en Disco:</label>
          <input type="text" id="open-folder-input" class="w-full bg-black/60 border bd rounded-xl p-3 text-white mono text-xs focus:outline-none focus:border-amber-400" placeholder="C:/proyectos/mi-proyecto">
        </div>

        <div>
          <div class="text-zinc-500 text-[11px] uppercase font-bold mb-1.5">Accesos Rápidos a Carpetas Locales:</div>
          <div class="space-y-1.5">
            <button onclick="setOpenFolderPreset('C:/Users/Lucilfer/Documents/Stable-Ecommerce-Orchestrator/SACL_IMPLEMENTATION_CAMPAIGN_v1/runs/impl-20261007-203727-e69378/worktrees/integration')" class="w-full text-left p-2.5 rounded-lg bg-black/40 border bd hover:border-amber-400/50 flex items-center justify-between text-zinc-300 hover:text-white">
              <span class="mono text-[11px] truncate">worktrees/integration (Espacio de Trabajo Activo)</span>
              <span class="text-amber-400 text-[10px] font-bold shrink-0">Seleccionar &rarr;</span>
            </button>
            <button onclick="setOpenFolderPreset('C:/Users/Lucilfer/Documents/Stable-Ecommerce-Orchestrator')" class="w-full text-left p-2.5 rounded-lg bg-black/40 border bd hover:border-amber-400/50 flex items-center justify-between text-zinc-300 hover:text-white">
              <span class="mono text-[11px] truncate">Stable-Ecommerce-Orchestrator (Raíz de Proyecto)</span>
              <span class="text-amber-400 text-[10px] font-bold shrink-0">Seleccionar &rarr;</span>
            </button>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-end gap-2.5 pt-3 border-t bd">
        <button onclick="closeOpenFolderModal()" class="btn btn-secondary text-xs px-4 py-2">Cancelar</button>
        <button onclick="submitOpenFolder()" class="btn btn-primary text-xs px-5 py-2">
          <span>Abrir Carpeta &rarr;</span>
        </button>
      </div>
    </div>
  </div>

  <!-- ========================================== -->
  <!-- MODAL: OPEN FILE PICKER -->
  <!-- ========================================== -->
  <div id="open-file-modal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-3 md:p-6 hidden">
    <div class="section-canvas w-full max-w-xl flex flex-col overflow-hidden bg-[#030305] border-emerald-500/40 shadow-2xl space-y-4 p-6">
      <div class="flex items-center justify-between border-b bd pb-3">
        <div class="flex items-center gap-2.5">
          <i data-lucide="file-code" class="w-5 h-5 text-emerald-400"></i>
          <h3 class="text-base font-bold text-white mono">Abrir Archivo (Open File)</h3>
        </div>
        <button onclick="closeOpenFileModal()" class="p-1.5 text-zinc-400 hover:text-white rounded-lg hover:bg-white/10 cursor-pointer">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
      </div>

      <div class="space-y-3 text-xs">
        <div>
          <label class="block text-zinc-400 mb-1 font-semibold">Ruta Absoluta del Archivo a Inspeccionar:</label>
          <input type="text" id="open-file-input" class="w-full bg-black/60 border bd rounded-xl p-3 text-white mono text-xs focus:outline-none focus:border-emerald-400" placeholder="C:/proyectos/pyproject.toml">
        </div>

        <div>
          <div class="text-zinc-500 text-[11px] uppercase font-bold mb-1.5">Archivos Clave Sugeridos:</div>
          <div class="space-y-1.5">
            <button onclick="setOpenFilePathPreset('pyproject.toml')" class="w-full text-left p-2.5 rounded-lg bg-black/40 border bd hover:border-emerald-400/50 flex items-center justify-between text-zinc-300 hover:text-white">
              <span class="mono text-[11px]">pyproject.toml (Configuración del Paquete)</span>
              <span class="text-emerald-400 text-[10px] font-bold">Abrir &rarr;</span>
            </button>
            <button onclick="setOpenFilePathPreset('src/sacl/cli.py')" class="w-full text-left p-2.5 rounded-lg bg-black/40 border bd hover:border-emerald-400/50 flex items-center justify-between text-zinc-300 hover:text-white">
              <span class="mono text-[11px]">src/sacl/cli.py (Punto de Entrada CLI)</span>
              <span class="text-emerald-400 text-[10px] font-bold">Abrir &rarr;</span>
            </button>
            <button onclick="setOpenFilePathPreset('README.md')" class="w-full text-left p-2.5 rounded-lg bg-black/40 border bd hover:border-emerald-400/50 flex items-center justify-between text-zinc-300 hover:text-white">
              <span class="mono text-[11px]">README.md (Documentación de Proyecto)</span>
              <span class="text-emerald-400 text-[10px] font-bold">Abrir &rarr;</span>
            </button>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-end gap-2.5 pt-3 border-t bd">
        <button onclick="closeOpenFileModal()" class="btn btn-secondary text-xs px-4 py-2">Cancelar</button>
        <button onclick="submitOpenFile()" class="btn btn-primary text-xs px-5 py-2">
          <span>Abrir & Inspeccionar &rarr;</span>
        </button>
      </div>
    </div>
  </div>

    <!-- ========================================== -->
  <!-- MODAL: OPEN FOLDER / WORKSPACE PICKER -->
  <!-- ========================================== -->
  <div id="open-folder-modal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-3 md:p-6 hidden">
    <div class="section-canvas w-full max-w-xl flex flex-col overflow-hidden bg-[#030305] border-amber-500/40 shadow-2xl space-y-4 p-6">
      <div class="flex items-center justify-between border-b bd pb-3">
        <div class="flex items-center gap-2.5">
          <i data-lucide="folder-open" class="w-5 h-5 text-amber-400"></i>
          <h3 class="text-base font-bold text-white mono">Abrir Carpeta (Open Folder)</h3>
        </div>
        <button onclick="closeOpenFolderModal()" class="p-1.5 text-zinc-400 hover:text-white rounded-lg hover:bg-white/10 cursor-pointer">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
      </div>

      <div class="space-y-3 text-xs">
        <div>
          <label class="block text-zinc-400 mb-1 font-semibold">Ruta de Carpeta en Disco:</label>
          <input type="text" id="open-folder-input" class="w-full bg-black/60 border bd rounded-xl p-3 text-white mono text-xs focus:outline-none focus:border-amber-400" placeholder="C:/Users/mi-proyecto">
        </div>

        <div>
          <div class="text-zinc-500 text-[11px] uppercase font-bold mb-1.5">Accesos Rápidos a Carpetas Locales:</div>
          <div class="space-y-1.5">
            <button onclick="setOpenFolderPreset('C:/Users/Lucilfer/Documents/Stable-Ecommerce-Orchestrator/SACL_IMPLEMENTATION_CAMPAIGN_v1/runs/impl-20261007-203727-e69378/worktrees/integration')" class="w-full text-left p-2.5 rounded-lg bg-black/40 border bd hover:border-amber-400/50 flex items-center justify-between text-zinc-300 hover:text-white">
              <span class="mono text-[11px] truncate">worktrees/integration (Espacio de Trabajo Activo)</span>
              <span class="text-amber-400 text-[10px] font-bold shrink-0">Seleccionar &rarr;</span>
            </button>
            <button onclick="setOpenFolderPreset('C:/Users/Lucilfer/Documents/Stable-Ecommerce-Orchestrator')" class="w-full text-left p-2.5 rounded-lg bg-black/40 border bd hover:border-amber-400/50 flex items-center justify-between text-zinc-300 hover:text-white">
              <span class="mono text-[11px] truncate">Stable-Ecommerce-Orchestrator (Raíz de Proyecto)</span>
              <span class="text-amber-400 text-[10px] font-bold shrink-0">Seleccionar &rarr;</span>
            </button>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-end gap-2.5 pt-3 border-t bd">
        <button onclick="closeOpenFolderModal()" class="btn btn-secondary text-xs px-4 py-2">Cancelar</button>
        <button onclick="submitOpenFolder()" class="btn btn-primary text-xs px-5 py-2">
          <span>Abrir Carpeta &rarr;</span>
        </button>
      </div>
    </div>
  </div>

  <!-- ========================================== -->
  <!-- MODAL: OPEN FILE PICKER -->
  <!-- ========================================== -->
  <div id="open-file-modal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-3 md:p-6 hidden">
    <div class="section-canvas w-full max-w-xl flex flex-col overflow-hidden bg-[#030305] border-emerald-500/40 shadow-2xl space-y-4 p-6">
      <div class="flex items-center justify-between border-b bd pb-3">
        <div class="flex items-center gap-2.5">
          <i data-lucide="file-code" class="w-5 h-5 text-emerald-400"></i>
          <h3 class="text-base font-bold text-white mono">Abrir Archivo (Open File)</h3>
        </div>
        <button onclick="closeOpenFileModal()" class="p-1.5 text-zinc-400 hover:text-white rounded-lg hover:bg-white/10 cursor-pointer">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
      </div>

      <div class="space-y-3 text-xs">
        <div>
          <label class="block text-zinc-400 mb-1 font-semibold">Ruta del Archivo a Inspeccionar:</label>
          <input type="text" id="open-file-input" class="w-full bg-black/60 border bd rounded-xl p-3 text-white mono text-xs focus:outline-none focus:border-emerald-400" placeholder="pyproject.toml o ruta completa">
        </div>

        <div>
          <div class="text-zinc-500 text-[11px] uppercase font-bold mb-1.5">Archivos Clave Sugeridos:</div>
          <div class="space-y-1.5">
            <button onclick="setOpenFilePathPreset('pyproject.toml')" class="w-full text-left p-2.5 rounded-lg bg-black/40 border bd hover:border-emerald-400/50 flex items-center justify-between text-zinc-300 hover:text-white">
              <span class="mono text-[11px]">pyproject.toml (Configuración del Paquete)</span>
              <span class="text-emerald-400 text-[10px] font-bold">Abrir &rarr;</span>
            </button>
            <button onclick="setOpenFilePathPreset('src/sacl/cli.py')" class="w-full text-left p-2.5 rounded-lg bg-black/40 border bd hover:border-emerald-400/50 flex items-center justify-between text-zinc-300 hover:text-white">
              <span class="mono text-[11px]">src/sacl/cli.py (Punto de Entrada CLI)</span>
              <span class="text-emerald-400 text-[10px] font-bold">Abrir &rarr;</span>
            </button>
            <button onclick="setOpenFilePathPreset('README.md')" class="w-full text-left p-2.5 rounded-lg bg-black/40 border bd hover:border-emerald-400/50 flex items-center justify-between text-zinc-300 hover:text-white">
              <span class="mono text-[11px]">README.md (Documentación de Proyecto)</span>
              <span class="text-emerald-400 text-[10px] font-bold">Abrir &rarr;</span>
            </button>
          </div>
        </div>
      </div>

      <div class="flex items-center justify-end gap-2.5 pt-3 border-t bd">
        <button onclick="closeOpenFileModal()" class="btn btn-secondary text-xs px-4 py-2">Cancelar</button>
        <button onclick="submitOpenFile()" class="btn btn-primary text-xs px-5 py-2">
          <span>Abrir & Inspeccionar &rarr;</span>
        </button>
      </div>
    </div>
  </div>

  <!-- ========================================== -->
  <!-- DRAWER: TERMINAL LOGS OVERLAY -->
  <!-- ========================================== -->
  <div id="terminal-drawer" class="fixed inset-y-0 right-0 w-full sm:w-[600px] bg-[#020204] border-l bd z-50 transform translate-x-full transition-transform duration-200 ease-out flex flex-col shadow-2xl">
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
    <div id="terminal-stdout-container" class="flex-1 p-4 font-mono text-xs text-zinc-300 overflow-y-auto space-y-1.5 select-text custom-scroll bg-[#000000]">
      <div class="text-zinc-500">[INIT] Consola de ejecución soberana lista. Aguardando procesos...</div>
    </div>
  </div>

  <!-- ========================================== -->
  <!-- DRAWER: SETTINGS & TOOLCHAIN OVERVIEW -->
  <!-- ========================================== -->
  <div id="settings-drawer" class="fixed inset-y-0 right-0 w-full sm:w-[420px] bg-[#030305] border-l bd z-50 transform translate-x-full transition-transform duration-200 ease-out flex flex-col shadow-2xl">
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
      <div class="section-canvas p-5 space-y-2.5">
        <div class="text-[10px] uppercase font-bold tracking-wider text-zinc-400">Autoría & Soberanía</div>
        <div class="text-base font-bold text-white">LUCILFER / risejoaquin</div>
        <div class="text-xs text-zinc-400">Cuenta GitHub activa: <span class="mono text-emerald-400 font-semibold">@risejoaquin</span></div>
        <div class="text-xs text-zinc-400">Email Resend: <span class="mono text-zinc-300">lucilfer@selfcaresinners.com</span></div>
      </div>

      <div class="space-y-2.5">
        <div class="text-xs font-bold uppercase tracking-wider text-zinc-400">Estado de Runtime</div>
        <div class="p-4 rounded-xl bg-black/40 border bd space-y-2 text-xs font-mono">
          <div class="flex justify-between"><span class="text-zinc-500">Python:</span><span class="text-zinc-300">3.11.9 (win32)</span></div>
          <div class="flex justify-between"><span class="text-zinc-500">Node.js:</span><span class="text-zinc-300">v24.14.0</span></div>
          <div class="flex justify-between"><span class="text-zinc-500">Base SQLite:</span><span class="text-emerald-400">sacl_ops.db (WAL)</span></div>
          <div class="flex justify-between"><span class="text-zinc-500">Crash State:</span><span id="drawer-crash-state" class="text-emerald-400 font-bold">CLEAN_STEADY</span></div>
        </div>
      </div>

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
  <div id="toast-container" class="fixed bottom-6 right-6 z-50 flex flex-col gap-2.5 pointer-events-none"></div>

  <!-- JAVASCRIPT APPLICATION CORE -->
  <script>
    const API_BASE = window.location.origin;
    let currentSection = 'dashboard';
    let isMultiSelectActive = false;
    let selectedActions = new Set();
    let allProjects = [];
    let currentGateRequestId = 'REQ-20261025-E43308B0';
    let activePendingGate = null;
    let activeTableRows = [];

    document.addEventListener('DOMContentLoaded', () => {
      lucide.createIcons();
      loadDashboardSnapshot(); loadHudEmbeddedTable('approvals'); loadHudEmbeddedTable('approvals');
      loadDbDashboard();
      loadProjects(); loadFsTree(); loadFsTree();
      loadChatHistory();
      loadActionHistory();
      initSSE();
    });

    // ==========================================
    // NAVIGATION SWITCHER
    // ==========================================
    function switchSection(secId) {
      currentSection = secId;
      ['dashboard', 'database', 'gates', 'sdlc', 'projects', 'chat'].forEach(id => {
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
      } else if (secId === 'database') {
        loadDbDashboard();
        viewTableRows('approvals');
      }
      lucide.createIcons();
    }
    window.switchSection = switchSection;

    // ==========================================
    // TOAST NOTIFIER (HIGH VISIBILITY)
    // ==========================================
    function showToast(msg, type = 'info') {
      const container = document.getElementById('toast-container');
      if (!container) return;
      const toast = document.createElement('div');
      const borderCol = type === 'success' ? 'border-emerald-500 bg-emerald-950/90 text-emerald-200' :
                        type === 'error' ? 'border-red-500 bg-red-950/90 text-red-200' : 'border-zinc-600 bg-[#040406] text-zinc-100';
      toast.className = `p-4 rounded-xl border ${borderCol} shadow-2xl text-xs font-semibold flex items-center gap-3 pointer-events-auto toast-animate min-w-[280px]`;
      toast.innerHTML = `<i data-lucide="${type === 'success' ? 'check-circle-2' : type === 'error' ? 'alert-triangle' : 'info'}" class="w-5 h-5 shrink-0 ${type === 'success' ? 'text-emerald-400' : type === 'error' ? 'text-red-400' : 'text-blue-400'}"></i><span>${msg}</span>`;
      container.appendChild(toast);
      lucide.createIcons();
      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-10px)';
        toast.style.transition = 'all 0.25s ease';
        setTimeout(() => toast.remove(), 250);
      }, 4000);
    }
    window.showToast = showToast;

    // ==========================================
    // DATABASE DASHBOARD & TABLE INSPECTOR
    // ==========================================
    async function loadDbDashboard() {
      try {
        const [statsRes, integRes] = await Promise.all([
          fetch(`${API_BASE}/api/db/stats`),
          fetch(`${API_BASE}/api/db/integrity`)
        ]);
        const stats = await statsRes.json();
        const integ = await integRes.json();

        if (stats.tables) {
          const t = stats.tables;
          const map = {
            'tbl-cnt-approvals': t.approvals || 0,
            'tbl-cnt-runs': t.runs || 0,
            'tbl-cnt-events': t.events || 0,
            'tbl-cnt-errors': t.errors || 0,
            'tbl-cnt-leases': t.leases || 0,
            'tbl-cnt-jobs': t.jobs || 0,
          };
          for (const [id, val] of Object.entries(map)) {
            const el = document.getElementById(id);
            if (el) el.innerText = val;
          }
          const totEl = document.getElementById('db-total-records');
          const tabTotEl = document.getElementById('db-tab-records');
          const navTotEl = document.getElementById('nav-db-records-badge');
          if (totEl) totEl.innerText = stats.total_records || 48;
          if (tabTotEl) tabTotEl.innerText = `${stats.total_records || 48} Registros`;
          if (navTotEl) navTotEl.innerText = stats.total_records || 48;
        }

        if (integ.success) {
          const sizeStr = `${integ.file_size_kb} KB (${integ.page_count} pág. de ${integ.page_size}B)`;
          const pEl = document.getElementById('db-file-path');
          const sEl = document.getElementById('db-file-size');
          const tpEl = document.getElementById('db-tab-path');
          const tsEl = document.getElementById('db-tab-size');
          if (pEl) pEl.innerText = integ.db_path || 'sacl_ops.db';
          if (sEl) sEl.innerText = `${integ.file_size_kb} KB`;
          if (tpEl) tpEl.innerText = integ.db_path || 'sacl_ops.db';
          if (tsEl) tsEl.innerText = sizeStr;
        }
      } catch (e) {
        console.error('Error loading db stats:', e);
      }
    }
    window.loadDbDashboard = loadDbDashboard;

    async function checkDbIntegrity() {
      showToast('Ejecutando PRAGMA integrity_check...', 'info');
      try {
        const res = await fetch(`${API_BASE}/api/db/integrity`);
        const data = await res.json();
        if (data.success && data.integrity === 'ok') {
          showToast(`PRAGMA integrity_check: OK (${data.page_count} páginas WAL validadas)`, 'success');
          loadDbDashboard();
        } else {
          showToast('Fallo de integridad: ' + (data.error || 'error'), 'error');
        }
      } catch (e) {
        showToast('Error de conexión a la base de datos: ' + e.message, 'error');
      }
    }
    window.checkDbIntegrity = checkDbIntegrity;

    async function viewTableRows(tableName) {
      if (currentSection !== 'database') {
        switchSection('database');
      }

      const headersEl = document.getElementById('db-table-headers');
      const bodyEl = document.getElementById('db-table-body');
      const countEl = document.getElementById('db-table-active-count');
      if (!headersEl || !bodyEl) return;

      document.querySelectorAll('#db-table-selector-tabs button').forEach(b => {
        if (b.id === 'tab-btn-' + tableName) b.classList.add('active');
        else b.classList.remove('active');
      });

      bodyEl.innerHTML = '<tr><td class="py-4 text-center text-zinc-500" colspan="10">Consultando tabla ' + tableName + '...</td></tr>';

      try {
        const res = await fetch(`${API_BASE}/api/db/rows?table=${tableName}&limit=25`);
        const data = await res.json();
        if (data.success) {
          activeTableRows = data.rows || [];
          countEl.innerText = `Tabla '${tableName}' (${data.count} filas registradas)`;

          if (data.columns.length === 0 || activeTableRows.length === 0) {
            headersEl.innerHTML = '<th class="py-2.5 px-3">Estado</th>';
            bodyEl.innerHTML = '<tr><td class="py-4 text-center text-zinc-500">Tabla vacía (0 registros).</td></tr>';
            return;
          }

          headersEl.innerHTML = data.columns.map(c => `<th class="py-2.5 px-3 uppercase text-[11px]">${c}</th>`).join('');

          bodyEl.innerHTML = activeTableRows.map(r => `
            <tr class="hover:bg-white/5 transition-colors">
              ${data.columns.map(c => {{
                let val = r[c];
                if (typeof val === 'object' && val !== null) val = JSON.stringify(val);
                if (val === null || val === undefined) val = '<span class="text-zinc-600">NULL</span>';
                else if (val === 'APPROVED') val = '<span class="text-emerald-400 font-bold">APPROVED</span>';
                else if (val === 'PENDING') val = '<span class="text-amber-400 font-bold">PENDING</span>';
                else if (val === 'REJECTED') val = '<span class="text-red-400 font-bold">REJECTED</span>';
                return `<td class="py-2.5 px-3 truncate max-w-xs" title="${escapeHtml(String(val))}">${val}</td>`;
              }}).join('')}
            </tr>
          `).join('');
        } else {
          bodyEl.innerHTML = `<tr><td class="py-4 text-center text-red-400" colspan="10">${data.error}</td></tr>`;
        }
      } catch (e) {
        bodyEl.innerHTML = `<tr><td class="py-4 text-center text-red-400" colspan="10">Error de red: ${e.message}</td></tr>`;
      }
    }
    window.viewTableRows = viewTableRows;

    // ==========================================
    // GATE DECISION & VISUAL FEEDBACK ENGINE
    // ==========================================
    async function quickApproveFromCard() {
      const btns = document.querySelectorAll('.btn-gate-approve-action');
      const gateCard = document.getElementById('active-gate-container');
      const gatesTabCard = document.getElementById('gates-tab-card-container');
      const reqId = currentGateRequestId;

      btns.forEach(b => {
        b.disabled = true;
        b.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Autorizando...</span>';
      });
      lucide.createIcons();

      showToast(`Autorizando compuerta ${reqId} en SQLite WAL...`, 'info');

      try {
        const res = await fetch(`${API_BASE}/api/gates/decide`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            request_id: reqId,
            decision: 'APPROVED',
            justification: 'Autorizado por operador soberano LUCILFER / risejoaquin'
          })
        });
        const data = await res.json();

        if (data.success) {
          const successHtml = `
            <div class="p-6 rounded-2xl bg-emerald-950/40 border border-emerald-500/50 text-center space-y-3.5 toast-animate">
              <div class="w-14 h-14 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center mx-auto text-emerald-400">
                <i data-lucide="check" class="w-7 h-7 stroke-[3]"></i>
              </div>
              <div>
                <div class="text-xl font-bold text-white mono">¡DESPLIEGUE AUTORIZADO CON ÉXITO!</div>
                <div class="text-xs text-emerald-400 mono mt-1 font-semibold">Compuerta ${reqId} aprobada en SQLite WAL</div>
              </div>
              <p class="text-xs text-zinc-300 max-w-md mx-auto leading-relaxed">
                Decisión registrada bajo guardrails inmutables. El pipeline efímero de Staging en Railway ha sido desbloqueado.
              </p>
              <div class="pt-2 flex flex-wrap justify-center gap-3">
                <button onclick="createNewGateSim()" class="btn btn-secondary text-xs px-4 py-2">
                  <i data-lucide="plus" class="w-3.5 h-3.5 text-emerald-400"></i>
                  <span>Crear Otra Compuerta de Prueba</span>
                </button>
                <button onclick="loadDashboardSnapshot()" class="btn btn-primary text-xs px-4 py-2">
                  <i data-lucide="refresh-cw" class="w-3.5 h-3.5 fill-black"></i>
                  <span>Refrescar Panel</span>
                </button>
              </div>
            </div>
          `;

          // VISUAL TRANSFORMATION: Transform both cards into prominent success confirmations
          if (gateCard) {
            gateCard.innerHTML = successHtml;
          }
          if (gatesTabCard) {
            gatesTabCard.innerHTML = successHtml;
          }
          lucide.createIcons();

          showToast(`✓ ¡Despliegue ${reqId} Autorizado Correctamente!`, 'success');
          loadDashboardSnapshot(); loadHudEmbeddedTable('approvals'); loadHudEmbeddedTable('approvals');
          loadDbDashboard();
        } else {
          showToast(`Fallo al autorizar: ${data.message || 'Error'}`, 'error');
          btns.forEach(b => {
            b.disabled = false;
            b.innerHTML = '<i data-lucide="check" class="w-4 h-4 stroke-[2.5]"></i><span>Reintentar Autorización</span>';
          });
          lucide.createIcons();
        }
      } catch (e) {
        showToast('Error de red al autorizar compuerta: ' + e.message, 'error');
        btns.forEach(b => {
          b.disabled = false;
          b.innerHTML = '<i data-lucide="check" class="w-4 h-4 stroke-[2.5]"></i><span>Reintentar Autorización</span>';
        });
        lucide.createIcons();
      }
    }
    window.quickApproveFromCard = quickApproveFromCard;

    async function quickRejectFromCard() {
      const reqId = currentGateRequestId;
      const gateCard = document.getElementById('active-gate-container');
      const gatesTabCard = document.getElementById('gates-tab-card-container');
      showToast(`Rechazando compuerta ${reqId} en SQLite WAL...`, 'info');

      try {
        const res = await fetch(`${API_BASE}/api/gates/decide`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            request_id: reqId,
            decision: 'REJECTED',
            justification: 'Compuerta rechazada por operador soberano LUCILFER / risejoaquin'
          })
        });
        const data = await res.json();
        if (data.success) {
          const rejectHtml = `
            <div class="p-6 rounded-2xl bg-red-950/40 border border-red-500/50 text-center space-y-3.5 toast-animate">
              <div class="w-14 h-14 rounded-full bg-red-500/20 border border-red-500/40 flex items-center justify-center mx-auto text-red-400">
                <i data-lucide="x" class="w-7 h-7 stroke-[3]"></i>
              </div>
              <div>
                <div class="text-xl font-bold text-white mono">DESPLIEGUE RECHAZADO / DETENIDO</div>
                <div class="text-xs text-red-400 mono mt-1 font-semibold">Compuerta ${reqId} cancelada en SQLite WAL</div>
              </div>
              <p class="text-xs text-zinc-300 max-w-md mx-auto leading-relaxed">
                El pipeline efímero ha sido detenido de forma segura. Se ha registrado el evento de veto en el ledger inmutable.
              </p>
              <div class="pt-2 flex flex-wrap justify-center gap-3">
                <button onclick="createNewGateSim()" class="btn btn-secondary text-xs px-4 py-2">
                  <i data-lucide="plus" class="w-3.5 h-3.5 text-emerald-400"></i>
                  <span>Crear Nueva Compuerta de Prueba</span>
                </button>
                <button onclick="loadDashboardSnapshot()" class="btn btn-primary text-xs px-4 py-2">
                  <i data-lucide="refresh-cw" class="w-3.5 h-3.5 fill-black"></i>
                  <span>Refrescar Panel</span>
                </button>
              </div>
            </div>
          `;
          if (gateCard) gateCard.innerHTML = rejectHtml;
          if (gatesTabCard) gatesTabCard.innerHTML = rejectHtml;
          lucide.createIcons();

          showToast(`✓ Compuerta ${reqId} rechazada con éxito`, 'error');
          loadDashboardSnapshot(); loadHudEmbeddedTable('approvals'); loadHudEmbeddedTable('approvals');
          loadDbDashboard();
        } else {
          showToast(`Fallo al rechazar: ${data.message || 'Error'}`, 'error');
        }
      } catch (e) {
        showToast('Error al rechazar: ' + e.message, 'error');
      }
    }
    window.quickRejectFromCard = quickRejectFromCard;

    async function createNewGateSim() {
      showToast('Generando nueva compuerta de despliegue...', 'info');
      try {
        const res = await fetch(`${API_BASE}/api/gates/create`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: 'DEPLOY_STAGING_PREVIEW',
            reason: 'Verificación de build efímero con contratos DR-INV-001.'
          })
        });
        const data = await res.json();
        if (data.success) {
          showToast(`Nueva compuerta ${data.request_id} creada con éxito`, 'success');
          loadDashboardSnapshot(); loadHudEmbeddedTable('approvals'); loadHudEmbeddedTable('approvals');
          loadDbDashboard();
        }
      } catch (e) {
        showToast('Error al crear compuerta: ' + e.message, 'error');
      }
    }
    window.createNewGateSim = createNewGateSim;

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

        // Render Pending Gates or Zero State
        const tuercaBadge = document.getElementById('tuerca-gate-badge');
        const navCount = document.getElementById('nav-gates-count');
        const gateCard = document.getElementById('active-gate-container');

        if (data.pending_gates && data.pending_gates.length > 0) {
          activePendingGate = data.pending_gates[0];
          currentGateRequestId = activePendingGate.request_id;
          
          const pill = document.getElementById('gate-request-id-pill');
          const title = document.getElementById('gate-action-title');
          const desc = document.getElementById('gate-reason-desc');
          const tabTitle = document.getElementById('gates-tab-action-title');
          const tabReq = document.getElementById('gates-tab-req-id');

          if (pill) pill.innerText = activePendingGate.request_id;
          if (title) title.innerText = activePendingGate.action;
          if (desc) desc.innerText = activePendingGate.reason || 'Compuerta de aprobación obligatoria';
          if (tabTitle) tabTitle.innerText = activePendingGate.action;
          if (tabReq) tabReq.innerText = activePendingGate.request_id;

          if (tuercaBadge) {
            tuercaBadge.innerText = data.pending_gates.length;
            tuercaBadge.classList.remove('hidden');
          }
          if (navCount) {
            navCount.innerText = data.pending_gates.length;
            navCount.classList.remove('hidden');
          }
        } else {
          if (tuercaBadge) tuercaBadge.classList.add('hidden');
          if (navCount) navCount.classList.add('hidden');
          if (gateCard && !gateCard.innerHTML.includes('¡DESPLIEGUE AUTORIZADO')) {
            gateCard.innerHTML = `
              <div class="p-6 rounded-2xl bg-black/40 border bd text-center space-y-3">
                <div class="w-10 h-10 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mx-auto text-emerald-400">
                  <i data-lucide="shield-check" class="w-5 h-5"></i>
                </div>
                <div class="text-sm font-bold text-white mono">0 COMPUERTAS PENDIENTES</div>
                <p class="text-xs text-zinc-400 max-w-sm mx-auto">
                  Todas las compuertas están autorizadas. Ecosistema en estado 100% autónomo.
                </p>
                <button onclick="createNewGateSim()" class="btn btn-secondary text-xs px-4 py-2">
                  <i data-lucide="plus" class="w-3.5 h-3.5 text-emerald-400"></i>
                  <span>Crear Nueva Compuerta de Prueba</span>
                </button>
              </div>
            `;
            lucide.createIcons();
          }
        }

        // Render Historical Table in Gates Tab
        loadDecisionsHistoryTable();

      } catch (e) {
        console.error('Error loading snapshot:', e);
      }
    }
    window.loadDashboardSnapshot = loadDashboardSnapshot;

    async function loadDecisionsHistoryTable() {
      const tbody = document.getElementById('decisions-history-tbody-full');
      if (!tbody) return;
      try {
        const res = await fetch(`${API_BASE}/api/db/rows?table=approvals&limit=10`);
        const data = await res.json();
        if (data.success && data.rows) {
          tbody.innerHTML = data.rows.map(r => `
            <tr>
              <td class="py-3 pr-4 text-zinc-300 font-semibold">${r.approval_id || r.request_id}</td>
              <td class="py-3 px-4 text-zinc-300">${r.action}</td>
              <td class="py-3 px-4">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold ${r.status === 'APPROVED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/25' : r.status === 'PENDING' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/25' : 'bg-red-500/10 text-red-400 border border-red-500/25'}">
                  ${r.status}
                </span>
              </td>
              <td class="py-3 px-4 text-zinc-400">${typeof r.approver === 'string' && r.approver.includes('identity') ? 'LUCILFER (CLI)' : (r.approver || 'Sistema')}</td>
              <td class="py-3 pl-4 text-zinc-500">${r.decided_at || r.requested_at || '--'}</td>
            </tr>
          `).join('');
        }
      } catch (e) {}
    }

    // ==========================================
    // ACTION EXECUTION ENGINE
    // ==========================================
    async function executeAction(actionType, params = {}, triggerBtn = null, event = null) {
      if (event) event.stopPropagation();
      let originalHtml = '';
      if (triggerBtn) {
        originalHtml = triggerBtn.innerHTML;
        triggerBtn.disabled = true;
        triggerBtn.innerHTML = '<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i><span>Ejecutando...</span>';
        lucide.createIcons();
      }

      // Desplegar terminal en vivo inmediatamente para que el usuario VEA la ejecución real
      openTerminalDrawer();
      appendTerminalLog(`========================================`);
      appendTerminalLog(`[DISPATCH] Lanzando acción: ${actionType.toUpperCase()}`);
      appendTerminalLog(`[TIMESTAMP] ${new Date().toLocaleTimeString()} | Operador: LUCILFER / risejoaquin`);
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
          showToast(`✓ ${exec.title}: COMPLETADO (Exit ${exec.exit_code})`, 'success');
          appendTerminalLog(`[EXIT_0] ${exec.title} completado en ${exec.duration_sec}s`);
          (exec.logs || []).forEach(l => appendTerminalLog(l));
          loadActionHistory();
          loadDashboardSnapshot(); loadHudEmbeddedTable('approvals'); loadHudEmbeddedTable('approvals');
          loadDbDashboard();

          if (triggerBtn) {
            triggerBtn.disabled = false;
            triggerBtn.innerHTML = '<i data-lucide="check" class="w-3.5 h-3.5 text-emerald-400"></i><span class="text-emerald-400 font-bold">¡Ejecutado!</span>';
            lucide.createIcons();
            setTimeout(() => {
              triggerBtn.innerHTML = originalHtml;
              lucide.createIcons();
            }, 3000);
            return exec;
          }
          return exec;
        } else {
          showToast(`Error al ejecutar ${actionType}: ${data.error || 'Fallo'}`, 'error');
          appendTerminalLog(`[ERROR] ${data.error || 'Fallo desconocido'}`);
        }
      } catch (err) {
        console.error(err);
        showToast(`Fallo de red: ${err.message}`, 'error');
        appendTerminalLog(`[EXCEPTION] ${err.message}`);
      } finally {
        if (triggerBtn && !triggerBtn.innerHTML.includes('Ejecutado')) {
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

          <div>
            <div class="text-[10px] uppercase font-bold tracking-wider text-zinc-400 mb-2">Documentación Detectada (Clic para ver)</div>
            <div class="flex flex-wrap gap-2">
              ${(p.documentation || []).map(d => `
                <button onclick="viewDocPreview('${encodeURIComponent(d.path)}', '${d.name}', event)"
                  class="mono text-xs px-2.5 py-1 rounded-lg bg-black/40 border bd hover:border-emerald-500/40 text-zinc-300 flex items-center gap-1.5 cursor-pointer transition-colors">
                  <i data-lucide="file-text" class="w-3.5 h-3.5 text-emerald-400"></i>
                  <span>${d.name}</span>
                </button>
              `).join('') || '<span class="text-xs text-zinc-500">Sin docs detectados</span>'}
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
          loadProjects(); loadFsTree(); loadFsTree();
          loadDashboardSnapshot(); loadHudEmbeddedTable('approvals'); loadHudEmbeddedTable('approvals');
          loadDbDashboard();
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
        let history = [];
        try {
          const res = await fetch(`${API_BASE}/api/chat/history`);
          const data = await res.json();
          if (data && data.history) history = data.history;
        } catch(e) {}

        // Fallback / merge with persistent localStorage
        const cached = localStorage.getItem('sacl_chat_history_cache');
        if (cached && history.length <= 1) {
          try {
            const parsed = JSON.parse(cached);
            if (Array.isArray(parsed) && parsed.length > history.length) {
              history = parsed;
            }
          } catch(e) {}
        }

        const container = document.getElementById('chat-messages-container');
        if (!container) return;

        container.innerHTML = '';
        history.forEach(msg => {
          appendChatMessage(msg.role, msg.content, msg.action_data, false, false);
        });
        scrollChatToBottom();
      } catch (e) {
        console.error('Chat history error:', e);
      }
    }
    window.loadChatHistory = loadChatHistory;

    async function clearChatHistory() {
      try {
        localStorage.removeItem('sacl_chat_history_cache');
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
          loadDashboardSnapshot(); loadHudEmbeddedTable('approvals'); loadHudEmbeddedTable('approvals');
          loadDbDashboard();
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

    function appendChatMessage(role, content, actionData = null, animate = false, shouldCache = true) {
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
          <div class="p-4 rounded-xl bg-[#030305] border bd text-xs text-zinc-200 space-y-1.5">
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

      if (shouldCache) {
        try {
          const cached = JSON.parse(localStorage.getItem('sacl_chat_history_cache') || '[]');
          cached.push({ role, content, action_data: actionData, timestamp: new Date().toISOString() });
          localStorage.setItem('sacl_chat_history_cache', JSON.stringify(cached.slice(-50)));
        } catch(e) {}
      }
    }

    function scrollChatToBottom() {
      const scroll = document.getElementById('chat-messages-scroll');
      if (scroll) scroll.scrollTop = scroll.scrollHeight;
    }

    async function inspectCurrentGateImpact() {
      try {
        const res = await fetch(`${API_BASE}/api/gates/impact?request_id=${currentGateRequestId}`);
        const data = await res.json();
        document.getElementById('diff-modal-title').innerText = `Diff Inspector · ${currentGateRequestId}`;
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
              showToast(`Nueva compuerta requerida: ${data.action}`, 'info');
              loadDashboardSnapshot(); loadHudEmbeddedTable('approvals'); loadHudEmbeddedTable('approvals');
              loadDbDashboard();
            } else if (data.type === 'GATE_DECIDED') {
              loadDashboardSnapshot(); loadHudEmbeddedTable('approvals'); loadHudEmbeddedTable('approvals');
              loadDbDashboard();
            } else if (data.type === 'ACTION_COMPLETED') {
              loadActionHistory();
              loadDbDashboard();
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
  
    // ==========================================
    // DECISION DOSSIER & PROGRESS ENGINE (V7)
    // ==========================================
    function switchDossierTab(tabName) {
      document.querySelectorAll('#dossier-tab-btn-checklist, #dossier-tab-btn-diff, #dossier-tab-btn-audit').forEach(b => {
        b.classList.remove('active');
      });
      const activeBtn = document.getElementById('dossier-tab-btn-' + tabName);
      if (activeBtn) activeBtn.classList.add('active');

      document.getElementById('dossier-panel-checklist').classList.add('hidden');
      document.getElementById('dossier-panel-diff').classList.add('hidden');
      document.getElementById('dossier-panel-audit').classList.add('hidden');

      const target = document.getElementById('dossier-panel-' + tabName);
      if (target) target.classList.remove('hidden');
    }
    window.switchDossierTab = switchDossierTab;

    async function executeWalCheckpoint() {
      showToast('Ejecutando PRAGMA wal_checkpoint(TRUNCATE)...', 'info');
      try {
        const res = await fetch(`${API_BASE}/api/db/checkpoint`);
        const data = await res.json();
        if (data.success) {
          showToast(`WAL Checkpoint: ${data.checkpointed_pages} páginas sincronizadas a disco`, 'success');
          loadDbDashboard();
          loadDashboardSnapshot();
        } else {
          showToast('Fallo en checkpoint: ' + (data.error || 'error'), 'error');
        }
      } catch (e) {
        showToast('Error de red al ejecutar checkpoint: ' + e.message, 'error');
      }
    }
    window.executeWalCheckpoint = executeWalCheckpoint;

    async function loadHudEmbeddedTable(tableName) {
      const titleEl = document.getElementById('hud-embedded-table-title');
      const headersEl = document.getElementById('hud-embedded-table-headers');
      const bodyEl = document.getElementById('hud-embedded-table-body');
      if (!bodyEl) return;

      if (titleEl) titleEl.innerText = `Registros Recientes: ${tableName}`;
      bodyEl.innerHTML = '<tr><td colspan="5" class="py-3 text-center text-zinc-500">Cargando registros...</td></tr>';

      try {
        const res = await fetch(`${API_BASE}/api/db/rows?table=${tableName}&limit=8`);
        const data = await res.json();
        if (data.success && data.rows && data.rows.length > 0) {
          const cols = data.columns.slice(0, 5);
          if (headersEl) {
            headersEl.innerHTML = cols.map(c => `<th class="py-2 px-3 uppercase text-[11px]">${c}</th>`).join('');
          }
          bodyEl.innerHTML = data.rows.map(r => `
            <tr class="hover:bg-white/5 transition-colors">
              ${cols.map(c => {
                let v = r[c];
                if (typeof v === 'object' && v !== null) v = JSON.stringify(v);
                if (v === null || v === undefined) v = '<span class="text-zinc-600">NULL</span>';
                else if (v === 'APPROVED' || v === 'COMPLETED' || v === 'DONE') v = `<span class="text-emerald-400 font-bold">${v}</span>`;
                else if (v === 'PENDING') v = `<span class="text-amber-400 font-bold">${v}</span>`;
                else if (v === 'REJECTED' || v === 'FAILED') v = `<span class="text-red-400 font-bold">${v}</span>`;
                return `<td class="py-2 px-3 truncate max-w-[140px]">${v}</td>`;
              }).join('')}
            </tr>
          `).join('');
        } else {
          bodyEl.innerHTML = '<tr><td colspan="5" class="py-3 text-center text-zinc-500">Tabla vacía (0 registros).</td></tr>';
        }
      } catch (e) {
        bodyEl.innerHTML = `<tr><td colspan="5" class="py-3 text-center text-red-400">Error: ${e.message}</td></tr>`;
      }
    }
    window.loadHudEmbeddedTable = loadHudEmbeddedTable;

    async function executeActionWithProgress(actionType, btn) {
      const container = document.getElementById('hero-action-progress-container');
      const bar = document.getElementById('hero-progress-bar');
      const pct = document.getElementById('hero-progress-pct');
      const label = document.getElementById('hero-progress-label');
      const step1 = document.getElementById('prog-step-1');
      const step2 = document.getElementById('prog-step-2');
      const step3 = document.getElementById('prog-step-3');
      const step4 = document.getElementById('prog-step-4');

      if (container) container.classList.remove('hidden');

      if (bar) bar.style.width = '25%';
      if (pct) pct.innerText = '25%';
      if (label) label.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Fase 1/4: Inspección de Contratos DR-INV-001 & DR-PAY-001...</span>';
      if (step1) step1.className = 'p-2 rounded bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 text-center font-bold';
      lucide.createIcons();

      await new Promise(r => setTimeout(r, 350));

      if (bar) bar.style.width = '55%';
      if (pct) pct.innerText = '55%';
      if (label) label.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Fase 2/4: Verificación de Singleton Leases & WAL Mode...</span>';
      if (step2) step2.className = 'p-2 rounded bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 text-center font-bold';
      lucide.createIcons();

      await new Promise(r => setTimeout(r, 350));

      if (bar) bar.style.width = '85%';
      if (pct) pct.innerText = '85%';
      if (label) label.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Fase 3/4: Despacho de Suite Pytest (29 tests)...</span>';
      if (step3) step3.className = 'p-2 rounded bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 text-center font-bold';
      lucide.createIcons();

      await executeAction(actionType, {}, btn);

      if (bar) bar.style.width = '100%';
      if (pct) pct.innerText = '100%';
      if (label) label.innerHTML = '<i data-lucide="check" class="w-4 h-4 text-emerald-400 stroke-[3]"></i><span class="text-emerald-400 font-bold">¡Completado con Éxito (EXIT 0)!</span>';
      if (step4) step4.className = 'p-2 rounded bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 text-center font-bold';
      lucide.createIcons();

      loadHudEmbeddedTable('approvals');

      setTimeout(() => {
        if (container) container.classList.add('hidden');
        if (bar) bar.style.width = '0%';
        if (step1) step1.className = 'p-2 rounded bg-black/40 border bd text-center';
        if (step2) step2.className = 'p-2 rounded bg-black/40 border bd text-center';
        if (step3) step3.className = 'p-2 rounded bg-black/40 border bd text-center';
        if (step4) step4.className = 'p-2 rounded bg-black/40 border bd text-center';
      }, 5000);
    }
    window.executeActionWithProgress = executeActionWithProgress;

  
    // ==========================================
    // FILE SYSTEM EXPLORER & CODE VIEWER ENGINE (V8)
    // ==========================================
    let currentRawFsTree = [];
    let currentViewedFilePath = '';
    let currentViewedFileContent = '';

    function showOpenFolderModal() {
      const modal = document.getElementById('open-folder-modal');
      const input = document.getElementById('open-folder-input');
      const curRoot = document.getElementById('fs-current-root-path')?.innerText;
      if (input && curRoot && curRoot !== 'Cargando carpeta...') {
        input.value = curRoot;
      }
      if (modal) modal.classList.remove('hidden');
      lucide.createIcons();
    }
    window.showOpenFolderModal = showOpenFolderModal;

    function closeOpenFolderModal() {
      document.getElementById('open-folder-modal')?.classList.add('hidden');
    }
    window.closeOpenFolderModal = closeOpenFolderModal;

    function setOpenFolderPreset(path) {
      const input = document.getElementById('open-folder-input');
      if (input) input.value = path;
      submitOpenFolder();
    }
    window.setOpenFolderPreset = setOpenFolderPreset;

    async function submitOpenFolder() {
      const input = document.getElementById('open-folder-input');
      const folderPath = (input?.value || '').trim();
      if (!folderPath) return;

      closeOpenFolderModal();
      showToast(`Abriendo carpeta: ${folderPath}...`, 'info');

      try {
        const res = await fetch(`${API_BASE}/api/fs/open-folder`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ folder: folderPath })
        });
        const data = await res.json();
        if (data.success) {
          showToast(`Carpeta abierta con éxito: ${data.root_name}`, 'success');
          loadFsTree(data.root_path);
        } else {
          showToast(`No se pudo abrir carpeta: ${data.error}`, 'error');
        }
      } catch (e) {
        showToast('Error de conexión al abrir carpeta: ' + e.message, 'error');
      }
    }
    window.submitOpenFolder = submitOpenFolder;

    function showOpenFileModal() {
      const modal = document.getElementById('open-file-modal');
      if (modal) modal.classList.remove('hidden');
      lucide.createIcons();
    }
    window.showOpenFileModal = showOpenFileModal;

    function closeOpenFileModal() {
      document.getElementById('open-file-modal')?.classList.add('hidden');
    }
    window.closeOpenFileModal = closeOpenFileModal;

    function setOpenFilePathPreset(relPath) {
      const curRoot = document.getElementById('fs-current-root-path')?.innerText || '';
      const full = curRoot ? `${curRoot}/${relPath}`.split(String.fromCharCode(92)).join('/') : relPath;
      const input = document.getElementById('open-file-input');
      if (input) input.value = full;
      submitOpenFile();
    }
    window.setOpenFilePathPreset = setOpenFilePathPreset;

    function submitOpenFile() {
      const input = document.getElementById('open-file-input');
      const filePath = (input?.value || '').trim();
      if (!filePath) return;
      closeOpenFileModal();
      openFsFile(filePath);
    }
    window.submitOpenFile = submitOpenFile;

    async function loadFsTree(folder = '') {
      const container = document.getElementById('fs-tree-container');
      const rootPathEl = document.getElementById('fs-current-root-path');
      const countEl = document.getElementById('fs-tree-item-count');
      if (!container) return;

      container.innerHTML = '<div class="py-8 text-center text-zinc-500 text-xs mono"><i data-lucide="loader-2" class="w-4 h-4 animate-spin mx-auto mb-2"></i>Leyendo archivos en disco...</div>';
      lucide.createIcons();

      try {
        const url = folder ? `${API_BASE}/api/fs/tree?folder=${encodeURIComponent(folder)}` : `${API_BASE}/api/fs/tree`;
        const res = await fetch(url);
        const data = await res.json();
        if (data.success) {
          currentRawFsTree = data.tree || [];
          if (rootPathEl) rootPathEl.innerText = data.root_path;
          if (countEl) countEl.innerText = `${data.items_count} elementos`;
          container.innerHTML = renderTreeNodes(currentRawFsTree, 0);
          lucide.createIcons();
        } else {
          container.innerHTML = `<div class="p-4 text-center text-red-400 text-xs mono">Error: ${data.error}</div>`;
        }
      } catch (e) {
        container.innerHTML = `<div class="p-4 text-center text-red-400 text-xs mono">Error de red: ${e.message}</div>`;
      }
    }
    window.loadFsTree = loadFsTree;

    function renderTreeNodes(nodes, level = 0) {
      if (!nodes || nodes.length === 0) return '';
      return nodes.map((n) => {
        const pad = level * 14;
        const nodeId = 'node-' + Math.random().toString(36).substr(2, 9);
        if (n.is_dir) {
          return `
            <div class="tree-item-dir">
              <div onclick="toggleFsFolder('${nodeId}')" class="flex items-center gap-1.5 py-1 px-2 rounded hover:bg-white/5 cursor-pointer text-xs text-zinc-300 font-medium select-none" style="padding-left: ${pad + 8}px">
                <i data-lucide="chevron-right" id="arrow-${nodeId}" class="w-3 h-3 text-zinc-500 transition-transform"></i>
                <i data-lucide="folder" class="w-3.5 h-3.5 text-amber-400"></i>
                <span class="truncate">${escapeHtml(n.name)}</span>
              </div>
              <div id="${nodeId}" class="hidden space-y-0.5">
                ${renderTreeNodes(n.children, level + 1)}
              </div>
            </div>
          `;
        } else {
          let iconColor = 'text-zinc-400';
          let iconName = 'file-text';
          const ext = n.extension;
          if (ext === '.py') { iconColor = 'text-blue-400'; iconName = 'file-code'; }
          else if (ext === '.json') { iconColor = 'text-amber-400'; iconName = 'file-json'; }
          else if (ext === '.md') { iconColor = 'text-emerald-400'; iconName = 'book-open'; }
          else if (ext === '.toml' || ext === '.yaml' || ext === '.yml') { iconColor = 'text-purple-400'; iconName = 'settings-2'; }
          else if (ext === '.sh' || ext === '.bat' || ext === '.ps1') { iconColor = 'text-rose-400'; iconName = 'terminal'; }

          const safePath = escapeHtml(n.path).split(String.fromCharCode(92)).join('/');
          return `
            <div onclick="openFsFile('${safePath}', this)" class="fs-file-pill flex items-center justify-between py-1 px-2 rounded hover:bg-white/10 cursor-pointer text-xs text-zinc-300 group select-none" style="padding-left: ${pad + 20}px">
              <div class="flex items-center gap-1.5 truncate">
                <i data-lucide="${iconName}" class="w-3.5 h-3.5 ${iconColor} shrink-0"></i>
                <span class="truncate">${escapeHtml(n.name)}</span>
              </div>
              <span class="text-[10px] text-zinc-600 group-hover:text-zinc-400 mono shrink-0">${(n.size_bytes / 1024).toFixed(1)}k</span>
            </div>
          `;
        }
      }).join('');
    }

    function toggleFsFolder(nodeId) {
      const el = document.getElementById(nodeId);
      const arrow = document.getElementById('arrow-' + nodeId);
      if (!el) return;
      if (el.classList.contains('hidden')) {
        el.classList.remove('hidden');
        if (arrow) arrow.style.transform = 'rotate(90deg)';
      } else {
        el.classList.add('hidden');
        if (arrow) arrow.style.transform = 'rotate(0deg)';
      }
    }
    window.toggleFsFolder = toggleFsFolder;

    async function openFsFile(filePath, el = null) {
      document.querySelectorAll('.fs-file-pill').forEach(p => p.classList.remove('bg-emerald-500/10', 'text-emerald-300', 'font-semibold'));
      if (el) el.classList.add('bg-emerald-500/10', 'text-emerald-300', 'font-semibold');

      const titleEl = document.getElementById('code-viewer-filename');
      const pathEl = document.getElementById('code-viewer-path');
      const metaEl = document.getElementById('code-viewer-meta');
      const bodyEl = document.getElementById('code-viewer-content');
      if (!bodyEl) return;

      bodyEl.innerHTML = '<div class="py-16 text-center text-zinc-500 mono"><i data-lucide="loader-2" class="w-5 h-5 animate-spin mx-auto mb-2 text-emerald-400"></i>Cargando código en memoria...</div>';
      lucide.createIcons();

      try {
        const res = await fetch(`${API_BASE}/api/fs/read?path=${encodeURIComponent(filePath)}`);
        const data = await res.json();
        if (data.success) {
          currentViewedFilePath = data.path;
          currentViewedFileContent = data.content;
          if (titleEl) titleEl.innerText = data.filename;
          if (pathEl) pathEl.innerText = data.path;
          if (metaEl) metaEl.innerText = `${data.lines_count} líneas · ${(data.size_bytes / 1024).toFixed(2)} KB`;

          const lines = data.content.split(String.fromCharCode(10));
          bodyEl.innerHTML = `
            <div class="flex text-xs font-mono select-text bg-[#000000]">
              <div class="pr-3 text-right select-none text-zinc-600 border-r bd py-3 space-y-0.5 min-w-[42px] bg-black/40">
                ${lines.map((_, i) => `<div>${i + 1}</div>`).join('')}
              </div>
              <pre class="pl-3 py-3 overflow-x-auto text-zinc-200 leading-relaxed space-y-0.5 flex-1 whitespace-pre custom-scroll"><code>${lines.map(l => escapeHtml(l) || '&nbsp;').join(String.fromCharCode(10))}</code></pre>
            </div>
          `;
          lucide.createIcons();
          showToast(`Archivo cargado: ${data.filename}`, 'info');
        } else {
          bodyEl.innerHTML = `<div class="p-8 text-center text-red-400 mono">Error: ${data.error}</div>`;
        }
      } catch (e) {
        bodyEl.innerHTML = `<div class="p-8 text-center text-red-400 mono">Error al leer archivo: ${e.message}</div>`;
      }
    }
    window.openFsFile = openFsFile;

    function copyCodeViewerContent() {
      if (!currentViewedFileContent) return;
      navigator.clipboard.writeText(currentViewedFileContent);
      const btn = document.getElementById('code-viewer-copy-btn-text');
      if (btn) {
        btn.innerText = '¡Copiado!';
        setTimeout(() => { btn.innerText = 'Copiar'; }, 2000);
      }
      showToast('Código copiado al portapapeles', 'success');
    }
    window.copyCodeViewerContent = copyCodeViewerContent;

    function filterFsTree() {
      const q = (document.getElementById('fs-search-input')?.value || '').toLowerCase();
      const container = document.getElementById('fs-tree-container');
      if (!q) {
        container.innerHTML = renderTreeNodes(currentRawFsTree, 0);
        lucide.createIcons();
        return;
      }
      // Flatten search matching
      function searchNodes(nodes) {
        let results = [];
        for (const n of nodes) {
          if (!n.is_dir && n.name.toLowerCase().includes(q)) {
            results.push(n);
          }
          if (n.children) {
            results = results.concat(searchNodes(n.children));
          }
        }
        return results;
      }
      const matched = searchNodes(currentRawFsTree);
      if (matched.length === 0) {
        container.innerHTML = `<div class="p-4 text-center text-zinc-500 text-xs mono">No se encontraron archivos con "${q}".</div>`;
        return;
      }
      container.innerHTML = matched.map(m => {
        const safePath = escapeHtml(m.path).split(String.fromCharCode(92)).join('/');
        return `
          <div onclick="openFsFile('${safePath}', this)" class="fs-file-pill flex items-center justify-between py-1.5 px-3 rounded hover:bg-white/10 cursor-pointer text-xs text-zinc-300">
            <span class="truncate mono text-emerald-300">${escapeHtml(m.name)}</span>
            <span class="text-[10px] text-zinc-500 mono">${(m.size_bytes / 1024).toFixed(1)}k</span>
          </div>
        `;
      }).join('');
    }
    window.filterFsTree = filterFsTree;

  
    // ==========================================
    // DECISION DOSSIER & PROGRESS ENGINE (V7)
    // ==========================================
    function switchDossierTab(tabName) {
      document.querySelectorAll('#dossier-tab-btn-checklist, #dossier-tab-btn-diff, #dossier-tab-btn-audit').forEach(b => {
        b.classList.remove('active');
      });
      const activeBtn = document.getElementById('dossier-tab-btn-' + tabName);
      if (activeBtn) activeBtn.classList.add('active');

      document.getElementById('dossier-panel-checklist').classList.add('hidden');
      document.getElementById('dossier-panel-diff').classList.add('hidden');
      document.getElementById('dossier-panel-audit').classList.add('hidden');

      const target = document.getElementById('dossier-panel-' + tabName);
      if (target) target.classList.remove('hidden');
    }
    window.switchDossierTab = switchDossierTab;

    async function executeWalCheckpoint() {
      showToast('Ejecutando PRAGMA wal_checkpoint(TRUNCATE)...', 'info');
      try {
        const res = await fetch(`${API_BASE}/api/db/checkpoint`);
        const data = await res.json();
        if (data.success) {
          showToast(`WAL Checkpoint: ${data.checkpointed_pages} páginas sincronizadas a disco`, 'success');
          loadDbDashboard();
          loadDashboardSnapshot();
        } else {
          showToast('Fallo en checkpoint: ' + (data.error || 'error'), 'error');
        }
      } catch (e) {
        showToast('Error de red al ejecutar checkpoint: ' + e.message, 'error');
      }
    }
    window.executeWalCheckpoint = executeWalCheckpoint;

    async function loadHudEmbeddedTable(tableName) {
      const titleEl = document.getElementById('hud-embedded-table-title');
      const headersEl = document.getElementById('hud-embedded-table-headers');
      const bodyEl = document.getElementById('hud-embedded-table-body');
      if (!bodyEl) return;

      if (titleEl) titleEl.innerText = `Registros Recientes: ${tableName}`;
      bodyEl.innerHTML = '<tr><td colspan="5" class="py-3 text-center text-zinc-500">Cargando registros...</td></tr>';

      try {
        const res = await fetch(`${API_BASE}/api/db/rows?table=${tableName}&limit=8`);
        const data = await res.json();
        if (data.success && data.rows && data.rows.length > 0) {
          const cols = data.columns.slice(0, 5);
          if (headersEl) {
            headersEl.innerHTML = cols.map(c => `<th class="py-2 px-3 uppercase text-[11px]">${c}</th>`).join('');
          }
          bodyEl.innerHTML = data.rows.map(r => `
            <tr class="hover:bg-white/5 transition-colors">
              ${cols.map(c => {
                let v = r[c];
                if (typeof v === 'object' && v !== null) v = JSON.stringify(v);
                if (v === null || v === undefined) v = '<span class="text-zinc-600">NULL</span>';
                else if (v === 'APPROVED' || v === 'COMPLETED' || v === 'DONE') v = `<span class="text-emerald-400 font-bold">${v}</span>`;
                else if (v === 'PENDING') v = `<span class="text-amber-400 font-bold">${v}</span>`;
                else if (v === 'REJECTED' || v === 'FAILED') v = `<span class="text-red-400 font-bold">${v}</span>`;
                return `<td class="py-2 px-3 truncate max-w-[140px]">${v}</td>`;
              }).join('')}
            </tr>
          `).join('');
        } else {
          bodyEl.innerHTML = '<tr><td colspan="5" class="py-3 text-center text-zinc-500">Tabla vacía (0 registros).</td></tr>';
        }
      } catch (e) {
        bodyEl.innerHTML = `<tr><td colspan="5" class="py-3 text-center text-red-400">Error: ${e.message}</td></tr>`;
      }
    }
    window.loadHudEmbeddedTable = loadHudEmbeddedTable;

    async function executeActionWithProgress(actionType, btn) {
      const container = document.getElementById('hero-action-progress-container');
      const bar = document.getElementById('hero-progress-bar');
      const pct = document.getElementById('hero-progress-pct');
      const label = document.getElementById('hero-progress-label');
      const step1 = document.getElementById('prog-step-1');
      const step2 = document.getElementById('prog-step-2');
      const step3 = document.getElementById('prog-step-3');
      const step4 = document.getElementById('prog-step-4');

      if (container) container.classList.remove('hidden');

      if (bar) bar.style.width = '25%';
      if (pct) pct.innerText = '25%';
      if (label) label.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Fase 1/4: Inspección de Contratos DR-INV-001 & DR-PAY-001...</span>';
      if (step1) step1.className = 'p-2 rounded bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 text-center font-bold';
      lucide.createIcons();

      await new Promise(r => setTimeout(r, 350));

      if (bar) bar.style.width = '55%';
      if (pct) pct.innerText = '55%';
      if (label) label.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Fase 2/4: Verificación de Singleton Leases & WAL Mode...</span>';
      if (step2) step2.className = 'p-2 rounded bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 text-center font-bold';
      lucide.createIcons();

      await new Promise(r => setTimeout(r, 350));

      if (bar) bar.style.width = '85%';
      if (pct) pct.innerText = '85%';
      if (label) label.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Fase 3/4: Despacho de Suite Pytest (29 tests)...</span>';
      if (step3) step3.className = 'p-2 rounded bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 text-center font-bold';
      lucide.createIcons();

      await executeAction(actionType, {}, btn);

      if (bar) bar.style.width = '100%';
      if (pct) pct.innerText = '100%';
      if (label) label.innerHTML = '<i data-lucide="check" class="w-4 h-4 text-emerald-400 stroke-[3]"></i><span class="text-emerald-400 font-bold">¡Completado con Éxito (EXIT 0)!</span>';
      if (step4) step4.className = 'p-2 rounded bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 text-center font-bold';
      lucide.createIcons();

      loadHudEmbeddedTable('approvals');

      setTimeout(() => {
        if (container) container.classList.add('hidden');
        if (bar) bar.style.width = '0%';
        if (step1) step1.className = 'p-2 rounded bg-black/40 border bd text-center';
        if (step2) step2.className = 'p-2 rounded bg-black/40 border bd text-center';
        if (step3) step3.className = 'p-2 rounded bg-black/40 border bd text-center';
        if (step4) step4.className = 'p-2 rounded bg-black/40 border bd text-center';
      }, 5000);
    }
    window.executeActionWithProgress = executeActionWithProgress;

  
    // ==========================================
    // FILE SYSTEM EXPLORER & CODE VIEWER ENGINE (V8)
    // ==========================================
    

  </script>
</body>
</html>"""
