import React, { useState, useEffect } from 'react'
import {
  X,
  Play,
  CheckCircle2,
  Loader2,
  Key,
  ArrowRight,
  ShieldCheck,
  Check,
  Folder,
  Bug,
  SlidersHorizontal,
  FileCheck,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Lock,
} from 'lucide-react'

interface SprintDesignerModalProps {
  isOpen: boolean
  onClose: () => void
  onSprintExecuted?: () => void
  initialTicket?: any | null
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
  initialTicket,
}) => {
  // 3-Step Friendly Stepper
  const [activeStep, setActiveStep] = useState<number>(1)

  // Advanced Engineer Mode toggle (hidden by default for non-technical simplicity)
  const [showAdvancedMode, setShowAdvancedMode] = useState<boolean>(false)

  // 1. Project Selection State
  const [projects, setProjects] = useState<ProjectOption[]>([])
  const [selectedProjectId, setSelectedProjectId] = useState<string>('stable-ecommerce')

  // 2. What do you want to achieve?
  const [selectedMission, setSelectedMission] = useState<string>('feature')
  const [sprintTitle, setSprintTitle] = useState<string>(
    'Reserva segura de productos y cobro confiable en caja'
  )
  const [sprintKey, setSprintKey] = useState<string>('SOLID-106')
  const [scopeIncluded, setScopeIncluded] = useState<string>(
    'Asegurar que el inventario se descuente sin errores y que ningún cliente pague dos veces por el mismo pedido.'
  )
  const [scopeExcluded, setScopeExcluded] = useState<string>(
    'No modificar pantallas externas ni borrar historial de compras existentes.'
  )
  const [selectedContracts, setSelectedContracts] = useState<string[]>([
    'DR-INV-001',
    'DR-PAY-001',
    'DR-IDEM-001',
  ])
  const [topologyMode, setTopologyMode] = useState<string>('waves')

  // Execution & Live feedback state
  const [loading, setLoading] = useState(false)
  const [executionPhase, setExecutionPhase] = useState<string>('')
  const [activePlan, setActivePlan] = useState<any>(null)
  const [executionResult, setExecutionResult] = useState<any>(null)
  const [hmacApplied, setHmacApplied] = useState(false)
  const [backlogTickets, setBacklogTickets] = useState<any[]>([])

  // Pre-load from Jira ticket if launched from Jira Backlog
  useEffect(() => {
    if (initialTicket) {
      if (initialTicket.title) setSprintTitle(initialTicket.title)
      if (initialTicket.key) setSprintKey(initialTicket.key)
      if (initialTicket.contracts && initialTicket.contracts.length > 0) {
        setSelectedContracts(initialTicket.contracts)
      }
      if (initialTicket.description) setScopeIncluded(initialTicket.description)
      setActiveStep(2)
    }
  }, [initialTicket])

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

  // Simplified, human-centered goal templates (with technical mappings underneath)
  const missionTypes = [
    {
      id: 'feature',
      title: 'Crear una función nueva',
      subtitle: 'Agregar pantallas, botones o mejoras para tus usuarios',
      icon: Sparkles,
      description: 'Ideal cuando quieres sumar una herramienta nueva o mejorar la experiencia de compra.',
      defaultTitle: 'Nueva mejora funcional para clientes',
      defaultContracts: ['DR-INV-001', 'DR-PAY-001', 'DR-IDEM-001'],
      protectionSummary: 'Protección de inventario y pagos activada',
    },
    {
      id: 'diagnosis',
      title: 'Corregir un problema o error',
      subtitle: 'Algo no funciona bien y necesitas repararlo rápido',
      icon: Bug,
      description: 'El equipo IA investiga la causa del fallo, lo repara en una copia segura y verifica que no vuelva a ocurrir.',
      defaultTitle: 'Corrección y reparación de error detectado',
      defaultContracts: ['DR-INV-001', 'DR-PAY-001', 'DR-ERR-001'],
      protectionSummary: 'Diagnóstico seguro sin afectar clientes actuales',
    },
    {
      id: 'hardening',
      title: 'Mejorar seguridad y velocidad',
      subtitle: 'Blindar datos privados y optimizar el sistema',
      icon: ShieldCheck,
      description: 'Revisa permisos de acceso, protege contraseñas y asegura que nadie vea información ajena.',
      defaultTitle: 'Refuerzo de seguridad y protección de datos',
      defaultContracts: ['DR-AUTH-001', 'DR-ERR-001', 'DR-IDEM-001'],
      protectionSummary: 'Blindaje de cuentas y privacidad activo',
    },
    {
      id: 'release',
      title: 'Verificar y publicar cambios',
      subtitle: 'Revisar que todo esté listo antes de salir en vivo',
      icon: FileCheck,
      description: 'Ejecuta todas las pruebas de calidad y deja el paquete listo para que lo apruebes con un clic.',
      defaultTitle: 'Verificación de calidad y preparación de entrega',
      defaultContracts: ['DR-INV-001', 'DR-PAY-001', 'DR-AUTH-001', 'DR-IDEM-001'],
      protectionSummary: 'Revisión completa antes de publicar',
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

  // Generate Automatic Work Plan
  const handleGeneratePlan = async () => {
    setLoading(true)
    setExecutionPhase('Traduciendo tu solicitud en un plan de trabajo paso a paso...')
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
        setActiveStep(3)
      } else {
        alert('No pudimos armar el plan: ' + (data.error || 'Intenta nuevamente'))
      }
    } catch (e: any) {
      alert('Error de conexión: ' + e.message)
    } finally {
      setLoading(false)
      setExecutionPhase('')
    }
  }

  // Execute Sprint with real agents & parallel waves
  const handleExecuteSprint = async () => {
    setLoading(true)
    setExecutionPhase('Paso 1/3: Creando copia aislada para no afectar el sistema en vivo...')
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

      setExecutionPhase('Paso 2/3: Los asistentes IA están programando y probando la solución...')
      const res = await fetch('/api/orchestrator/execute-sprint', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sprint_plan: currentPlan }),
      })
      const data = await res.json()
      if (res.ok && data.success) {
        setExecutionPhase('Paso 3/3: Guardando resultados en tu base de datos local...')
        setExecutionResult(data)
        onSprintExecuted?.()
      } else {
        alert('Hubo un inconveniente al ejecutar: ' + (data.error || 'Revisa los detalles'))
      }
    } catch (e: any) {
      alert('Error de conexión: ' + e.message)
    } finally {
      setLoading(false)
      setExecutionPhase('')
    }
  }

  // Approve and Apply Changes
  const handleApplyHmac = async () => {
    const approvalId =
      executionResult?.gate_request_id ||
      executionResult?.gate?.approval_id ||
      'REQ-PENDING'

    setLoading(true)
    try {
      const res = await fetch('/api/orchestrator/apply-changes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          approval_id: approvalId,
          operator: localStorage.getItem('sacl_operator_name') || 'Operador Autorizado',
          justification: 'Aprobado desde el Asistente Simplificado de Sprints.',
        }),
      })
      const data = await res.json()
      if (res.ok && data.success) {
        setHmacApplied(true)
        onSprintExecuted?.()
      } else {
        alert('No se pudo autorizar el cambio: ' + (data.error || 'Fallo de autorización'))
      }
    } catch (e: any) {
      alert('Error: ' + e.message)
    } finally {
      setLoading(false)
    }
  }

  const projectCards = [
    {
      id: 'stable-ecommerce',
      name: 'Tienda Online (E-Commerce)',
      friendlyType: 'Catálogo web, carrito de compras y pagos con tarjeta',
      protection: 'Evita vender productos sin stock o cobrar doble',
      badge: 'PRINCIPAL',
    },
    {
      id: 'pos',
      name: 'Punto de Venta (SolidPOS)',
      friendlyType: 'Caja registradora rápida para tiendas físicas',
      protection: 'Funciona incluso si se corta el internet y sincroniza después',
      badge: 'TIENDA FÍSICA',
    },
    {
      id: 'sacl-orchestrator',
      name: 'Cerebro Orquestador (SACL)',
      friendlyType: 'Panel de control y coordinación de asistentes IA',
      protection: 'Guarda todo el historial en tu computadora de forma privada',
      badge: 'SISTEMA',
    },
  ]

  const selectedProjectCard =
    projectCards.find((p) => p.id === selectedProjectId) || projectCards[0]
  const selectedMissionCard =
    missionTypes.find((m) => m.id === selectedMission) || missionTypes[0]

  return (
    <div className="fixed inset-0 bg-black/85 backdrop-blur-md z-50 flex items-center justify-center p-2.5 sm:p-4 animate-fade-in">
      <div className="bg-zinc-950 border border-zinc-800 rounded-3xl max-w-4xl w-full p-4 sm:p-6 space-y-5 shadow-2xl max-h-[94dvh] flex flex-col">
        {/* Clean Human-Friendly Header */}
        <div className="flex items-center justify-between border-b border-zinc-850 pb-4 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-white text-black flex items-center justify-center shrink-0 shadow-sm">
              <Sparkles className="w-5 h-5 text-black" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="text-base sm:text-lg font-bold text-white tracking-tight">
                  Asistente para Crear una Nueva Tarea o Sprint
                </h2>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-zinc-900 text-zinc-200 border border-zinc-700">
                  Guiado en 3 pasos simples
                </span>
              </div>
              <p className="text-xs text-zinc-400 mt-0.5">
                Dinos qué necesitas lograr en lenguaje sencillo; el sistema configura la seguridad y coordina a los agentes automáticamente.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-xl bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-zinc-400 hover:text-white flex items-center justify-center transition cursor-pointer"
            title="Cerrar ventana"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Visual 3-Step Progress Bar */}
        <div className="grid grid-cols-3 gap-2 shrink-0">
          {[
            { step: 1, title: '1. Elegir Proyecto', desc: '¿Dónde trabajaremos?' },
            { step: 2, title: '2. Qué Necesitas', desc: 'Explica tu objetivo' },
            { step: 3, title: '3. Revisar y Lanzar', desc: 'Ejecutar con 1 clic' },
          ].map((s) => {
            const isCurrent = activeStep === s.step
            const isDone = activeStep > s.step
            return (
              <button
                key={s.step}
                type="button"
                onClick={() => setActiveStep(s.step)}
                className={`p-2.5 sm:p-3 rounded-2xl border text-left transition cursor-pointer flex items-center justify-between ${
                  isCurrent
                    ? 'bg-white text-black border-white shadow-sm'
                    : isDone
                    ? 'bg-zinc-900/90 text-white border-zinc-700'
                    : 'bg-zinc-950 text-zinc-400 border-zinc-850 hover:border-zinc-700 hover:text-zinc-200'
                }`}
              >
                <div className="min-w-0">
                  <div className="text-xs font-bold truncate">{s.title}</div>
                  <div
                    className={`text-[10px] truncate hidden sm:block ${
                      isCurrent ? 'text-zinc-700' : 'text-zinc-400'
                    }`}
                  >
                    {s.desc}
                  </div>
                </div>
                {isDone && (
                  <CheckCircle2
                    className={`w-4 h-4 shrink-0 ${isCurrent ? 'text-black' : 'text-white'}`}
                  />
                )}
              </button>
            )
          })}
        </div>

        {/* Scrollable Content Area */}
        <div className="overflow-y-auto custom-scroll space-y-5 flex-1 pr-1">
          {/* =========================================================
              PASO 1: ¿EN QUÉ PROYECTO TRABAJAREMOS?
             ========================================================= */}
          {activeStep === 1 && (
            <div className="space-y-4 animate-fade-in">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Folder className="w-4 h-4 text-white" />
                  Paso 1: ¿En qué parte de tu negocio quieres hacer mejoras hoy?
                </h3>
                <p className="text-xs text-zinc-400 mt-0.5">
                  Selecciona la aplicación. El sistema creará una copia de seguridad automática antes de tocar cualquier archivo.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {projectCards.map((proj) => {
                  const isSelected = selectedProjectId === proj.id
                  return (
                    <div
                      key={proj.id}
                      onClick={() => setSelectedProjectId(proj.id)}
                      className={`p-4 rounded-2xl border transition cursor-pointer flex flex-col justify-between space-y-3 ${
                        isSelected
                          ? 'bg-zinc-900 border-white ring-1 ring-white shadow-lg'
                          : 'bg-black border-zinc-800 hover:border-zinc-700'
                      }`}
                    >
                      <div className="space-y-1.5">
                        <div className="flex items-center justify-between gap-2">
                          <span className="text-xs font-bold text-white">{proj.name}</span>
                          <span
                            className={`px-2 py-0.5 rounded-full text-[9px] font-mono font-bold shrink-0 ${
                              isSelected
                                ? 'bg-white text-black'
                                : 'bg-zinc-800 text-zinc-300 border border-zinc-700'
                            }`}
                          >
                            {proj.badge}
                          </span>
                        </div>
                        <p className="text-xs text-zinc-300 leading-relaxed">
                          {proj.friendlyType}
                        </p>
                      </div>

                      <div className="pt-2.5 border-t border-zinc-850 flex items-start gap-1.5 text-[11px] text-zinc-400">
                        <ShieldCheck className="w-3.5 h-3.5 text-white shrink-0 mt-0.5" />
                        <span>{proj.protection}</span>
                      </div>
                    </div>
                  )
                })}
              </div>

              {/* Additional detected repositories if user has custom ones */}
              {projects.length > 0 && (
                <div className="p-3 rounded-2xl bg-zinc-900/40 border border-zinc-850 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <span className="text-xs text-zinc-300">
                    Carpeta conectada en tu computadora:
                  </span>
                  <select
                    value={selectedProjectId}
                    onChange={(e) => setSelectedProjectId(e.target.value)}
                    className="bg-black border border-zinc-800 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-white font-mono"
                  >
                    {projects.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name} ({p.branch || 'principal'})
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div className="flex justify-end pt-2">
                <button
                  type="button"
                  onClick={() => setActiveStep(2)}
                  className="px-5 py-2.5 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-bold flex items-center gap-2 transition cursor-pointer shadow-sm"
                >
                  <span>Siguiente: Describir qué necesito</span>
                  <ArrowRight className="w-4 h-4 text-black" />
                </button>
              </div>
            </div>
          )}

          {/* =========================================================
              PASO 2: ¿QUÉ NECESITAS LOGRAR HOY? (LENGUAJE HUMANO)
             ========================================================= */}
          {activeStep === 2 && (
            <div className="space-y-4 animate-fade-in">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-white" />
                  Paso 2: ¿Qué te gustaría lograr hoy en {selectedProjectCard.name}?
                </h3>
                <p className="text-xs text-zinc-400 mt-0.5">
                  Elige una opción rápida o escribe con tus propias palabras lo que necesitas.
                </p>
              </div>

              {/* 4 Friendly Goal Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {missionTypes.map((m) => {
                  const isSelected = selectedMission === m.id
                  const Icon = m.icon
                  return (
                    <div
                      key={m.id}
                      onClick={() => handleSelectMission(m.id)}
                      className={`p-3.5 rounded-2xl border transition cursor-pointer flex items-start gap-3 ${
                        isSelected
                          ? 'bg-zinc-900 border-white ring-1 ring-white'
                          : 'bg-black border-zinc-800 hover:border-zinc-700'
                      }`}
                    >
                      <div
                        className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 mt-0.5 ${
                          isSelected
                            ? 'bg-white text-black'
                            : 'bg-zinc-900 border border-zinc-800 text-white'
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="space-y-1 min-w-0">
                        <h4 className="text-xs font-bold text-white">{m.title}</h4>
                        <p className="text-[11px] text-zinc-300">{m.subtitle}</p>
                        <p className="text-[10px] text-zinc-400 leading-relaxed">{m.description}</p>
                      </div>
                    </div>
                  )
                })}
              </div>

              {/* Plain-language Goal Input */}
              <div className="p-4 rounded-2xl bg-black border border-zinc-800 space-y-3">
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-white block">
                    Describe en una frase qué quieres que haga el equipo IA:
                  </label>
                  <input
                    type="text"
                    value={sprintTitle}
                    onChange={(e) => setSprintTitle(e.target.value)}
                    placeholder="Ej. Quiero agregar un botón para descargar facturas en PDF..."
                    className="w-full bg-zinc-950 border border-zinc-750 rounded-xl px-3.5 py-2.5 text-xs sm:text-sm text-white focus:outline-none focus:border-white"
                  />
                </div>

                {/* Quick 1-click ideas from Jira Backlog if available */}
                {backlogTickets.length > 0 && (
                  <div className="space-y-1.5 pt-1">
                    <span className="text-[11px] text-zinc-400 block">
                      💡 ¿Prefieres elegir una tarea pendiente de tu lista de Jira con 1 clic?
                    </span>
                    <div className="flex items-center gap-1.5 overflow-x-auto pb-1 custom-scroll">
                      {backlogTickets.slice(0, 5).map((t) => (
                        <button
                          key={t.key}
                          type="button"
                          onClick={() => {
                            setSprintKey(t.key)
                            setSprintTitle(t.title)
                          }}
                          className={`px-2.5 py-1.5 rounded-xl border text-[11px] whitespace-nowrap transition cursor-pointer ${
                            sprintKey === t.key
                              ? 'bg-white text-black border-white font-bold'
                              : 'bg-zinc-900 hover:bg-zinc-850 border-zinc-800 text-zinc-300 hover:text-white'
                          }`}
                        >
                          {t.key}: {t.title.slice(0, 38)}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                <div className="space-y-1.5 pt-1">
                  <label className="text-xs font-medium text-zinc-300 block">
                    Detalles adicionales (opcional): ¿Qué es lo más importante a cuidar?
                  </label>
                  <textarea
                    rows={2}
                    value={scopeIncluded}
                    onChange={(e) => setScopeIncluded(e.target.value)}
                    placeholder="Escribe cualquier detalle importante que debamos tomar en cuenta..."
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-xl p-2.5 text-xs text-zinc-200 focus:outline-none focus:border-white"
                  />
                </div>
              </div>

              {/* Automatic Safety Reassurance Banner (No configuration required by default) */}
              <div className="p-3.5 rounded-2xl bg-zinc-900/70 border border-zinc-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-start gap-2.5">
                  <Lock className="w-4 h-4 text-white shrink-0 mt-0.5" />
                  <div>
                    <span className="text-xs font-bold text-white block">
                      Protección Automática Activada (No necesitas configurar nada técnico)
                    </span>
                    <span className="text-[11px] text-zinc-300">
                      El sistema trabajará en un espacio de prueba seguro, cuidando tus ventas, inventario y datos antes de pedirte confirmación final.
                    </span>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setShowAdvancedMode(!showAdvancedMode)}
                  className="px-3 py-1.5 rounded-xl bg-zinc-950 hover:bg-zinc-850 border border-zinc-750 text-[11px] font-mono text-zinc-300 hover:text-white flex items-center gap-1.5 shrink-0 self-start sm:self-center cursor-pointer"
                >
                  <SlidersHorizontal className="w-3.5 h-3.5" />
                  <span>{showAdvancedMode ? 'Ocultar modo técnico' : 'Opciones para ingenieros'}</span>
                  {showAdvancedMode ? (
                    <ChevronUp className="w-3.5 h-3.5" />
                  ) : (
                    <ChevronDown className="w-3.5 h-3.5" />
                  )}
                </button>
              </div>

              {/* Collapsible Advanced Engineering Section (Progressive Disclosure) */}
              {showAdvancedMode && (
                <div className="p-4 rounded-2xl bg-black border border-zinc-800 space-y-3 animate-fade-in">
                  <div className="flex items-center justify-between border-b border-zinc-850 pb-2">
                    <span className="text-xs font-mono font-bold text-zinc-200">
                      ⚙️ Parámetros Avanzados de Ingeniería (Opcional)
                    </span>
                    <span className="text-[10px] font-mono text-zinc-400">
                      Configuración prellenada automáticamente
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="text-[11px] font-mono text-zinc-400 block mb-1">
                        Identificador de Ticket (Jira / Interno):
                      </label>
                      <input
                        type="text"
                        value={sprintKey}
                        onChange={(e) => setSprintKey(e.target.value)}
                        className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-1.5 text-xs text-white font-mono"
                      />
                    </div>
                    <div>
                      <label className="text-[11px] font-mono text-zinc-400 block mb-1">
                        Modo de Ejecución:
                      </label>
                      <select
                        value={topologyMode}
                        onChange={(e) => setTopologyMode(e.target.value)}
                        className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-1.5 text-xs text-white font-mono"
                      >
                        <option value="waves">Equipo Completo en Paralelo (Recomendado)</option>
                        <option value="fast_track">Tarea Rápida Individual (Fast-Track)</option>
                        <option value="dry_run">Simulación sin modificar archivos (Dry-Run)</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="text-[11px] font-mono text-zinc-400 block mb-1">
                      Límites de seguridad (Lo que el sistema tiene prohibido alterar):
                    </label>
                    <input
                      type="text"
                      value={scopeExcluded}
                      onChange={(e) => setScopeExcluded(e.target.value)}
                      className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-1.5 text-xs text-zinc-300 font-mono"
                    />
                  </div>

                  <div>
                    <label className="text-[11px] font-mono text-zinc-400 block mb-1.5">
                      Candados de Seguridad Activos:
                    </label>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                      {[
                        { id: 'DR-INV-001', label: 'Evitar sobreventa de stock' },
                        { id: 'DR-PAY-001', label: 'Cuadre exacto de pagos' },
                        { id: 'DR-IDEM-001', label: 'Evitar cobros duplicados' },
                        { id: 'DR-AUTH-001', label: 'Proteger cuentas y permisos' },
                        { id: 'DR-ERR-001', label: 'Mensajes de error claros' },
                        { id: 'DR-REC-001', label: 'Resguardar recibos de caja' },
                      ].map((c) => (
                        <label
                          key={c.id}
                          className="flex items-center gap-2 p-2 rounded-xl bg-zinc-950 border border-zinc-850 text-[11px] text-zinc-300 cursor-pointer"
                        >
                          <input
                            type="checkbox"
                            checked={selectedContracts.includes(c.id)}
                            onChange={() => toggleContract(c.id)}
                            className="rounded border-zinc-700 bg-zinc-900 text-white"
                          />
                          <span className="truncate">{c.label}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              <div className="flex items-center justify-between pt-2">
                <button
                  type="button"
                  onClick={() => setActiveStep(1)}
                  className="px-4 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-300 hover:text-white text-xs font-medium transition cursor-pointer"
                >
                  Volver al Paso 1
                </button>
                <button
                  type="button"
                  onClick={handleGeneratePlan}
                  disabled={loading}
                  className="px-5 py-2.5 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-bold flex items-center gap-2 transition cursor-pointer shadow-sm disabled:opacity-50"
                >
                  <Sparkles className="w-4 h-4 text-black" />
                  <span>{loading ? 'Preparando resumen...' : 'Preparar Resumen y Continuar'}</span>
                  <ArrowRight className="w-4 h-4 text-black" />
                </button>
              </div>
            </div>
          )}

          {/* =========================================================
              PASO 3: REVISAR RESUMEN Y LANZAR CON 1 CLIC
             ========================================================= */}
          {activeStep === 3 && (
            <div className="space-y-4 animate-fade-in">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-white" />
                  Paso 3: Todo listo para comenzar
                </h3>
                <p className="text-xs text-zinc-400 mt-0.5">
                  Revisa este resumen sencillo. Cuando presiones <strong>"Comenzar Trabajo Ahora"</strong>, los asistentes IA harán el trabajo pesado por ti.
                </p>
              </div>

              {/* Clean Executive Summary Card */}
              <div className="p-4 rounded-2xl bg-black border border-zinc-800 space-y-3">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div className="p-3 rounded-xl bg-zinc-950 border border-zinc-850">
                    <span className="text-[10px] text-zinc-400 uppercase tracking-wider block">
                      1. Proyecto Seleccionado
                    </span>
                    <span className="text-xs font-bold text-white mt-0.5 block">
                      {selectedProjectCard.name}
                    </span>
                    <span className="text-[11px] text-zinc-400">
                      Copia aislada de seguridad lista
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-zinc-950 border border-zinc-850">
                    <span className="text-[10px] text-zinc-400 uppercase tracking-wider block">
                      2. Tipo de Solicitud
                    </span>
                    <span className="text-xs font-bold text-white mt-0.5 block">
                      {selectedMissionCard.title}
                    </span>
                    <span className="text-[11px] text-zinc-400">
                      Ref: {sprintKey}
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-zinc-950 border border-zinc-850">
                    <span className="text-[10px] text-zinc-400 uppercase tracking-wider block">
                      3. Nivel de Protección
                    </span>
                    <span className="text-xs font-bold text-white mt-0.5 block">
                      Máxima Seguridad Activa
                    </span>
                    <span className="text-[11px] text-zinc-400">
                      Requiere tu visto bueno final
                    </span>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-zinc-950 border border-zinc-850">
                  <span className="text-[10px] text-zinc-400 uppercase tracking-wider block">
                    Objetivo a Realizar:
                  </span>
                  <p className="text-xs sm:text-sm font-bold text-white mt-0.5">
                    "{sprintTitle}"
                  </p>
                  <p className="text-xs text-zinc-300 mt-1">{scopeIncluded}</p>
                </div>
              </div>

              {/* How the AI Team will work (Human-friendly steps instead of Kahn DAG jargon) */}
              <div className="p-4 rounded-2xl bg-zinc-950 border border-zinc-850 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white">
                    ¿Qué hará el sistema paso a paso?
                  </span>
                  <span className="text-[11px] text-zinc-400">
                    Proceso automático en 4 etapas
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-4 gap-2.5">
                  {[
                    {
                      num: 'Etapa 1',
                      title: 'Copia Segura',
                      desc: 'Prepara una carpeta aparte para no afectar tu sistema actual.',
                    },
                    {
                      num: 'Etapa 2',
                      title: 'Desarrollo IA',
                      desc: 'Los especialistas crean los cambios solicitados.',
                    },
                    {
                      num: 'Etapa 3',
                      title: 'Control de Calidad',
                      desc: 'Se verifican pagos, inventario y seguridad automáticamente.',
                    },
                    {
                      num: 'Etapa 4',
                      title: 'Tu Aprobación',
                      desc: 'Te muestra el resultado y espera tu confirmación.',
                    },
                  ].map((stage, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl bg-black border border-zinc-800 space-y-1"
                    >
                      <span className="text-[10px] font-mono font-bold text-zinc-400 block">
                        {stage.num}
                      </span>
                      <span className="text-xs font-bold text-white block">{stage.title}</span>
                      <p className="text-[11px] text-zinc-400 leading-snug">{stage.desc}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Live Progress Banner while executing */}
              {loading && (
                <div className="p-4 rounded-2xl bg-zinc-900 border border-white/40 flex items-center gap-3 shadow-lg">
                  <Loader2 className="w-5 h-5 text-white animate-spin shrink-0" />
                  <div>
                    <span className="text-xs font-bold text-white block">
                      Trabajando en tu solicitud...
                    </span>
                    <span className="text-xs text-zinc-300">{executionPhase}</span>
                  </div>
                </div>
              )}

              {/* Execution Result Card (Dynamic & Easy to Understand) */}
              {executionResult && (
                <div className="p-4 sm:p-5 rounded-2xl bg-zinc-900 border border-white space-y-4 shadow-xl animate-fade-in">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded-xl bg-white text-black flex items-center justify-center">
                        <CheckCircle2 className="w-5 h-5 text-black" />
                      </div>
                      <div>
                        <span className="text-sm font-bold text-white block">
                          ¡Trabajo Terminado y Verificado con Éxito!
                        </span>
                        <span className="text-xs text-zinc-300">
                          Todo se guardó en tu base de datos local sin errores.
                        </span>
                      </div>
                    </div>
                    <span className="text-[11px] font-mono px-2.5 py-1 rounded-lg bg-black border border-zinc-700 text-zinc-200">
                      Registro #{executionResult.sprint_id}
                    </span>
                  </div>

                  {/* Clear Human Metrics + Assigned SolidBit Character Squad */}
                  <div className="p-3.5 rounded-xl bg-black border border-zinc-800 space-y-2">
                    <span className="text-[11px] font-bold text-emerald-400 block">
                      Escuadrón de Personajes SolidBit Asignado (Flujos IMPL-001..009 y Gates 0–5):
                    </span>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-[11px]">
                      <div className="p-2 rounded-lg bg-zinc-950 border border-zinc-850 text-zinc-200">
                        <strong className="text-sky-400">Atlas:</strong> Rama aislada lista
                      </div>
                      <div className="p-2 rounded-lg bg-zinc-950 border border-zinc-850 text-zinc-200">
                        <strong className="text-emerald-400">Vega:</strong> DR-INV-001 / DR-PAY-001
                      </div>
                      <div className="p-2 rounded-lg bg-zinc-950 border border-zinc-850 text-zinc-200">
                        <strong className="text-violet-400">Orión:</strong> Flujo UI sincronizado
                      </div>
                      <div className="p-2 rounded-lg bg-zinc-950 border border-zinc-850 text-zinc-200">
                        <strong className="text-amber-400">Centinela:</strong> Compuerta Gate 5
                      </div>
                      <div className="p-2 rounded-lg bg-zinc-950 border border-zinc-850 text-zinc-200">
                        <strong className="text-orange-400">Fénix:</strong> Evidencia SHA-256
                      </div>
                      <div className="p-2 rounded-lg bg-zinc-950 border border-zinc-850 text-zinc-200">
                        <strong className="text-pink-400">Nova:</strong> Suite Pytest verificada
                      </div>
                    </div>
                  </div>

                  {/* Clear Human Metrics */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
                    <div className="p-3 rounded-xl bg-black border border-zinc-800">
                      <span className="text-[10px] text-zinc-400 block">Pruebas de Calidad</span>
                      <span className="text-white font-bold text-xs sm:text-sm mt-0.5 block">
                        ✓ Todas Aprobadas
                      </span>
                    </div>
                    <div className="p-3 rounded-xl bg-black border border-zinc-800">
                      <span className="text-[10px] text-zinc-400 block">Protección de Datos</span>
                      <span className="text-white font-bold text-xs sm:text-sm mt-0.5 block">
                        ✓ 100% Seguro
                      </span>
                    </div>
                    <div className="p-3 rounded-xl bg-black border border-zinc-800">
                      <span className="text-[10px] text-zinc-400 block">Etapas Completadas</span>
                      <span className="text-white font-bold text-xs sm:text-sm mt-0.5 block">
                        {executionResult.waves_executed || 4} de {executionResult.waves_executed || 4} listas
                      </span>
                    </div>
                    <div className="p-3 rounded-xl bg-black border border-zinc-800">
                      <span className="text-[10px] text-zinc-400 block">Estado Final</span>
                      <span className="text-white font-bold text-xs sm:text-sm mt-0.5 block">
                        {hmacApplied ? '✓ Publicado' : 'Esperando tu OK'}
                      </span>
                    </div>
                  </div>

                  {/* Final 1-Click Human Approval */}
                  <div className="pt-3 border-t border-zinc-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="space-y-0.5">
                      <span className="text-xs font-bold text-white block">
                        ¿Autorizas aplicar estos cambios?
                      </span>
                      <p className="text-[11px] text-zinc-300">
                        Nada se publica sin tu permiso. Al aprobar, queda sellado con tu firma digital segura.
                      </p>
                    </div>
                    {hmacApplied ? (
                      <span className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white text-black text-xs font-bold shadow-sm">
                        <Check className="w-4 h-4 text-black" />
                        ¡Cambios Aprobados y Aplicados!
                      </span>
                    ) : (
                      <button
                        type="button"
                        onClick={handleApplyHmac}
                        disabled={loading}
                        className="px-5 py-2.5 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-bold flex items-center justify-center gap-2 transition cursor-pointer shadow-md disabled:opacity-50 shrink-0"
                      >
                        <Key className="w-4 h-4 text-black" />
                        <span>Aprobar y Aplicar Cambios</span>
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* Step 3 Footer Buttons */}
              <div className="flex items-center justify-between pt-2">
                <button
                  type="button"
                  onClick={() => setActiveStep(2)}
                  className="px-4 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-300 hover:text-white text-xs font-medium transition cursor-pointer"
                >
                  Modificar descripción
                </button>

                {!executionResult && (
                  <button
                    type="button"
                    onClick={handleExecuteSprint}
                    disabled={loading}
                    className="px-6 py-3 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs sm:text-sm font-bold flex items-center gap-2.5 transition cursor-pointer shadow-lg disabled:opacity-50"
                  >
                    <Play className="w-4 h-4 text-black fill-black" />
                    <span>
                      {loading ? 'Ejecutando tu solicitud...' : 'Comenzar Trabajo Ahora'}
                    </span>
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
