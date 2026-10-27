import React from 'react'
import {
  Home,
  MessageSquare,
  Sparkles,
  CheckSquare,
  Menu,
} from 'lucide-react'

interface MobileBottomNavProps {
  currentSection: string
  onSelectSection: (section: string) => void
  onOpenDrawer: () => void
  onOpenSprintModal: () => void
  hasPendingGate?: boolean
}

export const MobileBottomNav: React.FC<MobileBottomNavProps> = ({
  currentSection,
  onSelectSection,
  onOpenDrawer,
  onOpenSprintModal,
  hasPendingGate = false,
}) => {
  const isTabActive = (tabId: string) => {
    if (tabId === 'dashboard') return currentSection === 'dashboard'
    if (tabId === 'jira') return currentSection === 'jira'
    if (tabId === 'chat') return currentSection === 'chat'
    return false
  }

  return (
    <div className="fixed bottom-0 inset-x-0 z-40 md:hidden bg-zinc-950/95 backdrop-blur-md border-t border-zinc-800 px-2 py-1 flex items-center justify-around h-16 safe-area-pb">
      {/* 1. Inicio */}
      <button
        id="bottom-nav-dashboard"
        onClick={() => onSelectSection('dashboard')}
        className={`flex flex-col items-center justify-center w-14 py-1 rounded-xl transition cursor-pointer ${
          isTabActive('dashboard')
            ? 'text-white font-bold'
            : 'text-zinc-400 hover:text-white'
        }`}
      >
        <Home className="w-5 h-5" />
        <span className="text-[10px] mt-0.5">Inicio</span>
      </button>

      {/* 2. Jira Backlog */}
      <button
        id="bottom-nav-jira"
        onClick={() => onSelectSection('jira')}
        className={`flex flex-col items-center justify-center w-14 py-1 rounded-xl transition cursor-pointer ${
          isTabActive('jira')
            ? 'text-white font-bold'
            : 'text-zinc-400 hover:text-white'
        }`}
      >
        <CheckSquare className="w-5 h-5" />
        <span className="text-[10px] mt-0.5">Jira</span>
      </button>

      {/* 3. Diseñar Sprint (Primary Action) */}
      <button
        id="bottom-nav-sprint"
        onClick={onOpenSprintModal}
        className="flex flex-col items-center justify-center w-14 py-1 rounded-xl text-white transition cursor-pointer relative"
        title="Diseñar Sprint"
      >
        <div className="w-8 h-8 rounded-full bg-white text-black flex items-center justify-center shadow-lg shadow-white/10">
          <Sparkles className="w-4 h-4 fill-black" />
        </div>
        <span className="text-[9px] mt-0.5 font-bold text-white">Sprint</span>
      </button>

      {/* 4. Chat IA (AGY) */}
      <button
        id="bottom-nav-chat"
        onClick={() => onSelectSection('chat')}
        className={`flex flex-col items-center justify-center w-14 py-1 rounded-xl relative transition cursor-pointer ${
          isTabActive('chat')
            ? 'text-white font-bold'
            : 'text-zinc-400 hover:text-white'
        }`}
      >
        <MessageSquare className="w-5 h-5" />
        <span className="text-[10px] mt-0.5">Chat IA</span>
      </button>

      {/* 5. Menú Completo */}
      <button
        id="bottom-nav-menu"
        onClick={onOpenDrawer}
        className="flex flex-col items-center justify-center w-14 py-1 rounded-xl text-zinc-400 hover:text-white transition cursor-pointer relative"
      >
        {hasPendingGate && (
          <span className="absolute top-1 right-3 w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
        )}
        <Menu className="w-5 h-5" />
        <span className="text-[10px] mt-0.5">Menú</span>
      </button>
    </div>
  )
}
