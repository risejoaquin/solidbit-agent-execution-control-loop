import React, { useState } from 'react'
import {
  PanelLeftClose,
  PanelLeft,
  Zap,
  FolderGit2,
  GitBranch,
  Bot,
  ShieldCheck,
  CheckSquare,
  Key,
  Mail,
  MessageSquare,
  Layers,
  BarChart2,
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
  const [showSupportChannels, setShowSupportChannels] = useState<boolean>(false)
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false)

  // OOUX: Entidades canónicas interconectadas (sin prefijos numéricos rígidos)
  const canonicalDomainEntities: NavItem[] = [
    {
      id: 'dashboard',
      label: t('Sprint Activo', 'Active Sprint'),
      subtitle: t('Centro de control del pipeline', 'Pipeline mission control'),
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
      id: 'roadmap',
      label: t('Mapa de Flujo DAG', 'DAG Workflow Map'),
      subtitle: t('Secuencia de etapas y barreras', 'Stages & topological barriers'),
      icon: GitBranch,
      action: () => onSelectSection('roadmap'),
    },
    {
      id: 'agents',
      label: t('Escuadrón de Agentes', 'Agent Squad'),
      subtitle: t('Especialistas e interacción', 'Specialists & live interaction'),
      icon: Bot,
      action: () => onSelectSection('agents'),
    },
    {
      id: 'executions',
      label: t('Aprobaciones & Auditoría', 'Approvals & Audit'),
      subtitle:
        pendingGatesCount > 0
          ? `${pendingGatesCount} ${t('pendientes de firma', 'pending signature')}`
          : t('Decisiones HITL e historial', 'HITL decisions & history'),
      icon: ShieldCheck,
      action: () => onSelectSection('executions'),
      badge: pendingGatesCount > 0 ? pendingGatesCount : undefined,
    },
  ]

  // Canales auxiliares y de soporte (Progressive Disclosure)
  const supportChannels: NavItem[] = [
    {
      id: 'jira',
      label: t('Backlog & Requerimientos', 'Backlog & Requirements'),
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
      label: t('Notificaciones & Resend', 'Notifications & Resend'),
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
      label: t('Contratos SolidBit', 'SolidBit Contracts'),
      icon: Layers,
      action: () => onSelectSection('workflows'),
    },
    {
      id: 'database',
      label: t('Auditoría SQLite WAL', 'SQLite WAL Audit'),
      icon: BarChart2,
      action: () => onSelectSection('database'),
    },
    {
      id: 'github',
      label: t('Configuración & Sync', 'Settings & Sync'),
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
              {t('Navegación', 'Navigation')}
            </span>
          )}
          <button
            type="button"
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-850 text-zinc-400 hover:text-white transition cursor-pointer ml-auto"
            title={isCollapsed ? t('Expandir menú', 'Expand menu') : t('Colapsar menú', 'Collapse menu')}
          >
            {isCollapsed ? <PanelLeft className="w-3.5 h-3.5" /> : <PanelLeftClose className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* 5 Entidades Principales */}
        <nav className="space-y-1">
          {canonicalDomainEntities.map((item) => {
            const isActive = currentSection === item.id
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

        {/* Canales Secundarios / Herramientas de Soporte */}
        <div className="pt-2 border-t border-white/5 space-y-1">
          <button
            type="button"
            onClick={() => setShowSupportChannels(!showSupportChannels)}
            className="w-full flex items-center justify-between p-2 rounded-xl text-left text-zinc-400 hover:text-white hover:bg-zinc-900/40 transition cursor-pointer"
          >
            <span className="text-[10px] font-mono uppercase tracking-wider text-zinc-500 font-bold">
              {t('Herramientas Auxiliares', 'Auxiliary Tools')}
            </span>
            {showSupportChannels ? (
              <ChevronUp className="w-3.5 h-3.5 text-zinc-500" />
            ) : (
              <ChevronDown className="w-3.5 h-3.5 text-zinc-500" />
            )}
          </button>

          {showSupportChannels && (
            <div className="space-y-0.5 pt-1 animate-fade-in">
              {supportChannels.map((item) => {
                const isActive = currentSection === item.id
                const IconComponent = item.icon
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={item.action}
                    className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-left text-xs transition cursor-pointer ${
                      isActive
                        ? 'bg-zinc-800 text-white font-bold'
                        : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/50'
                    }`}
                  >
                    <IconComponent className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
                    <span className="truncate">{item.label}</span>
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
            <span className="text-zinc-500 uppercase">Motor SACL</span>
            <span className="text-emerald-400 font-bold flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              v1.0 WAL
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
