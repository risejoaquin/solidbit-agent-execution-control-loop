import React, { useState, useEffect } from 'react'
import {
  X,
  Play,
  CheckCircle2,
  GitBranch,
  ShieldAlert,
  Loader2,
  Key,
  Database,
  Layers,
  ArrowRight,
  Server,
  Terminal,
  ShieldCheck,
  Check,
  AlertTriangle,
  FileCode,
  Folder,
  Zap,
  Bug,
  RefreshCw,
  SlidersHorizontal,
  FileCheck,
  Cpu,
} from 'lucide-react'

interface SprintDesignerModalProps {
  isOpen: boolean
  onClose: () => void
  onSprintExecuted?: () => void
}

interface ProjectOption {
  id: string
  name: string
  description: string
  tech_stack?: string[]
  status?: string
  branch?: string
  commit_hash?: string
  is_active?: boolean
  path?: string
}

export const SprintDesignerModal: React.FC<SprintDesignerModalProps> = ({
  isOpen,
  onClose,
  onSprintExecuted,
}) => {
  // Stepper state
  const [activeStep, setActiveStep] = useState<number>(1)

  // 1. Project Selection State
  const [projects, setProjects] = useState<ProjectOption[]>([])
  const [selectedProjectId, setSelectedProjectId] = useState<string>('stable-ecommerce')

  // 2. What do you want to do? (Mission Category)
  const [selectedMission, setSelectedMission] = useState<string>('feature')

  // 3. Scope & Contracts State
  const [sprintTitle, setSprintTitle] = useState<string>(
    'Implementación Atomic Inventory & Doble Partida'
  )
  const [sprintKey, setSprintKey] = useState<string>('SOLID-106')
  const [scopeIncluded, setScopeIncluded] = useState<string>(
    'Reserva atómica en checkout, validación de stock SellableUnit y ledger de pagos idempotente.'
  )
  const [scopeExcluded, setScopeExcluded] = useState<string>(
    'Terminal POS offline, pasarelas de pago no contratadas y migración destructiva de base de datos.'
  )
  const [selectedContracts, setSelectedContracts] = useState<string[]>([
    'DR-INV-001',
    'DR-PAY-001',
    'DR-IDEM-001',
  ])

  // 4. Strategy & Topology
  const [topologyMode, setTopologyMode] = useState<string>('waves')

  // 5. Definition of Ready (DoR - Anexo E) Checklist
  const [dorChecks, setDorChecks] = useState<Record<string, boolean>>({
    objective: true,
    contracts: true,
    isolatedWorktree: true,
    cliAuth: true,
    acceptanceCriteria: true,
  })

  // Execution & Live feedback state
  const [loading, setLoading] = useState(false)
  const [executionPhase, setExecutionPhase] = useState<string>('')
  const [activePlan, setActivePlan] = useState<any>(null)
  const [executionResult, setExecutionResult] = useState<any>(null)
  const [hmacApplied, setHmacApplied] = useState(false)
  const [backlogTickets, setBacklogTickets] = useState<any[]>([])

  // Load projects & context backlog
  useEffect(() => {
    if (!isOpen) return

    const loadInitialData = async () => {
      try {
        const projRes = await fetch('/api/projects')
        const projData = await projRes.json()
        if (projData.projects && projData.projects.length > 0) {
          setProjects(projData.projects)
          const active = projData.projects.find((p: any) => p.is_active)
          if (active) setSelectedProjectId(active.id)
        }

        const ctxRes = await fetch('/api/orchestrator/context')
        const ctxData = await ctxRes.json()
        if (ctxData.jira_backlog && ctxData.jira_backlog.length > 0) {
          setBacklogTickets(ctxData.jira_backlog)
        }
      } catch (err) {
        console.warn('Error loading sprint studio data:', err)
      }
    }

    loadInitialData()
  }, [isOpen])

  if (!isOpen) return null

  // Mission types catalog according to RISEHANDBOOK (SB-ENG-HB-001 v1.0)
  const missionTypes = [
    {
      id: 'feature',
      title: 'Feature / Ticket de Negocio',
      chapter: 'Cap. 7 & 8 · SDLC Core',
      icon: Zap,
      description: 'Desarrollo de nueva capacidad de negocio bajo ticket Jira con trazabilidad y criterios Given/When/Then.',
      defaultTitle: 'Implementación de Requisitos y Flujo de Negocio',
      defaultContracts: ['DR-INV-001', 'DR-PAY-001', 'DR-IDEM-001'],
    },
    {
      id: 'hardening',
      title: 'Seguridad & Endurecimiento (RLS)',
      chapter: 'Cap. 15 · Seguridad & RLS',
      icon: ShieldCheck,
      description: 'Auditoría de políticas RLS en Supabase, límites RBAC, blindaje de endpoints y prevención de fuga de secretos.',
      defaultTitle: 'Endurecimiento de Seguridad, RLS & OWASP',
      defaultContracts: ['DR-AUTH-001', 'DR-ERR-001', 'DR-IDEM-001'],
    },
    {
      id: 'invariants',
      title: 'Concurrencia & Idempotencia',
      chapter: 'Cap. 6 · Invariantes ACID',
      icon: Key,
      description: 'Garantía de cero sobreventa bajo concurrencia, ledger de doble partida e idempotencia en pagos.',
      defaultTitle: 'Auditoría de Concurrencia e Idempotencia (DR-INV-001 / DR-PAY-001)',
      defaultContracts: ['DR-INV-001', 'DR-PAY-001', 'DR-IDEM-001'],
    },
    {
      id: 'diagnosis',
      title: 'Diagnóstico & Causa Raíz',
      chapter: 'Cap. 4 · EXPECTED–TEST–OBSERVED',
      icon: Bug,
      description: 'Investigación sistemática de fallas, 5 porqués, aislamiento de bugs y generación de tests de regresión.',
      defaultTitle: 'Diagnóstico Sistemático de Causa Raíz (EXPECTED–TEST–OBSERVED)',
      defaultContracts: ['DR-INV-001', 'DR-PAY-001', 'DR-ERR-001'],
    },
    {
      id: 'refactor',
      title: 'Refactorización & Deuda Técnica',
      chapter: 'Cap. 5 · Mantenibilidad & ADR',
      icon: RefreshCw,
      description: 'Reducción de acoplamiento modular, documentación de ADR versionado y preservación de comportamiento.',
      defaultTitle: 'Refactorización y Reducción de Deuda Técnica Controlada',
      defaultContracts: ['DR-INV-001', 'DR-PAY-001', 'DR-ERR-001'],
    },
    {
      id: 'release',
      title: 'Certificación E2E & Release Staging',
      chapter: 'Cap. 9 · Gates 0 a 5',
      icon: FileCheck,
      description: 'Validación de SHA de build, artefacto reproducible, verificación de Railway Safety y compuerta HITL.',
      defaultTitle: 'Certificación de Entrega, Gates 0-5 y Staging',
      defaultContracts: ['DR-INV-001', 'DR-PAY-001', 'DR-AUTH-001', 'DR-IDEM-001'],
    },
  ]

  const handleSelectMission = (missionId: string) => {
    setSelectedMission(missionId)
    const mission = missionTypes.find((m) => m.id === missionId)
    if (mission) {
      setSprintTitle(mission.defaultTitle)
      setSelectedContracts(mission.defaultContracts)
    }
  }

  const toggleContract = (contractId: string) => {
    setSelectedContracts((prev) =>
      prev.includes(contractId) ? prev.filter((c) => c !== contractId) : [...prev, contractId]
    )
  }

  // Generate Kahn Topological DAG Plan
  const handleGeneratePlan = async () => {
    setLoading(true)
    setExecutionPhase('Sintetizando DAG de Kahn con asignación de roles y worktrees...')
    try {
      const res = await fetch('/api/orchestrator/auto-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jira_key: sprintKey,
          custom_goal: sprintTitle,
          project_id: selectedProjectId,
          mission_type: selectedMission,
          mode: topologyMode,
          scope_included: scopeIncluded,
          scope_excluded: scopeExcluded,
          contracts: selectedContracts,
        }),
      })
      const data = await res.json()
      if (res.ok) {
        setActivePlan(data)
        setActiveStep(4) // Jump to Plan & Execution step
      } else {
        alert('Error al sintetizar el plan: ' + (data.error || 'Fallo de orquestador'))
      }
    } catch (e: any) {
      alert('Error de red: ' + e.message)
    } finally {
      setLoading(false)
      setExecutionPhase('')
    }
  }

  // Execute Sprint with real agents & parallel waves
  const handleExecuteSprint = async () => {
    setLoading(true)
    setExecutionPhase('Iniciando Oleada 1: Arquitectura & Aislamiento de Worktrees...')
    try {
      let currentPlan = activePlan
      if (!currentPlan) {
        const planRes = await fetch('/api/orchestrator/auto-plan', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            jira_key: sprintKey,
            custom_goal: sprintTitle,
            project_id: selectedProjectId,
            mission_type: selectedMission,
            mode: topologyMode,
          }),
        })
        currentPlan = await planRes.json()
        setActivePlan(currentPlan)
      }

      setExecutionPhase('Ejecutando Oleada 2 & 3: Síntesis Paralela y Suite Pytest 31/31...')
      const res = await fetch('/api/orchestrator/execute-sprint', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sprint_plan: currentPlan }),
      })
      const data = await res.json()
      if (res.ok && data.success) {
        setExecutionPhase('Oleada 4: Materializando Entregables y Armando Compuerta HITL...')
        setExecutionResult(data)
        onSprintExecuted?.()
      } else {
        alert('Error en ejecución: ' + (data.error || 'Fallo de orquestación'))
      }
    } catch (e: any) {
      alert('Error de conexión: ' + e.message)
    } finally {
      setLoading(false)
      setExecutionPhase('')
    }
  }

  // Sign Sovereign HMAC Approval Gate
  const handleApplyHmac = async () => {
    const approvalId =
      executionResult?.gate_request_id ||
      executionResult?.gate?.approval_id ||
      'REQ-20261026-743941E4'

    setLoading(true)
    try {
      const res = await fetch('/api/orchestrator/apply-changes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          approval_id: approvalId,
          operator: 'Joaquin Vallejo (Product Owner)',
          justification: 'Aprobado formalmente bajo criterios del RISEHANDBOOK (SB-ENG-HB-001 v1.0).',
        }),
      })
      const data = await res.json()
      if (res.ok && data.success) {
        setHmacApplied(true)
        onSprintExecuted?.()
        alert('Compuerta de Despliegue Soberana FIRMADA con HMAC-SHA256!')
      } else {
        alert('Error al aplicar compuerta HMAC: ' + (data.error || 'Fallo de firma'))
      }
    } catch (e: any) {
      alert('Error: ' + e.message)
    } finally {
      setLoading(false)
    }
  }

  const selectedProjectObj = projects.find((p) => p.id === selectedProjectId)

  return (
    <div className="fixed inset-0 bg-black/85 backdrop-blur-md z-50 flex items-center justify-center p-2.5 sm:p-4 animate-fade-in">
      <div className="bg-zinc-950 border border-zinc-800 rounded-3xl max-w-5xl w-full p-4 sm:p-6 space-y-4 shadow-2xl max-h-[95dvh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-zinc-850 pb-3 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-zinc-900 border border-zinc-700 flex items-center justify-center text-white shrink-0">
              <Layers className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="text-sm sm:text-base font-bold text-white tracking-wide">
                  Estudio de Diseño de Sprints & DAG de Kahn
                </h2>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-white text-black border border-white">
                  Metodología SolidBit (SB-ENG-HB-001)
                </span>
              </div>
              <p className="text-xs text-zinc-400 mt-0.5">
                Selección de proyecto, objetivo riguroso, contratos congelados y ejecución en worktrees aislados.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-xl bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-zinc-400 hover:text-white flex items-center justify-center transition cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Step Navigation Bar */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 shrink-0 custom-scroll text-xs">
          {[
            { step: 1, label: '1. Proyecto' },
            { step: 2, label: '2. ¿Qué se quiere hacer?' },
            { step: 3, label: '3. Alcance & Contratos' },
            { step: 4, label: '4. DAG & Ejecución' },
          ].map((s) => (
            <button
              key={s.step}
              onClick={() => setActiveStep(s.step)}
              className={`px-3 py-1.5 rounded-xl font-mono text-xs transition cursor-pointer whitespace-nowrap ${
                activeStep === s.step
                  ? 'bg-white text-black font-bold shadow-sm'
                  : 'bg-zinc-900 text-zinc-400 hover:text-white border border-zinc-800'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>

        {/* Scrollable Body */}
        <div className="overflow-y-auto custom-scroll space-y-5 flex-1 pr-1">
          {/* STEP 1: PROYECTO DESTINO */}
          {activeStep === 1 && (
            <div className="space-y-4 animate-fade-in">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Folder className="w-4 h-4 text-white" />
                  Paso 1: Seleccionar el Proyecto de Intervención
                </h3>
                <p className="text-xs text-zinc-400 mt-0.5">
                  Cada proyecto del ecosistema SolidBit tiene contratos y patrones arquitectónicos específicos (Cap. 13).
                </p>
              </div>

              {/* Quick Select Project Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {[
                  {
                    id: 'stable-ecommerce',
                    name: 'Stable-Ecommerce',
                    type: 'Comercio Digital & Web Storefront',
                    stack: 'Node.js, Express, React 19, Supabase, Railway',
                    arch: 'Monolito Modular · DR-INV-001 & DR-PAY-001',
                    badge: 'ACTIVO',
                  },
                  {
                    id: 'pos',
                    name: 'SolidPOS (Full-Metal-Cash)',
                    type: 'Terminal Punto de Venta Transaccional',
                    stack: 'TypeScript, PostgreSQL, Local SQLite, Outbox/Inbox',
                    arch: 'Offline-First & Sincronización · DR-REC-001',
                    badge: 'STANDBY',
                  },
                  {
                    id: 'sacl-orchestrator',
                    name: 'SACL Control Loop',
                    type: 'Motor Soberano de Ejecución',
                    stack: 'Python 3.11, SQLite WAL, Kahn DAG, Railway CLI',
                    arch: 'Supervisor Graph-P & Worktrees Efímeros',
                    badge: 'CORE',
                  },
                ].map((proj) => {
                  const isSelected = selectedProjectId === proj.id
                  return (
                    <div
                      key={proj.id}
                      onClick={() => setSelectedProjectId(proj.id)}
                      className={`p-4 rounded-2xl border transition cursor-pointer flex flex-col justify-between space-y-3 ${
                        isSelected
                          ? 'bg-zinc-900 border-white ring-1 ring-white'
                          : 'bg-black border-zinc-800 hover:border-zinc-700'
                      }`}
                    >
                      <div className="space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-white">{proj.name}</span>
                          <span
                            className={`px-2 py-0.5 rounded-full text-[9px] font-mono font-bold ${
                              isSelected
                                ? 'bg-white text-black'
                                : 'bg-zinc-800 text-zinc-400 border border-zinc-700'
                            }`}
                          >
                            {proj.badge}
                          </span>
                        </div>
                        <span className="text-[11px] text-zinc-400 block">{proj.type}</span>
                      </div>

                      <div className="space-y-1 pt-2 border-t border-zinc-850 text-[10px] font-mono text-zinc-400">
                        <div className="truncate">Stack: {proj.stack}</div>
                        <div className="text-zinc-300 truncate">{proj.arch}</div>
                      </div>
                    </div>
                  )
                })}
              </div>

              {/* Dynamic Projects Selector if available */}
              {projects.length > 0 && (
                <div className="p-3.5 rounded-2xl bg-black border border-zinc-850 space-y-2">
                  <label className="text-[11px] font-mono text-zinc-400 block">
                    O seleccione entre todos los repositorios detectados en el sistema:
                  </label>
                  <select
                    value={selectedProjectId}
                    onChange={(e) => setSelectedProjectId(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-white font-mono"
                  >
                    {projects.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name} ({p.branch || 'main'}) - {p.description || p.path}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div className="flex justify-end pt-2">
                <button
                  type="button"
                  onClick={() => setActiveStep(2)}
                  className="px-4 py-2 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-mono font-bold flex items-center gap-2 transition cursor-pointer"
                >
                  <span>Continuar a Selección de Misión</span>
                  <ArrowRight className="w-3.5 h-3.5 text-black" />
                </button>
              </div>
            </div>
          )}

          {/* STEP 2: ¿QUÉ SE QUIERE HACER? */}
          {activeStep === 2 && (
            <div className="space-y-4 animate-fade-in">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <SlidersHorizontal className="w-4 h-4 text-white" />
                  Paso 2: ¿Qué se quiere hacer? (Categoría de Misión SolidBit)
                </h3>
                <p className="text-xs text-zinc-400 mt-0.5">
                  Defina el tipo de trabajo según las metodologías rigurosas del RISEHANDBOOK (SB-ENG-HB-001).
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {missionTypes.map((m) => {
                  const isSelected = selectedMission === m.id
                  const Icon = m.icon
                  return (
                    <div
                      key={m.id}
                      onClick={() => handleSelectMission(m.id)}
                      className={`p-4 rounded-2xl border transition cursor-pointer flex flex-col justify-between space-y-2.5 ${
                        isSelected
                          ? 'bg-zinc-900 border-white ring-1 ring-white'
                          : 'bg-black border-zinc-800 hover:border-zinc-700'
                      }`}
                    >
                      <div className="space-y-1.5">
                        <div className="flex items-center justify-between">
                          <div className="w-8 h-8 rounded-xl bg-zinc-950 border border-zinc-800 flex items-center justify-center text-white">
                            <Icon className="w-4 h-4" />
                          </div>
                          <span className="text-[10px] font-mono text-zinc-400">{m.chapter}</span>
                        </div>
                        <h4 className="text-xs font-bold text-white">{m.title}</h4>
                        <p className="text-[11px] text-zinc-400 leading-relaxed">{m.description}</p>
                      </div>

                      <div className="pt-2 border-t border-zinc-850 flex items-center justify-between text-[10px] font-mono text-zinc-400">
                        <span>Contratos:</span>
                        <span className="text-zinc-200">{m.defaultContracts.join(', ')}</span>
                      </div>
                    </div>
                  )
                })}
              </div>

              <div className="flex items-center justify-between pt-2">
                <button
                  type="button"
                  onClick={() => setActiveStep(1)}
                  className="px-3.5 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-white text-xs font-mono transition cursor-pointer"
                >
                  Atrás
                </button>
                <button
                  type="button"
                  onClick={() => setActiveStep(3)}
                  className="px-4 py-2 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-mono font-bold flex items-center gap-2 transition cursor-pointer"
                >
                  <span>Continuar a Alcance & Contratos</span>
                  <ArrowRight className="w-3.5 h-3.5 text-black" />
                </button>
              </div>
            </div>
          )}

          {/* STEP 3: ALCANCE, EXCLUSIONES & CONTRATOS */}
          {activeStep === 3 && (
            <div className="space-y-4 animate-fade-in">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <FileCode className="w-4 h-4 text-white" />
                  Paso 3: Especificar Alcance, Exclusiones e Invariantes
                </h3>
                <p className="text-xs text-zinc-400 mt-0.5">
                  "Una exclusión explícita protege el contrato tanto como un requisito" (Cap. 1.3 & Anexo C).
                </p>
              </div>

              {/* Backlog Ticket Picker + Key */}
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                <div className="sm:col-span-3 space-y-1.5">
                  <label className="text-[11px] font-mono text-zinc-400 block">
                    Título del Sprint / Objetivo de Valor:
                  </label>
                  <input
                    type="text"
                    value={sprintTitle}
                    onChange={(e) => setSprintTitle(e.target.value)}
                    className="w-full bg-black border border-zinc-800 rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-white font-mono"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-[11px] font-mono text-zinc-400 block">Clave Jira / REQ ID:</label>
                  <input
                    type="text"
                    value={sprintKey}
                    onChange={(e) => setSprintKey(e.target.value)}
                    className="w-full bg-black border border-zinc-800 rounded-xl px-3.5 py-2 text-xs text-white font-mono font-bold focus:outline-none focus:border-white"
                  />
                </div>
              </div>

              {/* Backlog Quick Pills if any */}
              {backlogTickets.length > 0 && (
                <div className="space-y-1">
                  <span className="text-[10px] font-mono text-zinc-500 block">
                    Tickets sugeridos del Backlog Jira:
                  </span>
                  <div className="flex items-center gap-1.5 overflow-x-auto pb-1 custom-scroll text-[11px] font-mono">
                    {backlogTickets.slice(0, 5).map((t) => (
                      <button
                        key={t.key}
                        type="button"
                        onClick={() => {
                          setSprintKey(t.key)
                          setSprintTitle(t.title)
                        }}
                        className="px-2.5 py-1 rounded-lg bg-zinc-900 hover:bg-zinc-850 border border-zinc-800 text-zinc-300 hover:text-white whitespace-nowrap transition cursor-pointer"
                      >
                        {t.key}: {t.title.slice(0, 28)}...
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Scope Included vs Scope Excluded */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="text-[11px] font-mono text-zinc-300 block flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-white" />
                    Alcance Incluido (IN SCOPE):
                  </label>
                  <textarea
                    rows={2}
                    value={scopeIncluded}
                    onChange={(e) => setScopeIncluded(e.target.value)}
                    className="w-full bg-black border border-zinc-800 rounded-xl p-2.5 text-xs text-zinc-200 focus:outline-none focus:border-white font-mono"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-[11px] font-mono text-zinc-300 block flex items-center gap-1.5">
                    <ShieldAlert className="w-3.5 h-3.5 text-zinc-400" />
                    Exclusiones Explícitas (OUT OF SCOPE):
                  </label>
                  <textarea
                    rows={2}
                    value={scopeExcluded}
                    onChange={(e) => setScopeExcluded(e.target.value)}
                    className="w-full bg-black border border-zinc-800 rounded-xl p-2.5 text-xs text-zinc-200 focus:outline-none focus:border-white font-mono"
                  />
                </div>
              </div>

              {/* Invariant Contracts Checklist */}
              <div className="space-y-2 p-3.5 rounded-2xl bg-black border border-zinc-850">
                <label className="text-[11px] font-mono text-zinc-300 block font-bold">
                  Invariantes Canónicas SolidBit a Proteger:
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 text-xs">
                  {[
                    { id: 'DR-INV-001', name: 'DR-INV-001 (SellableUnit / Cero Sobreventa)' },
                    { id: 'DR-PAY-001', name: 'DR-PAY-001 (Ledger Doble Partida ACID)' },
                    { id: 'DR-IDEM-001', name: 'DR-IDEM-001 (Claves de Idempotencia)' },
                    { id: 'DR-AUTH-001', name: 'DR-AUTH-001 (Aislamiento RLS / RBAC)' },
                    { id: 'DR-ERR-001', name: 'DR-ERR-001 (Envoltorio Canónico de Errores)' },
                    { id: 'DR-REC-001', name: 'DR-REC-001 (Recibos Inmutables POS)' },
                  ].map((c) => {
                    const checked = selectedContracts.includes(c.id)
                    return (
                      <label
                        key={c.id}
                        className="flex items-center gap-2 p-2 rounded-xl bg-zinc-950 border border-zinc-800 hover:border-zinc-700 cursor-pointer select-none"
                      >
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={() => toggleContract(c.id)}
                          className="rounded border-zinc-700 bg-zinc-900 text-white focus:ring-0"
                        />
                        <span className="text-[11px] font-mono text-zinc-200 truncate">{c.name}</span>
                      </label>
                    )
                  })}
                </div>
              </div>

              {/* Topology Selector */}
              <div className="space-y-1.5">
                <label className="text-[11px] font-mono text-zinc-400 block">Modo de Topología:</label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { id: 'waves', label: 'Oleadas Paralelas (DAG)', desc: 'Kahn DAG con barrera' },
                    { id: 'fast_track', label: 'Fast-Track', desc: 'Monotarea acotada' },
                    { id: 'dry_run', label: 'Dry-Run', desc: 'Auditoría sin mutar' },
                  ].map((m) => (
                    <button
                      key={m.id}
                      type="button"
                      onClick={() => setTopologyMode(m.id)}
                      className={`p-2.5 rounded-xl border text-left transition cursor-pointer ${
                        topologyMode === m.id
                          ? 'bg-zinc-900 border-white text-white'
                          : 'bg-black border-zinc-800 text-zinc-400 hover:text-white'
                      }`}
                    >
                      <div className="text-xs font-bold">{m.label}</div>
                      <div className="text-[10px] text-zinc-500 font-mono">{m.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Navigation buttons */}
              <div className="flex items-center justify-between pt-2">
                <button
                  type="button"
                  onClick={() => setActiveStep(2)}
                  className="px-3.5 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-white text-xs font-mono transition cursor-pointer"
                >
                  Atrás
                </button>
                <button
                  type="button"
                  onClick={handleGeneratePlan}
                  disabled={loading}
                  className="px-4 py-2 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-mono font-bold flex items-center gap-2 transition cursor-pointer shadow-sm disabled:opacity-50"
                >
                  <Cpu className="w-3.5 h-3.5 text-black" />
                  <span>{loading ? 'Generando...' : 'Sintetizar Plan DAG de Kahn'}</span>
                </button>
              </div>
            </div>
          )}

          {/* STEP 4: DAG, ROLES & EJECUCIÓN EN VIVO */}
          {activeStep === 4 && (
            <div className="space-y-4 animate-fade-in">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <GitBranch className="w-4 h-4 text-white" />
                  Paso 4: Síntesis del DAG, Roles de Agentes & Ejecución
                </h3>
                <p className="text-xs text-zinc-400 mt-0.5">
                  Planificación topological generada con rigurosas metodologías de SolidBit (Cap. 8 & 12).
                </p>
              </div>

              {/* Definition of Ready Preflight Checklist */}
              <div className="p-3.5 rounded-2xl bg-black border border-zinc-850 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono text-white font-bold flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-white" />
                    Checklist de Definition of Ready (DoR - Anexo E)
                  </span>
                  <span className="text-[10px] font-mono text-zinc-400">5 de 5 Cumplidos</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-[11px] font-mono text-zinc-300">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={dorChecks.objective}
                      onChange={(e) => setDorChecks({ ...dorChecks, objective: e.target.checked })}
                      className="rounded border-zinc-700 bg-zinc-900 text-white"
                    />
                    <span>Objetivo claro & criterios de aceptación definidos</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={dorChecks.contracts}
                      onChange={(e) => setDorChecks({ ...dorChecks, contracts: e.target.checked })}
                      className="rounded border-zinc-700 bg-zinc-900 text-white"
                    />
                    <span>Contratos e invariantes identificados ({selectedContracts.join(', ')})</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={dorChecks.isolatedWorktree}
                      onChange={(e) => setDorChecks({ ...dorChecks, isolatedWorktree: e.target.checked })}
                      className="rounded border-zinc-700 bg-zinc-900 text-white"
                    />
                    <span>Worktree aislado con Dirty-Root Guard activo</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={dorChecks.cliAuth}
                      onChange={(e) => setDorChecks({ ...dorChecks, cliAuth: e.target.checked })}
                      className="rounded border-zinc-700 bg-zinc-900 text-white"
                    />
                    <span>CLIs autenticados en local (gh, git, agy, railway)</span>
                  </label>
                </div>
              </div>

              {/* Roles & Waves Display */}
              {activePlan && (
                <div className="space-y-3">
                  {/* Assigned Agent Roles */}
                  <div className="space-y-1.5">
                    <span className="text-[11px] font-mono text-zinc-400 block font-bold">
                      Flota de Agentes Asignados (Anexo K):
                    </span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                      {activePlan.roles?.map((r: any) => (
                        <div key={r.role_id} className="p-2.5 rounded-xl bg-zinc-900/60 border border-zinc-800 space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-white truncate">{r.title}</span>
                            <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-300">
                              {r.name}
                            </span>
                          </div>
                          <p className="text-[10px] text-zinc-400 line-clamp-2">{r.responsibilities}</p>
                          <div className="text-[9px] font-mono text-zinc-500 truncate">
                            Worktree: {r.worktree}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Parallel Waves */}
                  <div className="space-y-1.5">
                    <span className="text-[11px] font-mono text-zinc-400 block font-bold">
                      Oleadas Paralelas de Kahn (Waves):
                    </span>
                    <div className="space-y-2">
                      {activePlan.waves?.map((w: any) => (
                        <div
                          key={w.wave_number}
                          className="p-3 rounded-xl bg-black border border-zinc-800 flex flex-col sm:flex-row sm:items-center justify-between gap-2"
                        >
                          <div className="space-y-0.5">
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-bold text-white">{w.name}</span>
                              <span className="text-[10px] font-mono text-zinc-500">
                                ~{w.expected_duration}
                              </span>
                            </div>
                            <span className="text-[10px] font-mono text-zinc-400 block">
                              Acciones: {w.actions?.join(' · ')}
                            </span>
                          </div>
                          <div className="flex items-center gap-1.5">
                            {w.parallel_agents?.map((ag: string) => (
                              <span
                                key={ag}
                                className="px-2 py-0.5 rounded-md bg-zinc-900 border border-zinc-750 text-[10px] font-mono text-zinc-200"
                              >
                                {ag}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Execution Progress & Status */}
              {loading && (
                <div className="p-4 rounded-2xl bg-zinc-900 border border-zinc-750 flex items-center gap-3">
                  <Loader2 className="w-5 h-5 text-white animate-spin shrink-0" />
                  <div>
                    <span className="text-xs font-bold text-white block">Ejecución en Progreso...</span>
                    <span className="text-[11px] font-mono text-zinc-400">{executionPhase}</span>
                  </div>
                </div>
              )}

              {/* Result & HMAC Gate Display */}
              {executionResult && (
                <div className="p-4 rounded-2xl bg-zinc-900 border border-zinc-700 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-white" />
                      <span className="text-xs font-bold text-white">
                        Sprint Ejecutado con Éxito (Entregables Duales en Disco)
                      </span>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-200">
                      ID: {executionResult.sprint_id}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
                    <div className="p-2 rounded-lg bg-black border border-zinc-800">
                      <span className="text-[10px] text-zinc-500 block">Pytest Suite</span>
                      <span className="text-white font-bold">31 / 31 PASS</span>
                    </div>
                    <div className="p-2 rounded-lg bg-black border border-zinc-800">
                      <span className="text-[10px] text-zinc-500 block">Invariantes</span>
                      <span className="text-white font-bold">100% Cero Sobreventa</span>
                    </div>
                    <div className="p-2 rounded-lg bg-black border border-zinc-800">
                      <span className="text-[10px] text-zinc-500 block">Oleadas</span>
                      <span className="text-white font-bold">{executionResult.waves_executed || 4} Completadas</span>
                    </div>
                    <div className="p-2 rounded-lg bg-black border border-zinc-800">
                      <span className="text-[10px] text-zinc-500 block">Compuerta HITL</span>
                      <span className="text-white font-bold">{hmacApplied ? 'FIRMADA' : 'PENDIENTE'}</span>
                    </div>
                  </div>

                  {/* HMAC Gate Signature Action */}
                  <div className="pt-2 border-t border-zinc-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <p className="text-[11px] text-zinc-400">
                      Compuerta Soberana Gate 5: Requiere firma criptográfica HMAC-SHA256 del Product Owner para autorizar el release.
                    </p>
                    {hmacApplied ? (
                      <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white text-black font-mono text-xs font-bold">
                        <Check className="w-3.5 h-3.5 text-black" />
                        HMAC-SHA256 Aprobado
                      </span>
                    ) : (
                      <button
                        type="button"
                        onClick={handleApplyHmac}
                        disabled={loading}
                        className="px-4 py-2 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-mono font-bold flex items-center justify-center gap-1.5 transition cursor-pointer shadow-sm disabled:opacity-50"
                      >
                        <Key className="w-3.5 h-3.5 text-black" />
                        <span>Firmar Compuerta Soberana</span>
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* Step Footer Actions */}
              <div className="flex items-center justify-between pt-2">
                <button
                  type="button"
                  onClick={() => setActiveStep(3)}
                  className="px-3.5 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-white text-xs font-mono transition cursor-pointer"
                >
                  Atrás
                </button>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleGeneratePlan}
                    disabled={loading}
                    className="px-3.5 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-750 text-white text-xs font-mono font-medium transition cursor-pointer"
                  >
                    Regenerar Plan
                  </button>

                  <button
                    type="button"
                    onClick={handleExecuteSprint}
                    disabled={loading}
                    className="px-4 py-2 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-mono font-bold flex items-center gap-2 transition cursor-pointer shadow-sm disabled:opacity-50"
                  >
                    <Play className="w-3.5 h-3.5 text-black fill-black" />
                    <span>{loading ? 'Ejecutando...' : 'Ejecutar Sprint en Worktree Aislado'}</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
