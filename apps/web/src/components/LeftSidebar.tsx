import React, { useState } from 'react'

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
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false)

  const navItems = [
    {
      id: 'projects',
      label: 'Proyectos Locales',
      subtitle: `${projectsCount} vinculado(s)`,
      icon: (className: string) => (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
          <path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z" />
          <circle cx="12" cy="13" r="2" />
        </svg>
      ),
    },
    {
      id: 'chat',
      label: 'Chat de Planeación',
      subtitle: 'Comandos CQRS e IoC',
      icon: (className: string) => (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          <path d="M8 9h8" />
          <path d="M8 13h6" />
        </svg>
      ),
    },
    {
      id: 'workflows',
      label: 'Skills Importer',
      subtitle: 'SKILL.md & Manifiestos',
      icon: (className: string) => (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="12 2 2 7 12 12 22 7 12 2Universal" />
          <polyline points="2 17 12 22 22 17" />
          <polyline points="2 12 12 17 22 12" />
        </svg>
      ),
    },
    {
      id: 'connections',
      label: 'Tecnologías Locales',
      subtitle: 'Credenciales en Backend',
      icon: (className: string) => (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="7.5" cy="15.5" r="5.5" />
          <path d="m21 2-9.6 9.6" />
          <path d="m15.5 7.5 3 3L22 7l-3-3" />
        </svg>
      ),
    },
    {
      id: 'dashboard',
      label: 'Monitoreo en Tiempo Real',
      subtitle: 'Control Loop & Telemetría',
      icon: (className: string) => (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
          <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
        </svg>
      ),
      badge: pendingGatesCount > 0 ? pendingGatesCount : undefined,
    },
    {
      id: 'settings',
      label: 'Configuración / Git',
      subtitle: 'Daemon antigravity & WAL',
      icon: (className: string) => (
        <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="3" />
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
        </svg>
      ),
    },
  ]

  return (
    <aside
      id="left-sidebar-navigation"
      className={`border-r border-white/8 bg-[#000000] flex flex-col justify-between shrink-0 select-none h-screen transition-all duration-200 z-30 ${
        isCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Top Header & Navigation */}
      <div className="flex flex-col h-full overflow-hidden">
        {/* Brand & Collapse Header */}
        <div className="h-14 border-b border-white/8 px-3.5 flex items-center justify-between shrink-0">
          {!isCollapsed && (
            <div className="flex items-center gap-2.5 overflow-hidden">
              <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse shrink-0" />
              <div className="truncate">
                <span className="text-xs font-semibold tracking-wider text-white uppercase block leading-none">
                  SolidBit EOP
                </span>
                <span className="text-[10px] text-zinc-500 font-mono tracking-tight block mt-1">
                  Control Plane v1.0
                </span>
              </div>
            </div>
          )}
          <button
            type="button"
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 rounded bg-[#0a0a0a] hover:bg-zinc-900 border border-white/8 text-zinc-400 hover:text-white transition cursor-pointer ml-auto"
            title={isCollapsed ? 'Expandir menú' : 'Colapsar menú'}
            aria-label="Toggle Sidebar"
          >
            <svg
              className="w-4 h-4"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              {isCollapsed ? (
                <>
                  <rect width="18" height="18" x="3" y="3" rx="2" />
                  <path d="M9 3v18" />
                  <path d="m14 15 3-3-3-3" />
                </>
              ) : (
                <>
                  <rect width="18" height="18" x="3" y="3" rx="2" />
                  <path d="M9 3v18" />
                  <path d="m16 9-3 3 3 3" />
                </>
              )}
            </svg>
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="p-2 space-y-1 overflow-y-auto flex-1">
          {navItems.map((item) => {
            const isActive =
              currentSection === item.id ||
              (item.id === 'dashboard' && (currentSection === 'executions' || currentSection === 'database'))
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onSelectSection(item.id)}
                className={`w-full text-left rounded p-2.5 flex items-center transition border ${
                  isActive
                    ? 'bg-[#0a0a0a] border-white/20 text-white'
                    : 'bg-transparent border-transparent text-zinc-400 hover:text-zinc-200 hover:bg-[#0a0a0a] hover:border-white/8'
                } ${isCollapsed ? 'justify-center' : 'justify-between'}`}
                title={isCollapsed ? item.label : undefined}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div
                    className={`shrink-0 ${
                      isActive ? 'text-emerald-400' : 'text-zinc-400 group-hover:text-zinc-200'
                    }`}
                  >
                    {item.icon('w-4 h-4')}
                  </div>
                  {!isCollapsed && (
                    <div className="truncate text-left">
                      <div className="text-xs font-medium truncate leading-tight">{item.label}</div>
                      <div className="text-[10px] text-zinc-500 font-mono truncate leading-none mt-1">
                        {item.subtitle}
                      </div>
                    </div>
                  )}
                </div>

                {!isCollapsed && item.badge !== undefined && item.badge > 0 && (
                  <span className="ml-2 px-1.5 py-0.5 text-[10px] font-mono font-bold rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 shrink-0">
                    {item.badge}
                  </span>
                )}
              </button>
            )
          })}
        </nav>

        {/* Footer Status Pill */}
        <div className="p-3 border-t border-white/8 bg-[#000000] shrink-0">
          {isCollapsed ? (
            <div className="flex justify-center" title="Daemon antigravity conectado">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
            </div>
          ) : (
            <div className="bg-[#0a0a0a] border border-white/8 rounded p-2 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shrink-0" />
                <span className="text-[11px] text-zinc-300 font-mono">CLI Daemon :8765</span>
              </div>
              <span className="text-[9px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-1 py-0.5 rounded">
                EDA OK
              </span>
            </div>
          )}
        </div>
      </div>
    </aside>
  )
}
