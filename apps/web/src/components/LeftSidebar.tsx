import React from 'react'
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
  const navItems = [
    { id: 'dashboard', label: 'Inicio', icon: Home, action: () => onSelectSection('dashboard') },
    { id: 'chat', label: 'Chat IA (AGY)', icon: MessageSquare, action: () => onSelectSection('chat'), highlight: true },
    { id: 'designer', label: 'Roadmap', icon: GitBranch, action: () => onSelectSection('designer') },
    { id: 'agents', label: 'Agentes', icon: Bot, action: () => onSelectSection('agents') },
    { id: 'gates', label: 'Ejecuciones', icon: PlayCircle, action: () => onSelectSection('gates') },
    { id: 'projects', label: 'Proyectos', icon: Folder, action: () => onSelectSection('projects') },
    { id: 'database', label: 'Reportes', icon: BarChart2, action: () => onSelectSection('database') },
    { id: 'github', label: 'Configuración', icon: Settings, action: () => onSelectSection('github') },
  ]

  return (
    <aside className="hidden md:flex w-56 lg:w-60 border-r border-[#161f2c] bg-[#0c121a] flex-col justify-between shrink-0 p-3 select-none">
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
              type="button"
              id={`nav-btn-${item.id}`}
              onClick={item.action}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs transition cursor-pointer text-left ${
                isActive
                  ? 'bg-[#14261f] text-emerald-400 border border-emerald-500/20 font-bold'
                  : 'text-zinc-400 hover:text-white hover:bg-white/5 font-medium'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </div>
              {item.highlight && (
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-sm shadow-emerald-400/80" />
              )}
            </button>
          )
        })}
      </nav>

      {/* Bottom SQLite V1 System Card */}
      <div className="p-3 rounded-2xl bg-[#0f1622] border border-[#1b2533] space-y-2 text-xs">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="font-bold text-white text-[11px]">Sistema Operativo</span>
        </div>
        <div className="font-bold text-white text-xs font-mono">SQLite V1 (WAL Mode)</div>
        <div className="space-y-1.5 pt-1 border-t border-white/5 text-[11px] font-mono">
          <div className="flex items-center justify-between">
            <span className="text-zinc-400 flex items-center gap-1.5">
              <Layers className="w-3 h-3 text-zinc-500" /> Jobs ({dbStats?.jobs ?? 2})
            </span>
            <span className="px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-400 text-[10px] font-bold">
              Online
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-zinc-400 flex items-center gap-1.5">
              <Play className="w-3 h-3 text-zinc-500" /> Runs ({dbStats?.runs ?? 26})
            </span>
            <span className="px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-400 text-[10px] font-bold">
              Online
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-zinc-400 flex items-center gap-1.5">
              <Activity className="w-3 h-3 text-zinc-500" /> Eventos ({dbStats?.events ?? 26})
            </span>
            <span className="px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-400 text-[10px] font-bold">
              Online
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-zinc-400 flex items-center gap-1.5">
              <Terminal className="w-3 h-3 text-zinc-500" /> Logs
            </span>
            <span className="px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-400 text-[10px] font-bold">
              Online
            </span>
          </div>
        </div>
      </div>
    </aside>
  )
}
