import React, { useState } from 'react'
import {
  Cpu,
  GitBranch,
  GitFork,
  Database,
  Server,
  Mail,
  Layers,
  Terminal,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  ExternalLink,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'

export interface TechnologyItem {
  id: string
  name: string
  category: 'ai' | 'vcs' | 'infra' | 'database' | 'governance' | 'notifications' | 'runtime' | 'cloud'
  status: 'connected' | 'unauthenticated' | 'not_installed' | 'error'
  version?: string
  account_info?: string
  cli_path?: string
  last_checked?: string
}

interface ConnectedTechnologiesMatrixProps {
  connections: TechnologyItem[]
  onRefresh?: () => void
  onTestConnection?: (techId: string) => void
  onNavigateSection?: (sectionId: string) => void
}

export const ConnectedTechnologiesMatrix: React.FC<ConnectedTechnologiesMatrixProps> = ({
  connections = [],
  onRefresh,
  onTestConnection,
  onNavigateSection,
}) => {
  const [expanded, setExpanded] = useState<boolean>(false)
  const displayTechs = connections
  const connectedCount = displayTechs.filter((t) => t.status === 'connected').length

  const getTechIcon = (id: string, category: string) => {
    switch (id) {
      case 'agy':
        return <Cpu className="w-3.5 h-3.5 text-zinc-200" />
      case 'gh':
      case 'github':
        return <GitFork className="w-3.5 h-3.5 text-white" />
      case 'git':
        return <GitBranch className="w-3.5 h-3.5 text-zinc-200" />
      case 'supabase':
      case 'sqlite':
      case 'database':
        return <Database className="w-3.5 h-3.5 text-zinc-200" />
      case 'railway':
        return <Server className="w-3.5 h-3.5 text-zinc-200" />
      case 'resend':
        return <Mail className="w-3.5 h-3.5 text-zinc-200" />
      case 'jira':
        return <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
      default:
        return category === 'runtime' ? (
          <Terminal className="w-3.5 h-3.5 text-zinc-400" />
        ) : (
          <Layers className="w-3.5 h-3.5 text-zinc-400" />
        )
    }
  }

  return (
    <section
      aria-label="Matriz de Tecnologías y Servicios Conectados"
      className="p-4 sm:p-5 rounded-2xl bg-zinc-950 border border-zinc-800/90 space-y-3.5 shadow-lg"
    >
      {/* Compact Header & Status Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-white shrink-0">
            <Server className="w-4 h-4" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-xs sm:text-sm font-bold text-white tracking-tight">
                Ecosistema de Integraciones & Sesiones CLI
              </h2>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-bold">
                {connectedCount}/{displayTechs.length} Operativos
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          {onRefresh && (
            <button
              type="button"
              onClick={onRefresh}
              className="px-2.5 py-1.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-300 text-[11px] font-mono flex items-center gap-1.5 transition cursor-pointer"
              title="Actualizar diagnóstico de conexiones"
            >
              <RefreshCw className="w-3 h-3 text-zinc-300" />
              <span>Diagnóstico</span>
            </button>
          )}
          <button
            type="button"
            onClick={() => setExpanded(!expanded)}
            className="px-2.5 py-1.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-300 text-[11px] font-mono flex items-center gap-1 transition cursor-pointer"
          >
            <span>{expanded ? 'Vista Compacta' : 'Ver Detalles'}</span>
            {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
          {onNavigateSection && (
            <button
              type="button"
              id="btn-goto-auth-hub"
              onClick={() => onNavigateSection('connections')}
              className="px-3 py-1.5 rounded-xl bg-white hover:bg-zinc-200 text-black text-[11px] font-mono font-bold flex items-center gap-1.5 transition cursor-pointer shadow-sm"
            >
              <span>Auth Hub</span>
              <ExternalLink className="w-3 h-3 text-black" />
            </button>
          )}
        </div>
      </div>

      {/* Compact Pill Strip (Default) vs Detailed Grid (Expanded) */}
      {displayTechs.length === 0 ? (
        <div className="p-4 rounded-xl bg-black border border-zinc-850 text-center">
          <span className="text-xs text-zinc-400 font-mono">Verificando binarios y sesiones del sistema...</span>
        </div>
      ) : !expanded ? (
        <div className="flex flex-wrap items-center gap-2 pt-1">
          {displayTechs.map((tech) => {
            const isOk = tech.status === 'connected'
            const isWarn = tech.status === 'unauthenticated'
            return (
              <div
                key={tech.id}
                onClick={() => onTestConnection?.(tech.id)}
                title={`${tech.name}: ${tech.account_info || tech.version || tech.status}`}
                className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-black border border-zinc-800/90 hover:border-zinc-600 text-xs transition cursor-pointer"
              >
                <span
                  className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                    isOk ? 'bg-emerald-400' : isWarn ? 'bg-amber-400' : 'bg-zinc-600'
                  }`}
                />
                <span className="font-semibold text-zinc-200 text-[11px]">{tech.name}</span>
                <span className="text-[10px] font-mono text-zinc-500 hidden sm:inline">
                  {isOk ? 'OK' : isWarn ? 'STANDBY' : 'OFF'}
                </span>
              </div>
            )
          })}
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5 pt-2 border-t border-zinc-850 animate-fade-in">
          {displayTechs.map((tech) => {
            const isOk = tech.status === 'connected'
            const isWarn = tech.status === 'unauthenticated'
            return (
              <div
                key={tech.id}
                onClick={() => onTestConnection?.(tech.id)}
                className="p-3 rounded-xl bg-black border border-zinc-800 hover:border-zinc-600 space-y-1.5 transition cursor-pointer"
              >
                <div className="flex items-center justify-between">
                  <div className="w-6 h-6 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center">
                    {getTechIcon(tech.id, tech.category)}
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded-full text-[9px] font-mono font-bold ${
                      isOk
                        ? 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20'
                        : isWarn
                        ? 'bg-amber-500/10 text-amber-300 border border-amber-500/20'
                        : 'bg-zinc-900 text-zinc-500 border border-zinc-800'
                    }`}
                  >
                    {isOk ? 'CONECTADO' : isWarn ? 'STANDBY' : 'INACTIVO'}
                  </span>
                </div>
                <div>
                  <div className="text-xs font-bold text-white truncate">{tech.name}</div>
                  <div className="text-[10px] font-mono text-zinc-400 truncate">
                    {tech.account_info || tech.version || 'Local SDK'}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </section>
  )
}
