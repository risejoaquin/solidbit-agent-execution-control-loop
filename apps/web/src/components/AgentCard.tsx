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
  skin?: string
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

  // Mapeo determinístico de Sprite Bomberman por Agente
  const getBombermanSprite = () => {
    const name = agent.agentName.toLowerCase()
    if (name.includes('atlas')) {
      return {
        src: '/assets/sprites/bomberman/atlas_white_idle.png',
        cheerSrc: '/assets/sprites/bomberman/atlas_white_cheering.png',
        label: 'White Bomberman',
        border: 'border-blue-500/30 bg-blue-500/10',
      }
    }
    if (name.includes('vega')) {
      return {
        src: '/assets/sprites/bomberman/vega_blue_idle.png',
        cheerSrc: '/assets/sprites/bomberman/vega_blue_cheering.png',
        label: 'Blue Bomberman',
        border: 'border-purple-500/30 bg-purple-500/10',
      }
    }
    if (name.includes('nova')) {
      return {
        src: '/assets/sprites/bomberman/nova_red_idle.png',
        cheerSrc: '/assets/sprites/bomberman/nova_red_cheering.png',
        label: 'Red Bomberman',
        border: 'border-emerald-500/30 bg-emerald-500/10',
      }
    }
    return {
      src: '/assets/sprites/bomberman/centinela_black_idle.png',
      cheerSrc: '/assets/sprites/bomberman/centinela_black_cheering.png',
      label: 'Black Bomberman',
      border: 'border-amber-500/30 bg-amber-500/10',
    }
  }

  const sprite = getBombermanSprite()
  const displaySprite = agent.skin === 'bomberman_cheering' ? sprite.cheerSrc : sprite.src

  return (
    <div
      onClick={onInspect}
      className="bg-[#0a0a0a] border border-white/8 rounded p-3 flex flex-col justify-between hover:border-white/20 transition cursor-pointer select-none group"
    >
      {/* Top Identity Header */}
      <div>
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2.5 min-w-0">
            {/* Bomberman Avatar Sprite Container */}
            <div
              className={`w-9 h-9 rounded border flex items-center justify-center p-1 shrink-0 bg-[#000000] relative group-hover:scale-105 transition-transform ${sprite.border}`}
              title={sprite.label}
            >
              <img
                src={displaySprite}
                alt={agent.agentName}
                className="w-7 h-7 object-contain [image-rendering:pixelated]"
                loading="lazy"
              />
              <span className="absolute -bottom-1 -right-1 w-2 h-2 rounded-full bg-emerald-400 border border-black" />
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
        <span className="text-zinc-600">16-bit Skin</span>
      </div>
    </div>
  )
})
