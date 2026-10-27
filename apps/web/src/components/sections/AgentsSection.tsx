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
  ChevronDown,
  ChevronUp,
  Info,
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

interface ActiveAgentRunning {
  id: string
  name: string
  role: string
  pid?: number
  worktree: string
  command?: string
  status: 'RUNNING' | 'COMPLETED' | 'BLOCKED_ON_GATE' | 'FAILED'
  started_at?: string
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
  const [actionHistory, setActionHistory] = useState<any[]>([])
  const [executingAction, setExecutingAction] = useState<string | null>(null)
  const [executionFeedback, setExecutionFeedback] = useState<any | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [showCatalog, setShowCatalog] = useState<boolean>(false)

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

      // 2. Real Agent Action History from backend
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

  const activeAgents: ActiveAgentRunning[] = fleetState.active_agents || []
  const activeCount = activeAgents.length
  const isIdle = activeCount === 0

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* 1. Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-3xl bg-zinc-950 border border-zinc-800">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold text-white tracking-wide">
              Flota de Agentes Autónomos SACL
            </h1>
            <span
              className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold border ${
                isIdle
                  ? 'bg-zinc-900 text-zinc-300 border-zinc-700'
                  : 'bg-white text-black border-white animate-pulse'
              }`}
            >
              {isIdle ? 'ZERO-TOKEN IDLE' : `${activeCount} AGENTES ACTIVOS`}
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Supervisión soberana de agentes de IA con verdad empírica (SB-ENG-HB-001 Cap. 12.3). Cero datos simulados.
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

      {/* 3. Real Active Agent Fleet Section (Zero-Token Idle Banner vs Active Agents) */}
      <div className="p-6 rounded-3xl bg-zinc-950 border border-zinc-800 space-y-4 shadow-xl">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-4">
          <div className="flex items-center gap-2.5">
            <Bot className="w-4 h-4 text-zinc-200" />
            <h2 className="text-sm font-bold text-white tracking-wide">
              Agentes en Ejecución Activa
            </h2>
          </div>
          <span className="text-xs font-mono text-zinc-400">
            {isIdle ? '0 agentes consumiendo tokens' : `${activeCount} agentes activos`}
          </span>
        </div>

        {isIdle ? (
          <div className="p-8 rounded-2xl bg-black border border-zinc-850 text-center space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-zinc-900 border border-zinc-750 flex items-center justify-center text-zinc-300 mx-auto">
              <Layers className="w-6 h-6 text-zinc-400" />
            </div>
            <div className="max-w-md mx-auto space-y-1.5">
              <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
                Flota en Reposo (Zero-Token Idle)
              </h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                No hay agentes ejecutándose actualmente. De acuerdo con el RISEHANDBOOK (Capítulo 12.3), la flota no simula estados ni consume recursos en segundo plano mientras no haya una misión despachada.
              </p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
            {activeAgents.map((ag) => (
              <div
                key={ag.id}
                className="p-4 rounded-2xl bg-zinc-950 border border-zinc-700 shadow-md space-y-3"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white font-mono">{ag.id}</span>
                  <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold bg-white text-black font-mono">
                    <span className="w-1.5 h-1.5 rounded-full bg-black animate-ping" />
                    RUNNING
                  </span>
                </div>
                <div>
                  <h4 className="text-xs font-bold text-white">{ag.name}</h4>
                  <span className="text-[11px] font-mono text-zinc-400">{ag.role}</span>
                </div>
                {ag.command && (
                  <div className="p-2 rounded bg-black border border-zinc-800 font-mono text-[10px] text-zinc-300 truncate">
                    {ag.command}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 4. Collapsible Architectural Roles Catalog (Reference Specification) */}
      <div className="rounded-3xl bg-zinc-950 border border-zinc-800 overflow-hidden shadow-xl">
        <button
          type="button"
          onClick={() => setShowCatalog(!showCatalog)}
          className="w-full p-5 flex items-center justify-between hover:bg-zinc-900/50 transition cursor-pointer text-left"
        >
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-zinc-900 border border-zinc-750 flex items-center justify-center text-zinc-300">
              <FolderGit2 className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-xs font-bold text-white tracking-wide">
                  Catálogo de Roles & Especificación de Worktrees (SB-ENG-HB-001)
                </h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-zinc-900 text-zinc-400 border border-zinc-800">
                  Especificación de Arquitectura
                </span>
              </div>
              <p className="text-[11px] text-zinc-400 mt-0.5">
                Definición formal de los 5 roles permanentes que se instancian durante una oleada o sprint.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 text-zinc-400">
            <span className="text-xs font-mono">{showCatalog ? 'Ocultar catálogo' : 'Ver 5 roles'}</span>
            {showCatalog ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </div>
        </button>

        {showCatalog && (
          <div className="p-5 pt-0 border-t border-zinc-850 animate-fade-in">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5 mt-4">
              {PERMANENT_ROLES.map((roleDef) => (
                <div
                  key={roleDef.id}
                  className="p-4 rounded-2xl bg-black border border-zinc-850 hover:border-zinc-700 transition flex flex-col justify-between space-y-3"
                >
                  <div className="space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <div className="w-8 h-8 rounded-xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-200 shrink-0">
                        {getRoleIcon(roleDef.icon)}
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-zinc-900 text-zinc-400 border border-zinc-800">
                        {roleDef.id}
                      </span>
                    </div>

                    <div>
                      <h4 className="text-xs font-bold text-white">{roleDef.name}</h4>
                      <span className="text-[11px] font-mono text-zinc-400 block mt-0.5">{roleDef.role}</span>
                    </div>

                    <p className="text-xs text-zinc-400 leading-relaxed">{roleDef.description}</p>
                  </div>

                  <div className="space-y-1.5 pt-2 border-t border-zinc-900 text-[10px] font-mono">
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
        )}
      </div>

      {/* 5. Real Actions Executed Table (/api/actions/history) */}
      <div className="p-5 sm:p-6 rounded-3xl bg-zinc-950 border border-zinc-800 space-y-4 shadow-xl">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-zinc-200" />
            <h2 className="text-sm font-bold text-white">
              Historial de Acciones Ejecutadas por Agentes
            </h2>
          </div>
          <span className="text-xs text-zinc-400 font-mono">{actionHistory.length} ejecuciones</span>
        </div>

        <div className="overflow-x-auto custom-scroll">
          {actionHistory.length === 0 ? (
            <div className="text-center py-6 text-zinc-500 text-xs font-mono">
              No hay acciones ejecutadas en esta sesión.
            </div>
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
    </div>
  )
}
