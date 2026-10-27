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
  X,
  MessageSquare,
  Key,
  Mail,
  HelpCircle,
  Database,
  ExternalLink,
} from 'lucide-react'

interface MobileDrawerProps {
  isOpen: boolean
  onClose: () => void
  currentSection: string
  onSelectSection: (section: string) => void
  onOpenSprintModal: () => void
  projectName: string
  dbStats?: {
    jobs?: number
    runs?: number
    events?: number
  }
}

export const MobileDrawer: React.FC<MobileDrawerProps> = ({
  isOpen,
  onClose,
  currentSection,
  onSelectSection,
  onOpenSprintModal,
  projectName,
  dbStats,
}) => {
  const [showDbInfoModal, setShowDbInfoModal] = useState<boolean>(false)

  if (!isOpen) return null

  const navItems = [
    { id: 'dashboard', label: 'Inicio', icon: Home, action: () => onSelectSection('dashboard') },
    { id: 'chat', label: 'Chat IA (AGY)', icon: MessageSquare, action: () => onSelectSection('chat'), highlight: true },
    { id: 'connections', label: 'Sesiones CLI & Auth', icon: Key, action: () => onSelectSection('connections') },
    { id: 'workflows', label: 'Workflows & Skills (AGY)', icon: Layers, action: () => onSelectSection('workflows') },
    { id: 'designer', label: 'Roadmap & DAG', icon: GitBranch, action: () => onSelectSection('designer') },
    { id: 'agents', label: 'Flota de Agentes', icon: Bot, action: () => onSelectSection('agents') },
    { id: 'gates', label: 'Ejecuciones & HITL', icon: PlayCircle, action: () => onSelectSection('gates') },
    { id: 'projects', label: 'Proyectos & Worktrees', icon: Folder, action: () => onSelectSection('projects') },
    { id: 'email', label: 'Email Gateway', icon: Mail, action: () => onSelectSection('email') },
    { id: 'database', label: 'Reportes & SQLite WAL', icon: BarChart2, action: () => onSelectSection('database') },
    { id: 'github', label: 'Configuración & GitHub', icon: Settings, action: () => onSelectSection('github') },
  ]

  const handleItemClick = (action: () => void) => {
    action()
    onClose()
  }

  const jobsCount = dbStats?.jobs ?? 0
  const runsCount = dbStats?.runs ?? 0
  const eventsCount = dbStats?.events ?? 0

  return (
    <>
      <div className="fixed inset-0 z-[100] md:hidden flex animate-fade-in text-left">
        {/* Backdrop */}
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-sm transition-opacity"
          onClick={onClose}
        />

        {/* Drawer Panel */}
        <div className="relative w-72 max-w-[85vw] bg-black border-r border-zinc-800 flex flex-col justify-between p-4 shadow-2xl z-10 overflow-y-auto custom-scroll">
          <div>
            {/* Header */}
            <div className="flex items-center justify-between pb-4 border-b border-zinc-800">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-zinc-900 border border-zinc-750 flex items-center justify-center text-white">
                  <Layers className="w-4 h-4" />
                </div>
                <div>
                  <span className="text-xs font-bold text-white block">SolidBit SACL</span>
                  <span className="text-[10px] text-zinc-400 font-mono truncate max-w-[130px] block">
                    {projectName}
                  </span>
                </div>
              </div>

              <button
                id="drawer-close-btn"
                onClick={onClose}
                className="w-8 h-8 rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-white flex items-center justify-center transition cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Navigation Links */}
            <nav className="mt-4 space-y-1">
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
                    id={`drawer-nav-${item.id}`}
                    onClick={() => handleItemClick(item.action)}
                    className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition cursor-pointer ${
                      isActive
                        ? 'bg-white text-black font-bold shadow-sm'
                        : item.highlight
                        ? 'text-zinc-200 bg-zinc-900 border border-zinc-750'
                        : 'text-zinc-400 hover:text-white hover:bg-zinc-900'
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <Icon className="w-4 h-4" />
                      <span>{item.label}</span>
                    </div>
                    {item.highlight && !isActive && (
                      <span className="w-2 h-2 rounded-full bg-white animate-pulse" />
                    )}
                  </button>
                )
              })}
            </nav>
          </div>

          {/* Bottom Actions & Status */}
          <div className="space-y-3 pt-3 border-t border-zinc-800 mt-4">
            <button
              id="drawer-btn-sprint"
              onClick={() => {
                onClose()
                onOpenSprintModal()
              }}
              className="w-full py-2.5 px-3 rounded-xl bg-white hover:bg-zinc-200 text-black font-bold text-xs flex items-center justify-center gap-2 transition shadow-sm cursor-pointer"
            >
              <Play className="w-3.5 h-3.5 fill-black" />
              <span>Ejecutar Sprint</span>
            </button>

            {/* SQLite WAL stats: Honest & Clickable */}
            <div className="p-3 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-2 text-[10px] font-mono">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1.5 text-white font-bold">
                  <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
                  Persistencia Soberana
                </span>
                <button
                  type="button"
                  onClick={() => setShowDbInfoModal(true)}
                  className="text-zinc-400 hover:text-white"
                  title="¿Qué es esto?"
                >
                  <HelpCircle className="w-3.5 h-3.5" />
                </button>
              </div>

              <div className="flex items-center justify-between text-zinc-400">
                <span>Modo de Durabilidad:</span>
                <span className="text-zinc-200 font-bold">WAL ACID</span>
              </div>

              <div className="grid grid-cols-3 gap-1 pt-1 border-t border-zinc-800 text-center">
                <button
                  onClick={() => handleItemClick(() => onSelectSection('workflows'))}
                  className="p-1 rounded bg-zinc-900 hover:bg-zinc-850 text-zinc-300"
                >
                  <div className="text-[9px] text-zinc-500">Jobs</div>
                  <div className="font-bold text-white">{jobsCount}</div>
                </button>
                <button
                  onClick={() => handleItemClick(() => onSelectSection('executions'))}
                  className="p-1 rounded bg-zinc-900 hover:bg-zinc-850 text-zinc-300"
                >
                  <div className="text-[9px] text-zinc-500">Runs</div>
                  <div className="font-bold text-white">{runsCount}</div>
                </button>
                <button
                  onClick={() => handleItemClick(() => onSelectSection('database'))}
                  className="p-1 rounded bg-zinc-900 hover:bg-zinc-850 text-zinc-300"
                >
                  <div className="text-[9px] text-zinc-500">Eventos</div>
                  <div className="font-bold text-white">{eventsCount}</div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Explanatory Modal in Mobile */}
      {showDbInfoModal && (
        <div className="fixed inset-0 z-[110] bg-black/85 backdrop-blur-sm flex items-center justify-center p-4 text-left">
          <div className="w-full max-w-sm rounded-3xl bg-zinc-950 border border-zinc-800 p-5 space-y-3 shadow-2xl">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-white" />
                <h3 className="text-xs font-bold text-white">Persistencia Soberana SQLite</h3>
              </div>
              <button
                type="button"
                onClick={() => setShowDbInfoModal(false)}
                className="w-6 h-6 rounded bg-zinc-900 text-zinc-400 hover:text-white flex items-center justify-center"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
            <p className="text-[11px] text-zinc-400 leading-relaxed">
              Base de datos local relacional en disco. No depende de la nube.
              Registra de forma inmutable todos los Jobs, Runs de agentes, eventos y firmas HMAC.
            </p>
            <div className="pt-2 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => {
                  setShowDbInfoModal(false)
                  handleItemClick(() => onSelectSection('database'))
                }}
                className="px-3 py-1.5 rounded-xl bg-zinc-900 border border-zinc-800 text-xs text-white"
              >
                Ver Tablas
              </button>
              <button
                type="button"
                onClick={() => setShowDbInfoModal(false)}
                className="px-3 py-1.5 rounded-xl bg-white text-black font-bold text-xs"
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
