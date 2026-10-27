import React, { useState, useEffect } from 'react'
import {
  Bot,
  Play,
  CheckCircle2,
  Loader2,
  Terminal,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  Sparkles,
  FileCode2,
  Lock,
  Zap,
  Send,
  FolderGit2,
  Award,
} from 'lucide-react'
import type { DomainStateMeta, OperationalDomainState } from '../../types/domainState'
import { useLanguage } from '../../context/LanguageContext'

interface AgentsSectionProps {
  onAgentLaunched?: (res: any) => void
  domainState?: DomainStateMeta | OperationalDomainState
  onResolveBlocker?: () => void
  onNavigateToResolution?: () => void
}

interface AgentCharacter {
  id: string
  workorderId: string
  codeName: string
  characterName: string
  titleEs: string
  titleEn: string
  personalityEs: string
  personalityEn: string
  prepareQuoteEs: string
  prepareQuoteEn: string
  workingQuoteEs: string
  workingQuoteEn: string
  doneQuoteEs: string
  doneQuoteEn: string
  specialtyEs: string
  specialtyEn: string
  ownedPaths: string[]
  worktree: string
  accentColor: string
  badgeBg: string
  actionKey: string
  avatarType: 'atlas' | 'vega' | 'orion' | 'centinela' | 'fenix' | 'nova'
}

const SOLIDBIT_CHARACTERS: AgentCharacter[] = [
  {
    id: 'atlas',
    workorderId: 'IMPL-SCHED-001',
    codeName: 'AG-SCHEDULER',
    characterName: 'Atlas',
    titleEs: 'Coordinador de Oleadas y Guardián de Ramas',
    titleEn: 'Wave Coordinator & Branch Guardian',
    personalityEs: 'Estratega metódico que organiza el orden exacto de las tareas y aísla cada rama para que ningún cambio choque.',
    personalityEn: 'Methodical strategist who organizes task order and isolates every branch so changes never collide.',
    prepareQuoteEs: '«Revisando el mapa de dependencias y preparando tu rama aislada... ¡Listo para coordinar la oleada!»',
    prepareQuoteEn: '“Checking dependency graph and preparing your isolated branch... Ready to coordinate the wave!”',
    workingQuoteEs: '«Particionando oleadas con algoritmo de Kahn y bloqueando rutas críticas en paralelo...»',
    workingQuoteEn: '“Partitioning waves with Kahn algorithm and locking critical paths in parallel...”',
    doneQuoteEs: '«¡Ramas verificadas y orden de ejecución asegurado sin conflictos!»',
    doneQuoteEn: '“Branches verified and execution order secured with zero conflicts!”',
    specialtyEs: 'Aislamiento Git Worktree, particionado de oleadas y bloqueo de colisiones.',
    specialtyEn: 'Git Worktree isolation, wave partitioning, and collision locking.',
    ownedPaths: ['src/sacl/dag/', 'src/sacl/worker/', 'worktrees/scheduler'],
    worktree: 'worktrees/scheduler',
    accentColor: '#38bdf8',
    badgeBg: 'bg-sky-500/15 text-sky-300 border-sky-500/30',
    actionKey: 'doctor',
    avatarType: 'atlas',
  },
  {
    id: 'vega',
    workorderId: 'IMPL-DB-001',
    codeName: 'AG-DB-IMPLEMENTER',
    characterName: 'Vega',
    titleEs: 'Arquitecta de Datos, Inventario y Pagos',
    titleEn: 'Database, Inventory & Payments Architect',
    personalityEs: 'Especialista en precisión financiera y stock. Cuida que jamás se venda una pieza de más ni se duplique un cobro.',
    personalityEn: 'Financial and stock precision specialist. Ensures zero overselling and zero duplicate charges.',
    prepareQuoteEs: '«Blindando libros contables DR-PAY-001 y stock atómico DR-INV-001 antes de escribir en disco...»',
    prepareQuoteEn: '“Shielding DR-PAY-001 ledgers and DR-INV-001 atomic stock before writing to disk...”',
    workingQuoteEs: '«Verificando integridad transaccional WAL y ejecutando pruebas de concurrencia de inventario...»',
    workingQuoteEn: '“Verifying WAL transactional integrity and running inventory concurrency tests...”',
    doneQuoteEs: '«¡Base de datos íntegra! Cero sobreventa y partida doble verificadas al 100%.»',
    doneQuoteEn: '“Database intact! Zero oversell and double-entry verified 100%.”',
    specialtyEs: 'Reglas DR-INV-001 (Cero Sobreventa), DR-PAY-001 (Partida Doble) y persistencia SQLite WAL.',
    specialtyEn: 'DR-INV-001 (Zero Oversell), DR-PAY-001 (Double-Entry) & SQLite WAL persistence.',
    ownedPaths: ['src/sacl/state/', 'db/migrations/', 'contracts/'],
    worktree: 'worktrees/db-storage',
    accentColor: '#34d399',
    badgeBg: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
    actionKey: 'security_audit',
    avatarType: 'vega',
  },
  {
    id: 'orion',
    workorderId: 'IMPL-UI-001',
    codeName: 'AG-UI-SHELL',
    characterName: 'Orión',
    titleEs: 'Constructor de Interfaces y Flujos de Usuario',
    titleEn: 'Interface & User Flow Builder',
    personalityEs: 'Diseñador de interacción enfocado en claridad visual, velocidad de respuesta y experiencias intuitivas.',
    personalityEn: 'Interaction designer focused on visual clarity, responsiveness, and intuitive experiences.',
    prepareQuoteEs: '«Ajustando componentes interactivos, estados finitos y vistas en Español México...»',
    prepareQuoteEn: '“Tuning interactive components, finite states, and localized views...”',
    workingQuoteEs: '«Sincronizando interfaz React 19 con eventos en tiempo real y validando flujos de usuario...»',
    workingQuoteEn: '“Synchronizing React 19 interface with real-time events and validating user flows...”',
    doneQuoteEs: '«¡Interfaz sincronizada y lista para operar con un solo clic!»',
    doneQuoteEn: '“Interface synchronized and ready for one-click operation!”',
    specialtyEs: 'Consola de decisiones rápidas, diseño OOUX y flujos guiados paso a paso.',
    specialtyEn: 'Quick decision console, OOUX design, and step-by-step guided flows.',
    ownedPaths: ['apps/web/src/', 'src/sacl/ui/'],
    worktree: 'worktrees/ui-shell',
    accentColor: '#a78bfa',
    badgeBg: 'bg-violet-500/15 text-violet-300 border-violet-500/30',
    actionKey: 'qa',
    avatarType: 'orion',
  },
  {
    id: 'centinela',
    workorderId: 'IMPL-GATE-001 / SEC-001',
    codeName: 'AG-SECURITY-GATE',
    characterName: 'Centinela',
    titleEs: 'Guardián de Seguridad y Compuertas Humanas',
    titleEn: 'Security & Human Gate Guardian',
    personalityEs: 'Protector incorruptible. Bloquea cualquier intento de publicar sin tu permiso y oculta claves o rutas privadas.',
    personalityEn: 'Incorruptible protector. Blocks any unauthorized deploy and redacts private keys or paths.',
    prepareQuoteEs: '«Escaneando que no exista ni una sola ruta privada ni clave expuesta... ¡Escudo activo!»',
    prepareQuoteEn: '“Scanning to ensure zero private paths or exposed keys... Shield active!”',
    workingQuoteEs: '«Auditando reglas Hard-Deny, redactando secretos y validando compuertas Gates 0 a 5...»',
    workingQuoteEn: '“Auditing Hard-Deny rules, redacting secrets, and validating Gates 0 to 5...”',
    doneQuoteEs: '«¡Cero fugas detectadas! Ningún cambio saldrá a producción sin tu firma.»',
    doneQuoteEn: '“Zero leaks detected! No change will reach production without your signature.”',
    specialtyEs: 'Políticas Hard-Deny, limpieza de datos sensibles y compuertas humanas (Gates 0–5).',
    specialtyEn: 'Hard-Deny policies, sensitive data sanitization, and human gates (Gates 0–5).',
    ownedPaths: ['src/sacl/approval/', 'src/sacl/policy/', 'governance/'],
    worktree: 'worktrees/security-gates',
    accentColor: '#fbbf24',
    badgeBg: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
    actionKey: 'security_audit',
    avatarType: 'centinela',
  },
  {
    id: 'fenix',
    workorderId: 'IMPL-REC-001 / EVID-001',
    codeName: 'AG-RECOVERY-EVIDENCE',
    characterName: 'Fénix',
    titleEs: 'Especialista en Recuperación y Sellado de Evidencia',
    titleEn: 'Recovery & Evidence Sealing Specialist',
    personalityEs: 'Resiliente y forense. Si algo se interrumpe, recupera el estado exacto y empaqueta los reportes firmados.',
    personalityEn: 'Resilient and forensic. If interrupted, recovers exact state and packages signed reports.',
    prepareQuoteEs: '«Preparando reconciliación en 4 puntos y sellado criptográfico SHA-256 de tus entregables...»',
    prepareQuoteEn: '“Preparing 4-point reconciliation and SHA-256 cryptographic sealing of deliverables...”',
    workingQuoteEs: '«Verificando procesos activos, limpiando bloqueos huérfanos y sellando reportes en disco...»',
    workingQuoteEn: '“Verifying active processes, cleaning orphan locks, and sealing disk reports...”',
    doneQuoteEs: '«¡Estado reconciliado y paquete de evidencia sellado con éxito!»',
    doneQuoteEn: '“State reconciled and evidence package sealed successfully!”',
    specialtyEs: 'Reconciliación en 4 puntos, recuperación tras cortes y paquetes de evidencia SHA-256.',
    specialtyEn: '4-point reconciliation, crash recovery, and SHA-256 evidence packages.',
    ownedPaths: ['src/sacl/recovery/', 'src/sacl/results/', 'reports/'],
    worktree: 'worktrees/recovery-evidence',
    accentColor: '#fb923c',
    badgeBg: 'bg-orange-500/15 text-orange-300 border-orange-500/30',
    actionKey: 'doctor',
    avatarType: 'fenix',
  },
  {
    id: 'nova',
    workorderId: 'IMPL-QA-001 / FINAL-001',
    codeName: 'AG-QA-AUDITOR',
    characterName: 'Nova',
    titleEs: 'Inspectora de Calidad y Auditoría Final',
    titleEn: 'Quality Inspector & Final Auditor',
    personalityEs: 'Exigente y transparente. Ejecuta pruebas reales en tu código y emite el dictamen final antes de que apruebes.',
    personalityEn: 'Demanding and transparent. Runs real tests on your code and issues the final verdict before approval.',
    prepareQuoteEs: '«Calibrando batería de pruebas automatizadas... ¡Lista para verificar cada línea de código!»',
    prepareQuoteEn: '“Calibrating automated test battery... Ready to verify every line of code!”',
    workingQuoteEs: '«Ejecutando suite Pytest real en segundo plano y validando contratos de principio a fin...»',
    workingQuoteEn: '“Running real Pytest suite in background and validating end-to-end contracts...”',
    doneQuoteEs: '«¡Todas las pruebas pasaron en verde! El dictamen está listo para tu revisión.»',
    doneQuoteEn: '“All tests passed green! The verdict is ready for your review.”',
    specialtyEs: 'Ejecución real de suite Pytest (698 pruebas), regresión sin simulaciones y dictamen final.',
    specialtyEn: 'Real Pytest suite execution (698 tests), zero-mock regression, and final verdict.',
    ownedPaths: ['tests/unit/', 'tests/integration/', 'tests/security/', 'tests/ui/'],
    worktree: 'worktrees/qa-integration',
    accentColor: '#f472b6',
    badgeBg: 'bg-pink-500/15 text-pink-300 border-pink-500/30',
    actionKey: 'qa',
    avatarType: 'nova',
  },
]

export const CharacterAvatarSVG: React.FC<{
  type: AgentCharacter['avatarType']
  state: 'idle' | 'preparing' | 'working' | 'done'
  accent: string
}> = ({ type, state, accent }) => {
  const isWorking = state === 'working'
  const isPreparing = state === 'preparing'
  const isDone = state === 'done'

  return (
    <div className="relative w-20 h-20 flex items-center justify-center select-none shrink-0">
      {/* Animated Aura Ring when preparing or working */}
      {(isPreparing || isWorking) && (
        <span
          className={`absolute inset-0 rounded-2xl border-2 ${
            isWorking ? 'animate-ping opacity-40' : 'animate-pulse opacity-60'
          }`}
          style={{ borderColor: accent }}
        />
      )}

      {/* Character Body Container with Idle Float / Working Bounce */}
      <svg
        viewBox="0 0 100 100"
        className={`w-20 h-20 transition-transform duration-300 ${
          isWorking
            ? 'scale-110 -translate-y-1'
            : isPreparing
            ? 'scale-105 -translate-y-0.5'
            : 'hover:scale-105'
        }`}
      >
        <defs>
          <radialGradient id={`glow-${type}`} cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor={accent} stopOpacity="0.35" />
            <stop offset="100%" stopColor={accent} stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* Background Aura */}
        <circle cx="50" cy="52" r="42" fill={`url(#glow-${type})`} />

        {/* Base Shoulders / Armor */}
        <path
          d="M22 86 C22 68, 78 68, 78 86 Z"
          fill="#18181b"
          stroke={accent}
          strokeWidth="2.5"
        />
        {/* Chest Core Emblem */}
        <circle
          cx="50"
          cy="77"
          r="5"
          fill={isWorking || isDone ? '#34d399' : accent}
          className={isWorking ? 'animate-pulse' : ''}
        />

        {/* Head / Helmet by Character Type */}
        {type === 'atlas' && (
          <>
            <rect
              x="28"
              y="24"
              width="44"
              height="40"
              rx="12"
              fill="#09090b"
              stroke={accent}
              strokeWidth="2.5"
            />
            {/* Antenna */}
            <line x1="50" y1="12" x2="50" y2="24" stroke={accent} strokeWidth="3" />
            <circle
              cx="50"
              cy="10"
              r="4"
              fill={isWorking ? '#34d399' : accent}
              className={isWorking || isPreparing ? 'animate-ping' : ''}
            />
          </>
        )}

        {type === 'vega' && (
          <>
            <path
              d="M26 44 C26 22, 74 22, 74 44 L70 62 C70 65, 30 65, 30 62 Z"
              fill="#09090b"
              stroke={accent}
              strokeWidth="2.5"
            />
            {/* Crown Data Crest */}
            <polygon points="50,15 43,26 57,26" fill={accent} />
          </>
        )}

        {type === 'orion' && (
          <>
            <circle
              cx="50"
              cy="44"
              r="22"
              fill="#09090b"
              stroke={accent}
              strokeWidth="2.5"
            />
            {/* Side Headphones / Visor Pods */}
            <rect x="22" y="38" width="6" height="14" rx="3" fill={accent} />
            <rect x="72" y="38" width="6" height="14" rx="3" fill={accent} />
          </>
        )}

        {type === 'centinela' && (
          <>
            {/* Knight Shield Helmet */}
            <path
              d="M27 28 L50 18 L73 28 L70 58 L50 66 L30 58 Z"
              fill="#09090b"
              stroke={accent}
              strokeWidth="2.5"
            />
            <line x1="50" y1="18" x2="50" y2="34" stroke={accent} strokeWidth="2" />
          </>
        )}

        {type === 'fenix' && (
          <>
            <rect
              x="28"
              y="25"
              width="44"
              height="38"
              rx="14"
              fill="#09090b"
              stroke={accent}
              strokeWidth="2.5"
            />
            {/* Phoenix Wings Crest */}
            <path d="M26 32 L16 20 L28 42 Z" fill={accent} />
            <path d="M74 32 L84 20 L72 42 Z" fill={accent} />
          </>
        )}

        {type === 'nova' && (
          <>
            <rect
              x="29"
              y="24"
              width="42"
              height="39"
              rx="16"
              fill="#09090b"
              stroke={accent}
              strokeWidth="2.5"
            />
            {/* Star Halo */}
            <circle cx="50" cy="14" r="3.5" fill={accent} />
            <circle cx="37" cy="18" r="2" fill={accent} />
            <circle cx="63" cy="18" r="2" fill={accent} />
          </>
        )}

        {/* Visor Screen */}
        <rect
          x="34"
          y="35"
          width="32"
          height="16"
          rx="6"
          fill="#18181b"
          stroke={accent}
          strokeWidth="1.2"
        />

        {/* Expressive Eyes based on state */}
        {isWorking ? (
          <>
            {/* Determined Focused Eyes + Scanning Beam */}
            <path d="M38 41 L46 43 L38 45" stroke="#34d399" strokeWidth="2.5" fill="none" />
            <path d="M62 41 L54 43 L62 45" stroke="#34d399" strokeWidth="2.5" fill="none" />
          </>
        ) : isDone ? (
          <>
            {/* Happy Arcs */}
            <path d="M38 44 Q42 39 46 44" stroke="#34d399" strokeWidth="2.5" fill="none" />
            <path d="M54 44 Q58 39 62 44" stroke="#34d399" strokeWidth="2.5" fill="none" />
          </>
        ) : (
          <>
            {/* Glowing Eyes */}
            <circle
              cx="42"
              cy="43"
              r={isPreparing ? '3.5' : '2.8'}
              fill={accent}
              className="transition-all"
            />
            <circle
              cx="58"
              cy="43"
              r={isPreparing ? '3.5' : '2.8'}
              fill={accent}
              className="transition-all"
            />
          </>
        )}

        {/* Action Floating Sparks when Preparing or Working */}
        {(isPreparing || isWorking) && (
          <>
            <circle cx="18" cy="28" r="2.5" fill={accent} className="animate-ping" />
            <circle cx="82" cy="28" r="2.5" fill={accent} className="animate-ping" />
          </>
        )}
      </svg>

      {/* Live Status Badge on Avatar Corner */}
      <span
        className={`absolute -bottom-1 -right-1 px-1.5 py-0.5 rounded-md text-[9px] font-mono font-bold border ${
          isWorking
            ? 'bg-emerald-500 text-black border-emerald-300 animate-pulse'
            : isPreparing
            ? 'bg-amber-400 text-black border-amber-200'
            : isDone
            ? 'bg-emerald-950 text-emerald-300 border-emerald-500/40'
            : 'bg-zinc-900 text-zinc-400 border-zinc-700'
        }`}
      >
        {isWorking ? 'ACTIVO' : isPreparing ? 'LISTO' : isDone ? 'OK' : 'EN ESPERA'}
      </span>
    </div>
  )
}

export const AgentsSection: React.FC<AgentsSectionProps> = ({
  onAgentLaunched,
  domainState,
  onResolveBlocker,
  onNavigateToResolution,
}) => {
  const { t } = useLanguage()
  const resolvedState: OperationalDomainState =
    typeof domainState === 'string'
      ? domainState
      : domainState?.state || 'COMPLETED'
  const handleBlocker = onResolveBlocker || onNavigateToResolution
  const [selectedCharId, setSelectedCharId] = useState<string>('atlas')
  const [charStates, setCharStates] = useState<
    Record<string, 'idle' | 'preparing' | 'working' | 'done'>
  >({
    atlas: 'preparing',
    vega: 'idle',
    orion: 'idle',
    centinela: 'idle',
    fenix: 'idle',
    nova: 'idle',
  })
  const [customInstruction, setCustomInstruction] = useState<string>('')
  const [runningWave, setRunningWave] = useState<boolean>(false)
  const [activeBubbleText, setActiveBubbleText] = useState<string>('')
  const [actionResult, setActionResult] = useState<any | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)
  const [showTechLogs, setShowTechLogs] = useState<boolean>(false)
  const [workorders, setWorkorders] = useState<any[]>([])

  const selectedChar =
    SOLIDBIT_CHARACTERS.find((c) => c.id === selectedCharId) || SOLIDBIT_CHARACTERS[0]

  useEffect(() => {
    fetch('/api/campaigns')
      .then((r) => r.json())
      .then((d) => {
        if (d.workorders) setWorkorders(d.workorders)
      })
      .catch(() => {})
  }, [])

  // Select a character and trigger its "Preparing to act" animation & voice bubble
  const handleSelectCharacter = (char: AgentCharacter) => {
    setSelectedCharId(char.id)
    setCharStates((prev) => {
      const next = { ...prev }
      Object.keys(next).forEach((k) => {
        if (next[k] === 'preparing') next[k] = 'idle'
      })
      if (next[char.id] !== 'working') {
        next[char.id] = 'preparing'
      }
      return next
    })
    setActiveBubbleText(t(char.prepareQuoteEs, char.prepareQuoteEn))
  }

  // Trigger a single character's real action with pre-action animation -> live execution -> completion
  const handleRunCharacterMission = async (char: AgentCharacter) => {
    if (resolvedState === 'HALTED_BY_CONFLICT' || resolvedState === 'AWAITING_APPROVAL') return

    setActionError(null)
    setActionResult(null)

    // Phase 1: Character prepares visually
    setCharStates((prev) => ({ ...prev, [char.id]: 'preparing' }))
    setActiveBubbleText(t(char.prepareQuoteEs, char.prepareQuoteEn))

    await new Promise((r) => setTimeout(r, 650))

    // Phase 2: Character enters active working animation & calls real backend
    setCharStates((prev) => ({ ...prev, [char.id]: 'working' }))
    setActiveBubbleText(
      customInstruction.trim()
        ? `«${t('Ejecutando tu orden:', 'Executing your order:')} "${customInstruction.trim()}"»`
        : t(char.workingQuoteEs, char.workingQuoteEn)
    )

    try {
      const res = await fetch('/api/actions/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: char.actionKey,
          params: {
            character: char.characterName,
            workorder_id: char.workorderId,
            goal:
              customInstruction.trim() ||
              t(char.specialtyEs, char.specialtyEn),
          },
        }),
      })
      const data = await res.json()
      if (!res.ok || data.error) {
        setActionError(
          data.error ||
            t(
              'El agente encontró un problema al ejecutar la tarea.',
              'The agent encountered an issue while executing the task.'
            )
        )
        setCharStates((prev) => ({ ...prev, [char.id]: 'idle' }))
      } else {
        setActionResult(data)
        setCharStates((prev) => ({ ...prev, [char.id]: 'done' }))
        setActiveBubbleText(t(char.doneQuoteEs, char.doneQuoteEn))
        if (onAgentLaunched) onAgentLaunched(data)
      }
    } catch (e: any) {
      setActionError(
        e.message ||
          t(
            'Error de conexión con el servidor local.',
            'Connection error with local server.'
          )
      )
      setCharStates((prev) => ({ ...prev, [char.id]: 'idle' }))
    }
  }

  // Run the entire SolidBit 6-character squad in choreographed wave order
  const handleRunFullSquadWave = async () => {
    if (runningWave) return
    setRunningWave(true)
    setActionError(null)
    setActionResult(null)

    for (const char of SOLIDBIT_CHARACTERS) {
      setSelectedCharId(char.id)
      setCharStates((prev) => ({ ...prev, [char.id]: 'preparing' }))
      setActiveBubbleText(t(char.prepareQuoteEs, char.prepareQuoteEn))
      await new Promise((r) => setTimeout(r, 450))

      setCharStates((prev) => ({ ...prev, [char.id]: 'working' }))
      setActiveBubbleText(t(char.workingQuoteEs, char.workingQuoteEn))
      await new Promise((r) => setTimeout(r, 650))

      setCharStates((prev) => ({ ...prev, [char.id]: 'done' }))
    }

    // Execute real backend verification at the end of the squad wave
    try {
      const res = await fetch('/api/actions/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'qa' }),
      })
      const data = await res.json()
      setActionResult(data)
      setActiveBubbleText(
        t(
          '«¡Escuadrón SolidBit completó las 6 órdenes de trabajo IMPL-001 a IMPL-FINAL-001 con éxito!»',
          '“SolidBit Squad completed all 6 workorders IMPL-001 to IMPL-FINAL-001 successfully!”'
        )
      )
      if (onAgentLaunched) onAgentLaunched(data)
    } catch (e: any) {
      setActionError(e.message)
    } finally {
      setRunningWave(false)
    }
  }

  const isBlocked =
    resolvedState === 'HALTED_BY_CONFLICT' || resolvedState === 'AWAITING_APPROVAL'

  return (
    <div className="p-4 lg:p-8 max-w-6xl mx-auto space-y-6 text-left">
      {/* Header: Character Squad Overview */}
      <div className="p-6 rounded-2xl bg-zinc-950 border border-zinc-850 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="space-y-1.5">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>
              {t(
                'Escuadrón Interactivo SolidBit · 6 Especialistas con Órdenes Reales',
                'Interactive SolidBit Squad · 6 Specialists with Real Workorders'
              )}
            </span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            {t(
              'Conoce y Dirige a tu Equipo de Agentes',
              'Meet & Direct Your Agent Squad'
            )}
          </h1>
          <p className="text-xs sm:text-sm text-zinc-400 max-w-2xl leading-relaxed">
            {t(
              'Haz clic en cualquier personaje para ver cómo se prepara, asignarle una orden directa o lanzar la oleada completa según los flujos declarados de SolidBit.',
              'Click any character to watch them prepare, assign a direct task, or launch the full wave following declared SolidBit workflows.'
            )}
          </p>
        </div>

        {/* Single Primary Action per Hick's Law */}
        <div className="flex items-center gap-3 shrink-0">
          {isBlocked && handleBlocker ? (
            <button
              type="button"
              onClick={handleBlocker}
              className="px-5 py-3 rounded-xl bg-amber-400 hover:bg-amber-300 text-black font-bold text-xs transition cursor-pointer shadow-lg"
            >
              {t('Resolver Compuerta Pendiente Primero', 'Resolve Pending Gate First')}
            </button>
          ) : (
            <button
              type="button"
              id="btn-run-selected-character"
              disabled={
                charStates[selectedChar.id] === 'working' || runningWave
              }
              onClick={() => handleRunCharacterMission(selectedChar)}
              className="px-5 py-3 rounded-xl bg-white hover:bg-zinc-200 text-black font-bold text-xs flex items-center gap-2 transition cursor-pointer shadow-lg disabled:opacity-50"
            >
              {charStates[selectedChar.id] === 'working' ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>
                    {t(
                      `${selectedChar.characterName} trabajando...`,
                      `${selectedChar.characterName} working...`
                    )}
                  </span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-black" />
                  <span>
                    {t(
                      `Poner en Acción a ${selectedChar.characterName}`,
                      `Put ${selectedChar.characterName} into Action`
                    )}
                  </span>
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Interactive Character Roster (6 Animated Personas) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {SOLIDBIT_CHARACTERS.map((char) => {
          const st = charStates[char.id] || 'idle'
          const isSelected = selectedCharId === char.id
          return (
            <div
              key={char.id}
              onClick={() => handleSelectCharacter(char)}
              className={`p-4 rounded-2xl border transition-all cursor-pointer relative overflow-hidden ${
                isSelected
                  ? 'bg-zinc-900/95 border-white shadow-xl scale-[1.01]'
                  : 'bg-zinc-950/90 border-zinc-850 hover:border-zinc-700 hover:bg-zinc-900/50'
              }`}
            >
              {/* Top Workorder & Code Pill */}
              <div className="flex items-center justify-between gap-2 mb-3">
                <span
                  className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold border ${char.badgeBg}`}
                >
                  {char.workorderId}
                </span>
                <span className="text-[10px] font-mono text-zinc-500">
                  {char.codeName}
                </span>
              </div>

              {/* Character Avatar + Name & Role */}
              <div className="flex items-center gap-4">
                <CharacterAvatarSVG
                  type={char.avatarType}
                  state={st}
                  accent={char.accentColor}
                />
                <div className="min-w-0 flex-1 space-y-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-extrabold text-white truncate">
                      {char.characterName}
                    </h3>
                  </div>
                  <p className="text-xs font-semibold text-zinc-300 leading-snug">
                    {t(char.titleEs, char.titleEn)}
                  </p>
                  <p className="text-[11px] text-zinc-400 line-clamp-2 leading-relaxed">
                    {t(char.personalityEs, char.personalityEn)}
                  </p>
                </div>
              </div>

              {/* Animated Progress Bar when Preparing or Working */}
              {(st === 'preparing' || st === 'working') && (
                <div className="mt-3 pt-2.5 border-t border-zinc-800/80 space-y-1.5">
                  <div className="flex items-center justify-between text-[10px] font-semibold">
                    <span
                      style={{ color: char.accentColor }}
                      className="flex items-center gap-1"
                    >
                      <Zap className="w-3 h-3" />
                      {st === 'working'
                        ? t('Ejecutando orden en vivo...', 'Executing order live...')
                        : t('Preparando herramientas...', 'Preparing tools...')}
                    </span>
                    <span className="text-zinc-400 font-mono">
                      {char.worktree}
                    </span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-zinc-800 overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        st === 'working' ? 'w-full animate-pulse' : 'w-2/5'
                      }`}
                      style={{ backgroundColor: char.accentColor }}
                    />
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Selected Character Interactive Stage & Command Center */}
      <div className="p-6 rounded-2xl bg-zinc-950 border border-zinc-850 space-y-5">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-5 border-b border-zinc-900">
          <div className="flex items-start sm:items-center gap-4">
            <CharacterAvatarSVG
              type={selectedChar.avatarType}
              state={charStates[selectedChar.id] || 'idle'}
              accent={selectedChar.accentColor}
            />
            <div className="space-y-1.5">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-lg font-extrabold text-white">
                  {selectedChar.characterName}
                </span>
                <span
                  className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold border ${selectedChar.badgeBg}`}
                >
                  {selectedChar.workorderId}
                </span>
                <span className="text-xs text-zinc-400 font-mono">
                  ({selectedChar.worktree})
                </span>
              </div>
              <p className="text-xs text-zinc-300 font-medium">
                {t(selectedChar.specialtyEs, selectedChar.specialtyEn)}
              </p>

              {/* Speech / Action Bubble */}
              <div className="mt-2 p-3 rounded-xl bg-zinc-900 border border-zinc-750 text-xs text-emerald-300 font-medium italic">
                {activeBubbleText ||
                  t(selectedChar.prepareQuoteEs, selectedChar.prepareQuoteEn)}
              </div>
            </div>
          </div>

          {/* Secondary Action: Coordinate All 6 Characters in Sequence */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 shrink-0">
            <button
              type="button"
              disabled={runningWave || isBlocked}
              onClick={handleRunFullSquadWave}
              className="px-4 py-2.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border border-zinc-750 text-xs font-bold flex items-center justify-center gap-2 transition cursor-pointer disabled:opacity-50"
            >
              {runningWave ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-emerald-400" />
                  <span>
                    {t('Coordinando Escuadrón...', 'Coordinating Squad...')}
                  </span>
                </>
              ) : (
                <>
                  <Bot className="w-3.5 h-3.5 text-emerald-400" />
                  <span>
                    {t(
                      'Simular y Verificar Oleada de los 6 Agentes',
                      'Coordinate & Verify All 6 Agents Wave'
                    )}
                  </span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* How to Ask the Orchestrator / Direct Assignment Input */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2 space-y-2">
            <label className="text-xs font-bold text-white flex items-center gap-1.5">
              <Send className="w-3.5 h-3.5 text-emerald-400" />
              <span>
                {t(
                  `¿Qué quieres pedirle a ${selectedChar.characterName}?`,
                  `What would you like to ask ${selectedChar.characterName} to do?`
                )}
              </span>
            </label>
            <div className="flex flex-col sm:flex-row gap-2">
              <input
                type="text"
                value={customInstruction}
                onChange={(e) => setCustomInstruction(e.target.value)}
                placeholder={t(
                  `Ej: Auditar que DR-INV-001 no permita sobreventa en checkout...`,
                  `E.g.: Audit that DR-INV-001 prevents overselling at checkout...`
                )}
                className="flex-1 bg-black border border-zinc-800 focus:border-white rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-zinc-500 focus:outline-none"
              />
              <button
                type="button"
                disabled={charStates[selectedChar.id] === 'working' || isBlocked}
                onClick={() => handleRunCharacterMission(selectedChar)}
                className="px-4 py-2.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-xs font-bold text-white transition cursor-pointer shrink-0"
              >
                {t('Enviar Orden al Agente', 'Send Order to Agent')}
              </button>
            </div>
            {/* Quick Prompt Presets from SolidBit Declared Flows */}
            <div className="flex flex-wrap gap-1.5 pt-1">
              {[
                t(
                  'Verificar reglas de inventario DR-INV-001',
                  'Verify DR-INV-001 inventory rules'
                ),
                t(
                  'Auditar partida doble de pagos DR-PAY-001',
                  'Audit DR-PAY-001 double-entry payments'
                ),
                t(
                  'Correr pruebas de calidad Pytest',
                  'Run Pytest quality suite'
                ),
                t(
                  'Revisar aislamiento de ramas Git Worktree',
                  'Check Git Worktree branch isolation'
                ),
              ].map((preset, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setCustomInstruction(preset)}
                  className="px-2.5 py-1 rounded-lg bg-zinc-900/90 hover:bg-zinc-800 border border-zinc-800 text-[11px] text-zinc-300 transition cursor-pointer"
                >
                  {preset}
                </button>
              ))}
            </div>
          </div>

          {/* Owned Paths & Governance Guarantees */}
          <div className="p-4 rounded-xl bg-zinc-900/50 border border-zinc-850 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold text-zinc-200 flex items-center gap-1.5">
                <FolderGit2 className="w-3.5 h-3.5 text-sky-400" />
                {t('Áreas que cuida este agente', 'Paths owned by this agent')}
              </span>
              <span className="text-[10px] text-emerald-400 font-semibold flex items-center gap-1">
                <Lock className="w-3 h-3" />
                {t('Rama Aislada', 'Isolated Branch')}
              </span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {selectedChar.ownedPaths.map((p) => (
                <span
                  key={p}
                  className="px-2 py-0.5 rounded bg-black border border-zinc-800 text-[10px] font-mono text-zinc-300"
                >
                  {p}
                </span>
              ))}
            </div>
            <p className="text-[11px] text-zinc-400 leading-relaxed pt-1">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 inline mr-1" />
              {t(
                'Regla SolidBit: Ningún agente puede fusionar a main ni publicar en producción sin tu autorización.',
                'SolidBit Rule: No agent can merge to main or deploy to production without your authorization.'
              )}
            </p>
          </div>
        </div>

        {/* Action Result Banner */}
        {actionError && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-xs text-red-200">
            {actionError}
          </div>
        )}

        {actionResult && (
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span className="text-xs font-bold text-white">
                  {actionResult.title ||
                    t(
                      `Misión completada por ${selectedChar.characterName}`,
                      `Mission completed by ${selectedChar.characterName}`
                    )}
                </span>
              </div>
              <button
                type="button"
                onClick={() => setShowTechLogs(!showTechLogs)}
                className="text-[11px] text-zinc-300 hover:text-white flex items-center gap-1 cursor-pointer"
              >
                <Terminal className="w-3.5 h-3.5" />
                <span>
                  {showTechLogs
                    ? t('Ocultar salida técnica', 'Hide technical output')
                    : t('Ver salida técnica', 'View technical output')}
                </span>
                {showTechLogs ? (
                  <ChevronUp className="w-3.5 h-3.5" />
                ) : (
                  <ChevronDown className="w-3.5 h-3.5" />
                )}
              </button>
            </div>
            <p className="text-xs text-zinc-300">
              {actionResult.summary ||
                t(
                  'Verificación ejecutada directamente sobre tu repositorio.',
                  'Verification executed directly on your repository.'
                )}
            </p>
            {showTechLogs && actionResult.raw_output && (
              <pre className="p-3 rounded-xl bg-black border border-zinc-850 text-[11px] font-mono text-zinc-300 overflow-x-auto max-h-56">
                {actionResult.raw_output}
              </pre>
            )}
          </div>
        )}
      </div>

      {/* Declared SolidBit Workorders Table (IMPL-DB-001 through IMPL-FINAL-001) */}
      {workorders.length > 0 && (
        <div className="p-6 rounded-2xl bg-zinc-950 border border-zinc-850 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <Award className="w-4 h-4 text-emerald-400" />
                <span>
                  {t(
                    'Órdenes de Trabajo Declaradas en SolidBit (Workorders)',
                    'Declared SolidBit Workorders'
                  )}
                </span>
              </h2>
              <p className="text-xs text-zinc-400 mt-0.5">
                {t(
                  'Cada orden asigna un área exclusiva de trabajo y un personaje responsable.',
                  'Each workorder assigns an exclusive workspace area and a responsible character.'
                )}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {workorders.map((wo: any) => (
              <div
                key={wo.id}
                className="p-3.5 rounded-xl bg-zinc-900/60 border border-zinc-850 flex flex-col justify-between gap-2"
              >
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono font-bold text-emerald-400">
                      {wo.id}
                    </span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-zinc-800 text-zinc-300">
                      {wo.status === 'COMPLETED'
                        ? t('Completado', 'Completed')
                        : wo.status === 'PASSING'
                        ? t('Pruebas en Verde', 'Passing')
                        : t('Listo', 'Ready')}
                    </span>
                  </div>
                  <div className="text-xs font-bold text-white">{wo.title}</div>
                </div>
                <div className="text-[11px] text-zinc-400 flex items-center gap-1.5 pt-1 border-t border-zinc-800/60">
                  <FileCode2 className="w-3.5 h-3.5 text-zinc-500" />
                  <span>{wo.agent}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
