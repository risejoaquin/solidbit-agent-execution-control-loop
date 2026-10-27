import React, { useState, useEffect } from 'react'
import {
  ShieldAlert,
  CheckCircle2,
  Clock,
  Key,
  RotateCcw,
  Plus,
  Loader2,
  FileCheck2,
  AlertTriangle,
  Send,
  FileCode,
  Shield,
  Layers,
  Sparkles,
} from 'lucide-react'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'

export const ExecutionsSection: React.FC = () => {
  const [pendingGates, setPendingGates] = useState<any[]>([])
  const [selectedGate, setSelectedGate] = useState<any>(null)
  const [dossier, setDossier] = useState<any>(null)
  const [runs, setRuns] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [operatorName, setOperatorName] = useState('Joaquin Vallejo')
  const [justification, setJustification] = useState(
    'Aprobado por el Product Owner tras verificación empírica de pruebas unitarias y contratos congelados.'
  )
  const [decidedResult, setDecidedResult] = useState<any>(null)

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
      const rRes = await fetch('/api/db/rows?table=runs&limit=8')
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

  const handleDecision = async (decision: 'APPROVED' | 'REJECTED') => {
    if (!selectedGate) return
    setLoading(true)
    try {
      const res = await fetch('/api/gates/decide', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          request_id: selectedGate.request_id,
          decision,
          approver_id: operatorName,
          justification,
          channel: 'WEB_DECISION_SHELL',
        }),
      })
      const data = await res.json()
      if (res.ok && data.success) {
        setDecidedResult(data)
        alert(`Decisión ${decision} registrada exitosamente en SQLite approvals con firma HMAC-SHA256!`)
        loadData()
      } else {
        alert('Error: ' + (data.error || 'No se pudo registrar la decisión'))
      }
    } catch (e: any) {
      alert('Error de red: ' + e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateNewGate = async () => {
    try {
      const res = await fetch('/api/gates/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'DEPLOY_STAGING_PREVIEW',
          reason: 'Verificación de preview build con contratos DR-INV-001 y DR-PAY-001.',
        }),
      })
      const data = await res.json()
      if (data.success) {
        alert(`Nueva compuerta ${data.request_id} creada en SQLite sacl_ops.db!`)
        loadData()
      }
    } catch (e: any) {
      alert('Error creando compuerta: ' + e.message)
    }
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-3xl bg-zinc-950 border border-zinc-800">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold text-white tracking-wide">
              Compuertas de Decisión Humana (HITL) & Historial de Corridas
            </h1>
            <Badge variant={pendingGates.length > 0 ? "warning" : "default"}>
              {pendingGates.length} {pendingGates.length === 1 ? 'Compuerta Pendiente' : 'Compuertas Pendientes'}
            </Badge>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Gobernanza Soberana: autorización humana obligatoria para compuertas de despliegue y mutaciones de estado
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            onClick={handleCreateNewGate}
            variant="secondary"
            size="sm"
          >
            <Plus className="w-3.5 h-3.5 text-zinc-200" />
            <span>Crear Compuerta</span>
          </Button>
          <Button
            onClick={loadData}
            variant="secondary"
            size="sm"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Actualizar</span>
          </Button>
        </div>
      </div>

      {/* Active HITL Gate Decision Dossier (Evidence Pack) */}
      {selectedGate ? (
        <div className="p-6 rounded-3xl bg-zinc-950 border border-amber-500/40 space-y-5 shadow-2xl relative">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-800 pb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-sm font-bold text-white">
                    Compuerta Soberana: {selectedGate.action}
                  </h2>
                  <Badge variant="warning" className="animate-pulse">
                    {selectedGate.status}
                  </Badge>
                </div>
                <p className="text-xs text-zinc-400 mt-0.5">
                  ID: {selectedGate.request_id} &bull; Alcance: {selectedGate.scope}
                </p>
              </div>
            </div>

            <div className="text-right space-y-1">
              <div>
                <span className="text-[10px] font-mono text-zinc-500 block">Autoridad Requerida</span>
                <span className="text-xs font-bold text-zinc-200 font-mono">{operatorName}</span>
              </div>
              <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-[10px] font-mono text-amber-400">
                <Clock className="w-3 h-3 text-amber-400 animate-spin" />
                <span>SLA Fail-Closed: 14m 28s</span>
              </div>
            </div>
          </div>

          {/* Evidence Pack: Risk Assessment */}
          {dossier?.risk_assessment && (
            <div className="p-4 rounded-2xl bg-black/50 border border-zinc-850 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white flex items-center gap-2">
                  <Shield className="w-4 h-4 text-emerald-400" />
                  Evaluación Algorítmica de Riesgo (Evidence Pack)
                </span>
                <Badge variant="success">
                  NIVEL: {dossier.risk_assessment.level}
                </Badge>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-[11px] font-mono text-zinc-400 pt-1">
                <div>
                  <span className="text-zinc-500 block text-[10px]">Aislamiento:</span>
                  <span className="text-zinc-300">{dossier.risk_assessment.scope_isolation}</span>
                </div>
                <div>
                  <span className="text-zinc-500 block text-[10px]">Radio de Impacto:</span>
                  <span className="text-zinc-300">{dossier.risk_assessment.blast_radius}</span>
                </div>
                <div>
                  <span className="text-zinc-500 block text-[10px]">Reversibilidad:</span>
                  <span className="text-zinc-300">{dossier.risk_assessment.rollback_safety}</span>
                </div>
              </div>
            </div>
          )}

          {/* Evidence Pack: Checklist */}
          {dossier?.decision_checklist && (
            <div className="space-y-2">
              <span className="text-xs font-bold text-white font-mono uppercase tracking-wider block">
                Lista de Verificación de Invariantes & Contratos Congelados
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {dossier.decision_checklist.map((chk: any) => (
                  <div key={chk.id} className="p-3 rounded-2xl bg-black/40 border border-zinc-850 space-y-1">
                    <span className="text-[10px] font-mono text-zinc-500">{chk.name}</span>
                    <div className="flex items-center gap-1.5 text-xs font-bold text-zinc-200">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      <span>{chk.status}</span>
                    </div>
                    <p className="text-[10px] text-zinc-400 line-clamp-2">{chk.details}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Evidence Pack: Diff Inspector */}
          {dossier?.diff_lines && dossier.diff_lines.length > 0 && (
            <div className="space-y-2">
              <span className="text-xs font-bold text-white font-mono uppercase tracking-wider flex items-center gap-1.5">
                <FileCode className="w-3.5 h-3.5 text-zinc-400" />
                Diferencial Propuesto por el Agente (Git Diff)
              </span>
              <div className="p-3.5 rounded-2xl bg-black border border-zinc-850 font-mono text-xs max-h-48 overflow-y-auto custom-scroll space-y-0.5">
                {dossier.diff_lines.map((line: any, idx: number) => {
                  const isAdd = line.type === 'add' || line.text?.startsWith('+')
                  const isDel = line.type === 'del' || line.text?.startsWith('-')
                  const isHdr = line.type === 'header' || line.type === 'chunk'
                  return (
                    <div
                      key={idx}
                      className={`px-2 py-0.5 rounded text-[11px] ${
                        isAdd
                          ? 'bg-emerald-950/40 text-emerald-300'
                          : isDel
                          ? 'bg-red-950/40 text-red-300'
                          : isHdr
                          ? 'text-zinc-500 font-bold'
                          : 'text-zinc-400'
                      }`}
                    >
                      {line.text}
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Justification input */}
          <div className="space-y-1.5 pt-2">
            <label className="text-[11px] font-mono text-zinc-400">
              Justificación de Decisión Humana (Se registrará con token HMAC en SQLite approvals):
            </label>
            <input
              type="text"
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
              className="w-full bg-black border border-zinc-800 rounded-2xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-white font-sans"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3 pt-2">
            <Button
              onClick={() => handleDecision('APPROVED')}
              disabled={loading}
              size="lg"
              className="flex-1"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Key className="w-4 h-4" />}
              <span>Aprobar y Emitir Token Criptográfico HMAC-SHA256</span>
            </Button>

            <Button
              onClick={() => handleDecision('REJECTED')}
              disabled={loading}
              variant="danger"
              size="lg"
            >
              Rechazar
            </Button>
          </div>
        </div>
      ) : (
        <div className="p-8 rounded-3xl bg-zinc-950 border border-zinc-800 text-center space-y-2">
          <CheckCircle2 className="w-8 h-8 text-zinc-200 mx-auto" />
          <h3 className="text-sm font-bold text-white">Cero Compuertas Pendientes (Zero-Gate Idle)</h3>
          <p className="text-xs text-zinc-400">
            Todas las acciones y despliegues están al día en la tabla approvals de SQLite sacl_ops.db.
          </p>
        </div>
      )}

      {/* Real Runs from SQLite table */}
      <div className="p-6 rounded-3xl bg-zinc-950 border border-zinc-800 space-y-4 shadow-xl">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-zinc-200" />
            <h2 className="text-sm font-bold text-white">Historial de Corridas (/api/db/rows?table=runs)</h2>
          </div>
          <span className="text-xs text-zinc-400 font-mono">{runs.length} corridas registradas</span>
        </div>

        <div className="overflow-x-auto custom-scroll">
          {runs.length === 0 ? (
            <p className="text-xs text-zinc-500 py-3 font-mono">No hay corridas registradas en SQLite sacl_ops.db.</p>
          ) : (
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-zinc-800 text-[10px] text-zinc-500">
                  <th className="pb-2">Run ID</th>
                  <th className="pb-2">Campaña</th>
                  <th className="pb-2">Worktree</th>
                  <th className="pb-2">Estado</th>
                  <th className="pb-2 text-right pr-2">Actualizado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-850">
                {runs.map((r, i) => (
                  <tr key={r.run_id || i} className="hover:bg-zinc-900/40">
                    <td className="py-2.5 font-bold text-zinc-300">{r.run_id}</td>
                    <td className="py-2.5 text-white">{r.campaign_id}</td>
                    <td className="py-2.5 text-zinc-400">{r.worktree_path || 'integration'}</td>
                    <td className="py-2.5">
                      <span className="px-2 py-0.5 rounded-full text-[10px] bg-zinc-900 text-zinc-300 border border-zinc-750">
                        {r.state || r.status || 'SUCCESS'}
                      </span>
                    </td>
                    <td className="py-2.5 text-right pr-2 text-zinc-500">{r.updated_at || r.created_at}</td>
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
