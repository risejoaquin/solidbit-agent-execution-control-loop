import React, { useState, useEffect } from 'react'
import {
  CheckCircle2,
  ShieldAlert,
  Sparkles,
  ChevronDown,
  ChevronUp,
  FolderGit2,
  Loader2,
  Terminal,
  AlertTriangle,
  Key,
  FileCode,
  Play,
  ArrowRight,
  RotateCcw,
  Activity,
  Cpu,
  GitBranch,
  ShieldCheck,
  ExternalLink,
} from 'lucide-react'
import type {
  TaskItem,
  AgentItem,
  CommitItem,
  Project,
  ActivityEvent,
} from '../types/orchestrator'
import type { TechnologyItem } from './ConnectedTechnologiesMatrix'
import type { DomainStateMeta, OperationalDomainState } from '../types/domainState'
import { StatusBadge } from './ui/status-badge'
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from './ui/tooltip'
import { StructuredPayloadViewer } from './StructuredPayloadViewer'

interface CenterDashboardProps {
  domainState: DomainStateMeta
  tasks: TaskItem[]
  agents: AgentItem[]
  connections?: TechnologyItem[]
  onRefreshConnections?: () => void
  commits: CommitItem[]
  projects: Project[]
  events?: ActivityEvent[]
  onOpenSprintModal: () => void
  onNavigateSection: (section: string) => void
  pendingGatesCount?: number
  onConflictStateChange?: (hasConflict: boolean, reason?: string | null) => void
  onExecutingStateChange?: (isExecuting: boolean) => void
  onGateResolved?: () => void
}

export const CenterDashboard: React.FC<CenterDashboardProps> = ({
  domainState,
  tasks,
  agents,
  onRefreshConnections,
  commits,
  projects,
  onOpenSprintModal,
  onNavigateSection,
  onConflictStateChange,
  onExecutingStateChange,
  onGateResolved,
}) => {
  // Layer 2 Progressive Disclosure Drawer State
  const [showTelemetryDrawer, setShowTelemetryDrawer] = useState<boolean>(false)

  // Live Health / Verification State
  const [runningHealthCheck, setRunningHealthCheck] = useState<boolean>(false)
  const [healthResult, setHealthResult] = useState<any | null>(null)

  // Inline Approval Resolution State (when domainState.state === 'AWAITING_APPROVAL')
  const [pendingGate, setPendingGate] = useState<any | null>(null)
  const [gateDossier, setGateDossier] = useState<any | null>(null)
  const [justification, setJustification] = useState<string>(
    'Autorizado tras revisar que las verificaciones de calidad finalizaron correctamente.'
  )
  const [decidingGate, setDecidingGate] = useState<boolean>(false)
  const [showInlineDiff, setShowInlineDiff] = useState<boolean>(false)
  const [resolutionFeedback, setResolutionFeedback] = useState<{
    type: 'success' | 'error'
    message: string
  } | null>(null)

  // Interactive FSM Simulator / Override for testing all 6 states directly in the statechart
  const [manualSimulatedConflict, setManualSimulatedConflict] = useState<string | null>(null)

  // Load pending gate details when in AWAITING_APPROVAL state
  const loadPendingGateDetails = async () => {
    try {
      const res = await fetch('/api/gates/pending')
      const data = await res.json()
      const list = data?.gates || data?.pending_gates || []
      if (list.length > 0) {
        const firstGate = list[0]
        setPendingGate(firstGate)
        const dRes = await fetch(
          `/api/gates/dossier?request_id=${encodeURIComponent(firstGate.request_id)}`
        )
        const dData = await dRes.json()
        if (dData && dData.has_gate) {
          setGateDossier(dData)
        }
      } else {
        setPendingGate(null)
        setGateDossier(null)
      }
    } catch (e) {
      console.warn('Error loading inline gate details:', e)
    }
  }

  useEffect(() => {
    if (domainState.state === 'AWAITING_APPROVAL') {
      loadPendingGateDetails()
    } else {
      setPendingGate(null)
      setGateDossier(null)
    }
  }, [domainState.state])

  // Action: Run Real Health Verification
  const handleRunHealthVerification = async () => {
    setRunningHealthCheck(true)
    onExecutingStateChange?.(true)
    setResolutionFeedback(null)
    try {
      const res = await fetch('/api/actions/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action_type: 'security_audit', params: {} }),
      })
      const data = await res.json()
      setHealthResult(data)
      if (!data.success && data.exit_code !== 0) {
        onConflictStateChange?.(
          true,
          data.summary || 'Se detectó una diferencia durante la verificación preventiva.'
        )
      } else {
        onConflictStateChange?.(false, null)
        setManualSimulatedConflict(null)
      }
      onRefreshConnections?.()
    } catch (err: any) {
      onConflictStateChange?.(
        true,
        `No se pudo completar la verificación local: ${err.message || 'Error de comunicación'}`
      )
    } finally {
      setRunningHealthCheck(false)
      onExecutingStateChange?.(false)
    }
  }

  // Action: Resolve Conflict State (Nielsen #9 Direct Interactive Resolution)
  const handleResolveConflict = async () => {
    setManualSimulatedConflict(null)
    onConflictStateChange?.(false, null)
    await handleRunHealthVerification()
  }

  // Action: Inline Gate Decision (Poka-Yoke + CQRS Transition)
  const isJustificationValid = justification.trim().length >= 10

  const handleInlineGateDecision = async (decision: 'APPROVED' | 'REJECTED') => {
    if (!pendingGate || !isJustificationValid) return
    setDecidingGate(true)
    setResolutionFeedback(null)
    try {
      const operator = localStorage.getItem('sacl_operator_name') || 'Responsable de Producto'
      const res = await fetch('/api/gates/decide', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          request_id: pendingGate.request_id,
          decision,
          approver_id: operator,
          justification: justification.trim(),
          channel: 'INLINE_STATECHART_RESOLUTION',
        }),
      })
      const data = await res.json()
      if (res.ok && data.success) {
        setResolutionFeedback({
          type: 'success',
          message:
            decision === 'APPROVED'
              ? `Entrega ${pendingGate.request_id} autorizada e integrada con éxito.`
              : `Entrega ${pendingGate.request_id} rechazada. El flujo volvió a estado seguro.`,
        })
        onGateResolved?.()
        onRefreshConnections?.()
      } else {
        setResolutionFeedback({
          type: 'error',
          message: data.error || 'No se pudo procesar tu decisión.',
        })
      }
    } catch (e: any) {
      setResolutionFeedback({
        type: 'error',
        message: 'Error al registrar la autorización: ' + e.message,
      })
    } finally {
      setDecidingGate(false)
    }
  }

  const activeProject = projects.find((p) => p.is_active) || projects[0]
  const completedCount = tasks.filter(
    (t) => t.status === 'Completada' || t.progress === 100
  ).length
  const totalCount = tasks.length || 1
  const completionPct = Math.round((completedCount / totalCount) * 100)
  const isSprintFullyComplete = completedCount === totalCount && totalCount > 0

  // Title sanitizer to prevent orphan chars like ')' or empty titles
  const sanitizeTaskTitle = (title?: string, id?: string | number, key?: string): string => {
    if (!title) return `[Requerimiento SDLC #${key || id || '402'}]`
    const clean = title.trim()
    if (['(', ')', '[', ']', '{', '}', '-', '', 'null', 'undefined'].includes(clean) || clean.length < 3) {
      return `[Requerimiento SDLC #${key || id || '402'}]`
    }
    return clean
  }

  const stateSteps: Array<{ id: OperationalDomainState; label: string }> = [
    { id: 'UNINITIALIZED', label: '1. Vincular' },
    { id: 'PLANNING', label: '2. Planificar' },
    { id: 'EXECUTING', label: '3. Ejecutar' },
    { id: 'HALTED_BY_CONFLICT', label: 'Incidencia' },
    { id: 'AWAITING_APPROVAL', label: '4. Autorizar' },
    { id: 'COMPLETED', label: '5. Listo' },
  ]

  return (
    <TooltipProvider>
      <div className="space-y-6 max-w-7xl mx-auto pb-12 text-left animate-fade-in">
        {/* Bento Grid Layout: 65% Primary Column / 35% Real-Time Telemetry Column */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* =====================================================================
              COLUMNA IZQUIERDA (65% / 8 COLS): STATECHART Y SPRINT ACTIVO
             ===================================================================== */}
          <div className="lg:col-span-8 space-y-6">
            <section className="p-6 rounded-3xl bg-[#0C0C0E] border border-white/5 space-y-5 shadow-2xl">
              {/* Stepper y sincronización fiel de la FSM */}
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-800/80 pb-4">
                <div className="flex items-center gap-2 overflow-x-auto pb-1">
                  {stateSteps.map((st) => {
                    const isCurrent = domainState.state === st.id
                    if (st.id === 'HALTED_BY_CONFLICT' && !isCurrent) return null
                    return (
                      <span
                        key={st.id}
                        className={`px-3 py-1 rounded-full text-[11px] font-mono transition ${
                          isCurrent
                            ? st.id === 'HALTED_BY_CONFLICT'
                              ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40 font-bold'
                              : st.id === 'AWAITING_APPROVAL'
                              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold'
                              : 'bg-white text-black font-extrabold shadow-sm'
                            : 'bg-zinc-900/60 text-zinc-500'
                        }`}
                      >
                        {st.label}
                      </span>
                    )
                  })}
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-mono text-zinc-400">
                    FSM:
                  </span>
                  <StatusBadge
                    status={
                      domainState.state === 'COMPLETED'
                        ? isSprintFullyComplete
                          ? 'SUCCESS'
                          : 'RUNNING'
                        : domainState.state === 'AWAITING_APPROVAL'
                        ? 'WAITING'
                        : domainState.state === 'HALTED_BY_CONFLICT'
                        ? 'ERROR'
                        : domainState.state === 'EXECUTING'
                        ? 'RUNNING'
                        : 'IDLE'
                    }
                    label={
                      domainState.state === 'COMPLETED' && !isSprintFullyComplete
                        ? 'Sprint en Curso'
                        : domainState.badgeLabel
                    }
                    pulsing={domainState.state === 'EXECUTING' || (domainState.state === 'COMPLETED' && !isSprintFullyComplete)}
                  />
                </div>
              </div>

              {/* Resolution Feedback Banner */}
              {resolutionFeedback && (
                <div
                  className={`p-4 rounded-2xl border text-xs flex items-center justify-between gap-3 ${
                    resolutionFeedback.type === 'success'
                      ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-200'
                      : 'bg-rose-950/30 border-rose-500/40 text-rose-200'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>{resolutionFeedback.message}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setResolutionFeedback(null)}
                    className="text-xs underline cursor-pointer text-zinc-400 hover:text-white"
                  >
                    Cerrar
                  </button>
                </div>
              )}

              {/* =================================================================
                  BRANCH A: STATE = UNINITIALIZED (No Project Imported)
                 ================================================================= */}
              {domainState.state === 'UNINITIALIZED' && (
                <div className="p-6 rounded-2xl bg-zinc-900/40 border border-zinc-800 space-y-4">
                  <div className="flex items-start gap-3.5">
                    <div className="w-11 h-11 rounded-2xl bg-zinc-900 border border-zinc-750 flex items-center justify-center text-white shrink-0">
                      <FolderGit2 className="w-5 h-5" />
                    </div>
                    <div className="space-y-1">
                      <h1 className="text-lg font-bold text-white">{domainState.title}</h1>
                      <p className="text-xs sm:text-sm text-zinc-300 leading-relaxed">
                        {domainState.subtitle}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-end pt-2">
                    <button
                      type="button"
                      onClick={() => onNavigateSection('projects')}
                      className="px-5 py-2.5 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-extrabold flex items-center gap-2 transition cursor-pointer shadow-sm"
                    >
                      <FolderGit2 className="w-4 h-4 text-black" />
                      <span>{domainState.primaryActionLabel}</span>
                      <ArrowRight className="w-4 h-4 text-black" />
                    </button>
                  </div>
                </div>
              )}

              {/* =================================================================
                  BRANCH B: STATE = HALTED_BY_CONFLICT (Inline Error Recovery)
                 ================================================================= */}
              {domainState.state === 'HALTED_BY_CONFLICT' && (
                <div className="p-6 rounded-2xl bg-rose-950/20 border border-rose-500/40 space-y-5">
                  <div className="flex items-start gap-3.5">
                    <div className="w-11 h-11 rounded-2xl bg-rose-500/15 border border-rose-500/30 flex items-center justify-center text-rose-400 shrink-0">
                      <AlertTriangle className="w-5 h-5" />
                    </div>
                    <div className="space-y-1">
                      <span className="text-[10px] font-mono uppercase tracking-wider text-rose-300 font-bold">
                        Protección Preventiva Activada
                      </span>
                      <h1 className="text-lg font-bold text-white">{domainState.title}</h1>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                    <div className="p-3.5 rounded-xl bg-black/80 border border-zinc-800 space-y-1">
                      <span className="text-[10px] font-mono uppercase text-zinc-400 block">
                        (a) ¿Qué ocurrió? (Causa)
                      </span>
                      <p className="text-zinc-200 leading-relaxed">
                        {manualSimulatedConflict ||
                          domainState.subtitle ||
                          'Se detectaron cambios sin confirmar o una prueba que requiere revisión antes de continuar.'}
                      </p>
                    </div>

                    <div className="p-3.5 rounded-xl bg-black/80 border border-zinc-800 space-y-1">
                      <span className="text-[10px] font-mono uppercase text-zinc-400 block">
                        (b) Impacto en tu proyecto
                      </span>
                      <p className="text-zinc-200 leading-relaxed">
                        Tus archivos principales están intactos. El lanzamiento de nuevos sprints se pausó preventivamente para evitar sobrescribir tu trabajo.
                      </p>
                    </div>

                    <div className="p-3.5 rounded-xl bg-black/80 border border-zinc-800 space-y-1">
                      <span className="text-[10px] font-mono uppercase text-zinc-400 block">
                        (c) Solución directa
                      </span>
                      <p className="text-zinc-200 leading-relaxed">
                        Ejecuta la restauración automática del entorno seguro para limpiar el bloqueo y reanudar el trabajo.
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-rose-500/20">
                    <button
                      type="button"
                      onClick={() => onNavigateSection('connections')}
                      className="px-3.5 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-300 text-xs font-medium transition cursor-pointer"
                    >
                      Revisar Conexiones del Sistema
                    </button>

                    <button
                      type="button"
                      onClick={handleResolveConflict}
                      disabled={runningHealthCheck}
                      className="px-5 py-2.5 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-extrabold flex items-center gap-2 transition cursor-pointer shadow-sm disabled:opacity-50"
                    >
                      {runningHealthCheck ? (
                        <Loader2 className="w-4 h-4 animate-spin text-black" />
                      ) : (
                        <RotateCcw className="w-4 h-4 text-black" />
                      )}
                      <span>{domainState.primaryActionLabel}</span>
                    </button>
                  </div>
                </div>
              )}

              {/* =================================================================
                  BRANCH C: STATE = AWAITING_APPROVAL (Foreground Inline Resolution)
                 ================================================================= */}
              {domainState.state === 'AWAITING_APPROVAL' && (
                <div className="p-6 rounded-2xl bg-zinc-900/50 border border-amber-500/40 space-y-5">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-800 pb-4">
                    <div className="flex items-start gap-3.5">
                      <div className="w-11 h-11 rounded-2xl bg-amber-500/15 border border-amber-500/35 flex items-center justify-center text-amber-400 shrink-0">
                        <ShieldAlert className="w-5 h-5" />
                      </div>
                      <div>
                        <span className="text-[10px] font-mono uppercase tracking-wider text-amber-300 font-bold">
                          Paso Requerido antes de Continuar
                        </span>
                        <h1 className="text-lg font-bold text-white">{domainState.title}</h1>
                        <p className="text-xs text-zinc-300 mt-0.5">{domainState.subtitle}</p>
                      </div>
                    </div>
                  </div>

                  {gateDossier?.decision_checklist && (
                    <div className="space-y-2">
                      <span className="text-xs font-bold text-zinc-200 block">
                        1. Verificaciones de Calidad Superadas:
                      </span>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                        {gateDossier.decision_checklist.slice(0, 3).map((chk: any) => (
                          <div
                            key={chk.id}
                            className="p-3.5 rounded-xl bg-black border border-zinc-800 space-y-1"
                          >
                            <div className="flex items-center justify-between">
                              <span className="text-xs font-bold text-white">{chk.name}</span>
                              <span className="inline-flex items-center gap-1 text-[10px] font-mono text-emerald-400 font-bold">
                                <CheckCircle2 className="w-3.5 h-3.5" />
                                LISTO
                              </span>
                            </div>
                            <p className="text-[11px] text-zinc-400">{chk.details}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="pt-1">
                    <button
                      type="button"
                      onClick={() => setShowInlineDiff(!showInlineDiff)}
                      className="flex items-center gap-2 text-xs text-zinc-400 hover:text-white transition cursor-pointer"
                    >
                      <FileCode className="w-4 h-4" />
                      <span>
                        {showInlineDiff
                          ? 'Ocultar inspección técnica de archivos modificados'
                          : 'Inspección Técnica: Ver archivos y líneas de código propuestas'}
                      </span>
                      {showInlineDiff ? (
                        <ChevronUp className="w-4 h-4" />
                      ) : (
                        <ChevronDown className="w-4 h-4" />
                      )}
                    </button>

                    {showInlineDiff && gateDossier?.diff_lines && (
                      <div className="mt-2.5 p-3.5 rounded-xl bg-black border border-zinc-800 font-mono text-xs max-h-40 overflow-y-auto space-y-0.5">
                        {gateDossier.diff_lines.map((line: any, idx: number) => {
                          const isAdd = line.type === 'add' || line.text?.startsWith('+')
                          const isDel = line.type === 'del' || line.text?.startsWith('-')
                          return (
                            <div
                              key={idx}
                              className={`px-2 py-0.5 rounded text-[11px] ${
                                isAdd
                                  ? 'bg-emerald-950/40 text-emerald-300'
                                  : isDel
                                  ? 'bg-rose-950/40 text-rose-300'
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

                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-bold text-zinc-200">
                        2. Nota de autorización para el registro:
                      </label>
                      <span
                        className={`text-[11px] flex items-center gap-1 ${
                          isJustificationValid ? 'text-emerald-400' : 'text-amber-400'
                        }`}
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        {isJustificationValid
                          ? 'Nota lista para autorizar'
                          : 'Escribe al menos 10 caracteres'}
                      </span>
                    </div>
                    <input
                      type="text"
                      value={justification}
                      onChange={(e) => setJustification(e.target.value)}
                      className="w-full bg-black border border-zinc-750 rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-white"
                    />
                  </div>

                  <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-zinc-800">
                    <button
                      type="button"
                      onClick={() => handleInlineGateDecision('REJECTED')}
                      disabled={decidingGate || !isJustificationValid}
                      className="px-4 py-2.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-750 text-zinc-300 hover:text-white text-xs font-semibold transition cursor-pointer disabled:opacity-40"
                    >
                      Rechazar Entrega
                    </button>

                    <button
                      type="button"
                      onClick={() => handleInlineGateDecision('APPROVED')}
                      disabled={decidingGate || !isJustificationValid}
                      className="px-6 py-2.5 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-extrabold flex items-center gap-2 transition cursor-pointer shadow-sm disabled:opacity-40"
                    >
                      {decidingGate ? (
                        <Loader2 className="w-4 h-4 animate-spin text-black" />
                      ) : (
                        <Key className="w-4 h-4 text-black" />
                      )}
                      <span>{domainState.primaryActionLabel}</span>
                    </button>
                  </div>
                </div>
              )}

              {/* =================================================================
                  BRANCH D: STATE = EXECUTING (Live Execution Progress)
                 ================================================================= */}
              {domainState.state === 'EXECUTING' && (
                <div className="p-6 rounded-2xl bg-zinc-900/50 border border-zinc-750 space-y-4">
                  <div className="flex items-center gap-3.5">
                    <div className="w-11 h-11 rounded-2xl bg-zinc-900 border border-zinc-700 flex items-center justify-center text-white shrink-0">
                      <Loader2 className="w-5 h-5 animate-spin" />
                    </div>
                    <div>
                      <h1 className="text-lg font-bold text-white">{domainState.title}</h1>
                      <p className="text-xs text-zinc-400 mt-0.5">{domainState.subtitle}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* =================================================================
                  BRANCH E: STATE = COMPLETED / PLANNING (Unified Sprint Flow)
                 ================================================================= */}
              {(domainState.state === 'COMPLETED' || domainState.state === 'PLANNING') && (
                <div className="space-y-5">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-5 p-6 rounded-2xl bg-zinc-900/35 border border-white/5">
                    <div className="space-y-2 max-w-2xl">
                      <div className="flex items-center gap-2">
                        {isSprintFullyComplete ? (
                          <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-400">
                            <CheckCircle2 className="w-4 h-4" />
                            <span>Entrega Integrada al 100%</span>
                          </div>
                        ) : (
                          <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-sky-400">
                            <span className="relative flex h-2.5 w-2.5">
                              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sky-400 opacity-75"></span>
                              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-sky-500"></span>
                            </span>
                            <span>Última entrega autorizada &bull; Sprint activo</span>
                          </div>
                        )}
                      </div>

                      <h1 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
                        {isSprintFullyComplete
                          ? 'Todas las tareas del Sprint han sido completadas'
                          : `Sprint en Proceso (${completedCount} de ${tasks.length} completados)`}
                      </h1>
                      <p className="text-xs sm:text-sm text-zinc-300 leading-relaxed">
                        {isSprintFullyComplete
                          ? 'El repositorio se encuentra limpio y actualizado con todos los requerimientos aprobados.'
                          : 'Se están resolviendo los requerimientos activos asignados al escuadrón de agentes.'}
                      </p>
                    </div>

                    <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 shrink-0">
                      <button
                        type="button"
                        onClick={handleRunHealthVerification}
                        disabled={runningHealthCheck}
                        className="px-4 py-3 rounded-2xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-200 text-xs font-semibold flex items-center justify-center gap-2 transition cursor-pointer disabled:opacity-50"
                      >
                        {runningHealthCheck ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Play className="w-3.5 h-3.5 text-emerald-400" />
                        )}
                        <span>Verificar Repositorio</span>
                      </button>

                      <button
                        type="button"
                        id="btn-canonical-plan-sprint"
                        onClick={onOpenSprintModal}
                        className="px-6 py-3 rounded-2xl bg-white hover:bg-zinc-200 text-black text-xs sm:text-sm font-extrabold flex items-center justify-center gap-2 transition cursor-pointer shadow-lg"
                      >
                        <Sparkles className="w-4 h-4 text-black fill-black" />
                        <span>{domainState.primaryActionLabel}</span>
                        <ArrowRight className="w-4 h-4 text-black" />
                      </button>
                    </div>
                  </div>

                  {/* Empirical Verification Result (Structured CQRS & Postcondition Inspector) */}
                  {healthResult && (
                    <div className="pt-1">
                      <StructuredPayloadViewer
                        execution={healthResult}
                        onRetryTask={handleRunHealthVerification}
                      />
                    </div>
                  )}

                  {/* Requerimientos Activos (Sanitizados & Semánticamente Claros) */}
                  <div className="p-5 sm:p-6 rounded-2xl bg-zinc-900/25 border border-white/5 space-y-4">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div>
                        <h2 className="text-sm font-bold text-white">
                          Requerimientos del Sprint ({completedCount} de {tasks.length} completados)
                        </h2>
                        <p className="text-xs text-zinc-400 mt-0.5">
                          Proyecto: <strong className="text-zinc-200">{activeProject?.name || 'Tienda Online'}</strong>
                        </p>
                      </div>

                      <button
                        type="button"
                        onClick={() => onNavigateSection('jira')}
                        className="text-xs text-zinc-300 hover:text-white flex items-center gap-1 font-medium cursor-pointer self-start sm:self-auto"
                      >
                        <span>Ver todos en Backlog Jira</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>

                    {/* Progress Bar */}
                    <div className="h-2 w-full bg-zinc-900 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-emerald-400 rounded-full transition-all duration-500"
                        style={{ width: `${Math.max(completionPct, 8)}%` }}
                      />
                    </div>

                    {/* Task Grid with strict iconography semantics */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                      {tasks.slice(0, 6).map((task) => {
                        const isDone = task.status === 'Completada' || task.progress === 100
                        const titleClean = sanitizeTaskTitle(task.title, task.id, task.key)

                        return (
                          <div
                            key={task.id}
                            onClick={() => onNavigateSection('jira')}
                            className="p-3.5 rounded-2xl bg-[#121215] hover:bg-zinc-900/90 border border-white/5 transition cursor-pointer flex items-center justify-between gap-3 group"
                          >
                            <div className="flex items-center gap-3 min-w-0">
                              {isDone ? (
                                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                              ) : (
                                <span className="relative flex h-3 w-3 shrink-0">
                                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                                  <span className="relative inline-flex rounded-full h-3 w-3 bg-amber-500"></span>
                                </span>
                              )}
                              <span className="text-xs font-semibold text-white truncate group-hover:text-zinc-200" title={titleClean}>
                                {titleClean}
                              </span>
                            </div>

                            <StatusBadge
                              status={isDone ? 'SUCCESS' : 'RUNNING'}
                              label={isDone ? 'Completada' : 'En curso'}
                              pulsing={!isDone}
                            />
                          </div>
                        )
                      })}
                    </div>
                  </div>
                </div>
              )}
            </section>
          </div>

          {/* =====================================================================
              COLUMNA DERECHA (35% / 4 COLS): TELEMETRÍA EN TIEMPO REAL & BENTO METRICS
             ===================================================================== */}
          <div className="lg:col-span-4 space-y-4">
            {/* Tarjeta 1: Salud del Daemon y Conectividad */}
            <div className="p-5 rounded-3xl bg-[#0C0C0E] border border-white/5 space-y-4 shadow-xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs font-bold text-white tracking-tight uppercase font-mono">
                    Telemetría SACL
                  </span>
                </div>
                <StatusBadge status="SUCCESS" label="Daemon 8765" pulsing />
              </div>

              <div className="space-y-2.5 text-xs font-mono">
                <div className="p-3 rounded-2xl bg-[#121215] border border-white/5 flex items-center justify-between">
                  <span className="text-zinc-400">Procesos SO</span>
                  <span className="text-white font-bold">
                    {agents.length === 0 ? '0 en reposo (0 tokens)' : `${agents.length} activos`}
                  </span>
                </div>

                <div className="p-3 rounded-2xl bg-[#121215] border border-white/5 flex items-center justify-between">
                  <span className="text-zinc-400">Rama Git</span>
                  <span className="text-zinc-200 font-bold flex items-center gap-1.5">
                    <GitBranch className="w-3.5 h-3.5 text-sky-400" />
                    {(activeProject as any)?.branch || 'main'}
                  </span>
                </div>

                <div className="p-3 rounded-2xl bg-[#121215] border border-white/5 flex items-center justify-between">
                  <span className="text-zinc-400">Worktree</span>
                  <span className="text-emerald-400 font-semibold flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    Aislado &bull; Limpio
                  </span>
                </div>
              </div>
            </div>

            {/* Tarjeta 2: Accesos Directos al Último Commit y Estado Git */}
            <div className="p-5 rounded-3xl bg-[#0C0C0E] border border-white/5 space-y-3 shadow-xl">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white tracking-tight uppercase font-mono">
                  Últimos Commits
                </span>
                <button
                  type="button"
                  onClick={() => onNavigateSection('github')}
                  className="text-[10px] text-zinc-400 hover:text-white flex items-center gap-1 font-mono"
                >
                  Ver todo
                  <ExternalLink className="w-3 h-3" />
                </button>
              </div>

              <div className="space-y-2 font-mono text-xs">
                {commits.slice(0, 3).map((c, i) => (
                  <div
                    key={c.sha || i}
                    className="p-2.5 rounded-xl bg-[#121215] border border-white/5 space-y-1"
                  >
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="text-zinc-300 truncate max-w-[180px]">{c.message}</span>
                      <code className="text-[10px] text-sky-400 bg-sky-950/30 px-1.5 py-0.5 rounded border border-sky-500/20">
                        {c.sha?.substring(0, 7) || 'HEAD'}
                      </code>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Tarjeta 3: Invariante FSM Simulator */}
            <div className="p-5 rounded-3xl bg-[#0C0C0E] border border-white/5 space-y-3 shadow-xl">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-zinc-200 font-mono uppercase">
                  Simulador de Invariantes FSM
                </span>
                <Cpu className="w-3.5 h-3.5 text-zinc-500" />
              </div>
              <p className="text-[11px] text-zinc-400 leading-relaxed">
                Verifica de manera interactiva la contención preventiva y la recuperación de errores sin modificar código.
              </p>
              <button
                type="button"
                onClick={() => {
                  const nextConflict = domainState.state !== 'HALTED_BY_CONFLICT'
                  setManualSimulatedConflict(
                    nextConflict
                      ? 'Diferencia simulada en rama de trabajo para verificar recuperación interactiva.'
                      : null
                  )
                  onConflictStateChange?.(
                    nextConflict,
                    nextConflict
                      ? 'Diferencia simulada en rama de trabajo para verificar recuperación interactiva.'
                      : null
                  )
                }}
                className="w-full py-2.5 px-3 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-750 text-zinc-200 text-xs font-mono font-semibold transition cursor-pointer"
              >
                {domainState.state === 'HALTED_BY_CONFLICT'
                  ? 'Desactivar Simulación'
                  : 'Simular Incidencia Preventiva'}
              </button>
            </div>
          </div>
        </div>

        {/* =====================================================================
            CAPA 2: INSPECCIÓN TÉCNICA Y ACCESO RÁPIDO
           ===================================================================== */}
        <section className="rounded-2xl bg-[#0C0C0E] border border-white/5 overflow-hidden">
          <button
            type="button"
            onClick={() => setShowTelemetryDrawer(!showTelemetryDrawer)}
            className="w-full p-4 sm:p-5 flex items-center justify-between hover:bg-zinc-900/40 transition cursor-pointer text-left"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-400">
                <Terminal className="w-4 h-4" />
              </div>
              <div>
                <span className="text-xs font-bold text-zinc-200 block">
                  Capa 2 &bull; Historial de Transacciones SQLite WAL y Diagnósticos
                </span>
                <span className="text-[11px] text-zinc-500">
                  Registro de auditoría criptográfica, compuertas HITL y registros de sistema
                </span>
              </div>
            </div>
            <div className="flex items-center gap-1.5 text-xs font-mono text-zinc-400">
              <span>{showTelemetryDrawer ? 'Ocultar' : 'Desplegar'}</span>
              {showTelemetryDrawer ? (
                <ChevronUp className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </div>
          </button>

          {showTelemetryDrawer && (
            <div className="p-5 pt-0 border-t border-zinc-800/80 space-y-4 mt-4 text-xs animate-fade-in">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 font-mono">
                <div className="p-3.5 rounded-xl bg-[#121215] border border-white/5">
                  <span className="text-[10px] text-zinc-500 uppercase block">
                    Protocolo de Durabilidad
                  </span>
                  <span className="text-sm font-bold text-emerald-400 mt-0.5 block">
                    SQLite WAL &bull; Cero Pérdidas
                  </span>
                </div>

                <div className="p-3.5 rounded-xl bg-[#121215] border border-white/5">
                  <span className="text-[10px] text-zinc-500 uppercase block">
                    Modo de Ejecución
                  </span>
                  <span className="text-sm font-bold text-zinc-200 mt-0.5 block">
                    Deterministic CQRS &bull; Zero-Token Idle
                  </span>
                </div>

                <div className="p-3.5 rounded-xl bg-[#121215] border border-white/5">
                  <span className="text-[10px] text-zinc-500 uppercase block">
                    Compuertas Humanas
                  </span>
                  <span className="text-sm font-bold text-amber-400 mt-0.5 block">
                    Gates 0 a 5 &bull; Firmas HMAC Activas
                  </span>
                </div>
              </div>
            </div>
          )}
        </section>
      </div>
    </TooltipProvider>
  )
}
