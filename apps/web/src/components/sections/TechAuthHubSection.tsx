import React, { useState, useEffect } from 'react'

export interface ConnectionStatusItem {
  id: string
  name: string
  category: string
  status: 'connected' | 'unauthenticated' | 'disconnected' | 'degraded' | string
  account_info?: string
  last_checked?: string
  ping_ms?: number
  cli_command?: string
}

export const TechAuthHubSection: React.FC = () => {
  const [connections, setConnections] = useState<ConnectionStatusItem[]>([
    {
      id: 'github',
      name: 'GitHub VCS & PRs',
      category: 'Control de Versiones',
      status: 'connected',
      account_info: 'risejoaquin (Authenticated)',
      last_checked: 'Justo ahora',
      ping_ms: 42,
      cli_command: 'git status',
    },
    {
      id: 'sqlite_wal',
      name: 'SQLite WAL State Store',
      category: 'Persistencia Operacional',
      status: 'connected',
      account_info: 'sacl_ops.db (Domain 16)',
      last_checked: 'Justo ahora',
      ping_ms: 1,
      cli_command: 'sacl status',
    },
    {
      id: 'resend',
      name: 'Resend Mail Gateway',
      category: 'Notificaciones & HITL',
      status: 'connected',
      account_info: 'notificaciones@solidbit.mx',
      last_checked: 'Hace 2 min',
      ping_ms: 128,
      cli_command: 'sacl test --channel email',
    },
    {
      id: 'supabase',
      name: 'Supabase Database & RLS',
      category: 'Base de Datos de Producción',
      status: 'unauthenticated',
      account_info: 'Requiere vinculación en host CLI',
      last_checked: 'Inactivo',
      cli_command: 'supabase login',
    },
    {
      id: 'jira',
      name: 'Jira Software Cloud',
      category: 'Gestión de Requerimientos',
      status: 'connected',
      account_info: 'solidbit.atlassian.net',
      last_checked: 'Hace 1 min',
      ping_ms: 95,
      cli_command: 'sacl jira sync',
    },
    {
      id: 'cloudflare',
      name: 'Cloudflare Zero Trust Tunnel',
      category: 'Edge & Ingress Seguro',
      status: 'connected',
      account_info: 'doom-expenditures-forgot-indicates',
      last_checked: 'Justo ahora',
      ping_ms: 18,
      cli_command: 'cloudflared tunnel',
    },
  ])

  const [isLoading, setIsLoading] = useState<boolean>(false)

  const loadConnections = async () => {
    setIsLoading(true)
    try {
      const res = await fetch('/api/connections')
      const data = await res.json()
      if (data && data.technologies && data.technologies.length > 0) {
        setConnections(data.technologies)
      }
    } catch (e) {
      console.warn('Error loading connections:', e)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadConnections()
  }, [])

  return (
    <div className="flex flex-col h-full w-full bg-[#000000] space-y-3 select-none text-left">
      {/* Header Técnico */}
      <div className="h-12 border border-white/8 bg-[#0a0a0a] rounded px-4 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2.5">
          <svg className="w-4 h-4 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
          <span className="text-xs font-semibold text-white tracking-wide uppercase font-sans">
            Tecnologías Locales &amp; Conexiones
          </span>
          <span className="text-[10px] font-mono text-zinc-500">
            · Read-Only State Consumer (Seguridad Zero-Token en Frontend)
          </span>
        </div>

        <button
          onClick={loadConnections}
          disabled={isLoading}
          className="p-1.5 rounded bg-[#000000] border border-white/8 text-zinc-400 hover:text-white transition cursor-pointer"
          title="Actualizar estado de conexiones"
        >
          <svg className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
            <path d="M3 3v5h5" />
            <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16" />
            <path d="M16 21h5v-5" />
          </svg>
        </button>
      </div>

      {/* Grid de Conexiones */}
      <div className="flex-1 overflow-y-auto custom-scroll">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
          {connections.map((item) => {
            const isConnected = item.status === 'connected' || item.status === 'authenticated'
            const isDegraded = item.status === 'unauthenticated' || item.status === 'degraded'
            const statusClass = isConnected
              ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
              : isDegraded
              ? 'text-amber-400 bg-amber-500/10 border-amber-500/20'
              : 'text-red-400 bg-red-500/10 border-red-500/20'

            return (
              <div
                key={item.id}
                className="bg-[#0a0a0a] border border-white/8 rounded p-3 flex flex-col justify-between hover:border-white/20 transition"
              >
                <div>
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-semibold text-white truncate font-sans">{item.name}</span>
                    <span className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border uppercase shrink-0 ${statusClass}`}>
                      {item.status}
                    </span>
                  </div>
                  <div className="text-[10px] text-zinc-500 font-mono mt-0.5 truncate">{item.category}</div>
                </div>

                <div className="my-2.5 py-1.5 px-2 bg-[#000000] border border-white/8 rounded">
                  <div className="text-[10px] text-zinc-300 font-mono truncate">{item.account_info || 'Sin sesión activa'}</div>
                  {item.cli_command && (
                    <div className="text-[9px] text-zinc-500 font-mono mt-1 truncate">
                      cli: {item.cli_command}
                    </div>
                  )}
                </div>

                <div className="flex items-center justify-between text-[9px] font-mono text-zinc-500 pt-1 border-t border-white/8">
                  <span>{item.ping_ms ? `ping: ${item.ping_ms}ms` : 'IPC Local'}</span>
                  <span>{item.last_checked || 'Verificado'}</span>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
