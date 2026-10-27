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
  CheckSquare,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  SlidersHorizontal,
  Layers,
} from 'lucide-react'

interface NavItem {
  id: string
  label: string
  subtitle?: string
  icon: React.FC<{ className?: string }>
  action: () => void
  badge?: number
}

interface LeftSidebarProps {
  currentSection: string
  onSelectSection: (section: string) => void
  pendingGatesCount?: number
  projectsCount?: number
}

export const LeftSidebar: React.FC<LeftSidebarProps> = ({
  currentSection,
  onSelectSection,
  pendingGatesCount = 0,
  projectsCount = 1,
}) => {
  const [showSupportChannels, setShowSupportChannels] = useState<boolean>(false)

  // FASE 1 (OOUX & MECE): 5 Mutually Exclusive Canonical Domain Entities
  const canonicalDomainEntities: NavItem[] = [
    {
      id: 'dashboard',
      label: '1. Sprint Actual',
      subtitle: 'Flujo operativo y estado',
      icon: Home,
      action: () => onSelectSection('dashboard'),
      badge: pendingGatesCount > 0 ? pendingGatesCount : undefined,
    },
    {
      id: 'projects',
      label: '2. Proyectos',
      subtitle: `${projectsCount} ${projectsCount === 1 ? 'carpeta vinculada' : 'carpetas vinculadas'}`,
      icon: Folder,
      action: () => onSelectSection('projects'),
    },
    {
      id: 'roadmap',
      label: '3. Mapa de Flujo',
      subtitle: 'Secuencia de etapas y tareas',
      icon: GitBranch,
      action: () => onSelectSection('roadmap'),
    },
    {
      id: 'agents',
      label: '4. Equipo de Asistentes',
      subtitle: 'Especialistas y pruebas',
      icon: Bot,
      action: () => onSelectSection('agents'),
    },
    {
      id: 'executions',
      label: '5. Aprobaciones',
      subtitle:
        pendingGatesCount > 0
          ? `${pendingGatesCount} esperando autorización`
          : 'Decisiones e historial',
      icon: ShieldCheck,
      action: () => onSelectSection('executions'),
      badge: pendingGatesCount > 0 ? pendingGatesCount : undefined,
    },
  ]

  // Layer 2 / Auxiliary Channels & Configuration (Progressive Disclosure)
  const supportChannels: NavItem[] = [
    {
      id: 'jira',
      label: 'Requerimientos y Tareas',
      icon: CheckSquare,
      action: () => onSelectSection('jira'),
    },
    {
      id: 'connections',
      label: 'Conexiones del Sistema',
      icon: Key,
      action: () => onSelectSection('connections'),
    },
    {
      id: 'email',
      label: 'Notificaciones por Correo',
      icon: Mail,
      action: () => onSelectSection('email'),
    },
    {
      id: 'chat',
      label: 'Asistente de Consulta',
      icon: MessageSquare,
      action: () => onSelectSection('chat'),
    },
    {
      id: 'workflows',
      label: 'Catálogo de Flujos',
      icon: Layers,
      action: () => onSelectSection('workflows'),
    },
    {
      id: 'database',
      label: 'Registro de Actividad',
      icon: BarChart2,
      action: () => onSelectSection('database'),
    },
    {
      id: 'github',
      label: 'Perfil y Sincronización',
      icon: Settings,
      action: () => onSelectSection('github'),
    },
  ]

  return (
    <aside className="hidden md:flex w-64 border-r border-zinc-850 bg-[#09090b] flex-col justify-between shrink-0 p-4 select-none overflow-y-auto custom-scroll">
      <div className="space-y-6">
        {/* Canonical 5 OOUX Domain Entities (Zero duplicated action buttons — Invariant 2) */}
        <nav className="space-y-1.5" aria-label="Entidades del Dominio">
          <div className="px-2.5 pb-1.5 text-[10px] font-mono uppercase tracking-wider text-zinc-500 font-bold">
            Entidades de Trabajo (OOUX)
          </div>
          {canonicalDomainEntities.map((item) => {
            const Icon = item.icon
            const isActive =
              currentSection === item.id ||
              (item.id === 'roadmap' && currentSection === 'designer') ||
              (item.id === 'executions' && currentSection === 'gates')

            return (
              <button
                key={item.id}
                id={`nav-${item.id}`}
                type="button"
                onClick={item.action}
                className={`w-full flex items-center justify-between p-2.5 rounded-2xl text-left transition-all cursor-pointer group ${
                  isActive
                    ? 'bg-zinc-900 text-white border border-zinc-700 shadow-sm'
                    : 'text-zinc-300 hover:text-white hover:bg-zinc-900/50 border border-transparent'
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

        {/* Progressive Disclosure: Auxiliary Channels & System Configuration */}
        <div className="pt-3 border-t border-zinc-850 space-y-2">
          <button
            type="button"
            onClick={() => setShowSupportChannels(!showSupportChannels)}
            className="w-full flex items-center justify-between px-2.5 py-2 rounded-xl text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/40 text-xs font-medium transition cursor-pointer"
          >
            <span className="flex items-center gap-2">
              <SlidersHorizontal className="w-3.5 h-3.5 text-zinc-500" />
              <span>Canales y Configuración</span>
            </span>
            {showSupportChannels ? (
              <ChevronUp className="w-3.5 h-3.5" />
            ) : (
              <ChevronDown className="w-3.5 h-3.5" />
            )}
          </button>

          {showSupportChannels && (
            <div className="space-y-1 pl-1 animate-fade-in">
              {supportChannels.map((item) => {
                const Icon = item.icon
                const isActive =
                  currentSection === item.id ||
                  (item.id === 'database' && currentSection === 'reports') ||
                  (item.id === 'github' && currentSection === 'settings')

                return (
                  <button
                    key={item.id}
                    id={`nav-${item.id}`}
                    type="button"
                    onClick={item.action}
                    className={`w-full flex items-center gap-2.5 px-2.5 py-2 rounded-xl text-xs transition cursor-pointer ${
                      isActive
                        ? 'bg-zinc-900 text-white font-bold border border-zinc-700'
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

      {/* Clean Mental-Model Footer (Zero DB engine/protocol leaks in Layer 1) */}
      <div className="mt-6 pt-3 border-t border-zinc-850">
        <button
          type="button"
          onClick={() => onSelectSection('connections')}
          className="w-full p-3 rounded-2xl bg-zinc-950 hover:bg-zinc-900/80 border border-zinc-850 transition cursor-pointer text-left space-y-1"
        >
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-zinc-200">Entorno Privado en tu PC</span>
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
          </div>
          <p className="text-[10px] text-zinc-400 leading-snug">
            Tus proyectos y autorizaciones se procesan directamente en este equipo.
          </p>
        </button>
      </div>
    </aside>
  )
}
