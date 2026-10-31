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

  return (
    <div
      onClick={onInspect}
      className="bg-[#0a0a0a] border border-white/8 rounded p-3 flex flex-col justify-between hover:border-white/20 transition cursor-pointer select-none"
    >
      {/* Top Identity Header */}
      <div>
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            {/* Semantic SVG Status Indicator */}
            <div className={`w-2 h-2 rounded-full shrink-0 ${isHealthy ? 'bg-emerald-400' : isWaiting ? 'bg-amber-400 animate-pulse' : 'bg-red-400'}`} />
            <span className="text-xs font-semibold text-white truncate font-sans">{agent.agentName}</span>
          </div>

          <span className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border uppercase tracking-wider shrink-0 ${statusBadgeClass}`}>
            {agent.status}
          </span>
        </div>

        <div className="text-[10px] text-zinc-500 font-mono mt-1 truncate">
          {agent.role}
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

      {/* Bottom Metadata: PID / Commit / Latency */}
      <div className="flex items-center justify-between text-[9px] font-mono text-zinc-500 pt-1 border-t border-white/8">
        <span>PID: {agent.pid ? agent.pid : 'DAEMON'}</span>
        {agent.commitSha && (
          <span className="text-zinc-400">git: {agent.commitSha.substring(0, 7)}</span>
        )}
        <span>{agent.lastActive || 'Activo'}</span>
      </div>
    </div>
  )
})
