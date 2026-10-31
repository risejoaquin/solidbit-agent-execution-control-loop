import React, { useState, useEffect } from 'react'
import {
  ShieldAlert,
  CheckCircle2,
  RotateCcw,
  Loader2,
  FileCode,
  ShieldCheck,
  AlertCircle,
  Terminal,
  Activity,
  Trash2,
  RefreshCw,
  Key,
} from 'lucide-react'
import { StatusBadge } from '../ui/status-badge'
import { LogTerminal } from '../LogTerminal'

export const ExecutionsSection: React.FC = () => {
  const [pendingGates, setPendingGates] = useState<any[]>([])
  const [selectedGate, setSelectedGate] = useState<any>(null)
  const [dossier, setDossier] = useState<any>(null)
  const [runs, setRuns] = useState<any[]>([])
  const [events, setEvents] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [justification, setJustification] = useState(
    'Aprobado tras verificar resultados reales de pruebas unitarias y contratos.'
  )
  const [feedbackBanner, setFeedbackBanner] = useState<{
    type: 'success' | 'error'
    message: string
  } | null>(null)
  const [showDiff, setShowDiff] = useState(false)

  const loadData = async () => {
    try {
      const res = await fetch('/api/gates/pending')
      const data = await res.json()
      if (data && data.gates) {
        setPendingGates(data.gates)
        if (data.gates.length > 0) {
          setSelectedGate(data.gates[0])
          loadDossier(data.gates[0].request_id)
        } else {
          setSelectedGate(null)
          setDossier(null)
        }
      }
    } catch (e) {
      console.warn('Error loading pending gates:', e)
    }

    try {
      const rRes = await fetch('/api/db/rows?table=runs&limit=15')
      const rData = await rRes.json()
      if (rData && rData.rows) setRuns(rData.rows)
    } catch {}

    try {
      const eRes = await fetch('/api/db/rows?table=events&limit=50')
      const eData = await eRes.json()
      if (eData && eData.rows) setEvents(eData.rows)
    } catch {}
  }

  const loadDossier = async (reqId: string) => {
    try {
      const res = await fetch(`/api/gates/dossier?request_id=${encodeURIComponent(reqId)}`)
      const data = await res.json()
      if (data && data.has_gate) {
        setDossier(data)
      }
    } catch (e) {
      console.warn('Error loading dossier:', e)
    }
  }

  useEffect(() => {
    loadData()

    let sse: EventSource | null = null
    const onReload = () => loadData()

    try {
      sse = new EventSource('/api/events/stream')
      sse.addEventListener('gate', onReload)
      sse.addEventListener('gate_decided', onReload)
      sse.addEventListener('gate_requested', onReload)
      sse.addEventListener('approval_required', onReload)
      sse.addEventListener('job', onReload)
      sse.addEventListener('job_enqueued', onReload)
      sse.addEventListener('action_executed', onReload)
      sse.addEventListener('artifact_generated', onReload)
      sse.addEventListener('task_running', onReload)
      sse.addEventListener('agent_event', onReload)
    } catch {
      console.warn('SSE not supported in ExecutionsSection')
    }

    return () => {
      if (sse) {
        sse.removeEventListener('gate', onReload)
        sse.removeEventListener('gate_decided', onReload)
        sse.removeEventListener('gate_requested', onReload)
        sse.removeEventListener('approval_required', onReload)
        sse.removeEventListener('job', onReload)
        sse.removeEventListener('job_enqueued', onReload)
        sse.removeEventListener('action_executed', onReload)
        sse.removeEventListener('artifact_generated', onReload)
        sse.removeEventListener('task_running', onReload)
        sse.removeEventListener('agent_event', onReload)
        sse.close()
      }
    }
  }, [])

  const handleDecision = async (decision: 'APPROVED' | 'REJECTED') => {
    if (!selectedGate) return
    setLoading(true)
    setFeedbackBanner(null)

    try {
      const res = await fetch('/api/gates/decide', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          request_id: selectedGate.request_id,
          decision,
          authorizer: 'Operador Principal',
          rationale: justification,
        }),
      })
      const data = await res.json()
      if (res.ok && data.success) {
        setFeedbackBanner({
          type: 'success',
          message:
            decision === 'APPROVED'
              ? '✓ Entrega autorizada con éxito. El agente continuará con el flujo.'
              : 'Entrega rechazada. Los agentes fueron notificados.',
        })
        await loadData()
      } else {
        setFeedbackBanner({
          type: 'error',
          message: data.message || 'Error al registrar la decisión.',
        })
      }
    } catch (err: any) {
      setFeedbackBanner({ type: 'error', message: 'Error de conexión al enviar la decisión.' })
    } finally {
      setLoading(false)
    }
  }

  const handleLifecycleAction = async (action: 'retry' | 'revert' | 'release') => {
    setActionLoading(action)
    setFeedbackBanner(null)
    try {
      let actionName = 'security_audit'
      let params: any = {}
      if (action === 'revert') {
        actionName = 'revert_fsm'
        params = { fix: true, note: 'Reversión FSM a estado seguro' }
      } else if (action === 'release') {
        actionName = 'release_worktree'
        params = { clean_worktrees: true }
      }

      const res = await fetch('/api/actions/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: actionName, action_type: actionName, params }),
      })
      const data = await res.json()
      if (res.ok) {
        setFeedbackBanner({
          type: 'success',
          message: data.message || 'Operación completada con éxito.',
        })
        await loadData()
      } else {
        setFeedbackBanner({ type: 'error', message: data.error || 'Error al ejecutar la acción.' })
      }
    } catch (e: any) {
      setFeedbackBanner({ type: 'error', message: 'Error de red al ejecutar acción.' })
    } finally {
      setActionLoading(null)
    }
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto animate-fade-in pb-12 text-left">
      {/* Header KISS */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-3xl bg-[#0C0C0E] border border-white/5 shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2.5">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <h1 className="text-lg font-extrabold text-white tracking-tight">
              Aprobaciones & Compuertas Humanas
            </h1>
            <span
              className={`px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold ${
                pendingGates.length > 0
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  : 'bg-zinc-900 text-zinc-400 border border-zinc-750'
              }`}
            >
              {pendingGates.length} {pendingGates.length === 1 ? 'Pendiente' : 'Pendientes'}
            </span>
          </div>
          <p className="text-xs text-zinc-400">
            Punto de control donde el humano autoriza el avance entre las fases del escuadrón.
          </p>
        </div>

        <button
          type="button"
          onClick={loadData}
          className="px-4 py-2 rounded-2xl bg-zinc-900 hover:bg-zinc-800 text-zinc-300 hover:text-white border border-zinc-750 text-xs font-bold flex items-center gap-1.5 transition cursor-pointer self-start sm:self-auto"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Actualizar</span>
        </button>
      </div>

      {/* Banner de Feedback */}
      {feedbackBanner && (
        <div
          className={`p-4 rounded-2xl border text-xs flex items-center justify-between gap-3 ${
            feedbackBanner.type === 'success'
              ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-200'
              : 'bg-rose-950/40 border-rose-500/40 text-rose-200'
          }`}
        >
          <div className="flex items-center gap-2">
            {feedbackBanner.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            )}
            <span className="font-medium">{feedbackBanner.message}</span>
          </div>
          <button
            onClick={() => setFeedbackBanner(null)}
            className="text-xs text-zinc-400 hover:text-white cursor-pointer font-bold"
          >
            ✕
          </button>
        </div>
      )}

      {/* Tarjeta de Aprobación Pendiente (Si la hay) */}
      {selectedGate ? (
        <div className="p-6 rounded-3xl bg-[#0C0C0E] border border-amber-500/40 space-y-5 shadow-2xl">
          <div className="flex items-start gap-3.5 border-b border-white/5 pb-4">
            <div className="w-11 h-11 rounded-2xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400 shrink-0">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] font-mono uppercase tracking-wider text-amber-300 font-bold">
                Paso Requerido · Aprobación Humana
              </span>
              <h2 className="text-base font-extrabold text-white">
                Autorizar Entrega: {selectedGate.action}
              </h2>
              <p className="text-xs text-zinc-400 mt-0.5">
                {selectedGate.reason || dossier?.rationale || 'El agente ha completado su fase y requiere autorización para subir cambios.'}
              </p>
            </div>
          </div>

          {/* Verificaciones Reales */}
          {dossier?.decision_checklist && (
            <div className="space-y-2 text-xs">
              <span className="text-zinc-400 font-bold font-mono text-[10px] uppercase">
                Verificaciones Superadas en Verde:
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                {dossier.decision_checklist.map((chk: any) => (
                  <div key={chk.id} className="p-3 rounded-2xl bg-black border border-white/5 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-white">{chk.name}</span>
                      <span className="text-[10px] text-emerald-400 font-bold flex items-center gap-1 font-mono">
                        <CheckCircle2 className="w-3 h-3" /> {chk.status}
                      </span>
                    </div>
                    <p className="text-[11px] text-zinc-400">{chk.details}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Justificación del Operador */}
          <div className="space-y-1.5 text-xs">
            <label className="text-zinc-300 font-bold block font-mono text-[11px]">
              Nota o Justificación de Aprobación:
            </label>
            <input
              type="text"
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
              className="w-full bg-black border border-zinc-800 focus:border-white rounded-2xl px-4 py-2.5 text-xs text-white font-mono focus:outline-none"
            />
          </div>

          {/* Botones de Decisión Claros */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-white/5">
            <button
              type="button"
              onClick={() => handleDecision('REJECTED')}
              disabled={loading}
              className="px-5 py-2.5 rounded-2xl bg-zinc-900 hover:bg-zinc-850 text-zinc-300 hover:text-white border border-zinc-750 text-xs font-bold transition cursor-pointer disabled:opacity-40"
            >
              ✕ Rechazar Entrega
            </button>

            <button
              type="button"
              onClick={() => handleDecision('APPROVED')}
              disabled={loading}
              className="px-6 py-2.5 rounded-2xl bg-white hover:bg-zinc-200 text-black text-xs font-extrabold flex items-center gap-2 transition cursor-pointer shadow-lg disabled:opacity-40"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin text-black" />
              ) : (
                <Key className="w-4 h-4 text-black" />
              )}
              <span>✓ Autorizar y Continuar a Fase 3</span>
            </button>
          </div>
        </div>
      ) : (
        /* Estado Pacífico: No hay decisiones pendientes */
        <div className="p-8 rounded-3xl bg-[#0C0C0E] border border-white/5 space-y-3 shadow-xl text-center flex flex-col items-center">
          <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <h2 className="text-base font-extrabold text-white">
            Todo al día · No hay aprobaciones pendientes
          </h2>
          <p className="text-xs text-zinc-400 max-w-md">
            Todos los agentes operan conforme a los contratos establecidos y no hay entregas esperando firma humana en este momento.
          </p>
        </div>
      )}

      {/* Barra de Operaciones de Rescate y Liberación (KISS) */}
      <div className="p-4 rounded-3xl bg-[#0C0C0E] border border-white/5 flex flex-wrap items-center justify-between gap-3 shadow-md text-xs font-mono">
        <span className="text-zinc-400 font-bold uppercase text-[10px] flex items-center gap-1.5">
          <Activity className="w-3.5 h-3.5 text-sky-400" />
          Operaciones de Entorno:
        </span>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => handleLifecycleAction('revert')}
            disabled={actionLoading !== null}
            className="px-3.5 py-1.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-300 border border-zinc-750 transition cursor-pointer flex items-center gap-1.5"
          >
            {actionLoading === 'revert' ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RotateCcw className="w-3.5 h-3.5 text-amber-400" />}
            <span>Revertir FSM a Seguro</span>
          </button>

          <button
            type="button"
            onClick={() => handleLifecycleAction('release')}
            disabled={actionLoading !== null}
            className="px-3.5 py-1.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-300 border border-zinc-750 transition cursor-pointer flex items-center gap-1.5"
          >
            {actionLoading === 'release' ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Trash2 className="w-3.5 h-3.5 text-rose-400" />}
            <span>Liberar Worktrees</span>
          </button>
        </div>
      </div>

      {/* Consola de Logs y Auditoría SQLite (Colapsada por Defecto para Cero Ruido) */}
      <details className="group border border-white/5 rounded-3xl bg-[#0C0C0E] overflow-hidden">
        <summary className="p-4 sm:p-5 flex items-center justify-between text-xs font-mono text-zinc-400 hover:text-white cursor-pointer select-none">
          <span className="flex items-center gap-2 font-bold uppercase tracking-wider">
            <Terminal className="w-4 h-4 text-cyan-400" />
            <span>Ver Consola de Logs y Registros Históricos SQLite (Opcional)</span>
          </span>
          <span className="text-[10px] uppercase font-bold text-zinc-500 group-open:rotate-180 transition-transform">
            ▼
          </span>
        </summary>

        <div className="p-5 pt-0 border-t border-white/5 space-y-4">
          <div className="pt-3">
            <LogTerminal initialEvents={events} />
          </div>
        </div>
      </details>
    </div>
  )
}
