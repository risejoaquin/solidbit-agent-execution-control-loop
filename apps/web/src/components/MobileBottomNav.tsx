import React from 'react'
import {
  Home,
  MessageSquare,
  GitBranch,
  PlayCircle,
  Menu,
} from 'lucide-react'

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
  hasPendingGate = true,
}) => {
  const isTabActive = (tabId: string) => {
    if (tabId === 'dashboard') return currentSection === 'dashboard'
    if (tabId === 'chat') return currentSection === 'chat'
    if (tabId === 'designer') return currentSection === 'designer' || currentSection === 'roadmap'
    if (tabId === 'gates') return currentSection === 'gates' || currentSection === 'executions'
    return false
  }

  return (
    <div className="fixed bottom-0 inset-x-0 z-40 md:hidden bg-[#0a0f16]/95 backdrop-blur-md border-t border-zinc-800 px-2 py-1 flex items-center justify-around h-16 safe-area-pb">
      {/* 1. Inicio */}
      <button
        id="bottom-nav-dashboard"
        onClick={() => onSelectSection('dashboard')}
        className={`flex flex-col items-center justify-center w-14 py-1 rounded-xl transition ${
          isTabActive('dashboard')
            ? 'text-white font-bold font-bold'
            : 'text-zinc-400 hover:text-white'
        }`}
      >
        <Home className="w-5 h-5" />
        <span className="text-[10px] mt-0.5">Inicio</span>
      </button>

      {/* 2. Chat IA (AGY) */}
      <button
        id="bottom-nav-chat"
        onClick={() => onSelectSection('chat')}
        className={`flex flex-col items-center justify-center w-14 py-1 rounded-xl relative transition ${
          isTabActive('chat')
            ? 'text-white font-bold font-bold'
            : 'text-zinc-400 hover:text-white'
        }`}
      >
        <span className="absolute top-1 right-3 w-2 h-2 rounded-full bg-white ring-2 ring-[#0a0f16] animate-pulse" />
        <MessageSquare className="w-5 h-5" />
        <span className="text-[10px] mt-0.5">Chat IA</span>
      </button>

      {/* 3. Roadmap */}
      <button
        id="bottom-nav-designer"
        onClick={() => onSelectSection('designer')}
        className={`flex flex-col items-center justify-center w-14 py-1 rounded-xl transition ${
          isTabActive('designer')
            ? 'text-white font-bold font-bold'
            : 'text-zinc-400 hover:text-white'
        }`}
      >
        <GitBranch className="w-5 h-5" />
        <span className="text-[10px] mt-0.5">Roadmap</span>
      </button>

      {/* 4. Ejecuciones (HITL) */}
      <button
        id="bottom-nav-gates"
        onClick={() => onSelectSection('gates')}
        className={`flex flex-col items-center justify-center w-14 py-1 rounded-xl relative transition ${
          isTabActive('gates')
            ? 'text-white font-bold font-bold'
            : 'text-zinc-400 hover:text-white'
        }`}
      >
        {hasPendingGate && (
          <span className="absolute top-1 right-3 w-2 h-2 rounded-full bg-amber-400 ring-2 ring-[#0a0f16] animate-pulse" />
        )}
        <PlayCircle className="w-5 h-5" />
        <span className="text-[10px] mt-0.5">Ejecutar</span>
      </button>

      {/* 5. Menú Completo */}
      <button
        id="bottom-nav-menu"
        onClick={onOpenDrawer}
        className="flex flex-col items-center justify-center w-14 py-1 rounded-xl text-zinc-400 hover:text-white transition cursor-pointer"
      >
        <Menu className="w-5 h-5" />
        <span className="text-[10px] mt-0.5">Menú</span>
      </button>
    </div>
  )
}
