"""SACL V1 Apple-grade Decision Shell HTML/CSS/JS Application.

Implements an ultra-refined, responsive, dark-mode macOS/iOS styled
dashboard and micro-decision center for the SolidBit Orchestrator.
"""

HTML_APPLICATION = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SolidBit · SACL Orchestrator</title>
  <style>
    :root {
      --bg: #000000;
      --card-bg: rgba(22, 22, 28, 0.72);
      --card-elevated: rgba(30, 30, 38, 0.85);
      --border: rgba(255, 255, 255, 0.08);
      --border-focus: rgba(255, 255, 255, 0.2);
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
      --font: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: var(--font);
      -webkit-font-smoothing: antialiased;
      line-height: 1.45;
      overflow-x: hidden;
      min-height: 100vh;
      background-image: 
        radial-gradient(circle at 50% 0%, rgba(41, 151, 255, 0.08), transparent 45%),
        radial-gradient(circle at 10% 20%, rgba(191, 90, 242, 0.04), transparent 30%);
    }

    /* Container */
    .app-container {
      max-width: 1280px;
      margin: 0 auto;
      padding: 32px 24px 80px 24px;
    }

    /* Header */
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 28px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 32px;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .brand-mark {
      width: 36px;
      height: 36px;
      border-radius: 10px;
      background: linear-gradient(135deg, #2997ff, #bf5af2);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 17px;
      color: #fff;
      box-shadow: 0 4px 16px rgba(41, 151, 255, 0.3);
    }
    .brand-title {
      font-size: 19px;
      font-weight: 600;
      letter-spacing: -0.02em;
    }
    .brand-badge {
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      padding: 3px 8px;
      border-radius: 6px;
      background: rgba(255, 255, 255, 0.08);
      color: var(--text-secondary);
      margin-left: 6px;
    }

    /* Segmented Control Mode Switcher */
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
      font-size: 13px;
      font-weight: 500;
      padding: 6px 16px;
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
      padding: 14px 20px;
      margin-bottom: 28px;
      backdrop-filter: blur(20px);
    }
    .safety-left {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 13px;
    }
    .pulse-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--green);
      box-shadow: 0 0 10px var(--green);
      animation: pulse 2s infinite ease-in-out;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.5; transform: scale(0.85); }
    }
    .safety-tags {
      display: flex;
      gap: 8px;
    }
    .tag {
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.02em;
      padding: 4px 10px;
      border-radius: 6px;
      background: rgba(255, 255, 255, 0.06);
      color: var(--text-secondary);
      border: 1px solid var(--border);
    }
    .tag.locked {
      background: rgba(48, 209, 88, 0.12);
      color: var(--green);
      border-color: rgba(48, 209, 88, 0.25);
    }

    /* Key Metrics Grid */
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-bottom: 32px;
    }
    .metric-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 20px;
      backdrop-filter: blur(24px);
      transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
      border-color: var(--border-focus);
      transform: translateY(-2px);
    }
    .metric-title {
      font-size: 12px;
      font-weight: 500;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 8px;
    }
    .metric-value {
      font-size: 28px;
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
      margin-bottom: 18px;
    }
    .section-title {
      font-size: 17px;
      font-weight: 600;
      letter-spacing: -0.01em;
    }
    .section-sub {
      font-size: 13px;
      color: var(--text-secondary);
    }

    /* HUMAN GATES / MICRO-DECISION CENTER */
    .gates-section {
      margin-bottom: 36px;
    }
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
    .gate-top {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 14px;
    }
    .gate-title-group {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .risk-badge {
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.06em;
      padding: 4px 10px;
      border-radius: 6px;
      text-transform: uppercase;
    }
    .risk-badge.high { background: rgba(255, 69, 58, 0.15); color: var(--red); border: 1px solid rgba(255, 69, 58, 0.3); }
    .risk-badge.medium { background: rgba(255, 159, 10, 0.15); color: var(--orange); border: 1px solid rgba(255, 159, 10, 0.3); }
    .risk-badge.low { background: rgba(48, 209, 88, 0.15); color: var(--green); border: 1px solid rgba(48, 209, 88, 0.3); }

    .gate-action-name {
      font-size: 18px;
      font-weight: 600;
      letter-spacing: -0.01em;
    }
    .gate-scope {
      font-family: monospace;
      font-size: 13px;
      background: rgba(0, 0, 0, 0.4);
      padding: 3px 8px;
      border-radius: 6px;
      color: var(--text-secondary);
    }
    .gate-summary {
      font-size: 14px;
      color: var(--text);
      margin-bottom: 18px;
      line-height: 1.5;
    }
    .gate-actions-bar {
      display: flex;
      align-items: center;
      gap: 12px;
      padding-top: 16px;
      border-top: 1px solid var(--border);
    }
    .btn {
      font-family: var(--font);
      font-size: 13px;
      font-weight: 600;
      padding: 10px 20px;
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

    /* Empty state when no gates pending */
    .empty-gates-box {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 36px 24px;
      text-align: center;
      color: var(--text-secondary);
      font-size: 14px;
    }

    /* CONNECTIONS ECOSYSTEM GRID */
    .connections-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin-bottom: 36px;
    }
    .conn-card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 16px;
      backdrop-filter: blur(20px);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: all 0.2s ease;
    }
    .conn-card:hover {
      border-color: var(--border-focus);
    }
    .conn-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 10px;
    }
    .conn-name {
      font-size: 14px;
      font-weight: 600;
    }
    .status-indicator {
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }
    .status-indicator.connected { background: var(--green); box-shadow: 0 0 8px var(--green); }
    .status-indicator.degraded { background: var(--orange); box-shadow: 0 0 8px var(--orange); }
    .status-indicator.disconnected { background: var(--red); box-shadow: 0 0 8px var(--red); }
    .conn-version {
      font-size: 12px;
      color: var(--text-secondary);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    /* AGENT FLEET TABLE (TECHNICAL / AUDIT VIEW) */
    .fleet-table-container {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 16px;
      overflow: hidden;
      margin-bottom: 36px;
    }
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
      padding: 12px 18px;
      border-bottom: 1px solid var(--border);
      text-transform: uppercase;
      font-size: 11px;
      letter-spacing: 0.05em;
    }
    td {
      padding: 14px 18px;
      border-bottom: 1px solid var(--border);
      color: var(--text);
    }
    tr:last-child td { border-bottom: none; }
    .status-pill {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 5px;
      font-size: 11px;
      font-weight: 600;
    }
    .status-pill.COMPLETED { background: rgba(48, 209, 88, 0.15); color: var(--green); }
    .status-pill.RUNNING { background: rgba(41, 151, 255, 0.15); color: var(--accent); }
    .status-pill.FAILED { background: rgba(255, 69, 58, 0.15); color: var(--red); }
    .status-pill.PENDING { background: rgba(255, 255, 255, 0.08); color: var(--text-secondary); }

    /* TOAST NOTIFICATION */
    .toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: var(--card-elevated);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 14px 22px;
      border-radius: 12px;
      box-shadow: 0 8px 30px rgba(0,0,0,0.6);
      backdrop-filter: blur(20px);
      font-size: 13px;
      display: flex;
      align-items: center;
      gap: 10px;
      transform: translateY(100px);
      opacity: 0;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      z-index: 999;
    }
    .toast.visible {
      transform: translateY(0);
      opacity: 1;
    }

    /* RESPONSIVE */
    @media (max-width: 900px) {
      .metrics-grid, .connections-grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 600px) {
      .metrics-grid, .connections-grid { grid-template-columns: 1fr; }
      header { flex-direction: column; gap: 16px; align-items: flex-start; }
    }
  </style>
</head>
<body>
  <div class="app-container">
    <!-- Header -->
    <header>
      <div class="brand">
        <div class="brand-mark">S</div>
        <div>
          <div style="display: flex; align-items: center;">
            <span class="brand-title">SolidBit Orchestrator</span>
            <span class="brand-badge" id="project-badge">Stable-Ecommerce</span>
          </div>
          <div style="font-size: 12px; color: var(--text-secondary); margin-top: 2px;">
            SACL V1 Autonomous Multi-Agent Control Shell
          </div>
        </div>
      </div>
      <div class="segmented-control">
        <button class="segment-btn active" onclick="setMode('simple')">Simple</button>
        <button class="segment-btn" onclick="setMode('technical')">Technical</button>
        <button class="segment-btn" onclick="setMode('audit')">Audit</button>
      </div>
    </header>

    <!-- Safety Boundary Guardrail -->
    <div class="safety-banner">
      <div class="safety-left">
        <div class="pulse-dot"></div>
        <span><strong>Safety Guardrails Active:</strong> Sandboxed execution loop; non-blocking human approval.</span>
      </div>
      <div class="safety-tags">
        <span class="tag locked">PROD DEPLOY: BLOCKED</span>
        <span class="tag locked">RULESETS: LOCKED</span>
        <span class="tag locked">DIRTY ROOT: PREVENTED</span>
      </div>
    </div>

    <!-- Key Metrics -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-title">System Readiness</div>
        <div class="metric-value" id="metric-readiness" style="color: var(--green);">--%</div>
        <div class="metric-sub">Ecosystem verified</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Active Campaign</div>
        <div class="metric-value" id="metric-campaign" style="font-size: 20px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">--</div>
        <div class="metric-sub" id="metric-campaign-sub">Checking...</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Decision Gates</div>
        <div class="metric-value" id="metric-gates" style="color: var(--orange);">0</div>
        <div class="metric-sub">Awaiting micro-decision</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Agent Fleet</div>
        <div class="metric-value" id="metric-agents">0</div>
        <div class="metric-sub" id="metric-agents-sub">Workers idle</div>
      </div>
    </div>

    <!-- Human Decision Gate Section (The Core Micro-Decision Center) -->
    <div class="gates-section">
      <div class="section-header">
        <div>
          <div class="section-title">Human Decision Center (Micro-Decisions)</div>
          <div class="section-sub">Zero-friction decisions on architect-predefined governance gates.</div>
        </div>
      </div>
      <div id="gates-list">
        <!-- Rendered dynamically -->
      </div>
    </div>

    <!-- Technology Ecosystem Connections -->
    <div class="section-header">
      <div>
        <div class="section-title">Technology Connections</div>
        <div class="section-sub">Authenticated local CLIs and managed cloud platforms.</div>
      </div>
      <button class="btn btn-secondary" onclick="refreshData()" style="padding: 6px 14px; font-size: 12px;">⟳ Re-verify</button>
    </div>
    <div class="connections-grid" id="connections-grid">
      <!-- Rendered dynamically -->
    </div>

    <!-- Fleet & Worktrees (Visible in Technical and Audit modes) -->
    <div id="technical-panel" style="display: none;">
      <div class="section-header">
        <div>
          <div class="section-title">Execution Fleet & Worktree Isolation</div>
          <div class="section-sub">Live agent processes, leased paths, and memory states.</div>
        </div>
      </div>
      <div class="fleet-table-container">
        <table>
          <thead>
            <tr>
              <th>Agent ID</th>
              <th>Status</th>
              <th>PID</th>
              <th>Verdict</th>
              <th>Duration</th>
            </tr>
          </thead>
          <tbody id="fleet-tbody">
            <!-- Rendered dynamically -->
          </tbody>
        </table>
      </div>
    </div>

  </div>

  <div class="toast" id="toast">Gate action executed successfully.</div>

  <script>
    let currentMode = 'simple';

    function setMode(mode) {
      currentMode = mode;
      document.querySelectorAll('.segment-btn').forEach(btn => {
        btn.classList.toggle('active', btn.textContent.toLowerCase() === mode);
      });
      const techPanel = document.getElementById('technical-panel');
      if (techPanel) {
        techPanel.style.display = (mode === 'technical' || mode === 'audit') ? 'block' : 'none';
      }
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
            justification: 'Decided via SACL Decision Shell'
          })
        });
        const res = await resp.json();
        if (res.success) {
          showToast(`Gate ${decision}: ${res.message}`);
          refreshData();
        } else {
          showToast(`Error: ${res.message}`);
        }
      } catch (err) {
        showToast(`Request failed: ${err.message}`);
      }
    }

    async function refreshData() {
      try {
        const resp = await fetch('/api/snapshot?mode=' + currentMode);
        const data = await resp.json();
        renderDashboard(data);
      } catch (err) {
        console.error('Snapshot failed:', err);
      }
    }

    function renderDashboard(data) {
      // Metrics
      document.getElementById('metric-readiness').textContent = data.readiness_score + '%';
      document.getElementById('metric-campaign').textContent = data.active_campaign || 'Idle';
      document.getElementById('metric-campaign-sub').textContent = data.active_project;
      document.getElementById('project-badge').textContent = data.active_project;
      document.getElementById('metric-gates').textContent = data.pending_gates.length;
      document.getElementById('metric-agents').textContent = data.agents.length;
      document.getElementById('metric-agents-sub').textContent = data.agents.length > 0 ? `${data.agents.length} active` : 'All idle';

      // Pending Gates
      const gatesList = document.getElementById('gates-list');
      if (!data.pending_gates || data.pending_gates.length === 0) {
        gatesList.innerHTML = `
          <div class="empty-gates-box">
            ✓ <strong>No decision gates pending.</strong> The orchestrator is running smoothly without human bottlenecks.
          </div>
        `;
      } else {
        gatesList.innerHTML = data.pending_gates.map(g => `
          <div class="gate-card">
            <div class="gate-top">
              <div class="gate-title-group">
                <span class="risk-badge ${g.risk_level.toLowerCase()}">${g.risk_level} RISK</span>
                <span class="gate-action-name">${g.action}</span>
                <span class="gate-scope">${g.scope}</span>
              </div>
              <div style="font-size: 12px; color: var(--text-secondary);">Job: ${g.job_id}</div>
            </div>
            <div class="gate-summary">
              ${g.evidence_summary}
            </div>
            <div class="gate-actions-bar">
              <button class="btn btn-primary" onclick="submitGate('${g.request_id}', 'APPROVED')">
                ✓ Authorize Action
              </button>
              <button class="btn btn-secondary" onclick="showToast('Requested re-check of tests/diffs...')">
                ⟳ Request More Evidence
              </button>
              <button class="btn btn-danger" onclick="submitGate('${g.request_id}', 'REJECTED')">
                ✕ Reject / Safe Pause
              </button>
            </div>
          </div>
        `).join('');
      }

      // Technology Connections
      const connsGrid = document.getElementById('connections-grid');
      connsGrid.innerHTML = data.connections.map(c => `
        <div class="conn-card">
          <div>
            <div class="conn-top">
              <span class="conn-name">${c.name}</span>
              <div class="status-indicator ${c.status}"></div>
            </div>
            <div class="conn-version" title="${c.version || c.error_message || ''}">
              ${c.version || c.error_message || 'Unverified'}
            </div>
          </div>
          <div style="font-size: 11px; color: var(--text-tertiary); margin-top: 10px; text-transform: uppercase;">
            ${c.status.toUpperCase()}
          </div>
        </div>
      `).join('');

      // Fleet Table
      const fleetTbody = document.getElementById('fleet-tbody');
      if (fleetTbody) {
        if (!data.agents || data.agents.length === 0) {
          fleetTbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-secondary);">No active agents</td></tr>';
        } else {
          fleetTbody.innerHTML = data.agents.map(a => `
            <tr>
              <td><strong>${a.agent_id}</strong></td>
              <td><span class="status-pill ${a.status}">${a.status}</span></td>
              <td><code>${a.pid || '--'}</code></td>
              <td>${a.verdict || '--'}</td>
              <td>${a.duration_str || '--'}</td>
            </tr>
          `).join('');
        }
      }
    }

    // Auto-refresh every 4 seconds
    refreshData();
    setInterval(refreshData, 4000);
  </script>
</body>
</html>
"""
