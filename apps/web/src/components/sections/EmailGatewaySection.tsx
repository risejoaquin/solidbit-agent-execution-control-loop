import React, { useState, useEffect } from 'react'
import {
  Mail,
  Send,
  Key,
  ShieldCheck,
  CheckCircle2,
  Copy,
  Check,
  RefreshCw,
  AlertCircle,
  Inbox,
  Lock,
  ArrowUpRight,
  ArrowDownLeft,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'
import { formatSmartDateTime } from '../../utils/dateFormat'

interface EmailConfig {
  sender_email: string
  operator_email: string
  authorized_senders: string[]
  resend_status: string
  masked_api_key: string
  security: {
    token_required: boolean
    svix_signature: boolean
    sender_allowlist: boolean
  }
  inbound_webhook_url: string
  webhook_token: string
  logs_count: number
  recent_logs: Array<{
    id: string
    direction: 'OUTBOUND' | 'INBOUND'
    from: string
    to: string
    subject: string
    status: string
    timestamp: string
    summary?: string
    task_id?: string
  }>
}

export const EmailGatewaySection: React.FC = () => {
  const [config, setConfig] = useState<EmailConfig | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [saving, setSaving] = useState<boolean>(false)
  const [sendingTest, setSendingTest] = useState<boolean>(false)
  const [copiedWebhook, setCopiedWebhook] = useState<boolean>(false)
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(
    null
  )
  const [showWebhookDetails, setShowWebhookDetails] = useState<boolean>(false)

  // Edit fields
  const [senderEmail, setSenderEmail] = useState<string>('')
  const [operatorEmail, setOperatorEmail] = useState<string>('')
  const [resendApiKey, setResendApiKey] = useState<string>('')
  const [showKeyInput, setShowKeyInput] = useState<boolean>(false)

  const loadConfig = async () => {
    try {
      setLoading(true)
      const res = await fetch('/api/email/config')
      if (res.ok) {
        const data: EmailConfig = await res.json()
        setConfig(data)
        setSenderEmail(data.sender_email)
        setOperatorEmail(data.operator_email)
      }
    } catch (err: any) {
      console.error('Error fetching email config:', err)
      setFeedback({ type: 'error', message: 'No se pudo conectar con el servicio de correo.' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadConfig()
  }, [])

  // Poka-Yoke real-time email & key validation
  const isSenderValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(senderEmail.trim())
  const isOperatorValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(operatorEmail.trim())
  const isKeyValid = !showKeyInput || !resendApiKey.trim() || resendApiKey.trim().startsWith('re_')

  const handleSaveConfig = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isSenderValid || !isOperatorValid || !isKeyValid) return
    setSaving(true)
    setFeedback(null)
    try {
      const payload: Record<string, string> = {
        sender_email: senderEmail.trim(),
        operator_email: operatorEmail.trim(),
      }
      if (resendApiKey.trim()) {
        payload.resend_api_key = resendApiKey.trim()
      }

      const res = await fetch('/api/email/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const result = await res.json()
      if (result.success) {
        setFeedback({
          type: 'success',
          message: result.message || 'Configuración de correo guardada correctamente.',
        })
        setResendApiKey('')
        setShowKeyInput(false)
        await loadConfig()
      } else {
        setFeedback({
          type: 'error',
          message: result.error || 'Error al actualizar configuración.',
        })
      }
    } catch (err: any) {
      setFeedback({ type: 'error', message: err.message || 'Fallo de red al guardar.' })
    } finally {
      setSaving(false)
    }
  }

  const handleSendTestEmail = async () => {
    setSendingTest(true)
    setFeedback(null)
    try {
      const res = await fetch('/api/email/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
      const result = await res.json()
      if (result.success) {
        setFeedback({
          type: 'success',
          message: `Correo de prueba enviado a ${config?.operator_email} vía Resend API.`,
        })
        await loadConfig()
      } else {
        setFeedback({
          type: 'error',
          message: result.error || 'Error enviando correo de prueba.',
        })
      }
    } catch (err: any) {
      setFeedback({ type: 'error', message: `Fallo al enviar: ${err.message}` })
    } finally {
      setSendingTest(false)
    }
  }

  const handleCopyWebhook = () => {
    if (!config?.inbound_webhook_url) return
    navigator.clipboard.writeText(config.inbound_webhook_url)
    setCopiedWebhook(true)
    setTimeout(() => setCopiedWebhook(false), 2000)
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto animate-fade-in text-left pb-12">
      {/* 1. Header Simplificado (1 CTA Primario: Enviar Correo de Prueba) */}
      <div className="p-5 sm:p-6 rounded-2xl bg-zinc-950 border border-zinc-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-start sm:items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-zinc-900 border border-zinc-750 flex items-center justify-center text-white shrink-0">
            <Mail className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold text-white tracking-tight">
                Notificaciones por Correo (Resend)
              </h2>
              <span
                className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold border ${
                  config?.resend_status === 'ACTIVE'
                    ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                    : 'bg-zinc-900 text-zinc-400 border-zinc-800'
                }`}
              >
                {config?.resend_status === 'ACTIVE' ? 'CONECTADO A RESEND' : 'MODO LOCAL'}
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              Recibe resúmenes de sprints y enlaces para aprobar cambios desde tu teléfono o correo.
            </p>
          </div>
        </div>

        <button
          type="button"
          id="btn-send-test-email"
          onClick={handleSendTestEmail}
          disabled={sendingTest}
          className="px-4 py-2.5 rounded-xl bg-white hover:bg-zinc-200 text-black font-bold text-xs flex items-center gap-2 transition shadow-sm cursor-pointer disabled:opacity-50 self-start sm:self-auto"
        >
          <Send className="w-3.5 h-3.5" />
          <span>{sendingTest ? 'Enviando Correo...' : 'Enviar Correo de Prueba Ahora'}</span>
        </button>
      </div>

      {/* Feedback Banner */}
      {feedback && (
        <div
          className={`p-4 rounded-xl border text-xs flex items-center justify-between gap-3 ${
            feedback.type === 'success'
              ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-200'
              : 'bg-red-950/40 border-red-500/40 text-red-200'
          }`}
        >
          <div className="flex items-center gap-2.5">
            {feedback.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            )}
            <span className="font-medium">{feedback.message}</span>
          </div>
          <button
            type="button"
            onClick={() => setFeedback(null)}
            className="text-xs underline cursor-pointer"
          >
            Cerrar
          </button>
        </div>
      )}

      {/* 2. Formulario Principal con Validación Poka-Yoke en Tiempo Real */}
      <div className="p-5 sm:p-6 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-5">
        <div className="flex items-center justify-between border-b border-zinc-850 pb-3">
          <div className="flex items-center gap-2">
            <Key className="w-4 h-4 text-white" />
            <h3 className="text-sm font-bold text-white">Direcciones de Envío y Recepción</h3>
          </div>
          <button
            type="button"
            onClick={loadConfig}
            disabled={loading}
            className="text-xs text-zinc-400 hover:text-white flex items-center gap-1 cursor-pointer"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
            <span>Actualizar</span>
          </button>
        </div>

        <form onSubmit={handleSaveConfig} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-zinc-300">
                  Correo Remitente (Verificado en Resend)
                </label>
                <span
                  className={`text-[11px] flex items-center gap-1 ${
                    isSenderValid ? 'text-emerald-400' : 'text-amber-400'
                  }`}
                >
                  <CheckCircle2 className="w-3 h-3" />
                  {isSenderValid ? 'Válido' : 'Formato inválido'}
                </span>
              </div>
              <input
                type="email"
                value={senderEmail}
                onChange={(e) => setSenderEmail(e.target.value)}
                required
                className="w-full px-3.5 py-2.5 rounded-xl bg-black border border-zinc-800 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-white font-mono"
                placeholder="notificaciones@tudominio.com"
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-zinc-300">
                  Tu Correo Personal (Destinatario)
                </label>
                <span
                  className={`text-[11px] flex items-center gap-1 ${
                    isOperatorValid ? 'text-emerald-400' : 'text-amber-400'
                  }`}
                >
                  <CheckCircle2 className="w-3 h-3" />
                  {isOperatorValid ? 'Válido' : 'Formato inválido'}
                </span>
              </div>
              <input
                type="email"
                value={operatorEmail}
                onChange={(e) => setOperatorEmail(e.target.value)}
                required
                className="w-full px-3.5 py-2.5 rounded-xl bg-black border border-zinc-800 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-white font-mono"
                placeholder="tu@correo.com"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold text-zinc-300">Resend API Key</label>
              <button
                type="button"
                onClick={() => setShowKeyInput(!showKeyInput)}
                className="text-xs text-zinc-400 hover:text-white underline cursor-pointer"
              >
                {showKeyInput ? 'Cancelar cambio de clave' : 'Actualizar API Key'}
              </button>
            </div>

            {showKeyInput ? (
              <div className="space-y-1.5">
                <input
                  type="password"
                  value={resendApiKey}
                  onChange={(e) => setResendApiKey(e.target.value)}
                  placeholder="re_..."
                  className="w-full px-3.5 py-2.5 rounded-xl bg-black border border-zinc-700 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-white font-mono"
                />
                <span
                  className={`text-[11px] flex items-center gap-1 ${
                    isKeyValid ? 'text-emerald-400' : 'text-amber-400'
                  }`}
                >
                  <CheckCircle2 className="w-3 h-3" />
                  {isKeyValid
                    ? 'Formato de clave Resend válido (comienza con re_)'
                    : 'La clave debe comenzar con "re_"'}
                </span>
              </div>
            ) : (
              <div className="px-3.5 py-2.5 rounded-xl bg-black border border-zinc-850 text-xs text-zinc-300 font-mono flex items-center justify-between">
                <span>{config?.masked_api_key || 'No configurada'}</span>
                <Lock className="w-3.5 h-3.5 text-zinc-500" />
              </div>
            )}
          </div>

          <div className="pt-1">
            <button
              type="submit"
              disabled={saving || !isSenderValid || !isOperatorValid || !isKeyValid}
              className="px-5 py-2.5 rounded-xl bg-zinc-900 border border-zinc-750 hover:bg-zinc-800 text-xs text-white font-bold transition cursor-pointer disabled:opacity-40"
            >
              {saving ? 'Guardando...' : 'Guardar Configuración de Correo'}
            </button>
          </div>
        </form>
      </div>

      {/* 3. Historial de Correos Enviados y Recibidos */}
      <div className="p-5 sm:p-6 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-4">
        <div className="flex items-center justify-between border-b border-zinc-850 pb-3">
          <div className="flex items-center gap-2">
            <Mail className="w-4 h-4 text-white" />
            <h3 className="text-sm font-bold text-white">Historial de Correos</h3>
          </div>
          <span className="text-xs font-mono text-zinc-400">
            {config?.recent_logs.length || 0} enviados/recibidos
          </span>
        </div>

        {config?.recent_logs.length === 0 ? (
          <div className="py-6 text-center space-y-1.5">
            <Inbox className="w-7 h-7 text-zinc-600 mx-auto" />
            <p className="text-xs text-zinc-400">
              No se han enviado correos en esta sesión todavía.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left font-mono">
              <thead>
                <tr className="border-b border-zinc-800 text-[10px] text-zinc-500 uppercase">
                  <th className="py-2.5 px-3">Tipo</th>
                  <th className="py-2.5 px-3">Fecha</th>
                  <th className="py-2.5 px-3">Destinatario</th>
                  <th className="py-2.5 px-3">Asunto</th>
                  <th className="py-2.5 px-3 text-right">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-850">
                {config?.recent_logs.map((log) => (
                  <tr key={log.id} className="hover:bg-zinc-900/40">
                    <td className="py-3 px-3">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-zinc-900 border border-zinc-800 text-zinc-200">
                        {log.direction === 'OUTBOUND' ? (
                          <>
                            <ArrowUpRight className="w-3 h-3 text-emerald-400" /> ENVIADO
                          </>
                        ) : (
                          <>
                            <ArrowDownLeft className="w-3 h-3 text-zinc-400" /> RECIBIDO
                          </>
                        )}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-zinc-400">{formatSmartDateTime(log.timestamp)}</td>
                    <td className="py-3 px-3 text-zinc-300">{log.to}</td>
                    <td className="py-3 px-3 text-white font-sans font-medium">{log.subject}</td>
                    <td className="py-3 px-3 text-right">
                      <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                        {log.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* 4. Divulgación Progresiva: Opciones Avanzadas de Webhook Entrante */}
      <div className="rounded-2xl bg-zinc-950 border border-zinc-800 overflow-hidden">
        <button
          type="button"
          onClick={() => setShowWebhookDetails(!showWebhookDetails)}
          className="w-full p-5 flex items-center justify-between hover:bg-zinc-900/50 transition cursor-pointer text-left"
        >
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-zinc-900 border border-zinc-750 flex items-center justify-center text-zinc-300">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-xs font-bold text-white">
                Opciones Avanzadas: Webhook de Recepción de Correos (Inbound)
              </h3>
              <p className="text-[11px] text-zinc-400 mt-0.5">
                Configuración opcional para responder correos y disparar tareas automáticamente.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1.5 text-zinc-400 text-xs font-mono">
            <span>{showWebhookDetails ? 'Ocultar' : 'Mostrar'}</span>
            {showWebhookDetails ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </div>
        </button>

        {showWebhookDetails && (
          <div className="p-5 pt-0 border-t border-zinc-850 space-y-3 mt-3">
            <label className="block text-xs font-semibold text-zinc-300">
              URL del Webhook Entrante:
            </label>
            <div className="flex items-center gap-2">
              <div className="flex-1 px-3 py-2 rounded-xl bg-black border border-zinc-800 text-[11px] font-mono text-zinc-300 truncate select-all">
                {config?.inbound_webhook_url || 'Cargando URL...'}
              </div>
              <button
                type="button"
                onClick={handleCopyWebhook}
                className="px-3 py-2 rounded-xl bg-zinc-900 border border-zinc-750 hover:bg-zinc-800 text-xs text-white flex items-center gap-1.5 transition cursor-pointer shrink-0"
              >
                {copiedWebhook ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedWebhook ? 'Copiado' : 'Copiar'}</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
