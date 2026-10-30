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
} from 'lucide-react'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'

export const ExecutionsSection: React.FC = () => {
  const [pendingGates, setPendingGates] = useState<any[]>([])
  const [selectedGate, setSelectedGate] = useState<any>(null)
  const [dossier, setDossier] = useState<any>(null)
  const [runs, setRuns] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [operatorName, setOperatorName] = useState('Operador')
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
      const rRes = await fetch('/api/db/rows?table=runs&limit=10')
      const rData = await rRes.json()
      if (rData && rData.rows) {
        setRuns(rData.rows)
      }
    } catch (e) {
      console.warn('Error loading runs from SQLite:', e)
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

  return (
    <div className="space-y-6 max-w-6xl mx-auto text-left pb-12">
      {/* 1. Header Claro */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 sm:p-6 rounded-2xl bg-zinc-950 border border-zinc-800">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-lg font-bold text-white tracking-tight">
              Mis Aprobaciones y Historial de Sprints
            </h1>
            <Badge variant={pendingGates.length > 0 ? 'warning' : 'default'}>
              {pendingGates.length}{' '}
              {pendingGates.length === 1 ? 'Pendiente' : 'Pendientes'}
            </Badge>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Revisa el resumen de pruebas antes de autorizar cualquier integración o despliegue.
          </p>
        </div>

        <Button onClick={loadData} variant="secondary" size="sm">
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Actualizar</span>
        </Button>
      </div>

      {feedbackBanner && (
        <div
          className={`p-4 rounded-xl border text-xs flex items-center justify-between gap-3 ${
            feedbackBanner.type === 'success'
              ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-200'
              : 'bg-red-950/40 border-red-500/40 text-red-200'
          }`}
        >
          <div className="flex items-center gap-2">
            {feedbackBanner.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            )}
            <span className="font-medium">{feedbackBanner.message}</span>
          </div>
          <button
            onClick={() => setFeedbackBanner(null)}
            className="text-xs underline cursor-pointer"
          >
            Cerrar
          </button>
        </div>
      )}

      {/* 2. Selector si hay más de 1 aprobación pendiente */}
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

      {/* 3. Tarjeta de Aprobación Paso a Paso (Reconocimiento antes que recuerdo + Poka-Yoke) */}
      {selectedGate ? (
        <div className="p-6 rounded-2xl bg-zinc-950 border border-amber-500/40 space-y-5 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-850 pb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-sm font-bold text-white">
                    Solicitud de Autorización: {selectedGate.action}
                  </h2>
                  <Badge variant="warning">PENDIENTE DE TU FIRMA</Badge>
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

          {/* Resumen de Verificación y Dictamen de los 6 Personajes SolidBit */}
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
                    className="p-3 rounded-xl bg-black border border-zinc-850 space-y-1"
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
                        className="p-2.5 rounded-xl bg-black border border-zinc-850 space-y-1"
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

          {/* Divulgación Progresiva: Detalles técnicos de riesgo y Git Diff */}
          <div className="border-t border-zinc-850 pt-3">
            <button
              type="button"
              onClick={() => setShowDiff(!showDiff)}
              className="flex items-center gap-2 text-xs text-zinc-400 hover:text-white transition cursor-pointer font-mono"
            >
              <FileCode className="w-4 h-4" />
              <span>
                {showDiff
                  ? 'Ocultar detalles técnicos y cambios de código (Git Diff)'
                  : 'Ver detalles técnicos y cambios de código propuestos'}
              </span>
              {showDiff ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {showDiff && (
              <div className="mt-3 space-y-3 animate-fade-in">
                {dossier?.risk_assessment && (
                  <div className="p-3.5 rounded-xl bg-black border border-zinc-850 grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
                    <div>
                      <span className="text-zinc-500 block text-[10px] font-mono">Aislamiento:</span>
                      <span className="text-zinc-200">{dossier.risk_assessment.scope_isolation}</span>
                    </div>
                    <div>
                      <span className="text-zinc-500 block text-[10px] font-mono">Impacto:</span>
                      <span className="text-zinc-200">{dossier.risk_assessment.blast_radius}</span>
                    </div>
                    <div>
                      <span className="text-zinc-500 block text-[10px] font-mono">Reversión:</span>
                      <span className="text-emerald-400">{dossier.risk_assessment.rollback_safety}</span>
                    </div>
                  </div>
                )}

                {dossier?.diff_lines && (
                  <div className="p-3.5 rounded-xl bg-black border border-zinc-850 font-mono text-xs max-h-44 overflow-y-auto space-y-0.5">
                    {dossier.diff_lines.map((line: any, idx: number) => {
                      const isAdd = line.type === 'add' || line.text?.startsWith('+')
                      const isDel = line.type === 'del' || line.text?.startsWith('-')
                      return (
                        <div
                          key={idx}
                          className={`px-2 py-0.5 rounded text-[11px] ${
                            isAdd
                              ? 'bg-emerald-950/40 text-emerald-300'
                              : isDel
                              ? 'bg-red-950/40 text-red-300'
                              : 'text-zinc-400'
                          }`}
                        >
                          {line.text}
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Comentario con Validación Poka-Yoke en línea */}
          <div className="space-y-1.5 pt-1">
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
              className="w-full bg-black border border-zinc-700 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-white"
            />
          </div>

          {/* Botones de Acción (Ley de Fitts: amplios y junto al input) */}
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
        <div className="p-8 rounded-2xl bg-zinc-950 border border-zinc-800 text-center space-y-3">
          <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
          <h3 className="text-sm font-bold text-white">Todo al Día · Sin Aprobaciones Pendientes</h3>
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

      {/* 4. Historial de Sprints Guardados en SQLite */}
      <div className="p-5 sm:p-6 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-4">
        <div className="flex items-center justify-between border-b border-zinc-850 pb-3">
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
                      <span className="px-2 py-0.5 rounded-full text-[10px] bg-zinc-900 text-zinc-300 border border-zinc-750">
                        {r.status || 'COMPLETADO'}
                      </span>
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
  )
}
