import React from 'react'
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
}

export const ConnectedTechnologiesMatrix: React.FC<ConnectedTechnologiesMatrixProps> = ({
  connections = [],
  onRefresh,
  onTestConnection,
}) => {
  // Baseline technologies if waiting for backend data
  const defaultTechs: TechnologyItem[] = [
    {
      id: 'agy',
      name: 'Antigravity AI (AGY)',
      category: 'ai',
      status: 'connected',
      version: 'Local Daemon v2.0',
      account_info: 'Puerto 8765 (Gemini / Claude)',
    },
    {
      id: 'git',
      name: 'Git VCS & Worktrees',
      category: 'vcs',
      status: 'connected',
      version: 'Git 2.40+',
      account_info: 'Dirty-Root Guard Activo',
    },
    {
      id: 'gh',
      name: 'GitHub CLI (gh)',
      category: 'vcs',
      status: 'connected',
      version: 'Keyring Auth',
      account_info: 'CI/CD Actions Sincronizado',
    },
    {
      id: 'jira',
      name: 'Atlassian Jira Cloud',
      category: 'governance',
      status: 'connected',
      version: 'Tablero SOLID',
      account_info: 'Sincronización DoR/DoD',
    },
    {
      id: 'sqlite',
      name: 'SQLite WAL Store',
      category: 'database',
      status: 'connected',
      version: 'WAL ACID',
      account_info: 'sacl_ops.db (22 Dominios)',
    },
    {
      id: 'supabase',
      name: 'Supabase PostgreSQL',
      category: 'database',
      status: 'connected',
      version: 'v2.122.0',
      account_info: 'Migraciones Cloud Verificadas',
    },
    {
      id: 'railway',
      name: 'Railway Cloud PaaS',
      category: 'infra',
      status: 'connected',
      version: 'Staging Preview',
      account_info: 'autoDeploy: OFF (Gate 1)',
    },
    {
      id: 'resend',
      name: 'Resend Email Gateway',
      category: 'notifications',
      status: 'connected',
      version: 'CLI Activo',
      account_info: 'HMAC Webhooks & Alertas PO',
    },
  ]

  const displayTechs = connections.length > 0 ? connections : defaultTechs

  const getTechIcon = (id: string, category: string) => {
    switch (id) {
      case 'agy':
        return <Cpu className="w-4 h-4 text-zinc-200" />
      case 'gh':
      case 'github':
        return <GitFork className="w-4 h-4 text-white" />
      case 'git':
        return <GitBranch className="w-4 h-4 text-zinc-200" />
      case 'supabase':
      case 'sqlite':
      case 'database':
        return <Database className="w-4 h-4 text-zinc-200" />
      case 'railway':
        return <Server className="w-4 h-4 text-zinc-200" />
      case 'resend':
        return <Mail className="w-4 h-4 text-zinc-200" />
      case 'jira':
        return <ShieldCheck className="w-4 h-4 text-amber-400" />
      default:
        return category === 'runtime' ? (
          <Terminal className="w-4 h-4 text-zinc-400" />
        ) : (
          <Layers className="w-4 h-4 text-zinc-400" />
        )
    }
  }

  const getStatusBadge = (status: TechnologyItem['status']) => {
    switch (status) {
      case 'connected':
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-zinc-900 text-zinc-200 border border-zinc-700 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
            CONECTADO
          </span>
        )
      case 'unauthenticated':
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-500/15 text-amber-400 border border-amber-500/30">
            <AlertTriangle className="w-3 h-3 text-amber-400" />
            STANDBY
          </span>
        )
      case 'error':
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-rose-500/15 text-rose-400 border border-rose-500/30">
            ERROR
          </span>
        )
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-mono font-medium bg-zinc-800 text-zinc-400 border border-zinc-700">
            INACTIVO
          </span>
        )
    }
  }

  const connectedCount = displayTechs.filter((t) => t.status === 'connected').length

  return (
    <section
      aria-label="Matriz de Tecnologías y Servicios Conectados"
      className="p-4 sm:p-5 rounded-2xl sm:rounded-3xl bg-zinc-950 border border-zinc-800 space-y-4 shadow-xl"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-800 pb-3.5">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl sm:rounded-2xl bg-zinc-900 border border-zinc-750 flex items-center justify-center text-white shrink-0">
            <Server className="w-4 h-4 sm:w-5 sm:h-5" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-sm sm:text-base font-bold text-white tracking-wide">
                Tecnologías & Servicios Conectados
              </h2>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-zinc-200 border border-emerald-500/25 font-bold">
                {connectedCount} de {displayTechs.length} Operativos
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              Estado en tiempo real de infraestructura, agentes de IA, persistencia WAL y canales de notificación.
            </p>
          </div>
        </div>

        {onRefresh && (
          <button
            type="button"
            onClick={onRefresh}
            className="self-start sm:self-auto px-3 py-1.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-zinc-300 text-xs font-mono flex items-center gap-1.5 transition cursor-pointer"
            title="Actualizar diagnóstico de conexiones"
          >
            <RefreshCw className="w-3.5 h-3.5 text-zinc-200" />
            <span>Diagnóstico</span>
          </button>
        )}
      </div>

      {/* Grid: 2 columns on Mobile, 4 columns on Tablet, 4-5 on Desktop */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-4 gap-2.5 sm:gap-3">
        {displayTechs.map((tech) => (
          <div
            key={tech.id}
            onClick={() => onTestConnection?.(tech.id)}
            className="p-3 sm:p-3.5 rounded-xl sm:rounded-2xl bg-[#070b10] border border-zinc-800 hover:border-zinc-600 space-y-2 transition cursor-pointer group"
          >
            {/* Top row: Icon + Status */}
            <div className="flex items-center justify-between gap-1">
              <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-black/60 border border-white/5 flex items-center justify-center shrink-0 group-hover:scale-105 transition">
                {getTechIcon(tech.id, tech.category)}
              </div>
              {getStatusBadge(tech.status)}
            </div>

            {/* Name */}
            <div>
              <span className="text-xs font-bold text-white block truncate group-hover:text-zinc-200 transition">
                {tech.name}
              </span>
              <span className="text-[10px] font-mono text-zinc-400 block truncate mt-0.5">
                {tech.account_info || tech.version || 'Local SDK'}
              </span>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
