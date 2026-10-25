"""Compiled Revolut-Style Mobile & Desktop Responsive Template."""

HTML_APPLICATION = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>SolidBit SACL · Revolut Mobile & Desktop Dashboard</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <style>
    :root {
      --bg: #000000;
      --surface: #0a0a0e;
      --surface-elevated: #121218;
      --surface-card: #0e0e13;
      --border: rgba(255, 255, 255, 0.08);
      --border-focus: rgba(255, 255, 255, 0.2);
      --text: #ffffff;
      --text-muted: #a1a1aa;
      --text-dim: #71717a;
      --accent: #ffffff;
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      -webkit-font-smoothing: antialiased;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
    }
    .mono { font-family: var(--mono); }
    .bd { border-color: var(--border); }
    .surface { background: var(--surface); }
    .surface-elevated { background: var(--surface-elevated); }
    .surface-card { background: var(--surface-card); }
    .t2 { color: var(--text-muted); }
    .t3 { color: var(--text-dim); }

    /* Revolut card styles */
    .revolut-card {
      background: var(--surface-card);
      border: 1px solid var(--border);
      border-radius: 20px;
      transition: border-color 0.2s, transform 0.15s;
    }
    .revolut-card:hover {
      border-color: var(--border-focus);
    }

    /* Revolut Button standards */
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      font-weight: 600;
      border-radius: 9999px;
      transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
      cursor: pointer;
      user-select: none;
      touch-action: manipulation;
    }
    .btn-primary {
      background: #ffffff;
      color: #000000;
      border: 1px solid #ffffff;
      box-shadow: 0 4px 14px rgba(255, 255, 255, 0.15);
    }
    .btn-primary:hover, .btn-primary:active {
      background: #e4e4e7;
      transform: scale(0.98);
    }
    .btn-secondary {
      background: rgba(255, 255, 255, 0.06);
      color: #ffffff;
      border: 1px solid var(--border);
    }
    .btn-secondary:hover, .btn-secondary:active {
      background: rgba(255, 255, 255, 0.1);
      border-color: var(--border-focus);
    }
    .btn-danger {
      background: rgba(239, 68, 68, 0.14);
      color: #fca5a5;
      border: 1px solid rgba(239, 68, 68, 0.35);
    }
    .btn-danger:hover, .btn-danger:active {
      background: rgba(239, 68, 68, 0.25);
      color: #ffffff;
    }

    /* Segmented Navigation */
    .nav-pill {
      padding: 8px 16px;
      border-radius: 9999px;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-muted);
      transition: all 0.2s;
      white-space: nowrap;
      cursor: pointer;
    }
    .nav-pill.active {
      background: #ffffff;
      color: #000000;
      box-shadow: 0 4px 12px rgba(255, 255, 255, 0.15);
    }

    /* Mobile Bottom Navigation Bar */
    .mobile-tab-btn {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 3px;
      font-size: 10px;
      font-weight: 600;
      color: var(--text-muted);
      flex: 1;
      padding: 8px 0;
      touch-action: manipulation;
    }
    .mobile-tab-btn.active {
      color: #ffffff;
    }
    .mobile-tab-btn.active i {
      color: #ffffff;
      stroke-width: 2.5;
    }

    /* Custom scrollbars */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.15); border-radius: 9999px; }
    .no-scrollbar::-webkit-scrollbar { display: none; }
    .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }

    /* Toast */
    .toast-container {
      position: fixed;
      bottom: 84px;
      left: 16px;
      right: 16px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      pointer-events: none;
    }
    @media (min-width: 768px) {
      .toast-container {
        bottom: 24px;
        left: auto;
        right: 24px;
        align-items: flex-end;
      }
    }
    .toast {
      background: #121218;
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: #ffffff;
      padding: 12px 20px;
      border-radius: 9999px;
      font-size: 13px;
      font-weight: 500;
      box-shadow: 0 12px 35px rgba(0, 0, 0, 0.9);
      display: inline-flex;
      align-items: center;
      gap: 10px;
      pointer-events: auto;
      animation: popIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes popIn {
      from { transform: scale(0.9) translateY(10px); opacity: 0; }
      to { transform: scale(1) translateY(0); opacity: 1; }
    }
  </style>
</head>
<body class="flex flex-col h-screen select-none bg-black text-white">

  <!-- TOP HEADER (REVOLUT COMPACT HEADER) -->
  <header class="h-16 border-b bd flex items-center justify-between px-4 md:px-6 bg-black/80 backdrop-blur-md z-30 shrink-0">
    <!-- Brand / Project Selector -->
    <div class="flex items-center gap-3">
      <div class="w-9 h-9 rounded-full bg-white/10 flex items-center justify-center border bd overflow-hidden shrink-0 cursor-pointer" onclick="switchSection('dashboard')">
        <img src="data:image/png;base64,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" alt="SolidBit" class="w-5 h-5 object-contain invert">
      </div>
      <div>
        <div class="flex items-center gap-2">
          <span class="text-sm font-bold tracking-tight text-white">SolidBit SACL</span>
          <span class="text-[10px] mono px-2 py-0.5 rounded-full bg-white/10 text-zinc-300 font-semibold">REVOLUT UX</span>
        </div>
        <div class="text-[11px] text-zinc-400 flex items-center gap-1.5 truncate max-w-[200px] sm:max-w-xs">
          <i data-lucide="folder" class="w-3 h-3 text-emerald-400 shrink-0"></i>
          <span id="header-active-project-name" class="font-medium text-zinc-300 truncate">Stable-Ecommerce-Orchestrator</span>
        </div>
      </div>
    </div>

    <!-- Desktop Segmented Switcher -->
    <div class="hidden md:flex items-center p-1 rounded-full bg-white/5 border bd">
      <button id="dtab-dashboard" class="nav-pill active flex items-center gap-2" onclick="switchSection('dashboard')">
        <i data-lucide="layout-dashboard" class="w-4 h-4"></i>
        <span>Dashboard</span>
      </button>
      <button id="dtab-projects" class="nav-pill flex items-center gap-2" onclick="switchSection('projects')">
        <i data-lucide="folder-git-2" class="w-4 h-4"></i>
        <span>Proyectos</span>
      </button>
      <button id="dtab-sdlc" class="nav-pill flex items-center gap-2" onclick="switchSection('sdlc')">
        <i data-lucide="git-merge" class="w-4 h-4"></i>
        <span>SDLC & Automatizaciones</span>
      </button>
      <button id="dtab-chat" class="nav-pill flex items-center gap-2" onclick="switchSection('chat')">
        <i data-lucide="message-square" class="w-4 h-4"></i>
        <span>Asistente</span>
      </button>
    </div>

    <!-- Right Controls -->
    <div class="flex items-center gap-2.5">
      <!-- Live Indicator -->
      <div class="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-emerald-500/25 bg-emerald-500/10 text-emerald-400 text-xs font-semibold">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        <span class="mono">SSE LIVE PUSH</span>
      </div>

      <!-- Quick Tuerca Settings -->
      <button onclick="openSettingsDrawer()" class="relative p-2.5 rounded-full border bd surface-elevated hover:bg-white/10 text-white cursor-pointer" title="Configuración">
        <i data-lucide="sliders" class="w-4 h-4"></i>
        <span id="tuerca-gate-badge" class="absolute -top-1 -right-1 w-4 h-4 bg-amber-400 text-black text-[10px] font-bold rounded-full flex items-center justify-center border border-black hidden">1</span>
      </button>
    </div>
  </header>

  <!-- MAIN SCROLLABLE CONTAINER -->
  <main class="flex-1 overflow-y-auto pb-24 md:pb-8">

    <!-- ========================================== -->
    <!-- SECTION 1: DASHBOARD GENERAL (REVOLUT HERO) -->
    <!-- ========================================== -->
    <div id="sec-dashboard" class="p-4 md:p-6 lg:p-8 max-w-6xl mx-auto space-y-6">

      <!-- REVOLUT HERO CARD -->
      <div class="revolut-card p-6 md:p-8 bg-gradient-to-br from-[#12121a] via-[#09090d] to-black relative overflow-hidden border-white/10 shadow-2xl">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div class="flex items-center gap-2.5">
              <span class="text-xs uppercase tracking-widest font-bold text-zinc-400">Readiness Global SDLC</span>
              <span class="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/25 text-[11px] font-semibold flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Soberano Activo
              </span>
            </div>
            <div class="text-5xl md:text-6xl font-extrabold tracking-tight text-white mt-3">
              99.5%
            </div>
            <div class="text-xs text-zinc-400 mt-3 flex flex-wrap items-center gap-x-4 gap-y-1">
              <span>SQLite WAL: <span class="text-emerald-400 font-semibold">Operacional</span></span>
              <span>·</span>
              <span>Tests: <span class="text-emerald-400 font-semibold">690/690 Verde</span></span>
              <span>·</span>
              <span>Resend: <span class="text-emerald-400 font-semibold">Real (v2.26.0)</span></span>
              <span>·</span>
              <span>Railway: <span class="text-emerald-400 font-semibold">lucilfer</span></span>
            </div>
          </div>

          <!-- Quick Action Buttons (Revolut Style) -->
          <div class="grid grid-cols-2 sm:flex sm:flex-wrap items-center gap-3">
            <button onclick="launchActiveCampaign()" class="btn btn-primary px-5 py-3 text-xs w-full sm:w-auto">
              <i data-lucide="play" class="w-4 h-4 fill-black"></i>
              <span>Lanzar Sprint</span>
            </button>
            <button onclick="openDecisionGateModal()" class="btn btn-secondary px-4 py-3 text-xs w-full sm:w-auto">
              <i data-lucide="check-circle" class="w-4 h-4 text-emerald-400"></i>
              <span>Autorizar Gate</span>
            </button>
            <button onclick="switchSection('projects')" class="btn btn-secondary px-4 py-3 text-xs w-full sm:w-auto">
              <i data-lucide="folder-search" class="w-4 h-4 text-blue-400"></i>
              <span>Ver Proyectos</span>
            </button>
            <button onclick="switchSection('sdlc')" class="btn btn-secondary px-4 py-3 text-xs w-full sm:w-auto">
              <i data-lucide="cpu" class="w-4 h-4 text-purple-400"></i>
              <span>Automaciones</span>
            </button>
          </div>
        </div>
      </div>

      <!-- TWO-COLUMN DASHBOARD GRID -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <!-- COLUMN 1 & 2: CRITICAL GATE & TELEMETRY -->
        <div class="lg:col-span-2 space-y-6">

          <!-- WIDGET: MICRO-DECISIÓN INMEDIATA -->
          <div class="revolut-card p-6 border-amber-500/30 bg-gradient-to-r from-amber-500/10 via-transparent to-transparent">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping"></span>
                <span class="text-xs uppercase tracking-wider font-bold text-amber-400">Compuerta de Decisión Pendiente</span>
              </div>
              <span id="gate-request-id-pill" class="mono text-xs px-3 py-1 rounded-full bg-white/10 border bd text-zinc-200 font-semibold">REQ-20261025-406DBE23</span>
            </div>

            <h3 id="gate-action-title" class="text-base md:text-lg font-bold text-white leading-snug">Verificar despliegue efímero en Railway antes de merge a main</h3>
            <p id="gate-infra-impact" class="text-xs text-zinc-400 mt-1">Impacto: 1 servicio efímero en Railway · 0 mutaciones en producción · Contratos auditados OK</p>

            <div class="flex flex-wrap items-center gap-3 mt-5">
              <button onclick="submitGateDecisionDirect(activeGateId || 'REQ-20261025-406DBE23', 'APPROVED')" class="btn btn-primary px-5 py-2.5 text-xs">
                <i data-lucide="check" class="w-4 h-4"></i>
                <span>Autorizar Despliegue</span>
              </button>
              <button onclick="submitGateDecisionDirect(activeGateId || 'REQ-20261025-406DBE23', 'REJECTED')" class="btn btn-danger px-4 py-2.5 text-xs">
                <i data-lucide="x" class="w-4 h-4"></i>
                <span>Rechazar</span>
              </button>
              <button onclick="inspectDiffAndImpact(activeGateId || 'REQ-20261025-406DBE23')" class="btn btn-secondary px-4 py-2.5 text-xs">
                <i data-lucide="file-diff" class="w-4 h-4"></i>
                <span>Ver Diff de Código</span>
              </button>
            </div>
          </div>

          <!-- WIDGET: AVANCE DEL SPRINT (SVG DONUT) -->
          <div class="revolut-card p-6">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h4 class="text-sm font-bold text-white">Telemetría de Ejecución en Vivo</h4>
                <div class="text-xs text-zinc-400">Monitoreo topológico del DAG y avance de fases</div>
              </div>
              <button onclick="simulateProgressStep()" class="btn btn-secondary text-xs px-3 py-1.5">
                <i data-lucide="play-circle" class="w-3.5 h-3.5 text-emerald-400"></i>
                <span>Avanzar +15%</span>
              </button>
            </div>

            <div class="flex flex-col sm:flex-row items-center gap-6 pt-2">
              <!-- SVG Donut -->
              <div class="relative w-36 h-36 shrink-0 flex items-center justify-center">
                <svg class="w-full h-full -rotate-90" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="12"></circle>
                  <circle id="revolut-donut-circle" cx="50" cy="50" r="42" fill="none" stroke="#10b981" stroke-width="12" stroke-linecap="round" stroke-dasharray="264" stroke-dashoffset="66" class="transition-all duration-700"></circle>
                </svg>
                <div class="absolute inset-0 flex flex-col items-center justify-center text-center">
                  <span id="revolut-donut-text" class="text-3xl font-extrabold tracking-tight text-white">75%</span>
                  <span class="text-[10px] uppercase font-bold text-emerald-400">Completado</span>
                </div>
              </div>

              <!-- Metrics Summary -->
              <div class="flex-1 w-full space-y-2.5">
                <div class="flex items-center justify-between p-3 rounded-xl bg-white/5 border bd text-xs">
                  <span class="text-zinc-400">Workorders del DAG</span>
                  <span class="mono font-bold text-white">3 / 4 Listos</span>
                </div>
                <div class="flex items-center justify-between p-3 rounded-xl bg-white/5 border bd text-xs">
                  <span class="text-zinc-400">Tokens Ingeridos</span>
                  <span class="mono font-bold text-white">14,820</span>
                </div>
                <div class="flex items-center justify-between p-3 rounded-xl bg-white/5 border bd text-xs">
                  <span class="text-zinc-400">Contratos Auditados</span>
                  <span class="text-emerald-400 font-bold flex items-center gap-1.5">
                    <i data-lucide="shield-check" class="w-4 h-4"></i> 4 / 4 Intactos
                  </span>
                </div>
              </div>
            </div>
          </div>

        </div>

        <!-- COLUMN 3: CONNECTIONS & CONTRATOS -->
        <div class="space-y-6">

          <!-- CONEXIONES SDLC -->
          <div class="revolut-card p-6 space-y-3.5">
            <div class="flex items-center justify-between">
              <h4 class="text-sm font-bold text-white">Herramientas SDLC Conectadas</h4>
              <span class="text-[10px] mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/25 font-semibold">100% LISTAS</span>
            </div>

            <div class="space-y-2">
              <div class="p-3 rounded-xl bg-white/5 border bd flex items-center justify-between text-xs">
                <div class="flex items-center gap-3">
                  <i data-lucide="github" class="w-4 h-4 text-white"></i>
                  <div>
                    <div class="font-bold text-white">GitHub CLI</div>
                    <div class="text-[11px] text-zinc-400">@risejoaquin (Keyring)</div>
                  </div>
                </div>
                <span class="text-[10px] font-semibold text-emerald-400 px-2 py-0.5 rounded-full bg-emerald-500/10">Activo</span>
              </div>

              <div class="p-3 rounded-xl bg-white/5 border bd flex items-center justify-between text-xs">
                <div class="flex items-center gap-3">
                  <i data-lucide="train" class="w-4 h-4 text-purple-400"></i>
                  <div>
                    <div class="font-bold text-white">Railway CLI</div>
                    <div class="text-[11px] text-zinc-400">lucilfer (OAuth Device)</div>
                  </div>
                </div>
                <span class="text-[10px] font-semibold text-emerald-400 px-2 py-0.5 rounded-full bg-emerald-500/10">Activo</span>
              </div>

              <div class="p-3 rounded-xl bg-white/5 border bd flex items-center justify-between text-xs">
                <div class="flex items-center gap-3">
                  <i data-lucide="mail" class="w-4 h-4 text-emerald-400"></i>
                  <div>
                    <div class="font-bold text-white">Resend CLI</div>
                    <div class="text-[11px] text-zinc-400">v2.26.0 (Entrega Real)</div>
                  </div>
                </div>
                <span class="text-[10px] font-semibold text-emerald-400 px-2 py-0.5 rounded-full bg-emerald-500/10">Activo</span>
              </div>

              <div class="p-3 rounded-xl bg-white/5 border bd flex items-center justify-between text-xs">
                <div class="flex items-center gap-3">
                  <i data-lucide="database" class="w-4 h-4 text-emerald-500"></i>
                  <div>
                    <div class="font-bold text-white">Supabase CLI</div>
                    <div class="text-[11px] text-zinc-400">v2.122.0 (npx Runner)</div>
                  </div>
                </div>
                <span class="text-[10px] font-semibold text-emerald-400 px-2 py-0.5 rounded-full bg-emerald-500/10">Listo</span>
              </div>
            </div>
          </div>

          <!-- CONTRATOS INVIOLABLES -->
          <div class="revolut-card p-6 space-y-3">
            <h4 class="text-sm font-bold text-white">Contratos Inmutables</h4>
            <div class="space-y-2 text-xs">
              <div class="p-2.5 rounded-xl bg-white/5 border bd flex items-center justify-between">
                <span class="mono font-semibold text-zinc-200">DR-INV-001</span>
                <span class="text-[10px] font-bold text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10">Ledger Atómico</span>
              </div>
              <div class="p-2.5 rounded-xl bg-white/5 border bd flex items-center justify-between">
                <span class="mono font-semibold text-zinc-200">DR-PAY-001</span>
                <span class="text-[10px] font-bold text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10">Cero-Overcharge</span>
              </div>
              <div class="p-2.5 rounded-xl bg-white/5 border bd flex items-center justify-between">
                <span class="mono font-semibold text-zinc-200">DR-IDEM-001</span>
                <span class="text-[10px] font-bold text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10">Idempotencia</span>
              </div>
            </div>
          </div>

        </div>

      </div>

    </div>

    <!-- ========================================== -->
    <!-- SECTION 2: PROYECTOS & DOCUMENTACIÓN LOCAL -->
    <!-- ========================================== -->
    <div id="sec-projects" class="p-4 md:p-6 lg:p-8 max-w-6xl mx-auto space-y-6 hidden">
      <!-- Section Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <i data-lucide="folder-git-2" class="w-6 h-6 text-emerald-400"></i>
            <span>Proyectos Detectados en Local</span>
          </h2>
          <p class="text-xs text-zinc-400 mt-1">Explora repositorios, documentación arquitectónica detectada y cambia de espacio de trabajo.</p>
        </div>

        <div class="relative w-full sm:w-72">
          <input type="text" id="project-search-input" oninput="filterProjectsList()" placeholder="Buscar proyecto o documentación..."
            class="w-full bg-[#121218] border bd rounded-full px-4 py-2 pl-9 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-white/30">
          <i data-lucide="search" class="w-4 h-4 text-zinc-500 absolute left-3 top-2.5"></i>
        </div>
      </div>

      <!-- Scanned Projects List Container -->
      <div id="projects-scanned-container" class="grid grid-cols-1 md:grid-cols-2 gap-4"></div>
    </div>

    <!-- ========================================== -->
    <!-- SECTION 3: SDLC & AUTOMATIZACIONES (SCRIPTS) -->
    <!-- ========================================== -->
    <div id="sec-sdlc" class="p-4 md:p-6 lg:p-8 max-w-6xl mx-auto space-y-6 hidden">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <i data-lucide="git-merge" class="w-6 h-6 text-purple-400"></i>
            <span>SDLC & Automatizaciones de Proyectos</span>
          </h2>
          <p class="text-xs text-zinc-400 mt-1">Lanzadores directos de diseño de software, auditoría, testing y pipelines de release.</p>
        </div>
      </div>

      <!-- SDLC Automation Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="revolut-card p-5 space-y-3">
          <div class="w-10 h-10 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <i data-lucide="pen-tool" class="w-5 h-5"></i>
          </div>
          <h4 class="text-sm font-bold text-white">Diseño de Software</h4>
          <p class="text-xs text-zinc-400">Genera especificaciones de producto, esquemas de bases de datos y flujos UX.</p>
          <button onclick="launchAutomationSDLC('software_design')" class="btn btn-secondary text-xs w-full py-2">Ejecutar Diseño</button>
        </div>

        <div class="revolut-card p-5 space-y-3">
          <div class="w-10 h-10 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <i data-lucide="shield-alert" class="w-5 h-5"></i>
          </div>
          <h4 class="text-sm font-bold text-white">Auditoría & Seguridad</h4>
          <p class="text-xs text-zinc-400">Audita contratos inmutables DR-INV-001, balance transaccional e idempotencia.</p>
          <button onclick="launchAutomationSDLC('security_audit')" class="btn btn-secondary text-xs w-full py-2">Lanzar Auditoría</button>
        </div>

        <div class="revolut-card p-5 space-y-3">
          <div class="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <i data-lucide="check-check" class="w-5 h-5"></i>
          </div>
          <h4 class="text-sm font-bold text-white">Suite de Pruebas Unitarias</h4>
          <p class="text-xs text-zinc-400">Ejecuta pytest y tests de integración en worktree aislado con reconciliación.</p>
          <button onclick="launchAutomationSDLC('test_suite')" class="btn btn-secondary text-xs w-full py-2">Correr Pytest (690)</button>
        </div>

        <div class="revolut-card p-5 space-y-3">
          <div class="w-10 h-10 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <i data-lucide="rocket" class="w-5 h-5"></i>
          </div>
          <h4 class="text-sm font-bold text-white">Despliegue & Release</h4>
          <p class="text-xs text-zinc-400">Aprovisiona preview efímero en Railway y valida empaquetado de entrega.</p>
          <button onclick="launchAutomationSDLC('release_pipeline')" class="btn btn-secondary text-xs w-full py-2">Pipeline Staging</button>
        </div>
      </div>

      <!-- Scanned Automation Scripts in Active Project -->
      <div class="revolut-card p-6 space-y-4">
        <h3 class="text-sm font-bold text-white flex items-center gap-2">
          <i data-lucide="terminal" class="w-4 h-4 text-emerald-400"></i>
          <span>Scripts de Automatización Detectados en el Proyecto Activo</span>
        </h3>
        <div id="active-project-automations-list" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 text-xs"></div>
      </div>
    </div>

    <!-- ========================================== -->
    <!-- SECTION 4: ASISTENTE CHAT SOBERANO -->
    <!-- ========================================== -->
    <div id="sec-chat" class="p-4 md:p-6 lg:p-8 max-w-3xl mx-auto space-y-4 hidden">
      <!-- Chat Messages Scroll Area -->
      <div id="chat-messages-scroll" class="space-y-4 min-h-[350px]">
        <div id="chat-welcome-hero" class="text-center py-8 space-y-2">
          <div class="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center border bd mx-auto overflow-hidden">
            <img src="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" alt="SolidBit" class="w-7 h-7 object-contain invert">
          </div>
          <h2 class="text-xl font-extrabold tracking-tight text-white">SolidBit SACL · Asistente Soberano</h2>
          <p class="text-xs text-zinc-400 max-w-md mx-auto leading-relaxed">
            Ejecuta comandos de SDLC, audita proyectos locales, lanza campañas o autoriza compuertas directamente en tiempo real.
          </p>
        </div>
        <div id="chat-messages-container" class="space-y-3"></div>
      </div>

      <!-- Prompt Chips -->
      <div class="flex items-center gap-2 overflow-x-auto no-scrollbar py-2">
        <button onclick="sendQuickPrompt('Lanzar Sprint SACL')" class="btn btn-secondary text-xs px-3.5 py-1.5 whitespace-nowrap shrink-0">
          <i data-lucide="rocket" class="w-3.5 h-3.5 text-emerald-400"></i><span>Lanzar Sprint</span>
        </button>
        <button onclick="sendQuickPrompt('Auditar Contratos DR-INV-001')" class="btn btn-secondary text-xs px-3.5 py-1.5 whitespace-nowrap shrink-0">
          <i data-lucide="shield" class="w-3.5 h-3.5 text-blue-400"></i><span>Auditar DR-INV</span>
        </button>
        <button onclick="sendQuickPrompt('Ver Compuertas Pendientes')" class="btn btn-secondary text-xs px-3.5 py-1.5 whitespace-nowrap shrink-0">
          <i data-lucide="git-pull-request" class="w-3.5 h-3.5 text-amber-400"></i><span>Ver Compuertas</span>
        </button>
        <button onclick="sendQuickPrompt('Autorizar Despliegue')" class="btn btn-secondary text-xs px-3.5 py-1.5 whitespace-nowrap shrink-0">
          <i data-lucide="check-circle" class="w-3.5 h-3.5 text-emerald-400"></i><span>Autorizar</span>
        </button>
      </div>

      <!-- Chat Input Box -->
      <div class="relative rounded-2xl border bd surface-elevated focus-within:border-white/30 transition-all shadow-2xl">
        <textarea id="chat-input" rows="2" placeholder="Escribe una instrucción al orquestador..."
          class="w-full bg-transparent p-4 pr-12 text-sm text-white placeholder-zinc-500 focus:outline-none resize-none"
          onkeydown="handleChatKeyDown(event)"></textarea>
        <button id="chat-send-btn" onclick="sendChatMessage()" class="absolute right-3 bottom-3 w-8 h-8 rounded-full bg-white text-black flex items-center justify-center hover:bg-zinc-200 transition-all cursor-pointer">
          <i data-lucide="arrow-up" class="w-4 h-4"></i>
        </button>
      </div>
    </div>

  </main>

  <!-- MOBILE BOTTOM NAVIGATION BAR (REVOLUT STYLE) -->
  <nav class="md:hidden fixed bottom-0 inset-x-0 h-16 bg-[#08080c]/95 backdrop-blur-lg border-t bd z-40 flex items-center justify-around px-2">
    <button id="mtab-dashboard" class="mobile-tab-btn active" onclick="switchSection('dashboard')">
      <i data-lucide="layout-dashboard" class="w-5 h-5"></i>
      <span>Inicio</span>
    </button>
    <button id="mtab-projects" class="mobile-tab-btn" onclick="switchSection('projects')">
      <i data-lucide="folder-git-2" class="w-5 h-5"></i>
      <span>Proyectos</span>
    </button>
    <button id="mtab-sdlc" class="mobile-tab-btn" onclick="switchSection('sdlc')">
      <i data-lucide="git-merge" class="w-5 h-5"></i>
      <span>SDLC</span>
    </button>
    <button id="mtab-chat" class="mobile-tab-btn" onclick="switchSection('chat')">
      <i data-lucide="message-square" class="w-5 h-5"></i>
      <span>Chat</span>
    </button>
    <button class="mobile-tab-btn" onclick="openSettingsDrawer()">
      <i data-lucide="sliders" class="w-5 h-5"></i>
      <span>Ajustes</span>
    </button>
  </nav>

  <!-- IMPACT & VISUAL DIFF DRAWER -->
  <aside id="impact-drawer" class="fixed inset-y-0 right-0 w-full sm:w-[560px] bg-[#0c0c12] border-l bd z-50 transform translate-x-full transition-transform duration-300 ease-out flex flex-col shadow-2xl">
    <div class="h-16 border-b bd px-5 flex items-center justify-between bg-black/40">
      <div class="flex items-center gap-2.5">
        <i data-lucide="file-diff" class="w-5 h-5 text-amber-400"></i>
        <h3 class="text-sm font-bold text-white">Cajón de Impacto Visual & Diff</h3>
      </div>
      <button onclick="closeImpactDrawer()" class="p-2 rounded-lg hover:bg-white/10 text-zinc-400 hover:text-white cursor-pointer">
        <i data-lucide="x" class="w-5 h-5"></i>
      </button>
    </div>
    <div class="flex-1 overflow-y-auto p-5 space-y-5">
      <div>
        <div class="text-[10px] uppercase font-bold text-zinc-400 tracking-wider">COMPUERTA EVALUADA</div>
        <div id="diff-req-id" class="text-sm font-bold text-white mono mt-0.5">REQ-20261025-406DBE23</div>
        <div id="diff-action-name" class="text-xs text-amber-400 mono font-semibold">DEPLOY_STAGING_PREVIEW</div>
      </div>
      <div class="rounded-2xl border bd surface p-4 space-y-2.5 text-xs">
        <div class="flex items-center justify-between"><span class="text-zinc-400">Impacto en producción:</span><span class="text-emerald-400 font-bold">0 servicios mutados</span></div>
        <div class="flex items-center justify-between"><span class="text-zinc-400">Servicios efímeros:</span><span class="font-bold text-white">1 Railway Staging Preview</span></div>
        <div class="flex items-center justify-between"><span class="text-zinc-400">Contratos auditados:</span><span class="text-emerald-400 font-bold">DR-INV-001, DR-PAY-001 OK</span></div>
      </div>
      <div>
        <div class="text-xs font-bold text-white mb-2">Commits afectados en la rama</div>
        <div id="diff-commits-list" class="space-y-1.5"></div>
      </div>
      <div>
        <div class="text-xs font-bold text-white mb-2">Diff de código unificado</div>
        <pre id="diff-code-block" class="mono text-[11px] p-4 rounded-xl bg-black border bd text-zinc-300 overflow-x-auto max-h-80 leading-relaxed"></pre>
      </div>
    </div>
    <div class="p-4 border-t bd bg-black/60 flex items-center justify-end gap-3">
      <button onclick="closeImpactDrawer()" class="btn btn-secondary text-xs px-4 py-2.5">Cerrar</button>
      <button onclick="submitGateDecisionDirect(activeGateId || 'REQ-20261025-406DBE23', 'REJECTED')" class="btn btn-danger text-xs px-4 py-2.5">Rechazar</button>
      <button onclick="submitGateDecisionDirect(activeGateId || 'REQ-20261025-406DBE23', 'APPROVED')" class="btn btn-primary text-xs px-5 py-2.5">Autorizar Despliegue</button>
    </div>
  </aside>

  <!-- SETTINGS GEAR DRAWER (TUERCA) -->
  <aside id="settings-drawer" class="fixed inset-y-0 right-0 w-full sm:w-[620px] bg-[#0c0c12] border-l bd z-50 transform translate-x-full transition-transform duration-300 ease-out flex flex-col shadow-2xl">
    <div class="h-16 border-b bd px-5 flex items-center justify-between bg-black/40">
      <div class="flex items-center gap-3">
        <div class="p-2 rounded-xl bg-white/5 border bd">
          <i data-lucide="sliders" class="w-5 h-5 text-white"></i>
        </div>
        <div>
          <h3 class="text-sm font-bold text-white">Centro Operativo & Configuración</h3>
          <div class="text-[11px] text-zinc-400">Gobernanza, compuertas, contratos y conexiones</div>
        </div>
      </div>
      <button onclick="closeSettingsDrawer()" class="p-2 rounded-lg hover:bg-white/10 text-zinc-400 hover:text-white cursor-pointer">
        <i data-lucide="x" class="w-5 h-5"></i>
      </button>
    </div>

    <!-- Drawer Tabs -->
    <div class="border-b bd bg-black/20 px-3 py-2 flex items-center gap-1.5 overflow-x-auto no-scrollbar">
      <button class="settings-tab-btn active text-xs px-3.5 py-1.5 rounded-lg border bd font-semibold text-white" onclick="switchSettingsTab('gates')">Decision Gates</button>
      <button class="settings-tab-btn text-xs px-3.5 py-1.5 rounded-lg border border-transparent font-semibold text-zinc-400 hover:text-white" onclick="switchSettingsTab('connections')">Conexiones</button>
      <button class="settings-tab-btn text-xs px-3.5 py-1.5 rounded-lg border border-transparent font-semibold text-zinc-400 hover:text-white" onclick="switchSettingsTab('email')">Email Gateway</button>
      <button class="settings-tab-btn text-xs px-3.5 py-1.5 rounded-lg border border-transparent font-semibold text-zinc-400 hover:text-white" onclick="switchSettingsTab('contracts')">Contratos</button>
      <button class="settings-tab-btn text-xs px-3.5 py-1.5 rounded-lg border border-transparent font-semibold text-zinc-400 hover:text-white" onclick="switchSettingsTab('db')">Base de Datos</button>
    </div>

    <!-- Drawer Tab Panes -->
    <div class="flex-1 overflow-y-auto p-5 space-y-5">
      <!-- GATES TAB -->
      <div id="stab-gates" class="space-y-4">
        <div class="text-xs text-zinc-400">Compuertas de decisión registradas en SQLite WAL con tokens criptográficos HMAC.</div>
        <div id="drawer-gates-list" class="space-y-3"></div>
      </div>

      <!-- CONNECTIONS TAB -->
      <div id="stab-connections" class="space-y-4 hidden">
        <div class="text-xs text-zinc-400">Estado de herramientas locales y credenciales del sistema operativo.</div>
        <div id="drawer-connections-list" class="space-y-3"></div>
      </div>

      <!-- EMAIL TAB -->
      <div id="stab-email" class="space-y-4 hidden">
        <div class="rounded-2xl border bd surface p-5 space-y-3.5 text-xs">
          <div class="flex items-center justify-between">
            <span class="font-bold text-white text-sm">Canal Resend API Real</span>
            <span class="px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-bold">100% REAL</span>
          </div>
          <div>Remitente: <span class="mono text-zinc-200">onboarding@resend.dev</span></div>
          <div>Destinatario: <span class="mono text-zinc-200">joaquin.carpio261724@potros.itson.edu.mx</span></div>
          <button onclick="triggerEmailTest()" class="btn btn-primary text-xs w-full py-2.5 mt-2">Enviar Correo de Prueba a Mi Bandeja</button>
        </div>
      </div>

      <!-- CONTRACTS TAB -->
      <div id="stab-contracts" class="space-y-4 hidden">
        <div class="text-xs text-zinc-400">Catálogo de invariantes inviolables respaldados por Hard Deny Supremacy.</div>
        <div id="drawer-contracts-list" class="space-y-3"></div>
      </div>

      <!-- DB TAB -->
      <div id="stab-db" class="space-y-4 hidden">
        <div class="text-xs text-zinc-400">Estadísticas en vivo de tablas en `sacl_ops.db` (Modo WAL).</div>
        <div id="drawer-db-stats" class="grid grid-cols-2 gap-3 text-xs"></div>
      </div>
    </div>
  </aside>

  <!-- TOAST NOTIFIER -->
  <div id="toast-container" class="toast-container"></div>

  <!-- JAVASCRIPT APP LOGIC -->
  <script>
    const API_BASE = window.location.origin;
    let activeGateId = 'REQ-20261025-406DBE23';
    let allProjects = [];

    // Toast Notification
    function showToast(message, type = 'info') {
      const container = document.getElementById('toast-container');
      const toast = document.createElement('div');
      toast.className = 'toast';
      const icon = type === 'success' ? 'check-circle' : (type === 'error' ? 'alert-triangle' : 'info');
      const iconColor = type === 'success' ? 'text-emerald-400' : (type === 'error' ? 'text-red-400' : 'text-blue-400');
      toast.innerHTML = `<i data-lucide="${icon}" class="w-4 h-4 ${iconColor} shrink-0"></i><span>${message}</span>`;
      container.appendChild(toast);
      lucide.createIcons();
      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'scale(0.95)';
        toast.style.transition = 'all 0.25s ease';
        setTimeout(() => toast.remove(), 250);
      }, 3500);
    }

    // Switch Top/Bottom Sections (Dashboard, Projects, SDLC, Chat)
    function switchSection(sec) {
      const sections = ['dashboard', 'projects', 'sdlc', 'chat'];
      sections.forEach(s => {
        const el = document.getElementById(`sec-${s}`);
        if (el) el.classList.toggle('hidden', s !== sec);

        // Desktop nav pills
        const dtab = document.getElementById(`dtab-${s}`);
        if (dtab) dtab.classList.toggle('active', s === sec);

        // Mobile bottom nav buttons
        const mtab = document.getElementById(`mtab-${s}`);
        if (mtab) mtab.classList.toggle('active', s === sec);
      });

      if (sec === 'projects') loadProjects();
      if (sec === 'chat') {
        setTimeout(() => document.getElementById('chat-input')?.focus(), 100);
      }

      window.scrollTo({ top: 0, behavior: 'smooth' });
      lucide.createIcons();
    }
    window.switchSection = switchSection;

    // Drawers
    function openSettingsDrawer(tab = 'gates') {
      document.getElementById('settings-drawer').classList.remove('translate-x-full');
      switchSettingsTab(tab);
    }
    window.openSettingsDrawer = openSettingsDrawer;
    function closeSettingsDrawer() {
      document.getElementById('settings-drawer').classList.add('translate-x-full');
    }
    window.closeSettingsDrawer = closeSettingsDrawer;
    function openDecisionGateModal() {
      openSettingsDrawer('gates');
    }
    function closeImpactDrawer() {
      document.getElementById('impact-drawer').classList.add('translate-x-full');
    }

    function switchSettingsTab(tab) {
      const tabs = ['gates', 'connections', 'email', 'contracts', 'db'];
      tabs.forEach(t => {
        const el = document.getElementById(`stab-${t}`);
        if (el) el.classList.toggle('hidden', t !== tab);
      });
      document.querySelectorAll('.settings-tab-btn').forEach(b => {
        b.classList.remove('active', 'border-zinc-500', 'text-white');
        b.classList.add('border-transparent', 'text-zinc-400');
      });
      event?.target?.classList?.add('active', 'border-zinc-500', 'text-white');
      loadDrawerTabContent(tab);
    }
    window.switchSettingsTab = switchSettingsTab;

    // Projects Loader
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

    function renderProjectsList(projects) {
      const container = document.getElementById('projects-scanned-container');
      if (!container) return;

      container.innerHTML = projects.map(p => `
        <div class="revolut-card p-5 space-y-4 ${p.is_active ? 'border-emerald-500/40 bg-gradient-to-br from-emerald-500/5 to-transparent' : ''}">
          <div class="flex items-start justify-between gap-3">
            <div>
              <div class="flex items-center gap-2">
                <h3 class="text-base font-bold text-white">${p.name}</h3>
                ${p.is_active ? '<span class="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/25 text-[10px] font-bold">ACTIVO</span>' : ''}
              </div>
              <div class="text-[11px] mono text-zinc-400 mt-0.5 truncate max-w-xs">${p.path}</div>
            </div>
            <button onclick="switchActiveProject('${p.id}')" class="btn ${p.is_active ? 'btn-secondary opacity-60 cursor-default' : 'btn-primary'} text-xs px-3.5 py-1.5 shrink-0">
              ${p.is_active ? 'En Uso' : 'Seleccionar'}
            </button>
          </div>

          <div class="flex flex-wrap items-center gap-1.5">
            ${(p.tech_stack || []).map(t => `<span class="px-2 py-0.5 rounded-md bg-white/5 border bd text-[10px] font-medium text-zinc-300">${t}</span>`).join('')}
          </div>

          <!-- Documentation preview -->
          ${p.documentation && p.documentation.length > 0 ? `
            <div class="pt-3 border-t bd space-y-1.5">
              <div class="text-[10px] uppercase font-bold text-zinc-400 flex items-center justify-between">
                <span>Documentación Detectada</span>
                <span class="mono text-emerald-400">${p.docs_count || p.documentation.length} archivos</span>
              </div>
              <div class="grid grid-cols-2 gap-1.5 text-xs">
                ${p.documentation.slice(0, 4).map(d => `
                  <div class="p-2 rounded-lg bg-white/5 border bd truncate text-[11px] text-zinc-200 flex items-center gap-1.5">
                    <i data-lucide="file-text" class="w-3 h-3 text-blue-400 shrink-0"></i>
                    <span class="truncate">${d.name}</span>
                  </div>
                `).join('')}
              </div>
            </div>
          ` : ''}
        </div>
      `).join('');
      lucide.createIcons();
    }

    function filterProjectsList() {
      const query = document.getElementById('project-search-input').value.toLowerCase();
      const filtered = allProjects.filter(p => 
        p.name.toLowerCase().includes(query) || 
        p.path.toLowerCase().includes(query) ||
        (p.documentation || []).some(d => d.name.toLowerCase().includes(query))
      );
      renderProjectsList(filtered);
    }

    async function switchActiveProject(projectId) {
      try {
        showToast('Cambiando espacio de trabajo...', 'info');
        const res = await fetch(`${API_BASE}/api/projects/switch`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: projectId })
        });
        const data = await res.json();
        if (data.success) {
          showToast(`Proyecto cambiado a: ${data.active_project.name}`, 'success');
          loadProjects();
          loadDashboardSnapshot();
        }
      } catch (e) {
        showToast('Error cambiando de proyecto', 'error');
      }
    }

    function renderActiveProjectAutomations(project) {
      const list = document.getElementById('active-project-automations-list');
      if (!list) return;

      const automations = project.automations || [];
      if (automations.length === 0) {
        list.innerHTML = '<div class="col-span-full text-xs text-zinc-500 py-4 text-center">No se detectaron scripts ejecutables en la raíz del proyecto.</div>';
        return;
      }

      list.innerHTML = automations.map(a => `
        <div class="p-3 rounded-xl bg-white/5 border bd flex items-center justify-between">
          <div class="truncate mr-2">
            <div class="font-bold text-white truncate">${a.name}</div>
            <div class="text-[10px] text-zinc-400 mono truncate">${a.type}</div>
          </div>
          <button onclick="runLocalAutomationScript('${a.name}')" class="btn btn-secondary text-xs px-2.5 py-1 shrink-0">
            <i data-lucide="play" class="w-3 h-3 text-emerald-400"></i>
            <span>Correr</span>
          </button>
        </div>
      `).join('');
      lucide.createIcons();
    }

    function launchAutomationSDLC(type) {
      const titles = {
        software_design: 'Generador de Diseño de Software',
        security_audit: 'Auditoría de Seguridad y Contratos',
        test_suite: 'Ejecutor de Pruebas Unitarias Pytest',
        release_pipeline: 'Pipeline de Release Staging'
      };
      showToast(`Iniciando ${titles[type] || type}...`, 'info');
      if (type === 'test_suite') {
        sendQuickPrompt('Ejecutar Suite Tests');
      } else if (type === 'security_audit') {
        sendQuickPrompt('Auditar Contratos DR-INV-001 y DR-PAY-001');
      } else {
        launchActiveCampaign();
      }
    }

    function runLocalAutomationScript(scriptName) {
      showToast(`Ejecutando ${scriptName} en worktree aislado...`, 'info');
      sendQuickPrompt(`Ejecutar script de automatización ${scriptName}`);
    }

    // Load Snapshot
    async function loadDashboardSnapshot() {
      try {
        const gatesRes = await fetch(`${API_BASE}/api/gates/pending`);
        const gatesData = await gatesRes.json();
        const pending = gatesData.pending_gates || [];
        const badge = document.getElementById('tuerca-gate-badge');

        if (pending.length > 0) {
          activeGateId = pending[0].request_id || pending[0].approval_id;
          badge.innerText = pending.length;
          badge.classList.remove('hidden');
          document.getElementById('gate-request-id-pill').innerText = activeGateId;
          document.getElementById('gate-action-title').innerText = pending[0].reason || pending[0].action;
        } else {
          activeGateId = null;
          badge.classList.add('hidden');
          document.getElementById('gate-action-title').innerText = 'Ecosistema Limpio · Cero compuertas pendientes';
          document.getElementById('gate-request-id-pill').innerText = 'OPTIMAL';
        }
      } catch (e) {
        console.error(e);
      }
    }

    async function loadDrawerTabContent(tab) {
      if (tab === 'gates') {
        const res = await fetch(`${API_BASE}/api/gates/pending`);
        const data = await res.json();
        const list = document.getElementById('drawer-gates-list');
        list.innerHTML = (data.pending_gates || []).map(g => `
          <div class="p-4 rounded-xl border bd surface space-y-2.5">
            <div class="flex items-center justify-between">
              <span class="mono text-xs text-amber-400 font-bold">${g.request_id || g.approval_id}</span>
              <span class="text-[10px] mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 font-bold">PENDING</span>
            </div>
            <div class="text-xs font-bold text-white">${g.reason || g.action}</div>
            <div class="flex items-center gap-2 pt-2 border-t bd">
              <button onclick="inspectDiffAndImpact('${g.request_id || g.approval_id}')" class="btn btn-secondary text-xs flex-1 py-2">Diff & Impacto</button>
              <button onclick="submitGateDecisionDirect('${g.request_id || g.approval_id}', 'APPROVED')" class="btn btn-primary text-xs flex-1 py-2">Autorizar</button>
            </div>
          </div>
        `).join('') || '<div class="text-xs text-zinc-500 text-center py-6">No hay compuertas pendientes.</div>';
      } else if (tab === 'connections') {
        const res = await fetch(`${API_BASE}/api/connections`);
        const data = await res.json();
        const list = document.getElementById('drawer-connections-list');
        list.innerHTML = (data.connections || []).map(c => `
          <div class="p-3.5 rounded-xl border bd surface flex items-center justify-between">
            <div>
              <div class="text-xs font-bold text-white">${c.name}</div>
              <div class="text-[11px] text-zinc-400">${c.account_info || c.version || 'Listo'}</div>
            </div>
            <span class="text-[10px] mono px-2 py-0.5 rounded-full ${c.status === 'connected' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400'} font-bold">${c.status.toUpperCase()}</span>
          </div>
        `).join('');
      } else if (tab === 'db') {
        const res = await fetch(`${API_BASE}/api/db/stats`);
        const data = await res.json();
        const container = document.getElementById('drawer-db-stats');
        container.innerHTML = Object.entries(data.tables || {}).map(([k, v]) => `
          <div class="p-3 rounded-xl bg-white/5 border bd flex items-center justify-between">
            <span class="mono text-xs text-zinc-400">${k}</span>
            <span class="mono text-xs font-bold text-white">${v}</span>
          </div>
        `).join('');
      } else if (tab === 'contracts') {
        const res = await fetch(`${API_BASE}/api/contracts`);
        const data = await res.json();
        const list = document.getElementById('drawer-contracts-list');
        list.innerHTML = (data.contracts || []).map(c => `
          <div class="p-3.5 rounded-xl border bd surface space-y-1">
            <div class="flex items-center justify-between">
              <span class="mono text-xs font-bold text-emerald-400">${c.code || c.id}</span>
              <span class="text-[10px] font-bold text-emerald-400 px-2 py-0.5 rounded bg-emerald-500/10">INVIOLABLE</span>
            </div>
            <div class="text-xs font-bold text-white">${c.name || c.title}</div>
            <div class="text-[11px] text-zinc-400">${c.rule || c.description || 'Protegido por Hard Deny Supremacy'}</div>
          </div>
        `).join('');
      }
      lucide.createIcons();
    }

    // Gate Action & Diff
    async function submitGateDecisionDirect(gateId, decision) {
      try {
        const res = await fetch(`${API_BASE}/api/gates/decision`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            request_id: gateId,
            decision: decision,
            justification: 'Autorizado vía Revolut Dashboard'
          })
        });
        const data = await res.json();
        if (data.success) {
          showToast(`Compuerta ${gateId}: ${decision}`, 'success');
          loadDashboardSnapshot();
          closeImpactDrawer();
        } else {
          showToast(data.error || 'Error procesando compuerta', 'error');
        }
      } catch (e) {
        console.error(e);
        showToast('Error de comunicación', 'error');
      }
    }

    async function inspectDiffAndImpact(gateId) {
      try {
        const res = await fetch(`${API_BASE}/api/gates/impact?request_id=${gateId}`);
        const data = await res.json();
        document.getElementById('diff-req-id').innerText = data.request_id;
        document.getElementById('diff-action-name').innerText = data.action;
        document.getElementById('diff-code-block').innerText = data.git_context?.diff_preview || 'No hay cambios en diff unificado';
        
        const commitsList = document.getElementById('diff-commits-list');
        commitsList.innerHTML = (data.git_context?.commits || []).map(c => `
          <div class="p-2 rounded bg-black/60 border bd text-xs flex items-center justify-between">
            <span class="mono text-amber-400 font-semibold">${c.sha}</span>
            <span class="text-zinc-200 truncate flex-1 mx-2">${c.subject}</span>
            <span class="mono text-[10px] text-zinc-400">${c.author}</span>
          </div>
        `).join('') || '<div class="text-xs text-zinc-400">No hay commits recientes</div>';

        document.getElementById('impact-drawer').classList.remove('translate-x-full');
      } catch (e) {
        console.error(e);
        showToast('Error cargando diff', 'error');
      }
    }

    async function launchActiveCampaign() {
      try {
        showToast('Lanzando sprint y activando DAG...', 'info');
        const res = await fetch(`${API_BASE}/api/campaigns/launch`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ campaign_id: 'SACL_ORCHESTRATOR_IMPLEMENTATION_CAMPAIGN_v1_PREPARED' })
        });
        const data = await res.json();
        if (data.success) {
          showToast(`Sprint activo (${data.run_id})`, 'success');
          loadDashboardSnapshot();
        }
      } catch (e) {
        showToast('Error lanzando sprint', 'error');
      }
    }

    function simulateProgressStep() {
      const circle = document.getElementById('revolut-donut-circle');
      const text = document.getElementById('revolut-donut-text');
      let current = parseInt(text.innerText) || 75;
      let next = current >= 100 ? 25 : current + 15;
      text.innerText = next + '%';
      
      const circumference = 264;
      const offset = circumference - (next / 100 * circumference);
      circle.style.strokeDashoffset = offset;
      showToast(`Telemetría actualizada al ${next}%`, 'success');
    }

    // Chat
    async function sendChatMessage() {
      const input = document.getElementById('chat-input');
      const prompt = input.value.trim();
      if (!prompt) return;

      appendChatMessage('user', prompt);
      input.value = '';

      try {
        const res = await fetch(`${API_BASE}/api/chat/message`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: prompt, model_id: 'claude-3-7-sonnet' })
        });
        const data = await res.json();
        if (data.success && data.assistant_message) {
          appendChatMessage('assistant', data.assistant_message.content);
        }
      } catch (e) {
        appendChatMessage('assistant', 'Error de comunicación con el orquestador.');
      }
    }

    function sendQuickPrompt(text) {
      switchSection('chat');
      document.getElementById('chat-input').value = text;
      sendChatMessage();
    }

    function handleChatKeyDown(event) {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendChatMessage();
      }
    }

    function appendChatMessage(role, text) {
      const container = document.getElementById('chat-messages-container');
      const msg = document.createElement('div');
      msg.className = `p-4 rounded-2xl max-w-xl text-xs leading-relaxed ${role === 'user' ? 'bg-white/10 ml-auto text-white border bd' : 'bg-[#101016] mr-auto text-zinc-300 border bd'}`;
      let formatted = text.split(String.fromCharCode(10)).join('<br>');
      formatted = formatted.split('**').map((part, idx) => idx % 2 === 1 ? ('<strong>' + part + '</strong>') : part).join('');
      formatted = formatted.split('`').map((part, idx) => idx % 2 === 1 ? ('<code class="mono text-zinc-200 bg-white/10 px-1 py-0.5 rounded">' + part + '</code>') : part).join('');
      msg.innerHTML = formatted;
      container.appendChild(msg);
      document.getElementById('chat-messages-scroll').scrollTop = document.getElementById('chat-messages-scroll').scrollHeight;
    }

    // Init
    window.addEventListener('DOMContentLoaded', () => {
      lucide.createIcons();
      loadDashboardSnapshot();
      loadProjects();
    });
  </script>
</body>
</html>
"""
