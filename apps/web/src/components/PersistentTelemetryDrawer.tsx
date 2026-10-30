import React, { useState } from 'react'
import {
  PanelRightClose,
  PanelRight,
  Activity,
  Cpu,
  GitBranch,
  ShieldCheck,
  ExternalLink,
  ChevronUp,
  ChevronDown,
  Terminal,
  Clock,
  Layers,
  RotateCcw,
  RefreshCw,
  Trash2,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  Send,
  Play,
} from 'lucide-react'
import type { AgentItem, CommitItem, Project, ActivityEvent } from '../types/orchestrator'
import { StatusBadge } from './ui/status-badge'
import { LogTerminal } from './LogTerminal'
import { useLanguage } from '../context/LanguageContext'

interface PersistentTelemetryDrawerProps {
  daemonPort?: number
  activeProject?: Project
  activeBranch?: string
  agents: AgentItem[]
  commits: CommitItem[]
  events: ActivityEvent[]
  onNavigateSection: (section: string) => void
  onRefreshTelemetry?: () => void
  onSimulateConflict?: () => void
  hasConflict?: boolean
}

export const PersistentTelemetryDrawer: React.FC<PersistentTelemetryDrawerProps> = ({
  daemonPort = 8765,
  activeProject,
  activeBranch = 'worktrees/scheduler',
  agents,
  commits,
  events,
  onNavigateSection,
  onRefreshTelemetry,
  onSimulateConflict,
  hasConflict = false,
}) => {
  const { t } = useLanguage()
  const [activeTab, setActiveTab] = useState<'telemetry' | 'console'>('telemetry')
  const [lifecycleLoading, setLifecycleLoading] = useState<string | null>(null)
  const [feedback, setFeedback] = useState<string | null>(null)
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false)

  const handleAction = async (action: 'retry' | 'revert' | 'release') => {
    setLifecycleLoading(action)
    setFeedback(null)
    try {
      const currentCommitSha = commits[0]?.sha || 'HEAD'
      const context = {
        git_branch: activeBranch,
        worktree_path: activeProject?.path || '.',
        commit_sha: currentCommitSha,
      }

      let actionName = 'security_audit'
      let actionParams: any = { ...context }
      if (action === 'revert') {
        actionName = 'revert_fsm'
        actionParams = { fix: true, note: 'Reversión FSM a estado seguro', ...context }
      } else if (action === 'release') {
        actionName = 'release_worktree'
        actionParams = { clean_worktrees: true, ...context }
      }

      const body = {
        action: actionName,
        action_type: actionName,
        params: actionParams,
        context,
      }

      const res = await fetch('/api/actions/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-git-branch': activeBranch,
          'x-worktree-path': activeProject?.path || '.',
          'x-commit-sha': currentCommitSha,
        },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (res.ok) {
        setFeedback(
          action === 'retry'
            ? t('Verificación reejecutada exitosamente.', 'Verification executed successfully.')
            : action === 'revert'
            ? t('FSM revertida a estado seguro.', 'FSM reverted to safe state.')
            : t('Worktrees liberados con éxito.', 'Worktrees released successfully.')
        )
        onRefreshTelemetry?.()
      } else {
        setFeedback(data.error || t('Error en operación.', 'Operation error.'))
      }
    } catch (e: any) {
      setFeedback(e.message || t('Error de conexión.', 'Connection error.'))
    } finally {
      setLifecycleLoading(null)
    }
  }

  const activeAgentsCount = agents.filter((a) => a.status === 'Activo').length

  return (
    <aside
      id="persistent-telemetry-drawer"
      data-testid="persistent-telemetry-drawer"
      className={`border-l border-white/5 bg-[#0C0C0E] flex flex-col justify-between shrink-0 h-full select-none transition-all duration-300 ${
        isCollapsed ? 'w-14' : 'w-full xl:w-96'
      }`}
    >
      {/* Header del Panel Lateral */}
      <div className="p-3.5 border-b border-white/5 bg-[#0C0C0E] flex items-center justify-between gap-1">
        <button
          type="button"
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-white transition cursor-pointer"
          title={isCollapsed ? t('Expandir telemetría', 'Expand telemetry') : t('Colapsar telemetría', 'Collapse telemetry')}
        >
          {isCollapsed ? <PanelRight className="w-3.5 h-3.5 text-emerald-400" /> : <PanelRightClose className="w-3.5 h-3.5" />}
        </button>
        {!isCollapsed && (
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-emerald-400" />
            <span className="text-xs font-mono font-extrabold uppercase tracking-wider text-white">
              {t('Telemetría', 'Telemetry')}
            </span>
          </div>
        )}

        {/* Tab Switcher: Métricas vs Consola FSM en Vivo */}
        <div className="flex items-center p-1 rounded-xl bg-black border border-white/5">
          <button
            type="button"
            onClick={() => setActiveTab('telemetry')}
            className={`px-2.5 py-1 rounded-lg text-[11px] font-mono font-bold transition cursor-pointer ${
              activeTab === 'telemetry' ? 'bg-zinc-800 text-white' : 'text-zinc-400 hover:text-white'
            }`}
          >
            {t('Métricas', 'Metrics')}
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('console')}
            className={`px-2.5 py-1 rounded-lg text-[11px] font-mono font-bold transition flex items-center gap-1 cursor-pointer ${
              activeTab === 'console' ? 'bg-zinc-800 text-white' : 'text-zinc-400 hover:text-white'
            }`}
          >
            <Terminal className="w-3 h-3 text-cyan-400" />
            <span>{t('Consola FSM', 'FSM Console')}</span>
          </button>
        </div>
      </div>

      {/* Contenido Principal con Scroll */}
      <div className="flex-1 overflow-y-auto custom-scroll p-4 space-y-4">
        {feedback && (
          <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/40 text-[11px] text-emerald-200 flex items-center justify-between gap-2 animate-fade-in">
            <span>{feedback}</span>
            <button
              type="button"
              onClick={() => setFeedback(null)}
              className="underline text-[10px] cursor-pointer"
            >
              OK
            </button>
          </div>
        )}

        {activeTab === 'telemetry' ? (
          <div className="space-y-4 text-xs font-mono animate-fade-in">
            {/* 1. Salud del Daemon Local */}
            <div className="p-4 rounded-2xl bg-[#121215] border border-white/5 space-y-3 shadow-md">
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase text-zinc-400 font-bold tracking-wider">
                  {t('Estado del Daemon', 'Daemon Status')}
                </span>
                <StatusBadge status="SUCCESS" label={`Puerto ${daemonPort}`} pulsing />
              </div>

              <div className="space-y-2 text-[11px]">
                <div className="flex items-center justify-between p-2 rounded-xl bg-black border border-white/5">
                  <span className="text-zinc-400">{t('Procesos SO', 'OS Processes')}</span>
                  <span className="text-white font-bold">
                    {activeAgentsCount === 0
                      ? t('0 en reposo (Zero-Token)', '0 idle (Zero-Token)')
                      : `${activeAgentsCount} activos`}
                  </span>
                </div>

                <div className="flex items-center justify-between p-2 rounded-xl bg-black border border-white/5">
                  <span className="text-zinc-400">{t('Rama Activa', 'Active Branch')}</span>
                  <span className="text-sky-300 font-bold flex items-center gap-1.5 truncate max-w-[160px]">
                    <GitBranch className="w-3 h-3 text-sky-400 shrink-0" />
                    <span className="truncate">{activeBranch}</span>
                  </span>
                </div>

                <div className="flex items-center justify-between p-2 rounded-xl bg-black border border-white/5">
                  <span className="text-zinc-400">{t('Aislamiento Worktree', 'Worktree Isolation')}</span>
                  <span className="text-emerald-400 font-semibold flex items-center gap-1">
                    <ShieldCheck className="w-3 h-3" />
                    {t('Aislado &bull; Limpio', 'Isolated &bull; Clean')}
                  </span>
                </div>
              </div>
            </div>

            {/* 1b. Nodos de Agente y Telemetría FSM */}
            <div className="p-4 rounded-2xl bg-[#121215] border border-white/5 space-y-3 shadow-md">
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase text-zinc-400 font-bold tracking-wider">
                  {t('Nodos de Agente (FSM)', 'Agent Nodes (FSM)')}
                </span>
                <span className="text-[10px] font-mono text-zinc-500">
                  {agents.length} {t('nodos', 'nodes')}
                </span>
              </div>

              {agents.length === 0 ? (
                <div className="p-3 rounded-xl bg-black border border-white/5 text-[11px] text-zinc-500 text-center font-sans">
                  {t('No hay agentes activos en ejecución.', 'No active agents executing.')}
                </div>
              ) : (
                <div className="space-y-2">
                  {agents.slice(0, 4).map((a) => {
                    const isPass =
                      a.status === 'PASS' ||
                      a.status === 'Completado' ||
                      a.status_type === 'PASS' ||
                      a.status === 'Activo'
                    const isBlocked = a.status === 'BLOCKED' || a.status === 'Bloqueado'
                    const isError = a.status === 'ERROR' || a.status === 'Fallo'

                    const borderCol = isPass
                      ? 'border-emerald-500/40 bg-emerald-950/20 text-emerald-300'
                      : isBlocked
                      ? 'border-amber-500/40 bg-amber-950/20 text-amber-300'
                      : isError
                      ? 'border-rose-500/40 bg-rose-950/20 text-rose-300'
                      : 'border-white/5 bg-black text-zinc-300'

                    return (
                      <div
                        key={a.id || a.name}
                        data-testid={`telemetry-agent-${a.name.toLowerCase()}`}
                        className={`p-2.5 rounded-xl border flex items-center justify-between gap-2 transition-all ${borderCol}`}
                      >
                        <div className="min-w-0">
                          <div className="flex items-center gap-1.5">
                            <span
                              className={`w-2 h-2 rounded-full shrink-0 ${
                                isPass
                                  ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]'
                                  : isBlocked
                                  ? 'bg-amber-400'
                                  : isError
                                  ? 'bg-rose-400'
                                  : 'bg-zinc-500'
                              }`}
                            />
                            <span className="font-bold text-white text-xs truncate">{a.name}</span>
                          </div>
                          <span className="text-[10px] text-zinc-400 block truncate font-sans">
                            {a.role || 'Autonomous Specialist'}
                          </span>
                        </div>
                        <div className="flex flex-col items-end gap-1 shrink-0">
                          <span
                            data-testid={`agent-status-${a.name.toLowerCase()}`}
                            className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border ${
                              isPass
                                ? 'bg-emerald-900/40 border-emerald-500/40 text-emerald-300'
                                : isBlocked
                                ? 'bg-amber-900/40 border-amber-500/40 text-amber-300'
                                : isError
                                ? 'bg-rose-900/40 border-rose-500/40 text-rose-300'
                                : 'bg-zinc-800 border-zinc-700 text-zinc-400'
                            }`}
                          >
                            {a.status}
                          </span>
                          {a.commit_sha && (
                            <code
                              data-testid={`agent-commit-${a.name.toLowerCase()}`}
                              className="text-[9px] text-sky-400 font-mono"
                            >
                              {a.commit_sha.substring(0, 8)}
                            </code>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>

            {/* 2. Control de Ciclo de Vida Rápido */}
            <div className="p-4 rounded-2xl bg-[#121215] border border-white/5 space-y-2.5 shadow-md">
              <span className="text-[10px] uppercase text-zinc-400 font-bold tracking-wider block">
                {t('Operaciones de Ciclo de Vida', 'Lifecycle Operations')}
              </span>
              <div className="grid grid-cols-1 gap-2">
                <button
                  type="button"
                  data-testid="btn-action-retry"
                  onClick={() => handleAction('retry')}
                  disabled={lifecycleLoading !== null}
                  className="w-full py-2 px-3 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-750 text-zinc-200 text-[11px] font-semibold transition cursor-pointer flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {lifecycleLoading === 'retry' ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <RefreshCw className="w-3.5 h-3.5 text-emerald-400" />
                  )}
                  <span>{t('Reintentar Verificación', 'Retry Verification')}</span>
                </button>

                <button
                  type="button"
                  data-testid="btn-action-revert"
                  onClick={() => handleAction('revert')}
                  disabled={lifecycleLoading !== null}
                  className="w-full py-2 px-3 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-750 text-zinc-200 text-[11px] font-semibold transition cursor-pointer flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {lifecycleLoading === 'revert' ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <RotateCcw className="w-3.5 h-3.5 text-amber-400" />
                  )}
                  <span>{t('Revertir FSM a Estado Seguro', 'Revert FSM to Safe State')}</span>
                </button>

                <button
                  type="button"
                  data-testid="btn-action-release"
                  onClick={() => handleAction('release')}
                  disabled={lifecycleLoading !== null}
                  className="w-full py-2 px-3 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-750 text-zinc-200 text-[11px] font-semibold transition cursor-pointer flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {lifecycleLoading === 'release' ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Trash2 className="w-3.5 h-3.5 text-rose-400" />
                  )}
                  <span>{t('Forzar Liberación de Worktree', 'Force Release Worktree')}</span>
                </button>
              </div>
            </div>

            {/* 3. Últimos Commits Registrados */}
            <div className="p-4 rounded-2xl bg-[#121215] border border-white/5 space-y-2.5 shadow-md">
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase text-zinc-400 font-bold tracking-wider">
                  {t('Últimos Commits Git', 'Recent Git Commits')}
                </span>
                <button
                  type="button"
                  onClick={() => onNavigateSection('github')}
                  className="text-[10px] text-zinc-400 hover:text-white flex items-center gap-1"
                >
                  {t('Ver todo', 'View all')}
                  <ExternalLink className="w-3 h-3" />
                </button>
              </div>

              <div className="space-y-1.5">
                {commits.slice(0, 3).map((c, i) => (
                  <div
                    key={c.sha || i}
                    data-testid="latest-commit-item"
                    className="p-2.5 rounded-xl bg-black border border-white/5 flex items-center justify-between gap-2 text-[10px]"
                  >
                    <span className="text-zinc-300 truncate max-w-[190px]">{c.message}</span>
                    <code
                      data-testid="telemetry-commit-sha"
                      className="text-sky-400 bg-sky-950/30 px-1.5 py-0.5 rounded border border-sky-500/20 shrink-0 font-mono font-bold"
                    >
                      {c.sha?.substring(0, 8) || 'HEAD'}
                    </code>
                  </div>
                ))}
              </div>
            </div>

            {/* 4. Simulador de Invariante FSM */}
            {onSimulateConflict && (
              <div className="p-4 rounded-2xl bg-[#121215] border border-white/5 space-y-2 shadow-md">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] uppercase text-zinc-400 font-bold tracking-wider">
                    {t('Simulador Invariante FSM', 'FSM Invariant Simulator')}
                  </span>
                  <Cpu className="w-3.5 h-3.5 text-zinc-500" />
                </div>
                <p className="text-[10px] text-zinc-400 leading-relaxed font-sans">
                  {t(
                    'Verifica la contención preventiva y la recuperación interactiva de estados sin alterar código.',
                    'Test preventive containment and interactive state recovery without altering code.'
                  )}
                </p>
                <button
                  type="button"
                  onClick={onSimulateConflict}
                  className="w-full py-2 px-3 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-750 text-zinc-200 text-[11px] font-semibold transition cursor-pointer"
                >
                  {hasConflict
                    ? t('Desactivar Incidencia', 'Disable Conflict')
                    : t('Simular Incidencia Preventiva', 'Simulate Preventive Issue')}
                </button>
              </div>
            )}
          </div>
        ) : (
          /* Consola FSM con Ticker de Eventos en Tiempo Real */
          <div className="h-full space-y-3 animate-fade-in">
            <LogTerminal initialEvents={events} />
          </div>
        )}
      </div>

      {/* Footer del Panel Lateral: Protocolos de Durabilidad */}
      <div className="p-3 border-t border-white/5 bg-[#0C0C0E]">
        <div className="flex items-center justify-between text-[10px] font-mono text-zinc-400">
          <span>Durabilidad:</span>
          <span className="text-emerald-400 font-bold">SQLite WAL (Zero Data Loss)</span>
        </div>
      </div>
    </aside>
  )
}
