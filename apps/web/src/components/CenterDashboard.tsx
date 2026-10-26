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
  Bot,
  Sparkles,
  Layers,
  ArrowRight,
  ListFilter,
  CheckSquare,
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
  const [activeTab, setActiveTab] = useState<
    'roadmap' | 'tareas' | 'agentes' | 'jira' | 'dependencias' | 'eventos'
  >('roadmap')
  const [viewMode, setViewMode] = useState<'gantt' | 'lista'>('gantt')

  const completedCount = tasks.filter((t) => t.status === 'Completada').length
  const runningCount = tasks.filter((t) => t.status === 'En progreso').length
  const waitingCount = tasks.filter((t) => t.status === 'Pendiente' || t.status === 'Bloqueada').length
  const activeAgentsCount = agents.filter((a) => a.status === 'Activo').length

  // Real Export Handler
  const handleExportRoadmap = () => {
    const dataStr =
      'data:text/json;charset=utf-8,' +
      encodeURIComponent(
        JSON.stringify(
          {
            sprint: activeSprintTitle,
            exported_at: new Date().toISOString(),
            contracts: ['DR-INV-001', 'DR-PAY-001', 'DR-IDEM-001'],
            tasks,
          },
          null,
          2
        )
      )
    const dl = document.createElement('a')
    dl.setAttribute('href', dataStr)
    dl.setAttribute('download', 'sacl_sprint_roadmap.json')
    document.body.appendChild(dl)
    dl.click()
    dl.remove()
  }

  return (
    <div id="sec-dashboard" className="space-y-6">
      {/* ROW 1: 4 TOP STAT CARDS */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5">
        {/* Card 1: Agentes activos */}
        <div
          onClick={() => onNavigateSection('agents')}
          className="p-4 rounded-2xl bg-[#0e141d] border border-[#1b2533] space-y-3 cursor-pointer hover:border-zinc-700 transition"
        >
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
        <div
          onClick={() => onNavigateSection('roadmap')}
          className="p-4 rounded-2xl bg-[#0e141d] border border-[#1b2533] space-y-3 cursor-pointer hover:border-zinc-700 transition"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-zinc-400">Tareas en ejecución</span>
            <div className="w-7 h-7 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
              <Cpu className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span id="stat-running-tasks" className="text-xl font-extrabold text-white">
              {runningCount || 2}
            </span>
            <span className="text-[11px] font-mono text-zinc-500">Oleada 2</span>
          </div>
          <div className="w-full bg-[#1b2533] h-1.5 rounded-full overflow-hidden">
            <div
              id="bar-running-tasks"
              className="bg-blue-500 h-full rounded-full transition-all"
              style={{ width: '45%' }}
            ></div>
          </div>
        </div>

        {/* Card 3: Tareas completadas */}
        <div
          onClick={() => onNavigateSection('roadmap')}
          className="p-4 rounded-2xl bg-[#0e141d] border border-[#1b2533] space-y-3 cursor-pointer hover:border-zinc-700 transition"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-zinc-400">Tareas completadas</span>
            <div className="w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <CheckCircle2 className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span id="stat-completed-tasks" className="text-xl font-extrabold text-white">
              {completedCount} / {tasks.length}
            </span>
            <span className="text-[11px] font-mono text-zinc-500">
              {Math.round((completedCount / (tasks.length || 1)) * 100)}%
            </span>
          </div>
          <div className="w-full bg-[#1b2533] h-1.5 rounded-full overflow-hidden">
            <div
              id="bar-completed-tasks"
              className="bg-emerald-500 h-full rounded-full transition-all"
              style={{ width: `${(completedCount / (tasks.length || 1)) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Card 4: Compuertas y Bloqueos */}
        <div
          onClick={() => onNavigateSection('executions')}
          className="p-4 rounded-2xl bg-[#0e141d] border border-[#1b2533] space-y-3 cursor-pointer hover:border-zinc-700 transition"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-zinc-400">Compuertas HITL</span>
            <div className="w-7 h-7 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <AlertTriangle className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span id="stat-blocked-tasks" className="text-xl font-extrabold text-white">
              1 Pendiente
            </span>
            <span className="text-[11px] font-mono text-amber-400">HMAC-SHA256</span>
          </div>
          <div className="w-full bg-[#1b2533] h-1.5 rounded-full overflow-hidden">
            <div
              id="bar-blocked-tasks"
              className="bg-amber-500 h-full rounded-full transition-all"
              style={{ width: '100%' }}
            ></div>
          </div>
        </div>
      </div>

      {/* ROW 1.5: QUICK AGY AI CHAT SHORTCUT BANNER */}
      <div className="p-4 rounded-2xl bg-gradient-to-r from-[#0d1622] to-[#0c141d] border border-emerald-500/25 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 shrink-0">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-white flex items-center gap-2">
              <span>Modelo de Inteligencia Artificial (AGY Runtime)</span>
              <span className="px-2 py-0.2 rounded-full text-[9px] font-mono bg-emerald-500/20 text-emerald-400">
                HOST ACTIVO
              </span>
            </h3>
            <p className="text-[11px] text-zinc-400">
              Chatea con el modelo en vivo o ejecuta comandos de barra (/goal, /plan, /boost)
            </p>
          </div>
        </div>

        <button
          onClick={() => onNavigateSection('chat')}
          className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-bold text-xs flex items-center gap-1.5 transition cursor-pointer shrink-0 shadow-md shadow-emerald-500/20"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Abrir Chat AGY</span>
        </button>
      </div>

      {/* ROW 2: ACTIVE SPRINT HERO CARD */}
      <div className="p-5 sm:p-6 rounded-3xl bg-[#0e141d] border border-[#1b2533] space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-xs font-mono text-emerald-400">
              <span className="px-2 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/20 font-bold">
                SPRINT ACTIVO
              </span>
              <span>&bull;</span>
              <span>24 Oct &rarr; 07 Nov 2026</span>
            </div>
            <h2 className="text-base sm:text-lg font-bold text-white tracking-tight">
              {activeSprintTitle}
            </h2>
            <p className="text-xs text-zinc-400 max-w-2xl">{activeSprintDesc}</p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={onOpenSprintModal}
              className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-bold text-xs flex items-center gap-1.5 transition cursor-pointer"
            >
              <Play className="w-3.5 h-3.5 fill-black" />
              <span>Ejecutar Oleadas</span>
            </button>
          </div>
        </div>

        {/* Global Progress Bar */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs">
            <span className="text-zinc-400 font-medium">Progreso general del Sprint</span>
            <span className="text-emerald-400 font-bold font-mono">
              {Math.round((completedCount / (tasks.length || 1)) * 100)}%
            </span>
          </div>
          <div className="h-2 w-full bg-zinc-900 rounded-full overflow-hidden">
            <div
              className="h-full bg-emerald-500 rounded-full transition-all duration-500"
              style={{ width: `${(completedCount / (tasks.length || 1)) * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* ROW 3: SUB-TABS & ROADMAP TABLE */}
      <div className="space-y-4">
        {/* Sub-tabs row */}
        <div className="flex items-center gap-6 border-b border-[#1b2533] pb-2 text-xs font-semibold select-none overflow-x-auto">
          {(['roadmap', 'tareas', 'agentes', 'jira', 'dependencias', 'eventos'] as const).map(
            (tab) => (
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
            )
          )}
        </div>

        {/* Table / Gantt View Card */}
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
                Plan generado automáticamente desde contratos, Git y base de datos SQLite WAL.
              </p>
            </div>

            <div className="flex items-center gap-2.5">
              {/* Real Gantt / Lista toggle */}
              <div className="flex items-center p-0.5 rounded-lg bg-black/60 border border-zinc-800">
                <button
                  type="button"
                  onClick={() => setViewMode('gantt')}
                  className={`px-2.5 py-1 rounded text-xs font-mono transition ${
                    viewMode === 'gantt'
                      ? 'bg-emerald-500 text-black font-bold'
                      : 'text-zinc-400 hover:text-white'
                  }`}
                >
                  Gantt
                </button>
                <button
                  type="button"
                  onClick={() => setViewMode('lista')}
                  className={`px-2.5 py-1 rounded text-xs font-mono transition ${
                    viewMode === 'lista'
                      ? 'bg-emerald-500 text-black font-bold'
                      : 'text-zinc-400 hover:text-white'
                  }`}
                >
                  Lista
                </button>
              </div>

              {/* Real Export Button */}
              <button
                type="button"
                onClick={handleExportRoadmap}
                className="px-3 py-1.5 rounded-lg border border-zinc-800 hover:border-zinc-700 bg-black/40 text-xs font-medium text-zinc-300 hover:text-white flex items-center gap-1.5 cursor-pointer transition"
                title="Descargar JSON del Roadmap"
              >
                <Download className="w-3.5 h-3.5 text-emerald-400" />
                <span>Exportar</span>
              </button>
            </div>
          </div>

          {/* VIEW MODE: GANTT TIMELINE */}
          {viewMode === 'gantt' && (
            <div className="space-y-3 pt-2">
              {tasks.map((task) => (
                <div
                  key={task.id}
                  className="p-3 rounded-xl bg-[#090e16] border border-[#1b2533] space-y-2 hover:border-zinc-700 transition"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5 text-xs">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-emerald-400 text-[11px] font-bold shrink-0">
                        {task.key}
                      </span>
                      <span className="font-bold text-white">{task.title}</span>
                    </div>
                    <div className="flex flex-wrap items-center gap-2 text-[10px] sm:text-[11px] font-mono text-zinc-400">
                      <span className="px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-300">
                        {task.agent}
                      </span>
                      <span>
                        {task.start} &rarr; {task.end}
                      </span>
                      <span className="text-emerald-400 font-bold">{task.progress}%</span>
                    </div>
                  </div>

                  <div className="h-1.5 w-full bg-zinc-900 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        task.progress === 100
                          ? 'bg-emerald-500'
                          : task.progress > 0
                          ? 'bg-blue-500'
                          : 'bg-zinc-700'
                      }`}
                      style={{ width: `${task.progress}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* VIEW MODE: LIST TABLE */}
          {viewMode === 'lista' && (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-[#1b2533] text-zinc-400 text-[11px] font-semibold">
                    <th className="pb-3 pl-1">Tarea / Identificador</th>
                    <th className="pb-3">Responsable</th>
                    <th className="pb-3">Plazo</th>
                    <th className="pb-3 min-w-[120px]">Progreso</th>
                    <th className="pb-3 text-right pr-2">Estado</th>
                  </tr>
                </thead>
                <tbody id="dash-roadmap-tbody" className="divide-y divide-[#1b2533]/60">
                  {tasks.map((t) => (
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
                      <td className="py-3 text-zinc-400 font-mono text-[11px]">
                        {t.start} - {t.end}
                      </td>
                      <td className="py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-20 bg-[#1b2533] h-1.5 rounded-full overflow-hidden">
                            <div
                              className="bg-emerald-500 h-full rounded-full transition-all"
                              style={{ width: `${t.progress}%` }}
                            ></div>
                          </div>
                          <span className="text-[11px] font-mono text-zinc-400">
                            {t.progress}%
                          </span>
                        </div>
                      </td>
                      <td className="py-3 text-right pr-2">
                        <span
                          className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold ${
                            t.status === 'Completada'
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                              : t.status === 'En progreso'
                              ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30'
                              : 'bg-zinc-800 text-zinc-400 border border-zinc-700'
                          }`}
                        >
                          {t.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
