import React, { useState, useEffect, useRef } from 'react'
import {
  Search,
  Home,
  MessageSquare,
  Sparkles,
  CheckSquare,
  Key,
  Layers,
  GitBranch,
  Bot,
  PlayCircle,
  Folder,
  Mail,
  BarChart2,
  Settings,
  ArrowRight,
  Terminal,
  X,
  FileCode,
} from 'lucide-react'

interface CommandPaletteItem {
  id: string
  title: string
  subtitle: string
  category: 'Navegación' | 'Acción Rápida'
  icon: React.ComponentType<{ className?: string }>
  action: () => void
  shortcut?: string
}

interface CommandPaletteModalProps {
  isOpen: boolean
  onClose: () => void
  onNavigate: (section: string) => void
  onOpenSprintModal: () => void
  onOpenDiffModal?: () => void
}

export const CommandPaletteModal: React.FC<CommandPaletteModalProps> = ({
  isOpen,
  onClose,
  onNavigate,
  onOpenSprintModal,
  onOpenDiffModal,
}) => {
  const [query, setQuery] = useState<string>('')
  const [selectedIdx, setSelectedIdx] = useState<number>(0)
  const inputRef = useRef<HTMLInputElement>(null)

  const items: CommandPaletteItem[] = [
    // Acciones Rápidas
    {
      id: 'act-sprint',
      title: 'Diseñar Sprint de Ejecución (DAG Kahn)',
      subtitle: 'Orquestar oleadas, roles y worktrees de agentes',
      category: 'Acción Rápida',
      icon: Sparkles,
      action: () => {
        onClose()
        onOpenSprintModal()
      },
      shortcut: 'S',
    },
    {
      id: 'act-jira',
      title: 'Crear o Revisar Tickets Jira',
      subtitle: 'Gestionar requerimientos BDD (Given/When/Then)',
      category: 'Acción Rápida',
      icon: CheckSquare,
      action: () => {
        onClose()
        onNavigate('jira')
      },
      shortcut: 'J',
    },
    {
      id: 'act-diffs',
      title: 'Inspeccionar Diffs Git en Worktrees',
      subtitle: 'Auditoría de cambios pendientes y regla Dirty-Root',
      category: 'Acción Rápida',
      icon: GitBranch,
      action: () => {
        onClose()
        onOpenDiffModal?.()
      },
      shortcut: 'D',
    },

    // Navegación
    {
      id: 'nav-dashboard',
      title: 'Inicio / Panel de Control',
      subtitle: 'Supervisión general, telemetría y commits recientes',
      category: 'Navegación',
      icon: Home,
      action: () => {
        onClose()
        onNavigate('dashboard')
      },
    },
    {
      id: 'nav-chat',
      title: 'Chat IA (AGY) & Modelos',
      subtitle: 'Consola conversacional con 9 motores de inferencia',
      category: 'Navegación',
      icon: MessageSquare,
      action: () => {
        onClose()
        onNavigate('chat')
      },
    },
    {
      id: 'nav-jira',
      title: 'Jira Backlog & Requerimientos',
      subtitle: 'Backlog de producto, historias y criterios de aceptación',
      category: 'Navegación',
      icon: CheckSquare,
      action: () => {
        onClose()
        onNavigate('jira')
      },
    },
    {
      id: 'nav-auth',
      title: 'Sesiones CLI & Auth Hub',
      subtitle: 'Credenciales y diagnóstico de GitHub, Railway, Supabase, Jira',
      category: 'Navegación',
      icon: Key,
      action: () => {
        onClose()
        onNavigate('connections')
      },
    },
    {
      id: 'nav-workflows',
      title: 'Workflows & Skills (AGY)',
      subtitle: 'Habilidades activas y catálogo de herramientas',
      category: 'Navegación',
      icon: Layers,
      action: () => {
        onClose()
        onNavigate('workflows')
      },
    },
    {
      id: 'nav-roadmap',
      title: 'Roadmap & DAG Topológico',
      subtitle: 'Línea de tiempo SDLC y visualizador de dependencias',
      category: 'Navegación',
      icon: GitBranch,
      action: () => {
        onClose()
        onNavigate('roadmap')
      },
    },
    {
      id: 'nav-agents',
      title: 'Flota de Agentes & Procesos SO',
      subtitle: 'Tabla de PIDs del sistema operativo y consumo de recursos',
      category: 'Navegación',
      icon: Bot,
      action: () => {
        onClose()
        onNavigate('agents')
      },
    },
    {
      id: 'nav-gates',
      title: 'Compuertas Controls & Ejecuciones (HITL)',
      subtitle: 'Historial de runs y firmas criptográficas HMAC-SHA256',
      category: 'Navegación',
      icon: PlayCircle,
      action: () => {
        onClose()
        onNavigate('executions')
      },
    },
    {
      id: 'nav-email',
      title: 'Email Gateway & Resend',
      subtitle: 'Automatización bidireccional y micro-decisiones por correo',
      category: 'Navegación',
      icon: Mail,
      action: () => {
        onClose()
        onNavigate('email')
      },
    },
    {
      id: 'nav-database',
      title: 'Reportes Forenses & SQLite WAL',
      subtitle: 'Inspector de tablas locales y registros de auditoría',
      category: 'Navegación',
      icon: BarChart2,
      action: () => {
        onClose()
        onNavigate('database')
      },
    },
    {
      id: 'nav-github',
      title: 'Configuración & Repositorio GitHub',
      subtitle: 'Ajustes del perfil del operador y ramas remotas',
      category: 'Navegación',
      icon: Settings,
      action: () => {
        onClose()
        onNavigate('github')
      },
    },
  ]

  const filteredItems = items.filter((item) => {
    const q = query.toLowerCase().trim()
    if (!q) return true
    return (
      item.title.toLowerCase().includes(q) ||
      item.subtitle.toLowerCase().includes(q) ||
      item.category.toLowerCase().includes(q)
    )
  })

  useEffect(() => {
    if (isOpen) {
      setQuery('')
      setSelectedIdx(0)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [isOpen])

  // Keyboard navigation inside modal
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedIdx((prev) => (prev + 1) % (filteredItems.length || 1))
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedIdx((prev) => (prev - 1 + filteredItems.length) % (filteredItems.length || 1))
      } else if (e.key === 'Enter') {
        e.preventDefault()
        if (filteredItems[selectedIdx]) {
          filteredItems[selectedIdx].action()
        }
      } else if (e.key === 'Escape') {
        e.preventDefault()
        onClose()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, filteredItems, selectedIdx, onClose])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-[120] bg-black/80 backdrop-blur-sm flex items-start justify-center pt-20 p-4 animate-fade-in text-left">
      <div className="w-full max-w-xl rounded-3xl bg-zinc-950 border border-zinc-800 shadow-2xl overflow-hidden flex flex-col max-h-[75vh]">
        {/* Search Input Bar */}
        <div className="p-4 border-b border-zinc-800 flex items-center gap-3 bg-zinc-950">
          <Search className="w-4 h-4 text-zinc-400 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value)
              setSelectedIdx(0)
            }}
            placeholder="Escribe un comando o busca una sección... (↑ ↓ para navegar)"
            className="w-full bg-transparent text-sm text-white placeholder-zinc-500 focus:outline-none font-mono"
          />
          <kbd className="px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-[10px] font-mono text-zinc-400">
            ESC
          </kbd>
        </div>

        {/* Results List */}
        <div className="overflow-y-auto custom-scroll p-2 divide-y divide-zinc-900">
          {filteredItems.length === 0 ? (
            <div className="py-8 text-center text-xs text-zinc-500 font-mono">
              No se encontraron coincidencias para "{query}"
            </div>
          ) : (
            filteredItems.map((item, idx) => {
              const Icon = item.icon
              const isSelected = idx === selectedIdx

              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={item.action}
                  onMouseEnter={() => setSelectedIdx(idx)}
                  className={`w-full p-3 rounded-2xl flex items-center justify-between transition cursor-pointer text-left ${
                    isSelected
                      ? 'bg-zinc-900 border border-zinc-700 text-white'
                      : 'hover:bg-zinc-900/60 border border-transparent text-zinc-300'
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div
                      className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 border ${
                        isSelected
                          ? 'bg-white text-black border-white'
                          : 'bg-zinc-900 text-zinc-300 border-zinc-800'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-white truncate">
                          {item.title}
                        </span>
                        <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-400 border border-zinc-750">
                          {item.category}
                        </span>
                      </div>
                      <p className="text-[11px] text-zinc-400 truncate mt-0.5">
                        {item.subtitle}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0 ml-3">
                    {item.shortcut && (
                      <kbd className="hidden sm:inline-block px-1.5 py-0.5 rounded bg-zinc-850 text-zinc-400 border border-zinc-750 text-[10px] font-mono">
                        {item.shortcut}
                      </kbd>
                    )}
                    <ArrowRight
                      className={`w-3.5 h-3.5 transition-transform ${
                        isSelected ? 'translate-x-0.5 text-white' : 'text-zinc-600'
                      }`}
                    />
                  </div>
                </button>
              )
            })
          )}
        </div>

        {/* Footer info bar */}
        <div className="p-2.5 px-4 bg-zinc-900/40 border-t border-zinc-800 flex items-center justify-between text-[10px] text-zinc-500 font-mono">
          <div className="flex items-center gap-3">
            <span>↑ ↓ Navegar</span>
            <span>&bull;</span>
            <span>↵ Seleccionar</span>
            <span>&bull;</span>
            <span>ESC Cerrar</span>
          </div>
          <span>SACL Control Plane V41</span>
        </div>
      </div>
    </div>
  )
}
