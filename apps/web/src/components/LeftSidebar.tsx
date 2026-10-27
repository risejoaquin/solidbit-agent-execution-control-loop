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
} from 'lucide-react'

interface LeftSidebarProps {
  currentSection: string
  onSelectSection: (section: string) => void
  onOpenSprintModal: () => void
  dbStats?: {
    jobs?: number
    runs?: number
    events?: number
  }
}

export const LeftSidebar: React.FC<LeftSidebarProps> = ({
  currentSection,
  onSelectSection,
  onOpenSprintModal,
  dbStats,
}) => {
  const [showDbInfoModal, setShowDbInfoModal] = useState<boolean>(false)

  const navItems = [
    { id: 'dashboard', label: 'Inicio', icon: Home, action: () => onSelectSection('dashboard') },
    { id: 'chat', label: 'Chat IA (AGY)', icon: MessageSquare, action: () => onSelectSection('chat'), highlight: true },
    { id: 'sprint', label: 'Diseñar Sprint', icon: Sparkles, action: onOpenSprintModal },
    { id: 'jira', label: 'Jira Backlog', icon: CheckSquare, action: () => onSelectSection('jira') },
    { id: 'agents', label: 'Flota de Agentes', icon: Bot, action: () => onSelectSection('agents') },
    { id: 'connections', label: 'Sesiones CLI & Auth', icon: Key, action: () => onSelectSection('connections') },
    { id: 'workflows', label: 'Workflows & Skills', icon: Layers, action: () => onSelectSection('workflows') },
    { id: 'designer', label: 'Roadmap & DAG', icon: GitBranch, action: () => onSelectSection('designer') },
    { id: 'gates', label: 'Compuertas & Runs', icon: PlayCircle, action: () => onSelectSection('gates') },
    { id: 'projects', label: 'Worktrees & Archivos', icon: Folder, action: () => onSelectSection('projects') },
    { id: 'email', label: 'Email Gateway', icon: Mail, action: () => onSelectSection('email') },
    { id: 'database', label: 'Auditoría DB (WAL)', icon: BarChart2, action: () => onSelectSection('database') },
    { id: 'github', label: 'Configuración & Git', icon: Settings, action: () => onSelectSection('github') },
  ]

  const jobsCount = dbStats?.jobs ?? 0
  const runsCount = dbStats?.runs ?? 0
  const eventsCount = dbStats?.events ?? 0

  return (
    <>
      <aside className="hidden md:flex w-56 lg:w-60 border-r border-zinc-800 bg-black flex-col justify-between shrink-0 p-3 select-none">
        {/* Navigation Links */}
        <nav className="space-y-1">
          {navItems.map((item) => {
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
                className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs transition cursor-pointer ${
                  isActive
                    ? 'bg-white text-black font-semibold shadow-sm'
                    : 'text-zinc-400 hover:text-white hover:bg-zinc-900 font-medium'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </div>
                {item.highlight && (
                  <span className="w-2 h-2 rounded-full bg-white animate-pulse shadow-sm shadow-white/50" />
                )}
              </button>
            )
          })}
        </nav>

        {/* Persistencia Soberana: SQLite WAL Card */}
        <div className="p-3 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-2 text-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-white animate-pulse" />
              <span className="font-bold text-white text-[11px] tracking-tight">Persistencia Soberana</span>
            </div>
            <button
              type="button"
              onClick={() => setShowDbInfoModal(true)}
              className="text-zinc-500 hover:text-white transition p-0.5 rounded cursor-pointer"
              title="¿Qué es esto y para qué sirve?"
              aria-label="Información sobre SQLite WAL"
            >
              <HelpCircle className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="flex items-center justify-between">
            <span className="font-bold text-zinc-300 text-[11px] font-mono">SQLite V1 (WAL Mode)</span>
            <span className="px-1.5 py-0.2 rounded bg-zinc-900 text-zinc-300 border border-zinc-700 text-[9px] font-mono font-semibold">
              ACID LOCAL
            </span>
          </div>

          {/* Clickable database entity rows */}
          <div className="space-y-1 pt-1.5 border-t border-zinc-850 text-[11px] font-mono">
            <button
              type="button"
              onClick={() => onSelectSection('workflows')}
              className="w-full flex items-center justify-between p-1 rounded hover:bg-zinc-900 transition text-left cursor-pointer group"
              title="Ver definición de Jobs y Workflows"
            >
              <span className="text-zinc-400 group-hover:text-white flex items-center gap-1.5">
                <Layers className="w-3 h-3 text-zinc-500 group-hover:text-white" /> Jobs ({jobsCount})
              </span>
              <span className="text-[10px] text-zinc-500 group-hover:text-zinc-300 underline">Ver</span>
            </button>

            <button
              type="button"
              onClick={() => onSelectSection('executions')}
              className="w-full flex items-center justify-between p-1 rounded hover:bg-zinc-900 transition text-left cursor-pointer group"
              title="Ver historial de Runs y compuertas"
            >
              <span className="text-zinc-400 group-hover:text-white flex items-center gap-1.5">
                <Play className="w-3 h-3 text-zinc-500 group-hover:text-white" /> Runs ({runsCount})
              </span>
              <span className="text-[10px] text-zinc-500 group-hover:text-zinc-300 underline">Ver</span>
            </button>

            <button
              type="button"
              onClick={() => onSelectSection('database')}
              className="w-full flex items-center justify-between p-1 rounded hover:bg-zinc-900 transition text-left cursor-pointer group"
              title="Inspeccionar Eventos en SQLite"
            >
              <span className="text-zinc-400 group-hover:text-white flex items-center gap-1.5">
                <Activity className="w-3 h-3 text-zinc-500 group-hover:text-white" /> Eventos ({eventsCount})
              </span>
              <span className="text-[10px] text-zinc-500 group-hover:text-zinc-300 underline">Ver</span>
            </button>

            <button
              type="button"
              onClick={() => onSelectSection('database')}
              className="w-full flex items-center justify-between p-1 rounded hover:bg-zinc-900 transition text-left cursor-pointer group"
              title="Auditoría forense de Logs"
            >
              <span className="text-zinc-400 group-hover:text-white flex items-center gap-1.5">
                <Terminal className="w-3 h-3 text-zinc-500 group-hover:text-white" /> Logs Forenses
              </span>
              <span className="text-[10px] text-zinc-500 group-hover:text-zinc-300 underline">Ver</span>
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
                  (<code className="text-zinc-200 font-mono">control_loop.db</code>). Opera en modo 
                  <strong> WAL (Write-Ahead Logging)</strong>, lo que permite lecturas concurrentes sin bloquear escrituras.
                </p>
              </div>

              <div>
                <h4 className="font-bold text-white mb-1">¿Para qué sirve?</h4>
                <ul className="list-disc list-inside space-y-1 text-zinc-400">
                  <li><strong>Soberanía Total:</strong> Cero dependencia de servicios de base de datos cloud externos. Tus datos no salen de tu entorno local.</li>
                  <li><strong>Trazabilidad Inmutable:</strong> Registra cada <span className="text-zinc-200">Job</span>, cada ejecución de agentes (<span className="text-zinc-200">Runs</span>), cada bloqueo de seguridad y las firmas HMAC de las compuertas Human-in-the-Loop.</li>
                  <li><strong>Durabilidad ACID:</strong> En caso de fallo eléctrico o interrupción del proceso, el archivo WAL garantiza recuperación inmediata sin corrupción.</li>
                  <li><strong>Telemetría y Métricas:</strong> Alimenta las tablas de eventos y reportes forenses en tiempo real.</li>
                </ul>
              </div>

              <div className="p-3 rounded-2xl bg-zinc-900/60 border border-zinc-800 text-[11px] text-zinc-400">
                <span className="font-bold text-white">Acceso Rápido:</span> Haz clic en cualquiera de las métricas (Jobs, Runs, Eventos, Logs) para saltar directamente a la tabla correspondiente.
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
