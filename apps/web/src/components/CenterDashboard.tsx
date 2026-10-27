import React, { useState } from 'react'
import {
  CheckCircle2,
  AlertTriangle,
  Play,
  ShieldCheck,
  Loader2,
  Sparkles,
  ArrowRight,
  MessageSquare,
  ChevronDown,
  ChevronUp,
  Terminal,
  Folder,
  Bot,
  CheckSquare,
} from 'lucide-react'
import type {
  TaskItem,
  AgentItem,
  CommitItem,
  Project,
  ActivityEvent,
} from '../types/orchestrator'
import { LogTerminal } from './LogTerminal'
import { ConnectedTechnologiesMatrix, type TechnologyItem } from './ConnectedTechnologiesMatrix'

interface CenterDashboardProps {
  tasks: TaskItem[]
  agents: AgentItem[]
  commits: CommitItem[]
  projects: Project[]
  events: ActivityEvent[]
  connections?: TechnologyItem[]
  onRefreshConnections?: () => void
  activeSprintTitle?: string
  activeSprintDesc?: string
  onOpenSprintModal: () => void
  onNavigateSection: (section: string) => void
  pendingGatesCount?: number
}

export const CenterDashboard: React.FC<CenterDashboardProps> = ({
  tasks,
  agents,
  events,
  connections = [],
  onRefreshConnections,
  onOpenSprintModal,
  onNavigateSection,
  pendingGatesCount = 0,
}) => {
  const [executingAction, setExecutingAction] = useState<string | null>(null)
  const [lastExecutionResult, setLastExecutionResult] = useState<any | null>(null)
  const [showTechnicalLogs, setShowTechnicalLogs] = useState<boolean>(false)

  const completedCount = tasks.filter((t) => t.status === 'Completada').length
  const activeAgentsCount = agents.filter((a) => a.status === 'Activo').length
  const progressPercent = tasks.length > 0 ? Math.round((completedCount / tasks.length) * 100) : 0

  const handleExecuteRealAction = async (
    actionType: 'campaign_sprint' | 'test_suite' | 'security_audit'
  ) => {
    setExecutingAction(actionType)
    try {
      const res = await fetch('/api/actions/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action_type: actionType, params: {} }),
      })
      const data = await res.json()
      setLastExecutionResult(data)
    } catch (err) {
      console.error('Error executing action:', err)
    } finally {
      setExecutingAction(null)
    }
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* =====================================================================
          1. HERO DE BIENVENIDA: "¿QUÉ QUIERES HACER HOY?" (3 CARTAS CLARAS)
         ===================================================================== */}
      <section className="rounded-3xl bg-zinc-950 border border-zinc-800 p-5 sm:p-7 space-y-6 shadow-2xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-zinc-850 pb-5">
          <div className="space-y-1">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-white text-black">
              Centro de Trabajo Simplificado
            </span>
            <h1 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight pt-1">
              ¿Qué necesitas hacer hoy en tu proyecto?
            </h1>
            <p className="text-xs sm:text-sm text-zinc-400">
              Elige una de las 3 acciones principales para comenzar sin configuraciones complicadas.
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              type="button"
              onClick={() => handleExecuteRealAction('test_suite')}
              disabled={executingAction !== null}
              className="px-3.5 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-750 text-xs font-semibold text-zinc-200 flex items-center gap-2 transition cursor-pointer"
              title="Revisar automáticamente que todo el sistema funcione bien"
            >
              {executingAction === 'test_suite' ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
              )}
              <span>Verificar Salud del Sistema</span>
            </button>
          </div>
        </div>

        {/* 3 Giant, Unambiguous Action Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Card 1: Create New Task / Sprint */}
          <div
            onClick={onOpenSprintModal}
            className="p-5 rounded-2xl bg-white text-black hover:bg-zinc-100 transition cursor-pointer flex flex-col justify-between space-y-4 shadow-lg group"
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="w-10 h-10 rounded-xl bg-black text-white flex items-center justify-center">
                  <Sparkles className="w-5 h-5" />
                </div>
                <span className="text-[10px] font-mono font-extrabold uppercase px-2 py-0.5 rounded-full bg-black/10 text-black">
                  Paso 1 Recomendado
                </span>
              </div>
              <h2 className="text-base font-extrabold tracking-tight pt-1">
                1. Pedir un Cambio o Mejora
              </h2>
              <p className="text-xs text-zinc-700 leading-relaxed">
                Describe con tus palabras qué función nueva quieres agregar o qué error necesitas reparar.
              </p>
            </div>

            <div className="pt-2 border-t border-black/10 flex items-center justify-between text-xs font-extrabold">
              <span>Abrir asistente de 3 pasos</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>

          {/* Card 2: Chat with AI Assistant */}
          <div
            onClick={() => onNavigateSection('chat')}
            className="p-5 rounded-2xl bg-black border border-zinc-800 hover:border-zinc-600 transition cursor-pointer flex flex-col justify-between space-y-4 group"
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="w-10 h-10 rounded-xl bg-zinc-900 border border-zinc-750 text-white flex items-center justify-center">
                  <MessageSquare className="w-5 h-5" />
                </div>
                <span className="text-[10px] font-mono text-zinc-400">Ayuda interactiva</span>
              </div>
              <h2 className="text-base font-bold text-white tracking-tight pt-1">
                2. Consultar al Asistente IA
              </h2>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Hazle preguntas en español sobre tu tienda, pídele ideas o revisa el estado de cualquier archivo.
              </p>
            </div>

            <div className="pt-2 border-t border-zinc-850 flex items-center justify-between text-xs font-bold text-zinc-200 group-hover:text-white">
              <span>Ir al chat de ayuda</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>

          {/* Card 3: Review & Approve Deliveries */}
          <div
            onClick={() => onNavigateSection('executions')}
            className={`p-5 rounded-2xl border transition cursor-pointer flex flex-col justify-between space-y-4 group ${
              pendingGatesCount > 0
                ? 'bg-amber-500/10 border-amber-500/40 hover:border-amber-400'
                : 'bg-black border-zinc-800 hover:border-zinc-600'
            }`}
          >
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center border ${
                    pendingGatesCount > 0
                      ? 'bg-amber-400 text-black border-amber-300'
                      : 'bg-zinc-900 border-zinc-750 text-white'
                  }`}
                >
                  {pendingGatesCount > 0 ? (
                    <AlertTriangle className="w-5 h-5" />
                  ) : (
                    <CheckCircle2 className="w-5 h-5" />
                  )}
                </div>
                <span
                  className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full ${
                    pendingGatesCount > 0
                      ? 'bg-amber-400 text-black'
                      : 'bg-zinc-900 text-zinc-400'
                  }`}
                >
                  {pendingGatesCount > 0
                    ? `${pendingGatesCount} esperando tu OK`
                    : 'Todo al día'}
                </span>
              </div>
              <h2 className="text-base font-bold text-white tracking-tight pt-1">
                3. Aprobar y Publicar
              </h2>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Nada se publica sin tu permiso. Revisa los trabajos terminados y autorízalos con 1 clic.
              </p>
            </div>

            <div className="pt-2 border-t border-zinc-850 flex items-center justify-between text-xs font-bold text-zinc-200 group-hover:text-white">
              <span>Ver mis aprobaciones</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        </div>

        {/* Feedback Banner when a quick check completes */}
        {lastExecutionResult && (
          <div className="p-4 rounded-2xl bg-zinc-900 border border-emerald-500/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs animate-fade-in">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
              <div>
                <div className="font-bold text-white">
                  ¡Revisión completada con éxito!
                </div>
                <div className="text-zinc-300 text-xs">
                  {lastExecutionResult.summary || 'Todas las pruebas de seguridad e inventario pasaron correctamente.'}
                </div>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setLastExecutionResult(null)}
              className="px-3 py-1.5 rounded-xl bg-black text-zinc-300 hover:text-white text-xs font-bold cursor-pointer self-start sm:self-center"
            >
              Entendido
            </button>
          </div>
        )}
      </section>

      {/* =====================================================================
          2. RESUMEN SENCILLO DEL ESTADO DE TU SISTEMA (3 INDICADORES CLAROS)
         ===================================================================== */}
      <section className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div
          onClick={() => onNavigateSection('jira')}
          className="p-4 rounded-2xl bg-zinc-950 border border-zinc-800/90 hover:border-zinc-700 transition cursor-pointer flex items-center justify-between"
        >
          <div className="space-y-1">
            <span className="text-xs text-zinc-400 block">Avance de Tareas</span>
            <span className="text-xl font-extrabold text-white block">
              {completedCount} de {tasks.length} listas
            </span>
            <span className="text-[11px] text-zinc-400 block">
              {progressPercent}% del plan completado
            </span>
          </div>
          <div className="w-10 h-10 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-white">
            <CheckSquare className="w-5 h-5" />
          </div>
        </div>

        <div
          onClick={() => onNavigateSection('agents')}
          className="p-4 rounded-2xl bg-zinc-950 border border-zinc-800/90 hover:border-zinc-700 transition cursor-pointer flex items-center justify-between"
        >
          <div className="space-y-1">
            <span className="text-xs text-zinc-400 block">Consumo de Recursos IA</span>
            <span className="text-xl font-extrabold text-white block">
              {activeAgentsCount === 0 ? 'En Reposo (0%)' : `${activeAgentsCount} Trabajando`}
            </span>
            <span className="text-[11px] text-emerald-400 block">
              {activeAgentsCount === 0
                ? '✓ No gasta saldo ni memoria'
                : 'Ejecutando tu solicitud'}
            </span>
          </div>
          <div className="w-10 h-10 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-white">
            <Bot className="w-5 h-5" />
          </div>
        </div>

        <div
          onClick={() => onNavigateSection('projects')}
          className="p-4 rounded-2xl bg-zinc-950 border border-zinc-800/90 hover:border-zinc-700 transition cursor-pointer flex items-center justify-between"
        >
          <div className="space-y-1">
            <span className="text-xs text-zinc-400 block">Protección de tu Negocio</span>
            <span className="text-xl font-extrabold text-white block">100% Activa</span>
            <span className="text-[11px] text-zinc-400 block">
              Inventario y pagos blindados
            </span>
          </div>
          <div className="w-10 h-10 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-emerald-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
        </div>
      </section>

      {/* =====================================================================
          3. LISTA DE TAREAS DEL PROYECTO (FÁCIL DE LEER Y LANZAR CON 1 CLIC)
         ===================================================================== */}
      <section className="p-5 sm:p-6 rounded-3xl bg-zinc-950 border border-zinc-800/90 space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-850 pb-4">
          <div>
            <h2 className="text-base font-bold text-white">
              Lista de Tareas de tu Proyecto
            </h2>
            <p className="text-xs text-zinc-400 mt-0.5">
              Aquí ves qué tareas están terminadas y cuáles puedes iniciar con un clic.
            </p>
          </div>

          <button
            type="button"
            onClick={onOpenSprintModal}
            className="px-4 py-2 rounded-xl bg-white hover:bg-zinc-200 text-black font-bold text-xs flex items-center gap-2 transition cursor-pointer self-start sm:self-center shadow-sm"
          >
            <Sparkles className="w-3.5 h-3.5 text-black" />
            <span>+ Agregar o Iniciar Tarea</span>
          </button>
        </div>

        {tasks.length === 0 ? (
          <div className="p-8 text-center rounded-2xl bg-black border border-zinc-850 space-y-3">
            <Folder className="w-6 h-6 text-zinc-500 mx-auto" />
            <div className="text-xs font-bold text-white">
              Aún no hay tareas registradas en esta vista
            </div>
            <button
              type="button"
              onClick={onOpenSprintModal}
              className="px-4 py-2 rounded-xl bg-white text-black font-bold text-xs hover:bg-zinc-200 transition cursor-pointer"
            >
              Crear mi primera tarea
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {tasks.map((task) => {
              const isDone = task.progress >= 100 || task.status === 'Completada'
              return (
                <div
                  key={task.id}
                  onClick={onOpenSprintModal}
                  className="p-4 rounded-2xl bg-black border border-zinc-800/90 hover:border-zinc-600 transition cursor-pointer flex flex-col justify-between space-y-3 group"
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-mono text-[10px] px-2 py-0.5 rounded-md bg-zinc-900 border border-zinc-800 text-zinc-300 font-bold">
                        {task.key}
                      </span>
                      <span
                        className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
                          isDone
                            ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30'
                            : 'bg-zinc-900 text-zinc-300 border border-zinc-800'
                        }`}
                      >
                        {isDone ? '✓ Completada' : task.status}
                      </span>
                    </div>
                    <h3 className="text-xs sm:text-sm font-bold text-white group-hover:underline">
                      {task.title}
                    </h3>
                  </div>

                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-[11px] text-zinc-400">
                      <span>Avance: {task.progress}%</span>
                      <span className="text-zinc-300 font-medium group-hover:text-white flex items-center gap-1">
                        <Play className="w-3 h-3" /> Trabajar en esto
                      </span>
                    </div>
                    <div className="h-1.5 w-full bg-zinc-900 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-white rounded-full transition-all"
                        style={{ width: `${task.progress}%` }}
                      />
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </section>

      {/* =====================================================================
          4. HERRAMIENTAS Y DETALLES TÉCNICOS (OCULTOS POR DEFECTO)
         ===================================================================== */}
      <div className="pt-2">
        <button
          type="button"
          onClick={() => setShowTechnicalLogs(!showTechnicalLogs)}
          className="w-full p-3.5 rounded-2xl bg-zinc-950 hover:bg-zinc-900 border border-zinc-850 text-xs text-zinc-400 hover:text-white flex items-center justify-between transition cursor-pointer"
        >
          <span className="flex items-center gap-2 font-medium">
            <Terminal className="w-4 h-4 text-zinc-500" />
            <span>
              {showTechnicalLogs
                ? 'Ocultar herramientas conectadas y consola técnica'
                : 'Mostrar detalles técnicos para ingenieros (Conexiones y Consola en Vivo)'}
            </span>
          </span>
          {showTechnicalLogs ? (
            <ChevronUp className="w-4 h-4" />
          ) : (
            <ChevronDown className="w-4 h-4" />
          )}
        </button>

        {showTechnicalLogs && (
          <div className="space-y-4 mt-4 animate-fade-in">
            <ConnectedTechnologiesMatrix
              connections={connections}
              onRefresh={onRefreshConnections}
              onNavigateSection={onNavigateSection}
            />
            <LogTerminal
              initialEvents={events}
              onOpenGate={() => onNavigateSection('executions')}
            />
          </div>
        )}
      </div>
    </div>
  )
}
