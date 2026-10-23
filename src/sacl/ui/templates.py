"""SACL V1 Resend-style Decision Shell with Pure Black Palette, Native SVG Donut, and WCAG AAA Contrast.

Meticulously crafted for high-performance developer ergonomics, featuring:
- Resend-inspired pure black (#000) and crisp neutral typography (#ededed, #a1a1aa).
- SolidBit black disc logo with sharp white linework.
- Segmented Control (Simple · Technical · Audit).
- Critical action micro-decision panel with elevated orange tint and rich git context.
- Native SVG donut charts eliminating external Chart.js dependencies.
- Zero emojis: 100% vector SVGs.
"""

HTML_APPLICATION = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SolidBit · SACL Decision Shell Pro</title>
  <!-- Tailwind CSS & Inter Font -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    /* Resend-grade dark palette: Pure Black, crisp neutral contrast, WCAG AAA */
    :root {
      --bg: #000000;
      --surface: #0a0a0a;
      --surface-elevated: #111113;
      --border: rgba(255, 255, 255, 0.08);
      --border-focus: rgba(255, 255, 255, 0.16);
      --text: #ededed;
      --text-muted: #a1a1aa; /* 7.8:1 WCAG AAA */
      --text-dim: #8b8b93;   /* 5.9:1 WCAG AA */
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
      display: flex;
      flex-direction: column;
    }

    .mono { font-family: var(--mono); }
    .t2 { color: var(--text-muted); }
    .t3 { color: var(--text-dim); }
    .bd { border-color: var(--border); }
    .surface { background: var(--surface); }

    /* SolidBit Black Disc Logo */
    .logo-black {
      width: 32px;
      height: 32px;
      border-radius: 9999px;
      overflow: hidden;
      box-shadow: 0 0 0 1px rgba(255,255,255,0.14);
      background: #000;
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .logo-black img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transform: scale(1.14);
      filter: invert(1) grayscale(1) contrast(1.4);
    }

    /* Resend Sidebar Navigation */
    .nav-item {
      display: flex;
      align-items: center;
      gap: 12px;
      height: 36px;
      padding: 0 12px;
      border-radius: 8px;
      font-size: 14px;
      color: var(--text-muted);
      cursor: pointer;
      transition: background .15s, color .15s;
      user-select: none;
    }
    .nav-item:hover {
      background: rgba(255, 255, 255, 0.05);
      color: var(--text);
    }
    .nav-item.active {
      background: rgba(255, 255, 255, 0.08);
      color: #ffffff;
      font-weight: 500;
    }
    .nav-item svg {
      width: 16px;
      height: 16px;
      flex-shrink: 0;
    }
    .nav-badge {
      margin-left: auto;
      min-width: 20px;
      height: 20px;
      padding: 0 6px;
      border-radius: 9999px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 600;
      line-height: 1;
    }

    /* Segmented Control */
    .seg {
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.10);
      border-radius: 8px;
      padding: 3px;
      display: flex;
      align-items: center;
      gap: 3px;
    }
    .seg button {
      color: #b4b4bc;
      border: none;
      background: transparent;
      padding: 4px 12px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      transition: all .15s;
    }
    .seg button:hover {
      color: #ffffff;
    }
    .seg button.on {
      background: rgba(255, 255, 255, 0.14);
      color: #ffffff;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.4);
    }

    /* Resend Button System */
    .btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      height: 34px;
      padding: 0 14px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all .15s;
      text-decoration: none;
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
    }
    .btn-secondary {
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.12);
      color: var(--text);
    }
    .btn-secondary:hover {
      background: rgba(255, 255, 255, 0.10);
      border-color: rgba(255, 255, 255, 0.20);
      color: #ffffff;
    }
    .btn-danger {
      background: rgba(239, 68, 68, 0.10);
      border: 1px solid rgba(248, 113, 113, 0.35);
      color: #f87171;
    }
    .btn-danger:hover {
      background: rgba(239, 68, 68, 0.18);
      color: #fca5a5;
    }

    /* Critical Micro-Decision Card */
    .critical-card {
      background: linear-gradient(180deg, rgba(249,115,22,0.045), rgba(249,115,22,0.02));
      border: 1px solid rgba(249,115,22,0.22);
      border-top: 2px solid #f97316;
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 8px 32px -8px rgba(249,115,22,0.18), 0 2px 8px rgba(0,0,0,0.5);
    }

    /* Tab Content Switch */
    .tab-pane { display: none; }
    .tab-pane.active { display: block; animation: fadeIn .18s ease-out; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

    /* Resend Slide-over Drawer */
    .drawer-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(8px);
      z-index: 1000;
      opacity: 0;
      pointer-events: none;
      transition: opacity .25s ease;
    }
    .drawer-overlay.open { opacity: 1; pointer-events: auto; }
    .drawer {
      position: fixed;
      top: 0;
      right: -640px;
      width: 600px;
      max-width: 90vw;
      height: 100vh;
      background: #09090b;
      border-left: 1px solid var(--border-focus);
      z-index: 1001;
      display: flex;
      flex-direction: column;
      transition: right .3s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: -20px 0 60px rgba(0,0,0,0.85);
    }
    .drawer.open { right: 0; }

    /* Modal System */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(8px);
      z-index: 1100;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .modal-overlay.open { display: flex; animation: fadeIn .18s ease; }
    .modal-box {
      background: #0a0a0a;
      border: 1px solid var(--border-focus);
      border-radius: 14px;
      width: 520px;
      max-width: 100%;
      padding: 28px;
      box-shadow: 0 24px 60px rgba(0,0,0,0.9);
    }

    /* Form Controls */
    .form-control {
      width: 100%;
      background: rgba(0,0,0,0.5);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 8px 12px;
      color: var(--text);
      font-size: 13px;
      outline: none;
      transition: border-color .15s;
    }
    .form-control:focus {
      border-color: #ffffff;
    }

    /* Focus Rings */
    .focus-ring:focus-visible {
      outline: 2px solid #ffffff;
      outline-offset: 2px;
    }
  </style>
</head>
<body>

<div class="flex h-screen overflow-hidden">

  <!-- ==================== SIDEBAR ==================== -->
  <aside class="w-[248px] shrink-0 border-r bd flex flex-col px-3 py-4 gap-1 select-none">
    <!-- Brand Header with Black Disc Logo -->
    <div class="flex items-center gap-3 px-2 pb-4">
      <div class="logo-black">
        <img alt="SolidBit" src="data:image/png;base64,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">
      </div>
      <div class="leading-tight">
        <div class="text-[15px] font-semibold tracking-tight text-white">SolidBit SACL</div>
        <div class="text-xs t3 tracking-[0.12em]">DECISION SHELL · MX</div>
      </div>
    </div>

    <!-- Project Context Selector Button -->
    <button class="focus-ring mx-1 mb-4 flex items-center gap-2 h-9 px-3 rounded-lg btn-secondary text-[13px] text-left truncate" onclick="switchTab('projects')">
      <i data-i="folder" class="t2"></i>
      <span id="sidebar-active-project" class="truncate font-medium">Stable-Ecommerce</span>
      <i data-i="updown" class="ml-auto t3"></i>
    </button>

    <!-- Nav Section: Operación -->
    <div class="px-3 pt-2 pb-1 text-xs font-medium t3 uppercase tracking-wider">Operación</div>
    <div class="nav-item active" onclick="switchTab('overview')">
      <i data-i="dashboard"></i><span>Visión General</span>
    </div>
    <div class="nav-item" onclick="switchTab('telemetry')">
      <i data-i="activity"></i><span>Ejecución en Vivo</span>
      <span class="nav-badge bg-white/10 text-zinc-200" id="badge-telemetry">75%</span>
    </div>
    <div class="nav-item" onclick="switchTab('gates')">
      <i data-i="gate"></i><span>Decision Gates</span>
      <span class="nav-badge bg-orange-500 text-black font-bold" id="badge-gates">1</span>
    </div>

    <!-- Nav Section: Gobernanza -->
    <div class="px-3 pt-4 pb-1 text-xs font-medium t3 uppercase tracking-wider">Gobernanza</div>
    <div class="nav-item" onclick="switchTab('roadmap')">
      <i data-i="calendar"></i><span>Roadmap SDLC</span>
    </div>
    <div class="nav-item" onclick="switchTab('designer')">
      <i data-i="workflow"></i><span>Diseñador DAG</span>
    </div>
    <div class="nav-item" onclick="switchTab('email')">
      <i data-i="mail"></i><span>Email Gateway</span>
      <span class="nav-badge bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[11px]">E2E</span>
    </div>

    <!-- Nav Section: Plataforma -->
    <div class="px-3 pt-4 pb-1 text-xs font-medium t3 uppercase tracking-wider">Plataforma</div>
    <div class="nav-item" onclick="switchTab('connections')">
      <i data-i="plug"></i><span>Conexiones & Auth</span>
      <span class="nav-badge bg-white/10 text-zinc-200" id="badge-conns">6/9</span>
    </div>
    <div class="nav-item" onclick="switchTab('contracts')">
      <i data-i="shield"></i><span>Contratos Inmutables</span>
    </div>

    <!-- User / Operator Footer -->
    <div class="mt-auto border-t bd pt-3 px-2 flex items-center gap-3">
      <div class="w-8 h-8 rounded-full bg-white/10 border border-white/10 flex items-center justify-center text-xs font-semibold text-white">L</div>
      <div class="min-w-0">
        <div class="text-[13px] font-medium text-white truncate">Lucilfer</div>
        <div class="text-xs t2 truncate font-mono">lawlieeet@outlook.es</div>
      </div>
    </div>
  </aside>

  <!-- ==================== MAIN VIEW CONTAINER ==================== -->
  <div class="flex-1 min-w-0 flex flex-col h-screen overflow-hidden">

    <!-- RESEND TOP HEADER BAR -->
    <header class="h-16 border-b bd flex items-center gap-6 px-8 shrink-0 surface select-none">
      <!-- Breadcrumb tags with ample spacing -->
      <div class="flex items-center gap-3">
        <span class="inline-flex items-center gap-2 h-8 px-3.5 rounded-lg btn-secondary text-[13px]">
          <i data-i="folder" class="t2"></i>
          <span id="header-project-name">Stable-Ecommerce</span>
        </span>
        <span class="t3">/</span>
        <span class="inline-flex items-center gap-2 h-8 px-3.5 rounded-lg btn-secondary text-[13px]">
          <i data-i="workflow" class="t2"></i>
          <span id="header-campaign-name">Productization V1</span>
        </span>
      </div>

      <!-- Segmented Control (Simple · Technical · Audit) -->
      <div class="seg" role="tablist" aria-label="Modo de vista">
        <button class="on focus-ring" onclick="changeMode('simple', this)">Simple</button>
        <button class="focus-ring" onclick="changeMode('technical', this)">Technical</button>
        <button class="focus-ring" onclick="changeMode('audit', this)">Audit</button>
      </div>

      <!-- Header Right Controls -->
      <div class="ml-auto flex items-center gap-4">
        <!-- SSE Live Indicator -->
        <div class="inline-flex items-center gap-2 text-[13px] text-emerald-400 font-medium">
          <span class="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399]"></span>
          <span>SSE LIVE PUSH</span>
        </div>

        <!-- AI Model Selector Pill -->
        <button class="focus-ring inline-flex items-center gap-2 h-8 px-3.5 rounded-lg btn-secondary text-[13px]" onclick="openModelModal()">
          <i data-i="sparkles" class="t2"></i>
          <span id="header-model-name">Claude 3.7 Sonnet</span>
          <i data-i="updown" class="t3"></i>
        </button>

        <!-- White Resend Primary Action -->
        <button class="focus-ring btn btn-primary" onclick="launchActiveCampaign()">
          <i data-i="play"></i>
          <span>Iniciar sprint</span>
        </button>
      </div>
    </header>

    <!-- MAIN SCROLLABLE CONTENT -->
    <main class="flex-1 overflow-y-auto px-8 py-8 max-w-[1280px] w-full">

      <!-- ==================== TAB 1: OVERVIEW ==================== -->
      <section id="tab-overview" class="tab-pane active">
        <div class="mb-6">
          <h1 class="text-2xl font-semibold tracking-tight text-white">Visión General</h1>
          <p class="text-sm t2 mt-1">Estado del ciclo SDLC, micro-decisiones pendientes y salud del ecosistema.</p>
        </div>

        <!-- Safety Guardrails Banner (Filled status badges) -->
        <div class="rounded-xl border bd surface px-5 py-4 mb-6 flex items-center gap-4 flex-wrap">
          <div class="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <i data-i="shield"></i>
          </div>
          <div class="min-w-0">
            <div class="text-sm font-medium text-white">Safety guardrails activos</div>
            <div class="text-[13px] t2">Ninguna acción de producción, merge destructivo o borrado puede ejecutarse sin compuerta humana.</div>
          </div>
          <div class="ml-auto flex items-center gap-2 flex-wrap">
            <span class="mono inline-flex items-center gap-1.5 h-7 px-2.5 rounded-md text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/25">
              <i data-i="lock"></i>PROD DEPLOY · BLOCKED
            </span>
            <span class="mono inline-flex items-center gap-1.5 h-7 px-2.5 rounded-md text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/25">
              <i data-i="lock"></i>FORCE PUSH · BLOCKED
            </span>
            <span class="mono inline-flex items-center gap-1.5 h-7 px-2.5 rounded-md text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/25">
              <i data-i="check"></i>RULESETS · LOCKED
            </span>
            <span class="mono inline-flex items-center gap-1.5 h-7 px-2.5 rounded-md text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/25">
              <i data-i="check"></i>DIRTY ROOT · PREVENTED
            </span>
          </div>
        </div>

        <!-- KPI Cards Grid (p-6 uniform padding) -->
        <div class="grid grid-cols-4 gap-4 mb-6">
          <div class="rounded-xl border bd surface p-6">
            <div class="text-[13px] t2 font-medium">Readiness Score</div>
            <div class="text-[28px] font-semibold tracking-tight text-white mt-2" id="val-readiness">94%</div>
            <div class="text-[13px] t2 mt-2">Ecosistema validado</div>
          </div>
          <div class="rounded-xl border bd surface p-6">
            <div class="text-[13px] t2 font-medium">Campaña activa</div>
            <div class="text-[28px] font-semibold tracking-tight text-white mt-2">4 / 9</div>
            <div class="text-[13px] t2 mt-2">DAG de 9 workorders</div>
          </div>
          <div class="rounded-xl border bd surface p-6">
            <div class="text-[13px] t2 font-medium">Compuertas humanas</div>
            <div class="text-[28px] font-semibold tracking-tight text-orange-400 mt-2" id="val-pending-gates">1</div>
            <div class="text-[13px] t2 mt-2">Esperando tu decisión</div>
          </div>
          <div class="rounded-xl border bd surface p-6">
            <div class="text-[13px] t2 font-medium">Pruebas unitarias</div>
            <div class="text-[28px] font-semibold tracking-tight text-white mt-2">683<span class="text-lg t3"> / 683</span></div>
            <div class="text-[13px] t2 mt-2">Suite en verde (100% pass)</div>
          </div>
        </div>

        <!-- Active Decision & Live Donut Row -->
        <div class="grid grid-cols-3 gap-4 mb-6">
          <!-- CRITICAL ACTION CARD (Elevated with orange tint) -->
          <div class="col-span-2 critical-card" id="overview-critical-gate">
            <div class="flex items-center gap-2 mb-4">
              <i data-i="alert" class="text-orange-400"></i>
              <span class="text-[13px] font-medium text-orange-300">Micro-decisión soberana requerida</span>
              <span class="ml-auto text-xs t2" id="gate-expiry-time">Expira en ~52 min</span>
            </div>

            <h2 class="text-xl font-semibold text-white tracking-tight" id="gate-action-title">Desplegar preview efímero en staging</h2>
            <div class="flex items-center gap-2 mt-2 flex-wrap">
              <span class="mono text-xs px-2 py-0.5 rounded bg-white/[0.06] border border-white/10 text-zinc-300" id="gate-action-code">DEPLOY_STAGING_PREVIEW</span>
              <span class="mono text-xs t2" id="gate-request-id-pill">REQ-20261023-29F6C674</span>
              <span class="text-xs px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/25">Riesgo medio · reversible</span>
            </div>

            <!-- Useful Context Grid (No redundancy) -->
            <dl class="grid grid-cols-3 gap-4 mt-5">
              <div class="rounded-lg border bd bg-black/40 p-3.5">
                <dt class="text-xs t2 flex items-center gap-1.5"><i data-i="bot"></i>Disparado por</dt>
                <dd class="text-[13px] text-white mt-1.5 font-medium" id="gate-triggered-by">Agente codegen · WO-04</dd>
                <dd class="mono text-xs t3 mt-0.5" id="gate-run-id">run-20261023-123038</dd>
              </div>
              <div class="rounded-lg border bd bg-black/40 p-3.5">
                <dt class="text-xs t2 flex items-center gap-1.5"><i data-i="server"></i>Impacto en infra</dt>
                <dd class="text-[13px] text-white mt-1.5 font-medium" id="gate-infra-impact">1 servicio Railway efímero</dd>
                <dd class="text-xs text-emerald-400 mt-0.5">0 cambios en producción</dd>
              </div>
              <div class="rounded-lg border bd bg-black/40 p-3.5">
                <dt class="text-xs t2 flex items-center gap-1.5"><i data-i="shield"></i>Contratos</dt>
                <dd class="text-[13px] text-white mt-1.5 font-medium">4 / 4 intactos</dd>
                <dd class="mono text-xs t3 mt-0.5">DR-INV · DR-PAY · IDEM · AUTH</dd>
              </div>
            </dl>

            <!-- Affected Commits Box -->
            <div class="mt-4 rounded-lg border bd bg-black/40 divide-y divide-white/[0.06]" id="gate-commits-box">
              <div class="px-3.5 py-2.5 text-xs t2 flex items-center justify-between">
                <span>3 commits afectados en la rama</span>
                <span class="mono"><span class="text-emerald-400">+62</span> <span class="text-red-400">−9</span> · 3 archivos</span>
              </div>
              <div class="px-3.5 py-2.5 flex items-center gap-3 text-[13px]">
                <i data-i="commit" class="t3"></i>
                <span class="mono text-xs t2">a1f3c9e</span>
                <span class="text-zinc-200 truncate">feat(cart): reserva atómica de inventario (DR-INV-001)</span>
              </div>
              <div class="px-3.5 py-2.5 flex items-center gap-3 text-[13px]">
                <i data-i="commit" class="t3"></i>
                <span class="mono text-xs t2">7b20d14</span>
                <span class="text-zinc-200 truncate">feat(checkout): idempotency-key en captura de pago</span>
              </div>
            </div>

            <!-- Action Buttons Bar -->
            <div class="flex items-center gap-3 mt-6">
              <button class="focus-ring btn btn-primary" onclick="quickApproveFromCard()">
                <i data-i="check"></i>Autorizar
              </button>
              <button class="focus-ring btn btn-secondary" onclick="openImpactDrawer()">
                <i data-i="diff"></i>Ver impacto & diff
              </button>
              <button class="focus-ring btn btn-secondary" onclick="notifyMobileForCurrentGate()">
                <i data-i="phone"></i>Enviar a mi móvil
              </button>
              <button class="focus-ring ml-auto btn btn-danger" onclick="quickRejectFromCard()">
                <i data-i="x"></i>Rechazar
              </button>
            </div>
          </div>

          <!-- LIVE SVG DONUT CARD (Chart.js eliminated, zero external dep) -->
          <div class="rounded-xl border bd surface p-6 flex flex-col">
            <div class="flex items-center justify-between mb-4">
              <span class="text-sm font-medium text-white">Ejecución en vivo</span>
              <span class="text-xs t2 mono">WO-04</span>
            </div>
            <div class="flex justify-center my-2">
              <svg viewBox="0 0 42 42" class="w-40 h-40 -rotate-90" id="live-donut-svg"></svg>
            </div>
            <div class="text-center -mt-[104px] mb-[64px] pointer-events-none">
              <div class="text-3xl font-semibold text-white tracking-tight" id="donut-percent">75%</div>
              <div class="text-xs t2">global</div>
            </div>
            <ul class="space-y-2.5 text-[13px] mt-auto" id="donut-phases-list"></ul>
          </div>
        </div>

        <!-- RESEND STYLE ACTIVITY TABLE -->
        <div class="rounded-xl border bd overflow-hidden">
          <div class="px-5 py-4 border-b bd flex items-center justify-between surface">
            <span class="text-sm font-medium text-white">Actividad y auditoría reciente</span>
            <div class="flex items-center gap-2 h-8 px-3 rounded-lg btn-secondary text-[13px] t2 w-64">
              <i data-i="search"></i>
              <input type="text" placeholder="Filtrar eventos..." class="bg-transparent border-none outline-none text-xs text-white w-full">
            </div>
          </div>
          <table class="w-full text-[13px]">
            <thead>
              <tr class="text-left text-xs t2 border-b bd surface">
                <th class="font-medium px-5 py-3">Evento</th>
                <th class="font-medium px-5 py-3">Origen / Disparador</th>
                <th class="font-medium px-5 py-3">Estado</th>
                <th class="font-medium px-5 py-3 text-right">Hora</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/[0.06]" id="overview-activity-tbody">
              <tr class="hover:bg-white/[0.02]">
                <td class="px-5 py-3.5 text-white font-medium">Sprint iniciado por correo electrónico</td>
                <td class="px-5 py-3.5 mono text-xs t2">lawlieeet@outlook.es</td>
                <td class="px-5 py-3.5"><span class="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Aceptado</span></td>
                <td class="px-5 py-3.5 text-right t2">05:30</td>
              </tr>
              <tr class="hover:bg-white/[0.02]">
                <td class="px-5 py-3.5 text-white font-medium">Compuerta creada: preview staging efímero</td>
                <td class="px-5 py-3.5 mono text-xs t2">agent/codegen</td>
                <td class="px-5 py-3.5"><span class="text-xs px-2 py-0.5 rounded-full bg-orange-500/10 text-orange-400 border border-orange-500/20">Pendiente</span></td>
                <td class="px-5 py-3.5 text-right t2">05:12</td>
              </tr>
              <tr class="hover:bg-white/[0.02]">
                <td class="px-5 py-3.5 text-white font-medium">Suite de pruebas pytest 683/683</td>
                <td class="px-5 py-3.5 mono text-xs t2">pytest · runner</td>
                <td class="px-5 py-3.5"><span class="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Pasó</span></td>
                <td class="px-5 py-3.5 text-right t2">05:12</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ==================== TAB 2: TELEMETRÍA ==================== -->
      <section id="tab-telemetry" class="tab-pane">
        <div class="mb-6 flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-semibold tracking-tight text-white">Ejecución en Vivo</h1>
            <p class="text-sm t2 mt-1">Avance porcentual de fases del sprint y consola de logs determinista.</p>
          </div>
          <button class="btn btn-secondary" onclick="simulateTaskProgress()">
            <i data-i="play"></i>Simular avance (+15%)
          </button>
        </div>

        <div class="grid grid-cols-3 gap-6">
          <div class="rounded-xl border bd surface p-6">
            <h3 class="text-sm font-medium text-white mb-4">Ponderación de Fases</h3>
            <div class="flex justify-center my-4">
              <svg viewBox="0 0 42 42" class="w-48 h-48 -rotate-90" id="telemetry-large-donut"></svg>
            </div>
            <div class="space-y-3 mt-6 text-[13px]" id="telemetry-phases-full"></div>
          </div>

          <div class="col-span-2 rounded-xl border bd bg-[#050505] flex flex-col h-[520px] overflow-hidden">
            <div class="px-4 py-3 border-b bd flex items-center justify-between surface text-xs t2">
              <span class="mono">sacl-agent-runner · tempfs/worktree/integration</span>
              <button class="btn btn-secondary text-xs h-7 px-2.5" onclick="clearLogs()">Limpiar</button>
            </div>
            <div class="flex-1 p-4 font-mono text-xs overflow-y-auto space-y-1.5 text-zinc-300" id="terminal-logs-body"></div>
          </div>
        </div>
      </section>

      <!-- ==================== TAB 3: GATES ==================== -->
      <section id="tab-gates" class="tab-pane">
        <div class="mb-6">
          <h1 class="text-2xl font-semibold tracking-tight text-white">Decision Gates</h1>
          <p class="text-sm t2 mt-1">Aprobaciones soberanas que detienen el avance del agente ante cambios de riesgo.</p>
        </div>
        <div class="space-y-4" id="full-gates-container"></div>
      </section>

      <!-- ==================== TAB 4: ROADMAP ==================== -->
      <section id="tab-roadmap" class="tab-pane">
        <div class="mb-6">
          <h1 class="text-2xl font-semibold tracking-tight text-white">Roadmap Integral SDLC</h1>
          <p class="text-sm t2 mt-1">Fases, contratos inmutables e integración de tickets Jira.</p>
        </div>
        <div class="space-y-4" id="roadmap-phases-container"></div>
      </section>

      <!-- ==================== TAB 5: DESIGNER ==================== -->
      <section id="tab-designer" class="tab-pane">
        <div class="mb-6 flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-semibold tracking-tight text-white">Diseñador Visual de DAG</h1>
            <p class="text-sm t2 mt-1">Modela la secuencia de ejecución de agentes sin escribir JSON manualmente.</p>
          </div>
          <button class="btn btn-primary" onclick="saveCampaignDAG()">
            <i data-i="check"></i>Guardar Manifiesto
          </button>
        </div>
        <div class="grid grid-cols-3 gap-4" id="designer-nodes-container"></div>
      </section>

      <!-- ==================== TAB 6: EMAIL GATEWAY ==================== -->
      <section id="tab-email" class="tab-pane">
        <div class="mb-6 flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-semibold tracking-tight text-white">Email Gateway & Control Remoto</h1>
            <p class="text-sm t2 mt-1">Ciclo bidireccional seguro entre lucilfer@selfcaresinners.com y lawlieeet@outlook.es.</p>
          </div>
          <div class="flex items-center gap-3">
            <button class="btn btn-secondary" onclick="testSendEmail()"><i data-i="mail"></i>Enviar Correo de Prueba</button>
            <button class="btn btn-primary" onclick="simulateInboundEmail()"><i data-i="bot"></i>Simular Correo Entrante</button>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-6 mb-8">
          <div class="rounded-xl border bd surface p-6">
            <div class="flex items-center gap-2 mb-2 text-emerald-400 font-medium text-sm">
              <i data-i="mail"></i>Canal Saliente (Sistema &rarr; Operador)
            </div>
            <p class="text-[13px] t2 mb-4 leading-relaxed">
              El servidor notifica tareas completadas y compuertas pendientes con resumen y enlace 1-tap firmado por HMAC.
            </p>
            <div class="space-y-2 text-xs mono">
              <div class="flex items-center gap-2"><span class="t3">DE:</span><span class="text-white">lucilfer@selfcaresinners.com</span></div>
              <div class="flex items-center gap-2"><span class="t3">PARA:</span><span class="text-white">lawlieeet@outlook.es</span></div>
            </div>
          </div>

          <div class="rounded-xl border bd surface p-6">
            <div class="flex items-center gap-2 mb-2 text-emerald-400 font-medium text-sm">
              <i data-i="bot"></i>Canal Entrante (Operador &rarr; Agentes)
            </div>
            <p class="text-[13px] t2 mb-4 leading-relaxed">
              Responde desde tu Outlook con instrucciones (ej: "EJECUTAR SPRINT-01"). El webhook autenticado valida tu remitente y despierta el DAG.
            </p>
            <div class="space-y-2 text-xs mono">
              <div class="flex items-center gap-2"><span class="t3">DE:</span><span class="text-white">lawlieeet@outlook.es</span></div>
              <div class="flex items-center gap-2"><span class="t3">PARA:</span><span class="text-white">lucilfer@selfcaresinners.com</span></div>
            </div>
          </div>
        </div>

        <div class="rounded-xl border bd overflow-hidden">
          <div class="px-5 py-4 border-b bd surface text-sm font-medium text-white">Historial de Notificaciones y Comandos</div>
          <table class="w-full text-[13px]">
            <thead>
              <tr class="text-left text-xs t2 border-b bd surface">
                <th class="font-medium px-5 py-3">Dirección</th>
                <th class="font-medium px-5 py-3">Remitente / Destino</th>
                <th class="font-medium px-5 py-3">Asunto</th>
                <th class="font-medium px-5 py-3">Estado</th>
                <th class="font-medium px-5 py-3 text-right">Hora</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/[0.06]" id="email-logs-tbody"></tbody>
          </table>
        </div>
      </section>

      <!-- ==================== TAB 7: CONNECTIONS ==================== -->
      <section id="tab-connections" class="tab-pane">
        <div class="mb-6">
          <h1 class="text-2xl font-semibold tracking-tight text-white">Conexiones & Autenticación Web</h1>
          <p class="text-sm t2 mt-1">Herramientas del desarrollador conectadas al control loop con login asistido por navegador.</p>
        </div>
        <div class="grid grid-cols-3 gap-4" id="connections-grid"></div>
      </section>

      <!-- ==================== TAB 8: CONTRACTS ==================== -->
      <section id="tab-contracts" class="tab-pane">
        <div class="mb-6">
          <h1 class="text-2xl font-semibold tracking-tight text-white">Contratos Inmutables & Invariantes</h1>
          <p class="text-sm t2 mt-1">Especificaciones blindadas contra regresiones financieras, inventario y mutación destructiva.</p>
        </div>
        <div class="grid grid-cols-2 gap-4" id="contracts-grid"></div>
      </section>

    </main>
  </div>
</div>

<!-- ==================== SLIDE-OVER VISUAL IMPACT DRAWER ==================== -->
<div id="drawer-overlay" class="drawer-overlay" onclick="closeImpactDrawer()"></div>
<aside id="impact-drawer" class="drawer">
  <div class="p-6 border-b bd flex items-center justify-between surface">
    <div>
      <h2 class="text-lg font-semibold text-white tracking-tight flex items-center gap-2">
        <i data-i="diff"></i>Impacto Visual & Diff
      </h2>
      <div class="text-xs t2 mt-0.5 mono" id="drawer-gate-id">REQ-20261023-29F6C674</div>
    </div>
    <button class="btn btn-secondary text-xs h-8 px-2.5" onclick="closeImpactDrawer()"><i data-i="x"></i></button>
  </div>

  <div class="flex-1 p-6 overflow-y-auto space-y-6">
    <div class="rounded-lg border bd surface p-4">
      <div class="text-xs font-semibold t3 uppercase tracking-wider mb-1">Resumen Ejecutivo</div>
      <p class="text-sm text-zinc-200 leading-relaxed" id="drawer-human-summary"></p>
    </div>

    <div>
      <div class="text-xs font-semibold t3 uppercase tracking-wider mb-2">Semáforo de Contratos</div>
      <div class="grid grid-cols-2 gap-2" id="drawer-contracts-status"></div>
    </div>

    <div>
      <div class="text-xs font-semibold t3 uppercase tracking-wider mb-2">Archivos Modificados</div>
      <div class="rounded-lg border bd bg-[#050505] p-3 text-xs mono space-y-1.5" id="drawer-files-list"></div>
    </div>

    <div>
      <div class="text-xs font-semibold t3 uppercase tracking-wider mb-2">Diff Sintáctico de Git</div>
      <pre class="rounded-lg border bd bg-[#050505] p-4 text-xs mono text-zinc-300 overflow-x-auto leading-relaxed max-h-64" id="drawer-diff-text"></pre>
    </div>
  </div>

  <div class="p-6 border-t bd surface flex items-center gap-3">
    <button class="btn btn-danger flex-1" onclick="submitDrawerDecision('REJECTED')">
      <i data-i="x"></i>Rechazar
    </button>
    <button class="btn btn-primary flex-1 justify-center" onclick="submitDrawerDecision('APPROVED')">
      <i data-i="check"></i>Autorizar Acción
    </button>
  </div>
</aside>

<!-- ==================== AUTH / BROWSER LOGIN MODAL ==================== -->
<div id="auth-modal" class="modal-overlay">
  <div class="modal-box">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-base font-semibold text-white" id="modal-auth-title">Autenticar Herramienta</h3>
      <button class="btn btn-secondary text-xs h-7 px-2" onclick="closeAuthModal()"><i data-i="x"></i></button>
    </div>
    <p class="text-sm t2 mb-6" id="modal-auth-desc">Inicia sesión abriendo el portal en tu navegador predeterminado.</p>
    
    <div class="p-4 rounded-lg border bd surface mb-6 text-center">
      <button class="btn btn-primary w-full justify-center" onclick="launchBrowserAuthAction()">
        <i data-i="plug"></i>Abrir Navegador para Autenticar
      </button>
      <div class="text-xs t3 mt-2">Se abrirá el portal oficial de OAuth/Tokens en tu navegador.</div>
    </div>

    <div class="mb-6">
      <label class="block text-xs font-medium t2 mb-2 uppercase tracking-wider">Token / API Key (Opcional)</label>
      <input type="password" id="auth-token-input" class="form-control" placeholder="Pegar token generado aquí...">
    </div>

    <div class="flex items-center gap-3">
      <button class="btn btn-secondary flex-1 justify-center" onclick="closeAuthModal()">Cancelar</button>
      <button class="btn btn-primary flex-1 justify-center" onclick="submitTokenAuth()">Guardar y Conectar</button>
    </div>
  </div>
</div>

<!-- ==================== AI MODEL SETTINGS MODAL ==================== -->
<div id="model-modal" class="modal-overlay">
  <div class="modal-box">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-base font-semibold text-white">Configuración del Motor Cognitivo</h3>
      <button class="btn btn-secondary text-xs h-7 px-2" onclick="closeModelModal()"><i data-i="x"></i></button>
    </div>

    <div class="space-y-4 mb-6">
      <div>
        <label class="block text-xs font-medium t2 mb-2 uppercase tracking-wider">Modelo Activo</label>
        <select id="model-picker-select" class="form-control" onchange="selectModel(this.value)">
          <option value="claude-3-7-sonnet">Claude 3.7 Sonnet (Flagship Hybrid)</option>
          <option value="claude-3-5-sonnet">Claude 3.5 Sonnet (Code Specialist)</option>
          <option value="gemini-2-flash">Gemini 2.0 Flash (Ultra-Low Latency)</option>
          <option value="gemini-1-5-pro">Gemini 1.5 Pro (2M Context)</option>
          <option value="gpt-4o">OpenAI GPT-4o (Omni)</option>
          <option value="deepseek-r1">DeepSeek R1 (Local Ollama)</option>
        </select>
      </div>

      <div>
        <div class="flex justify-between text-xs mb-2">
          <span class="t2 uppercase tracking-wider font-medium">Temperatura</span>
          <span class="mono text-white" id="temp-val">0.20</span>
        </div>
        <input type="range" min="0" max="1" step="0.05" value="0.2" class="w-full accent-white" id="model-temp-slider" oninput="document.getElementById('temp-val').innerText = parseFloat(this.value).toFixed(2)">
      </div>

      <div class="flex items-center gap-3 pt-2">
        <input type="checkbox" id="guardrails-checkbox" checked class="w-4 h-4 rounded accent-white">
        <label for="guardrails-checkbox" class="text-xs text-zinc-300 select-none cursor-pointer">
          Blindaje Constitucional Hard Deny (Inviolable)
        </label>
      </div>
    </div>

    <div class="flex items-center gap-3">
      <button class="btn btn-secondary flex-1 justify-center" onclick="closeModelModal()">Cerrar</button>
      <button class="btn btn-primary flex-1 justify-center" onclick="saveModelSettings()">Aplicar Ajustes</button>
    </div>
  </div>
</div>

<!-- ==================== CLIENT JAVASCRIPT ==================== -->
<script>
  // Inline SVG icon dictionary (Clean 1.75px stroke, no emojis)
  const ICONS = {
    dashboard: '<rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/>',
    activity: '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    gate: '<circle cx="18" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><path d="M13 6h3a2 2 0 0 1 2 2v7"/><path d="M6 9v12"/>',
    calendar: '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    workflow: '<rect x="3" y="3" width="8" height="8" rx="2"/><path d="M7 11v4a2 2 0 0 0 2 2h4"/><rect x="13" y="13" width="8" height="8" rx="2"/>',
    mail: '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    plug: '<path d="M12 22v-5M9 8V2M15 8V2"/><path d="M18 8v5a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4V8Z"/>',
    shield: '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
    folder: '<path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/>',
    updown: '<path d="m7 15 5 5 5-5M7 9l5-5 5 5"/>',
    play: '<path d="M6 3l14 9-14 9V3z"/>',
    check: '<path d="M20 6 9 17l-5-5"/>',
    x: '<path d="M18 6 6 18M6 6l12 12"/>',
    phone: '<rect x="5" y="2" width="14" height="20" rx="2"/><path d="M12 18h.01"/>',
    diff: '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M9 10h6M12 7v6M9 17h6"/>',
    commit: '<circle cx="12" cy="12" r="3"/><path d="M3 12h6M15 12h6"/>',
    server: '<rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><path d="M6 6h.01M6 18h.01"/>',
    bot: '<path d="M12 8V4H8"/><rect x="4" y="8" width="16" height="12" rx="2"/><path d="M2 14h2M20 14h2M15 13v2M9 13v2"/>',
    lock: '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    alert: '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4M12 17h.01"/>',
    search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    sparkles: '<path d="M12 3l1.9 5.8L20 10l-6.1 1.2L12 17l-1.9-5.8L4 10l6.1-1.2Z"/>'
  };

  function renderIcons() {
    document.querySelectorAll('i[data-i]').forEach(el => {
      const iconName = el.dataset.i;
      const svgPath = ICONS[iconName] || '';
      const classes = el.className || '';
      el.outerHTML = `<svg class="${classes}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${svgPath}</svg>`;
    });
  }

  let activeGateId = "REQ-20261023-29F6C674";
  let activeAuthToolId = null;

  // Initialize
  window.addEventListener('DOMContentLoaded', () => {
    renderIcons();
    initSSE();
    loadDashboardSnapshot();
    loadTelemetryData();
    loadRoadmapData();
    loadDesignerData();
    loadEmailData();
  });

  // Tab Navigation
  function switchTab(tabId) {
    document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

    const target = document.getElementById(`tab-${tabId}`);
    if (target) target.classList.add('active');

    const navs = document.querySelectorAll('.nav-item');
    navs.forEach(n => {
      if (n.getAttribute('onclick') && n.getAttribute('onclick').includes(tabId)) {
        n.classList.add('active');
      }
    });
    renderIcons();
  }

  // Segmented Mode Control
  function changeMode(mode, btn) {
    if (btn && btn.parentElement) {
      btn.parentElement.querySelectorAll('button').forEach(b => b.classList.remove('on'));
      btn.classList.add('on');
    }
    loadDashboardSnapshot(mode);
  }

  // Real-time Push (SSE)
  function initSSE() {
    try {
      const source = new EventSource('/api/events/stream');
      source.addEventListener('snapshot', e => renderSnapshot(JSON.parse(e.data)));
      source.addEventListener('gate_decided', () => { loadDashboardSnapshot(); closeImpactDrawer(); });
      source.addEventListener('campaign_launched', () => { loadDashboardSnapshot(); loadTelemetryData(); });
      source.addEventListener('telemetry_updated', e => renderTelemetry(JSON.parse(e.data)));
      source.addEventListener('email_sent', () => loadEmailData());
      source.addEventListener('inbound_email_triggered', () => { loadEmailData(); loadDashboardSnapshot(); });
    } catch (e) {
      console.warn("SSE fallback mode:", e);
    }
  }

  // Snapshot Loader
  async function loadDashboardSnapshot(mode = 'simple') {
    try {
      const res = await fetch(`/api/snapshot?mode=${mode}`);
      const data = await res.json();
      renderSnapshot(data);
    } catch (err) {
      console.error("Snapshot error:", err);
    }
  }

  function renderSnapshot(snap) {
    if (!snap) return;
    document.getElementById('val-readiness').innerText = `${snap.readiness_score || 94}%`;
    document.getElementById('header-project-name').innerText = snap.active_project || "Stable-Ecommerce";
    document.getElementById('sidebar-active-project').innerText = snap.active_project || "Stable-Ecommerce";
    document.getElementById('header-campaign-name').innerText = snap.active_campaign || "Productization V1";

    const gates = snap.pending_gates || [];
    document.getElementById('val-pending-gates').innerText = gates.length;
    document.getElementById('badge-gates').innerText = gates.length;

    if (gates.length > 0) {
      const g = gates[0];
      activeGateId = g.approval_id;
      document.getElementById('gate-action-title').innerText = g.reason || g.action;
      document.getElementById('gate-action-code').innerText = g.action;
      document.getElementById('gate-request-id-pill').innerText = g.approval_id;
      document.getElementById('overview-critical-gate').style.display = 'block';
    } else {
      document.getElementById('overview-critical-gate').style.display = 'none';
    }

    renderGatesList(gates);
    renderConnections(snap.connections || []);
  }

  function renderGatesList(gates) {
    const container = document.getElementById('full-gates-container');
    if (!container) return;
    if (gates.length === 0) {
      container.innerHTML = '<div class="p-8 text-center t2 border bd rounded-xl surface">Cero compuertas pendientes. El control loop autónomo continúa.</div>';
      return;
    }
    let html = '';
    gates.forEach(g => {
      html += `
      <div class="critical-card">
        <div class="flex items-center gap-2 mb-3">
          <i data-i="alert" class="text-orange-400"></i>
          <span class="mono text-xs text-orange-300 font-medium">${g.action}</span>
          <span class="mono text-xs t3">· ${g.approval_id}</span>
        </div>
        <h3 class="text-lg font-semibold text-white mb-2">${g.reason}</h3>
        <div class="text-xs t2 mb-5">Alcance: <span class="mono text-zinc-300">${g.scope}</span></div>
        <div class="flex items-center gap-3">
          <button class="btn btn-primary" onclick="submitGateDecisionDirect('${g.approval_id}', 'APPROVED')">
            <i data-i="check"></i>Autorizar
          </button>
          <button class="btn btn-secondary" onclick="openImpactDrawer('${g.approval_id}')">
            <i data-i="diff"></i>Ver Diff & Impacto
          </button>
          <button class="btn btn-danger ml-auto" onclick="submitGateDecisionDirect('${g.approval_id}', 'REJECTED')">
            <i data-i="x"></i>Rechazar
          </button>
        </div>
      </div>`;
    });
    container.innerHTML = html;
    renderIcons();
  }

  function renderConnections(conns) {
    const grid = document.getElementById('connections-grid');
    if (!grid) return;
    let connected = 0;
    let html = '';
    conns.forEach(c => {
      const isOk = (c.status === 'connected');
      if (isOk) connected++;
      html += `
      <div class="rounded-xl border bd surface p-5 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-semibold text-white">${c.name}</span>
            <span class="inline-flex items-center gap-1.5 text-xs ${isOk ? 'text-emerald-400' : 'text-red-400'} font-medium">
              <span class="w-1.5 h-1.5 rounded-full ${isOk ? 'bg-emerald-400' : 'bg-red-400'}"></span>
              ${isOk ? 'Conectado' : 'Desconectado'}
            </span>
          </div>
          <div class="text-xs t2 mb-1">Versión: <span class="mono text-zinc-300">${c.version || 'No detectada'}</span></div>
          <div class="text-xs t3">Cuenta: ${c.account_info || 'N/A'}</div>
        </div>
        <div class="mt-6 flex items-center gap-2">
          <button class="btn btn-secondary text-xs flex-1 justify-center" onclick="openAuthModal('${c.id}', '${c.name}')">
            <i data-i="plug"></i>Abrir en Navegador
          </button>
          <button class="btn btn-secondary text-xs px-2.5" onclick="testConnection('${c.id}')">
            <i data-i="activity"></i>
          </button>
        </div>
      </div>`;
    });
    grid.innerHTML = html;
    document.getElementById('badge-conns').innerText = `${connected}/${conns.length}`;
    renderIcons();
  }

  // Native SVG Donut Renderer (No Chart.js dependency)
  function renderDonut(svgId, phases) {
    const el = document.getElementById(svgId);
    if (!el) return;
    const r = 15.9155, C = 2 * Math.PI * r;
    let offset = 0, svg = `<circle cx="21" cy="21" r="${r}" fill="none" stroke="rgba(255,255,255,0.07)" stroke-width="3.2"/>`;
    phases.forEach(ph => {
      const len = (ph.weight / 100) * C;
      const progressLen = len * (ph.progress / 100);
      if (progressLen > 0) {
        svg += `<circle cx="21" cy="21" r="${r}" fill="none" stroke="${ph.color}" stroke-width="3.2" stroke-dasharray="${Math.max(progressLen - 0.5, 0)} ${C}" stroke-dashoffset="${-offset}"/>`;
      }
      offset += len;
    });
    el.innerHTML = svg;
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
    document.getElementById('donut-percent').innerText = `${t.overall_progress_percent}%`;
    document.getElementById('badge-telemetry').innerText = `${t.overall_progress_percent}%`;

    const colors = ['#60a5fa', '#34d399', '#c084fc', '#fbbf24', '#67e8f9'];
    const phases = (t.phases || []).map((p, i) => ({ ...p, color: colors[i % colors.length] }));

    renderDonut('live-donut-svg', phases);
    renderDonut('telemetry-large-donut', phases);

    const listHtml = phases.map(ph => `
      <li class="flex items-center gap-2.5">
        <span class="w-2 h-2 rounded-full" style="background:${ph.color}"></span>
        <span class="text-zinc-300 truncate">${ph.name}</span>
        <span class="ml-auto mono text-xs ${ph.progress === 100 ? 'text-zinc-400' : 'text-amber-400'}">${ph.progress}%</span>
      </li>`).join('');

    const el1 = document.getElementById('donut-phases-list');
    const el2 = document.getElementById('telemetry-phases-full');
    if (el1) el1.innerHTML = listHtml;
    if (el2) el2.innerHTML = listHtml;

    const term = document.getElementById('terminal-logs-body');
    if (term) {
      term.innerHTML = (t.live_logs || []).map(l => `
        <div class="flex items-start gap-2">
          <span class="t3">[${l.timestamp}]</span>
          <span class="text-zinc-400">[${l.level}]</span>
          <span class="text-zinc-200">${l.message}</span>
        </div>`).join('');
      term.scrollTop = term.scrollHeight;
    }
  }

  // Slide-over Visual Impact Drawer
  async function openImpactDrawer(gateId = activeGateId) {
    activeGateId = gateId;
    document.getElementById('drawer-gate-id').innerText = gateId;
    document.getElementById('drawer-overlay').classList.add('open');
    document.getElementById('impact-drawer').classList.add('open');

    try {
      const res = await fetch(`/api/gates/impact?gate_id=${gateId}`);
      const d = await res.json();
      document.getElementById('drawer-human-summary').innerText = d.human_summary;
      document.getElementById('drawer-diff-text').innerText = d.diff_preview;

      let semHtml = '';
      for (const [k, v] of Object.entries(d.contracts_status || {})) {
        semHtml += `
        <div class="p-2.5 rounded border bd bg-[#050505] text-xs flex justify-between items-center">
          <span class="mono font-semibold text-white">${k}</span>
          <span class="text-emerald-400 font-medium">${v}</span>
        </div>`;
      }
      document.getElementById('drawer-contracts-status').innerHTML = semHtml;

      document.getElementById('drawer-files-list').innerHTML = (d.file_tree || []).map(f => `
        <div class="flex justify-between items-center py-0.5">
          <span class="text-zinc-300">${f.path}</span>
          <span class="text-emerald-400">+${f.lines_added} <span class="text-red-400">−${f.lines_removed}</span></span>
        </div>`).join('');
    } catch (e) {
      console.error(e);
    }
  }

  function closeImpactDrawer() {
    document.getElementById('drawer-overlay').classList.remove('open');
    document.getElementById('impact-drawer').classList.remove('open');
  }

  async function submitDrawerDecision(decision) {
    if (!activeGateId) return;
    await submitGateDecisionDirect(activeGateId, decision);
    closeImpactDrawer();
  }

  async function submitGateDecisionDirect(reqId, decision) {
    try {
      await fetch('/api/gates/decide', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ request_id: reqId, decision: decision, justification: 'Decidido desde SACL Decision Shell' })
      });
      loadDashboardSnapshot();
    } catch (e) {
      console.error(e);
    }
  }

  function quickApproveFromCard() {
    submitGateDecisionDirect(activeGateId, 'APPROVED');
  }
  function quickRejectFromCard() {
    submitGateDecisionDirect(activeGateId, 'REJECTED');
  }

  async function notifyMobileForCurrentGate() {
    try {
      const res = await fetch('/api/gates/notify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ request_id: activeGateId, channel: 'resend' })
      });
      const data = await res.json();
      alert(data.message || 'Notificación móvil despachada.');
    } catch (e) {
      console.error(e);
    }
  }

  // Email Gateway
  async function loadEmailData() {
    try {
      const res = await fetch('/api/email/config');
      const data = await res.json();
      const tbody = document.getElementById('email-logs-tbody');
      if (!tbody) return;
      tbody.innerHTML = (data.recent_logs || []).map(l => {
        const isOut = (l.direction === 'OUTBOUND');
        return `
        <tr class="hover:bg-white/[0.02]">
          <td class="px-5 py-3.5"><span class="text-xs px-2 py-0.5 rounded ${isOut ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'}">${l.direction}</span></td>
          <td class="px-5 py-3.5 mono text-xs t2">${l.from} &rarr; ${l.to}</td>
          <td class="px-5 py-3.5 text-white font-medium">${l.subject}</td>
          <td class="px-5 py-3.5"><span class="text-xs font-semibold text-emerald-400">${l.status}</span></td>
          <td class="px-5 py-3.5 text-right t2 text-xs">${(l.timestamp || '').split('T')[1]?.slice(0,8) || ''}</td>
        </tr>`;
      }).join('');
    } catch (e) {
      console.error(e);
    }
  }

  async function testSendEmail() {
    try {
      const res = await fetch('/api/email/test', { method: 'POST' });
      const data = await res.json();
      alert(data.message || 'Correo despachado.');
      loadEmailData();
    } catch (e) {
      console.error(e);
    }
  }

  async function simulateInboundEmail() {
    try {
      const res = await fetch('/api/webhooks/inbound-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          from: 'lawlieeet@outlook.es',
          subject: 'EJECUTAR SPRINT-01',
          text: 'Autorizo ejecución de pipeline autónomo en checkout.'
        })
      });
      const data = await res.json();
      alert(data.message || 'Comando por correo recibido.');
      loadEmailData();
    } catch (e) {
      console.error(e);
    }
  }

  // Browser Auth
  function openAuthModal(toolId, toolName) {
    activeAuthToolId = toolId;
    document.getElementById('modal-auth-title').innerText = `Autenticar ${toolName}`;
    document.getElementById('auth-modal').classList.add('open');
  }
  function closeAuthModal() {
    document.getElementById('auth-modal').classList.remove('open');
    activeAuthToolId = null;
  }
  async function launchBrowserAuthAction() {
    if (!activeAuthToolId) return;
    try {
      const res = await fetch('/api/connections/browser-auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tool_id: activeAuthToolId })
      });
      const data = await res.json();
      if (data.auth_url) window.open(data.auth_url, '_blank');
    } catch (e) {
      console.error(e);
    }
  }
  async function submitTokenAuth() {
    const token = document.getElementById('auth-token-input').value;
    if (!activeAuthToolId) return;
    await fetch('/api/connections/auth', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tool_id: activeAuthToolId, credentials: { token: token } })
    });
    closeAuthModal();
    loadDashboardSnapshot();
  }

  // Model Settings
  function openModelModal() { document.getElementById('model-modal').classList.add('open'); }
  function closeModelModal() { document.getElementById('model-modal').classList.remove('open'); }
  async function selectModel(id) {
    await fetch('/api/model/select', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model_id: id })
    });
    document.getElementById('header-model-name').innerText = id;
  }
  async function saveModelSettings() {
    const temp = parseFloat(document.getElementById('model-temp-slider').value);
    const id = document.getElementById('model-picker-select').value;
    await fetch('/api/model/select', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model_id: id, temperature: temp })
    });
    closeModelModal();
  }

  // Roadmap & Designer
  async function loadRoadmapData() {
    try {
      const res = await fetch('/api/roadmap');
      const d = await res.json();
      const el = document.getElementById('roadmap-phases-container');
      if (!el) return;
      el.innerHTML = (d.phases || []).map(p => `
        <div class="rounded-xl border bd surface p-6">
          <div class="flex items-center justify-between mb-3">
            <div>
              <span class="mono text-xs font-semibold text-emerald-400">${p.code}</span>
              <h3 class="text-base font-semibold text-white mt-0.5">${p.name}</h3>
            </div>
            <div class="text-right">
              <span class="text-lg font-semibold text-white">${p.progress}%</span>
              <div class="text-xs t3">${p.period}</div>
            </div>
          </div>
          <div class="w-full bg-white/5 h-1.5 rounded-full overflow-hidden mb-4">
            <div class="bg-emerald-400 h-full" style="width:${p.progress}%"></div>
          </div>
          <ul class="text-xs t2 space-y-1.5 list-disc list-inside">
            ${(p.deliverables || []).map(item => `<li>${item}</li>`).join('')}
          </ul>
        </div>`).join('');
    } catch (e) {
      console.error(e);
    }
  }

  async function loadDesignerData() {
    try {
      const res = await fetch('/api/campaigns/designer');
      const d = await res.json();
      const el = document.getElementById('designer-nodes-container');
      if (!el) return;
      el.innerHTML = (d.nodes || []).map(n => `
        <div class="rounded-xl border bd surface p-5">
          <div class="mono text-xs t3 mb-1">${n.id}</div>
          <h4 class="text-sm font-semibold text-white mb-2">${n.label}</h4>
          <div class="text-xs text-emerald-400 font-mono mb-3">Acción: ${n.action}</div>
          <div class="text-xs ${n.gate_required ? 'text-amber-400' : 't3'}">
            ${n.gate_required ? 'Compuerta humana requerida' : 'Ejecución 100% autónoma'}
          </div>
        </div>`).join('');
    } catch (e) {
      console.error(e);
    }
  }

  async function launchActiveCampaign() {
    try {
      const res = await fetch('/api/campaigns/launch', { method: 'POST' });
      const d = await res.json();
      alert(d.message || 'Campaña iniciada con éxito.');
      loadDashboardSnapshot();
    } catch (e) {
      console.error(e);
    }
  }

  async function simulateTaskProgress() {
    const cur = parseInt(document.getElementById('donut-percent').innerText) || 75;
    const nextVal = Math.min(100, cur + 15);
    await fetch('/api/telemetry/progress', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ progress: nextVal, phase: 'Verificación de Invariantes' })
    });
  }

  function clearLogs() {
    const term = document.getElementById('terminal-logs-body');
    if (term) term.innerHTML = '';
  }
</script>
</body>
</html>
"""
