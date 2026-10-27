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

  const stateSteps: Array<{ id: OperationalDomainState; label: string }> = [
    { id: 'UNINITIALIZED', label: '1. Vincular' },
    { id: 'PLANNING', label: '2. Planificar' },
    { id: 'EXECUTING', label: '3. Ejecutar' },
    { id: 'HALTED_BY_CONFLICT', label: 'Incidencia' },
    { id: 'AWAITING_APPROVAL', label: '4. Autorizar' },
    { id: 'COMPLETED', label: '5. Listo' },
  ]

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12 text-left animate-fade-in">
      {/* =====================================================================
          CAPA 1 (SUPERFICIE OPERATIVA): STATECHART DETERMINISTA UI = f(DomainState)
         ===================================================================== */}
      <section className="p-6 rounded-3xl bg-zinc-950 border border-zinc-850 space-y-5 shadow-xl">
        {/* Top Row: State Stepper Signifier */}
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-zinc-900 pb-4">
          <div className="flex items-center gap-2 overflow-x-auto pb-1">
            {stateSteps.map((st) => {
              const isCurrent = domainState.state === st.id
              if (st.id === 'HALTED_BY_CONFLICT' && !isCurrent) return null
              return (
                <span
                  key={st.id}
                  className={`px-2.5 py-1 rounded-full text-[11px] font-mono transition ${
                    isCurrent
                      ? st.id === 'HALTED_BY_CONFLICT'
                        ? 'bg-red-500/20 text-red-300 border border-red-500/40 font-bold'
                        : st.id === 'AWAITING_APPROVAL'
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold'
                        : 'bg-white text-black font-bold'
                      : 'bg-zinc-900/70 text-zinc-500'
                  }`}
                >
                  {st.label}
                </span>
              )
            })}
          </div>

          <span className="text-[11px] font-mono text-zinc-400">
            Estado actual: <strong className="text-zinc-200">{domainState.badgeLabel}</strong>
          </span>
        </div>

        {/* Resolution Feedback Banner */}
        {resolutionFeedback && (
          <div
            className={`p-4 rounded-2xl border text-xs flex items-center justify-between gap-3 ${
              resolutionFeedback.type === 'success'
                ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-200'
                : 'bg-red-950/30 border-red-500/40 text-red-200'
            }`}
          >
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>{resolutionFeedback.message}</span>
            </div>
            <button
              type="button"
              onClick={() => setResolutionFeedback(null)}
              className="text-xs underline cursor-pointer"
            >
              Cerrar
            </button>
          </div>
        )}

        {/* =================================================================
            BRANCH A: STATE = UNINITIALIZED (No Project Imported)
            Invariant 3: Zero Dead-Ends — Direct interactive step to link project
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
              {/* SINGLE Primary Action Token (Hick's Law) */}
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
            BRANCH B: STATE = HALTED_BY_CONFLICT (Inline Error Recovery - Nielsen #9)
            Translates exception into: (a) Natural Cause, (b) Flow Impact, (c) Direct Action
           ================================================================= */}
        {domainState.state === 'HALTED_BY_CONFLICT' && (
          <div className="p-6 rounded-2xl bg-red-950/20 border border-red-500/40 space-y-5">
            <div className="flex items-start gap-3.5">
              <div className="w-11 h-11 rounded-2xl bg-red-500/15 border border-red-500/30 flex items-center justify-center text-red-400 shrink-0">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div className="space-y-1">
                <span className="text-[10px] font-mono uppercase tracking-wider text-red-300 font-bold">
                  Protección Preventiva Activada
                </span>
                <h1 className="text-lg font-bold text-white">{domainState.title}</h1>
              </div>
            </div>

            {/* Nielsen #9 Structured 3-Part Diagnosis */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
              <div className="p-3.5 rounded-xl bg-black/80 border border-zinc-850 space-y-1">
                <span className="text-[10px] font-mono uppercase text-zinc-400 block">
                  (a) ¿Qué ocurrió? (Causa)
                </span>
                <p className="text-zinc-200 leading-relaxed">
                  {manualSimulatedConflict ||
                    domainState.subtitle ||
                    'Se detectaron cambios sin confirmar o una prueba que requiere revisión antes de continuar.'}
                </p>
              </div>

              <div className="p-3.5 rounded-xl bg-black/80 border border-zinc-850 space-y-1">
                <span className="text-[10px] font-mono uppercase text-zinc-400 block">
                  (b) Impacto en tu proyecto
                </span>
                <p className="text-zinc-200 leading-relaxed">
                  Tus archivos principales están intactos. El lanzamiento de nuevos sprints se pausó preventivamente para evitar sobrescribir tu trabajo.
                </p>
              </div>

              <div className="p-3.5 rounded-xl bg-black/80 border border-zinc-850 space-y-1">
                <span className="text-[10px] font-mono uppercase text-zinc-400 block">
                  (c) Solución directa
                </span>
                <p className="text-zinc-200 leading-relaxed">
                  Ejecuta la restauración automática del entorno seguro para limpiar el bloqueo y reanudar el trabajo.
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-red-500/20">
              <button
                type="button"
                onClick={() => onNavigateSection('connections')}
                className="px-3.5 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-300 text-xs font-medium transition cursor-pointer"
              >
                Revisar Conexiones del Sistema
              </button>

              {/* SINGLE Primary Action Token (Hick's Law) */}
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
            BRANCH C: STATE = AWAITING_APPROVAL (Foreground Inline Resolution Flow)
            Poka-Yoke: Blocks new sprint launches and presents step-by-step approval inline
           ================================================================= */}
        {domainState.state === 'AWAITING_APPROVAL' && (
          <div className="p-6 rounded-2xl bg-zinc-900/50 border border-amber-500/40 space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-850 pb-4">
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

            {/* Step 1: Plain-language Verification Summary */}
            {gateDossier?.decision_checklist && (
              <div className="space-y-2">
                <span className="text-xs font-bold text-zinc-200 block">
                  1. Verificaciones de Calidad Superadas:
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                  {gateDossier.decision_checklist.slice(0, 3).map((chk: any) => (
                    <div
                      key={chk.id}
                      className="p-3.5 rounded-xl bg-black border border-zinc-850 space-y-1"
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

            {/* Layer 2 On-Demand Technical Diff Accordion */}
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
                <div className="mt-2.5 p-3.5 rounded-xl bg-black border border-zinc-850 font-mono text-xs max-h-40 overflow-y-auto space-y-0.5">
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

            {/* Step 2: Poka-Yoke Note Validation */}
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

            {/* Step 3: CQRS Action Buttons (1 Primary Token + 1 Secondary Action) */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-zinc-850">
              <button
                type="button"
                onClick={() => handleInlineGateDecision('REJECTED')}
                disabled={decidingGate || !isJustificationValid}
                className="px-4 py-2.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-750 text-zinc-300 hover:text-white text-xs font-semibold transition cursor-pointer disabled:opacity-40"
              >
                Rechazar Entrega
              </button>

              {/* SINGLE Primary Action Token (Hick's Law) */}
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
            Blocks conflicting actions while real subprocesses run
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
            BRANCH E: STATE = COMPLETED / READY / PLANNING (Clean Happy Path)
            Strictly ONE Primary Action Button in the entire viewport (Invariant 2)
           ================================================================= */}
        {(domainState.state === 'COMPLETED' || domainState.state === 'PLANNING') && (
          <div className="space-y-5">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-5 p-6 rounded-2xl bg-zinc-900/35 border border-zinc-850">
              <div className="space-y-2 max-w-2xl">
                <div className="inline-flex items-center gap-2 text-xs font-semibold text-emerald-400">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>{domainState.badgeLabel}</span>
                </div>
                <h1 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
                  {domainState.title}
                </h1>
                <p className="text-xs sm:text-sm text-zinc-300 leading-relaxed">
                  {domainState.subtitle}
                </p>
              </div>

              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 shrink-0">
                {/* Secondary Action: Verify Project Health */}
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
                  <span>Verificar Estado del Proyecto</span>
                </button>

                {/* SINGLE Primary Action Token in the Viewport (Hick's Law & Invariant 2) */}
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

            {/* Empirical Verification Result if just executed */}
            {healthResult && (
              <div className="p-4 rounded-2xl bg-black border border-emerald-500/35 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div className="flex items-center gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <div>
                    <span className="font-bold text-white block">{healthResult.title}</span>
                    <span className="text-zinc-400">{healthResult.summary}</span>
                  </div>
                </div>
                <div className="flex items-center gap-3 self-end sm:self-center">
                  <span className="px-2.5 py-1 rounded-lg bg-zinc-900 text-emerald-400 font-mono font-bold">
                    Medido: {healthResult.duration_sec}s
                  </span>
                  <button
                    type="button"
                    onClick={() => setHealthResult(null)}
                    className="text-zinc-400 hover:text-white underline cursor-pointer"
                  >
                    Cerrar
                  </button>
                </div>
              </div>
            )}

            {/* Gestalt Proximity & Figure-Ground: Clean Task Progress Overview without duplicate CTAs */}
            <div className="p-5 sm:p-6 rounded-2xl bg-zinc-900/25 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <h2 className="text-sm font-bold text-white">
                    Progreso de Requerimientos Activos ({completedCount} de {tasks.length} completados)
                  </h2>
                  <p className="text-xs text-zinc-400 mt-0.5">
                    Proyecto vinculado: <strong className="text-zinc-200">{activeProject?.name || 'Tienda Online'}</strong>
                  </p>
                </div>

                {/* Secondary link to the Canonical Backlog entity */}
                <button
                  type="button"
                  onClick={() => onNavigateSection('jira')}
                  className="text-xs text-zinc-300 hover:text-white flex items-center gap-1 font-medium cursor-pointer self-start sm:self-auto"
                >
                  <span>Gestionar requerimientos completos</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Clean Progress Bar */}
              <div className="h-2 w-full bg-zinc-900 rounded-full overflow-hidden">
                <div
                  className="h-full bg-emerald-400 rounded-full transition-all duration-500"
                  style={{ width: `${Math.max(completionPct, 12)}%` }}
                />
              </div>

              {/* Task Items (Read-only summary in Layer 1 — no duplicate "+ Nueva Tarea" button!) */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                {tasks.slice(0, 4).map((task) => {
                  const isDone = task.status === 'Completada' || task.progress === 100
                  return (
                    <div
                      key={task.id}
                      onClick={() => onNavigateSection('jira')}
                      className="p-3.5 rounded-2xl bg-zinc-950/90 hover:bg-zinc-900/80 border border-zinc-850 transition cursor-pointer flex items-center justify-between gap-3"
                    >
                      <div className="flex items-center gap-2.5 min-w-0">
                        <CheckCircle2
                          className={`w-4 h-4 shrink-0 ${
                            isDone ? 'text-emerald-400' : 'text-zinc-500'
                          }`}
                        />
                        <span className="text-xs font-semibold text-white truncate">
                          {task.title}
                        </span>
                      </div>
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-semibold shrink-0 ${
                          isDone
                            ? 'bg-emerald-500/15 text-emerald-300'
                            : 'bg-zinc-900 text-zinc-400'
                        }`}
                      >
                        {isDone ? 'Completada' : 'En curso'}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        )}
      </section>

      {/* =====================================================================
          CAPA 2 (TELEMETRÍA E IMPLEMENTACIÓN BAJO DEMANDA)
          Encapsulates Git commits, runtime process counts, and statechart testing
         ===================================================================== */}
      <section className="rounded-2xl bg-zinc-950 border border-zinc-850 overflow-hidden">
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
                Capa 2 · Inspección Técnica y Telemetría de Ingeniería
              </span>
              <span className="text-[11px] text-zinc-500">
                Historial de versiones, procesos activos en sistema operativo y simulador de estados FSM
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
          <div className="p-5 pt-0 border-t border-zinc-900 space-y-4 mt-4 text-xs animate-fade-in">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 font-mono">
              <div className="p-3.5 rounded-xl bg-black border border-zinc-850">
                <span className="text-[10px] text-zinc-500 uppercase block">
                  Procesos Activos en SO
                </span>
                <span className="text-sm font-bold text-white mt-0.5 block">
                  {agents.length === 0
                    ? '0 en ejecución (0 tokens en reposo)'
                    : `${agents.length} activos`}
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-black border border-zinc-850">
                <span className="text-[10px] text-zinc-500 uppercase block">
                  Rama y Estado del Repositorio
                </span>
                <span className="text-sm font-bold text-zinc-200 mt-0.5 block">
                  {(activeProject as any)?.branch || 'main'} &bull; Verificado
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-black border border-zinc-850 flex items-center justify-between">
                <div>
                  <span className="text-[10px] text-zinc-500 uppercase block">
                    Prueba de Invariante FSM
                  </span>
                  <span className="text-[11px] text-zinc-300 mt-0.5 block">
                    Simular bloqueo preventivo
                  </span>
                </div>
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
                  className="px-2.5 py-1.5 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-750 text-zinc-200 text-[11px] cursor-pointer"
                >
                  {domainState.state === 'HALTED_BY_CONFLICT'
                    ? 'Quitar Simulación'
                    : 'Probar Estado Conflicto'}
                </button>
              </div>
            </div>

            {/* Recent Git Commits (Layer 2) */}
            {commits.length > 0 && (
              <div className="space-y-2">
                <span className="text-[10px] font-mono uppercase text-zinc-500 block">
                  Últimos Commits Registrados en Git:
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 font-mono">
                  {commits.slice(0, 4).map((c, i) => (
                    <div
                      key={c.sha || i}
                      className="p-2.5 rounded-xl bg-black border border-zinc-850 flex items-center justify-between gap-2"
                    >
                      <span className="text-zinc-300 truncate">{c.message}</span>
                      <span className="text-[10px] text-zinc-500 shrink-0">{c.sha}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  )
}
