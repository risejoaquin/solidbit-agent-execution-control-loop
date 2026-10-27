import React from 'react'
import {
  Home,
  Folder,
  GitBranch,
  ShieldCheck,
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
  hasPendingGate = false,
}) => {
  const isTabActive = (tabId: string) => {
    if (tabId === 'dashboard') return currentSection === 'dashboard'
    if (tabId === 'projects') return currentSection === 'projects'
    if (tabId === 'roadmap') return currentSection === 'roadmap' || currentSection === 'designer'
    if (tabId === 'executions') return currentSection === 'executions' || currentSection === 'gates'
    return false
  }

  return (
    <div className="fixed bottom-0 inset-x-0 z-40 md:hidden bg-zinc-950/95 backdrop-blur-md border-t border-zinc-850 px-2 py-1 flex items-center justify-around h-16 safe-area-pb">
      <button
        id="bottom-nav-dashboard"
        type="button"
        onClick={() => onSelectSection('dashboard')}
        className={`flex flex-col items-center justify-center w-16 py-1 rounded-xl transition cursor-pointer ${
          isTabActive('dashboard') ? 'text-white font-bold' : 'text-zinc-400 hover:text-white'
        }`}
      >
        <Home className="w-5 h-5" />
        <span className="text-[10px] mt-0.5">Sprint</span>
      </button>

      <button
        id="bottom-nav-projects"
        type="button"
        onClick={() => onSelectSection('projects')}
        className={`flex flex-col items-center justify-center w-16 py-1 rounded-xl transition cursor-pointer ${
          isTabActive('projects') ? 'text-white font-bold' : 'text-zinc-400 hover:text-white'
        }`}
      >
        <Folder className="w-5 h-5" />
        <span className="text-[10px] mt-0.5">Proyectos</span>
      </button>

      <button
        id="bottom-nav-roadmap"
        type="button"
        onClick={() => onSelectSection('roadmap')}
        className={`flex flex-col items-center justify-center w-16 py-1 rounded-xl transition cursor-pointer ${
          isTabActive('roadmap') ? 'text-white font-bold' : 'text-zinc-400 hover:text-white'
        }`}
      >
        <GitBranch className="w-5 h-5" />
        <span className="text-[10px] mt-0.5">Flujo</span>
      </button>

      <button
        id="bottom-nav-executions"
        type="button"
        onClick={() => onSelectSection('executions')}
        className={`flex flex-col items-center justify-center w-16 py-1 rounded-xl relative transition cursor-pointer ${
          isTabActive('executions') ? 'text-white font-bold' : 'text-zinc-400 hover:text-white'
        }`}
      >
        {hasPendingGate && (
          <span className="absolute top-1 right-3 w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
        )}
        <ShieldCheck className="w-5 h-5" />
        <span className="text-[10px] mt-0.5">Aprobar</span>
      </button>

      <button
        id="bottom-nav-menu"
        type="button"
        onClick={onOpenDrawer}
        className="flex flex-col items-center justify-center w-16 py-1 rounded-xl text-zinc-400 hover:text-white transition cursor-pointer"
      >
        <Menu className="w-5 h-5" />
        <span className="text-[10px] mt-0.5">Más</span>
      </button>
    </div>
  )
}
