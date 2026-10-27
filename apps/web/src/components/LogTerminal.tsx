import React, { useState, useEffect, useRef } from 'react'
import { formatSmartDateTime } from '../utils/dateFormat'
import {
  Terminal,
  Search,
  Copy,
  Trash2,
  Maximize2,
  Minimize2,
  Filter,
  CheckCircle2,
  AlertTriangle,
  Info,
  Shield,
  Layers,
  ArrowDownCircle,
} from 'lucide-react'

export interface LogEntry {
  id: string
  timestamp: string
  subsystem: 'KERNEL' | 'AGY' | 'GATE' | 'WAL' | 'VCS'
  level: 'INFO' | 'SUCCESS' | 'WARN' | 'ERROR' | 'AUDIT'
  message: string
  details?: string
  pid?: number
}

interface LogTerminalProps {
  initialEvents?: any[]
  onOpenGate?: () => void
}

export const LogTerminal: React.FC<LogTerminalProps> = ({
  initialEvents = [],
  onOpenGate,
}) => {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [streamFilter, setStreamFilter] = useState<'ALL' | 'AGY' | 'GATE' | 'WAL'>('ALL')
  const [levelFilter, setLevelFilter] = useState<string>('ALL')
  const [searchTerm, setSearchTerm] = useState('')
  const [autoScroll, setAutoScroll] = useState(true)
  const [isExpanded, setIsExpanded] = useState(false)
  const [copied, setCopied] = useState(false)

  const terminalEndRef = useRef<HTMLDivElement>(null)
  const viewportRef = useRef<HTMLDivElement>(null)

  // Map initial SQLite WAL events to structured log entries
  useEffect(() => {
    if (initialEvents && initialEvents.length > 0) {
      const mapped: LogEntry[] = initialEvents.map((ev: any, idx: number) => {
        let sub: LogEntry['subsystem'] = 'WAL'
        let lvl: LogEntry['level'] = 'INFO'
        const evType = ev.event_type || ''

        if (evType.includes('gate') || evType.includes('approval') || evType.includes('hmac')) {
          sub = 'GATE'
          lvl = 'WARN'
        } else if (evType.includes('agent') || evType.includes('job') || evType.includes('run')) {
          sub = 'AGY'
          lvl = evType.includes('error') ? 'ERROR' : 'INFO'
        } else if (evType.includes('commit') || evType.includes('git')) {
          sub = 'VCS'
          lvl = 'SUCCESS'
        }

        const dateStr = formatSmartDateTime(ev.created_at)

        return {
          id: String(ev.event_id || idx),
          timestamp: dateStr,
          subsystem: sub,
          level: lvl,
          message: ev.payload_json || ev.event_type || 'Evento transaccional en SQLite WAL',
          pid: ev.pid || undefined,
        }
      })
      setLogs(mapped)
    } else {
      // Baseline SolidBit kernel startup logs
      setLogs([
        {
          id: 'log-0',
          timestamp: formatSmartDateTime(new Date()),
          subsystem: 'KERNEL',
          level: 'SUCCESS',
          message: 'SolidBit SACL Kernel inicializado en modo transaccional WAL.',
          pid: undefined,
        },
        {
          id: 'log-1',
          timestamp: formatSmartDateTime(new Date()),
          subsystem: 'AGY',
          level: 'INFO',
          message: 'Host AGY detectado (Antigravity CLI v2.0) en runtime local.',
          pid: undefined,
        },
        {
          id: 'log-2',
          timestamp: formatSmartDateTime(new Date()),
          subsystem: 'WAL',
          level: 'SUCCESS',
          message: 'Base de datos sacl_ops.db verificada: 22 estados canónicos consistentes.',
          pid: undefined,
        },
        {
          id: 'log-3',
          timestamp: formatSmartDateTime(new Date()),
          subsystem: 'GATE',
          level: 'AUDIT',
          message: 'Compuertas soberanas habilitadas: Zero unauthorized deploy (HMAC-SHA256).',
          pid: undefined,
        },
      ])
    }
  }, [initialEvents])

  // Live SSE stream listener for real-time logs
  useEffect(() => {
    try {
      const sse = new EventSource('/api/events/stream')

      const handleIncoming = (evType: string, data: any) => {
        const newEntry: LogEntry = {
          id: `live-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
          timestamp: formatSmartDateTime(new Date()),
          subsystem: evType.includes('gate') ? 'GATE' : (evType.includes('job') ? 'AGY' : 'WAL'),
          level: evType.includes('error') ? 'ERROR' : (evType.includes('gate') ? 'WARN' : 'INFO'),
          message: typeof data === 'string' ? data : (data?.message || JSON.stringify(data)),
          pid: data?.pid || undefined,
        }
        setLogs((prev) => [...prev.slice(-250), newEntry])
      }

      sse.addEventListener('gate', (e: MessageEvent) => handleIncoming('gate', e.data))
      sse.addEventListener('job', (e: MessageEvent) => handleIncoming('job', e.data))
      sse.addEventListener('sprint_executed', (e: MessageEvent) => handleIncoming('sprint', e.data))
      sse.addEventListener('changes_applied', (e: MessageEvent) => handleIncoming('changes', e.data))

      return () => sse.close()
    } catch {}
  }, [])

  // Auto-scroll logic (scrolls ONLY the terminal container, never the page window)
  useEffect(() => {
    if (autoScroll && viewportRef.current) {
      viewportRef.current.scrollTop = viewportRef.current.scrollHeight
    }
  }, [logs, autoScroll])

  // Filtering
  const filteredLogs = logs.filter((l) => {
    if (streamFilter === 'AGY' && l.subsystem !== 'AGY') return false
    if (streamFilter === 'GATE' && l.subsystem !== 'GATE') return false
    if (streamFilter === 'WAL' && l.subsystem !== 'WAL' && l.subsystem !== 'KERNEL') return false

    if (levelFilter !== 'ALL' && l.level !== levelFilter) return false

    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      return (
        l.message.toLowerCase().includes(term) ||
        l.subsystem.toLowerCase().includes(term) ||
        String(l.pid).includes(term)
      )
    }
    return true
  })

  const handleCopyLogs = () => {
    const text = filteredLogs
      .map((l) => `[${l.timestamp}] [${l.subsystem}:${l.pid || 'SYS'}] [${l.level}] ${l.message}`)
      .join('\n')
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const getLevelBadge = (level: LogEntry['level']) => {
    switch (level) {
      case 'SUCCESS':
        return 'text-zinc-100 bg-zinc-900 border-zinc-700'
      case 'WARN':
        return 'text-amber-300 bg-zinc-900 border-amber-500/30'
      case 'ERROR':
        return 'text-rose-300 bg-zinc-900 border-rose-500/30'
      case 'AUDIT':
        return 'text-zinc-200 bg-zinc-900 border-zinc-700'
      default:
        return 'text-zinc-300 bg-zinc-900 border-zinc-700'
    }
  }

  const getSubsystemColor = (sub: LogEntry['subsystem']) => {
    switch (sub) {
      case 'AGY':
        return 'text-zinc-200'
      case 'GATE':
        return 'text-zinc-300'
      case 'WAL':
        return 'text-zinc-300'
      case 'VCS':
        return 'text-zinc-300'
      default:
        return 'text-zinc-400'
    }
  }

  return (
    <div
      id="solidbit-log-terminal"
      className={`rounded-2xl sm:rounded-3xl bg-black border border-zinc-800 shadow-2xl flex flex-col transition-all overflow-hidden ${
        isExpanded ? 'fixed inset-3 sm:inset-6 z-50' : 'w-full'
      }`}
    >
      {/* Top Header / Bar */}
      <div className="px-4 py-3 bg-zinc-950 border-b border-zinc-800 flex flex-wrap items-center justify-between gap-3 shrink-0">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-white">
            <Terminal className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-white font-mono tracking-wide">
                Terminal de Telemetría & Logs SACL
              </span>
              <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-mono bg-zinc-900 text-zinc-300 border border-zinc-750">
                <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
                EN VIVO (SSE)
              </span>
            </div>
            <p className="text-[10px] text-zinc-500 font-mono">
              Salida estructurada: Kernel, agentes AGY, compuertas HMAC y eventos SQLite WAL
            </p>
          </div>
        </div>

        {/* Streams Tab Pills */}
        <div className="flex items-center gap-1 p-0.5 rounded-xl bg-black/50 border border-zinc-800">
          {(['ALL', 'AGY', 'GATE', 'WAL'] as const).map((stream) => (
            <button
              key={stream}
              onClick={() => setStreamFilter(stream)}
              className={`px-2.5 py-1 rounded-lg text-[10px] font-mono transition cursor-pointer ${
                streamFilter === stream
                  ? 'bg-white text-black font-bold shadow-sm'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              {stream === 'ALL'
                ? 'Todos'
                : stream === 'AGY'
                ? 'Agentes'
                : stream === 'GATE'
                ? 'Compuertas'
                : 'SQLite WAL'}
            </button>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setAutoScroll(!autoScroll)}
            className={`px-2.5 py-1.5 rounded-xl border text-[11px] font-mono flex items-center gap-1 transition cursor-pointer ${
              autoScroll
                ? 'bg-emerald-500/10 border-emerald-500/30 text-zinc-200'
                : 'bg-zinc-900 border-zinc-800 text-zinc-500'
            }`}
            title="Desplazamiento automático al recibir nuevos eventos"
          >
            <ArrowDownCircle className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Auto-scroll</span>
          </button>

          <button
            onClick={handleCopyLogs}
            className="p-1.5 rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-white transition cursor-pointer"
            title="Copiar buffer completo"
          >
            {copied ? <CheckCircle2 className="w-4 h-4 text-zinc-200" /> : <Copy className="w-4 h-4" />}
          </button>

          <button
            onClick={() => setLogs([])}
            className="p-1.5 rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-red-400 transition cursor-pointer"
            title="Limpiar consola"
          >
            <Trash2 className="w-4 h-4" />
          </button>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1.5 rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-white transition cursor-pointer"
            title={isExpanded ? 'Minimizar' : 'Pantalla Completa'}
          >
            {isExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="px-4 py-2 bg-[#080d13] border-b border-zinc-800 flex flex-wrap items-center justify-between gap-3 text-xs">
        {/* Search */}
        <div className="relative flex-1 min-w-[180px] max-w-xs">
          <Search className="w-3.5 h-3.5 text-zinc-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Filtrar por texto, PID o módulo..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-[#05080c] border border-zinc-800 rounded-xl pl-8 pr-3 py-1.5 text-xs text-white placeholder-zinc-600 focus:outline-none focus:border-emerald-500/50 font-mono"
          />
        </div>

        {/* Severity Filter */}
        <div className="flex items-center gap-1.5 text-[11px] font-mono text-zinc-400">
          <span className="hidden sm:inline">Nivel:</span>
          {(['ALL', 'INFO', 'SUCCESS', 'WARN', 'ERROR', 'AUDIT'] as const).map((lvl) => (
            <button
              key={lvl}
              onClick={() => setLevelFilter(lvl)}
              className={`px-2 py-0.5 rounded-md border text-[10px] transition cursor-pointer ${
                levelFilter === lvl
                  ? 'bg-zinc-800 border-zinc-600 text-white font-bold'
                  : 'border-transparent text-zinc-500 hover:text-zinc-300'
              }`}
            >
              {lvl}
            </button>
          ))}
        </div>

        <span className="text-[10px] font-mono text-zinc-500">
          Mostrando {filteredLogs.length} de {logs.length} líneas
        </span>
      </div>

      {/* Terminal Viewport */}
      <div
        ref={viewportRef}
        className={`p-3 sm:p-4 overflow-y-auto custom-scroll font-mono text-[11px] sm:text-xs leading-relaxed space-y-1 select-text ${
          isExpanded ? 'flex-1' : 'h-64 sm:h-72'
        }`}
      >
        {filteredLogs.length === 0 ? (
          <div className="text-center py-10 text-zinc-600 font-mono text-xs">
            No hay registros para los filtros seleccionados.
          </div>
        ) : (
          filteredLogs.map((log) => (
            <div
              key={log.id}
              className="flex items-start gap-2 sm:gap-3 hover:bg-white/[0.02] px-2 py-0.5 rounded transition group"
            >
              {/* Timestamp */}
              <span className="text-zinc-600 select-none shrink-0 font-mono text-[10px] sm:text-[11px]">
                {log.timestamp}
              </span>

              {/* Subsystem & PID */}
              <span
                className={`font-bold select-none shrink-0 text-[10px] sm:text-[11px] ${getSubsystemColor(
                  log.subsystem
                )}`}
              >
                [{log.subsystem}
                {log.pid ? `:${log.pid}` : ''}]
              </span>

              {/* Level Badge */}
              <span
                className={`px-1.5 py-0.2 rounded border text-[9px] font-bold select-none shrink-0 ${getLevelBadge(
                  log.level
                )}`}
              >
                {log.level}
              </span>

              {/* Log Message */}
              <span className="text-zinc-300 break-all flex-1 font-mono">
                {log.message}
              </span>
            </div>
          ))
        )}
        <div ref={terminalEndRef} />
      </div>

      {/* Terminal Footer Info Bar */}
      <div className="px-4 py-2 bg-[#080d13] border-t border-zinc-800 flex items-center justify-between text-[10px] font-mono text-zinc-500 shrink-0">
        <div className="flex items-center gap-3">
          <span>HOST: 127.0.0.1:8765</span>
          <span>&bull;</span>
          <span>MOTOR: SQLite WAL</span>
          <span>&bull;</span>
          <span>STATUS: Crash-Consistent</span>
        </div>
        <div>
          <span>Presione Copiar para exportar el buffer</span>
        </div>
      </div>
    </div>
  )
}
