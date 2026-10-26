import React, { useState, useEffect, useRef } from 'react'
import {
  Send,
  Bot,
  User,
  Sparkles,
  Terminal,
  RotateCcw,
  ShieldCheck,
  CheckCircle2,
  Loader2,
  Cpu,
} from 'lucide-react'

interface ChatMessage {
  id: string
  sender: 'user' | 'agy'
  name: string
  role: string
  text: string
  timestamp: string
  status?: string
  tools?: any[]
}

interface ChatSectionProps {
  onExecutePrompt?: (prompt: string) => void
}

export const ChatSection: React.FC<ChatSectionProps> = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'init-1',
      sender: 'agy',
      name: 'Antigravity AGY Runtime',
      role: 'AI Model / System Engine',
      text: 'Hola Joaquín. El runtime de Antigravity (AGY) está activo y conectado al orquestador SACL. ¿En qué plan de sprint o arquitectura trabajamos hoy?',
      timestamp: new Date().toLocaleTimeString(),
      status: 'delivered',
    },
  ])
  const [inputText, setInputText] = useState('')
  const [loading, setLoading] = useState(false)
  const [operatorName, setOperatorName] = useState('Joaquin Vallejo')
  const [operatorRole, setOperatorRole] = useState('Product Owner / Sovereign Authority')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  // Load chat history and profile
  useEffect(() => {
    fetch('/api/settings/profile')
      .then((r) => r.json())
      .then((data) => {
        if (data.profile?.name) setOperatorName(data.profile.name)
        if (data.profile?.role) setOperatorRole(data.profile.role)
      })
      .catch(() => {})

    fetch('/api/agy/history')
      .then((r) => r.json())
      .then((data) => {
        if (data.history && data.history.length > 0) {
          setMessages(data.history)
        }
      })
      .catch(() => {})

    // SSE listener for new chat messages
    try {
      const sse = new EventSource('/api/events/stream')
      sse.addEventListener('chat_message', (ev: MessageEvent) => {
        try {
          const msg = JSON.parse(ev.data)
          setMessages((prev) => {
            if (prev.some((m) => m.id === msg.id)) return prev
            return [...prev, msg]
          })
        } catch {
          // ignore
        }
      })
      return () => sse.close()
    } catch {
      // ignore
    }
  }, [])

  const handleSendMessage = async (textToSend?: string) => {
    const text = (textToSend || inputText).trim()
    if (!text || loading) return

    const tempUserMsg: ChatMessage = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      name: operatorName,
      role: operatorRole,
      text,
      timestamp: new Date().toLocaleTimeString(),
      status: 'sent',
    }

    setMessages((prev) => [...prev, tempUserMsg])
    setInputText('')
    setLoading(true)

    try {
      const res = await fetch('/api/agy/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      })
      const data = await res.json()
      if (data.success && data.history) {
        setMessages(data.history)
      } else if (data.reply) {
        setMessages((prev) => [...prev, data.reply])
      }
    } catch (e: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          sender: 'agy',
          name: 'Antigravity AGY Runtime',
          role: 'Error Reporter',
          text: `Error de comunicación con el daemon AGY: ${e.message}`,
          timestamp: new Date().toLocaleTimeString(),
          status: 'error',
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const slashShortcuts = [
    { label: '/goal', prompt: '/goal Implementar contratos SellableUnit e invariantes DR-INV-001' },
    { label: '/plan', prompt: '/plan Síntesis del DAG de Kahn en 4 oleadas' },
    { label: '/boost', prompt: '/boost Analizar arquitectura y verificar cobertura Pytest 31/31' },
    { label: '/grill-me', prompt: '/grill-me Evaluar compuertas HITL y riesgos en Railway' },
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
                Consola Conversacional de Inteligencia Artificial (AGY Runtime)
              </h2>
              <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                agy.exe ACTIVO
              </span>
            </div>
            <p className="text-xs text-zinc-400">
              Interacción directa con el modelo de lenguaje de Google Antigravity ejecutado en el host
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              setMessages([
                {
                  id: 'init-reset',
                  sender: 'agy',
                  name: 'Antigravity AGY Runtime',
                  role: 'AI Model / System Engine',
                  text: 'Sesión reiniciada. ¿En qué plan de sprint o arquitectura trabajamos hoy?',
                  timestamp: new Date().toLocaleTimeString(),
                },
              ])
            }}
            className="px-3 py-1.5 rounded-xl bg-zinc-900 border border-[#1b2533] hover:bg-zinc-800 text-xs text-zinc-300 flex items-center gap-1.5 transition"
            title="Limpiar conversación"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reiniciar</span>
          </button>
        </div>
      </div>

      {/* Slash commands quick pills */}
      <div className="flex items-center gap-2 px-6 py-2 bg-[#090d13] border-b border-[#1b2533]/60 overflow-x-auto text-xs">
        <span className="text-[11px] font-mono text-zinc-500 uppercase tracking-wider shrink-0 flex items-center gap-1">
          <Terminal className="w-3 h-3 text-emerald-400" />
          Atajos:
        </span>
        {slashShortcuts.map((sc) => (
          <button
            key={sc.label}
            onClick={() => handleSendMessage(sc.prompt)}
            className="px-2.5 py-1 rounded-lg bg-zinc-900/80 border border-zinc-800 hover:border-emerald-500/50 hover:bg-emerald-500/10 text-[11px] font-mono text-zinc-300 hover:text-emerald-300 transition shrink-0"
          >
            <span className="text-emerald-400 font-bold">{sc.label}</span>
          </button>
        ))}
      </div>

      {/* Messages Viewport */}
      <div className="flex-1 overflow-y-auto custom-scroll p-6 space-y-4">
        {messages.map((msg) => {
          const isUser = msg.sender === 'user'
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

              {/* Message Bubble */}
              <div
                className={`flex flex-col gap-1 rounded-2xl p-4 text-xs leading-relaxed ${
                  isUser
                    ? 'bg-blue-600/15 border border-blue-500/30 text-blue-50'
                    : 'bg-[#090e16] border border-[#1b2533] text-zinc-200 shadow-md'
                }`}
              >
                <div className="flex items-center justify-between gap-3 border-b border-white/5 pb-1.5 mb-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white text-[11px]">{msg.name}</span>
                    <span className="text-[10px] text-zinc-400 font-mono">({msg.role})</span>
                  </div>
                  <span className="text-[10px] text-zinc-500 font-mono">{msg.timestamp}</span>
                </div>

                <div className="whitespace-pre-wrap font-sans text-xs">{msg.text}</div>

                {/* Subagent & Tool indicators */}
                {!isUser && (
                  <div className="mt-2 pt-2 border-t border-white/5 flex items-center gap-2 text-[10px] font-mono text-zinc-500">
                    <ShieldCheck className="w-3 h-3 text-emerald-400" />
                    <span>Contratos auditados: DR-INV-001 &bull; DR-PAY-001</span>
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
              <span>Antigravity CLI (agy.exe) está procesando la solicitud...</span>
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
              placeholder="Instrucción al modelo de IA en AGY (e.g. /goal Diseñar arquitectura de pagos)..."
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
