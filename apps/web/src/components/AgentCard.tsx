import React from 'react'

export interface AgentCardData {
  agentName: string
  role: string
  currentProcess: string
  status: 'RUNNING' | 'COMPLETED' | 'PASS' | 'WAITING_APPROVAL' | 'BLOCKED' | 'ERROR' | 'FAILED' | string
  lastLog?: string
  pid?: number
  commitSha?: string
  lastActive?: string
  latencyMs?: number
  syncStatus?: string
  memoryMb?: number
}

interface AgentCardProps {
  agent: AgentCardData
  onInspect?: () => void
}

export const AgentCard: React.FC<AgentCardProps> = React.memo(({ agent, onInspect }) => {
  const isHealthy = ['RUNNING', 'COMPLETED', 'PASS', 'Activo'].includes(agent.status)
  const isWaiting = ['WAITING_APPROVAL', 'BLOCKED', 'HUMAN_IN_THE_LOOP', 'En espera'].includes(agent.status)
  const isError = ['ERROR', 'FAILED', 'FAIL'].includes(agent.status)

  const statusBadgeClass = isHealthy
    ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
    : isWaiting
    ? 'text-amber-400 bg-amber-500/10 border-amber-500/20'
    : 'text-red-400 bg-red-500/10 border-red-500/20'

  // Iconografía de rol canónica
  const getRoleIcon = () => {
    const name = agent.agentName.toLowerCase()
    if (name.includes('atlas')) {
      return (
        <svg className="w-3.5 h-3.5 text-blue-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" />
          <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20" />
          <path d="M2 12h20" />
        </svg>
      )
    }
    if (name.includes('vega')) {
      return (
        <svg className="w-3.5 h-3.5 text-purple-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <ellipse cx="12" cy="5" rx="9" ry="3" />
          <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
          <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
        </svg>
      )
    }
    if (name.includes('nova')) {
      return (
        <svg className="w-3.5 h-3.5 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
          <path d="m9 12 2 2 4-4" />
        </svg>
      )
    }
    return (
      <svg className="w-3.5 h-3.5 text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 2v20M2 12h20" />
      </svg>
    )
  }

  return (
    <div
      onClick={onInspect}
      className="bg-[#0a0a0a] border border-white/8 rounded p-3 flex flex-col justify-between hover:border-white/20 transition cursor-pointer select-none"
    >
      {/* Top Identity Header */}
      <div>
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            <div className="p-1 rounded bg-[#121212] border border-white/8 shrink-0">
              {getRoleIcon()}
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-semibold text-white truncate font-sans">{agent.agentName}</span>
                <div className={`w-1.5 h-1.5 rounded-full shrink-0 ${isHealthy ? 'bg-emerald-400' : isWaiting ? 'bg-amber-400 animate-pulse' : 'bg-red-400'}`} />
              </div>
              <div className="text-[10px] text-zinc-500 font-mono truncate">
                {agent.role}
              </div>
            </div>
          </div>

          <span className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border uppercase tracking-wider shrink-0 ${statusBadgeClass}`}>
            {agent.status}
          </span>
        </div>
      </div>

      {/* Middle: Active Task / Process */}
      <div className="my-2.5 py-1.5 px-2 bg-[#000000] border border-white/8 rounded">
        <div className="text-[10px] text-zinc-400 font-sans truncate">
          {agent.currentProcess || 'En espera de despacho DAG'}
        </div>
        {agent.lastLog && (
          <div className="text-[9px] text-zinc-500 font-mono mt-1 truncate">
            &gt; {agent.lastLog}
          </div>
        )}
      </div>

      {/* Telemetry Strip (Latency Sparkline & Memory) */}
      <div className="mb-2 px-1.5 py-1 bg-[#121212]/50 rounded flex items-center justify-between text-[9px] font-mono text-zinc-400">
        <span className="flex items-center gap-1">
          <span className="text-zinc-600">RTT:</span>
          <span className="text-emerald-400">{agent.latencyMs ? `${agent.latencyMs.toFixed(1)}ms` : '<15ms'}</span>
        </span>
        <span className="flex items-center gap-1">
          <span className="text-zinc-600">Sync:</span>
          <span className="text-zinc-300">{agent.syncStatus || '100% OK'}</span>
        </span>
        <span className="text-zinc-500">
          {agent.memoryMb ? `${agent.memoryMb}MB` : 'WAL'}
        </span>
      </div>

      {/* Bottom Metadata: PID / Commit */}
      <div className="flex items-center justify-between text-[9px] font-mono text-zinc-500 pt-1 border-t border-white/8">
        <span>PID: {agent.pid ? agent.pid : 'DAEMON'}</span>
        {agent.commitSha && (
          <span className="text-zinc-400">git: {agent.commitSha.substring(0, 7)}</span>
        )}
        <span className="text-zinc-600">O(1) memo</span>
      </div>
    </div>
  )
})
