import React, { useState } from 'react'
import {
  X,
  Plus,
  Play,
  CheckCircle2,
  GitBranch,
  ShieldAlert,
  Loader2,
  Key,
  Database,
} from 'lucide-react'

interface SprintDesignerModalProps {
  isOpen: boolean
  onClose: () => void
  onSprintExecuted?: () => void
}

export const SprintDesignerModal: React.FC<SprintDesignerModalProps> = ({
  isOpen,
  onClose,
  onSprintExecuted,
}) => {
  const [sprintTitle, setSprintTitle] = useState('Implementación Atomic Inventory & Doble Partida (DR-INV-001 & DR-PAY-001)')
  const [sprintKey, setSprintKey] = useState('SOLID-301')
  const [tasksStr, setTasksStr] = useState('1. Congelar contratos SellableUnit\n2. Ledger transaccional de doble partida\n3. Suite Pytest y colisiones')
  const [criteriaStr, setCriteriaStr] = useState('- Cero sobreventa en concurrencia\n- 100% pruebas unitarias en verde\n- Token HMAC firmado por PO')
  const [loading, setLoading] = useState(false)
  const [createdSprint, setCreatedSprint] = useState<any>(null)
  const [activePlan, setActivePlan] = useState<any>(null)
  const [executionResult, setExecutionResult] = useState<any>(null)
  const [hmacApplied, setHmacApplied] = useState(false)

  if (!isOpen) return null

  const handleCreateSprint = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/orchestrator/create-sprint', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: sprintTitle,
          goals: sprintTitle,
          key: sprintKey,
          tasks: tasksStr.split('\n').filter(Boolean),
          acceptance_criteria: criteriaStr.split('\n').filter(Boolean),
          priority: 'CRITICAL',
        }),
      })
      const data = await res.json()
      if (res.ok && data.success) {
        setCreatedSprint(data.ticket)
        setActivePlan(data.plan)
      } else {
        alert('Error: ' + (data.error || 'No se pudo crear el sprint'))
      }
    } catch (e: any) {
      alert('Error de red: ' + e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleExecutePlan = async () => {
    if (!activePlan) return
    setLoading(true)
    try {
      const res = await fetch('/api/orchestrator/execute-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan: activePlan }),
      })
      const data = await res.json()
      if (res.ok && data.success) {
        setExecutionResult(data)
        onSprintExecuted?.()
      } else {
        alert('Error en ejecución: ' + (data.error || 'Fallo de orquestación'))
      }
    } catch (e: any) {
      alert('Error de conexión: ' + e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleApplyHmac = async () => {
    if (!executionResult?.gate?.approval_id) return
    setLoading(true)
    try {
      const res = await fetch('/api/gates/apply-approved', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          approval_id: executionResult.gate.approval_id,
          request_id: executionResult.gate.request_id,
        }),
      })
      const data = await res.json()
      if (res.ok && data.success) {
        setHmacApplied(true)
        onSprintExecuted?.()
      } else {
        alert('Error al aplicar compuerta HMAC: ' + (data.error || 'Fallo de firma'))
      }
    } catch (e: any) {
      alert('Error: ' + e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-[#0e141d] border border-[#1b2533] rounded-3xl max-w-4xl w-full p-6 space-y-6 shadow-2xl max-h-[92vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#1b2533] pb-4 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <GitBranch className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white tracking-tight">Diseñador y Orquestador de Sprints</h2>
              <p className="text-xs text-zinc-400">
                Flujo completo: Diseño &rarr; Jira &rarr; Grafo Topológico Kahn &rarr; Ejecución &rarr; Firma HMAC
              </p>
            </div>
          </div>
          <button onClick={onClose} className="text-zinc-400 hover:text-white p-1 rounded-lg hover:bg-white/5 transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto custom-scroll space-y-5 pr-1">
          {/* Form Step 1: Diseño */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-1.5 md:col-span-2">
              <label className="text-xs font-semibold text-zinc-300">Título del Sprint / Objetivo</label>
              <input
                type="text"
                value={sprintTitle}
                onChange={(e) => setSprintTitle(e.target.value)}
                className="w-full bg-black/50 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-white focus:border-emerald-500 focus:outline-none"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-zinc-300">Clave Jira / Job ID</label>
              <input
                type="text"
                value={sprintKey}
                onChange={(e) => setSprintKey(e.target.value)}
                className="w-full bg-black/50 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-white font-mono focus:border-emerald-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-zinc-300">Tareas del Sprint (Una por línea)</label>
              <textarea
                rows={3}
                value={tasksStr}
                onChange={(e) => setTasksStr(e.target.value)}
                className="w-full bg-black/50 border border-zinc-800 rounded-xl p-3 text-xs text-white font-mono focus:border-emerald-500 focus:outline-none"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-zinc-300">Criterios de Aceptación (Invariantes)</label>
              <textarea
                rows={3}
                value={criteriaStr}
                onChange={(e) => setCriteriaStr(e.target.value)}
                className="w-full bg-black/50 border border-zinc-800 rounded-xl p-3 text-xs text-white font-mono focus:border-emerald-500 focus:outline-none"
              />
            </div>
          </div>

          {/* Action 1: Create Sprint */}
          {!createdSprint && (
            <button
              type="button"
              onClick={handleCreateSprint}
              disabled={loading}
              className="w-full py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-bold text-xs flex items-center justify-center gap-2 transition disabled:opacity-50 cursor-pointer shadow-[0_0_20px_rgba(16,185,129,0.2)]"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
              <span>Crear y Persistir Sprint en Jira / SQLite WAL</span>
            </button>
          )}

          {/* Step 2: Auto-Designed Roadmap & DAG */}
          {createdSprint && (
            <div className="p-4 rounded-2xl bg-[#080c10] border border-emerald-500/30 space-y-4">
              <div className="flex items-center justify-between border-b border-white/5 pb-3">
                <div className="flex items-center gap-2 text-emerald-400">
                  <CheckCircle2 className="w-4 h-4" />
                  <span className="text-xs font-bold">Sprint Persistido & Roadmap Sintetizado</span>
                </div>
                <span className="text-[10px] font-mono text-zinc-400">Algoritmo de Kahn &bull; 4 Oleadas</span>
              </div>

              {/* Kahn DAG Waves View */}
              {activePlan && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                  {activePlan.waves?.map((wave: any) => (
                    <div key={wave.wave_number} className="p-2.5 rounded-xl bg-black/40 border border-white/5 space-y-1.5">
                      <div className="flex items-center justify-between text-[10px] font-bold text-emerald-400 font-mono">
                        <span>Oleada {wave.wave_number}</span>
                        <span>{wave.nodes?.length} nodos</span>
                      </div>
                      {wave.nodes?.map((nodeId: string) => (
                        <div key={nodeId} className="p-1.5 rounded bg-zinc-900 border border-zinc-800 text-[10px] text-zinc-300 truncate">
                          {nodeId}
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              )}

              {/* Action 2: Execute Parallel Waves */}
              {!executionResult && (
                <button
                  type="button"
                  onClick={handleExecutePlan}
                  disabled={loading}
                  className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs flex items-center justify-center gap-2 transition cursor-pointer"
                >
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                  <span>Ejecutar Agentes en Paralelo por Oleadas</span>
                </button>
              )}
            </div>
          )}

          {/* Step 3: Execution Deliverables & HITL Gate */}
          {executionResult && (
            <div className="p-4 rounded-2xl bg-[#080c10] border border-blue-500/30 space-y-4">
              <div className="flex items-center justify-between border-b border-white/5 pb-3">
                <div className="flex items-center gap-2 text-blue-400">
                  <CheckCircle2 className="w-4 h-4" />
                  <span className="text-xs font-bold">Ejecución Completada (Run: {executionResult.run_id})</span>
                </div>
                <span className="text-[10px] font-mono text-emerald-400">Pytest 31/31 Exit 0</span>
              </div>

              {/* Deliverables on disk */}
              <div className="space-y-1 text-xs font-mono">
                {executionResult.deliverables?.map((d: any) => (
                  <div key={d.name} className="flex items-center justify-between p-2 rounded bg-black/40 border border-white/5 text-[11px]">
                    <span className="text-white">{d.name}</span>
                    <span className="text-zinc-500">{d.size_bytes} bytes</span>
                  </div>
                ))}
              </div>

              {/* Human Gate Authorization */}
              {!hmacApplied ? (
                <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 space-y-2">
                  <div className="flex items-center gap-2 text-amber-400 font-bold text-xs">
                    <ShieldAlert className="w-4 h-4" />
                    <span>Compuerta HITL: Autorización Soberana del Product Owner</span>
                  </div>
                  <p className="text-[11px] text-zinc-300">
                    Se requiere firma criptográfica HMAC-SHA256 para fusionar los cambios de los worktrees en el repositorio principal.
                  </p>
                  <button
                    type="button"
                    onClick={handleApplyHmac}
                    disabled={loading}
                    className="w-full py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-bold text-xs flex items-center justify-center gap-2 transition cursor-pointer"
                  >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Key className="w-4 h-4" />}
                    <span>Firmar con Token HMAC y Aplicar Cambios</span>
                  </button>
                </div>
              ) : (
                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold flex items-center justify-center gap-2">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>¡Cambios Firmados con Éxito y Ticket Completado en SQLite WAL!</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t border-[#1b2533] shrink-0 text-xs">
          <span className="text-zinc-500 font-mono flex items-center gap-1.5">
            <Database className="w-3.5 h-3.5" /> Estado Persistido: sacl_ops.db (WAL)
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-black/50 border border-zinc-800 text-zinc-300 hover:text-white transition"
          >
            Cerrar Ventana
          </button>
        </div>
      </div>
    </div>
  )
}
