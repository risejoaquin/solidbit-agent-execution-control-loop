import React, { useState } from 'react'
import {
  Zap,
  Cpu,
  CheckCircle2,
  AlertTriangle,
  Calendar,
  Flag,
  Play,
  GitBranch,
  GitMerge,
  GitCommit,
  Folder,
  Download,
  MoreVertical,
} from 'lucide-react'
import type { TaskItem, AgentItem, CommitItem, Project, ActivityEvent } from '../types/orchestrator'

interface CenterDashboardProps {
  tasks: TaskItem[]
  agents: AgentItem[]
  commits: CommitItem[]
  projects: Project[]
  events: ActivityEvent[]
  activeSprintTitle?: string
  activeSprintDesc?: string
  onOpenSprintModal: () => void
  onNavigateSection: (section: string) => void
}

export const CenterDashboard: React.FC<CenterDashboardProps> = ({
  tasks,
  agents,
  commits,
  projects,
  events,
  activeSprintTitle = 'Sprint 1 — MVP E-commerce',
  activeSprintDesc = 'Desarrollo del flujo base de la tienda online (catálogo, carrito, pagos y administración)',
  onOpenSprintModal,
  onNavigateSection,
}) => {
  const [activeTab, setActiveTab] = useState<'roadmap' | 'tareas' | 'agentes' | 'jira' | 'dependencias' | 'eventos'>('roadmap')
  const [viewMode, setViewMode] = useState<'gantt' | 'lista'>('gantt')

  const completedCount = tasks.filter((t) => t.status === 'Completada').length
  const runningCount = tasks.filter((t) => t.status === 'En progreso').length
  const waitingCount = tasks.filter((t) => t.status === 'Pendiente' || t.status === 'Bloqueada').length
  const activeAgentsCount = agents.filter((a) => a.status === 'Activo').length

  return (
    <div id="sec-dashboard" className="space-y-6">
      {/* ROW 1: 4 TOP STAT CARDS */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5">
        {/* Card 1: Agentes activos */}
        <div className="p-4 rounded-2xl bg-[#0e141d] border border-[#1b2533] space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-zinc-400">Agentes activos</span>
            <div className="w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <Zap className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span id="stat-active-agents" className="text-xl font-extrabold text-white">
              {activeAgentsCount} / {agents.length}
            </span>
            <span className="text-[11px] font-mono text-zinc-500">
              {Math.round((activeAgentsCount / (agents.length || 1)) * 100)}%
            </span>
          </div>
          <div className="w-full bg-[#1b2533] h-1.5 rounded-full overflow-hidden">
            <div
              id="bar-active-agents"
              className="bg-emerald-500 h-full rounded-full transition-all"
              style={{ width: `${(activeAgentsCount / (agents.length || 1)) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Card 2: Tareas en ejecución */}
        <div className="p-4 rounded-2xl bg-[#0e141d] border border-[#1b2533] space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-zinc-400">Tareas en ejecución</span>
            <div className="w-7 h-7 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
              <Cpu className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span id="stat-running-tasks" className="text-xl font-extrabold text-white">
              {runningCount || 7}
            </span>
            <span className="text-[11px] font-mono text-zinc-500">24%</span>
          </div>
          <div className="w-full bg-[#1b2533] h-1.5 rounded-full overflow-hidden">
            <div id="bar-running-tasks" className="bg-blue-500 h-full rounded-full transition-all" style={{ width: '24%' }}></div>
          </div>
        </div>

        {/* Card 3: Tareas completadas */}
        <div className="p-4 rounded-2xl bg-[#0e141d] border border-[#1b2533] space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-zinc-400">Tareas completadas</span>
            <div className="w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <CheckCircle2 className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span id="stat-completed-tasks" className="text-xl font-extrabold text-white">
              {completedCount || 18}
            </span>
            <span className="text-[11px] font-mono text-zinc-500">62%</span>
          </div>
          <div className="w-full bg-[#1b2533] h-1.5 rounded-full overflow-hidden">
            <div id="bar-completed-tasks" className="bg-emerald-500 h-full rounded-full transition-all" style={{ width: '62%' }}></div>
          </div>
        </div>

        {/* Card 4: Tareas en espera */}
        <div className="p-4 rounded-2xl bg-[#0e141d] border border-[#1b2533] space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-zinc-400">Tareas en espera</span>
            <div className="w-7 h-7 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <AlertTriangle className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span id="stat-waiting-tasks" className="text-xl font-extrabold text-white">
              {waitingCount || 2}
            </span>
            <span className="text-[11px] font-mono text-zinc-500">7%</span>
          </div>
          <div className="w-full bg-[#1b2533] h-1.5 rounded-full overflow-hidden">
            <div id="bar-waiting-tasks" className="bg-amber-500 h-full rounded-full transition-all" style={{ width: '7%' }}></div>
          </div>
        </div>
      </div>

      {/* ROW 2: SPRINT ACTUAL HERO CARD */}
      <div className="p-5 rounded-2xl bg-[#0e141d] border border-[#1b2533] flex flex-col md:flex-row md:items-center justify-between gap-5">
        <div className="space-y-2">
          <div className="flex items-center gap-2.5">
            <span className="text-xs font-semibold text-zinc-400">Sprint actual</span>
            <span id="dash-sprint-badge" className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-bold text-[10px]">
              En progreso
            </span>
          </div>
          <h2 id="dash-sprint-title" className="text-lg font-bold text-white tracking-tight">
            {activeSprintTitle}
          </h2>
          <p id="dash-sprint-desc" className="text-xs text-zinc-400 max-w-2xl leading-relaxed">
            {activeSprintDesc}
          </p>
          <div className="flex items-center gap-4 pt-1 text-xs text-zinc-400 flex-wrap">
            <span className="flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-zinc-500" />
              <span id="dash-sprint-start">Inicio: 24 Oct 2026</span>
            </span>
            <span className="flex items-center gap-1.5">
              <Flag className="w-3.5 h-3.5 text-zinc-500" />
              <span id="dash-sprint-end">Fin: 07 Nov 2026</span>
            </span>
            <span className="flex items-center gap-1.5">
              <Play className="w-3.5 h-3.5 text-zinc-500" />
              <span id="dash-sprint-tasks-count">{tasks.length || 12} tareas</span>
            </span>
            <span className="flex items-center gap-1.5">
              <GitBranch className="w-3.5 h-3.5 text-zinc-500" />
              <span id="dash-sprint-deps-count">3 dependencias</span>
            </span>
          </div>
        </div>

        {/* Right Circular Progress + Ver Detalles */}
        <div className="flex items-center gap-4 shrink-0">
          <div className="relative w-16 h-16 flex items-center justify-center">
            <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
              <path
                className="text-[#1b2533]"
                strokeWidth="3.5"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className="text-[#00d084]"
                strokeDasharray="41, 100"
                strokeWidth="3.5"
                strokeLinecap="round"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <span id="dash-sprint-pct" className="absolute text-xs font-bold text-white">
              41%
            </span>
          </div>
          <button
            type="button"
            onClick={onOpenSprintModal}
            className="px-3.5 py-2 rounded-xl bg-black/40 border border-white/10 hover:border-white/20 text-xs font-semibold text-white transition cursor-pointer"
          >
            Ver detalles
          </button>
        </div>
      </div>

      {/* ROW 3: SUB-TABS & ROADMAP TABLE */}
      <div className="space-y-4">
        {/* Sub-tabs row */}
        <div className="flex items-center gap-6 border-b border-[#1b2533] pb-2 text-xs font-semibold select-none overflow-x-auto">
          {(['roadmap', 'tareas', 'agentes', 'jira', 'dependencias', 'eventos'] as const).map((tab) => (
            <button
              key={tab}
              type="button"
              id={`subtab-btn-${tab}`}
              onClick={() => setActiveTab(tab)}
              className={`pb-2 -mb-2 cursor-pointer transition uppercase text-[11px] tracking-wider ${
                activeTab === tab
                  ? 'text-white border-b-2 border-emerald-400 font-bold'
                  : 'text-zinc-400 hover:text-white font-medium'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Table Card */}
        <div className="p-5 rounded-2xl bg-[#0e141d] border border-[#1b2533] space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <GitMerge className="w-4 h-4 text-emerald-400" />
                <h3 className="text-sm font-bold text-white capitalize">
                  {activeTab === 'roadmap' ? 'Roadmap del Sprint' : `${activeTab} del Orquestador`}
                </h3>
              </div>
              <p className="text-xs text-zinc-400 mt-0.5">
                {activeTab === 'roadmap'
                  ? 'Plan generado automáticamente desde Jira, repositorio y dependencias.'
                  : `Visualización reactiva en tiempo real del módulo ${activeTab}.`}
              </p>
            </div>
            <div className="flex items-center gap-2.5">
              <select
                value={viewMode}
                onChange={(e) => setViewMode(e.target.value as any)}
                className="bg-black/60 border border-zinc-800 rounded-lg px-2.5 py-1.5 text-xs text-white font-mono cursor-pointer"
              >
                <option value="gantt">Vista: Gantt</option>
                <option value="lista">Vista: Lista</option>
              </select>
              <button
                type="button"
                onClick={() => alert('Exportando roadmap JSON/CSV...')}
                className="px-3 py-1.5 rounded-lg border border-zinc-800 hover:border-zinc-700 bg-black/40 text-xs font-medium text-zinc-300 hover:text-white flex items-center gap-1.5 cursor-pointer"
              >
                <Download className="w-3.5 h-3.5" /> Exportar
              </button>
              <button type="button" className="p-1.5 rounded-lg text-zinc-400 hover:text-white cursor-pointer">
                <MoreVertical className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Dynamic Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#1b2533] text-zinc-400 text-[11px] font-semibold">
                  <th className="pb-3 pl-1">Tarea / Identificador</th>
                  <th className="pb-3">Responsable</th>
                  <th className="pb-3">Inicio</th>
                  <th className="pb-3">Fin</th>
                  <th className="pb-3 min-w-[120px]">Progreso</th>
                  <th className="pb-3 text-right pr-2">Estado</th>
                </tr>
              </thead>
              <tbody id="dash-roadmap-tbody" className="divide-y divide-[#1b2533]/60">
                {activeTab === 'roadmap' &&
                  tasks.map((t) => (
                    <tr key={t.id} className="hover:bg-white/[0.02] transition">
                      <td className="py-3 pl-1">
                        <div className="font-semibold text-white">{t.title}</div>
                        <div className="text-[10px] font-mono text-emerald-400">{t.key}</div>
                      </td>
                      <td className="py-3">
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-[#16231d] border border-emerald-500/30 text-emerald-400 text-[11px] font-medium">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                          {t.agent}
                        </span>
                      </td>
                      <td className="py-3 font-mono text-zinc-400 text-[11px]">{t.start}</td>
                      <td className="py-3 font-mono text-zinc-400 text-[11px]">{t.end}</td>
                      <td className="py-3">
                        <div className="w-28 bg-[#1b2533] h-1.5 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              t.status === 'Completada' ? 'bg-emerald-400' : t.status === 'En progreso' ? 'bg-blue-400' : 'bg-zinc-600'
                            }`}
                            style={{ width: `${t.progress}%` }}
                          ></div>
                        </div>
                      </td>
                      <td className="py-3 text-right pr-2">
                        <span
                          className={`px-2 py-0.5 rounded-full border text-[10px] font-bold ${
                            t.status === 'Completada'
                              ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                              : t.status === 'En progreso'
                              ? 'bg-blue-500/20 text-blue-400 border-blue-500/30'
                              : 'bg-zinc-800 text-zinc-400 border-zinc-700'
                          }`}
                        >
                          {t.status}
                        </span>
                      </td>
                    </tr>
                  ))}

                {activeTab === 'agentes' &&
                  agents.map((a) => (
                    <tr key={a.id} className="hover:bg-white/[0.02] transition">
                      <td className="py-3 pl-1">
                        <div className="font-semibold text-white">{a.name}</div>
                        <div className="text-[10px] text-zinc-500 font-mono">Worktree wt-{a.name}</div>
                      </td>
                      <td className="py-3">
                        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-bold">
                          {a.role}
                        </span>
                      </td>
                      <td className="py-3 font-mono text-zinc-400 text-[11px]">Online</td>
                      <td className="py-3 font-mono text-zinc-400 text-[11px]">PID {a.pid || 8900}</td>
                      <td className="py-3">
                        <div className="w-28 bg-[#1b2533] h-1.5 rounded-full overflow-hidden">
                          <div className="bg-emerald-400 h-full rounded-full" style={{ width: a.status === 'Activo' ? '80%' : '10%' }}></div>
                        </div>
                      </td>
                      <td className="py-3 text-right pr-2">
                        <span
                          className={`px-2 py-0.5 rounded-full border text-[10px] font-bold ${
                            a.status === 'Activo'
                              ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                              : 'bg-zinc-800 text-zinc-400 border-zinc-700'
                          }`}
                        >
                          {a.status}
                        </span>
                      </td>
                    </tr>
                  ))}

                {activeTab === 'eventos' &&
                  events.slice(0, 5).map((ev) => (
                    <tr key={ev.event_id} className="hover:bg-white/[0.02] transition">
                      <td className="py-3 pl-1">
                        <div className="font-semibold text-white font-mono text-[11px]">{ev.event_type}</div>
                        <div className="text-[10px] text-zinc-500 truncate max-w-xs">{ev.payload_json?.slice(0, 50)}...</div>
                      </td>
                      <td className="py-3">
                        <span className="px-2 py-0.5 rounded bg-black/40 text-zinc-400 text-[10px] font-mono">SQLite WAL</span>
                      </td>
                      <td className="py-3 font-mono text-zinc-400 text-[11px]">
                        {ev.created_at ? new Date(ev.created_at).toLocaleTimeString() : 'ahora'}
                      </td>
                      <td className="py-3 font-mono text-zinc-400 text-[11px]">{ev.run_id || 'sys'}</td>
                      <td className="py-3">
                        <span className={`text-xs font-bold ${ev.severity === 'FATAL' ? 'text-red-400' : 'text-emerald-400'}`}>
                          {ev.severity}
                        </span>
                      </td>
                      <td className="py-3 text-right pr-2">
                        <span className="px-2 py-0.5 rounded-full border text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border-emerald-500/30">
                          Registrado
                        </span>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* ROW 4: BOTTOM 3 CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Col 1: Últimos commits */}
        <div className="p-4 rounded-2xl bg-[#0e141d] border border-[#1b2533] space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-white flex items-center gap-1.5">
              <GitCommit className="w-3.5 h-3.5 text-zinc-400" /> Últimos commits
            </span>
            <button type="button" onClick={() => onNavigateSection('github')} className="text-[11px] text-zinc-400 hover:text-white">
              Ver todos
            </button>
          </div>
          <div id="dash-commits-list" className="space-y-2.5 text-xs">
            {commits.map((c) => (
              <div
                key={c.sha}
                className="flex items-start justify-between gap-2 p-2 rounded-xl bg-black/30 border border-white/5 hover:border-white/10 transition"
              >
                <div className="space-y-0.5 min-w-0">
                  <div className="text-xs font-semibold text-white truncate max-w-[200px]" title={c.message}>
                    {c.message}
                  </div>
                  <div className="text-[10px] text-zinc-500 flex items-center gap-1.5">
                    <span className="font-mono text-emerald-400">{c.sha.slice(0, 7)}</span>
                    <span>•</span>
                    <span>{c.author}</span>
                    <span>•</span>
                    <span>{c.time}</span>
                  </div>
                </div>
                <GitCommit className="w-3.5 h-3.5 text-zinc-500 shrink-0 mt-0.5" />
              </div>
            ))}
          </div>
        </div>

        {/* Col 2: Métricas de ejecución */}
        <div className="p-4 rounded-2xl bg-[#0e141d] border border-[#1b2533] space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-white">Métricas de ejecución</span>
            <span className="text-[11px] text-zinc-500">Últimos 7 días</span>
          </div>
          <div className="flex items-center gap-3 text-[10px] text-zinc-400">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span> Completadas
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-blue-400"></span> En progreso
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-red-400"></span> Fallidas
            </span>
          </div>
          {/* Vectorial Wave Chart */}
          <div className="h-28 w-full flex items-end">
            <svg className="w-full h-full" viewBox="0 0 200 80" preserveAspectRatio="none">
              <line x1="0" y1="20" x2="200" y2="20" stroke="#1b2533" strokeDasharray="2,2" />
              <line x1="0" y1="50" x2="200" y2="50" stroke="#1b2533" strokeDasharray="2,2" />
              <path d="M0 65 Q 30 70, 60 50 T 120 30 T 160 20 T 200 45" fill="none" stroke="#10b981" strokeWidth="2" />
              <path d="M0 72 Q 40 60, 80 65 T 140 40 T 200 55" fill="none" stroke="#3b82f6" strokeWidth="1.8" />
            </svg>
          </div>
          <div className="flex justify-between text-[9px] font-mono text-zinc-500">
            <span>20/10</span>
            <span>21/10</span>
            <span>22/10</span>
            <span>23/10</span>
            <span>24/10</span>
            <span>25/10</span>
            <span>26/10</span>
          </div>
        </div>

        {/* Col 3: Proyectos */}
        <div className="p-4 rounded-2xl bg-[#0e141d] border border-[#1b2533] space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-white flex items-center gap-1.5">
              <Folder className="w-3.5 h-3.5 text-zinc-400" /> Proyectos
            </span>
            <button type="button" onClick={() => onNavigateSection('projects')} className="text-[11px] text-zinc-400 hover:text-white">
              Ver todos
            </button>
          </div>
          <div id="dash-projects-list" className="space-y-2 text-xs">
            {projects.slice(0, 3).map((p) => (
              <div key={p.id} className="p-2 rounded-xl bg-black/30 border border-white/5 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white text-xs truncate max-w-[130px]">{p.name}</span>
                  <span className="text-[10px] font-mono text-emerald-400">{p.readiness || 80}%</span>
                </div>
                <div className="w-full bg-[#1b2533] h-1 rounded-full overflow-hidden">
                  <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${p.readiness || 80}%` }}></div>
                </div>
                <div className="flex items-center justify-between text-[10px] text-zinc-500 pt-0.5">
                  <span>{p.tech_stack ? p.tech_stack.slice(0, 2).join(', ') : 'Node.js, React'}</span>
                  <span className="px-1.5 py-0.2 rounded bg-emerald-500/10 text-emerald-400 font-semibold text-[9px]">
                    {p.status || 'ACTIVE'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
