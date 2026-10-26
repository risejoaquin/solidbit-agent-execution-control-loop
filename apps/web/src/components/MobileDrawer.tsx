import React from 'react'
import {
  Home,
  MessageSquare,
  GitBranch,
  Bot,
  PlayCircle,
  Folder,
  BarChart2,
  Settings,
  Play,
  X,
  Activity,
  Layers,
  Sparkles,
  Terminal,
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
  if (!isOpen) return null

  const navItems = [
    { id: 'dashboard', label: 'Inicio', icon: Home, action: () => onSelectSection('dashboard') },
    { id: 'chat', label: 'Chat IA (AGY)', icon: MessageSquare, action: () => onSelectSection('chat'), highlight: true },
    { id: 'designer', label: 'Roadmap & DAG', icon: GitBranch, action: () => onSelectSection('designer') },
    { id: 'agents', label: 'Flota de Agentes', icon: Bot, action: () => onSelectSection('agents') },
    { id: 'gates', label: 'Ejecuciones & HITL', icon: PlayCircle, action: () => onSelectSection('gates') },
    { id: 'projects', label: 'Proyectos & Worktrees', icon: Folder, action: () => onSelectSection('projects') },
    { id: 'database', label: 'Reportes & SQLite WAL', icon: BarChart2, action: () => onSelectSection('database') },
    { id: 'github', label: 'Configuración & GitHub', icon: Settings, action: () => onSelectSection('github') },
  ]

  const handleItemClick = (action: () => void) => {
    action()
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 md:hidden flex animate-fade-in">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/80 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      {/* Drawer Panel */}
      <div className="relative w-72 max-w-[85vw] bg-[#0c121a] border-r border-[#1b2533] flex flex-col justify-between p-4 shadow-2xl z-10">
        <div>
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-[#1b2533]">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
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
              className="w-8 h-8 rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-white flex items-center justify-center transition"
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
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition ${
                    isActive
                      ? 'bg-emerald-500 text-black font-bold shadow-md shadow-emerald-500/10'
                      : item.highlight
                      ? 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/25'
                      : 'text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.03]'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </div>
                  {item.highlight && !isActive && (
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  )}
                </button>
              )
            })}
          </nav>
        </div>

        {/* Bottom Actions & Status */}
        <div className="space-y-3 pt-3 border-t border-[#1b2533]">
          <button
            id="drawer-btn-sprint"
            onClick={() => {
              onClose()
              onOpenSprintModal()
            }}
            className="w-full py-2.5 px-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-bold text-xs flex items-center justify-center gap-2 transition shadow-lg shadow-emerald-500/20 cursor-pointer"
          >
            <Play className="w-3.5 h-3.5 fill-black" />
            <span>Ejecutar Sprint</span>
          </button>

          {/* SQLite WAL stats */}
          <div className="p-2.5 rounded-xl bg-[#080c10] border border-[#1b2533] space-y-1 text-[10px] font-mono">
            <div className="flex items-center justify-between text-zinc-400">
              <span className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                SQLite WAL:
              </span>
              <span className="text-emerald-400 font-bold">Activo</span>
            </div>
            <div className="flex justify-between text-zinc-500 text-[9px]">
              <span>Jobs: {dbStats?.jobs ?? 2}</span>
              <span>Runs: {dbStats?.runs ?? 28}</span>
              <span>Events: {dbStats?.events ?? 28}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
