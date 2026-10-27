import React from 'react'
import {
  Bot,
  Clock,
  Cpu,
  Server,
  Database,
  Shield,
  ShoppingBag,
  Layout,
  CheckCircle2,
  Terminal,
} from 'lucide-react'
import type { AgentItem, ActivityEvent } from '../types/orchestrator'

interface RightSidebarProps {
  agents: AgentItem[]
  events: ActivityEvent[]
  onSelectAgent?: (agent: AgentItem) => void
  onSelectEvent?: (event: ActivityEvent) => void
  onNavigateSection: (section: string) => void
}

export const RightSidebar: React.FC<RightSidebarProps> = ({
  agents,
  events,
  onSelectAgent,
  onSelectEvent,
  onNavigateSection,
}) => {
  const getIcon = (iconName: string) => {
    switch (iconName) {
      case 'cpu':
        return <Cpu className="w-3.5 h-3.5" />
      case 'server':
        return <Server className="w-3.5 h-3.5" />
      case 'database':
        return <Database className="w-3.5 h-3.5" />
      case 'shield':
        return <Shield className="w-3.5 h-3.5" />
      case 'shopping-bag':
        return <ShoppingBag className="w-3.5 h-3.5" />
      case 'layout':
        return <Layout className="w-3.5 h-3.5" />
      case 'check-circle':
        return <CheckCircle2 className="w-3.5 h-3.5" />
      default:
        return <Terminal className="w-3.5 h-3.5" />
    }
  }

  const activeCount = agents.filter((a) => a.status === 'Activo').length

  return (
    <aside
      id="dashboard-right-sidebar"
      className="w-72 lg:w-80 border-l border-zinc-800 bg-black overflow-y-auto custom-scroll p-4 space-y-5 shrink-0 hidden xl:block select-none"
    >
      {/* Card 1: Agentes */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-white flex items-center gap-2">
            <Bot className="w-4 h-4 text-zinc-200" /> Agentes
          </span>
          <span id="right-agents-ratio" className="text-[11px] font-mono text-zinc-400">
            {activeCount}/{agents.length} activos
          </span>
        </div>

        <div id="right-agents-list" className="space-y-2 text-xs">
          {agents.map((a) => {
            const isEmerald = a.color === 'emerald'
            const isAmber = a.color === 'amber'
            return (
              <div
                key={a.id}
                onClick={() => onSelectAgent?.(a)}
                className="flex items-center justify-between p-2 rounded-xl bg-zinc-950 border border-zinc-800/80 hover:border-zinc-600 hover:bg-zinc-900 transition cursor-pointer"
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <div className="w-7 h-7 rounded-lg bg-black/40 border border-white/5 flex items-center justify-center text-zinc-300 shrink-0">
                    {getIcon(a.icon)}
                  </div>
                  <div className="leading-tight truncate">
                    <div className="text-xs font-semibold text-white truncate">{a.name}</div>
                    <div className="text-[10px] text-zinc-400 truncate">{a.role}</div>
                  </div>
                </div>
                <div
                  className={`flex items-center gap-1.5 text-[10px] font-medium shrink-0 ${
                    isEmerald ? 'text-zinc-200' : isAmber ? 'text-amber-400' : 'text-zinc-500'
                  }`}
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      isEmerald ? 'bg-white' : isAmber ? 'bg-amber-400' : 'bg-zinc-600'
                    }`}
                  ></span>
                  <span>{a.status}</span>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Card 2: Actividad reciente */}
      <div className="space-y-3 pt-3 border-t border-[#1b2533]">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-white flex items-center gap-2">
            <Clock className="w-4 h-4 text-zinc-400" /> Actividad reciente
          </span>
          <button
            type="button"
            onClick={() => onNavigateSection('database')}
            className="text-[11px] text-zinc-400 hover:text-white transition"
          >
            Ver todas
          </button>
        </div>

        <div id="right-activity-list" className="space-y-2.5 text-xs">
          {events.length > 0 ? (
            events.slice(0, 6).map((ev) => {
              const isFatal = ev.severity === 'FATAL' || ev.severity === 'ERROR'
              const isWarn = ev.severity === 'WARN'
              return (
                <div
                  key={ev.event_id}
                  onClick={() => onSelectEvent?.(ev)}
                  className="p-2 rounded-xl bg-zinc-950 border border-zinc-800/80 space-y-1 hover:border-white/10 transition cursor-pointer"
                >
                  <div className="flex items-center justify-between">
                    <span
                      className={`text-[11px] font-bold font-mono ${
                        isFatal ? 'text-red-400' : isWarn ? 'text-amber-400' : 'text-zinc-200'
                      }`}
                    >
                      {ev.event_type}
                    </span>
                    <span className="text-[9px] font-mono text-zinc-500">
                      {ev.created_at ? new Date(ev.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'ahora'}
                    </span>
                  </div>
                  <div className="text-[11px] text-zinc-300 truncate max-w-[240px]">
                    {ev.payload_json ? ev.payload_json.slice(0, 60) + '...' : 'Evento auditado en SQLite WAL'}
                  </div>
                </div>
              )
            })
          ) : (
            <div className="text-xs text-zinc-500 text-center py-2">Sin eventos recientes registrados</div>
          )}
        </div>
      </div>
    </aside>
  )
}
