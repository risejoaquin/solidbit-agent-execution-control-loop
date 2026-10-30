import React from 'react'
import {
  Home,
  Layers,
  GitBranch,
  Bot,
  ShieldCheck,
  Folder,
  BarChart2,
  Settings,
  X,
  MessageSquare,
  Key,
  Mail,
  CheckSquare,
} from 'lucide-react'

interface MobileDrawerProps {
  isOpen: boolean
  onClose: () => void
  currentSection: string
  onSelectSection: (section: string) => void
  projectName: string
}

export const MobileDrawer: React.FC<MobileDrawerProps> = ({
  isOpen,
  onClose,
  currentSection,
  onSelectSection,
  projectName,
}) => {
  if (!isOpen) return null

  const navItems = [
    { id: 'dashboard', label: '1. Sprint Actual', icon: Home, action: () => onSelectSection('dashboard') },
    { id: 'projects', label: '2. Proyectos', icon: Folder, action: () => onSelectSection('projects') },
    { id: 'roadmap', label: '3. Mapa de Flujo', icon: GitBranch, action: () => onSelectSection('roadmap') },
    { id: 'agents', label: '4. Equipo de Asistentes', icon: Bot, action: () => onSelectSection('agents') },
    { id: 'executions', label: '5. Aprobaciones', icon: ShieldCheck, action: () => onSelectSection('executions') },
    { id: 'jira', label: 'Requerimientos y Tareas', icon: CheckSquare, action: () => onSelectSection('jira') },
    { id: 'connections', label: 'Conexiones del Sistema', icon: Key, action: () => onSelectSection('connections') },
    { id: 'email', label: 'Notificaciones por Correo', icon: Mail, action: () => onSelectSection('email') },
    { id: 'chat', label: 'Asistente de Consulta', icon: MessageSquare, action: () => onSelectSection('chat') },
    { id: 'workflows', label: 'Catálogo de Flujos', icon: Layers, action: () => onSelectSection('workflows') },
    { id: 'database', label: 'Registro de Actividad', icon: BarChart2, action: () => onSelectSection('database') },
    { id: 'github', label: 'Perfil y Sincronización', icon: Settings, action: () => onSelectSection('github') },
  ]

  const handleItemClick = (action: () => void) => {
    action()
    onClose()
  }

  return (
    <div className="fixed inset-0 z-[100] md:hidden flex animate-fade-in text-left">
      <div
        className="fixed inset-0 bg-black/80 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      <div className="relative w-72 max-w-[85vw] bg-black border-r border-zinc-850 flex flex-col justify-between p-4 shadow-2xl z-10 overflow-y-auto custom-scroll">
        <div>
          <div className="flex items-center justify-between pb-4 border-b border-zinc-850">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-white text-black font-extrabold text-xs flex items-center justify-center">
                SB
              </div>
              <div>
                <span className="text-xs font-bold text-white block">Centro de Control</span>
                <span className="text-[10px] text-zinc-400 truncate max-w-[140px] block">
                  {projectName}
                </span>
              </div>
            </div>

            <button
              id="drawer-close-btn"
              type="button"
              onClick={onClose}
              className="w-8 h-8 rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-white flex items-center justify-center transition cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <nav className="mt-4 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive =
                currentSection === item.id ||
                (item.id === 'roadmap' && currentSection === 'designer') ||
                (item.id === 'executions' && currentSection === 'gates') ||
                (item.id === 'database' && currentSection === 'reports') ||
                (item.id === 'github' && currentSection === 'settings')

              return (
                <button
                  key={item.id}
                  id={`drawer-nav-${item.id}`}
                  type="button"
                  onClick={() => handleItemClick(item.action)}
                  className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition cursor-pointer ${
                    isActive
                      ? 'bg-zinc-900 text-white border border-zinc-700 font-bold'
                      : 'text-zinc-400 hover:text-white hover:bg-zinc-900/60'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </div>
                </button>
              )
            })}
          </nav>
        </div>

        <div className="pt-3 border-t border-zinc-850 mt-4">
          <div className="p-3 rounded-2xl bg-zinc-950 border border-zinc-850 text-[11px] text-zinc-400">
            <span className="text-white font-bold block">Entorno Local Privado</span>
            <span>Tus proyectos y decisiones se resguardan en este equipo.</span>
          </div>
        </div>
      </div>
    </div>
  )
}
