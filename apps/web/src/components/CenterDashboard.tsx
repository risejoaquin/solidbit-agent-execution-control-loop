import React, { useState, useEffect } from 'react'
import {
  AlertTriangle,
  RotateCcw,
  Loader2,
  FolderGit2,
  ArrowRight,
} from 'lucide-react'
import type {
  TaskItem,
  AgentItem,
  CommitItem,
  Project,
  ActivityEvent,
} from '../types/orchestrator'
import type { TechnologyItem } from './ConnectedTechnologiesMatrix'
import type { DomainStateMeta } from '../types/domainState'
import { TooltipProvider } from './ui/tooltip'
import { OrchestratorFlow } from './OrchestratorFlow'

interface CenterDashboardProps {
  domainState: DomainStateMeta
  tasks: TaskItem[]
  agents: AgentItem[]
  connections?: TechnologyItem[]
  onRefreshConnections?: () => void
  commits: CommitItem[]
  projects: Project[]
  events?: ActivityEvent[]
  onOpenSprintModal: () => void
  onNavigateSection: (section: string) => void
  pendingGatesCount?: number
  onConflictStateChange?: (hasConflict: boolean, reason?: string | null) => void
  onExecutingStateChange?: (isExecuting: boolean) => void
  onGateResolved?: () => void
}

export const CenterDashboard: React.FC<CenterDashboardProps> = ({
  domainState,
  tasks,
  agents,
  onRefreshConnections,
  commits,
  projects,
  onNavigateSection,
  onConflictStateChange,
  onExecutingStateChange,
  onGateResolved,
}) => {
  const [runningHealthCheck, setRunningHealthCheck] = useState<boolean>(false)

  const activeProject =
    projects.find((p) => p.is_active) ||
    projects[0]

  // Notify parent of state changes
  useEffect(() => {
    if (onConflictStateChange) {
      const isConflict = domainState.state === 'HALTED_BY_CONFLICT'
      onConflictStateChange(isConflict, domainState.subtitle)
    }
    if (onExecutingStateChange) {
      const isExec = domainState.state === 'EXECUTING' || agents.length > 0
      onExecutingStateChange(isExec)
    }
  }, [domainState.state, domainState.subtitle, agents.length, onConflictStateChange, onExecutingStateChange])

  // Resolve conflict / unblock
  const handleResolveConflict = async () => {
    setRunningHealthCheck(true)
    try {
      const res = await fetch('/api/actions/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'revert_fsm',
          params: { fix: true, note: 'Resolución de contención preventiva desde el dashboard KISS' },
        }),
      })
      const data = await res.json()
      if (res.ok && data.success) {
        if (onGateResolved) onGateResolved()
      }
    } catch (e) {
      console.warn('Error resolviendo contención:', e)
    } finally {
      setRunningHealthCheck(false)
    }
  }

  return (
    <TooltipProvider>
      <div className="space-y-6 animate-fade-in pb-8">
        {/* Banner de Resolución Inmediata si el sistema está detenido por conflicto */}
        {domainState.state === 'HALTED_BY_CONFLICT' && (
          <div className="p-5 rounded-2xl bg-rose-950/30 border border-rose-500/40 space-y-4 shadow-xl">
            <div className="flex items-start gap-3.5">
              <div className="w-10 h-10 rounded-xl bg-rose-500/20 border border-rose-500/30 flex items-center justify-center text-rose-400 shrink-0">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div className="space-y-1">
                <span className="text-[10px] font-mono uppercase tracking-wider text-rose-300 font-bold">
                  Protección Preventiva Activada
                </span>
                <h1 className="text-base font-bold text-white">{domainState.title}</h1>
                <p className="text-xs text-zinc-300 leading-relaxed">
                  {domainState.subtitle || 'Se detectaron cambios que requieren sincronización antes de continuar.'}
                </p>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-2 border-t border-rose-500/20">
              <button
                type="button"
                onClick={handleResolveConflict}
                disabled={runningHealthCheck}
                className="px-4 py-2 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-extrabold flex items-center gap-2 transition cursor-pointer shadow-sm disabled:opacity-50"
              >
                {runningHealthCheck ? (
                  <Loader2 className="w-4 h-4 animate-spin text-black" />
                ) : (
                  <RotateCcw className="w-4 h-4 text-black" />
                )}
                <span>Restaurar Entorno Seguro</span>
              </button>
            </div>
          </div>
        )}

        {/* Banner si el estado es UNINITIALIZED */}
        {domainState.state === 'UNINITIALIZED' && (
          <div className="p-6 rounded-2xl bg-zinc-950 border border-white/10 space-y-4 shadow-xl">
            <div className="flex items-start gap-3.5">
              <div className="w-10 h-10 rounded-xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-400 shrink-0">
                <FolderGit2 className="w-5 h-5" />
              </div>
              <div className="space-y-1">
                <h1 className="text-base font-bold text-white">{domainState.title}</h1>
                <p className="text-xs text-zinc-300">{domainState.subtitle}</p>
              </div>
            </div>
            <div className="flex items-center justify-end">
              <button
                type="button"
                onClick={() => onNavigateSection('projects')}
                className="px-4 py-2 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-extrabold flex items-center gap-2 transition cursor-pointer"
              >
                <FolderGit2 className="w-4 h-4 text-black" />
                <span>Vincular un Proyecto para Iniciar</span>
                <ArrowRight className="w-4 h-4 text-black" />
              </button>
            </div>
          </div>
        )}

        {/* Flujo KISS Central de 3 Fases (Robot Flow Diagram + Interactive Card) */}
        <OrchestratorFlow
          activeProject={activeProject}
          activeBranch={activeProject?.branch || 'worktrees/scheduler'}
          commits={commits}
          tasks={tasks}
          agents={agents}
          isBlocked={domainState.state === 'HALTED_BY_CONFLICT' || domainState.state === 'POST_CONDITION_FAILED'}
          blockReason={domainState.subtitle}
          onRefreshAll={onRefreshConnections}
          onNavigateSection={onNavigateSection}
          onGateResolved={onGateResolved}
        />
      </div>
    </TooltipProvider>
  )
}
