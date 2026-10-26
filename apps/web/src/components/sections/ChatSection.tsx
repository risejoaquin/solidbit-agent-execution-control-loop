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
} from 'lucide-react'

interface BackendChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: string
  action_data?: any
}

export const ChatSection: React.FC = () => {
  const [messages, setMessages] = useState<BackendChatMessage[]>([])
  const [inputText, setInputText] = useState('')
  const [loading, setLoading] = useState(false)
  const [operatorName, setOperatorName] = useState('Joaquin Vallejo')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  // Load real chat history and operator profile from backend
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

  const handleSendMessage = async (textToSend?: string) => {
    const text = (textToSend || inputText).trim()
    if (!text || loading) return

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
        body: JSON.stringify({ prompt: text, model_id: 'SACL_ORCHESTRATOR' }),
      })
      const data = await res.json()
      if (data.success && data.assistant_message) {
        setMessages((prev) => {
          // Replace temp with server version if needed, or append
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
    { label: '/sprint', prompt: 'lanzar campaña sprint SACL con contratos DR-INV-001 y DR-PAY-001' },
    { label: '/compuertas', prompt: 'revisar compuertas pendientes de aprobación HITL' },
    { label: '/contratos', prompt: 'auditar estado de los 6 contratos inmutables de SolidBit' },
    { label: '/status', prompt: 'mostrar estado general del runtime, base de datos SQLite y worktrees' },
  ]

  return (
    <div className="flex flex-col h-[calc(100vh-8.5rem)] rounded-3xl bg-[#0e141d] border border-[#1b2533] overflow-hidden shadow-2xl">
      {/* Top Header */}
      <div className="flex items-center justify-between px-6 py-4 bg-[#0a0f16] border-b border-[#1b2533]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-white tracking-wide">
                Consola Conversacional SACL & Runtime AGY
              </h2>
              <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                BACKEND CONECTADO
              </span>
            </div>
            <p className="text-xs text-zinc-400">
              Conexión directa con ChatModule (/api/chat/message) y runtime local de Antigravity
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleClearHistory}
            className="px-3 py-1.5 rounded-xl bg-zinc-900 border border-[#1b2533] hover:bg-zinc-800 text-xs text-zinc-300 flex items-center gap-1.5 transition cursor-pointer"
            title="Limpiar conversación en backend"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Limpiar</span>
          </button>
        </div>
      </div>

      {/* Quick operational prompts */}
      <div className="flex items-center gap-2 px-6 py-2.5 bg-[#090d13] border-b border-[#1b2533]/60 overflow-x-auto text-xs">
        <span className="text-[11px] font-mono text-zinc-500 uppercase tracking-wider shrink-0 flex items-center gap-1">
          <Terminal className="w-3.5 h-3.5 text-emerald-400" />
          Comandos Operacionales:
        </span>
        {slashShortcuts.map((sc) => (
          <button
            key={sc.label}
            onClick={() => handleSendMessage(sc.prompt)}
            className="px-2.5 py-1 rounded-lg bg-zinc-900/80 border border-zinc-800 hover:border-emerald-500/50 hover:bg-emerald-500/10 text-[11px] font-mono text-zinc-300 hover:text-emerald-300 transition shrink-0 cursor-pointer"
          >
            <span className="text-emerald-400 font-bold">{sc.label}</span>
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
                    ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                    : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                }`}
              >
                {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              {/* Message Content */}
              <div
                className={`flex flex-col gap-1 rounded-2xl p-4 text-xs leading-relaxed ${
                  isUser
                    ? 'bg-blue-600/15 border border-blue-500/30 text-blue-50'
                    : 'bg-[#090e16] border border-[#1b2533] text-zinc-200 shadow-md'
                }`}
              >
                <div className="flex items-center justify-between gap-3 border-b border-white/5 pb-1.5 mb-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white text-[11px]">
                      {isUser ? operatorName : 'Asistente Soberano SACL'}
                    </span>
                    <span className="text-[10px] text-zinc-400 font-mono">
                      ({isUser ? 'Product Owner' : 'AGY Runtime'})
                    </span>
                  </div>
                  {msg.timestamp && (
                    <span className="text-[10px] text-zinc-500 font-mono">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </span>
                  )}
                </div>

                <div className="whitespace-pre-wrap font-sans text-xs">{msg.content}</div>

                {/* Real Action Payload if returned by backend */}
                {msg.action_data && (
                  <div className="mt-3 p-3 rounded-xl bg-black/60 border border-emerald-500/30 space-y-1.5 font-mono text-[11px]">
                    <div className="flex items-center justify-between text-emerald-400 font-bold">
                      <span className="flex items-center gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Acción Operacional Ejecutada
                      </span>
                      <span>{msg.action_data.execution_id || msg.action_data.status}</span>
                    </div>
                    {msg.action_data.deliverables && (
                      <div className="text-[10px] text-zinc-400">
                        {msg.action_data.deliverables.length} entregables físicos generados en disco.
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )
        })}

        {loading && (
          <div className="flex gap-3 max-w-2xl">
            <div className="w-9 h-9 rounded-2xl shrink-0 flex items-center justify-center bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              <Bot className="w-4 h-4 animate-spin" />
            </div>
            <div className="p-4 rounded-2xl bg-[#090e16] border border-[#1b2533] text-zinc-400 text-xs flex items-center gap-2">
              <Loader2 className="w-3.5 h-3.5 animate-spin text-emerald-400" />
              <span>Procesando solicitud en el backend SACL y runtime AGY...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input bar */}
      <div className="p-4 bg-[#0a0f16] border-t border-[#1b2533]">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSendMessage()
          }}
          className="flex items-center gap-3"
        >
          <div className="relative flex-1">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Escribe una orden o comando (e.g. 'auditar contratos', 'lanzar campaña sprint')..."
              disabled={loading}
              className="w-full bg-[#080c10] border border-[#1b2533] rounded-2xl px-4 py-3 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-emerald-500/60 focus:ring-1 focus:ring-emerald-500/30 transition"
            />
          </div>

          <button
            type="submit"
            disabled={loading || !inputText.trim()}
            className="px-5 py-3 rounded-2xl bg-emerald-500 hover:bg-emerald-400 disabled:opacity-40 disabled:hover:bg-emerald-500 text-black font-bold text-xs flex items-center gap-2 transition cursor-pointer shrink-0"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            <span>Enviar</span>
          </button>
        </form>
      </div>
    </div>
  )
}
