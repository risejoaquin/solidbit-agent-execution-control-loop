import React, { useState, useEffect } from 'react'
import {
  Zap,
  Cpu,
  CheckCircle2,
  AlertTriangle,
  Play,
  GitMerge,
  Download,
  Terminal,
  ShieldCheck,
  Loader2,
  Layers,
  CheckSquare,
  Sparkles,
  ArrowRight,
  GitBranch,
  Activity,
} from 'lucide-react'
import type {
  TaskItem,
  AgentItem,
  CommitItem,
  Project,
  ActivityEvent,
  AgentProcess,
} from '../types/orchestrator'
import { LogTerminal } from './LogTerminal'
import { AgentFleetProcessTable } from './AgentFleetProcessTable'
import { ConnectedTechnologiesMatrix, type TechnologyItem } from './ConnectedTechnologiesMatrix'

interface CenterDashboardProps {
  tasks: TaskItem[]
  agents: AgentItem[]
  commits: CommitItem[]
  projects: Project[]
  events: ActivityEvent[]
  connections?: TechnologyItem[]
  onRefreshConnections?: () => void
  activeSprintTitle?: string
  activeSprintDesc?: string
  onOpenSprintModal: () => void
  onNavigateSection: (section: string) => void
  pendingGatesCount?: number
}

export const CenterDashboard: React.FC<CenterDashboardProps> = ({
  tasks,
  agents,
  events,
  connections = [],
  onRefreshConnections,
  activeSprintTitle = 'Sprint 1 — MVP E-commerce (DR-INV-001 & DR-PAY-001)',
  activeSprintDesc = 'Flujo de venta atómica, contratos congelados SellableUnit y ledger de doble partida sin sobreventa.',
  onOpenSprintModal,
  onNavigateSection,
  pendingGatesCount = 0,
}) => {
  const [viewMode, setViewMode] = useState<'gantt' | 'lista'>('gantt')
  const [executingAction, setExecutingAction] = useState<string | null>(null)
  const [lastExecutionResult, setLastExecutionResult] = useState<any | null>(null)
  const [processes, setProcesses] = useState<AgentProcess[]>([])

  useEffect(() => {
    let isMounted = true
    const fetchRealOSProcesses = async () => {
      try {
        const res = await fetch('/api/agents/fleet')
        if (!res.ok) return
        const data = await res.json()
        if (isMounted) {
          if (data.active_agents && data.active_agents.length > 0) {
            setProcesses(data.active_agents)
          } else {
            setProcesses([])
          }
        }
      } catch (err) {
        console.warn('Real agent fleet poll skipped:', err)
      }
    }

    fetchRealOSProcesses()
    const interval = setInterval(fetchRealOSProcesses, 10000)
    return () => {
      isMounted = false
      clearInterval(interval)
    }
  }, [])

  const completedCount = tasks.filter((t) => t.status === 'Completada').length
  const runningCount = tasks.filter((t) => t.status === 'En progreso').length
  const activeAgentsCount = agents.filter((a) => a.status === 'Activo').length
  const progressPercent = tasks.length > 0 ? Math.round((completedCount / tasks.length) * 100) : 0

  const handleExecuteRealAction = async (
    actionType: 'campaign_sprint' | 'test_suite' | 'security_audit',
    targetAgentId?: string
  ) => {
    setExecutingAction(actionType)
    const agentToActivate =
      targetAgentId ||
      (actionType === 'test_suite'
        ? 'AGENT-QA-03'
        : actionType === 'security_audit'
        ? 'AGENT-GOV-02'
        : 'AGY-HOST-01')

    setProcesses((prev) =>
      prev.map((p) =>
        p.id === agentToActivate
          ? {
              ...p,
              state: 'RUNNING',
              lastCommand:
                actionType === 'test_suite'
                  ? 'pytest tests/ui/test_cli_ui.py -q'
                  : actionType === 'security_audit'
                  ? 'sacl audit invariants --strict'
                  : 'sacl wave dispatch --kahn-dag',
            }
          : p
      )
    )

    try {
      const res = await fetch('/api/actions/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: actionType, params: {} }),
      })
      const data = await res.json()
      setLastExecutionResult(data)
      setProcesses((prev) =>
        prev.map((p) =>
          p.id === agentToActivate
            ? {
                ...p,
                state: data.gate_request_id ? 'BLOCKED_ON_GATE' : 'COMPLETED',
              }
            : p
        )
      )
    } catch (err) {
      console.error('Error executing action:', err)
    } finally {
      setExecutingAction(null)
    }
  }

  const handleExportRoadmap = () => {
    const dataStr =
      'data:text/json;charset=utf-8,' +
      encodeURIComponent(
        JSON.stringify(
          {
            sprint: activeSprintTitle,
            exported_at: new Date().toISOString(),
            tasks,
          },
          null,
          2
        )
      )
    const downloadAnchor = document.createElement('a')
    downloadAnchor.setAttribute('href', dataStr)
    downloadAnchor.setAttribute('download', 'sacl_sprint_roadmap.json')
    document.body.appendChild(downloadAnchor)
    downloadAnchor.click()
    downloadAnchor.remove()
  }

  // SDLC 5-Stage Pipeline Steps
  const sdlcStages = [
    {
      step: '01',
      title: '1. Requisitos & Jira',
      subtitle: `${tasks.length} tickets en backlog`,
      icon: CheckSquare,
      action: () => onNavigateSection('jira'),
      active: tasks.length > 0,
    },
    {
      step: '02',
      title: '2. Diseño DAG (Kahn)',
      subtitle: 'Topología acíclica',
      icon: GitBranch,
      action: onOpenSprintModal,
      active: true,
    },
    {
      step: '03',
      title: '3. Flota de Agentes',
      subtitle: activeAgentsCount === 0 ? 'Zero-Token Idle' : `${activeAgentsCount} activos`,
      icon: Cpu,
      action: () => onNavigateSection('agents'),
      active: activeAgentsCount > 0,
    },
    {
      step: '04',
      title: '4. QA & Invariantes',
      subtitle: 'DR-INV-001 & DR-PAY-001',
      icon: ShieldCheck,
      action: () => handleExecuteRealAction('test_suite'),
      active: true,
    },
    {
      step: '05',
      title: '5. Compuerta HITL',
      subtitle: pendingGatesCount > 0 ? `${pendingGatesCount} por firmar` : 'Cero bloqueos',
      icon: AlertTriangle,
      action: () => onNavigateSection('executions'),
      highlight: pendingGatesCount > 0,
    },
  ]

  return (
    <div className="space-y-5 max-w-7xl mx-auto">
      {/* 1. UNIFIED COMMAND COCKPIT HERO & SDLC PIPELINE STEPPER */}
      <section
        aria-label="Centro de Comando del Sprint y Flujo SDLC"
        className="rounded-3xl bg-zinc-950 border border-zinc-800/90 p-5 sm:p-6 space-y-5 shadow-2xl relative overflow-hidden"
      >
        {/* Top Row: Sprint Context + Immediate Execution Triggers */}
        <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-5">
          <div className="space-y-2 max-w-2xl">
            <div className="flex flex-wrap items-center gap-2 text-[11px] font-mono">
              <span className="px-2.5 py-0.5 rounded-full bg-white text-black font-extrabold tracking-tight">
                SPRINT ACTIVO
              </span>
              <span className="px-2.5 py-0.5 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-300">
                SB-ENG-HB-001 v1.0
              </span>
              <span className="text-zinc-400">
                {new Date().toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })} &rarr;{' '}
                {new Date(Date.now() + 14 * 86400000).toLocaleDateString('es-ES', {
                  day: 'numeric',
                  month: 'short',
                  year: 'numeric',
                })}
              </span>
            </div>

            <h1 className="text-lg sm:text-2xl font-extrabold text-white tracking-tight leading-snug">
              {activeSprintTitle}
            </h1>
            <p className="text-xs sm:text-sm text-zinc-400 leading-relaxed">{activeSprintDesc}</p>
          </div>

          {/* Right Action Cluster: Primary Dispatch + Quick Audits */}
          <div className="flex flex-wrap items-center gap-2.5 shrink-0">
            <button
              type="button"
              onClick={() => handleExecuteRealAction('campaign_sprint')}
              disabled={executingAction !== null}
              className="px-4 py-2.5 rounded-xl bg-white hover:bg-zinc-200 disabled:opacity-50 text-black font-extrabold text-xs flex items-center gap-2 transition cursor-pointer shadow-md active:scale-[0.99]"
            >
              {executingAction === 'campaign_sprint' ? (
                <Loader2 className="w-4 h-4 animate-spin text-black" />
              ) : (
                <Play className="w-4 h-4 fill-black text-black" />
              )}
              <span>Lanzar Oleada Kahn</span>
            </button>

            <button
              type="button"
              onClick={onOpenSprintModal}
              className="px-3.5 py-2.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-100 border border-zinc-700 font-bold text-xs flex items-center gap-2 transition cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5 text-zinc-200" />
              <span>Diseñar Sprint</span>
            </button>

            <button
              type="button"
              onClick={() => handleExecuteRealAction('test_suite')}
              disabled={executingAction !== null}
              className="px-3.5 py-2.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border border-zinc-800 font-semibold text-xs flex items-center gap-1.5 transition cursor-pointer"
            >
              {executingAction === 'test_suite' ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              )}
              <span>Pytest QA</span>
            </button>

            <button
              type="button"
              onClick={() => handleExecuteRealAction('security_audit')}
              disabled={executingAction !== null}
              className="px-3.5 py-2.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border border-zinc-800 font-semibold text-xs flex items-center gap-1.5 transition cursor-pointer"
            >
              {executingAction === 'security_audit' ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <ShieldCheck className="w-3.5 h-3.5 text-zinc-300" />
              )}
              <span>Auditar Invariantes</span>
            </button>
          </div>
        </div>

        {/* Interactive 5-Stage SDLC Workflow Stepper */}
        <div className="pt-4 border-t border-zinc-850">
          <div className="flex items-center justify-between mb-2.5">
            <span className="text-[10px] font-mono uppercase tracking-widest text-zinc-400 font-bold">
              Flujo Operativo del Ciclo de Vida (Haz clic en cualquier etapa para operar)
            </span>
            <span className="text-xs font-mono font-bold text-white">
              Avance del Sprint: {progressPercent}%
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2.5">
            {sdlcStages.map((st, idx) => {
              const Icon = st.icon
              return (
                <button
                  key={st.step}
                  type="button"
                  onClick={st.action}
                  className={`p-3 rounded-2xl border text-left transition-all flex items-center justify-between group cursor-pointer ${
                    st.highlight
                      ? 'bg-amber-500/10 border-amber-500/30 hover:border-amber-400'
                      : 'bg-black/70 border-zinc-800/90 hover:border-zinc-600 hover:bg-zinc-900/60'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div
                      className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 border ${
                        st.highlight
                          ? 'bg-amber-500/20 border-amber-500/40 text-amber-300'
                          : 'bg-zinc-900 border-zinc-800 text-zinc-200 group-hover:bg-white group-hover:text-black transition-colors'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="truncate">
                      <div className="text-xs font-bold text-white truncate">{st.title}</div>
                      <div
                        className={`text-[10px] font-mono truncate ${
                          st.highlight ? 'text-amber-300 font-semibold' : 'text-zinc-400'
                        }`}
                      >
                        {st.subtitle}
                      </div>
                    </div>
                  </div>
                  {idx < 4 && (
                    <ArrowRight className="w-3.5 h-3.5 text-zinc-600 group-hover:text-zinc-300 shrink-0 hidden lg:block" />
                  )}
                </button>
              )
            })}
          </div>
        </div>
      </section>

      {/* Live Execution Feedback Banner */}
      {lastExecutionResult && (
        <div
          role="status"
          aria-live="polite"
          className="p-4 rounded-2xl bg-zinc-950 border border-zinc-700 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono animate-fade-in shadow-lg"
        >
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            <div>
              <div className="font-bold text-white">
                {lastExecutionResult.title || 'Ejecución Completada'} (ID: {lastExecutionResult.execution_id})
              </div>
              <div className="text-zinc-400 text-[11px]">
                {lastExecutionResult.summary || 'Sincronizado en SQLite WAL con 0 errores.'}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-emerald-400 font-bold text-[11px]">● Auditado en WAL</span>
            <button
              type="button"
              onClick={() => setLastExecutionResult(null)}
              className="px-2.5 py-1 rounded-lg bg-zinc-900 text-zinc-300 hover:text-white transition cursor-pointer"
            >
              Cerrar
            </button>
          </div>
        </div>
      )}

      {/* 2. TELEMETRY BENTO GRID (4 METRIC CARDS) */}
      <section aria-label="Métricas Operativas" className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {/* Metric 1: Flota de Agentes */}
        <div
          onClick={() => onNavigateSection('agents')}
          className="p-4 rounded-2xl bg-zinc-950 border border-zinc-800/90 space-y-2 cursor-pointer hover:border-zinc-600 transition group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-zinc-400 group-hover:text-zinc-200 transition">
              Flota de Agentes
            </span>
            <div className="w-7 h-7 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-200">
              <Zap className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-lg sm:text-2xl font-extrabold text-white font-mono">
              {activeAgentsCount} Activos
            </span>
            <span className="text-[10px] font-mono text-zinc-400">
              {activeAgentsCount === 0 ? 'Zero-Token Idle' : 'En Ejecución'}
            </span>
          </div>
        </div>

        {/* Metric 2: Tareas del Sprint */}
        <div
          onClick={() => onNavigateSection('roadmap')}
          className="p-4 rounded-2xl bg-zinc-950 border border-zinc-800/90 space-y-2 cursor-pointer hover:border-zinc-600 transition group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-zinc-400 group-hover:text-zinc-200 transition">
              Tareas del Sprint
            </span>
            <div className="w-7 h-7 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-200">
              <Activity className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-lg sm:text-2xl font-extrabold text-white font-mono">
              {runningCount} / {tasks.length}
            </span>
            <span className="text-[10px] font-mono text-zinc-400">
              {completedCount} Completadas
            </span>
          </div>
        </div>

        {/* Metric 3: Contratos Congelados */}
        <div
          onClick={() => onNavigateSection('workflows')}
          className="p-4 rounded-2xl bg-zinc-950 border border-zinc-800/90 space-y-2 cursor-pointer hover:border-zinc-600 transition group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-zinc-400 group-hover:text-zinc-200 transition">
              Contratos Congelados
            </span>
            <div className="w-7 h-7 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-emerald-400">
              <ShieldCheck className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-lg sm:text-2xl font-extrabold text-white font-mono">6 / 6</span>
            <span className="text-[10px] font-mono text-emerald-400 font-semibold">100% Blindados</span>
          </div>
        </div>

        {/* Metric 4: Compuertas HITL */}
        <div
          onClick={() => onNavigateSection('executions')}
          className="p-4 rounded-2xl bg-zinc-950 border border-zinc-800/90 space-y-2 cursor-pointer hover:border-zinc-600 transition group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-zinc-400 group-hover:text-zinc-200 transition">
              Compuertas HITL
            </span>
            <div className="w-7 h-7 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-amber-400">
              <AlertTriangle className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-lg sm:text-2xl font-extrabold text-white font-mono">
              {pendingGatesCount} {pendingGatesCount === 1 ? 'Pendiente' : 'Pendientes'}
            </span>
            <span className={`text-[10px] font-mono ${pendingGatesCount > 0 ? 'text-amber-400 font-bold' : 'text-zinc-500'}`}>
              {pendingGatesCount > 0 ? 'Requiere Firma' : 'Al Día'}
            </span>
          </div>
        </div>
      </section>

      {/* 3. TWO-COLUMN OPERATIONAL WORKSPACE: ROADMAP (LEFT) + AGENT FLEET STATUS (RIGHT) */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-5 items-start">
        {/* Left 7 Columns: Roadmap & Backlog Execution */}
        <section
          aria-label="Plan de Trabajo del Sprint"
          className="xl:col-span-7 p-5 rounded-3xl bg-zinc-950 border border-zinc-800/90 space-y-4 shadow-xl"
        >
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-850 pb-3.5">
            <div>
              <div className="flex items-center gap-2">
                <GitMerge className="w-4 h-4 text-zinc-200" />
                <h2 className="text-sm font-bold text-white">
                  Backlog Activo & Cronograma de Trabajo
                </h2>
              </div>
              <p className="text-[11px] text-zinc-400 mt-0.5">
                Tareas sincronizadas con Jira y particionado topológico de Kahn.
              </p>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <div className="flex items-center p-0.5 rounded-xl bg-black border border-zinc-800">
                <button
                  type="button"
                  onClick={() => setViewMode('gantt')}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-mono transition cursor-pointer ${
                    viewMode === 'gantt' ? 'bg-white text-black font-bold' : 'text-zinc-400 hover:text-white'
                  }`}
                >
                  Gantt
                </button>
                <button
                  type="button"
                  onClick={() => setViewMode('lista')}
                  className={`px-2.5 py-1 rounded-lg text-[11px] font-mono transition cursor-pointer ${
                    viewMode === 'lista' ? 'bg-white text-black font-bold' : 'text-zinc-400 hover:text-white'
                  }`}
                >
                  Tabla
                </button>
              </div>

              <button
                type="button"
                onClick={handleExportRoadmap}
                className="px-2.5 py-1.5 rounded-xl border border-zinc-800 hover:border-zinc-700 bg-black text-[11px] font-mono text-zinc-300 hover:text-white flex items-center gap-1.5 cursor-pointer transition"
                title="Descargar JSON del Roadmap"
              >
                <Download className="w-3 h-3" />
                <span>JSON</span>
              </button>
            </div>
          </div>

          {tasks.length === 0 ? (
            <div className="p-8 text-center rounded-2xl bg-black border border-zinc-850 space-y-3">
              <Layers className="w-6 h-6 text-zinc-500 mx-auto" />
              <div className="text-xs font-bold text-white">Sin tareas asignadas al sprint actual</div>
              <div className="flex items-center justify-center gap-2 pt-1">
                <button
                  type="button"
                  onClick={onOpenSprintModal}
                  className="px-3 py-1.5 rounded-xl bg-white text-black font-bold text-xs hover:bg-zinc-200 transition cursor-pointer"
                >
                  + Diseñar Sprint
                </button>
                <button
                  type="button"
                  onClick={() => onNavigateSection('jira')}
                  className="px-3 py-1.5 rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-200 text-xs hover:bg-zinc-800 transition cursor-pointer"
                >
                  Abrir Jira
                </button>
              </div>
            </div>
          ) : viewMode === 'gantt' ? (
            <div className="space-y-2.5 max-h-[380px] overflow-y-auto custom-scroll pr-1">
              {tasks.map((task) => (
                <div
                  key={task.id}
                  className="p-3 rounded-2xl bg-black border border-zinc-800/80 space-y-2 hover:border-zinc-600 transition"
                >
                  <div className="flex items-center justify-between gap-2 text-xs">
                    <div className="flex items-center gap-2 min-w-0">
                      <span className="font-mono text-zinc-300 text-[10px] px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800 font-bold shrink-0">
                        {task.key}
                      </span>
                      <span className="font-bold text-white truncate">{task.title}</span>
                    </div>
                    <span className="text-[11px] font-mono text-white font-bold shrink-0">
                      {task.progress}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[10px] font-mono text-zinc-400">
                    <span>{task.agent}</span>
                    <span>
                      {task.start} &rarr; {task.end}
                    </span>
                  </div>
                  <div className="h-1.5 w-full bg-zinc-900 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-white rounded-full transition-all"
                      style={{ width: `${task.progress}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="overflow-x-auto custom-scroll max-h-[380px]">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-zinc-800 text-zinc-400 text-[10px] font-mono uppercase">
                    <th className="pb-2.5">Clave / Tarea</th>
                    <th className="pb-2.5">Fase</th>
                    <th className="pb-2.5">Avance</th>
                    <th className="pb-2.5 text-right">Estado</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-850">
                  {tasks.map((t) => (
                    <tr key={t.id} className="hover:bg-zinc-900/40 transition">
                      <td className="py-2.5 pr-2">
                        <div className="font-bold text-white text-xs">{t.title}</div>
                        <div className="text-[10px] font-mono text-zinc-400">{t.key}</div>
                      </td>
                      <td className="py-2.5 text-[11px] font-mono text-zinc-300">{t.agent}</td>
                      <td className="py-2.5 font-mono text-xs text-white font-bold">{t.progress}%</td>
                      <td className="py-2.5 text-right">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-zinc-900 text-zinc-300 border border-zinc-800">
                          {t.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* Right 5 Columns: Agent Fleet Status */}
        <div className="xl:col-span-5">
          <AgentFleetProcessTable
            processes={processes}
            onExecuteAgent={(id) => handleExecuteRealAction('campaign_sprint', id)}
            executingId={executingAction ? 'RUNNING' : null}
          />
        </div>
      </div>

      {/* 4. COMPACT CONNECTED TECHNOLOGIES PILL BAR */}
      <ConnectedTechnologiesMatrix
        connections={connections}
        onRefresh={onRefreshConnections}
        onNavigateSection={onNavigateSection}
      />

      {/* 5. STRUCTURED LOG TERMINAL */}
      <LogTerminal
        initialEvents={events}
        onOpenGate={() => onNavigateSection('executions')}
      />
    </div>
  )
}
