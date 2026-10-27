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
          <span
            role="status"
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] sm:text-xs font-mono font-bold bg-white text-black font-bold shadow-sm"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-black animate-ping" />
            RUNNING (PID {processes.find((p) => p.state === 'RUNNING')?.pid || 'EXEC'})
          </span>
        )
      case 'COMPLETED':
        return (
          <span
            role="status"
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] sm:text-xs font-mono font-bold bg-zinc-900 text-zinc-200 border border-zinc-700"
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-zinc-200" />
            COMPLETED (Exit 0)
          </span>
        )
      case 'BLOCKED_ON_GATE':
        return (
          <span
            role="status"
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] sm:text-xs font-mono font-bold bg-amber-500/15 text-zinc-300 border border-amber-500/30"
          >
            <ShieldAlert className="w-3.5 h-3.5 text-zinc-300" />
            WAITING_GATE (HMAC)
          </span>
        )
      case 'FAILED':
        return (
          <span
            role="status"
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] sm:text-xs font-mono font-bold bg-red-500/15 text-red-400 border border-red-500/30"
          >
            <AlertCircle className="w-3.5 h-3.5 text-red-400" />
            FAILED (Exit 1)
          </span>
        )
      default:
        return (
          <span
            role="status"
            className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] sm:text-xs font-mono font-medium bg-zinc-800/80 text-zinc-400 border border-zinc-700/60"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-zinc-500" />
            IDLE (Zero-Token)
          </span>
        )
    }
  }

  const getAgentIcon = (id: string) => {
    if (id.includes('AGY')) return <Radio className="w-4 h-4 text-zinc-200" />
    if (id.includes('GOV')) return <ShieldAlert className="w-4 h-4 text-zinc-300" />
    if (id.includes('QA')) return <CheckCircle2 className="w-4 h-4 text-zinc-300" />
    return <Terminal className="w-4 h-4 text-zinc-400" />
  }

  return (
    <section
      aria-label="Supervisión de Procesos de la Flota de Agentes"
      className="rounded-2xl sm:rounded-3xl bg-zinc-950 border border-zinc-800 p-4 sm:p-6 space-y-4 shadow-xl"
    >
      {/* Header with high visual hierarchy */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl sm:rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-zinc-200 shrink-0">
            <Cpu className="w-4 h-4 sm:w-5 sm:h-5" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-sm sm:text-base font-bold text-white tracking-wide">
                Flota de Agentes & Procesos en Tiempo Real
              </h2>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-zinc-200 border border-emerald-500/25 font-semibold">
                {processes.length} Agentes Registrados
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              Supervisión de subprocesos locales, PID, aislamiento en worktrees y telemetría de ejecución.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono text-zinc-400 shrink-0">
          <span className="flex items-center gap-1.5 bg-black/40 px-2.5 py-1 rounded-lg border border-white/5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Supervisión: <strong className="text-white">Graph-P Local</strong>
          </span>
        </div>
      </div>

      {/* 1. DESKTOP / TABLET: HIGH-DENSITY PROCESS TABLE (>= 768px) */}
      <div className="hidden md:block overflow-x-auto custom-scroll">
        <table className="w-full text-left text-xs font-mono">
          <thead>
            <tr className="border-b border-zinc-800 text-[11px] text-zinc-400 font-semibold">
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
                    <div className="flex items-center gap-2.5">
                      <div className="w-7 h-7 rounded-lg bg-black/60 border border-white/5 flex items-center justify-center text-zinc-300 shrink-0">
                        {getAgentIcon(proc.id)}
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
                    <span className="px-2 py-0.5 rounded-md bg-black/40 border border-white/5 text-[11px] font-mono text-zinc-300 font-semibold">
                      {proc.pid ? `PID:${proc.pid}` : 'STANDBY'}
                    </span>
                  </td>

                  {/* Worktree */}
                  <td className="py-3">
                    <div className="flex items-center gap-1.5 text-zinc-400 text-[11px]" title={proc.worktree}>
                      <FolderGit2 className="w-3 h-3 text-zinc-200 shrink-0" />
                      <span className="truncate max-w-[140px]">{proc.worktree}</span>
                    </div>
                  </td>

                  {/* Last Command */}
                  <td className="py-3">
                    <div
                      className="max-w-[220px] truncate text-zinc-400 text-[11px] font-mono bg-black/30 px-2 py-1 rounded border border-white/5"
                      title={proc.lastCommand}
                    >
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
                      type="button"
                      onClick={() => onExecuteAgent?.(proc.id)}
                      disabled={isBusy}
                      className="px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 hover:border-emerald-500/40 text-zinc-300 hover:text-white text-xs font-mono transition cursor-pointer disabled:opacity-40"
                      title={`Despachar agente ${proc.name}`}
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

      {/* 2. MOBILE: RESPONSIVE TOUCH-FRIENDLY CARD VIEW (< 768px) */}
      <div className="block md:hidden space-y-3">
        {processes.map((proc) => {
          const isBusy = executingId === proc.id || proc.state === 'RUNNING'

          return (
            <div
              key={proc.id}
              className={`p-3.5 rounded-xl bg-[#080d14] border border-zinc-800 space-y-2.5 transition ${
                isBusy ? 'border-blue-500/40 bg-blue-500/[0.04]' : 'hover:border-zinc-700'
              }`}
            >
              {/* Top Row: Icon + Name + Badge */}
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-black/60 border border-white/5 flex items-center justify-center text-zinc-300 shrink-0">
                    {getAgentIcon(proc.id)}
                  </div>
                  <div>
                    <span className="font-bold text-white text-xs block">{proc.name}</span>
                    <span className="text-[10px] text-zinc-500 font-mono">{proc.id}</span>
                  </div>
                </div>
                {getStateBadge(proc.state)}
              </div>

              {/* Middle Row: Role Description */}
              <p className="text-xs text-zinc-300 font-sans leading-relaxed">
                {proc.role}
              </p>

              {/* Telemetry Chips: PID & Worktree */}
              <div className="flex flex-wrap items-center gap-2 text-[11px] font-mono">
                <span className="px-2 py-0.5 rounded bg-black/50 border border-white/10 text-zinc-200 font-bold">
                  {proc.pid ? `PID:${proc.pid}` : 'STANDBY'}
                </span>
                <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-black/50 border border-white/10 text-zinc-300 truncate max-w-[200px]">
                  <FolderGit2 className="w-3 h-3 text-zinc-200 shrink-0" />
                  <span className="truncate">{proc.worktree}</span>
                </span>
              </div>

              {/* Command Preview */}
              <div
                className="text-[10px] font-mono text-zinc-400 bg-black/40 px-2.5 py-1.5 rounded-lg border border-white/5 truncate"
                title={proc.lastCommand}
              >
                <code>{proc.lastCommand}</code>
              </div>

              {/* Action Button: Touch target minimum >= 44px (Fitts's Law) */}
              <div className="pt-1">
                <button
                  type="button"
                  onClick={() => onExecuteAgent?.(proc.id)}
                  disabled={isBusy}
                  className="w-full min-h-[44px] px-4 py-2.5 rounded-xl bg-zinc-900 border border-zinc-700 hover:border-emerald-500/50 text-white font-bold text-xs flex items-center justify-center gap-2 transition cursor-pointer disabled:opacity-40 active:scale-[0.99]"
                >
                  <Play className="w-3.5 h-3.5 fill-white text-white" />
                  <span>{isBusy ? 'Ejecutando proceso en OS...' : `Despachar ${proc.name}`}</span>
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
