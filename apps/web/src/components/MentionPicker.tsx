import React, { useEffect, useRef, useState } from 'react'
import { FileCode, ShieldCheck, Database, CheckSquare, AtSign } from 'lucide-react'

export interface MentionItem {
  id: string
  name: string
  desc: string
  category: 'contract' | 'jira' | 'table' | 'file'
}

interface MentionPickerProps {
  query: string
  onSelect: (item: MentionItem) => void
  onClose: () => void
}

export const MentionPicker: React.FC<MentionPickerProps> = ({ query, onSelect, onClose }) => {
  const [mentions, setMentions] = useState<{
    contracts: MentionItem[]
    jira: MentionItem[]
    tables: MentionItem[]
    files: MentionItem[]
  }>({
    contracts: [],
    jira: [],
    tables: [],
    files: [],
  })

  useEffect(() => {
    fetch('/api/commands/mentions')
      .then((r) => r.json())
      .then((d) => {
        if (d.mentions) {
          setMentions(d.mentions)
        }
      })
      .catch(() => {})
  }, [])

  const cleanQuery = query.replace(/^@/, '').toLowerCase()

  const allItems: MentionItem[] = [
    ...mentions.contracts,
    ...mentions.jira,
    ...mentions.tables,
    ...mentions.files,
  ].filter(
    (item) =>
      item.id.toLowerCase().includes(cleanQuery) ||
      item.name.toLowerCase().includes(cleanQuery) ||
      item.desc.toLowerCase().includes(cleanQuery)
  )

  const getIcon = (category: string) => {
    switch (category) {
      case 'contract':
        return <ShieldCheck className="w-3.5 h-3.5 text-zinc-200" />
      case 'jira':
        return <CheckSquare className="w-3.5 h-3.5 text-zinc-200" />
      case 'table':
        return <Database className="w-3.5 h-3.5 text-zinc-200" />
      default:
        return <FileCode className="w-3.5 h-3.5 text-zinc-200" />
    }
  }

  if (allItems.length === 0) return null

  return (
    <div className="absolute bottom-full left-0 right-0 mb-2 max-h-64 overflow-y-auto custom-scroll rounded-2xl bg-zinc-950 border border-zinc-800 shadow-2xl p-2 z-50 animate-fade-in backdrop-blur-xl">
      <div className="px-3 py-1.5 border-b border-zinc-800/60 mb-1 text-[10px] font-mono text-zinc-500 flex items-center gap-1.5">
        <AtSign className="w-3 h-3 text-zinc-200" />
        ADJUNTAR CONTEXTO (@MENTIONS)
      </div>
      <div className="space-y-1">
        {allItems.slice(0, 15).map((item) => (
          <div
            key={item.id}
            onClick={() => onSelect(item)}
            className="flex items-center justify-between p-2 rounded-xl hover:bg-zinc-900/80 cursor-pointer transition border border-transparent hover:border-zinc-800"
          >
            <div className="flex items-center gap-2 min-w-0">
              {getIcon(item.category)}
              <span className="font-mono text-xs font-bold text-white tracking-wide truncate">
                @{item.id}
              </span>
              <span className="text-[11px] text-zinc-400 truncate">{item.desc}</span>
            </div>
            <span className="text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-zinc-800/80 text-zinc-400 shrink-0">
              {item.category}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
