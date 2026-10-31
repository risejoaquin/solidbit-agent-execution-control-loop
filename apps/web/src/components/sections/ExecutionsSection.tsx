import React, { useState, useEffect } from 'react'
import { AgentCard, type AgentCardData } from '../AgentCard'

export const ExecutionsSection: React.FC = () => {
  const [agents, setAgents] = useState<AgentCardData[]>([
    {
      agentName: 'Atlas',
      role: 'Coordinador de Flujos & DAG',
      currentProcess: 'Topological Kahn Scheduler Activo',
      status: 'PASS',
      lastLog: 'DAG topológico verificado sin ciclos de ramas.',
      pid: 14208,
      commitSha: 'b61e2e9',
      lastActive: 'Justo ahora',
    },
    {
      agentName: 'Vega',
      role: 'Arquitecta de Datos & Contratos',
      currentProcess: 'Invariantes DR-INV-001 y DR-PAY-001',
      status: 'PASS',
      lastLog: 'Balance transaccional verificado en SQLite WAL.',
      pid: 14212,
      commitSha: 'b61e2e9',
      lastActive: 'Justo ahora',
    },
    {
      agentName: 'Nova',
      role: 'Inspectora de Calidad & Pytest',
      currentProcess: 'Suite Automatizada de Verificación',
      status: 'PASS',
      lastLog: '37/37 pruebas de UI pasaron exitosamente.',
      pid: 14216,
      commitSha: 'b61e2e9',
      lastActive: 'Justo ahora',
    },
    {
      agentName: 'Centinela',
      role: 'Guardián de Políticas y Hard Deny',
      currentProcess: 'Auditoría Constitucional de Seguridad',
      status: 'PASS',
      lastLog: '9/9 políticas constitucionales validadas.',
      pid: 14220,
      commitSha: 'b61e2e9',
      lastActive: 'Justo ahora',
    },
  ])

  const [pendingGates, setPendingGates] = useState<any[]>([])
  const [selectedGate, setSelectedGate] = useState<any>(null)
  const [decisionLoading, setDecisionLoading] = useState(false)
  const [justification, setJustification] = useState('Autorización humana otorgada con verificación de contratos.')

  const loadPendingGates = async () => {
    try {
      const res = await fetch('/api/gates/pending')
      const data = await res.json()
      if (data && data.gates) {
        setPendingGates(data.gates)
        setSelectedGate(data.gates[0] || null)
      }
    } catch (e) {
      console.warn('Error loading pending gates:', e)
    }
  }

  // Smart Telemetry Ingestion (SSE Stream Listeners with Robust Cleanup)
  useEffect(() => {
    loadPendingGates()

    let sse: EventSource | null = null

    const handleTelemetryEvent = (e: MessageEvent) => {
      try {
        const payload = JSON.parse(e.data)
        const agentName = payload.agent || payload.agent_id || payload.agent_name || payload.component
        if (!agentName) return

        const status = payload.status || (e.type === 'approval_required' ? 'BLOCKED' : 'RUNNING')
        const task = payload.task || payload.current_task || payload.message || payload.goal || 'Proceso en curso'
        const log = payload.reason || payload.last_log || payload.message

        setAgents((prev) => {
          const idx = prev.findIndex((a) => a.agentName.toLowerCase() === String(agentName).toLowerCase())
          const updated: AgentCardData = {
            agentName,
            role: idx >= 0 ? prev[idx].role : 'EOP Execution Agent',
            currentProcess: task,
            status,
            lastLog: log,
            pid: payload.pid || (idx >= 0 ? prev[idx].pid : undefined),
            commitSha: payload.commit || payload.commit_sha || (idx >= 0 ? prev[idx].commitSha : undefined),
            lastActive: 'Justo ahora',
          }

          if (idx >= 0) {
            const next = [...prev]
            next[idx] = { ...next[idx], ...updated }
            return next
          }
          return [updated, ...prev]
        })
      } catch {}
    }

    const handleGateChange = () => loadPendingGates()

    try {
      sse = new EventSource('/api/events/stream')
      sse.addEventListener('task_running', handleTelemetryEvent)
      sse.addEventListener('agent_spawned', handleTelemetryEvent)
      sse.addEventListener('artifact_generated', handleTelemetryEvent)
      sse.addEventListener('approval_required', handleTelemetryEvent)
      sse.addEventListener('heartbeat_recorded', handleTelemetryEvent)
      sse.addEventListener('agent_event', handleTelemetryEvent)
      sse.addEventListener('gate_requested', handleGateChange)
      sse.addEventListener('gate_decided', handleGateChange)
    } catch {
      console.warn('SSE stream not supported in ExecutionsSection')
    }

    return () => {
      if (sse) {
        sse.removeEventListener('task_running', handleTelemetryEvent)
        sse.removeEventListener('agent_spawned', handleTelemetryEvent)
        sse.removeEventListener('artifact_generated', handleTelemetryEvent)
        sse.removeEventListener('approval_required', handleTelemetryEvent)
        sse.removeEventListener('heartbeat_recorded', handleTelemetryEvent)
        sse.removeEventListener('agent_event', handleTelemetryEvent)
        sse.removeEventListener('gate_requested', handleGateChange)
        sse.removeEventListener('gate_decided', handleGateChange)
        sse.close()
      }
    }
  }, [])

  const handleDecision = async (decision: 'APPROVED' | 'REJECTED') => {
    if (!selectedGate) return
    setDecisionLoading(true)
    try {
      await fetch('/api/gates/decide', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          request_id: selectedGate.request_id,
          decision,
          authorizer: 'Operador Principal',
          rationale: justification,
        }),
      })
      await loadPendingGates()
    } catch (err) {
      console.warn('Error submitting decision:', err)
    } finally {
      setDecisionLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full w-full bg-[#000000] space-y-3 select-none">
      {/* Header Aeronáutico Técnico */}
      <div className="h-12 border border-white/8 bg-[#0a0a0a] rounded px-4 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shrink-0" />
          <span className="text-xs font-semibold text-white tracking-wide uppercase font-sans">
            Control Loop en Tiempo Real
          </span>
          <span className="text-[10px] font-mono text-zinc-500">
            · {agents.length} agentes coordinados por Kahn DAG
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-zinc-400">Stream SSE :8765</span>
          <span className="text-[9px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-1.5 py-0.5 rounded">
            LIVE
          </span>
        </div>
      </div>

      {/* Compuerta Humana Pendiente (Si existe) */}
      {selectedGate && (
        <div className="bg-[#0a0a0a] border border-amber-500/30 rounded p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 text-amber-400 text-xs font-semibold">
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
              <span>Compuerta de Decisión Activa: {selectedGate.action || 'Fase de Integración'}</span>
            </div>
            <p className="text-[11px] text-zinc-400 mt-1 font-sans">
              {selectedGate.rationale || 'Se requiere validación de firma HMAC para avanzar el DAG.'}
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => handleDecision('REJECTED')}
              disabled={decisionLoading}
              className="px-3 py-1.5 rounded text-xs font-medium border border-red-500/30 text-red-400 hover:bg-red-500/10 transition cursor-pointer"
            >
              Rechazar
            </button>
            <button
              onClick={() => handleDecision('APPROVED')}
              disabled={decisionLoading}
              className="px-3.5 py-1.5 rounded text-xs font-medium bg-emerald-500 text-black hover:bg-emerald-400 font-semibold transition cursor-pointer"
            >
              Aprobar Entrega
            </button>
          </div>
        </div>
      )}

      {/* Cuadrícula de Alta Densidad (Agent Cards) */}
      <div className="flex-1 overflow-y-auto custom-scroll">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
          {agents.map((agent) => (
            <AgentCard key={agent.agentName} agent={agent} />
          ))}
        </div>
      </div>
    </div>
  )
}
