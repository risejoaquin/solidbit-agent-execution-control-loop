import React from 'react'

interface MobileBottomNavProps {
  currentSection: string
  onSelectSection: (section: string) => void
  onOpenDrawer: () => void
  hasPendingGate?: boolean
}

export const MobileBottomNav: React.FC<MobileBottomNavProps> = ({
  currentSection,
  onSelectSection,
  onOpenDrawer,
  hasPendingGate = false,
}) => {
  const isTabActive = (tabId: string) => {
    if (tabId === 'dashboard') return currentSection === 'dashboard' || currentSection === 'executions'
    if (tabId === 'projects') return currentSection === 'projects'
    if (tabId === 'chat') return currentSection === 'chat'
    if (tabId === 'workflows') return currentSection === 'workflows' || currentSection === 'skills'
    return false
  }

  return (
    <div className="fixed bottom-0 inset-x-0 z-40 md:hidden bg-[#0a0a0a] border-t border-white/8 px-2 py-1 flex items-center justify-around h-14 safe-area-pb">
      {/* 1. Proyectos */}
      <button
        id="bottom-nav-projects"
        type="button"
        onClick={() => onSelectSection('projects')}
        className={`flex flex-col items-center justify-center w-14 py-1 rounded transition ${
          isTabActive('projects') ? 'text-white font-medium' : 'text-zinc-500 hover:text-zinc-300'
        }`}
      >
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
          <path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z" />
        </svg>
        <span className="text-[10px] mt-0.5 leading-none">Proyectos</span>
      </button>

      {/* 2. Chat */}
      <button
        id="bottom-nav-chat"
        type="button"
        onClick={() => onSelectSection('chat')}
        className={`flex flex-col items-center justify-center w-14 py-1 rounded transition ${
          isTabActive('chat') ? 'text-white font-medium' : 'text-zinc-500 hover:text-zinc-300'
        }`}
      >
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
        <span className="text-[10px] mt-0.5 leading-none">Chat</span>
      </button>

      {/* 3. Monitoreo (Dashboard) */}
      <button
        id="bottom-nav-dashboard"
        type="button"
        onClick={() => onSelectSection('dashboard')}
        className={`flex flex-col items-center justify-center w-14 py-1 rounded relative transition ${
          isTabActive('dashboard') ? 'text-white font-medium' : 'text-zinc-500 hover:text-zinc-300'
        }`}
      >
        {hasPendingGate && (
          <span className="absolute top-1 right-3 w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
        )}
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
          <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
        </svg>
        <span className="text-[10px] mt-0.5 leading-none">Control</span>
      </button>

      {/* 4. Skills */}
      <button
        id="bottom-nav-workflows"
        type="button"
        onClick={() => onSelectSection('workflows')}
        className={`flex flex-col items-center justify-center w-14 py-1 rounded transition ${
          isTabActive('workflows') ? 'text-white font-medium' : 'text-zinc-500 hover:text-zinc-300'
        }`}
      >
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="12 2 2 7 12 12 22 7 12 2Universal" />
          <polyline points="2 12 12 17 22 12" />
        </svg>
        <span className="text-[10px] mt-0.5 leading-none">Skills</span>
      </button>

      {/* 5. Menú Completo (Drawer EOP con las 6 rutas) */}
      <button
        id="bottom-nav-menu"
        type="button"
        onClick={onOpenDrawer}
        className="flex flex-col items-center justify-center w-14 py-1 rounded text-zinc-500 hover:text-zinc-300 transition"
        aria-label="Abrir menú EOP"
      >
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
          <line x1="4" x2="20" y1="12" y2="12" />
          <line x1="4" x2="20" y1="6" y2="6" />
          <line x1="4" x2="20" y1="18" y2="18" />
        </svg>
        <span className="text-[10px] mt-0.5 leading-none">Más</span>
      </button>
    </div>
  )
}
