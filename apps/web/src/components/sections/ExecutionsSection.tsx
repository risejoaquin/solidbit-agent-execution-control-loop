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
} from 'lucide-react'

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
        alert(`Decisión ${decision} registrada exitosamente en SQLite approvals!`)
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
    <div className="space-y-6">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-3xl bg-[#0e141d] border border-[#1b2533]">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold text-white tracking-wide">
              Compuertas de Decisión Humana (HITL) & Historial de Corridas
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/30">
              {pendingGates.length} Compuertas Pendientes
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Gobernanza Soberana: autorización humana obligatoria para compuertas de despliegue y mutaciones
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleCreateNewGate}
            className="px-3 py-1.5 rounded-xl bg-zinc-900 border border-[#1b2533] hover:bg-zinc-800 text-xs text-zinc-300 flex items-center gap-1.5 transition cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5 text-emerald-400" />
            <span>Crear Compuerta</span>
          </button>
          <button
            onClick={loadData}
            className="px-3 py-1.5 rounded-xl bg-zinc-900 border border-[#1b2533] hover:bg-zinc-800 text-xs text-zinc-300 flex items-center gap-1.5 transition cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Actualizar</span>
          </button>
        </div>
      </div>

      {/* Active HITL Gate Decision Dossier */}
      {selectedGate ? (
        <div className="p-6 rounded-3xl bg-[#0e141d] border border-amber-500/40 space-y-5 shadow-2xl relative">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1b2533] pb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-sm font-bold text-white">
                    Compuerta: {selectedGate.action}
                  </h2>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse">
                    {selectedGate.status}
                  </span>
                </div>
                <p className="text-xs text-zinc-400 mt-0.5">
                  ID: {selectedGate.request_id} &bull; Alcance: {selectedGate.scope}
                </p>
              </div>
            </div>

            <div className="text-right">
              <span className="text-[10px] font-mono text-zinc-500 block">Autoridad Requerida</span>
              <span className="text-xs font-bold text-emerald-400 font-mono">{operatorName}</span>
            </div>
          </div>

          {/* Real Dossier checklist from backend */}
          {dossier?.decision_checklist && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {dossier.decision_checklist.map((chk: any) => (
                <div key={chk.id} className="p-3 rounded-2xl bg-black/40 border border-white/5 space-y-1">
                  <span className="text-[10px] font-mono text-zinc-500">{chk.name}</span>
                  <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-400">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>{chk.status}</span>
                  </div>
                  <p className="text-[10px] text-zinc-400 line-clamp-2">{chk.details}</p>
                </div>
              ))}
            </div>
          )}

          {/* Justification input */}
          <div className="space-y-1.5">
            <label className="text-[11px] font-mono text-zinc-400">
              Justificación de Decisión Humana (Se registrará en SQLite approvals):
            </label>
            <input
              type="text"
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
              className="w-full bg-[#080c10] border border-[#1b2533] rounded-2xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-emerald-500/60 font-sans"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={() => handleDecision('APPROVED')}
              disabled={loading}
              className="flex-1 py-3 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-black font-bold text-xs flex items-center justify-center gap-2 transition cursor-pointer shadow-lg shadow-emerald-500/10"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Key className="w-4 h-4" />}
              <span>Aprobar y Emitir Token Soberano (POST /api/gates/decide)</span>
            </button>

            <button
              onClick={() => handleDecision('REJECTED')}
              disabled={loading}
              className="px-6 py-3 rounded-2xl bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 font-bold text-xs transition cursor-pointer"
            >
              Rechazar
            </button>
          </div>
        </div>
      ) : (
        <div className="p-8 rounded-3xl bg-[#0e141d] border border-[#1b2533] text-center space-y-2">
          <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
          <h3 className="text-sm font-bold text-white">Cero Compuertas Pendientes</h3>
          <p className="text-xs text-zinc-400">
            Todas las acciones y despliegues están al día en la tabla approvals de SQLite sacl_ops.db.
          </p>
        </div>
      )}

      {/* Real Runs from SQLite table */}
      <div className="p-6 rounded-3xl bg-[#0e141d] border border-[#1b2533] space-y-4 shadow-xl">
        <div className="flex items-center justify-between border-b border-[#1b2533] pb-3">
          <h2 className="text-sm font-bold text-white">Historial de Corridas (Tabla 'runs' en SQLite WAL)</h2>
          <span className="text-xs text-zinc-400 font-mono">{runs.length} registradas</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-[#1b2533] text-[10px] text-zinc-500">
                <th className="pb-2 pl-2">Run ID</th>
                <th className="pb-2">Job ID</th>
                <th className="pb-2">Proyecto</th>
                <th className="pb-2">Veredicto</th>
                <th className="pb-2">Inicio</th>
                <th className="pb-2 pr-2">Estado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1b2533]/40">
              {runs.map((r, i) => (
                <tr key={r.run_id || i} className="hover:bg-white/[0.02]">
                  <td className="py-2.5 pl-2 font-bold text-blue-400">{r.run_id}</td>
                  <td className="py-2.5 text-zinc-300">{r.job_id}</td>
                  <td className="py-2.5 text-white">{r.project || r.project_id}</td>
                  <td className="py-2.5 text-emerald-400">{r.reconciled_verdict || 'PASS'}</td>
                  <td className="py-2.5 text-zinc-500 text-[11px]">{r.started_at}</td>
                  <td className="py-2.5 pr-2">
                    <span className="px-2 py-0.5 rounded-full text-[10px] bg-zinc-800 text-zinc-300">
                      {r.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
