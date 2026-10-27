import React, { useState, useEffect, useRef } from 'react'
import {
  Send,
  Bot,
  User,
  RotateCcw,
  ShieldCheck,
  CheckCircle2,
  Loader2,
  Terminal,
  Activity,
  GitBranch,
  Sparkles,
  AtSign,
} from 'lucide-react'
import { SlashCommandMenu, type SlashCommandItem } from '../SlashCommandMenu'
import { MentionPicker, type MentionItem } from '../MentionPicker'
import { ToolCallCard, type ToolCallData } from '../ToolCallCard'
import { DiffInspectorModal } from '../DiffInspectorModal'
import { formatSmartDateTime } from '../../utils/dateFormat'
import { ChevronDown, Cpu, Check } from 'lucide-react'

interface AIModelItem {
  id: string
  name: string
  provider: string
  tier: string
  badge: string
  description: string
  context_window: string
  default_temp: number
  is_active?: boolean
}

interface BackendChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: string
  action_data?: any
  tool_calls?: ToolCallData[]
}

export const ChatSection: React.FC = () => {
  const [messages, setMessages] = useState<BackendChatMessage[]>([])
  const [inputText, setInputText] = useState('')
  const [loading, setLoading] = useState(false)
  const [operatorName, setOperatorName] = useState('Operador')
  const [availableModels, setAvailableModels] = useState<AIModelItem[]>([])
  const [activeModel, setActiveModel] = useState<AIModelItem | null>(null)
  const [selectedModelId, setSelectedModelId] = useState<string>('claude-3-7-sonnet')
  const [showModelDropdown, setShowModelDropdown] = useState<boolean>(false)
  const [modelSwitching, setModelSwitching] = useState<boolean>(false)

  // Slash commands and mentions state
  const [commandsRegistry, setCommandsRegistry] = useState<SlashCommandItem[]>([])
  const [showSlashMenu, setShowSlashMenu] = useState(false)
  const [showMentionPicker, setShowMentionPicker] = useState(false)
  const [slashQuery, setSlashQuery] = useState('')
  const [mentionQuery, setMentionQuery] = useState('')
  const [selectedSlashIdx, setSelectedSlashIdx] = useState(0)

  // Diff Inspector Modal state
  const [isDiffModalOpen, setIsDiffModalOpen] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  // Load chat history, profile, and command registry from backend
  const loadChat = async () => {
    try {
      const res = await fetch('/api/chat/history')
      const data = await res.json()
      if (data && data.history) {
        setMessages(data.history)
      }
    } catch (e) {
      console.warn('Error loading chat history:', e)
    }

    try {
      const pRes = await fetch('/api/settings/profile')
      const pData = await pRes.json()
      if (pData.profile?.name) setOperatorName(pData.profile.name)
    } catch {}

    try {
      const cmdRes = await fetch('/api/commands/registry')
      const cmdData = await cmdRes.json()
      if (cmdData.commands) {
        setCommandsRegistry(cmdData.commands)
      }
    } catch {}

    try {
      const mRes = await fetch('/api/model/config')
      if (mRes.ok) {
        const mData = await mRes.json()
        if (mData.available_models) setAvailableModels(mData.available_models)
        if (mData.active_model) {
          setActiveModel(mData.active_model)
          setSelectedModelId(mData.active_model.id)
        }
      }
    } catch {}
  }

  useEffect(() => {
    loadChat()

    // Real-time SSE listener
    try {
      const sse = new EventSource('/api/events/stream')
      sse.addEventListener('chat_message', (ev: MessageEvent) => {
        try {
          const data = JSON.parse(ev.data)
          if (data && data.assistant_message) {
            setMessages((prev) => {
              if (prev.some((m) => m.id === data.assistant_message.id)) return prev
              return [...prev, data.assistant_message]
            })
          }
        } catch {}
      })
      return () => sse.close()
    } catch {}
  }, [])

  const handleInputChange = (val: string) => {
    setInputText(val)

    // Check for slash command trigger
    if (val.startsWith('/')) {
      setShowSlashMenu(true)
      setShowMentionPicker(false)
      setSlashQuery(val)
      return
    }

    // Check for @mention trigger (last token)
    const tokens = val.split(' ')
    const lastToken = tokens[tokens.length - 1]
    if (lastToken.startsWith('@')) {
      setShowMentionPicker(true)
      setShowSlashMenu(false)
      setMentionQuery(lastToken)
      return
    }

    setShowSlashMenu(false)
    setShowMentionPicker(false)
  }

  const handleSelectSlashCommand = (cmd: SlashCommandItem) => {
    setInputText(cmd.command + (cmd.requires_arg ? ' ' : ''))
    setShowSlashMenu(false)
    inputRef.current?.focus()
  }

  const handleSelectMention = (item: MentionItem) => {
    const tokens = inputText.split(' ')
    tokens[tokens.length - 1] = `@${item.id} `
    setInputText(tokens.join(' '))
    setShowMentionPicker(false)
    inputRef.current?.focus()
  }

  const handleSelectModel = async (model: AIModelItem) => {
    setSelectedModelId(model.id)
    setActiveModel(model)
    setShowModelDropdown(false)
    setModelSwitching(true)
    try {
      await fetch('/api/model/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_id: model.id }),
      })
    } catch (e) {
      console.warn('Error saving model selection:', e)
    } finally {
      setModelSwitching(false)
    }
  }

  const handleSendMessage = async (textToSend?: string) => {
    const text = (textToSend || inputText).trim()
    if (!text || loading) return

    setShowSlashMenu(false)
    setShowMentionPicker(false)

    // Local intercept for opening diff modal directly
    if (text === '/diff') {
      setIsDiffModalOpen(true)
    }

    const tempUserMsg: BackendChatMessage = {
      id: `usr-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, tempUserMsg])
    setInputText('')
    setLoading(true)

    try {
      const res = await fetch('/api/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: text, model_id: selectedModelId }),
      })
      const data = await res.json()
      if (data.success && data.assistant_message) {
        setMessages((prev) => {
          const filtered = prev.filter((m) => m.id !== tempUserMsg.id)
          return [...filtered, data.user_message || tempUserMsg, data.assistant_message]
        })
      } else {
        alert('Error: ' + (data.error || 'No se pudo procesar el mensaje'))
      }
    } catch (e: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: 'assistant',
          content: `Error de conexión con el backend SACL: ${e.message}`,
          timestamp: new Date().toISOString(),
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const handleClearHistory = async () => {
    try {
      await fetch('/api/chat/clear', { method: 'POST' })
      setMessages([])
      loadChat()
    } catch (e: any) {
      alert('Error limpiando historial: ' + e.message)
    }
  }

  const slashShortcuts = [
    { label: '/plan', prompt: '/plan Planificar oleadas del sprint' },
    { label: '/audit', prompt: '/audit' },
    { label: '/diff', prompt: '/diff' },
    { label: '/goal', prompt: '/goal Completar verificación de contratos' },
    { label: '/schedule', prompt: '/schedule */15 * * * *' },
  ]

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-5xl mx-auto rounded-3xl bg-zinc-950 border border-zinc-800 shadow-2xl overflow-hidden animate-fade-in">
      {/* Top Bar */}
      <div className="px-6 py-4 border-b border-zinc-800 bg-zinc-950 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-2xl bg-zinc-900 border border-zinc-750 flex items-center justify-center text-white">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-white tracking-wide">
                Consola Conversacional SACL & Runtime AGY
              </h2>
              <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono bg-zinc-900 text-zinc-300 border border-zinc-750">
                <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
                ANTIGRAVITY MOTOR ACTIVO
              </span>
            </div>
            <p className="text-xs text-zinc-400">
              Soporte nativo de Slash Commands (<code className="text-zinc-200 font-mono">/</code>), Menciones (<code className="text-zinc-300 font-mono">@</code>), y Tool Calls colapsables.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* AI Model Selector Dropdown */}
          <div className="relative">
            <button
              type="button"
              id="btn-select-model"
              onClick={() => setShowModelDropdown(!showModelDropdown)}
              className="px-3 py-1.5 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-600 text-xs text-white flex items-center gap-2 transition cursor-pointer"
              title="Seleccionar modelo de inferencia IA"
            >
              <Cpu className="w-3.5 h-3.5 text-white" />
              <div className="flex items-center gap-1.5 text-left">
                <span className="font-semibold text-white max-w-[140px] sm:max-w-[180px] truncate">
                  {activeModel?.name || selectedModelId}
                </span>
                {activeModel?.badge && (
                  <span className="hidden sm:inline-block px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-300 border border-zinc-700 text-[9px] font-mono">
                    {activeModel.badge}
                  </span>
                )}
              </div>
              <ChevronDown className={`w-3 h-3 text-zinc-400 transition-transform ${showModelDropdown ? 'rotate-180' : ''}`} />
            </button>

            {/* Model Dropdown Menu */}
            {showModelDropdown && (
              <div
                id="model-selector-menu"
                className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl bg-zinc-950 border border-zinc-800 shadow-2xl p-2.5 z-50 text-left space-y-1.5 max-h-96 overflow-y-auto custom-scroll animate-fade-in"
              >
                <div className="px-2 py-1 border-b border-zinc-850 flex items-center justify-between">
                  <span className="text-[11px] font-bold text-white uppercase tracking-wider font-mono">
                    Motores de Inferencia (AGY / SACL)
                  </span>
                  <span className="text-[10px] text-zinc-500 font-mono">
                    {availableModels.length} disponibles
                  </span>
                </div>

                {availableModels.map((m) => {
                  const isCurrent = m.id === selectedModelId
                  return (
                    <button
                      key={m.id}
                      type="button"
                      onClick={() => handleSelectModel(m)}
                      className={`w-full p-2.5 rounded-xl text-left transition cursor-pointer border ${
                        isCurrent
                          ? 'bg-zinc-900 border-zinc-700 text-white'
                          : 'bg-zinc-950/60 border-transparent hover:bg-zinc-900/60 hover:border-zinc-800 text-zinc-300'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-white flex items-center gap-1.5">
                          {m.name}
                        </span>
                        <div className="flex items-center gap-1.5">
                          {m.badge && (
                            <span className="px-1.5 py-0.2 rounded bg-zinc-850 text-zinc-300 border border-zinc-750 text-[9px] font-mono">
                              {m.badge}
                            </span>
                          )}
                          {isCurrent && <Check className="w-3.5 h-3.5 text-white" />}
                        </div>
                      </div>
                      <p className="text-[11px] text-zinc-400 mt-0.5 line-clamp-2">
                        {m.description}
                      </p>
                      <div className="flex items-center gap-2 mt-1.5 text-[10px] text-zinc-500 font-mono">
                        <span>{m.provider}</span>
                        <span>&bull;</span>
                        <span>Ctx: {m.context_window}</span>
                        <span>&bull;</span>
                        <span>Temp: {m.default_temp}</span>
                      </div>
                    </button>
                  )
                })}
              </div>
            )}
          </div>

          <button
            onClick={() => setIsDiffModalOpen(true)}
            className="px-3 py-1.5 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-600 text-xs text-zinc-300 flex items-center gap-1.5 transition cursor-pointer"
            title="Abrir inspector de diffs"
          >
            <GitBranch className="w-3.5 h-3.5 text-zinc-200" />
            <span className="hidden sm:inline">Inspector Diff</span>
          </button>
          <button
            onClick={handleClearHistory}
            className="px-3 py-1.5 rounded-xl bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-xs text-zinc-300 flex items-center gap-1.5 transition cursor-pointer"
            title="Limpiar conversación en backend"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Limpiar</span>
          </button>
        </div>
      </div>

      {/* Quick operational prompts */}
      <div className="flex items-center gap-2 px-6 py-2 bg-black border-b border-zinc-800/60 overflow-x-auto text-xs">
        <span className="text-[11px] font-mono text-zinc-500 uppercase tracking-wider shrink-0 flex items-center gap-1">
          <Terminal className="w-3.5 h-3.5 text-zinc-200" />
          Comandos Rápidos:
        </span>
        {slashShortcuts.map((sc) => (
          <button
            key={sc.label}
            onClick={() => handleSendMessage(sc.prompt)}
            className="px-2.5 py-1 rounded-lg bg-zinc-900/80 border border-zinc-800 hover:border-zinc-600 hover:bg-zinc-800 text-[11px] font-mono text-zinc-300 hover:text-white transition shrink-0 cursor-pointer"
          >
            <span className="text-zinc-200 font-bold">{sc.label}</span>
          </button>
        ))}
      </div>

      {/* Messages list */}
      <div className="flex-1 overflow-y-auto custom-scroll p-6 space-y-4">
        {messages.map((msg) => {
          const isUser = msg.role === 'user'
          return (
            <div
              key={msg.id}
              className={`flex gap-3 max-w-3xl ${isUser ? 'ml-auto flex-row-reverse' : ''}`}
            >
              {/* Avatar */}
              <div
                className={`w-9 h-9 rounded-2xl shrink-0 flex items-center justify-center ${
                  isUser
                    ? 'bg-white text-black font-bold'
                    : 'bg-zinc-900 text-white border border-zinc-750'
                }`}
              >
                {isUser ? <User className="w-4 h-4 text-black" /> : <Bot className="w-4 h-4 text-white" />}
              </div>

              {/* Message Content */}
              <div
                className={`flex flex-col gap-1 rounded-2xl p-4 text-xs leading-relaxed max-w-2xl ${
                  isUser
                    ? 'bg-zinc-800 border border-zinc-700 text-white'
                    : 'bg-zinc-950 border border-zinc-800 text-zinc-200 shadow-md'
                }`}
              >
                <div className="flex items-center justify-between gap-3 border-b border-white/5 pb-1.5 mb-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white text-[11px]">
                      {isUser ? operatorName : 'Asistente Principal SACL'}
                    </span>
                    <span className="text-[10px] text-zinc-400 font-mono">
                      ({isUser ? 'Product Owner' : 'AGY Runtime'})
                    </span>
                  </div>
                  {msg.timestamp && (
                    <span className="text-[10px] text-zinc-500 font-mono">
                      {formatSmartDateTime(msg.timestamp, false)}
                    </span>
                  )}
                </div>

                <div className="whitespace-pre-wrap font-sans text-xs">{msg.content}</div>

                {/* Tool Calls Collapsible Step Cards */}
                {msg.tool_calls && msg.tool_calls.length > 0 && (
                  <div className="mt-3 pt-2 border-t border-white/5 space-y-1">
                    <div className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider">
                      Llamadas de Herramientas ({msg.tool_calls.length}):
                    </div>
                    {msg.tool_calls.map((tc, idx) => (
                      <ToolCallCard key={idx} toolCall={tc} />
                    ))}
                  </div>
                )}

                {/* Action feedback button if applicable */}
                {msg.action_data?.type === 'OPEN_DIFF' && (
                  <div className="mt-3">
                    <button
                      type="button"
                      onClick={() => setIsDiffModalOpen(true)}
                      className="px-3.5 py-1.5 rounded-xl bg-white hover:bg-zinc-200 text-black font-bold font-mono text-xs font-bold flex items-center gap-2 transition cursor-pointer"
                    >
                      <GitBranch className="w-3.5 h-3.5" />
                      <span>Abrir Diff Inspector en Pantalla Completa</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          )
        })}

        {loading && (
          <div className="flex gap-3 max-w-2xl">
            <div className="w-9 h-9 rounded-2xl shrink-0 flex items-center justify-center bg-zinc-900 text-white border border-zinc-750">
              <Bot className="w-4 h-4 animate-spin" />
            </div>
            <div className="p-4 rounded-2xl bg-zinc-950 border border-zinc-800 text-zinc-400 text-xs flex items-center gap-2">
              <Loader2 className="w-3.5 h-3.5 animate-spin text-zinc-200" />
              <span>Procesando instrucción y ejecutando herramientas en runtime AGY...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input bar with floating menus */}
      <div className="p-4 bg-black border-t border-zinc-800 relative">
        {/* Floating Slash Command Menu */}
        {showSlashMenu && (
          <SlashCommandMenu
            commands={commandsRegistry}
            query={slashQuery}
            selectedIndex={selectedSlashIdx}
            onSelect={handleSelectSlashCommand}
            onClose={() => setShowSlashMenu(false)}
          />
        )}

        {/* Floating Mention Picker */}
        {showMentionPicker && (
          <MentionPicker
            query={mentionQuery}
            onSelect={handleSelectMention}
            onClose={() => setShowMentionPicker(false)}
          />
        )}

        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSendMessage()
          }}
          className="flex items-center gap-3"
        >
          <div className="relative flex-1">
            <input
              ref={inputRef}
              type="text"
              value={inputText}
              onChange={(e) => handleInputChange(e.target.value)}
              onKeyDown={(e) => {
                if (showSlashMenu) {
                  if (e.key === 'ArrowDown') {
                    e.preventDefault()
                    setSelectedSlashIdx((prev) => prev + 1)
                  } else if (e.key === 'ArrowUp') {
                    e.preventDefault()
                    setSelectedSlashIdx((prev) => Math.max(0, prev - 1))
                  }
                }
              }}
              placeholder="Escribe '/' para comandos de Antigravity o '@' para adjuntar contratos, archivos o tickets..."
              disabled={loading}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-2xl px-4 py-3 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-500 focus:ring-1 focus:ring-zinc-600 font-mono transition"
            />
          </div>

          <button
            type="submit"
            disabled={loading || !inputText.trim()}
            className="px-5 py-3 rounded-2xl bg-white hover:bg-zinc-200 disabled:opacity-30 disabled:hover:bg-white text-black font-bold text-xs flex items-center gap-2 transition cursor-pointer shrink-0"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            <span>Enviar</span>
          </button>
        </form>
      </div>

      {/* Fullscreen Diff Inspector Modal */}
      <DiffInspectorModal
        isOpen={isDiffModalOpen}
        onClose={() => setIsDiffModalOpen(false)}
      />
    </div>
  )
}
