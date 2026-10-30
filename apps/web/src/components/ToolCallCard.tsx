import React, { useState } from 'react'
import {
  Terminal,
  FileCode,
  CheckCircle2,
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  GitBranch,
  Layers,
  Clock,
} from 'lucide-react'

export interface ToolCallData {
  tool: string
  args: Record<string, any>
  output?: string
  exit_code?: number
  duration_ms?: number
}

interface ToolCallCardProps {
  toolCall: ToolCallData
}

export const ToolCallCard: React.FC<ToolCallCardProps> = ({ toolCall }) => {
  const [isOpen, setIsOpen] = useState(false)

  const isSuccess = toolCall.exit_code === 0 || toolCall.exit_code === undefined

  const getToolIcon = (tool: string) => {
    switch (tool) {
      case 'run_command':
      case 'git_status':
        return <Terminal className="w-3.5 h-3.5 text-zinc-200 shrink-0" />
      case 'write_file':
      case 'edit_file':
        return <FileCode className="w-3.5 h-3.5 text-zinc-200 shrink-0" />
      case 'auto_plan':
        return <Layers className="w-3.5 h-3.5 text-zinc-200 shrink-0" />
      case 'schedule':
        return <Clock className="w-3.5 h-3.5 text-zinc-200 shrink-0" />
      default:
        return <Terminal className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
    }
  }

  const getSummary = () => {
    if (toolCall.tool === 'run_command' && toolCall.args?.command) {
      return `$ ${toolCall.args.command}`
    }
    if (toolCall.tool === 'write_file' && toolCall.args?.path) {
      return `write: ${toolCall.args.path}`
    }
    if (toolCall.tool === 'edit_file' && toolCall.args?.path) {
      return `edit: ${toolCall.args.path}`
    }
    if (toolCall.tool === 'auto_plan') {
      return `plan: ${toolCall.args?.goal || 'Kahn DAG'}`
    }
    if (toolCall.tool === 'schedule') {
      return `cron: ${toolCall.args?.cron || 'scheduled'}`
    }
    return toolCall.tool
  }

  return (
    <div className="rounded-xl bg-black/60 border border-zinc-800 overflow-hidden text-xs font-mono my-2 transition">
      {/* Header bar (clickable to toggle) */}
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between p-2.5 bg-zinc-950 hover:bg-zinc-900/80 cursor-pointer select-none transition"
      >
        <div className="flex items-center gap-2 min-w-0">
          {isOpen ? (
            <ChevronDown className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
          ) : (
            <ChevronRight className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
          )}
          {getToolIcon(toolCall.tool)}
          <span className="text-[11px] font-bold text-white tracking-wide truncate">
            {getSummary()}
          </span>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {toolCall.duration_ms && (
            <span className="text-[10px] text-zinc-500">{toolCall.duration_ms}ms</span>
          )}
          {isSuccess ? (
            <span className="inline-flex items-center gap-1 text-[10px] text-zinc-200 font-bold bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/30">
              <CheckCircle2 className="w-3 h-3 text-zinc-200" />
              SUCCESS
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-[10px] text-red-400 font-bold bg-red-500/10 px-2 py-0.5 rounded-full border border-red-500/30">
              <AlertTriangle className="w-3 h-3 text-red-400" />
              ERROR {toolCall.exit_code}
            </span>
          )}
        </div>
      </div>

      {/* Collapsed body */}
      {isOpen && (
        <div className="p-3 bg-black/90 border-t border-zinc-800 space-y-2 text-[11px]">
          {toolCall.args && Object.keys(toolCall.args).length > 0 && (
            <div>
              <div className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1">Argumentos:</div>
              <pre className="p-2 rounded-lg bg-zinc-950 text-zinc-300 overflow-x-auto custom-scroll text-[10px]">
                {JSON.stringify(toolCall.args, null, 2)}
              </pre>
            </div>
          )}

          {toolCall.output && (
            <div>
              <div className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1">Salida / Output:</div>
              <pre className="p-2 rounded-lg bg-zinc-950 text-emerald-300/90 overflow-x-auto custom-scroll text-[10px] whitespace-pre-wrap">
                {toolCall.output}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
