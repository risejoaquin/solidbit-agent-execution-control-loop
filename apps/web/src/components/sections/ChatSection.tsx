import React, { useState, useEffect, useRef } from 'react'
import { SoftPhaseMultiVoice, AVAILABLE_VOICES } from '../SoftPhaseMultiVoice'
import { CampaignVisualBuilder } from '../CampaignVisualBuilder'

interface CQRSCommandMessage {
  id: string
  role: 'user' | 'system_ack' | 'error'
  content: string
  job_id?: string
  status?: string
  timestamp: string
}

export const ChatSection: React.FC = () => {
  const [messages, setMessages] = useState<CQRSCommandMessage[]>([])
  const [hasInteracted, setHasInteracted] = useState(false)
  const [inputText, setInputText] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [selectedVoiceIds, setSelectedVoiceIds] = useState<string[]>(['sec-auditor', 'arch-strict', 'data-vega'])
  const [isMultiVoiceOpen, setIsMultiVoiceOpen] = useState(false)
  const [isCampaignBuilderOpen, setIsCampaignBuilderOpen] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const toggleVoice = (id: string) => {
    setSelectedVoiceIds((prev) =>
      prev.includes(id) ? (prev.length > 1 ? prev.filter((v) => v !== id) : prev) : [...prev, id]
    )
  }

  const handleSuggestionClick = (promptText: string) => {
    setInputText(promptText)
    inputRef.current?.focus()
  }

  // Despacho de Intención CQRS (Write Model Asíncrono con inyección Multi-Voice)
  const handleSendCommand = async (e?: React.FormEvent, directText?: string) => {
    if (e) e.preventDefault()
    const text = (directText || inputText).trim()
    if (!text || isSubmitting) return

    // Anotar que el usuario ha interactuado para desvanecer la bienvenida (Boceto Foto 1)
    setHasInteracted(true)

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

    // Compilación estructurada de directivas multivoz
    const activeDirectives = AVAILABLE_VOICES.filter((v) => selectedVoiceIds.includes(v.id)).map(
      (v) => `[${v.name} (${v.role})]: ${v.systemPromptDirective}`
    )

    let payload: Record<string, any>
    if (text.startsWith('{') && text.endsWith('}')) {
      try {
        payload = JSON.parse(text)
        if (payload.payload) {
          payload.payload.multivoice_directives = activeDirectives
        }
      } catch {
        payload = { command: 'EXECUTE_INTENT', prompt: text, multivoice_directives: activeDirectives }
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
          multivoice_directives: activeDirectives,
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

      if (res.ok) {
        setMessages((prev) => [
          ...prev,
          {
            id: `ack-${Date.now()}`,
            role: 'system_ack',
            content: `Intención encolada exitosamente. Job ID: ${data.job_id || userMsgId}. DAG Kahn planificado.`,
            job_id: data.job_id || userMsgId,
            status: 'ACCEPTED',
            timestamp: new Date().toLocaleTimeString('es-ES'),
          },
        ])
      } else {
        setMessages((prev) => [
          ...prev,
          {
            id: `err-${Date.now()}`,
            role: 'error',
            content: `Error al procesar intención: ${data.detail || data.error || 'Gateway rechazó el comando'}`,
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
          content: `Fallo de comunicación con Local Gateway (:8765): ${err.message || 'Error de red'}`,
          timestamp: new Date().toLocaleTimeString('es-ES'),
        },
      ])
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="flex flex-col h-full w-full bg-[#000000] rounded-lg border border-white/8 overflow-hidden select-none text-left">
      {/* Header del Command Hub */}
      <div className="h-12 border-b border-white/8 px-4 flex items-center justify-between bg-[#0a0a0a] shrink-0">
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75">
            <polyline points="4 17 10 11 4 5" />
            <line x1="12" x2="20" y1="19" y2="19" />
          </svg>
          <span className="text-xs font-semibold text-white tracking-wide uppercase font-sans">Command Hub</span>
          <span className="text-[10px] font-mono text-zinc-500 hidden sm:inline">· CQRS Write Model</span>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setIsCampaignBuilderOpen(true)}
            className="px-2.5 py-1 rounded text-[10px] font-mono border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 transition cursor-pointer flex items-center gap-1.5"
          >
            <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <path d="M3 9h18" />
              <path d="M9 21V9" />
            </svg>
            <span className="hidden sm:inline">Diseñar Campaña Visual</span>
            <span className="sm:hidden">Campaña</span>
          </button>

          <button
            type="button"
            onClick={() => setIsMultiVoiceOpen(!isMultiVoiceOpen)}
            className={`px-2.5 py-1 rounded text-[10px] font-mono border transition cursor-pointer flex items-center gap-1.5 ${
              isMultiVoiceOpen
                ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-400'
                : 'bg-[#121212] border-white/8 text-zinc-400 hover:text-white'
            }`}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            <span>Fase Soft: {selectedVoiceIds.length}</span>
            <span className="text-zinc-600">{isMultiVoiceOpen ? '▲' : '▼'}</span>
          </button>

          <div className="hidden sm:flex items-center gap-1.5 pl-2 border-l border-white/8">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-[10px] font-mono text-zinc-400">Gateway Activo</span>
          </div>
        </div>
      </div>

      {/* Selector Desplegable de Multivoces (Soft Phase) */}
      {isMultiVoiceOpen && (
        <div className="p-3 bg-[#0a0a0a] border-b border-white/8 shrink-0">
          <SoftPhaseMultiVoice
            selectedVoiceIds={selectedVoiceIds}
            onToggleVoice={toggleVoice}
          />
        </div>
      )}

      {/* Flujo de Mensajes y ACKs */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scroll">
        {/* Splash de Bienvenida Efímero (Anotación literal de la Foto 1 del Boceto: "Desaparece el mensaje de bienvenida cuando se entrega el primer mensaje") */}
        <div
          className={`transition-all duration-300 ease-in-out ${
            hasInteracted || messages.length > 0
              ? 'opacity-0 max-h-0 pointer-events-none -my-2 overflow-hidden'
              : 'opacity-100 max-h-[500px] mb-4'
          }`}
        >
          <div className="bg-[#0a0a0a] border border-white/8 rounded-xl p-4 sm:p-5 shadow-lg relative overflow-hidden">
            <div className="flex items-start justify-between gap-3 mb-3">
              <div>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider font-sans">
                    Bienvenida · SolidBit EOP Command Hub
                  </h3>
                </div>
                <p className="text-xs text-zinc-400 mt-1 font-sans leading-relaxed">
                  Diseña tus waves y campañas desatendidas. Establece cómo debe actuar la IA y qué debe hacer con el flujo automatizado de los videos 1, 2 y 3.
                </p>
              </div>
              <span className="text-[9px] font-mono text-zinc-500 bg-white/5 border border-white/10 px-2 py-0.5 rounded shrink-0">
                FOTO 1 BOCETO
              </span>
            </div>

            {/* Sugerencias Rápidas de 1 Toque */}
            <div className="space-y-1.5 pt-2 border-t border-white/8">
              <span className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider block mb-2">
                Sugerencias Rápidas de Inicio (1 Toque):
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => handleSuggestionClick('Planear Wave de Inventario con balance transaccional estricto en SQLite WAL bajo invariante DR-INV-001.')}
                  className="p-2.5 rounded-lg bg-[#121212] hover:bg-zinc-800 border border-white/8 hover:border-emerald-500/40 text-left transition cursor-pointer group"
                >
                  <div className="text-xs font-semibold text-zinc-200 group-hover:text-emerald-400 font-sans">
                    📦 Planear Wave de Inventario
                  </div>
                  <div className="text-[10px] text-zinc-500 font-mono mt-0.5 truncate">
                    Invariantes DR-INV-001 & WAL
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => handleSuggestionClick('Auditar contratos ACID de pago DR-PAY-001 y verificar compatibilidad de esquema con microservicios.')}
                  className="p-2.5 rounded-lg bg-[#121212] hover:bg-zinc-800 border border-white/8 hover:border-emerald-500/40 text-left transition cursor-pointer group"
                >
                  <div className="text-xs font-semibold text-zinc-200 group-hover:text-emerald-400 font-sans">
                    🛡️ Auditar Contratos ACID
                  </div>
                  <div className="text-[10px] text-zinc-500 font-mono mt-0.5 truncate">
                    DR-PAY-001 & Cero-Fuga
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => handleSuggestionClick('Ejecutar auditoría constitucional de seguridad con Centinela y preparar compuerta Gate 5 HMAC.')}
                  className="p-2.5 rounded-lg bg-[#121212] hover:bg-zinc-800 border border-white/8 hover:border-emerald-500/40 text-left transition cursor-pointer group"
                >
                  <div className="text-xs font-semibold text-zinc-200 group-hover:text-emerald-400 font-sans">
                    🔒 Revisar Políticas Gate 5
                  </div>
                  <div className="text-[10px] text-zinc-500 font-mono mt-0.5 truncate">
                    Hard Deny & HMAC Seal
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Mensajes del Chat */}
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
                  <div className="flex items-center gap-2 text-xs text-red-400 font-medium font-sans">
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

          // ACK del Sistema
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
                      <span className="text-[9px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-1 py-0.5 rounded">
                        Job: {m.job_id.substring(0, 12)}
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
          <span>Enter para enviar · {selectedVoiceIds.length} directivas soft activas</span>
          <span>Zero-Blocking ACK</span>
        </div>
      </div>

      {/* Modal Visual Campaign Builder (Fase 3 EOP) */}
      <CampaignVisualBuilder
        isOpen={isCampaignBuilderOpen}
        onClose={() => setIsCampaignBuilderOpen(false)}
        onDispatched={(jobId) => {
          setHasInteracted(true)
          setMessages((prev) => [
            ...prev,
            {
              id: `builder-ack-${Date.now()}`,
              role: 'system_ack',
              content: `Campaña visual despachada exitosamente vía Command Hub. Job ID: ${jobId}`,
              job_id: jobId,
              status: 'ENQUEUED',
              timestamp: new Date().toLocaleTimeString('es-ES'),
            },
          ])
        }}
      />
    </div>
  )
}
