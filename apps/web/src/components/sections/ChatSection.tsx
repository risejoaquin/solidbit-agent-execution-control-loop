import React, { useState, useEffect, useRef } from 'react'

interface CQRSCommandMessage {
  id: string
  role: 'user' | 'system_ack' | 'error'
  content: string
  job_id?: string
  status?: string
  timestamp: string
}

export const ChatSection: React.FC = () => {
  const [messages, setMessages] = useState<CQRSCommandMessage[]>([
    {
      id: 'init-msg',
      role: 'system_ack',
      content: 'EOP Command Hub en línea. Envía instrucciones de sprint o comandos CQRS para despachar tareas desatendidas.',
      status: 'READY',
      timestamp: new Date().toLocaleTimeString('es-ES'),
    },
  ])
  const [inputText, setInputText] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Despacho de Intención CQRS (Write Model Asíncrono)
  const handleSendCommand = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    const text = inputText.trim()
    if (!text || isSubmitting) return

    const userMsgId = `cmd-${Date.now()}`
    const userMsg: CQRSCommandMessage = {
      id: userMsgId,
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString('es-ES'),
    }

    // Inyección optimista del mensaje del usuario
    setMessages((prev) => [...prev, userMsg])
    setInputText('')
    setIsSubmitting(true)

    // Compilación estructurada de la orden según cqrsContract
    let payload: Record<string, any>
    if (text.startsWith('{') && text.endsWith('}')) {
      try {
        payload = JSON.parse(text)
      } catch {
        payload = { command: 'EXECUTE_INTENT', prompt: text }
      }
    } else {
      payload = {
        command: 'EXECUTE_WAVE',
        job_id: userMsgId,
        project_id: 'stable-ecommerce',
        manifest: {
          id: `pkg-${Date.now()}`,
          intent: text,
          phase: 1,
          tasks: [text],
        },
        priority: 0,
      }
    }

    try {
      // Petición al Local Gateway del demonio antigravity
      const res = await fetch('/api/orchestrator/enqueue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const data = await res.json()

      if (res.ok && data.accepted) {
        // Inyección instantánea del ACK del sistema (Zero-Blocking UX)
        setMessages((prev) => [
          ...prev,
          {
            id: `ack-${Date.now()}`,
            role: 'system_ack',
            content: `Intención admitida en el orquestador. Tareas encoladas de forma desatendida.`,
            job_id: data.job_id,
            status: data.status || 'QUEUED',
            timestamp: new Date().toLocaleTimeString('es-ES'),
          },
        ])
      } else {
        setMessages((prev) => [
          ...prev,
          {
            id: `err-${Date.now()}`,
            role: 'error',
            content: `Rechazo de Ingress: ${data.message || 'Error al validar payload CQRS.'}`,
            timestamp: new Date().toLocaleTimeString('es-ES'),
          },
        ])
      }
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: 'error',
          content: `Fallo de transporte al Local Gateway: ${err.message}`,
          timestamp: new Date().toLocaleTimeString('es-ES'),
        },
      ])
    } finally {
      // Liberación inmediata del input
      setIsSubmitting(false)
      inputRef.current?.focus()
    }
  }

  return (
    <div className="flex flex-col h-full w-full bg-[#000000] rounded-lg border border-white/8 overflow-hidden select-none">
      {/* Header del Command Hub */}
      <div className="h-12 border-b border-white/8 px-4 flex items-center justify-between bg-[#0a0a0a] shrink-0">
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75">
            <polyline points="4 17 10 11 4 5" />
            <line x1="12" x2="20" y1="19" y2="19" />
          </svg>
          <span className="text-xs font-semibold text-white tracking-wide uppercase">Command Hub</span>
          <span className="text-[10px] font-mono text-zinc-500">· CQRS Write Model (Asíncrono)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-[10px] font-mono text-zinc-400">Zero-Blocking Local Gateway</span>
        </div>
      </div>

      {/* Flujo de Mensajes y ACKs */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scroll">
        {messages.map((m) => {
          if (m.role === 'user') {
            return (
              <div key={m.id} className="flex justify-end">
                <div className="max-w-[80%] bg-[#0a0a0a] border border-white/8 rounded-lg p-3 text-right">
                  <div className="text-xs text-zinc-200 font-mono text-left break-words">{m.content}</div>
                  <span className="text-[9px] text-zinc-600 font-mono mt-1.5 block">{m.timestamp}</span>
                </div>
              </div>
            )
          }

          if (m.role === 'error') {
            return (
              <div key={m.id} className="flex justify-start">
                <div className="max-w-[85%] bg-red-500/10 border border-red-500/20 rounded-lg p-3">
                  <div className="flex items-center gap-2 text-xs text-red-400 font-medium">
                    <svg className="w-3.5 h-3.5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10" />
                      <line x1="12" x2="12" y1="8" y2="12" />
                      <line x1="12" x2="12.01" y1="16" y2="16" />
                    </svg>
                    <span>{m.content}</span>
                  </div>
                  <span className="text-[9px] text-red-400/60 font-mono mt-1 block">{m.timestamp}</span>
                </div>
              </div>
            )
          }

          // ACK del Sistema (Minimalista, sin cajas pesadas)
          return (
            <div key={m.id} className="flex justify-start py-1">
              <div className="max-w-[85%] flex items-start gap-2.5 text-left">
                <div className="mt-0.5 w-4 h-4 rounded bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center shrink-0">
                  <svg className="w-2.5 h-2.5 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                </div>
                <div>
                  <p className="text-xs text-zinc-300 font-sans leading-relaxed">{m.content}</p>
                  <div className="flex items-center gap-2 mt-1">
                    {m.job_id && (
                      <span className="text-[10px] font-mono text-emerald-400/90 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
                        {m.job_id}
                      </span>
                    )}
                    {m.status && (
                      <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-wider">
                        Estado: {m.status}
                      </span>
                    )}
                    <span className="text-[9px] text-zinc-600 font-mono">{m.timestamp}</span>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Dock Anclado al Fondo */}
      <div className="p-3 border-t border-white/8 bg-[#0a0a0a] shrink-0">
        <form onSubmit={handleSendCommand} className="flex items-center gap-2">
          <div className="relative flex-1">
            <input
              ref={inputRef}
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Ingresa una instrucción de orquestación o comando CQRS..."
              className="w-full bg-[#000000] border border-white/8 rounded px-3.5 py-2 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-white/20 transition font-sans"
              disabled={isSubmitting}
            />
          </div>

          <button
            type="submit"
            disabled={!inputText.trim() || isSubmitting}
            className={`px-3.5 py-2 rounded text-xs font-medium flex items-center gap-1.5 transition border ${
              inputText.trim() && !isSubmitting
                ? 'bg-white text-black border-white hover:bg-zinc-200 cursor-pointer'
                : 'bg-zinc-900 text-zinc-600 border-white/8 cursor-not-allowed'
            }`}
          >
            <span>Despachar</span>
            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="22" x2="11" y1="2" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </form>
        <div className="flex items-center justify-between mt-2 px-1 text-[10px] text-zinc-500 font-mono">
          <span>Presiona Enter para enviar al Local Gateway</span>
          <span>El seguimiento de progreso se delega al Dashboard</span>
        </div>
      </div>
    </div>
  )
}
