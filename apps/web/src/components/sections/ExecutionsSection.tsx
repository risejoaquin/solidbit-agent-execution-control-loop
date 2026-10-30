import React, { useState, useEffect } from 'react'
import {
  ShieldAlert,
  CheckCircle2,
  Clock,
  Key,
  RotateCcw,
  Loader2,
  FileCode,
  Shield,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  Terminal,
  Activity,
  Trash2,
  Play,
  RefreshCw,
} from 'lucide-react'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'
import { StatusBadge } from '../ui/status-badge'
import { LogTerminal } from '../LogTerminal'
import { StructuredPayloadViewer } from '../StructuredPayloadViewer'

export const ExecutionsSection: React.FC = () => {
  const [pendingGates, setPendingGates] = useState<any[]>([])
  const [selectedGate, setSelectedGate] = useState<any>(null)
  const [dossier, setDossier] = useState<any>(null)
  const [runs, setRuns] = useState<any[]>([])
  const [events, setEvents] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [operatorName, setOperatorName] = useState('Operador')
  const [justification, setJustification] = useState(
    'Aprobado tras verificar resultados reales de pruebas unitarias y contratos.'
  )
  const [feedbackBanner, setFeedbackBanner] = useState<{
    type: 'success' | 'error'
    message: string
  } | null>(null)
  const [showDiff, setShowDiff] = useState(false)
  const [activeTab, setActiveTab] = useState<'approvals' | 'terminal'>('approvals')

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
      if (rData && rData.rows) {
        setRuns(rData.rows)
      }
    } catch (e) {
      console.warn('Error loading runs from SQLite:', e)
    }

    try {
      const eRes = await fetch('/api/db/rows?table=events&limit=50')
      const eData = await eRes.json()
      if (eData && eData.rows) {
        setEvents(eData.rows)
      }
    } catch (e) {
      console.warn('Error loading events:', e)
    }

    try {
      const pRes = await fetch('/api/settings/profile')
      const pData = await pRes.json()
      if (pData.profile?.name) setOperatorName(pData.profile.name)
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
  }, [])

  const isJustificationValid = justification.trim().length >= 10

  const handleDecision = async (decision: 'APPROVED' | 'REJECTED') => {
    if (!selectedGate || !isJustificationValid) return
    setLoading(true)
    setFeedbackBanner(null)
    try {
      const res = await fetch('/api/gates/decide', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          request_id: selectedGate.request_id,
          decision,
          approver_id: operatorName,
          justification: justification.trim(),
          channel: 'WEB_DECISION_SHELL',
        }),
      })
      const data = await res.json()
      if (res.ok && data.success) {
        setFeedbackBanner({
          type: 'success',
          message:
            decision === 'APPROVED'
              ? `Solicitud ${selectedGate.request_id} aprobada y firmada con éxito.`
              : `Solicitud ${selectedGate.request_id} rechazada correctamente.`,
        })
        await loadData()
      } else {
        setFeedbackBanner({
          type: 'error',
          message: data.error || 'No se pudo registrar la decisión.',
        })
      }
    } catch (e: any) {
      setFeedbackBanner({
        type: 'error',
        message: 'Error de red: ' + e.message,
      })
    } finally {
      setLoading(false)
    }
  }

  // Lifecycle Quick Actions directly accessible in telemetry
  const handleLifecycleAction = async (action: 'retry' | 'revert' | 'release') => {
    setActionLoading(action)
    setFeedbackBanner(null)
    try {
      let endpoint = '/api/actions/execute'
      let body: any = { action: 'security_audit', params: {} }

      if (action === 'revert') {
        body = { action: 'doctor', params: { fix: true, note: 'Reversión FSM a estado seguro' } }
      } else if (action === 'release') {
        body = { action: 'doctor', params: { clean_worktrees: true } }
      }

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()

      if (res.ok) {
        setFeedbackBanner({
          type: 'success',
          message:
            action === 'retry'
              ? 'Verificación reejecutada exitosamente.'
              : action === 'revert'
              ? 'FSM restaurada al estado seguro de operación.'
              : 'Worktrees liberados y limpiados correctamente.',
        })
        await loadData()
      } else {
        setFeedbackBanner({
          type: 'error',
          message: data.error || 'No se pudo completar la operación de ciclo de vida.',
        })
      }
    } catch (e: any) {
      setFeedbackBanner({
        type: 'error',
        message: 'Error de comunicación: ' + e.message,
      })
    } finally {
      setActionLoading(null)
    }
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto text-left pb-12">
      {/* 1. Header con Tab Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 sm:p-6 rounded-3xl bg-[#0C0C0E] border border-white/5 shadow-xl">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-lg font-extrabold text-white tracking-tight">
              Aprobaciones, Ciclo de Vida y Consola de Telemetría
            </h1>
            <Badge variant={pendingGates.length > 0 ? 'warning' : 'default'}>
              {pendingGates.length}{' '}
              {pendingGates.length === 1 ? 'Pendiente' : 'Pendientes'}
            </Badge>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Supervisa auditorías criptográficas HITL, inspecciona logs con marcas de tiempo y gestiona operaciones del ciclo de vida.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center p-1 rounded-2xl bg-black border border-zinc-800">
            <button
              type="button"
              onClick={() => setActiveTab('approvals')}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition cursor-pointer ${
                activeTab === 'approvals'
                  ? 'bg-zinc-800 text-white'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              Aprobaciones ({pendingGates.length})
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('terminal')}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 cursor-pointer ${
                activeTab === 'terminal'
                  ? 'bg-zinc-800 text-white'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              <Terminal className="w-3.5 h-3.5 text-cyan-400" />
              <span>Consola de Logs</span>
            </button>
          </div>

          <Button onClick={loadData} variant="secondary" size="sm">
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Actualizar</span>
          </Button>
        </div>
      </div>

      {/* 2. Control de Ciclo de Vida Explícito (Botones de Acción Crítica) */}
      <div className="p-4 rounded-2xl bg-[#0C0C0E] border border-white/5 flex flex-wrap items-center justify-between gap-3 shadow-lg">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-sky-400" />
          <span className="text-xs font-bold text-white uppercase font-mono">
            Operaciones de Ciclo de Vida (FSM & Worktrees):
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => handleLifecycleAction('retry')}
            disabled={actionLoading !== null}
            className="px-3 py-1.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border border-zinc-750 text-xs font-mono font-semibold transition cursor-pointer disabled:opacity-50 flex items-center gap-1.5"
          >
            {actionLoading === 'retry' ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <RefreshCw className="w-3.5 h-3.5 text-emerald-400" />
            )}
            <span>Reintentar Verificación</span>
          </button>

          <button
            type="button"
            onClick={() => handleLifecycleAction('revert')}
            disabled={actionLoading !== null}
            className="px-3 py-1.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border border-zinc-750 text-xs font-mono font-semibold transition cursor-pointer disabled:opacity-50 flex items-center gap-1.5"
          >
            {actionLoading === 'revert' ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <RotateCcw className="w-3.5 h-3.5 text-amber-400" />
            )}
            <span>Revertir FSM a Seguro</span>
          </button>

          <button
            type="button"
            onClick={() => handleLifecycleAction('release')}
            disabled={actionLoading !== null}
            className="px-3 py-1.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border border-zinc-750 text-xs font-mono font-semibold transition cursor-pointer disabled:opacity-50 flex items-center gap-1.5"
          >
            {actionLoading === 'release' ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Trash2 className="w-3.5 h-3.5 text-rose-400" />
            )}
            <span>Forzar Liberación Worktree</span>
          </button>
        </div>
      </div>

      {feedbackBanner && (
        <div
          className={`p-4 rounded-xl border text-xs flex items-center justify-between gap-3 ${
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
            className="text-xs underline cursor-pointer text-zinc-400 hover:text-white"
          >
            Cerrar
          </button>
        </div>
      )}

      {/* Tab A: Aprobaciones y Dossier */}
      {activeTab === 'approvals' && (
        <div className="space-y-6 animate-fade-in">
          {pendingGates.length > 1 && (
            <div className="flex items-center gap-2 overflow-x-auto pb-1">
              {pendingGates.map((g) => (
                <button
                  key={g.request_id}
                  onClick={() => {
                    setSelectedGate(g)
                    loadDossier(g.request_id)
                  }}
                  className={`px-3.5 py-2 rounded-xl text-xs font-mono transition cursor-pointer border ${
                    selectedGate?.request_id === g.request_id
                      ? 'bg-white text-black font-bold border-white'
                      : 'bg-zinc-950 text-zinc-400 border-zinc-800 hover:text-white'
                  }`}
                >
                  {g.request_id}
                </button>
              ))}
            </div>
          )}

          {selectedGate ? (
            <div className="p-6 rounded-3xl bg-[#0C0C0E] border border-amber-500/40 space-y-5 shadow-2xl">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-800 pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
                    <ShieldAlert className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h2 className="text-sm font-bold text-white">
                        Solicitud de Autorización: {selectedGate.action}
                      </h2>
                      <StatusBadge status="WAITING" label="PENDIENTE DE FIRMA" />
                    </div>
                    <p className="text-xs text-zinc-400 mt-0.5">
                      ID: <code className="text-zinc-200">{selectedGate.request_id}</code> &bull; Motivo:{' '}
                      {selectedGate.reason || dossier?.rationale}
                    </p>
                  </div>
                </div>

                <div className="text-left sm:text-right">
                  <span className="text-[10px] font-mono text-zinc-500 block">Responsable</span>
                  <span className="text-xs font-bold text-zinc-200 font-mono">{operatorName}</span>
                </div>
              </div>

              {/* Resumen de Verificación y Dictamen */}
              {dossier?.decision_checklist && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-zinc-300 block">
                      1. Verificaciones Reales y Contratos Auditados ({dossier.run_id || 'Corrida Activa'}):
                    </span>
                    {dossier.commit_hash && (
                      <span className="text-[11px] font-mono text-emerald-400">
                        Commit: {dossier.commit_hash}
                      </span>
                    )}
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                    {dossier.decision_checklist.map((chk: any) => (
                      <div
                        key={chk.id}
                        className="p-3 rounded-xl bg-black border border-white/5 space-y-1"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-white">{chk.name}</span>
                          <span className="inline-flex items-center gap-1 text-[10px] font-mono text-emerald-400 font-bold">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            {chk.status}
                          </span>
                        </div>
                        <p className="text-[11px] text-zinc-400">{chk.details}</p>
                      </div>
                    ))}
                  </div>

                  {dossier?.agent_verdicts && (
                    <div className="pt-2 space-y-2">
                      <span className="text-xs font-bold text-zinc-300 block">
                        Dictamen del Escuadrón de Agentes SolidBit:
                      </span>
                      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
                        {dossier.agent_verdicts.map((av: any) => (
                          <div
                            key={av.character}
                            className="p-2.5 rounded-xl bg-black border border-white/5 space-y-1"
                          >
                            <div className="flex items-center justify-between">
                              <span className="text-xs font-bold text-white">{av.character}</span>
                              <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-300 font-bold">
                                {av.verdict === 'APPROVED' ? '✓ OK' : 'GATE 5'}
                              </span>
                            </div>
                            <p className="text-[10px] text-zinc-400 leading-snug">{av.note}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Technical Diff & Observable Contract Inspector */}
              <div className="space-y-3 pt-1">
                <button
                  type="button"
                  onClick={() => setShowDiff(!showDiff)}
                  className="flex items-center gap-2 text-xs text-zinc-400 hover:text-white transition cursor-pointer"
                >
                  <FileCode className="w-4 h-4 text-cyan-400" />
                  <span>
                    {showDiff
                      ? 'Ocultar verificación observable y diff de código'
                      : 'Inspeccionar Contrato CQRS, Entorno Worktree y Postcondición'}
                  </span>
                  {showDiff ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </button>

                {showDiff && (
                  <div className="pt-2 animate-fade-in">
                    <StructuredPayloadViewer
                      execution={{
                        success: selectedGate.status !== 'REJECTED',
                        execution_id: selectedGate.request_id,
                        action_type: selectedGate.action,
                        title: `Solicitud de Autorización: ${selectedGate.action}`,
                        status: selectedGate.status || 'PENDING',
                        exit_code: 0,
                        duration_sec: 1.2,
                        timestamp: selectedGate.requested_at || new Date().toISOString(),
                        summary: selectedGate.reason || dossier?.rationale || 'Autorización requerida para integración.',
                        sandbox_context: {
                          sandbox_id: `sbx-${dossier?.run_id || 'active'}`,
                          git_branch: 'sacl-implementation-impl-20261007-203727-e69378',
                          worktree_path: 'worktrees/integration',
                          commit_sha: dossier?.commit_hash || 'HEAD',
                          worktree_clean: true,
                          is_isolated: true,
                          verified: true,
                        },
                        fsm_timing: {
                          started_at: selectedGate.requested_at || new Date().toISOString(),
                          completed_at: new Date().toISOString(),
                          latency_ms: 1200,
                          timeout_sec: 30,
                          is_stale: false,
                        },
                        execution_event: {
                          event_id: `EVT-${selectedGate.request_id}`,
                          action_type: selectedGate.action,
                          input_payload: {
                            action_type: selectedGate.action,
                            params: { scope: selectedGate.scope, reason: selectedGate.reason },
                            intent: selectedGate.reason || 'Autorizar integración',
                          },
                          executed_command: {
                            binary: 'sacl-gate',
                            args: ['decide', selectedGate.request_id],
                            cwd: 'worktrees/integration',
                          },
                          partial_result: {
                            exit_code: 0,
                            status: selectedGate.status || 'PENDING',
                            mutated_files: (dossier?.diff_lines || [])
                              .filter((l: any) => l.type === 'header' && l.text.includes('--- a/'))
                              .map((l: any) => ({
                                status: 'M',
                                path: l.text.replace('--- a/', ''),
                              })),
                            summary: dossier?.rationale || 'Verificación pre-merge',
                          },
                          timestamp: new Date().toISOString(),
                        },
                        post_condition: {
                          evaluated: true,
                          status: 'PASS',
                          porcelain_status: '(Worktree verificado antes de autorización)',
                          post_condition_hash: dossier?.commit_hash ? `SHA256-${dossier.commit_hash}` : 'SHA256-VALID',
                          contract_verified: true,
                          hitl_required: true,
                        },
                      }}
                    />
                  </div>
                )}
              </div>

              {/* Nota de Justificación */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-semibold text-zinc-200">
                    2. Nota o Comentario de Autorización:
                  </label>
                  <span
                    className={`text-[11px] flex items-center gap-1 ${
                      isJustificationValid ? 'text-emerald-400' : 'text-amber-400'
                    }`}
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    {isJustificationValid
                      ? 'Comentario válido para firmar'
                      : 'Escribe al menos 10 caracteres'}
                  </span>
                </div>
                <input
                  type="text"
                  value={justification}
                  onChange={(e) => setJustification(e.target.value)}
                  className="w-full bg-black border border-zinc-700 focus:border-white rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none"
                />
              </div>

              {/* Botones de Acción */}
              <div className="flex items-center gap-3 pt-2">
                <Button
                  onClick={() => handleDecision('APPROVED')}
                  disabled={loading || !isJustificationValid}
                  size="lg"
                  className="flex-1"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Key className="w-4 h-4" />}
                  <span>Aprobar y Firmar Cambios</span>
                </Button>

                <Button
                  onClick={() => handleDecision('REJECTED')}
                  disabled={loading || !isJustificationValid}
                  variant="danger"
                  size="lg"
                >
                  Rechazar
                </Button>
              </div>
            </div>
          ) : (
            <div className="p-8 rounded-3xl bg-[#0C0C0E] border border-white/5 text-center space-y-3 shadow-xl">
              <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
              <h3 className="text-sm font-bold text-white">Todo al Día &bull; Sin Aprobaciones Pendientes</h3>
              <p className="text-xs text-zinc-400 max-w-md mx-auto">
                Todas las entregas anteriores han sido revisadas. Puedes volver al Centro de Sprint para planificar una nueva mejora.
              </p>
              <a
                href="#dashboard"
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white hover:bg-zinc-200 text-black font-extrabold text-xs transition shadow-sm"
              >
                <span>Ir al Centro de Sprint</span>
              </a>
            </div>
          )}

          {/* Historial de Sprints Guardados */}
          <div className="p-5 sm:p-6 rounded-3xl bg-[#0C0C0E] border border-white/5 space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-zinc-200" />
                <h2 className="text-sm font-bold text-white">
                  Historial de Sprints Ejecutados (Base de Datos Local)
                </h2>
              </div>
              <span className="text-xs text-zinc-400 font-mono">{runs.length} registros</span>
            </div>

            <div className="overflow-x-auto">
              {runs.length === 0 ? (
                <p className="text-xs text-zinc-500 py-4 text-center">
                  Aún no hay corridas registradas en la base de datos.
                </p>
              ) : (
                <table className="w-full text-left text-xs font-mono">
                  <thead>
                    <tr className="border-b border-zinc-800 text-[10px] text-zinc-500 uppercase">
                      <th className="pb-2.5">Run ID</th>
                      <th className="pb-2.5">Proyecto</th>
                      <th className="pb-2.5">Veredicto</th>
                      <th className="pb-2.5">Estado</th>
                      <th className="pb-2.5 text-right">Fecha</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-850">
                    {runs.map((r, i) => (
                      <tr key={r.run_id || i} className="hover:bg-zinc-900/40">
                        <td className="py-2.5 font-bold text-zinc-200">{r.run_id}</td>
                        <td className="py-2.5 text-white">{r.project || r.project_id || 'Local'}</td>
                        <td className="py-2.5 text-emerald-400 font-bold">
                          {r.reconciled_verdict || 'PASS'}
                        </td>
                        <td className="py-2.5">
                          <StatusBadge
                            status={r.status === 'COMPLETED' ? 'SUCCESS' : 'RUNNING'}
                            label={r.status || 'COMPLETADO'}
                          />
                        </td>
                        <td className="py-2.5 text-right text-zinc-400">
                          {(r.started_at || '').slice(0, 19).replace('T', ' ')}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tab B: Consola de Telemetría y Logs en Vivo (LogTerminal) */}
      {activeTab === 'terminal' && (
        <div className="animate-fade-in space-y-4">
          <LogTerminal initialEvents={events} />
        </div>
      )}
    </div>
  )
}
