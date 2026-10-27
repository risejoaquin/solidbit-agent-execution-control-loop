import React, { useState, useEffect } from 'react'
import {
  Bot,
  Cpu,
  Shield,
  CheckCircle2,
  AlertTriangle,
  Play,
  RotateCcw,
  Terminal,
  Activity,
  Layers,
  Sparkles,
  Loader2,
  Radio,
  FileCode,
  FolderGit2,
  XCircle,
  Eye,
} from 'lucide-react'
import { formatSmartDateTime } from '../../utils/dateFormat'

interface AgentRoleDefinition {
  id: string
  name: string
  role: string
  worktree: string
  model: string
  description: string
  responsibility: string
  icon: 'host' | 'gov' | 'qa' | 'coder'
}

interface OSProcessItem {
  id: string
  pid: number | null
  name: string
  type: string
  role: string
  status: string
  memory_mb?: number
  log_size_kb?: number
  last_updated?: string
}

const PERMANENT_ROLES: AgentRoleDefinition[] = [
  {
    id: 'AGY-HOST-01',
    name: 'Antigravity Host Daemon',
    role: 'Orquestador Maestro (Kernel)',
    worktree: 'main / host',
    model: 'Gemini 3.8 / Claude 3.7 Sonnet',
    description: 'Controlador del bucle SACL, particionado acíclico DAG y despacho de oleadas.',
    responsibility: 'Garantizar regla Dirty-Root y durabilidad ACID en SQLite WAL.',
    icon: 'host',
  },
  {
    id: 'AGENT-GOV-02',
    name: 'HITL Sentinel',
    role: 'Compuertas Soberanas & Seguridad',
    worktree: 'worktrees/gov-audit',
    model: 'Inferencia Determinista',
    description: 'Custodio criptográfico de compuertas HITL y validación de tokens HMAC-SHA256.',
    responsibility: 'Bloquear despliegues no autorizados e inspeccionar dossier de cambios.',
    icon: 'gov',
  },
  {
    id: 'AGENT-QA-03',
    name: 'Zero-Bypass QA Engineer',
    role: 'Verificador de Invariantes & Pytest',
    worktree: 'worktrees/qa-gate',
    model: 'Pytest Suite Runner',
    description: 'Ejecución rigurosa de 155 pruebas de seguridad STRIDE y 34 contratos congelados.',
    responsibility: 'Exigir 100% verde en pruebas antes de permitir cualquier merge.',
    icon: 'qa',
  },
  {
    id: 'AGENT-CODER-ALPHA',
    name: 'Senior Core Engineer',
    role: 'Síntesis de Lógica Central',
    worktree: 'worktrees/alpha-core',
    model: 'AGY Autonomous Coder',
    description: 'Implementación aislada de flujos atómicos, endpoints REST y reglas de negocio.',
    responsibility: 'Código limpio, tipado estricto y cero acoplamiento indebido.',
    icon: 'coder',
  },
  {
    id: 'AGENT-CODER-BETA',
    name: 'Senior Systems Engineer',
    role: 'Adaptadores & Idempotencia',
    worktree: 'worktrees/beta-adapters',
    model: 'AGY Autonomous Coder',
    description: 'Construcción de capas de persistencia SQLite WAL, deduplicación e idempotencia.',
    responsibility: 'Garantizar contratos DR-INV-001, DR-PAY-001 y DR-IDEM-001.',
    icon: 'coder',
  },
]

export const AgentsSection: React.FC = () => {
  const [fleetState, setFleetState] = useState<any>({ fleet_state: 'IDLE', running_count: 0, active_agents: [] })
  const [osProcesses, setOsProcesses] = useState<OSProcessItem[]>([])
  const [actionHistory, setActionHistory] = useState<any[]>([])
  const [executingAction, setExecutingAction] = useState<string | null>(null)
  const [executionFeedback, setExecutionFeedback] = useState<any | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [selectedProcessLog, setSelectedProcessLog] = useState<{ id: string; content: string } | null>(null)
  const [killingId, setKillingId] = useState<string | null>(null)

  const loadData = async () => {
    setLoading(true)
    try {
      // 1. Real Agent Fleet State from backend
      try {
        const fRes = await fetch('/api/agents/fleet')
        const fData = await fRes.json()
        setFleetState(fData || { fleet_state: 'IDLE', running_count: 0, active_agents: [] })
      } catch (e) {
        console.warn('Error loading fleet state:', e)
      }

      // 2. Real OS Tasks / Background daemons from backend
      try {
        const subRes = await fetch('/api/subagents/list')
        const subData = await subRes.json()
        if (subData && subData.tasks) {
          // Filter to running or unique real processes
          setOsProcesses(subData.tasks.filter((t: any) => t.status === 'RUNNING' || t.pid))
        }
      } catch (e) {
        console.warn('Error loading OS processes:', e)
      }

      // 3. Real Agent Action History from backend
      try {
        const actRes = await fetch('/api/actions/history')
        const actData = await actRes.json()
        if (actData && actData.history) {
          setActionHistory(actData.history)
        }
      } catch (e) {
        console.warn('Error loading action history:', e)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleExecuteAction = async (actionType: 'campaign_sprint' | 'test_suite' | 'security_audit') => {
    setExecutingAction(actionType)
    setExecutionFeedback(null)
    try {
      const res = await fetch('/api/actions/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: actionType, params: {} }),
      })
      const data = await res.json()
      setExecutionFeedback(data)
      loadData()
    } catch (e: any) {
      alert('Error ejecutando acción de agente: ' + e.message)
    } finally {
      setExecutingAction(null)
    }
  }

  const handleViewProcessLog = async (procId: string) => {
    try {
      const res = await fetch(`/api/subagents/logs?task_id=${encodeURIComponent(procId)}`)
      const data = await res.json()
      setSelectedProcessLog({
        id: procId,
        content: data.logs || data.content || 'Sin registros recientes en el buffer.',
      })
    } catch (e: any) {
      alert('Error leyendo log: ' + e.message)
    }
  }

  const handleKillProcess = async (procId: string) => {
    if (!confirm(`¿Confirmas la detención forzosa del proceso ${procId}?`)) return
    setKillingId(procId)
    try {
      const res = await fetch('/api/subagents/kill', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_id: procId }),
      })
      const data = await res.json()
      alert(`Proceso ${procId}: ${data.message || (data.success ? 'Detenido con éxito.' : 'No se pudo detener.')}`)
      loadData()
    } catch (e: any) {
      alert('Error al detener proceso: ' + e.message)
    } finally {
      setKillingId(null)
    }
  }

  const getRoleIcon = (icon: AgentRoleDefinition['icon']) => {
    switch (icon) {
      case 'host':
        return <Sparkles className="w-5 h-5 text-zinc-100" />
      case 'gov':
        return <Shield className="w-5 h-5 text-amber-400" />
      case 'qa':
        return <CheckCircle2 className="w-5 h-5 text-zinc-200" />
      default:
        return <Terminal className="w-5 h-5 text-zinc-300" />
    }
  }

  const activeAgentsCount = fleetState.active_agents?.length ?? 0
  const isIdle = activeAgentsCount === 0

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* 1. Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-3xl bg-zinc-950 border border-zinc-800">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold text-white tracking-wide">
              Flota de Agentes Autónomos & Supervisión de Procesos OS
            </h1>
            <span
              className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold border ${
                isIdle
                  ? 'bg-zinc-900 text-zinc-300 border-zinc-700'
                  : 'bg-white text-black border-white animate-pulse'
              }`}
            >
              {isIdle ? 'ZERO-TOKEN IDLE' : `${activeAgentsCount} AGENTES ACTIVOS`}
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Supervisión soberana de agentes de IA, procesos reales del sistema operativo y aislamiento en ramas efímeras
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={loading}
          className="px-3.5 py-2 rounded-xl bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-xs text-zinc-300 flex items-center gap-2 transition cursor-pointer self-start sm:self-auto"
        >
          <RotateCcw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Actualizar Telemetría</span>
        </button>
      </div>

      {/* 2. Control & Dispatch Banner */}
      <div className="p-5 rounded-3xl bg-zinc-950 border border-zinc-800 flex flex-col lg:flex-row lg:items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-zinc-900 border border-zinc-750 flex items-center justify-center text-white shrink-0">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-white font-mono uppercase tracking-wide">
                Despacho Manual de Agentes
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-zinc-900 text-zinc-400 border border-zinc-800">
                Kahn DAG
              </span>
            </div>
            <p className="text-[11px] text-zinc-400 mt-0.5">
              Lanza agentes en procesos aislados para ejecutar pruebas, generar código o verificar contratos.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
          <button
            type="button"
            onClick={() => handleExecuteAction('campaign_sprint')}
            disabled={executingAction !== null}
            className="px-4 py-2.5 rounded-xl bg-white hover:bg-zinc-200 disabled:opacity-50 text-black font-extrabold text-xs flex items-center justify-center gap-2 transition cursor-pointer shadow-sm active:scale-[0.99]"
          >
            {executingAction === 'campaign_sprint' ? (
              <Loader2 className="w-4 h-4 animate-spin text-black" />
            ) : (
              <Play className="w-4 h-4 fill-black text-black" />
            )}
            <span>Lanzar Oleada Kahn</span>
          </button>

          <button
            type="button"
            onClick={() => handleExecuteAction('test_suite')}
            disabled={executingAction !== null}
            className="px-4 py-2.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 disabled:opacity-50 text-zinc-200 border border-zinc-700 font-bold text-xs flex items-center justify-center gap-2 transition cursor-pointer active:scale-[0.99]"
          >
            {executingAction === 'test_suite' ? (
              <Loader2 className="w-4 h-4 animate-spin text-zinc-200" />
            ) : (
              <CheckCircle2 className="w-4 h-4 text-zinc-300" />
            )}
            <span>Correr Pytest (QA)</span>
          </button>

          <button
            type="button"
            onClick={() => handleExecuteAction('security_audit')}
            disabled={executingAction !== null}
            className="px-4 py-2.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 disabled:opacity-50 text-zinc-200 border border-zinc-700 font-bold text-xs flex items-center justify-center gap-2 transition cursor-pointer active:scale-[0.99]"
          >
            {executingAction === 'security_audit' ? (
              <Loader2 className="w-4 h-4 animate-spin text-zinc-200" />
            ) : (
              <Shield className="w-4 h-4 text-zinc-300" />
            )}
            <span>Auditar Invariantes</span>
          </button>
        </div>
      </div>

      {/* Execution Feedback Banner */}
      {executionFeedback && (
        <div className="p-4 rounded-2xl bg-zinc-950 border border-zinc-750 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono animate-fade-in shadow-md">
          <div className="flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-zinc-200 shrink-0" />
            <div>
              <span className="text-white font-bold block">
                {executionFeedback.title || 'Ejecución de Agente Completada'} (Exit {executionFeedback.exit_code ?? 0})
              </span>
              <span className="text-[11px] text-zinc-400 block mt-0.5">
                ID: {executionFeedback.execution_id} &bull; Duración: {executionFeedback.duration_sec || 0.8}s &bull; Worktree: integration
              </span>
            </div>
          </div>
          <button
            onClick={() => setExecutionFeedback(null)}
            className="text-zinc-400 hover:text-white px-2 py-1 rounded hover:bg-zinc-900 self-end sm:self-auto cursor-pointer"
          >
            Cerrar
          </button>
        </div>
      )}

      {/* 3. The 5 Permanent SACL Agent Roles */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bot className="w-4 h-4 text-zinc-200" />
            <h2 className="text-sm font-bold text-white tracking-wide">
              Definición de Roles & Worktrees de la Flota (SB-ENG-HB-001)
            </h2>
          </div>
          <span className="text-xs text-zinc-400 font-mono">5 Agentes Especializados</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {PERMANENT_ROLES.map((roleDef) => (
            <div
              key={roleDef.id}
              className="p-4 rounded-2xl bg-zinc-950 border border-zinc-800 hover:border-zinc-700 transition flex flex-col justify-between space-y-3"
            >
              <div className="space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <div className="w-9 h-9 rounded-xl bg-zinc-900 border border-zinc-750 flex items-center justify-center text-zinc-200 shrink-0">
                    {getRoleIcon(roleDef.icon)}
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-zinc-900 text-zinc-300 border border-zinc-800">
                      {roleDef.id}
                    </span>
                  </div>
                </div>

                <div>
                  <h3 className="text-xs font-bold text-white">{roleDef.name}</h3>
                  <span className="text-[11px] font-mono text-zinc-400 block mt-0.5">{roleDef.role}</span>
                </div>

                <p className="text-xs text-zinc-400 leading-relaxed">{roleDef.description}</p>
              </div>

              <div className="space-y-1.5 pt-2 border-t border-zinc-850 text-[10px] font-mono">
                <div className="flex items-center justify-between text-zinc-400">
                  <span className="text-zinc-500">Worktree:</span>
                  <span className="text-zinc-300 font-semibold truncate max-w-[170px]">{roleDef.worktree}</span>
                </div>
                <div className="flex items-center justify-between text-zinc-400">
                  <span className="text-zinc-500">Modelo / Motor:</span>
                  <span className="text-zinc-300 font-semibold">{roleDef.model}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 4. Active OS Daemons & Real Background Processes (/api/subagents/list) */}
      <div className="p-5 sm:p-6 rounded-3xl bg-zinc-950 border border-zinc-800 space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-zinc-800 pb-3">
          <div className="flex items-center gap-2.5">
            <Radio className="w-4 h-4 text-zinc-200" />
            <h2 className="text-sm font-bold text-white">
              Procesos en Vivo del Sistema Operativo & Daemons (/api/subagents/list)
            </h2>
          </div>
          <span className="text-xs font-mono text-zinc-400">
            {osProcesses.length} procesos reales en ejecución
          </span>
        </div>

        {osProcesses.length === 0 ? (
          <div className="p-6 rounded-2xl bg-black border border-zinc-850 text-center space-y-2">
            <span className="text-xs font-mono font-bold text-zinc-400 block">CERO PROCESOS SECUNDARIOS</span>
            <p className="text-xs text-zinc-500">No hay procesos secundarios o túneles ejecutándose en este momento.</p>
          </div>
        ) : (
          <div className="overflow-x-auto custom-scroll">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-zinc-800 text-[11px] text-zinc-400">
                  <th className="pb-2.5 pl-2">Identificador</th>
                  <th className="pb-2.5">PID (SO)</th>
                  <th className="pb-2.5">Rol / Tarea</th>
                  <th className="pb-2.5">Memoria</th>
                  <th className="pb-2.5">Estado</th>
                  <th className="pb-2.5 text-right pr-2">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-850">
                {osProcesses.map((proc) => (
                  <tr key={proc.id} className="hover:bg-zinc-900/50 transition">
                    <td className="py-3 pl-2">
                      <span className="font-bold text-white block">{proc.name}</span>
                      <span className="text-[10px] text-zinc-500">{proc.id}</span>
                    </td>
                    <td className="py-3">
                      <span className="px-2 py-0.5 rounded bg-zinc-900 text-zinc-300 border border-zinc-800 text-[10px] font-bold">
                        PID {proc.pid ?? 'EXEC'}
                      </span>
                    </td>
                    <td className="py-3 text-zinc-300 text-xs font-sans max-w-xs truncate">
                      {proc.role}
                    </td>
                    <td className="py-3 text-zinc-400 text-xs">
                      {proc.memory_mb ? `${proc.memory_mb.toFixed(1)} MB` : 'Ligero'}
                    </td>
                    <td className="py-3">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-white text-black">
                        <span className="w-1.5 h-1.5 rounded-full bg-black animate-ping" />
                        RUNNING
                      </span>
                    </td>
                    <td className="py-3 text-right pr-2 space-x-2">
                      <button
                        type="button"
                        onClick={() => handleViewProcessLog(proc.id)}
                        className="px-2.5 py-1 rounded-lg bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-zinc-300 text-[11px] transition cursor-pointer"
                        title="Ver logs en vivo"
                      >
                        Logs
                      </button>
                      <button
                        type="button"
                        onClick={() => handleKillProcess(proc.id)}
                        disabled={killingId === proc.id}
                        className="px-2.5 py-1 rounded-lg bg-red-950/40 border border-red-500/30 hover:bg-red-900/50 text-red-300 text-[11px] transition cursor-pointer"
                        title="Detener proceso"
                      >
                        {killingId === proc.id ? 'Deteniendo...' : 'Detener'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* 5. Real Actions Executed Table (/api/actions/history) */}
      <div className="p-5 sm:p-6 rounded-3xl bg-zinc-950 border border-zinc-800 space-y-4 shadow-xl">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-zinc-200" />
            <h2 className="text-sm font-bold text-white">
              Historial de Acciones Ejecutadas por Agentes (/api/actions/history)
            </h2>
          </div>
          <span className="text-xs text-zinc-400 font-mono">{actionHistory.length} ejecuciones</span>
        </div>

        <div className="overflow-x-auto custom-scroll">
          {actionHistory.length === 0 ? (
            <p className="text-xs text-zinc-500 py-3 font-mono">No hay ejecuciones de acciones registradas aún.</p>
          ) : (
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-zinc-800 text-[10px] text-zinc-500">
                  <th className="pb-2.5">Execution ID</th>
                  <th className="pb-2.5">Acción</th>
                  <th className="pb-2.5">Duración</th>
                  <th className="pb-2.5">Exit Code</th>
                  <th className="pb-2.5 pr-2">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-850">
                {actionHistory.map((act, i) => (
                  <tr key={act.execution_id || i} className="hover:bg-zinc-900/40 transition">
                    <td className="py-2.5 font-bold text-zinc-300">{act.execution_id}</td>
                    <td className="py-2.5 text-white">{act.title || act.action_type}</td>
                    <td className="py-2.5 text-zinc-400">{act.duration_sec}s</td>
                    <td className="py-2.5 text-zinc-200">{act.exit_code}</td>
                    <td className="py-2.5 pr-2">
                      <span className="px-2 py-0.5 rounded-full text-[10px] bg-zinc-900 text-zinc-300 border border-zinc-750">
                        {act.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Log Modal */}
      {selectedProcessLog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
          <div className="bg-zinc-950 border border-zinc-800 rounded-2xl max-w-2xl w-full p-5 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <span className="font-mono text-xs font-bold text-white">
                Log Buffer: {selectedProcessLog.id}
              </span>
              <button
                onClick={() => setSelectedProcessLog(null)}
                className="text-zinc-400 hover:text-white p-1 rounded transition cursor-pointer"
              >
                Cerrar
              </button>
            </div>
            <pre className="p-3 rounded-xl bg-black border border-zinc-850 font-mono text-[11px] text-zinc-300 max-h-80 overflow-y-auto custom-scroll whitespace-pre-wrap">
              {selectedProcessLog.content}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}
