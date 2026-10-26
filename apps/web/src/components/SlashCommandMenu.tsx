import React, { useEffect, useRef } from 'react'
import {
  Sparkles,
  Layers,
  Terminal,
  ShieldCheck,
  GitBranch,
  Search,
  Code2,
  Clock,
  Compass,
} from 'lucide-react'

export interface SlashCommandItem {
  command: string
  label: string
  description: string
  category: 'workflow' | 'core' | 'governance' | 'devtools'
  syntax: string
  example?: string
  requires_arg?: boolean
  arg_placeholder?: string
  skill_id?: string
  scope?: string
}

interface SlashCommandMenuProps {
  commands: SlashCommandItem[]
  query: string
  selectedIndex: number
  onSelect: (command: SlashCommandItem) => void
  onClose: () => void
}

export const SlashCommandMenu: React.FC<SlashCommandMenuProps> = ({
  commands,
  query,
  selectedIndex,
  onSelect,
  onClose,
}) => {
  const menuRef = useRef<HTMLDivElement>(null)

  // Filter commands by query (without the leading '/')
  const cleanQuery = query.replace(/^\//, '').toLowerCase()
  const filtered = commands.filter(
    (c) =>
      c.command.toLowerCase().includes(cleanQuery) ||
      c.label.toLowerCase().includes(cleanQuery) ||
      c.description.toLowerCase().includes(cleanQuery)
  )

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onClose])

  if (filtered.length === 0) return null

  const getCategoryBadge = (category: string, scope?: string) => {
    if (category === 'workflow') {
      return (
        <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-purple-500/15 text-purple-400 border border-purple-500/30">
          {scope ? `SKILL (${scope.toUpperCase()})` : 'WORKFLOW'}
        </span>
      )
    }
    if (category === 'governance') {
      return (
        <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
          SOLIDBIT GOV
        </span>
      )
    }
    if (category === 'devtools') {
      return (
        <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-blue-500/15 text-blue-400 border border-blue-500/30">
          DEVTOOL
        </span>
      )
    }
    return (
      <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-400 border border-amber-500/30">
        CORE AGY
      </span>
    )
  }

  const getCommandIcon = (category: string, command: string) => {
    if (command === '/diff') return <GitBranch className="w-4 h-4 text-emerald-400 shrink-0" />
    if (command === '/audit') return <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
    if (command === '/schedule') return <Clock className="w-4 h-4 text-amber-400 shrink-0" />
    if (command === '/browser') return <Compass className="w-4 h-4 text-blue-400 shrink-0" />
    if (category === 'workflow') return <Layers className="w-4 h-4 text-purple-400 shrink-0" />
    return <Sparkles className="w-4 h-4 text-emerald-400 shrink-0" />
  }

  return (
    <div
      ref={menuRef}
      className="absolute bottom-full left-0 right-0 mb-2 max-h-72 overflow-y-auto custom-scroll rounded-2xl bg-[#090e16] border border-[#1b2533] shadow-2xl p-2 z-50 animate-fade-in backdrop-blur-xl"
    >
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-[#1b2533]/60 mb-1 text-[10px] font-mono text-zinc-500">
        <span className="flex items-center gap-1.5">
          <Terminal className="w-3 h-3 text-emerald-400" />
          COMANDOS DE ANTIGRAVITY & SKILLS DISPONIBLES ({filtered.length})
        </span>
        <span className="hidden sm:inline">Navega con &uarr;&darr; &bull; Enter para seleccionar</span>
      </div>

      <div className="space-y-1">
        {filtered.map((item, idx) => {
          const isSelected = idx === selectedIndex % filtered.length
          return (
            <div
              key={item.command}
              onClick={() => onSelect(item)}
              className={`flex items-start gap-3 p-2.5 rounded-xl cursor-pointer transition ${
                isSelected
                  ? 'bg-emerald-500/15 border border-emerald-500/40 text-white'
                  : 'hover:bg-zinc-900/80 border border-transparent text-zinc-300'
              }`}
            >
              <div className="mt-0.5">{getCommandIcon(item.category, item.command)}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-white tracking-wide">
                    {item.command}
                  </span>
                  <span className="text-[11px] font-semibold text-zinc-300">{item.label}</span>
                  {getCategoryBadge(item.category, item.scope)}
                </div>
                <p className="text-[11px] text-zinc-400 truncate mt-0.5">{item.description}</p>
                {item.example && (
                  <div className="text-[10px] font-mono text-zinc-500 mt-0.5">
                    Ejemplo: <code className="text-zinc-400">{item.example}</code>
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
