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
  Sparkles,
} from 'lucide-react'
import { formatSmartDateTime, formatRelativeTime } from '../../utils/dateFormat'

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
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null)

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
      setFeedback({ type: 'error', message: 'No se pudo conectar con el servicio Email Gateway' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadConfig()
  }, [])

  const handleSaveConfig = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setFeedback(null)
    try {
      const payload: Record<string, string> = {
        sender_email: senderEmail,
        operator_email: operatorEmail,
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
        setFeedback({ type: 'success', message: result.message || 'Configuración guardada correctamente.' })
        setResendApiKey('')
        setShowKeyInput(false)
        await loadConfig()
      } else {
        setFeedback({ type: 'error', message: result.error || 'Error al actualizar configuración.' })
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
          message: `Reporte de prueba enviado exitosamente a ${config?.operator_email}. ID: ${result.result?.id || 'OK'}`,
        })
        await loadConfig()
      } else {
        setFeedback({
          type: 'error',
          message: result.error || 'Error enviando email de prueba.',
        })
      }
    } catch (err: any) {
      setFeedback({ type: 'error', message: `Fallo al invocar API de envío: ${err.message}` })
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
    <div className="space-y-6 max-w-6xl mx-auto animate-fade-in text-left">
      {/* Header Banner */}
      <div className="p-6 rounded-3xl bg-zinc-950 border border-zinc-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-zinc-900 border border-zinc-750 flex items-center justify-center text-white">
              <Mail className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white tracking-tight">
                  Email Gateway & Automatización Soberana
                </h2>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-zinc-900 text-zinc-300 border border-zinc-750">
                  RESEND BI-DIRECCIONAL
                </span>
              </div>
              <p className="text-xs text-zinc-400">
                Canal autónomo para informes de cierre de sprint, compuertas de decisión HITL y disparo remoto vía email.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            type="button"
            onClick={loadConfig}
            disabled={loading}
            className="px-3.5 py-2 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-xs text-zinc-300 hover:text-white flex items-center gap-2 transition cursor-pointer"
            title="Refrescar configuración"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refrescar</span>
          </button>
          <button
            type="button"
            id="btn-send-test-email"
            onClick={handleSendTestEmail}
            disabled={sendingTest}
            className="px-4 py-2 rounded-xl bg-white hover:bg-zinc-200 text-black font-bold text-xs flex items-center gap-2 transition shadow-sm cursor-pointer disabled:opacity-50"
          >
            <Send className="w-3.5 h-3.5" />
            <span>{sendingTest ? 'Enviando Reporte...' : 'Enviar Email de Prueba'}</span>
          </button>
        </div>
      </div>

      {/* Global Feedback Banner */}
      {feedback && (
        <div
          className={`p-4 rounded-2xl border text-xs flex items-center justify-between gap-3 ${
            feedback.type === 'success'
              ? 'bg-zinc-900 border-zinc-700 text-white'
              : 'bg-zinc-900 border-zinc-700 text-zinc-300'
          }`}
        >
          <div className="flex items-center gap-2.5">
            {feedback.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-white shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-zinc-400 shrink-0" />
            )}
            <span className="font-medium">{feedback.message}</span>
          </div>
          <button
            type="button"
            onClick={() => setFeedback(null)}
            className="text-zinc-500 hover:text-white font-mono text-xs px-2 py-1 rounded"
          >
            Cerrar
          </button>
        </div>
      )}

      {/* Grid: 2 Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Outbound & Resend Settings */}
        <div className="p-6 rounded-3xl bg-zinc-950 border border-zinc-800 space-y-5">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
            <div className="flex items-center gap-2">
              <Key className="w-4 h-4 text-white" />
              <h3 className="text-sm font-bold text-white">Credenciales y Configuración de Canal</h3>
            </div>
            <span
              className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold ${
                config?.resend_status === 'ACTIVE'
                  ? 'bg-zinc-900 text-white border border-zinc-700'
                  : 'bg-zinc-900 text-zinc-400 border border-zinc-800'
              }`}
            >
              ESTADO: {config?.resend_status || 'DESCONOCIDO'}
            </span>
          </div>

          <form onSubmit={handleSaveConfig} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-zinc-300 mb-1.5">
                Dirección Emisora del Sistema (Sender)
              </label>
              <input
                type="email"
                value={senderEmail}
                onChange={(e) => setSenderEmail(e.target.value)}
                required
                className="w-full px-3.5 py-2.5 rounded-xl bg-zinc-900 border border-zinc-800 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-500 font-mono"
                placeholder="notificaciones@tudominio.com"
              />
              <span className="text-[10px] text-zinc-500 mt-1 block">
                Dominio verificado en Resend para la emisión automatizada.
              </span>
            </div>

            <div>
              <label className="block text-xs font-semibold text-zinc-300 mb-1.5">
                Dirección del Operador Titular (Destination)
              </label>
              <input
                type="email"
                value={operatorEmail}
                onChange={(e) => setOperatorEmail(e.target.value)}
                required
                className="w-full px-3.5 py-2.5 rounded-xl bg-zinc-900 border border-zinc-800 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-500 font-mono"
                placeholder="operador@empresa.com"
              />
              <span className="text-[10px] text-zinc-500 mt-1 block">
                Recibe los resúmenes ejecutivos y enlaces firmados HMAC de compuertas HITL.
              </span>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-semibold text-zinc-300">
                  Resend API Key
                </label>
                <button
                  type="button"
                  onClick={() => setShowKeyInput(!showKeyInput)}
                  className="text-[10px] text-zinc-400 hover:text-white underline cursor-pointer"
                >
                  {showKeyInput ? 'Ocultar edición' : 'Cambiar clave'}
                </button>
              </div>

              {showKeyInput ? (
                <input
                  type="password"
                  value={resendApiKey}
                  onChange={(e) => setResendApiKey(e.target.value)}
                  placeholder="re_..."
                  className="w-full px-3.5 py-2.5 rounded-xl bg-zinc-900 border border-zinc-800 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-500 font-mono"
                />
              ) : (
                <div className="px-3.5 py-2.5 rounded-xl bg-zinc-900/60 border border-zinc-800 text-xs text-zinc-400 font-mono flex items-center justify-between">
                  <span>{config?.masked_api_key || 'No configurada'}</span>
                  <Lock className="w-3.5 h-3.5 text-zinc-500" />
                </div>
              )}
            </div>

            <div className="pt-2">
              <button
                type="submit"
                disabled={saving}
                className="w-full py-2.5 px-4 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-600 hover:bg-zinc-800 text-xs text-white font-semibold transition cursor-pointer disabled:opacity-50"
              >
                {saving ? 'Guardando...' : 'Guardar Cambios de Configuración'}
              </button>
            </div>
          </form>
        </div>

        {/* Right Column: Inbound Webhook Automation */}
        <div className="p-6 rounded-3xl bg-zinc-950 border border-zinc-800 space-y-5">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
            <div className="flex items-center gap-2">
              <Inbox className="w-4 h-4 text-white" />
              <h3 className="text-sm font-bold text-white">Webhook Entrante (Inbound Automation)</h3>
            </div>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-zinc-900 text-zinc-300 border border-zinc-800">
              DISPARO AUTÓNOMO
            </span>
          </div>

          <p className="text-xs text-zinc-400 leading-relaxed">
            Permite a SACL recibir comandos por correo electrónico para disparar revisiones de código, 
            despliegues de sprints o consultas a la flota de agentes desde clientes móviles.
          </p>

          <div className="space-y-2">
            <label className="block text-xs font-semibold text-zinc-300">
              URL del Webhook con Token de Autenticación
            </label>
            <div className="flex items-center gap-2">
              <div className="flex-1 px-3 py-2 rounded-xl bg-zinc-900 border border-zinc-800 text-[11px] font-mono text-zinc-300 truncate select-all">
                {config?.inbound_webhook_url || 'Cargando URL...'}
              </div>
              <button
                type="button"
                id="btn-copy-webhook-url"
                onClick={handleCopyWebhook}
                className="px-3 py-2 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-600 text-xs text-white flex items-center gap-1.5 transition cursor-pointer shrink-0"
                title="Copiar URL"
              >
                {copiedWebhook ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-white" />
                    <span>Copiado</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copiar</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Security Checklist */}
          <div className="p-3.5 rounded-2xl bg-zinc-900/40 border border-zinc-800 space-y-2 text-xs">
            <div className="text-[11px] font-bold text-white flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-white" /> Controles de Seguridad de Inbound
            </div>
            <div className="space-y-1 text-[11px] text-zinc-400 font-mono">
              <div className="flex items-center justify-between">
                <span>Token en Query/Header:</span>
                <span className="text-white font-semibold">Exigido</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Firma Criptográfica Svix:</span>
                <span className="text-zinc-300">
                  {config?.security.svix_signature ? 'Habilitada' : 'Opcional (Token Válido)'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span>Lista Blanca de Remitentes:</span>
                <span className="text-white font-semibold">Estricta ({config?.authorized_senders.length ?? 0} direcciones)</span>
              </div>
            </div>
          </div>

          <div className="text-[11px] text-zinc-500 leading-normal">
            <strong>Modo de uso:</strong> Configura esta URL en el panel de Resend bajo Inbound Webhooks. Los correos entrantes de <code className="text-zinc-300">{operatorEmail}</code> activarán los planes de ejecución correspondientes.
          </div>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="p-6 rounded-3xl bg-zinc-950 border border-zinc-800 space-y-4">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div className="flex items-center gap-2">
            <Mail className="w-4 h-4 text-white" />
            <h3 className="text-sm font-bold text-white">Registro de Auditoría de Correos</h3>
          </div>
          <span className="text-xs font-mono text-zinc-400">
            {config?.recent_logs.length || 0} registros recientes
          </span>
        </div>

        {config?.recent_logs.length === 0 ? (
          <div className="py-8 text-center space-y-2">
            <Inbox className="w-8 h-8 text-zinc-600 mx-auto" />
            <p className="text-xs text-zinc-400">No hay eventos de correo registrados aún en esta sesión.</p>
            <p className="text-[11px] text-zinc-600">
              Presiona "Enviar Email de Prueba" para verificar la integración en vivo con Resend.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto custom-scroll">
            <table className="w-full text-xs text-left">
              <thead>
                <tr className="border-b border-zinc-800 text-[11px] text-zinc-500 font-mono">
                  <th className="py-2.5 px-3">DIRECCIÓN</th>
                  <th className="py-2.5 px-3">FECHA / HORA</th>
                  <th className="py-2.5 px-3">DE / PARA</th>
                  <th className="py-2.5 px-3">ASUNTO</th>
                  <th className="py-2.5 px-3 text-right">ESTADO</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-900 font-mono">
                {config?.recent_logs.map((log) => (
                  <tr key={log.id} className="hover:bg-zinc-900/50 transition">
                    <td className="py-3 px-3">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-zinc-900 border border-zinc-800 text-zinc-200">
                        {log.direction === 'OUTBOUND' ? (
                          <>
                            <ArrowUpRight className="w-3 h-3 text-white" /> SALIENTE
                          </>
                        ) : (
                          <>
                            <ArrowDownLeft className="w-3 h-3 text-zinc-400" /> ENTRANTE
                          </>
                        )}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-zinc-300" title={log.timestamp}>
                      {formatSmartDateTime(log.timestamp)}
                    </td>
                    <td className="py-3 px-3 text-zinc-400">
                      <div>De: {log.from}</div>
                      <div>Para: {log.to}</div>
                    </td>
                    <td className="py-3 px-3 text-white font-medium">
                      {log.subject}
                      {log.summary && (
                        <p className="text-[10px] text-zinc-500 font-sans mt-0.5 truncate max-w-md">
                          {log.summary}
                        </p>
                      )}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <span className="px-2 py-0.5 rounded text-[10px] bg-zinc-800 text-zinc-200 border border-zinc-700">
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
    </div>
  )
}
