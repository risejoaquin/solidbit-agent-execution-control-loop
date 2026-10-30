import React from 'react'
import { ChevronRight, Home } from 'lucide-react'

interface BreadcrumbItem {
  label: string
  sectionId?: string
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[]
  onNavigate: (sectionId: string) => void
}

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({ items, onNavigate }) => {
  return (
    <nav aria-label="Ruta de navegación" className="flex items-center text-xs font-mono text-zinc-400 py-1">
      <button
        type="button"
        onClick={() => onNavigate('dashboard')}
        className="flex items-center gap-1 text-zinc-400 hover:text-emerald-400 transition cursor-pointer"
        title="Ir a Inicio"
      >
        <Home className="w-3.5 h-3.5" />
        <span className="hidden sm:inline">Inicio</span>
      </button>

      {items.map((item, idx) => {
        const isLast = idx === items.length - 1
        return (
          <React.Fragment key={idx}>
            <ChevronRight className="w-3 h-3 text-zinc-600 mx-1.5 shrink-0" />
            {isLast || !item.sectionId ? (
              <span className="text-white font-bold truncate max-w-[180px] sm:max-w-none" aria-current="page">
                {item.label}
              </span>
            ) : (
              <button
                type="button"
                onClick={() => onNavigate(item.sectionId!)}
                className="text-zinc-400 hover:text-emerald-400 transition cursor-pointer truncate max-w-[150px]"
              >
                {item.label}
              </button>
            )}
          </React.Fragment>
        )
      })}
    </nav>
  )
}
