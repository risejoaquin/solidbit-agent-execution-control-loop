import React, { useState } from 'react'
import {
  PanelLeftClose,
  PanelLeft,
  Zap,
  FolderGit2,
  Database,
  ShieldCheck,
  Bot,
  CheckSquare,
  Key,
  Mail,
  MessageSquare,
  Layers,
  Settings,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'
import { useLanguage } from '../context/LanguageContext'

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
  const { t } = useLanguage()
  const [showAdvancedTools, setShowAdvancedTools] = useState<boolean>(false)
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false)

  // Navegación Principal Estricta SolidBit KISS (3 Entidades Nucleares)
  const primaryDomainEntities: NavItem[] = [
    {
      id: 'dashboard',
      label: t('Sprint Activo (Flujo 3 Fases)', 'Active Sprint (3 Phases)'),
      subtitle: t('Diseñar → Implementar → Subir', 'Design → Implement → Deploy'),
      icon: Zap,
      action: () => onSelectSection('dashboard'),
      badge: pendingGatesCount > 0 ? pendingGatesCount : undefined,
    },
    {
      id: 'projects',
      label: t('Proyectos & Repositorios', 'Projects & Repositories'),
      subtitle: `${projectsCount} ${
        projectsCount === 1
          ? t('repositorio vinculado', 'linked repository')
          : t('repositorios vinculados', 'linked repositories')
      }`,
      icon: FolderGit2,
      action: () => onSelectSection('projects'),
    },
    {
      id: 'database',
      label: t('Auditoría Base de Datos', 'Database Audit'),
      subtitle: t('sacl_ops.db · SQLite WAL', 'sacl_ops.db · SQLite WAL'),
      icon: Database,
      action: () => onSelectSection('database'),
    },
  ]

  // Carpeta de "Herramientas Avanzadas" (Colapsable)
  const advancedTools: NavItem[] = [
    {
      id: 'executions',
      label: t('Aprobaciones Humanas', 'Human Approvals'),
      icon: ShieldCheck,
      action: () => onSelectSection('executions'),
      badge: pendingGatesCount > 0 ? pendingGatesCount : undefined,
    },
    {
      id: 'agents',
      label: t('Escuadrón de Agentes', 'Agent Squad'),
      icon: Bot,
      action: () => onSelectSection('agents'),
    },
    {
      id: 'jira',
      label: t('Requerimientos & Backlog', 'Requirements & Backlog'),
      icon: CheckSquare,
      action: () => onSelectSection('jira'),
    },
    {
      id: 'connections',
      label: t('Conexiones de Infraestructura', 'Infrastructure Connections'),
      icon: Key,
      action: () => onSelectSection('connections'),
    },
    {
      id: 'email',
      label: t('Notificaciones Resend', 'Resend Notifications'),
      icon: Mail,
      action: () => onSelectSection('email'),
    },
    {
      id: 'chat',
      label: t('Terminal de Consulta', 'Consultation Terminal'),
      icon: MessageSquare,
      action: () => onSelectSection('chat'),
    },
    {
      id: 'workflows',
      label: t('Catálogo de Flujos / Contratos', 'Flow Catalog / Contracts'),
      icon: Layers,
      action: () => onSelectSection('workflows'),
    },
    {
      id: 'github',
      label: t('Configuración & Git', 'Settings & Git'),
      icon: Settings,
      action: () => onSelectSection('github'),
    },
  ]

  return (
    <aside
      id="left-sidebar-navigation"
      className={`border-r border-white/5 bg-[#0C0C0E] flex flex-col justify-between shrink-0 select-none hidden md:flex h-full transition-all duration-300 ${
        isCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Zona Superior: Entidades Principales */}
      <div className="p-3.5 space-y-4 overflow-y-auto custom-scroll">
        <div className="px-2 pt-1 pb-0.5 flex items-center justify-between">
          {!isCollapsed && (
            <span className="text-[10px] font-mono uppercase tracking-widest text-zinc-500 font-extrabold">
              {t('SolidBit Navegación', 'SolidBit Navigation')}
            </span>
          )}
          <button
            type="button"
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-850 text-zinc-400 hover:text-white transition cursor-pointer ml-auto"
            title={isCollapsed ? t('Expandir menú', 'Expand menu') : t('Colapsar menú', 'Collapse menu')}
          >
            {isCollapsed ? <PanelLeft className="w-3.5 h-3.5 text-emerald-400" /> : <PanelLeftClose className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* 3 Entidades Principales */}
        <nav className="space-y-1">
          {primaryDomainEntities.map((item) => {
            const isActive = currentSection === item.id || (item.id === 'database' && currentSection === 'reports')
            const IconComponent = item.icon
            return (
              <button
                key={item.id}
                type="button"
                id={`nav-item-${item.id}`}
                onClick={item.action}
                className={`w-full flex items-center justify-between p-2.5 rounded-2xl text-left transition-all cursor-pointer group ${
                  isActive
                    ? 'bg-[#18181B] border border-white/10 text-white shadow-lg'
                    : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60 border border-transparent'
                }`}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div
                    className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 transition-colors ${
                      isActive
                        ? 'bg-white text-black font-extrabold shadow-sm'
                        : 'bg-zinc-900 border border-white/5 text-zinc-400 group-hover:text-zinc-200 group-hover:bg-zinc-850'
                    }`}
                  >
                    <IconComponent className="w-4 h-4" />
                  </div>
                  {!isCollapsed && (
                    <div className="min-w-0 leading-tight">
                      <span
                        className={`text-xs block truncate ${
                          isActive ? 'font-bold text-white' : 'font-medium'
                        }`}
                      >
                        {item.label}
                      </span>
                      {item.subtitle && (
                        <span className="text-[10px] text-zinc-500 block truncate mt-0.5 font-mono">
                          {item.subtitle}
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {item.badge !== undefined && (
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 shrink-0 ml-1">
                    {item.badge}
                  </span>
                )}
              </button>
            )
          })}
        </nav>

        {/* Carpeta "Herramientas Avanzadas" (Colapsada por defecto) */}
        <div className="pt-2 border-t border-white/5 space-y-1">
          <button
            type="button"
            onClick={() => setShowAdvancedTools(!showAdvancedTools)}
            className="w-full flex items-center justify-between p-2 rounded-xl text-left text-zinc-400 hover:text-white hover:bg-zinc-900/40 transition cursor-pointer"
          >
            <span className="text-[10px] font-mono uppercase tracking-wider text-zinc-500 font-bold">
              {t('Herramientas Avanzadas', 'Advanced Tools')}
            </span>
            {showAdvancedTools ? (
              <ChevronUp className="w-3.5 h-3.5 text-zinc-500" />
            ) : (
              <ChevronDown className="w-3.5 h-3.5 text-zinc-500" />
            )}
          </button>

          {showAdvancedTools && (
            <div className="space-y-0.5 pt-1 animate-fade-in">
              {advancedTools.map((item) => {
                const isActive = currentSection === item.id
                const IconComponent = item.icon
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={item.action}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-left text-xs transition cursor-pointer ${
                      isActive
                        ? 'bg-zinc-800 text-white font-bold'
                        : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/50'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <IconComponent className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
                      <span className="truncate">{item.label}</span>
                    </div>
                    {item.badge !== undefined && (
                      <span className="px-1.5 py-0.2 rounded-full text-[9px] font-mono font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                        {item.badge}
                      </span>
                    )}
                  </button>
                )
              })}
            </div>
          )}
        </div>
      </div>

      {/* Zona Inferior: Estado del Runtime Local */}
      <div className="p-3 border-t border-white/5 space-y-2">
        <div className="p-2.5 rounded-xl bg-black border border-white/5 space-y-1 font-mono text-[10px]">
          <div className="flex items-center justify-between">
            <span className="text-zinc-500 uppercase">sacl_ops.db</span>
            <span className="text-emerald-400 font-bold flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              SQLite WAL
            </span>
          </div>
          <div className="flex items-center justify-between text-zinc-400">
            <span>Daemon</span>
            <span className="text-zinc-300">127.0.0.1:8765</span>
          </div>
        </div>
      </div>
    </aside>
  )
}
