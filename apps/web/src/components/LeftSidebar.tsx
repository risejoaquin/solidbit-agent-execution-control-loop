import React, { useState } from 'react'
import {
  Home,
  GitBranch,
  Bot,
  Folder,
  BarChart2,
  Settings,
  MessageSquare,
  Key,
  Mail,
  Database,
  X,
  CheckSquare,
  Sparkles,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  Wrench,
} from 'lucide-react'

interface NavItem {
  id: string
  label: string
  subtitle?: string
  icon: React.FC<{ className?: string }>
  action: () => void
  highlight?: boolean
  badge?: number
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
  const [showAdvancedNav, setShowAdvancedNav] = useState<boolean>(false)

  // 4 Simple Core Actions for any user
  const primaryItems: NavItem[] = [
    {
      id: 'dashboard',
      label: 'Inicio · Mi Proyecto',
      subtitle: 'Resumen y avances de hoy',
      icon: Home,
      action: () => onSelectSection('dashboard'),
    },
    {
      id: 'sprint',
      label: 'Nueva Tarea / Sprint',
      subtitle: 'Pedir un cambio paso a paso',
      icon: Sparkles,
      action: onOpenSprintModal,
      highlight: true,
    },
    {
      id: 'chat',
      label: 'Hablar con Asistente IA',
      subtitle: 'Chat directo de ayuda',
      icon: MessageSquare,
      action: () => onSelectSection('chat'),
    },
    {
      id: 'gates',
      label: 'Mis Aprobaciones',
      subtitle: pendingGatesCount > 0 ? `${pendingGatesCount} esperando tu OK` : 'Sin pendientes',
      icon: ShieldCheck,
      action: () => onSelectSection('gates'),
      badge: pendingGatesCount > 0 ? pendingGatesCount : undefined,
    },
  ]

  // Advanced / Technical Views tucked neatly under a collapsible drawer
  const advancedItems: NavItem[] = [
    { id: 'jira', label: 'Tablero de Tareas (Jira)', icon: CheckSquare, action: () => onSelectSection('jira') },
    { id: 'designer', label: 'Mapa Visual del Flujo', icon: GitBranch, action: () => onSelectSection('designer') },
    { id: 'agents', label: 'Equipo de Agentes IA', icon: Bot, action: () => onSelectSection('agents') },
    { id: 'projects', label: 'Carpetas y Proyectos', icon: Folder, action: () => onSelectSection('projects') },
    { id: 'connections', label: 'Conexiones del Sistema', icon: Key, action: () => onSelectSection('connections') },
    { id: 'email', label: 'Avisos por Correo', icon: Mail, action: () => onSelectSection('email') },
    { id: 'database', label: 'Historial y Base de Datos', icon: BarChart2, action: () => onSelectSection('database') },
    { id: 'github', label: 'Ajustes y GitHub', icon: Settings, action: () => onSelectSection('github') },
  ]

  const jobsCount = dbStats?.jobs ?? 0
  const runsCount = dbStats?.runs ?? 0
  const eventsCount = dbStats?.events ?? 0

  return (
    <>
      <aside className="hidden md:flex w-64 border-r border-zinc-800/80 bg-[#09090b] flex-col justify-between shrink-0 p-4 select-none overflow-y-auto custom-scroll">
        <div className="space-y-6">
          {/* Primary CTA Button */}
          <button
            type="button"
            onClick={onOpenSprintModal}
            className="w-full py-3 px-4 rounded-2xl bg-white hover:bg-zinc-200 text-black font-extrabold text-xs flex items-center justify-center gap-2 shadow-lg transition cursor-pointer active:scale-[0.99]"
          >
            <Sparkles className="w-4 h-4 text-black" />
            <span>+ Crear Nueva Tarea</span>
          </button>

          {/* Main 4 Navigation Items */}
          <nav className="space-y-1.5">
            <div className="px-2 pb-1 text-[10px] font-mono uppercase tracking-wider text-zinc-500 font-bold">
              Menú Principal
            </div>
            {primaryItems.map((item) => {
              const Icon = item.icon
              const isActive =
                currentSection === item.id ||
                (item.id === 'gates' && currentSection === 'executions')

              return (
                <button
                  key={item.id}
                  id={`nav-${item.id}`}
                  onClick={item.action}
                  className={`w-full flex items-center justify-between p-2.5 rounded-2xl text-left transition-all cursor-pointer group ${
                    isActive
                      ? 'bg-zinc-900 text-white border border-white/80 shadow-sm'
                      : 'text-zinc-300 hover:text-white hover:bg-zinc-900/60 border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div
                      className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 transition ${
                        isActive
                          ? 'bg-white text-black'
                          : 'bg-zinc-900 border border-zinc-800 text-zinc-300 group-hover:text-white'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="min-w-0">
                      <div className="text-xs font-bold truncate">{item.label}</div>
                      {item.subtitle && (
                        <div className="text-[10px] text-zinc-400 truncate">{item.subtitle}</div>
                      )}
                    </div>
                  </div>

                  {item.badge !== undefined && (
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-extrabold bg-amber-400 text-black shrink-0">
                      {item.badge}
                    </span>
                  )}
                </button>
              )
            })}
          </nav>

          {/* Collapsible Technical Tools Drawer */}
          <div className="pt-2 border-t border-zinc-850 space-y-2">
            <button
              type="button"
              onClick={() => setShowAdvancedNav(!showAdvancedNav)}
              className="w-full flex items-center justify-between px-2.5 py-2 rounded-xl text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/40 text-xs font-medium transition cursor-pointer"
            >
              <span className="flex items-center gap-2">
                <Wrench className="w-3.5 h-3.5 text-zinc-500" />
                <span>Herramientas Avanzadas</span>
              </span>
              {showAdvancedNav ? (
                <ChevronUp className="w-3.5 h-3.5" />
              ) : (
                <ChevronDown className="w-3.5 h-3.5" />
              )}
            </button>

            {showAdvancedNav && (
              <div className="space-y-1 pl-1 animate-fade-in">
                {advancedItems.map((item) => {
                  const Icon = item.icon
                  const isActive =
                    currentSection === item.id ||
                    (item.id === 'designer' && currentSection === 'roadmap') ||
                    (item.id === 'database' && currentSection === 'reports') ||
                    (item.id === 'github' && currentSection === 'settings')

                  return (
                    <button
                      key={item.id}
                      id={`nav-${item.id}`}
                      onClick={item.action}
                      className={`w-full flex items-center gap-2.5 px-2.5 py-2 rounded-xl text-xs transition cursor-pointer ${
                        isActive
                          ? 'bg-white text-black font-bold'
                          : 'text-zinc-400 hover:text-white hover:bg-zinc-900/60'
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5 shrink-0" />
                      <span className="truncate">{item.label}</span>
                    </button>
                  )
                })}
              </div>
            )}
          </div>
        </div>

        {/* Simple Local Storage Reassurance Footer */}
        <div className="mt-6 pt-3 border-t border-zinc-800/80">
          <div
            onClick={() => setShowDbInfoModal(true)}
            className="p-3 rounded-2xl bg-zinc-950 border border-zinc-800/90 hover:border-zinc-700 transition cursor-pointer space-y-1.5"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5 text-[11px] font-bold text-zinc-200">
                <Database className="w-3.5 h-3.5 text-emerald-400" />
                <span>Memoria Local Activa</span>
              </div>
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
            </div>
            <p className="text-[10px] text-zinc-400 leading-snug">
              {jobsCount} tareas y {eventsCount} registros guardados en tu PC.
            </p>
          </div>
        </div>
      </aside>

      {/* Simple Modal Explaining Local Storage */}
      {showDbInfoModal && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in"
          onClick={() => setShowDbInfoModal(false)}
        >
          <div
            className="bg-zinc-950 border border-zinc-800 rounded-3xl max-w-md w-full p-6 space-y-4 shadow-2xl text-left"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <div className="flex items-center gap-2.5">
                <Database className="w-5 h-5 text-emerald-400" />
                <h3 className="text-sm font-bold text-white">Tu Caja Fuerte de Datos Local</h3>
              </div>
              <button
                type="button"
                onClick={() => setShowDbInfoModal(false)}
                className="w-7 h-7 rounded-xl bg-zinc-900 text-zinc-400 hover:text-white flex items-center justify-center cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-zinc-300 leading-relaxed">
              Toda la información de tus proyectos se guarda directamente en tu computadora en el archivo privado <code className="text-white font-mono">sacl_ops.db</code>. Nadie externo tiene acceso a tus tareas ni aprobaciones.
            </p>

            <div className="grid grid-cols-3 gap-2 text-center font-mono text-xs">
              <div className="p-2.5 rounded-xl bg-zinc-900 border border-zinc-800">
                <span className="text-[10px] text-zinc-400 block">Tareas</span>
                <span className="text-white font-bold text-sm">{jobsCount}</span>
              </div>
              <div className="p-2.5 rounded-xl bg-zinc-900 border border-zinc-800">
                <span className="text-[10px] text-zinc-400 block">Corridas</span>
                <span className="text-white font-bold text-sm">{runsCount}</span>
              </div>
              <div className="p-2.5 rounded-xl bg-zinc-900 border border-zinc-800">
                <span className="text-[10px] text-zinc-400 block">Historial</span>
                <span className="text-white font-bold text-sm">{eventsCount}</span>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => {
                  setShowDbInfoModal(false)
                  onSelectSection('database')
                }}
                className="px-4 py-2 rounded-xl bg-white text-black text-xs font-bold cursor-pointer"
              >
                Ver Historial Completo
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
