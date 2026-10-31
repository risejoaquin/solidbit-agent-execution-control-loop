import React, { useState, useEffect, useRef, useMemo } from 'react'

export interface LogEntry {
  id: string
  timestamp: string
  level: 'INFO' | 'WARN' | 'ERROR' | 'FSM' | 'DAEMON'
  source: string
  message: string
}

interface GlobalLiveLogsTerminalProps {
  maxLines?: number
}

export const GlobalLiveLogsTerminal: React.FC<GlobalLiveLogsTerminalProps> = ({
  maxLines = 150,
}) => {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [filterLevel, setFilterLevel] = useState<'ALL' | 'INFO' | 'WARN' | 'ERROR' | 'FSM' | 'DAEMON'>('ALL')
  const [isPaused, setIsPaused] = useState<boolean>(false)
  const [autoScroll, setAutoScroll] = useState<boolean>(true)
  const [copied, setCopied] = useState<boolean>(false)
  const terminalEndRef = useRef<HTMLDivElement>(null)

  // Ingesta de telemetría en tiempo real desde el SSE unificado del EOP
  useEffect(() => {
    const sse = new EventSource('/api/events')

    const appendLog = (entry: Omit<LogEntry, 'id'>) => {
      if (isPaused) return
      setLogs((prev) => {
        const next = [
          ...prev,
          {
            ...entry,
            id: `log-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`,
          },
        ]
        return next.length > maxLines ? next.slice(next.length - maxLines) : next
      })
    }

    // Inicial con log de conexión
    appendLog({
      timestamp: new Date().toLocaleTimeString(),
      level: 'DAEMON',
      source: 'SACL_ENGINE',
      message: 'Terminal de observabilidad en vivo enlazado a /api/events (SSE Stream Activo).',
    })

    const handleTaskEvent = (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data)
        appendLog({
          timestamp: new Date().toLocaleTimeString(),
          level: 'FSM',
          source: data.agent || 'WorkflowEngine',
          message: data.task || data.message || 'Transición de estado FSM registrada.',
        })
      } catch {}
    }

    const handleHeartbeat = (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data)
        appendLog({
          timestamp: new Date().toLocaleTimeString(),
          level: 'DAEMON',
          source: data.agent_id || 'Heartbeat',
          message: `Heartbeat grabado en SQLite WAL: ${data.current_task || 'Idle / Supervisión'}`,
        })
      } catch {}
    }

    const handleGenericMessage = (e: MessageEvent) => {
      try {
        const data = JSON.parse(e.data)
        appendLog({
          timestamp: new Date().toLocaleTimeString(),
          level: data.level?.toUpperCase() === 'ERROR' ? 'ERROR' : 'INFO',
          source: data.source || 'Orchestrator',
          message: typeof data === 'string' ? data : data.message || JSON.stringify(data),
        })
      } catch {}
    }

    sse.addEventListener('task_running', handleTaskEvent)
    sse.addEventListener('heartbeat_recorded', handleHeartbeat)
    sse.addEventListener('agent_heartbeat', handleHeartbeat)
    sse.addEventListener('message', handleGenericMessage)

    return () => {
      sse.removeEventListener('task_running', handleTaskEvent)
      sse.removeEventListener('heartbeat_recorded', handleHeartbeat)
      sse.removeEventListener('agent_heartbeat', handleHeartbeat)
      sse.removeEventListener('message', handleGenericMessage)
      sse.close()
    }
  }, [isPaused, maxLines])

  // Auto-scroll reactivo
  useEffect(() => {
    if (autoScroll && terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs, autoScroll])

  // Filtrado de logs O(1) con useMemo
  const filteredLogs = useMemo(() => {
    if (filterLevel === 'ALL') return logs
    return logs.filter((log) => log.level === filterLevel)
  }, [logs, filterLevel])

  const handleCopyLogs = () => {
    const text = filteredLogs
      .map((l) => `[${l.timestamp}] [${l.level}] [${l.source}] ${l.message}`)
      .join('\n')
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const getLevelBadgeClass = (lvl: LogEntry['level']) => {
    switch (lvl) {
      case 'ERROR':
        return 'text-red-400 bg-red-500/10 border-red-500/30'
      case 'WARN':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/30'
      case 'FSM':
        return 'text-purple-400 bg-purple-500/10 border-purple-500/30'
      case 'DAEMON':
        return 'text-blue-400 bg-blue-500/10 border-blue-500/30'
      default:
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
    }
  }

  return (
    <div className="bg-[#0a0a0a] border border-white/8 rounded-lg flex flex-col h-[480px] overflow-hidden select-none text-left">
      {/* Terminal Toolbar */}
      <div className="h-11 px-3 bg-[#000000] border-b border-white/8 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-mono font-semibold text-white uppercase tracking-wider">
            Live Logs Terminal
          </span>
          <span className="text-[10px] font-mono text-zinc-500">
            ({filteredLogs.length} eventos)
          </span>
        </div>

        {/* Filters and Actions */}
        <div className="flex items-center gap-1.5">
          {/* Level Filters */}
          <div className="flex rounded border border-white/8 overflow-hidden text-[9px] font-mono">
            {(['ALL', 'FSM', 'DAEMON', 'INFO', 'ERROR'] as const).map((lvl) => (
              <button
                key={lvl}
                onClick={() => setFilterLevel(lvl)}
                className={`px-2 py-0.5 transition cursor-pointer ${
                  filterLevel === lvl
                    ? 'bg-zinc-800 text-white font-bold'
                    : 'text-zinc-500 hover:text-zinc-300'
                }`}
              >
                {lvl}
              </button>
            ))}
          </div>

          {/* Pause / Resume */}
          <button
            onClick={() => setIsPaused(!isPaused)}
            className={`px-2 py-0.5 rounded border text-[9px] font-mono transition cursor-pointer ${
              isPaused
                ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                : 'border-white/8 text-zinc-400 hover:text-white'
            }`}
          >
            {isPaused ? '▶ Reanudar' : '⏸ Pausar'}
          </button>

          {/* Auto-scroll toggle */}
          <button
            onClick={() => setAutoScroll(!autoScroll)}
            className={`px-2 py-0.5 rounded border text-[9px] font-mono transition cursor-pointer ${
              autoScroll
                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                : 'border-white/8 text-zinc-500'
            }`}
            title="Auto-scroll anclado al último log"
          >
            AutoScroll
          </button>

          {/* Copy Button */}
          <button
            onClick={handleCopyLogs}
            className="px-2 py-0.5 rounded border border-white/8 text-[9px] font-mono text-zinc-400 hover:text-white transition cursor-pointer"
          >
            {copied ? '✓ Copiado' : 'Copiar'}
          </button>

          {/* Clear Button */}
          <button
            onClick={() => setLogs([])}
            className="px-2 py-0.5 rounded border border-white/8 text-[9px] font-mono text-zinc-500 hover:text-red-400 transition cursor-pointer"
          >
            Limpiar
          </button>
        </div>
      </div>

      {/* Terminal Viewport */}
      <div className="flex-1 bg-[#000000] p-3 overflow-y-auto font-mono text-xs custom-scroll space-y-1">
        {filteredLogs.length === 0 ? (
          <div className="h-full flex items-center justify-center text-zinc-600 text-xs font-mono">
            Esperando eventos SSE de antigravity daemon...
          </div>
        ) : (
          filteredLogs.map((log) => (
            <div
              key={log.id}
              className="flex items-start gap-2 hover:bg-white/[0.02] py-0.5 px-1 rounded transition"
            >
              <span className="text-[10px] text-zinc-600 shrink-0 select-none">
                {log.timestamp}
              </span>
              <span
                className={`text-[8px] font-bold px-1 rounded border uppercase tracking-wider shrink-0 ${getLevelBadgeClass(
                  log.level
                )}`}
              >
                {log.level}
              </span>
              <span className="text-[10px] text-zinc-500 shrink-0 truncate max-w-[120px]">
                [{log.source}]
              </span>
              <span
                className={`text-xs break-all ${
                  log.level === 'ERROR'
                    ? 'text-red-300'
                    : log.level === 'FSM'
                    ? 'text-purple-300'
                    : 'text-zinc-300'
                }`}
              >
                {log.message}
              </span>
            </div>
          ))
        )}
        <div ref={terminalEndRef} />
      </div>

      {/* Terminal Footer Info */}
      <div className="h-6 px-3 bg-[#0a0a0a] border-t border-white/8 flex items-center justify-between text-[9px] font-mono text-zinc-600 shrink-0">
        <span>Canal: SSE /api/events</span>
        <span>Buffer O(1): {filteredLogs.length}/{maxLines}</span>
        <span>Daemon Port: 8765</span>
      </div>
    </div>
  )
}
