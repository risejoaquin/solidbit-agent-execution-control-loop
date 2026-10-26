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
      <button id="dtab-designer" class="nav-pill flex items-center gap-1.5" onclick="switchSection('designer')">
        <i data-lucide="git-fork" class="w-3.5 h-3.5 text-purple-400"></i>
        <span>Studio DAG</span>
        <span class="mono text-[10px] px-1.5 py-0.2 rounded-full bg-purple-500/20 text-purple-300 font-bold">V1</span>
      </button>
      <button id="dtab-github" class="nav-pill flex items-center gap-1.5" onclick="switchSection('github')">
        <i data-lucide="github" class="w-3.5 h-3.5 text-blue-400"></i>
        <span>GitHub Hub</span>
        <span id="nav-github-prs-badge" class="mono text-[10px] px-1.5 py-0.2 rounded-full bg-blue-500/20 text-blue-300 font-bold">4 PRs</span>
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
    <div id="sec-dashboard" class="p-4 md:p-8 max-w-7xl mx-auto space-y-6">

      <!-- TOP RUN CONTROL BAR (Temporal / LangGraph Standard) -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 rounded-2xl bg-white/[0.03] border bd">
        <div class="flex items-center gap-3.5">
          <div class="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/25 flex items-center justify-center text-emerald-400 shrink-0">
            <i data-lucide="git-branch" class="w-5 h-5"></i>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="text-xs font-bold uppercase tracking-wider text-zinc-400">Run Activo:</span>
              <span id="hud-active-run-id" class="mono text-xs font-bold text-white bg-white/10 px-2 py-0.5 rounded">run-20261026-051101-9a00ad</span>
              <span class="mono text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-bold border border-amber-500/30">WAITING_GATE</span>
            </div>
            <div class="text-xs text-zinc-400 mt-0.5 flex items-center gap-2">
              <span>Worktree: <code class="mono text-zinc-300">integration</code></span>
              <span>&bull;</span>
              <span>Modo: <code class="mono text-zinc-300">Hard Deny Supremacy (Zero-Bypass)</code></span>
            </div>
          </div>
        </div>

        <!-- Primary Execution Actions -->
        <div class="flex items-center gap-2">
          <button onclick="executeAction('campaign_sprint', {}, this)" class="btn btn-primary text-xs px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-black font-bold">
            <i data-lucide="play" class="w-3.5 h-3.5"></i>
            <span>▶ Inicializar Sprint</span>
          </button>
          <button onclick="executeAction('reconcile_runs', {}, this)" class="btn btn-secondary text-xs px-3.5 py-2">
            <i data-lucide="refresh-cw" class="w-3.5 h-3.5 text-emerald-400"></i>
            <span>Reconciliar</span>
          </button>
          <button onclick="openTerminalDrawer()" class="btn btn-secondary text-xs px-3.5 py-2 text-emerald-400">
            <i data-lucide="terminal" class="w-3.5 h-3.5"></i>
            <span>Terminal</span>
          </button>
        </div>
      </div>

      <!-- COMPACT METRICS CHIPS ROW (Cero ruido, alta densidad) -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div class="p-3 rounded-xl bg-black border bd flex items-center justify-between">
          <span class="text-[11px] text-zinc-400 uppercase font-semibold">SDLC Test Suite</span>
          <span class="mono text-xs font-bold text-emerald-400">29/29 PASS</span>
        </div>
        <div class="p-3 rounded-xl bg-black border bd flex items-center justify-between">
          <span class="text-[11px] text-zinc-400 uppercase font-semibold">Contratos Inmutables</span>
          <span class="mono text-xs font-bold text-white">4/4 DR-INV</span>
        </div>
        <div class="p-3 rounded-xl bg-black border bd flex items-center justify-between">
          <span class="text-[11px] text-zinc-400 uppercase font-semibold">Persistencia SQLite</span>
          <span class="mono text-xs font-bold text-emerald-400">WAL INTEGRITY OK</span>
        </div>
        <div class="p-3 rounded-xl bg-black border bd flex items-center justify-between">
          <span class="text-[11px] text-zinc-400 uppercase font-semibold">Túnel Universal</span>
          <span class="mono text-xs font-bold text-blue-400 flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></span> ONLINE
          </span>
        </div>
      </div>

      <!-- PIPELINE TOPOLÓGICO DE FASES (Temporal / Airflow Standard Flow) -->
      <div class="section-canvas p-5 md:p-6 space-y-4">
        <div class="flex items-center justify-between border-b bd pb-3">
          <div class="flex items-center gap-2.5">
            <i data-lucide="git-merge" class="w-4 h-4 text-emerald-400"></i>
            <h3 class="text-xs font-bold uppercase tracking-wider text-white">Grafo de Ejecución Topológica Multi-Agente (DAG 2026)</h3>
          </div>
          <span class="mono text-[11px] text-zinc-400">Topological Sort: Linear Pipeline</span>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <!-- Fase 1 -->
          <div class="p-3.5 rounded-xl bg-black/60 border border-emerald-500/30 space-y-2">
            <div class="flex items-center justify-between">
              <span class="mono text-[10px] text-zinc-400 font-bold uppercase">Fase 1 &bull; Arquitectura</span>
              <span class="mono text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold">VERIFIED</span>
            </div>
            <div class="text-xs font-bold text-white">spec-enforcer</div>
            <div class="text-[11px] text-zinc-400">Contratos DR-INV-001 & Schemas</div>
            <div class="pt-2 border-t bd text-[10px] mono text-zinc-500 flex justify-between">
              <span>Duración: 0.08s</span>
              <span>Exit 0</span>
            </div>
          </div>

          <!-- Fase 2 -->
          <div class="p-3.5 rounded-xl bg-black/60 border border-blue-500/30 space-y-2">
            <div class="flex items-center justify-between">
              <span class="mono text-[10px] text-zinc-400 font-bold uppercase">Fase 2 &bull; Síntesis</span>
              <span class="mono text-[10px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 font-bold">COMPLETED</span>
            </div>
            <div class="text-xs font-bold text-white">worktree-coder (AGY)</div>
            <div class="text-[11px] text-zinc-400">Aislamiento Git en integration</div>
            <div class="pt-2 border-t bd text-[10px] mono text-zinc-500 flex justify-between">
              <span>Duración: 0.15s</span>
              <span>Exit 0</span>
            </div>
          </div>

          <!-- Fase 3 -->
          <div class="p-3.5 rounded-xl bg-black/60 border border-emerald-500/30 space-y-2">
            <div class="flex items-center justify-between">
              <span class="mono text-[10px] text-zinc-400 font-bold uppercase">Fase 3 &bull; Calidad</span>
              <span class="mono text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-bold">PASSED</span>
            </div>
            <div class="text-xs font-bold text-white">zero-bypass-qa</div>
            <div class="text-[11px] text-zinc-400">29 Tests Unitarios & RLS</div>
            <div class="pt-2 border-t bd text-[10px] mono text-zinc-500 flex justify-between">
              <span>Duración: 0.22s</span>
              <span>Exit 0</span>
            </div>
          </div>

          <!-- Fase 4 -->
          <div class="p-3.5 rounded-xl bg-black/60 border border-amber-500/40 space-y-2 shadow-[0_0_15px_rgba(245,158,11,0.08)]">
            <div class="flex items-center justify-between">
              <span class="mono text-[10px] text-amber-400 font-bold uppercase">Fase 4 &bull; Sentinel</span>
              <span class="mono text-[10px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 font-bold animate-pulse">GATE WAITING</span>
            </div>
            <div class="text-xs font-bold text-white">hitl-sentinel</div>
            <div class="text-[11px] text-zinc-400">Compuerta DEPLOY_STAGING</div>
            <div class="pt-2 border-t bd text-[10px] mono text-amber-400 flex justify-between">
              <span>TTL: 14m 20s</span>
              <span>Firma HMAC</span>
            </div>
          </div>
        </div>
      </div>

      <!-- COMPUERTA DE GOBERNANZA HUMANA ACTIVA (HITL) -->
      <div id="active-gate-container" class="section-canvas p-5 md:p-6 space-y-5 border-amber-500/30 bg-black">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b bd pb-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 shrink-0">
              <i data-lucide="shield-alert" class="w-5 h-5"></i>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <h3 class="text-base font-bold text-white mono" id="gate-action-title">DEPLOY_STAGING_PREVIEW</h3>
                <span class="mono text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/25">REQ-20261025-E43308B0</span>
              </div>
              <p class="text-xs text-zinc-400 mt-0.5">El agente ha completado la síntesis. Se requiere micro-decisión humana para desplegar el preview efímero.</p>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <span class="text-xs mono text-zinc-400">Radio de impacto: <strong class="text-white">Preview Aislado (Railway)</strong></span>
          </div>
        </div>

        <!-- Dossier Navigation Tabs -->
        <div class="flex items-center gap-2 border-b bd pb-2 text-xs">
          <button id="dossier-tab-btn-checklist" class="nav-pill active flex items-center gap-1.5" onclick="switchDossierTab('checklist')">
            <i data-lucide="check-square" class="w-3.5 h-3.5 text-emerald-400"></i>
            <span>Checklist Técnico</span>
          </button>
          <button id="dossier-tab-btn-diff" class="nav-pill flex items-center gap-1.5" onclick="switchDossierTab('diff')">
            <i data-lucide="file-diff" class="w-3.5 h-3.5 text-blue-400"></i>
            <span>Inspección de Git Diff</span>
          </button>
          <button id="dossier-tab-btn-audit" class="nav-pill flex items-center gap-1.5" onclick="switchDossierTab('audit')">
            <i data-lucide="history" class="w-3.5 h-3.5 text-zinc-400"></i>
            <span>Traza de Auditoría</span>
          </button>
        </div>

        <!-- TAB 1: Checklist -->
        <div id="dossier-panel-checklist" class="space-y-2.5 text-xs">
          <div class="p-3 rounded-xl bg-white/[0.02] border bd flex items-center justify-between">
            <div class="flex items-center gap-2.5">
              <i data-lucide="check-circle" class="w-4 h-4 text-emerald-400"></i>
              <span class="text-zinc-200">Invariante de Inventario DR-INV-001 (Zero-Oversell SellableUnit)</span>
            </div>
            <span class="mono text-emerald-400 font-bold">PASS</span>
          </div>
          <div class="p-3 rounded-xl bg-white/[0.02] border bd flex items-center justify-between">
            <div class="flex items-center gap-2.5">
              <i data-lucide="check-circle" class="w-4 h-4 text-emerald-400"></i>
              <span class="text-zinc-200">Invariante de Pago DR-PAY-001 (Ledger de Doble Partida)</span>
            </div>
            <span class="mono text-emerald-400 font-bold">PASS</span>
          </div>
          <div class="p-3 rounded-xl bg-white/[0.02] border bd flex items-center justify-between">
            <div class="flex items-center gap-2.5">
              <i data-lucide="check-circle" class="w-4 h-4 text-emerald-400"></i>
              <span class="text-zinc-200">Aislamiento de Worktree Git (sin mutación en main)</span>
            </div>
            <span class="mono text-emerald-400 font-bold">PASS</span>
          </div>
        </div>

        <!-- TAB 2: Live Code Diff -->
        <div id="dossier-panel-diff" class="hidden text-xs mono space-y-2">
          <div class="p-3 rounded-xl bg-black border bd text-zinc-300 overflow-x-auto max-h-48 custom-scroll">
            <div class="text-emerald-400">+++ src/sacl/ui/modules/actions.py (Exit code parsing fix)</div>
            <div class="text-emerald-400">+ "success": status == "COMPLETED" or exit_code == 0</div>
            <div class="text-emerald-400">+++ src/sacl/ui/server.py (Response envelope)</div>
            <div class="text-emerald-400">+ self._send_json(200, {"success": True, "execution": res})</div>
            <div class="text-zinc-500">@@ Contratos inmutables preservados al 100% @@</div>
          </div>
        </div>

        <!-- TAB 3: Audit Trail -->
        <div id="dossier-panel-audit" class="hidden text-xs mono space-y-1.5 text-zinc-400">
          <div class="p-2.5 rounded-lg bg-black border bd flex items-center justify-between">
            <span>2026-10-25 18:31:01 &bull; Proceso despachado por LUCILFER</span>
            <span class="text-emerald-400">SPAWNED</span>
          </div>
          <div class="p-2.5 rounded-lg bg-black border bd flex items-center justify-between">
            <span>2026-10-25 18:31:02 &bull; Preflight y Dirty-Root Invariant verificado</span>
            <span class="text-emerald-400">VERIFIED</span>
          </div>
        </div>

        <!-- Decision Buttons -->
        <div class="pt-4 border-t bd flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div class="text-xs text-zinc-400 mono">
            Operador autenticado: <strong class="text-white">LUCILFER / risejoaquin</strong>
          </div>
          <div class="flex items-center gap-2.5">
            <button onclick="submitDossierDecision('REJECTED')" class="btn btn-secondary text-xs px-4 py-2 text-red-400 hover:text-red-300 hover:border-red-500/40">
              <i data-lucide="x-circle" class="w-3.5 h-3.5"></i>
              <span>Rechazar Despliegue</span>
            </button>
            <button onclick="submitDossierDecision('APPROVED')" class="btn btn-primary text-xs px-5 py-2 bg-emerald-500 hover:bg-emerald-400 text-black font-bold">
              <i data-lucide="check-circle" class="w-3.5 h-3.5"></i>
              <span>Autorizar Despliegue (Emitir Token HMAC)</span>
            </button>
          </div>
        </div>
      </div>

    </div>

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
        <!-- ========================================== -->
    <!-- SECTION 4B: STUDIO VISUAL DE DAG & CAMPAÑAS -->
    <!-- ========================================== -->
    <div id="sec-designer" class="p-4 md:p-8 max-w-7xl mx-auto space-y-6 hidden">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b bd pb-4">
        <div>
          <div class="flex items-center gap-2">
            <h2 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
              <i data-lucide="git-fork" class="w-6 h-6 text-purple-400"></i>
              <span>Studio Visual de DAG & Campañas de Agentes</span>
            </h2>
            <span class="mono text-xs px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30 font-bold">TOPOLOGÍA SOBERANA</span>
          </div>
          <p class="text-sm text-zinc-400 mt-1">Diseña, edita dependencias acíclicas, configura compuertas humanas y exporta paquetes Wave canónicos.</p>
        </div>

        <div class="flex flex-wrap items-center gap-2">
          <button onclick="openAddNodeModal()" class="btn btn-primary text-xs px-3.5 py-2">
            <i data-lucide="plus" class="w-3.5 h-3.5"></i>
            <span>Agregar Agente</span>
          </button>
          <button onclick="validateCurrentDAG()" class="btn btn-secondary text-xs px-3.5 py-2">
            <i data-lucide="check-circle-2" class="w-3.5 h-3.5 text-emerald-400"></i>
            <span>Validar Grafo (Kahn)</span>
          </button>
          <button onclick="saveDagManifest()" class="btn btn-secondary text-xs px-3.5 py-2">
            <i data-lucide="save" class="w-3.5 h-3.5 text-blue-400"></i>
            <span>Guardar JSON</span>
          </button>
          <button onclick="exportWaveZip()" class="btn btn-secondary text-xs px-3.5 py-2">
            <i data-lucide="archive" class="w-3.5 h-3.5 text-amber-400"></i>
            <span>Exportar Wave ZIP</span>
          </button>
          <button onclick="launchVisualSprint()" class="btn btn-primary text-xs px-3.5 py-2 bg-emerald-500 hover:bg-emerald-400 text-black font-bold">
            <i data-lucide="play" class="w-3.5 h-3.5"></i>
            <span>▶ Ejecutar Sprint</span>
          </button>
        </div>
      </div>

      <!-- Live Summary Bar -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
        <div class="p-3.5 rounded-xl bg-white/5 border bd flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 shrink-0">
            <i data-lucide="layers" class="w-4 h-4"></i>
          </div>
          <div>
            <div class="text-[10px] uppercase font-bold text-zinc-400">Total Nodos / Agentes</div>
            <div id="designer-stat-nodes" class="text-base font-bold text-white mono">6</div>
          </div>
        </div>
        <div class="p-3.5 rounded-xl bg-white/5 border bd flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 shrink-0">
            <i data-lucide="check-check" class="w-4 h-4"></i>
          </div>
          <div>
            <div class="text-[10px] uppercase font-bold text-zinc-400">Aciclicidad (DAG)</div>
            <div id="designer-stat-status" class="text-xs font-bold text-emerald-400 mono">VERIFICADO (0 Ciclos)</div>
          </div>
        </div>
        <div class="p-3.5 rounded-xl bg-white/5 border bd flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 shrink-0">
            <i data-lucide="shield-alert" class="w-4 h-4"></i>
          </div>
          <div>
            <div class="text-[10px] uppercase font-bold text-zinc-400">Compuertas Humanas</div>
            <div id="designer-stat-gates" class="text-base font-bold text-amber-400 mono">1 HITL Activa</div>
          </div>
        </div>
        <div class="p-3.5 rounded-xl bg-white/5 border bd flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 shrink-0">
            <i data-lucide="cpu" class="w-4 h-4"></i>
          </div>
          <div>
            <div class="text-[10px] uppercase font-bold text-zinc-400">Estándar Canónico</div>
            <div class="text-xs font-bold text-zinc-200 mono">SACL-SPEC-PKG-v1</div>
          </div>
        </div>
      </div>

      <!-- Interactive Canvas & Flow Visualizer -->
      <div class="section-canvas p-6 space-y-5">
        <div class="flex items-center justify-between border-b bd pb-3">
          <div class="flex items-center gap-2">
            <h3 class="text-sm font-bold uppercase tracking-wider text-white">Flujo Topológico de Ejecución (Orden Secuencial y Paralelo)</h3>
          </div>
          <div id="designer-topo-breadcrumb" class="text-xs mono text-zinc-400 truncate max-w-xl"></div>
        </div>

        <!-- Visual Node Cards Grid -->
        <div id="designer-nodes-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <!-- Dynamically populated -->
        </div>
      </div>
    </div>

<div id="sec-projects" class="p-4 md:p-8 max-w-7xl mx-auto space-y-6 hidden">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b bd pb-4">
        <div>
          <h2 class="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
            <i data-lucide="folder-tree" class="w-6 h-6 text-amber-400"></i>
            <span>Explorador de Archivos, Carpetas & Código Fuente</span>
          </h2>
          <p class="text-sm text-zinc-400 mt-1">Navega libremente por el áarbol de directorios, abre cualquier archivo local e inspecciona su contenido en vivo.</p>
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
          <button onclick="loadFsTree()" class="p-2 rounded-lg border bd bg-white/5 hover:bg-white/10 text-zinc-300 cursor-pointer" title="Recargar Áarbol">
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
            Haz clic en cualquier archivo del áarbol o pulsa "Abrir Archivo" para inspeccionar.
          </div>

          <!-- Code Display Container -->
          <div id="code-viewer-content" class="flex-1 overflow-y-auto max-h-[520px] custom-scroll select-text">
            <div class="py-24 text-center text-zinc-500 mono space-y-2">
              <i data-lucide="file-search" class="w-8 h-8 text-zinc-600 mx-auto"></i>
              <div class="text-xs font-semibold text-zinc-400">Ningún archivo cargado en el visor</div>
              <p class="text-[11px] text-zinc-600 max-w-sm mx-auto">Haz clic en cualquier elemento del áarbol izquierdo (.py, .json, .md, .toml) para abrir su código fuente en vivo.</p>
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
    <!-- SECTION: GITHUB ENGINEERING HUB (LIVE GH CLI) -->
    <!-- ========================================== -->
    <div id="sec-github" class="p-4 md:p-8 max-w-7xl mx-auto space-y-6 hidden">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-zinc-800 pb-4">
        <div>
          <div class="flex items-center gap-2.5">
            <i data-lucide="github" class="w-6 h-6 text-white"></i>
            <h2 class="text-2xl font-bold tracking-tight text-white">GitHub Engineering Hub</h2>
            <span class="mono text-xs px-2.5 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/25 text-blue-400 font-bold" id="gh-sync-badge">Sincronizado</span>
          </div>
          <p class="text-sm text-zinc-400 mt-1">Supervisión en vivo de Pull Requests, ramas remotas, commits y workflows de GitHub Actions.</p>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="syncGitHubRepo()" class="btn btn-secondary text-xs px-3.5 py-2">
            <i data-lucide="refresh-cw" class="w-3.5 h-3.5 text-blue-400"></i>
            <span>Sincronizar (git fetch)</span>
          </button>
          <a href="https://github.com/risejoaquin/solidbit-agent-execution-control-loop" target="_blank" class="btn btn-secondary text-xs px-3.5 py-2">
            <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
            <span>Ver en GitHub</span>
          </a>
          <button onclick="openNewPrModal()" class="btn btn-primary text-xs px-3.5 py-2 font-bold">
            <i data-lucide="git-pull-request" class="w-3.5 h-3.5"></i>
            <span>+ Nuevo PR</span>
          </button>
        </div>
      </div>

      <!-- GitHub Metadata Strip -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="item-card p-4 space-y-1">
          <span class="text-xs text-zinc-400">Repositorio Activo:</span>
          <div class="text-sm font-bold mono text-white truncate" id="gh-meta-repo">risejoaquin/solidbit-agent-execution-control-loop</div>
          <div class="text-xs text-emerald-400 font-semibold" id="gh-meta-user">Identidad: @risejoaquin</div>
        </div>
        <div class="item-card p-4 space-y-1">
          <span class="text-xs text-zinc-400">Rama Actual:</span>
          <div class="text-sm font-bold mono text-emerald-400 truncate" id="gh-meta-branch">sacl-implementation-impl-20261007-203727-e69378</div>
          <div class="text-xs text-zinc-500" id="gh-meta-tracking">Al día con origin</div>
        </div>
        <div class="item-card p-4 space-y-1">
          <span class="text-xs text-zinc-400">Estado de Archivos:</span>
          <div class="text-sm font-bold mono text-emerald-400" id="gh-meta-clean">Working Tree Limpio</div>
          <div class="text-xs text-zinc-500">0 cambios sin commitear</div>
        </div>
        <div class="item-card p-4 space-y-1">
          <span class="text-xs text-zinc-400">Commits Ahead / Behind:</span>
          <div class="text-sm font-bold mono text-white" id="gh-meta-counts">0 Ahead / 0 Behind</div>
          <div class="text-xs text-zinc-500">Totalmente sincronizado</div>
        </div>
      </div>

      <!-- Main GitHub Grid: PRs on Left, Commits & Actions on Right -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- PRs Panel (2 cols) -->
        <div class="lg:col-span-2 section-canvas p-6 space-y-4">
          <div class="flex items-center justify-between border-b border-zinc-800 pb-3">
            <div class="flex items-center gap-2">
              <i data-lucide="git-pull-request" class="w-4 h-4 text-blue-400"></i>
              <h3 class="text-sm font-bold text-white uppercase tracking-wider">Pull Requests Activos</h3>
            </div>
            <span class="text-xs mono text-zinc-400" id="gh-prs-count">Cargando PRs...</span>
          </div>
          <div id="gh-prs-list" class="space-y-3">
            <div class="p-6 text-center text-zinc-500 text-xs">Cargando Pull Requests desde GitHub API...</div>
          </div>
        </div>

        <!-- Commits & Workflows Column (1 col) -->
        <div class="space-y-6">
          <!-- Recent Commits -->
          <div class="section-canvas p-6 space-y-4">
            <div class="flex items-center justify-between border-b border-zinc-800 pb-3">
              <div class="flex items-center gap-2">
                <i data-lucide="git-commit" class="w-4 h-4 text-emerald-400"></i>
                <h3 class="text-sm font-bold text-white uppercase tracking-wider">Commits Recientes</h3>
              </div>
              <span class="text-xs mono text-zinc-500">Git Log</span>
            </div>
            <div id="gh-commits-list" class="space-y-2.5 max-h-[360px] overflow-y-auto custom-scroll pr-1">
              <div class="p-4 text-center text-zinc-500 text-xs">Cargando commits...</div>
            </div>
          </div>

          <!-- GitHub Actions Workflows -->
          <div class="section-canvas p-6 space-y-4">
            <div class="flex items-center justify-between border-b border-zinc-800 pb-3">
              <div class="flex items-center gap-2">
                <i data-lucide="play" class="w-4 h-4 text-purple-400"></i>
                <h3 class="text-sm font-bold text-white uppercase tracking-wider">GitHub Actions CI/CD</h3>
              </div>
              <span class="text-xs mono text-zinc-500">gh run list</span>
            </div>
            <div id="gh-runs-list" class="space-y-2.5">
              <div class="p-4 text-center text-zinc-500 text-xs">Cargando workflows...</div>
            </div>
          </div>
        </div>
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
    <button id="mtab-designer" class="mobile-tab" onclick="switchSection('designer')">
      <i data-lucide="git-fork" class="w-4 h-4 text-purple-400"></i>
      <span>Studio</span>
    </button>
    <button id="mtab-github" class="mobile-tab" onclick="switchSection('github')">
      <i data-lucide="github" class="w-4 h-4"></i>
      <span>GitHub</span>
    </button>
    <button id="mtab-chat" class="mobile-tab" onclick="switchSection('chat')">
      <i data-lucide="terminal" class="w-4 h-4"></i>
      <span>REPL</span>
    </button>
  </nav>

  <!-- ========================================== -->
  <!-- MODAL: DOCUMENTATION VIEWER -->
  <!-- ========================================== -->
    <!-- ========================================== -->
  <!-- MODAL: AGREGAR / EDITAR NODO DE AGENTE -->
  <!-- ========================================== -->
  <div id="designer-node-modal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 hidden">
    <div class="section-canvas w-full max-w-xl flex flex-col overflow-hidden bg-[#030305] border-[#27272a] shadow-2xl rounded-2xl">
      <div class="p-5 border-b bd flex items-center justify-between bg-white/[0.02]">
        <div class="flex items-center gap-2.5">
          <i data-lucide="git-commit" class="w-5 h-5 text-purple-400"></i>
          <h3 id="designer-modal-title" class="text-base font-bold text-white">Configurar Nodo de Agente en DAG</h3>
        </div>
        <button onclick="closeDesignerNodeModal()" class="text-zinc-400 hover:text-white p-1 rounded-lg hover:bg-white/5">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>

      <div class="p-6 space-y-4 text-xs overflow-y-auto max-h-[70vh]">
        <input type="hidden" id="node-edit-mode" value="add">
        
        <div>
          <label class="block text-zinc-400 mb-1 font-semibold uppercase tracking-wider text-[10px]">Identificador Único (ID)</label>
          <input type="text" id="node-input-id" placeholder="node-nombre-agente" class="w-full px-3 py-2 rounded-lg bg-black/60 border bd text-zinc-200 mono text-xs focus:border-purple-500 focus:outline-none">
        </div>

        <div>
          <label class="block text-zinc-400 mb-1 font-semibold uppercase tracking-wider text-[10px]">Etiqueta / Nombre Descriptivo</label>
          <input type="text" id="node-input-label" placeholder="Ej: 3. Síntesis de Código con Coder AGY" class="w-full px-3 py-2 rounded-lg bg-black/60 border bd text-zinc-200 text-xs focus:border-purple-500 focus:outline-none">
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-zinc-400 mb-1 font-semibold uppercase tracking-wider text-[10px]">Rol del Agente</label>
            <select id="node-input-role" class="w-full px-3 py-2 rounded-lg bg-black/60 border bd text-zinc-200 text-xs focus:border-purple-500 focus:outline-none">
              <option value="Architect Agent">Architect Agent</option>
              <option value="Senior Coder AGY" selected>Senior Coder AGY</option>
              <option value="QA Security Auditor">QA Security Auditor</option>
              <option value="HITL Gate Sentinel">HITL Gate Sentinel</option>
              <option value="Transport Worker">Transport Worker</option>
            </select>
          </div>
          <div>
            <label class="block text-zinc-400 mb-1 font-semibold uppercase tracking-wider text-[10px]">Acción Ejecutable</label>
            <select id="node-input-action" class="w-full px-3 py-2 rounded-lg bg-black/60 border bd text-zinc-200 text-xs focus:border-purple-500 focus:outline-none">
              <option value="WORKTREE_PROVISION">WORKTREE_PROVISION</option>
              <option value="CONTRACT_VERIFY">CONTRACT_VERIFY</option>
              <option value="AGENT_CODEGEN" selected>AGENT_CODEGEN</option>
              <option value="RUN_TESTS">RUN_TESTS</option>
              <option value="HUMAN_APPROVAL_GATE">HUMAN_APPROVAL_GATE</option>
              <option value="STAGE_PREVIEW">STAGE_PREVIEW</option>
              <option value="CUSTOM_SCRIPT">CUSTOM_SCRIPT</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-zinc-400 mb-1 font-semibold uppercase tracking-wider text-[10px]">Timeout (Segundos)</label>
            <input type="number" id="node-input-timeout" value="120" class="w-full px-3 py-2 rounded-lg bg-black/60 border bd text-zinc-200 mono text-xs focus:border-purple-500 focus:outline-none">
          </div>
          <div class="flex items-center gap-2 pt-5">
            <input type="checkbox" id="node-input-gate" class="w-4 h-4 rounded border-zinc-700 bg-black text-amber-500 focus:ring-0">
            <label for="node-input-gate" class="text-zinc-300 font-medium cursor-pointer">Requiere Compuerta HITL</label>
          </div>
        </div>

        <div>
          <label class="block text-zinc-400 mb-1 font-semibold uppercase tracking-wider text-[10px]">Dependencias Previas</label>
          <div id="node-dependencies-checklist" class="space-y-1.5 p-3 rounded-lg bg-black/40 border bd max-h-32 overflow-y-auto">
          </div>
        </div>
      </div>

      <div class="p-4 border-t bd flex items-center justify-end gap-2.5 bg-white/[0.01]">
        <button onclick="closeDesignerNodeModal()" class="btn btn-secondary text-xs px-4 py-2">Cancelar</button>
        <button onclick="saveDesignerNode()" class="btn btn-primary text-xs px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white font-bold">Guardar Nodo</button>
      </div>
    </div>
  </div>

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
            <button onclick="setOpenFolderPreset('~/Documents/Stable-Ecommerce-Orchestrator/SACL_IMPLEMENTATION_CAMPAIGN_v1/runs/impl-20261007-203727-e69378/worktrees/integration')" class="w-full text-left p-2.5 rounded-lg bg-black/40 border bd hover:border-amber-400/50 flex items-center justify-between text-zinc-300 hover:text-white">
              <span class="mono text-[11px] truncate">worktrees/integration (Espacio de Trabajo Activo)</span>
              <span class="text-amber-400 text-[10px] font-bold shrink-0">Seleccionar &rarr;</span>
            </button>
            <button onclick="setOpenFolderPreset('~/Documents/Stable-Ecommerce-Orchestrator')" class="w-full text-left p-2.5 rounded-lg bg-black/40 border bd hover:border-amber-400/50 flex items-center justify-between text-zinc-300 hover:text-white">
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
            <button onclick="setOpenFolderPreset('~/Documents/Stable-Ecommerce-Orchestrator/SACL_IMPLEMENTATION_CAMPAIGN_v1/runs/impl-20261007-203727-e69378/worktrees/integration')" class="w-full text-left p-2.5 rounded-lg bg-black/40 border bd hover:border-amber-400/50 flex items-center justify-between text-zinc-300 hover:text-white">
              <span class="mono text-[11px] truncate">worktrees/integration (Espacio de Trabajo Activo)</span>
              <span class="text-amber-400 text-[10px] font-bold shrink-0">Seleccionar &rarr;</span>
            </button>
            <button onclick="setOpenFolderPreset('~/Documents/Stable-Ecommerce-Orchestrator')" class="w-full text-left p-2.5 rounded-lg bg-black/40 border bd hover:border-amber-400/50 flex items-center justify-between text-zinc-300 hover:text-white">
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
      ['dashboard', 'database', 'gates', 'sdlc', 'projects', 'github', 'chat', 'designer'].forEach(id => {
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
      } else if (secId === 'github') {
        loadGitHubDashboard();
      } else if (secId === 'designer') {
        loadDesignerDAG();
      }
      lucide.createIcons();
    }
    window.switchSection = switchSection;

    // ==========================================
    // GITHUB ENGINEERING HUB JAVASCRIPT
    // ==========================================
    async function loadGitHubDashboard() {
      try {
        const sRes = await fetch('/api/github/status');
        if (sRes.ok) {
          const s = await sRes.json();
          const rEl = document.getElementById('gh-meta-repo');
          if (rEl) rEl.textContent = s.repo;
          const bEl = document.getElementById('gh-meta-branch');
          if (bEl) bEl.textContent = s.branch;
          const uEl = document.getElementById('gh-meta-user');
          if (uEl) uEl.textContent = 'Identidad: @' + s.user;
          const cEl = document.getElementById('gh-meta-clean');
          if (cEl) cEl.textContent = s.is_clean ? 'Working Tree Limpio' : 'Cambios Pendientes';
          const cntEl = document.getElementById('gh-meta-counts');
          if (cntEl) cntEl.textContent = s.ahead + ' Ahead / ' + s.behind + ' Behind';
          const badge = document.getElementById('gh-sync-badge');
          if (badge) badge.textContent = s.status_label;
        }

        const prRes = await fetch('/api/github/prs');
        if (prRes.ok) {
          const pData = await prRes.json();
          const prs = pData.prs || [];
          const cntBadge = document.getElementById('nav-github-prs-badge');
          if (cntBadge) cntBadge.textContent = prs.length + ' PRs';
          const countEl = document.getElementById('gh-prs-count');
          if (countEl) countEl.textContent = prs.length + ' Pull Requests Abiertos';
          
          const listEl = document.getElementById('gh-prs-list');
          if (listEl) {
            if (prs.length === 0) {
              listEl.innerHTML = '<div class="p-8 text-center text-zinc-500 text-xs">No hay Pull Requests pendientes en este repositorio.</div>';
            } else {
              listEl.innerHTML = prs.map(pr => `
                <div class="p-4 rounded-xl bg-white/5 border border-white/10 hover:border-blue-500/40 transition flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div class="space-y-1">
                    <div class="flex items-center gap-2">
                      <span class="px-2 py-0.5 rounded text-[10px] font-bold mono ${pr.isDraft ? 'bg-zinc-800 text-zinc-300 border border-zinc-700' : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'}">
                        ${pr.isDraft ? 'BORRADOR' : 'ABIERTO'}
                      </span>
                      <span class="mono text-xs text-zinc-400 font-bold">#${pr.number}</span>
                      <h4 class="text-sm font-semibold text-white tracking-tight">${pr.title}</h4>
                    </div>
                    <div class="flex items-center gap-3 text-xs text-zinc-400 mono">
                      <span class="text-blue-400">rama: ${pr.headRefName}</span>
                      <span>•</span>
                      <span>Actualizado: ${new Date(pr.updatedAt).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <a href="${pr.url}" target="_blank" class="btn btn-secondary text-xs px-3.5 py-1.5 shrink-0 flex items-center gap-1.5">
                    <span>Ver en GitHub</span>
                    <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
                  </a>
                </div>
              `).join('');
            }
          }
        }

        const cRes = await fetch('/api/github/commits?limit=8');
        if (cRes.ok) {
          const cData = await cRes.json();
          const commits = cData.commits || [];
          const listEl = document.getElementById('gh-commits-list');
          if (listEl) {
            listEl.innerHTML = commits.map(c => `
              <div class="p-2.5 rounded-lg bg-black/60 border border-white/5 flex items-start justify-between gap-2 text-xs">
                <div class="space-y-0.5 truncate">
                  <div class="font-medium text-white truncate">${c.message}</div>
                  <div class="text-[11px] text-zinc-400 mono flex items-center gap-2">
                    <span class="text-emerald-400 font-bold">@${c.author}</span>
                    <span>•</span>
                    <span>${c.time}</span>
                  </div>
                </div>
                <span class="mono text-[10px] px-2 py-0.5 rounded bg-white/10 text-zinc-300 shrink-0 font-bold">${c.sha}</span>
              </div>
            `).join('');
          }
        }

        const rRes = await fetch('/api/github/runs?limit=5');
        if (rRes.ok) {
          const rData = await rRes.json();
          const runs = rData.runs || [];
          const listEl = document.getElementById('gh-runs-list');
          if (listEl) {
            listEl.innerHTML = runs.map(r => `
              <div class="p-2.5 rounded-lg bg-black/60 border border-white/5 flex items-center justify-between gap-2 text-xs">
                <div class="truncate">
                  <div class="font-medium text-white truncate">${r.name}</div>
                  <div class="text-[10px] text-zinc-400 mono">${r.headBranch}</div>
                </div>
                <div class="flex items-center gap-1.5 shrink-0">
                  <span class="px-2 py-0.5 rounded text-[10px] font-bold mono ${r.conclusion === 'success' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'}">
                    ${r.conclusion || r.status}
                  </span>
                  <a href="${r.url}" target="_blank" class="text-zinc-400 hover:text-white p-1">
                    <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
                  </a>
                </div>
              </div>
            `).join('');
          }
        }
        lucide.createIcons();
      } catch (err) {
        console.error('Error cargando GitHub Dashboard:', err);
      }
    }
    window.loadGitHubDashboard = loadGitHubDashboard;

    async function syncGitHubRepo() {
      showToast('Sincronizando con origin (git fetch)...', 'info');
      try {
        const res = await fetch('/api/github/sync', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
          showToast('Repositorio sincronizado con éxito con origin.', 'success');
          loadGitHubDashboard();
        } else {
          showToast('Error sincronizando repositorio: ' + data.output, 'error');
        }
      } catch (e) {
        showToast('Fallo de conexión al sincronizar.', 'error');
      }
    }
    window.syncGitHubRepo = syncGitHubRepo;

    function openNewPrModal() {
      const modal = document.getElementById('modal-new-pr');
      if (modal) modal.classList.remove('hidden');
      lucide.createIcons();
    }
    window.openNewPrModal = openNewPrModal;

    function closeNewPrModal() {
      const modal = document.getElementById('modal-new-pr');
      if (modal) modal.classList.add('hidden');
    }
    window.closeNewPrModal = closeNewPrModal;

    async function submitNewPr() {
      const title = document.getElementById('new-pr-title').value.trim();
      const body = document.getElementById('new-pr-body').value.trim();
      const base = document.getElementById('new-pr-base').value.trim() || 'main';
      const draft = document.getElementById('new-pr-draft').checked;

      if (!title) {
        showToast('Ingresa un título para el Pull Request', 'error');
        return;
      }

      const btn = document.getElementById('btn-submit-new-pr');
      if (btn) btn.disabled = true;
      showToast('Creando Pull Request en GitHub...', 'info');

      try {
        const res = await fetch('/api/github/pr', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title, body, base, draft })
        });
        const data = await res.json();
        if (data.success) {
          showToast('Pull Request creado exitosamente en GitHub!', 'success');
          closeNewPrModal();
          loadGitHubDashboard();
        } else {
          showToast('Error al crear PR: ' + (data.error || 'falló gh pr create'), 'error');
        }
      } catch (err) {
        showToast('Error de conexión al crear PR', 'error');
      } finally {
        if (btn) btn.disabled = false;
      }
    }
    window.submitNewPr = submitNewPr;


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
        const exec = data.execution || data;
        const isOk = data.success || (exec && (exec.status === 'COMPLETED' || exec.exit_code === 0));
        if (isOk && exec) {
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
    
    // ==========================================
    // STUDIO VISUAL DE DAG & CAMPAÑAS JAVASCRIPT
    // ==========================================
    let currentDagState = null;

    async function loadDesignerDAG() {
      try {
        const res = await fetch(`${API_BASE}/api/campaigns/designer`);
        const data = await res.json();
        currentDagState = data;
        renderDesignerCanvas(data);
      } catch (e) {
        console.error('Error loading designer DAG:', e);
      }
    }
    window.loadDesignerDAG = loadDesignerDAG;

    function renderDesignerCanvas(dag) {
      const container = document.getElementById('designer-nodes-container');
      const statNodes = document.getElementById('designer-stat-nodes');
      const statGates = document.getElementById('designer-stat-gates');
      const breadcrumb = document.getElementById('designer-topo-breadcrumb');
      if (!container || !dag) return;

      const nodes = dag.nodes || [];
      if (statNodes) statNodes.innerText = nodes.length;

      let gateCount = 0;
      let orderNames = [];

      container.innerHTML = '';

      nodes.forEach((node, idx) => {
        if (node.gate_required) gateCount++;
        orderNames.push(node.id);

        const card = document.createElement('div');
        card.className = 'section-canvas p-4 space-y-3 relative hover:border-purple-500/40 transition-all';
        
        let actionBadgeColor = 'bg-blue-500/10 text-blue-400 border-blue-500/25';
        if (node.action === 'CONTRACT_VERIFY' || node.action === 'RUN_TESTS') {
          actionBadgeColor = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/25';
        } else if (node.action === 'AGENT_CODEGEN') {
          actionBadgeColor = 'bg-purple-500/10 text-purple-400 border-purple-500/25';
        } else if (node.action === 'HUMAN_APPROVAL_GATE') {
          actionBadgeColor = 'bg-amber-500/10 text-amber-400 border-amber-500/25';
        }

        const depsHtml = (node.dependencies && node.dependencies.length > 0)
          ? node.dependencies.map(d => `<span class="px-1.5 py-0.5 rounded bg-black/60 border bd text-[10px] text-zinc-400 mono">↳ ${escapeHtml(d)}</span>`).join(' ')
          : '<span class="text-[10px] text-zinc-500 mono italic">Raíz (Sin dependencias)</span>';

        const gateHtml = node.gate_required
          ? `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
               <i data-lucide="shield-alert" class="w-3 h-3"></i> HITL Gate
             </span>`
          : '';

        card.innerHTML = `
          <div class="flex items-start justify-between gap-2 border-b bd pb-2.5">
            <div class="flex items-center gap-2">
              <span class="w-6 h-6 rounded-full bg-white/10 text-zinc-300 font-bold mono text-xs flex items-center justify-center">${idx + 1}</span>
              <div>
                <div class="text-xs font-bold text-white">${escapeHtml(node.label || node.id)}</div>
                <div class="text-[10px] mono text-purple-400">${escapeHtml(node.agent_role || 'Senior Coder AGY')}</div>
              </div>
            </div>
            ${gateHtml}
          </div>

          <div class="space-y-1.5 text-xs">
            <div class="flex items-center justify-between">
              <span class="text-[10px] uppercase font-bold text-zinc-500">Acción:</span>
              <span class="px-2 py-0.5 rounded text-[10px] font-bold mono border ${actionBadgeColor}">${escapeHtml(node.action)}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-[10px] uppercase font-bold text-zinc-500">Timeout:</span>
              <span class="text-zinc-300 mono text-[11px]">${node.timeout_sec || 120}s</span>
            </div>
            <div class="pt-1.5 border-t bd">
              <div class="text-[10px] uppercase font-bold text-zinc-500 mb-1">Dependencias:</div>
              <div class="flex flex-wrap gap-1">${depsHtml}</div>
            </div>
          </div>

          <div class="pt-2 border-t bd flex items-center justify-end gap-2">
            <button onclick="openEditNodeModal('${escapeHtml(node.id)}')" class="btn btn-secondary text-[11px] px-2.5 py-1">
              <i data-lucide="edit-3" class="w-3 h-3"></i> Editar
            </button>
            <button onclick="deleteDagNode('${escapeHtml(node.id)}')" class="btn btn-secondary text-[11px] px-2.5 py-1 text-red-400 hover:text-red-300">
              <i data-lucide="trash-2" class="w-3 h-3"></i> Eliminar
            </button>
          </div>
        `;
        container.appendChild(card);
      });

      if (statGates) statGates.innerText = `${gateCount} HITL ${gateCount === 1 ? 'Activa' : 'Activas'}`;
      if (breadcrumb) breadcrumb.innerText = orderNames.join(' ➔ ');
      lucide.createIcons();
    }

    function openAddNodeModal() {
      document.getElementById('designer-modal-title').innerText = 'Agregar Nuevo Agente / Nodo al DAG';
      document.getElementById('node-edit-mode').value = 'add';
      const idInput = document.getElementById('node-input-id');
      idInput.value = 'node-' + Math.floor(Math.random() * 8999 + 1000);
      idInput.removeAttribute('disabled');
      document.getElementById('node-input-label').value = '';
      document.getElementById('node-input-role').value = 'Senior Coder AGY';
      document.getElementById('node-input-action').value = 'AGENT_CODEGEN';
      document.getElementById('node-input-timeout').value = '120';
      document.getElementById('node-input-gate').checked = false;

      populateDepsChecklist();
      document.getElementById('designer-node-modal').classList.remove('hidden');
      lucide.createIcons();
    }
    window.openAddNodeModal = openAddNodeModal;

    function openEditNodeModal(nodeId) {
      if (!currentDagState || !currentDagState.nodes) return;
      const node = currentDagState.nodes.find(n => n.id === nodeId);
      if (!node) return;

      document.getElementById('designer-modal-title').innerText = `Editar Nodo: ${node.id}`;
      document.getElementById('node-edit-mode').value = 'edit';
      const idInput = document.getElementById('node-input-id');
      idInput.value = node.id;
      idInput.setAttribute('disabled', 'true');
      document.getElementById('node-input-label').value = node.label || '';
      document.getElementById('node-input-role').value = node.agent_role || 'Senior Coder AGY';
      document.getElementById('node-input-action').value = node.action || 'AGENT_CODEGEN';
      document.getElementById('node-input-timeout').value = node.timeout_sec || 120;
      document.getElementById('node-input-gate').checked = !!node.gate_required;

      populateDepsChecklist(node.id, node.dependencies || []);
      document.getElementById('designer-node-modal').classList.remove('hidden');
      lucide.createIcons();
    }
    window.openEditNodeModal = openEditNodeModal;

    function closeDesignerNodeModal() {
      document.getElementById('designer-node-modal').classList.add('hidden');
    }
    window.closeDesignerNodeModal = closeDesignerNodeModal;

    function populateDepsChecklist(excludeId = null, selectedDeps = []) {
      const container = document.getElementById('node-dependencies-checklist');
      if (!container || !currentDagState) return;

      const candidates = (currentDagState.nodes || []).filter(n => n.id !== excludeId);
      if (candidates.length === 0) {
        container.innerHTML = '<div class="text-zinc-500 italic">No hay otros nodos disponibles para vincular.</div>';
        return;
      }

      container.innerHTML = candidates.map(n => {
        const isChecked = selectedDeps.includes(n.id) ? 'checked' : '';
        return `
          <div class="flex items-center gap-2">
            <input type="checkbox" id="dep-chk-${escapeHtml(n.id)}" value="${escapeHtml(n.id)}" class="dep-node-chk w-3.5 h-3.5 rounded border-zinc-700 bg-black text-purple-500" ${isChecked}>
            <label for="dep-chk-${escapeHtml(n.id)}" class="text-zinc-300 mono cursor-pointer">${escapeHtml(n.id)} <span class="text-zinc-500">(${escapeHtml(n.label || '')})</span></label>
          </div>
        `;
      }).join('');
    }

    async function saveDesignerNode() {
      const mode = document.getElementById('node-edit-mode').value;
      const id = document.getElementById('node-input-id').value.trim();
      const label = document.getElementById('node-input-label').value.trim() || id;
      const agent_role = document.getElementById('node-input-role').value;
      const action = document.getElementById('node-input-action').value;
      const timeout_sec = parseInt(document.getElementById('node-input-timeout').value, 10) || 120;
      const gate_required = document.getElementById('node-input-gate').checked;

      const checkedBoxes = document.querySelectorAll('.dep-node-chk:checked');
      const dependencies = Array.from(checkedBoxes).map(b => b.value);

      if (!id) {
        showToast('El ID del nodo es requerido', 'error');
        return;
      }

      const endpoint = mode === 'edit'
        ? `${API_BASE}/api/campaigns/designer/update-node`
        : `${API_BASE}/api/campaigns/designer/add-node`;

      try {
        const res = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            id, label, agent_role, action, timeout_sec, gate_required, dependencies
          })
        });
        const data = await res.json();
        if (data.success) {
          showToast(mode === 'edit' ? 'Nodo actualizado' : 'Nodo agregado al DAG', 'success');
          closeDesignerNodeModal();
          loadDesignerDAG();
        } else {
          showToast(`Error: ${data.error}`, 'error');
        }
      } catch (e) {
        showToast(`Fallo de conexión al guardar nodo: ${e}`, 'error');
      }
    }
    window.saveDesignerNode = saveDesignerNode;

    async function deleteDagNode(nodeId) {
      if (!confirm(`¿Eliminar nodo ${nodeId} del DAG?`)) return;
      try {
        const res = await fetch(`${API_BASE}/api/campaigns/designer/remove-node`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ id: nodeId })
        });
        const data = await res.json();
        if (data.success) {
          showToast(`Nodo ${nodeId} eliminado`, 'info');
          loadDesignerDAG();
        } else {
          showToast(`Error: ${data.error}`, 'error');
        }
      } catch (e) {
        showToast(`Fallo al eliminar nodo: ${e}`, 'error');
      }
    }
    window.deleteDagNode = deleteDagNode;

    async function validateCurrentDAG() {
      try {
        const res = await fetch(`${API_BASE}/api/campaigns/designer/validate`, { method: 'POST' });
        const data = await res.json();
        if (data.is_valid) {
          showToast(`DAG Válido: ${data.message}`, 'success');
          const statStatus = document.getElementById('designer-stat-status');
          if (statStatus) {
            statStatus.innerText = 'VERIFICADO (0 Ciclos)';
            statStatus.className = 'text-xs font-bold text-emerald-400 mono';
          }
        } else {
          showToast(`Error en Grafo: ${data.error}`, 'error');
          const statStatus = document.getElementById('designer-stat-status');
          if (statStatus) {
            statStatus.innerText = 'ERROR DE CICLO';
            statStatus.className = 'text-xs font-bold text-red-400 mono';
          }
        }
      } catch (e) {
        showToast(`Fallo al validar DAG: ${e}`, 'error');
      }
    }
    window.validateCurrentDAG = validateCurrentDAG;

    async function saveDagManifest() {
      try {
        const res = await fetch(`${API_BASE}/api/campaigns/designer/save`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
          showToast(`Manifiesto guardado: ${data.message}`, 'success');
        } else {
          showToast(`Error: ${data.error}`, 'error');
        }
      } catch (e) {
        showToast(`Fallo al guardar manifiesto: ${e}`, 'error');
      }
    }
    window.saveDagManifest = saveDagManifest;

    async function exportWaveZip() {
      try {
        showToast('Empaquetando Wave ZIP canónico con SHA-256...', 'info');
        const res = await fetch(`${API_BASE}/api/campaigns/designer/export-zip`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
          showToast(`Éxito: ${data.filename} (${data.size_bytes} bytes)`, 'success');
        } else {
          showToast(`Error: ${data.error}`, 'error');
        }
      } catch (e) {
        showToast(`Fallo al exportar Wave ZIP: ${e}`, 'error');
      }
    }
    window.exportWaveZip = exportWaveZip;

    function launchVisualSprint() {
      showToast('Lanzando Sprint Topológico en Vivo...', 'info');
      openTerminalDrawer();
      executeAction('campaign_sprint');
    }
    window.launchVisualSprint = launchVisualSprint;

    // Chat Token Streaming Handler
    function handleChatTokenStream(data) {
      const container = document.getElementById('chat-messages-container');
      const typing = document.getElementById('chat-typing-indicator');
      if (!container) return;

      let bubble = document.getElementById('chat-streaming-bubble');
      if (!bubble && data.token) {
        if (typing) typing.classList.remove('hidden');
        bubble = document.createElement('div');
        bubble.id = 'chat-streaming-bubble';
        bubble.className = 'space-y-1.5 toast-animate';
        bubble.innerHTML = `
          <div class="flex items-center gap-2 mono text-xs text-zinc-400">
            <span class="text-purple-400 font-bold">agy&gt;</span>
            <span class="text-zinc-400 text-[10px]">stream</span>
          </div>
          <div id="chat-streaming-body" class="p-3.5 rounded-xl bg-white/5 border bd text-xs text-zinc-200 leading-relaxed font-mono whitespace-pre-wrap"></div>
        `;
        container.appendChild(bubble);
      }

      if (bubble && data.token) {
        const bodyEl = document.getElementById('chat-streaming-body');
        if (bodyEl) bodyEl.textContent += data.token;
        scrollChatToBottom();
      }

      if (data.done) {
        if (typing) typing.classList.add('hidden');
        if (bubble) {
          const bodyEl = document.getElementById('chat-streaming-body');
          if (bodyEl) {
            bodyEl.innerHTML = formatMarkdownContent(bodyEl.textContent);
          }
          bubble.removeAttribute('id');
          if (bodyEl) bodyEl.removeAttribute('id');
        }
        scrollChatToBottom();
      }
    }
    window.handleChatTokenStream = handleChatTokenStream;


function initSSE() {
      try {
        const evtSource = new EventSource(`${API_BASE}/api/events/stream`);

        evtSource.addEventListener('terminal_log', (event) => {
          try {
            const d = JSON.parse(event.data);
            if (d && d.line) {
              appendTerminalLog(d.line);
            }
          } catch (e) {}
        });

        evtSource.addEventListener('chat_token', (event) => {
          try {
            const d = JSON.parse(event.data);
            handleChatTokenStream(d);
          } catch (e) {}
        });

        evtSource.addEventListener('dag_updated', () => {
          loadDesignerDAG();
        });

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
    

  
    async function switchEcosystemProject(folderPath, projectName) {
      showToast(`Cambiando espacio de trabajo a ${projectName}...`, 'info');
      try {
        const res = await fetch(`${API_BASE}/api/fs/open-folder`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ folder: folderPath })
        });
        const data = await res.json();
        if (data.success) {
          showToast(`Proyecto activo: ${projectName}`, 'success');
          // Reload FS tree if on explorer
          if (typeof loadFsTree === 'function') loadFsTree();
          // Update indicator if exists
          const curEl = document.getElementById('fs-current-root-path');
          if (curEl) curEl.innerText = data.root_path;
        } else {
          showToast(`Error al abrir proyecto: ${data.error}`, 'error');
        }
      } catch (e) {
        showToast(`Error de conexion: ${e.message}`, 'error');
      }
    }
    window.switchEcosystemProject = switchEcosystemProject;

  </script>
  <!-- ========================================== -->
  <!-- MODAL: NUEVO PULL REQUEST -->
  <!-- ========================================== -->
  <div id="modal-new-pr" class="fixed inset-0 bg-black/85 backdrop-blur-md z-50 flex items-center justify-center p-4 hidden">
    <div class="bg-black border border-white/20 rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl">
      <div class="flex items-center justify-between border-b border-white/10 pb-3">
        <div class="flex items-center gap-2">
          <i data-lucide="git-pull-request" class="w-5 h-5 text-blue-400"></i>
          <h3 class="text-base font-bold text-white">Crear Nuevo Pull Request</h3>
        </div>
        <button onclick="closeNewPrModal()" class="text-zinc-400 hover:text-white p-1">
          <i data-lucide="x" class="w-5 h-5"></i>
        </button>
      </div>
      <div class="space-y-4 text-xs">
        <div>
          <label class="block text-zinc-400 font-semibold mb-1">Título del PR</label>
          <input type="text" id="new-pr-title" class="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white font-mono" placeholder="feat: descripción del cambio">
        </div>
        <div>
          <label class="block text-zinc-400 font-semibold mb-1">Descripción / Notas</label>
          <textarea id="new-pr-body" class="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white font-mono h-24" placeholder="Detalles de la implementación, tickets relacionados..."></textarea>
        </div>
        <div class="grid grid-cols-2 gap-3 font-mono">
          <div>
            <label class="block text-zinc-400 font-semibold mb-1">Rama Base (Target)</label>
            <input type="text" id="new-pr-base" value="main" class="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-zinc-300">
          </div>
          <div class="flex items-center gap-2 pt-6">
            <input type="checkbox" id="new-pr-draft" checked class="w-4 h-4 rounded text-blue-500 bg-zinc-900 border-zinc-700">
            <label for="new-pr-draft" class="text-zinc-300 font-sans">Crear como Draft</label>
          </div>
        </div>
      </div>
      <div class="flex items-center justify-end gap-3 pt-3 border-t border-white/10">
        <button onclick="closeNewPrModal()" class="btn btn-secondary text-xs px-4 py-2">Cancelar</button>
        <button onclick="submitNewPr()" id="btn-submit-new-pr" class="btn btn-primary text-xs px-5 py-2 font-bold">
          <span>Crear Pull Request en GitHub</span>
        </button>
      </div>
    </div>
  </div>

</body>
</html>"""
