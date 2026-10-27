import React, { useState } from 'react'
import {
  Home,
  Layers,
  GitBranch,
  Bot,
  PlayCircle,
  Folder,
  BarChart2,
  Settings,
  Play,
  Activity,
  Terminal,
  MessageSquare,
  Key,
  Mail,
  HelpCircle,
  Database,
  X,
  ExternalLink,
  CheckSquare,
  Sparkles,
  ShieldCheck,
} from 'lucide-react'

interface NavItem {
  id: string
  label: string
  icon: React.FC<{ className?: string }>
  action: () => void
  highlight?: boolean
  badge?: number
  shortcut?: string
}

interface NavGroup {
  title: string
  items: NavItem[]
}

interface LeftSidebarProps {
  currentSection: string
  onSelectSection: (section: string) => void
  onOpenSprintModal: () => void
  dbStats?: {
    jobs?: number
    runs?: number
    events?: number
  }
  pendingGatesCount?: number
}

export const LeftSidebar: React.FC<LeftSidebarProps> = ({
  currentSection,
  onSelectSection,
  onOpenSprintModal,
  dbStats,
  pendingGatesCount = 0,
}) => {
  const [showDbInfoModal, setShowDbInfoModal] = useState<boolean>(false)

  const navGroups: NavGroup[] = [
    {
      title: '1. Comando & Orquestación',
      items: [
        { id: 'dashboard', label: 'Centro de Mando', icon: Home, action: () => onSelectSection('dashboard'), shortcut: 'G D' },
        { id: 'chat', label: 'Copiloto IA (AGY)', icon: MessageSquare, action: () => onSelectSection('chat'), highlight: true, shortcut: 'G C' },
        { id: 'sprint', label: 'Diseñar Sprint', icon: Sparkles, action: onOpenSprintModal, shortcut: 'G S' },
      ],
    },
    {
      title: '2. Ciclo SDLC & Ejecución',
      items: [
        { id: 'jira', label: 'Jira Backlog', icon: CheckSquare, action: () => onSelectSection('jira'), shortcut: 'G J' },
        { id: 'designer', label: 'Topología DAG (Kahn)', icon: GitBranch, action: () => onSelectSection('designer'), shortcut: 'G R' },
        { id: 'agents', label: 'Flota de Agentes', icon: Bot, action: () => onSelectSection('agents'), shortcut: 'G A' },
        {
          id: 'gates',
          label: 'Compuertas HITL',
          icon: ShieldCheck,
          action: () => onSelectSection('gates'),
          badge: pendingGatesCount > 0 ? pendingGatesCount : undefined,
          shortcut: 'G G',
        },
      ],
    },
    {
      title: '3. Infraestructura & Auditoría',
      items: [
        { id: 'projects', label: 'Worktrees & Archivos', icon: Folder, action: () => onSelectSection('projects') },
        { id: 'workflows', label: 'Workflows & Skills', icon: Layers, action: () => onSelectSection('workflows') },
        { id: 'connections', label: 'Sesiones CLI & Auth', icon: Key, action: () => onSelectSection('connections') },
        { id: 'email', label: 'Email Gateway', icon: Mail, action: () => onSelectSection('email') },
        { id: 'database', label: 'Auditoría DB (WAL)', icon: BarChart2, action: () => onSelectSection('database') },
        { id: 'github', label: 'Configuración & Git', icon: Settings, action: () => onSelectSection('github') },
      ],
    },
  ]

  const jobsCount = dbStats?.jobs ?? 0
  const runsCount = dbStats?.runs ?? 0
  const eventsCount = dbStats?.events ?? 0

  return (
    <>
      <aside className="hidden md:flex w-60 lg:w-64 border-r border-zinc-800/80 bg-[#09090b] flex-col justify-between shrink-0 p-3.5 select-none overflow-y-auto custom-scroll">
        {/* Categorized Navigation Groups */}
        <nav className="space-y-5">
          {navGroups.map((group) => (
            <div key={group.title} className="space-y-1">
              <div className="px-2.5 pb-1 text-[10px] font-mono uppercase tracking-widest text-zinc-500 font-semibold">
                {group.title}
              </div>
              {group.items.map((item) => {
                const Icon = item.icon
                const isActive =
                  currentSection === item.id ||
                  (item.id === 'designer' && currentSection === 'roadmap') ||
                  (item.id === 'gates' && currentSection === 'executions') ||
                  (item.id === 'database' && currentSection === 'reports') ||
                  (item.id === 'github' && currentSection === 'settings')

                return (
                  <button
                    key={item.id}
                    id={`nav-${item.id}`}
                    onClick={item.action}
                    className={`w-full flex items-center justify-between px-2.5 py-2 rounded-xl text-xs transition-all duration-150 cursor-pointer group ${
                      isActive
                        ? 'bg-white text-black font-bold shadow-sm'
                        : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900/70 font-medium'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <Icon
                        className={`w-4 h-4 shrink-0 transition-colors ${
                          isActive ? 'text-black' : 'text-zinc-400 group-hover:text-zinc-200'
                        }`}
                      />
                      <span className="truncate">{item.label}</span>
                    </div>

                    <div className="flex items-center gap-1.5 shrink-0">
                      {item.badge !== undefined && (
                        <span
                          className={`px-1.5 py-0.5 rounded-full text-[9px] font-mono font-extrabold ${
                            isActive
                              ? 'bg-black text-white'
                              : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                          }`}
                        >
                          {item.badge}
                        </span>
                      )}
                      {item.highlight && !isActive && (
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                      )}
                      {item.shortcut && !item.badge && (
                        <span
                          className={`text-[9px] font-mono px-1 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity ${
                            isActive ? 'text-zinc-700' : 'text-zinc-600'
                          }`}
                        >
                          {item.shortcut}
                        </span>
                      )}
                    </div>
                  </button>
                )
              })}
            </div>
          ))}
        </nav>

        {/* Persistencia Soberana: Compact SQLite WAL Telemetry Footer */}
        <div className="mt-6 p-3 rounded-2xl bg-zinc-950/90 border border-zinc-800/80 space-y-2.5 text-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="font-bold text-zinc-200 text-[11px] tracking-tight">SQLite WAL Engine</span>
            </div>
            <button
              type="button"
              onClick={() => setShowDbInfoModal(true)}
              className="text-zinc-500 hover:text-white transition p-0.5 rounded cursor-pointer"
              title="¿Qué es la Persistencia Soberana SQLite WAL?"
              aria-label="Información sobre SQLite WAL"
            >
              <HelpCircle className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="grid grid-cols-3 gap-1.5 pt-1 text-center font-mono">
            <button
              type="button"
              onClick={() => onSelectSection('workflows')}
              className="p-1.5 rounded-xl bg-zinc-900/70 hover:bg-zinc-900 border border-zinc-800/60 transition cursor-pointer"
              title="Ver Jobs"
            >
              <div className="text-xs font-extrabold text-white">{jobsCount}</div>
              <div className="text-[9px] text-zinc-500 uppercase">Jobs</div>
            </button>
            <button
              type="button"
              onClick={() => onSelectSection('executions')}
              className="p-1.5 rounded-xl bg-zinc-900/70 hover:bg-zinc-900 border border-zinc-800/60 transition cursor-pointer"
              title="Ver Runs"
            >
              <div className="text-xs font-extrabold text-white">{runsCount}</div>
              <div className="text-[9px] text-zinc-500 uppercase">Runs</div>
            </button>
            <button
              type="button"
              onClick={() => onSelectSection('database')}
              className="p-1.5 rounded-xl bg-zinc-900/70 hover:bg-zinc-900 border border-zinc-800/60 transition cursor-pointer"
              title="Ver Eventos"
            >
              <div className="text-xs font-extrabold text-white">{eventsCount}</div>
              <div className="text-[9px] text-zinc-500 uppercase">Eventos</div>
            </button>
          </div>
        </div>
      </aside>

      {/* Explanatory Modal: ¿Qué es la Persistencia Soberana SQLite? */}
      {showDbInfoModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in text-left">
          <div className="w-full max-w-lg rounded-3xl bg-zinc-950 border border-zinc-800 p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-zinc-900 border border-zinc-700 flex items-center justify-center text-white">
                  <Database className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">Persistencia Soberana Local (SQLite WAL)</h3>
                  <p className="text-[11px] text-zinc-400">Normativa SolidBit RISEHANDBOOK (SB-ENG-HB-001 v1.0)</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowDbInfoModal(false)}
                className="w-7 h-7 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-white flex items-center justify-center transition cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs text-zinc-300 leading-relaxed">
              <div>
                <h4 className="font-bold text-white mb-1">¿Qué es este módulo?</h4>
                <p className="text-zinc-400">
                  Es la base de datos relacional nativa alojada directamente en el disco de tu máquina local 
                  (<code className="text-zinc-200 font-mono">sacl_ops.db</code>). Opera en modo 
                  <strong> WAL (Write-Ahead Logging)</strong>, lo que permite lecturas concurrentes sin bloquear escrituras.
                </p>
              </div>

              <div>
                <h4 className="font-bold text-white mb-1">¿Para qué sirve?</h4>
                <ul className="list-disc list-inside space-y-1 text-zinc-400">
                  <li><strong>Soberanía Total:</strong> Cero dependencia de bases de datos externas. Tus datos permanecen en tu entorno local.</li>
                  <li><strong>Trazabilidad Inmutable:</strong> Registra cada <span className="text-zinc-200">Job</span>, cada ejecución de agentes (<span className="text-zinc-200">Runs</span>), cada bloqueo de seguridad y las firmas HMAC de las compuertas Human-in-the-Loop.</li>
                  <li><strong>Durabilidad ACID:</strong> En caso de interrupción del proceso, el archivo WAL garantiza recuperación inmediata sin corrupción.</li>
                </ul>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-zinc-800">
              <button
                type="button"
                onClick={() => {
                  setShowDbInfoModal(false)
                  onSelectSection('database')
                }}
                className="px-3.5 py-1.5 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-600 text-xs text-white transition flex items-center gap-1.5 cursor-pointer"
              >
                <ExternalLink className="w-3.5 h-3.5" /> Explorar Base de Datos
              </button>
              <button
                type="button"
                onClick={() => setShowDbInfoModal(false)}
                className="px-4 py-1.5 rounded-xl bg-white text-black font-semibold text-xs hover:bg-zinc-200 transition cursor-pointer"
              >
                Entendido
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
