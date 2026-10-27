import React, { useState, useEffect } from 'react'
import {
  Bot,
  Cpu,
  Shield,
  CheckCircle2,
  Play,
  RotateCcw,
  Terminal,
  Activity,
  Layers,
  Sparkles,
  Loader2,
  FolderGit2,
  ChevronDown,
  ChevronUp,
  FileText,
  AlertCircle,
} from 'lucide-react'

interface AgentRoleDefinition {
  id: string
  name: string
  role: string
  worktree: string
  model: string
  description: string
  icon: 'host' | 'gov' | 'qa' | 'coder'
}

interface ActiveAgentRunning {
  id: string
  name: string
  role: string
  worktree: string
  command?: string
  status: 'RUNNING' | 'COMPLETED' | 'BLOCKED_ON_GATE' | 'FAILED'
}

const PERMANENT_ROLES: AgentRoleDefinition[] = [
  {
    id: 'AGY-HOST-01',
    name: 'Orquestador Principal',
    role: 'Coordinador de Flujo y Ramas',
    worktree: 'main / integration',
    model: 'Gemini 3.8 / Claude 3.7 Sonnet',
    description: 'Coordina el orden de tareas, inspecciona el estado de Git y guarda el avance en SQLite WAL.',
    icon: 'host',
  },
  {
    id: 'AGENT-GOV-02',
    name: 'Guardián de Aprobaciones (HITL)',
    role: 'Seguridad y Firma HMAC',
    worktree: 'worktrees/gov-audit',
    model: 'Verificador Criptográfico',
    description: 'Prepara el resumen de cambios y solicita tu autorización antes de integrar o desplegar.',
    icon: 'gov',
  },
  {
    id: 'AGENT-QA-03',
    name: 'Ingeniero QA Automatizado',
    role: 'Ejecutor Real de Pytest',
    worktree: 'worktrees/qa-gate',
    model: 'Pytest Suite Runner',
    description: 'Ejecuta físicamente las pruebas unitarias y contratos en Python, midiendo tiempos reales.',
    icon: 'qa',
  },
  {
    id: 'AGENT-CODER-ALPHA',
    name: 'Ingeniero de Código Principal',
    role: 'Implementación de Funcionalidades',
    worktree: 'worktrees/alpha-core',
    model: 'AGY Autonomous Coder',
    description: 'Desarrolla endpoints, componentes e integraciones dentro de su propio árbol de trabajo.',
    icon: 'coder',
  },
  {
    id: 'AGENT-CODER-BETA',
    name: 'Ingeniero de Datos y Persistencia',
    role: 'Esquemas SQLite & Contratos',
    worktree: 'worktrees/beta-adapters',
    model: 'AGY Autonomous Coder',
    description: 'Verifica la integridad de datos, idempotencia y contratos transaccionales.',
    icon: 'coder',
  },
]

export const AgentsSection: React.FC = () => {
  const [fleetState, setFleetState] = useState<any>({
    fleet_state: 'IDLE',
    running_count: 0,
    active_agents: [],
  })
  const [actionHistory, setActionHistory] = useState<any[]>([])
  const [executingAction, setExecutingAction] = useState<string | null>(null)
  const [executionFeedback, setExecutionFeedback] = useState<any | null>(null)
  const [errorBanner, setErrorBanner] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(true)
  const [showCatalog, setShowCatalog] = useState<boolean>(false)
  const [showLogs, setShowLogs] = useState<boolean>(false)

  const loadData = async () => {
    setLoading(true)
    try {
      const fRes = await fetch('/api/agents/fleet')
      if (fRes.ok) {
        const fData = await fRes.json()
        setFleetState(fData || { fleet_state: 'IDLE', running_count: 0, active_agents: [] })
      }
    } catch (e) {
      console.warn('Error loading fleet state:', e)
    }

    try {
      const actRes = await fetch('/api/actions/history')
      if (actRes.ok) {
        const actData = await actRes.json()
        if (actData && actData.history) {
          setActionHistory(actData.history)
        }
      }
    } catch (e) {
      console.warn('Error loading action history:', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleExecuteAction = async (
    actionType: 'campaign_sprint' | 'test_suite' | 'security_audit'
  ) => {
    setExecutingAction(actionType)
    setErrorBanner(null)
    try {
      const res = await fetch('/api/actions/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action_type: actionType, params: {} }),
      })
      const data = await res.json()
      setExecutionFeedback(data)
      await loadData()
    } catch (e: any) {
      setErrorBanner('Error al ejecutar la acción: ' + (e.message || 'Fallo de red'))
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
        return <CheckCircle2 className="w-5 h-5 text-emerald-400" />
      default:
        return <Terminal className="w-5 h-5 text-zinc-300" />
    }
  }

  const activeAgents: ActiveAgentRunning[] = fleetState.active_agents || []
  const activeCount = activeAgents.length
  const isIdle = activeCount === 0 && executingAction === null

  return (
    <div className="space-y-6 max-w-6xl mx-auto text-left pb-12">
      {/* 1. Header Claro (Visibilidad continua del estado real) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 sm:p-6 rounded-2xl bg-zinc-950 border border-zinc-800">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-lg font-bold text-white tracking-tight">
              Equipo de Agentes y Ejecución Real
            </h1>
            <span
              className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold border ${
                isIdle
                  ? 'bg-zinc-900 text-zinc-300 border-zinc-700'
                  : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 animate-pulse'
              }`}
            >
              {isIdle ? 'EN REPOSO (0 TOKENS)' : 'EJECUTANDO COMANDOS REALES'}
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Cada acción ejecuta procesos reales en tu PC (`pytest`, `git status`, `sacl.cli doctor`) y mide su duración exacta.
          </p>
        </div>

        <button
          onClick={loadData}
          disabled={loading}
          className="px-3.5 py-2 rounded-xl bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-xs text-zinc-300 flex items-center gap-2 transition cursor-pointer self-start sm:self-auto"
        >
          <RotateCcw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Actualizar Estado</span>
        </button>
      </div>

      {errorBanner && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-500/40 text-xs text-red-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            <span>{errorBanner}</span>
          </div>
          <button onClick={() => setErrorBanner(null)} className="text-xs underline">
            Cerrar
          </button>
        </div>
      )}

      {/* 2. Panel de Ejecución Directa (Ley de Hick & Fitts: 1 Acción Principal Destacada + 2 Pruebas Rápidas) */}
      <div className="p-5 sm:p-6 rounded-2xl bg-zinc-950 border border-zinc-800 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-11 h-11 rounded-xl bg-zinc-900 border border-zinc-750 flex items-center justify-center text-white shrink-0">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white">Ejecutar Diagnóstico o Sprint en Vivo</h2>
            <p className="text-xs text-zinc-400 mt-0.5">
              Los resultados mostrarán el comando exacto ejecutado, los archivos creados en `runs/` y el tiempo real en segundos.
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {/* CTA Primario (Ley de Hick) */}
          <button
            type="button"
            onClick={() => handleExecuteAction('campaign_sprint')}
            disabled={executingAction !== null}
            className="px-4 py-2.5 rounded-xl bg-white hover:bg-zinc-200 disabled:opacity-50 text-black font-extrabold text-xs flex items-center justify-center gap-2 transition cursor-pointer shadow-sm"
          >
            {executingAction === 'campaign_sprint' ? (
              <Loader2 className="w-4 h-4 animate-spin text-black" />
            ) : (
              <Play className="w-4 h-4 fill-black text-black" />
            )}
            <span>
              {executingAction === 'campaign_sprint'
                ? 'Ejecutando Sprint Real...'
                : 'Ejecutar Sprint Completo'}
            </span>
          </button>

          {/* Acciones Secundarias de Verificación */}
          <button
            type="button"
            onClick={() => handleExecuteAction('test_suite')}
            disabled={executingAction !== null}
            className="px-3.5 py-2.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 disabled:opacity-50 text-zinc-200 border border-zinc-750 font-semibold text-xs flex items-center justify-center gap-2 transition cursor-pointer"
          >
            {executingAction === 'test_suite' ? (
              <Loader2 className="w-4 h-4 animate-spin text-zinc-200" />
            ) : (
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            )}
            <span>Correr Pytest Real</span>
          </button>

          <button
            type="button"
            onClick={() => handleExecuteAction('security_audit')}
            disabled={executingAction !== null}
            className="px-3.5 py-2.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 disabled:opacity-50 text-zinc-200 border border-zinc-750 font-semibold text-xs flex items-center justify-center gap-2 transition cursor-pointer"
          >
            {executingAction === 'security_audit' ? (
              <Loader2 className="w-4 h-4 animate-spin text-zinc-200" />
            ) : (
              <Shield className="w-4 h-4 text-zinc-300" />
            )}
            <span>Auditar Contratos y Git</span>
          </button>
        </div>
      </div>

      {/* 3. Resultado Empírico Paso a Paso (Reconocimiento antes que recuerdo) */}
      {executionFeedback && (
        <div className="p-5 sm:p-6 rounded-2xl bg-zinc-950 border border-emerald-500/40 space-y-4 animate-fade-in shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-850 pb-3">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />
              <div>
                <h3 className="text-sm font-bold text-white">
                  {executionFeedback.title} (Código de salida: {executionFeedback.exit_code ?? 0})
                </h3>
                <p className="text-xs text-zinc-300 mt-0.5">{executionFeedback.summary}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 self-end sm:self-center">
              <span className="px-2.5 py-1 rounded-lg bg-black border border-zinc-800 text-xs font-mono text-emerald-400 font-bold">
                Tiempo Total Medido: {executionFeedback.duration_sec}s
              </span>
              <button
                onClick={() => setExecutionFeedback(null)}
                className="text-xs text-zinc-400 hover:text-white px-2.5 py-1 rounded-lg bg-zinc-900 cursor-pointer"
              >
                Cerrar
              </button>
            </div>
          </div>

          {/* Pasos Reales Medidos */}
          {executionFeedback.steps && executionFeedback.steps.length > 0 && (
            <div className="space-y-2">
              <span className="text-[11px] font-mono uppercase text-zinc-400 block">
                Pasos Físicos Ejecutados en el Sistema:
              </span>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                {executionFeedback.steps.map((st: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-3 rounded-xl bg-black border border-zinc-850 flex items-start justify-between gap-2 text-xs"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 font-semibold text-white">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        <span>{st.name}</span>
                      </div>
                      {st.command && (
                        <code className="text-[11px] font-mono text-zinc-400 block pl-5">
                          $ {st.command}
                        </code>
                      )}
                    </div>
                    <span className="px-2 py-0.5 rounded bg-zinc-900 text-zinc-300 font-mono text-[11px] shrink-0">
                      {st.duration}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Archivos Reales Creados en Disco */}
          {executionFeedback.deliverables && executionFeedback.deliverables.length > 0 && (
            <div className="space-y-2 pt-1">
              <span className="text-[11px] font-mono uppercase text-zinc-400 block">
                Archivos Reales Escritos en Disco ({executionFeedback.deliverables.length}):
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                {executionFeedback.deliverables.map((deliv: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-2.5 rounded-xl bg-black border border-zinc-850 flex items-center gap-2.5 text-xs"
                  >
                    <FileText className="w-4 h-4 text-zinc-300 shrink-0" />
                    <div className="min-w-0">
                      <div className="font-bold text-white truncate">{deliv.name}</div>
                      <div className="text-[10px] font-mono text-zinc-400 truncate">
                        {deliv.rel_path}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Divulgación Progresiva: Salida de Consola */}
          {executionFeedback.logs && executionFeedback.logs.length > 0 && (
            <div className="pt-2 border-t border-zinc-850">
              <button
                type="button"
                onClick={() => setShowLogs(!showLogs)}
                className="text-xs font-mono text-zinc-400 hover:text-white flex items-center gap-1.5 cursor-pointer"
              >
                <Terminal className="w-3.5 h-3.5" />
                <span>
                  {showLogs
                    ? 'Ocultar salida de terminal'
                    : `Ver salida completa de terminal (${executionFeedback.logs.length} líneas)`}
                </span>
                {showLogs ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>

              {showLogs && (
                <div className="mt-2 p-3.5 rounded-xl bg-black border border-zinc-800 font-mono text-[11px] text-zinc-300 max-h-56 overflow-y-auto space-y-1">
                  {executionFeedback.logs.map((ln: string, i: number) => (
                    <div key={i}>{ln}</div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* 4. Estado Actual de Procesos */}
      <div className="p-5 sm:p-6 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-4">
        <div className="flex items-center justify-between border-b border-zinc-850 pb-3">
          <div className="flex items-center gap-2">
            <Bot className="w-4 h-4 text-zinc-200" />
            <h2 className="text-sm font-bold text-white">Procesos de Agentes en este Momento</h2>
          </div>
          <span className="text-xs font-mono text-zinc-400">
            {isIdle ? '0 procesos en ejecución' : 'Ejecución en curso'}
          </span>
        </div>

        {isIdle ? (
          <div className="p-6 rounded-xl bg-black border border-zinc-850 text-center space-y-2">
            <Layers className="w-6 h-6 text-zinc-400 mx-auto" />
            <h3 className="text-xs font-bold text-white uppercase font-mono">
              En Reposo Real (Sin Procesos Simulados)
            </h3>
            <p className="text-xs text-zinc-400 max-w-lg mx-auto">
              Cuando no hay una tarea activa, el sistema no deja procesos falsos corriendo ni gasta tokens en segundo plano. Usa los botones de arriba para ejecutar una prueba o sprint real.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {activeAgents.map((ag) => (
              <div
                key={ag.id}
                className="p-4 rounded-xl bg-black border border-emerald-500/30 space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white">{ag.name}</span>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/20 text-emerald-300">
                    EJECUTANDO
                  </span>
                </div>
                <p className="text-xs text-zinc-400">{ag.role}</p>
                {ag.command && (
                  <code className="block p-2 rounded bg-zinc-950 border border-zinc-800 font-mono text-[11px] text-zinc-300">
                    $ {ag.command}
                  </code>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 5. Historial de Ejecuciones en esta Sesión */}
      <div className="p-5 sm:p-6 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-4">
        <div className="flex items-center justify-between border-b border-zinc-850 pb-3">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-zinc-200" />
            <h2 className="text-sm font-bold text-white">Historial de Ejecuciones Reales</h2>
          </div>
          <span className="text-xs text-zinc-400 font-mono">
            {actionHistory.length} registradas
          </span>
        </div>

        {actionHistory.length === 0 ? (
          <div className="text-center py-6 text-zinc-500 text-xs">
            Aún no has ejecutado acciones en esta sesión. Haz clic en "Ejecutar Sprint Completo" o "Correr Pytest Real".
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-zinc-800 text-[10px] text-zinc-500 uppercase">
                  <th className="pb-2.5">ID</th>
                  <th className="pb-2.5">Acción</th>
                  <th className="pb-2.5">Resumen Empírico</th>
                  <th className="pb-2.5">Tiempo Medido</th>
                  <th className="pb-2.5 text-right">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-850">
                {actionHistory.map((act, i) => (
                  <tr
                    key={act.execution_id || i}
                    onClick={() => setExecutionFeedback(act)}
                    className="hover:bg-zinc-900/50 transition cursor-pointer"
                    title="Haz clic para ver el detalle de pasos y archivos"
                  >
                    <td className="py-3 font-bold text-zinc-300">{act.execution_id}</td>
                    <td className="py-3 text-white font-sans font-semibold">
                      {act.title || act.action_type}
                    </td>
                    <td className="py-3 text-zinc-400 font-sans max-w-md truncate">
                      {act.summary}
                    </td>
                    <td className="py-3 text-emerald-400 font-bold">{act.duration_sec}s</td>
                    <td className="py-3 text-right">
                      <span className="px-2 py-0.5 rounded-full text-[10px] bg-zinc-900 text-zinc-200 border border-zinc-750">
                        {act.status} (Exit {act.exit_code})
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* 6. Divulgación Progresiva: Catálogo de Roles */}
      <div className="rounded-2xl bg-zinc-950 border border-zinc-800 overflow-hidden">
        <button
          type="button"
          onClick={() => setShowCatalog(!showCatalog)}
          className="w-full p-5 flex items-center justify-between hover:bg-zinc-900/50 transition cursor-pointer text-left"
        >
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-zinc-900 border border-zinc-750 flex items-center justify-center text-zinc-300">
              <FolderGit2 className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-xs font-bold text-white">
                Ver Arquitectura de Roles del Equipo IA (5 Especialistas)
              </h3>
              <p className="text-[11px] text-zinc-400 mt-0.5">
                Información de referencia sobre cómo se dividen las tareas durante un sprint.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1.5 text-zinc-400 text-xs font-mono">
            <span>{showCatalog ? 'Ocultar' : 'Mostrar'}</span>
            {showCatalog ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </div>
        </button>

        {showCatalog && (
          <div className="p-5 pt-0 border-t border-zinc-850 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5 mt-4">
            {PERMANENT_ROLES.map((roleDef) => (
              <div
                key={roleDef.id}
                className="p-4 rounded-xl bg-black border border-zinc-850 space-y-2.5"
              >
                <div className="flex items-center justify-between">
                  <div className="w-8 h-8 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center">
                    {getRoleIcon(roleDef.icon)}
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-900 text-zinc-400 border border-zinc-800">
                    {roleDef.id}
                  </span>
                </div>
                <div>
                  <h4 className="text-xs font-bold text-white">{roleDef.name}</h4>
                  <span className="text-[11px] text-zinc-400 block">{roleDef.role}</span>
                </div>
                <p className="text-xs text-zinc-400 leading-relaxed">{roleDef.description}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
