import React from 'react'
import {
  Cpu,
  Terminal,
  ShieldAlert,
  CheckCircle2,
  AlertCircle,
  Play,
  RotateCw,
  Activity,
  FolderGit2,
  Radio,
  FileCode,
  Layers,
} from 'lucide-react'
import type { AgentProcess } from '../types/orchestrator'

interface AgentFleetProcessTableProps {
  processes: AgentProcess[]
  onExecuteAgent?: (agentId: string) => void
  onSelectAgentLogs?: (agentId: string) => void
  executingId?: string | null
}

export const AgentFleetProcessTable: React.FC<AgentFleetProcessTableProps> = ({
  processes,
  onExecuteAgent,
  onSelectAgentLogs,
  executingId,
}) => {
  const getStateBadge = (state: AgentProcess['state']) => {
    switch (state) {
      case 'RUNNING':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-blue-500/15 text-blue-400 border border-blue-500/30 animate-pulse">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-ping" />
            RUNNING (PID {processes.find(p => p.state === 'RUNNING')?.pid || 'EXEC'})
          </span>
        )
      case 'COMPLETED':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            COMPLETED (Exit 0)
          </span>
        )
      case 'BLOCKED_ON_GATE':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-amber-500/15 text-amber-400 border border-amber-500/30">
            <ShieldAlert className="w-3 h-3 text-amber-400" />
            WAITING_GATE (HMAC)
          </span>
        )
      case 'FAILED':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-red-500/15 text-red-400 border border-red-500/30">
            <AlertCircle className="w-3 h-3 text-red-400" />
            FAILED (Exit 1)
          </span>
        )
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono font-medium bg-zinc-800/80 text-zinc-400 border border-zinc-700/60">
            <span className="w-1.5 h-1.5 rounded-full bg-zinc-500" />
            IDLE (Zero-Token)
          </span>
        )
    }
  }

  return (
    <div className="rounded-2xl sm:rounded-3xl bg-[#0c121a] border border-[#1b2533] p-4 sm:p-6 space-y-4 shadow-xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1b2533] pb-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 shrink-0">
            <Cpu className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm sm:text-base font-bold text-white tracking-wide">
                Flota de Agentes & Procesos en Tiempo Real
              </h2>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/25">
                {processes.length} Agentes Registrados
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              Supervisión de subprocesos locales, PID, aislamiento en worktrees y telemetría de ejecución.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono text-zinc-400">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Supervisión: <strong className="text-white">Graph-P Local</strong>
          </span>
        </div>
      </div>

      {/* Process Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead>
            <tr className="border-b border-[#1b2533] text-[11px] text-zinc-400 font-semibold">
              <th className="pb-3 pl-2">Agente / Identificador</th>
              <th className="pb-3">Rol SDLC</th>
              <th className="pb-3">PID / OS</th>
              <th className="pb-3">Worktree Aislado</th>
              <th className="pb-3">Comando / Tarea</th>
              <th className="pb-3">Estado</th>
              <th className="pb-3 text-right pr-2">Acción</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1b2533]/50">
            {processes.map((proc) => {
              const isBusy = executingId === proc.id || proc.state === 'RUNNING'

              return (
                <tr
                  key={proc.id}
                  className={`hover:bg-white/[0.02] transition ${
                    isBusy ? 'bg-blue-500/[0.04]' : ''
                  }`}
                >
                  {/* ID & Name */}
                  <td className="py-3 pl-2">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 rounded-lg bg-black/60 border border-white/5 flex items-center justify-center text-zinc-300">
                        {proc.id.includes('AGY') ? (
                          <Radio className="w-3.5 h-3.5 text-emerald-400" />
                        ) : proc.id.includes('GOV') ? (
                          <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
                        ) : proc.id.includes('QA') ? (
                          <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" />
                        ) : (
                          <Terminal className="w-3.5 h-3.5 text-zinc-400" />
                        )}
                      </div>
                      <div>
                        <span className="font-bold text-white block">{proc.name}</span>
                        <span className="text-[10px] text-zinc-500 font-mono">{proc.id}</span>
                      </div>
                    </div>
                  </td>

                  {/* Role */}
                  <td className="py-3 text-zinc-300 font-sans text-xs">
                    {proc.role}
                  </td>

                  {/* PID */}
                  <td className="py-3">
                    <span className="px-2 py-0.5 rounded-md bg-black/40 border border-white/5 text-[11px] font-mono text-zinc-300">
                      {proc.pid ? `PID:${proc.pid}` : 'STANDBY'}
                    </span>
                  </td>

                  {/* Worktree */}
                  <td className="py-3">
                    <div className="flex items-center gap-1.5 text-zinc-400 text-[11px]" title={proc.worktree}>
                      <FolderGit2 className="w-3 h-3 text-emerald-400 shrink-0" />
                      <span className="truncate max-w-[120px]">{proc.worktree}</span>
                    </div>
                  </td>

                  {/* Last Command */}
                  <td className="py-3">
                    <div className="max-w-[220px] truncate text-zinc-400 text-[11px] font-mono bg-black/30 px-2 py-1 rounded border border-white/5" title={proc.lastCommand}>
                      {proc.lastCommand}
                    </div>
                  </td>

                  {/* State */}
                  <td className="py-3">
                    {getStateBadge(proc.state)}
                  </td>

                  {/* Action */}
                  <td className="py-3 text-right pr-2">
                    <button
                      onClick={() => onExecuteAgent?.(proc.id)}
                      disabled={isBusy}
                      className="px-2.5 py-1 rounded-lg bg-zinc-900 border border-zinc-800 hover:border-emerald-500/40 text-zinc-300 hover:text-white text-[11px] font-mono transition cursor-pointer disabled:opacity-40"
                      title="Despachar agente"
                    >
                      {isBusy ? 'Corriendo...' : 'Despachar'}
                    </button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
