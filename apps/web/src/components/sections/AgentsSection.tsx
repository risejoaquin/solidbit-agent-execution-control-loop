import React, { useState } from 'react'
import {
  Bot,
  Play,
  CheckCircle2,
  Loader2,
  Terminal,
  ShieldCheck,
  Zap,
  Send,
  Sparkles,
  GitCommit,
  Layers,
} from 'lucide-react'
import type { DomainStateMeta, OperationalDomainState } from '../../types/domainState'
import { useLanguage } from '../../context/LanguageContext'
import { StructuredPayloadViewer } from '../StructuredPayloadViewer'

interface AgentsSectionProps {
  onAgentLaunched?: (res: any) => void
  domainState?: DomainStateMeta | OperationalDomainState
  onResolveBlocker?: () => void
  onNavigateToResolution?: () => void
}

interface RobotAgent {
  id: string
  name: string
  phaseNumber: number
  phaseTitle: string
  diagramRole: string
  specialty: string
  worktree: string
  accentColor: string
  badgeBg: string
  actionKey: string
  presets: string[]
}

const ROBOT_AGENTS: RobotAgent[] = [
  {
    id: 'atlas',
    name: 'Atlas',
    phaseNumber: 1,
    phaseTitle: 'Agente Fase 1 · Diseño',
    diagramRole: 'Diseñar sprint con chat o métodos establecidos de lo que se quiere hacer',
    specialty: 'Planificación de sprint, particionado de oleadas y grafo DAG.',
    worktree: 'worktrees/scheduler',
    accentColor: '#38bdf8',
    badgeBg: 'bg-sky-500/15 text-sky-300 border-sky-500/30',
    actionKey: 'doctor',
    presets: [
      'Refactorizar invariantes de pago y stock con contratos DR-INV-001',
      'Diseñar arquitectura de microservicios para inventario',
      'Verificar consistencia del grafo DAG sin colisiones',
    ],
  },
  {
    id: 'vega',
    name: 'Vega',
    phaseNumber: 2,
    phaseTitle: 'Agente Fase 2 · Implementación',
    diagramRole: 'Implementa lo decidido y muestra los resultados de código',
    specialty: 'Escritura de código en worktree aislado, Pytest unitarios y contratos.',
    worktree: 'worktrees/db_implementer',
    accentColor: '#34d399',
    badgeBg: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
    actionKey: 'test',
    presets: [
      'Ejecutar suite Pytest y verificar contratos DR-INV-001 en verde',
      'Implementar bloqueo atómico de inventario con SELECT FOR UPDATE',
      'Comprobar idempotencia en pasarela de pagos',
    ],
  },
  {
    id: 'nova',
    name: 'Nova',
    phaseNumber: 3,
    phaseTitle: 'Agente Fase 3 · Despliegue',
    diagramRole: 'Sube los cambios a Git y libera el entorno de trabajo',
    specialty: 'Commit atómico, push a rama remota, liberación de worktree y cierre.',
    worktree: 'worktrees/integration',
    accentColor: '#c084fc',
    badgeBg: 'bg-purple-500/15 text-purple-300 border-purple-500/30',
    actionKey: 'release_worktree',
    presets: [
      'Integrar cambios en rama principal y podar worktrees temporales',
      'Generar reporte criptográfico de auditoría SQLite WAL',
      'Verificar hash de commit y estado final de producción',
    ],
  },
]

export const AgentsSection: React.FC<AgentsSectionProps> = ({
  onAgentLaunched,
  domainState,
  onNavigateToResolution,
}) => {
  const { t } = useLanguage()
  const [selectedAgentId, setSelectedAgentId] = useState<string>('atlas')
  const [agentStates, setAgentStates] = useState<Record<string, 'idle' | 'working' | 'done'>>({
    atlas: 'idle',
    vega: 'idle',
    nova: 'idle',
  })
  const [customOrder, setCustomOrder] = useState<string>('')
  const [actionResult, setActionResult] = useState<any | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  const selectedAgent = ROBOT_AGENTS.find((a) => a.id === selectedAgentId) || ROBOT_AGENTS[0]

  const handleRunAgentOrder = async (agent: RobotAgent, orderText?: string) => {
    const textToRun = orderText || customOrder.trim() || agent.presets[0]
    setActionError(null)
    setActionResult(null)

    setAgentStates((prev) => ({ ...prev, [agent.id]: 'working' }))

    try {
      const res = await fetch('/api/actions/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: agent.actionKey,
          params: {
            character: agent.name,
            goal: textToRun,
            worktree: agent.worktree,
          },
        }),
      })
      const data = await res.json()
      if (!res.ok || data.error) {
        setActionError(data.error || 'Error al ejecutar la orden con el agente.')
        setAgentStates((prev) => ({ ...prev, [agent.id]: 'idle' }))
      } else {
        setActionResult(data)
        setAgentStates((prev) => ({ ...prev, [agent.id]: 'done' }))
        if (onAgentLaunched) onAgentLaunched(data)
      }
    } catch (e: any) {
      setActionError('Error de conexión con el daemon de agentes.')
      setAgentStates((prev) => ({ ...prev, [agent.id]: 'idle' }))
    }
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto animate-fade-in pb-12 text-left">
      {/* Header KISS */}
      <div className="p-5 sm:p-6 rounded-3xl bg-[#0C0C0E] border border-white/5 shadow-xl space-y-1">
        <div className="flex items-center gap-2.5">
          <Bot className="w-5 h-5 text-emerald-400" />
          <h1 className="text-lg font-extrabold text-white tracking-tight">
            Escuadrón de Agentes · Flujo de 3 Fases
          </h1>
        </div>
        <p className="text-xs text-zinc-400">
          Los 3 robots autónomos que ejecutan el ciclo completo: Diseño (1) → Implementación (2) → Despliegue (3).
        </p>
      </div>

      {/* Los 3 Robots en Grid de 3 Columnas (Fieles al Dibujo) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {ROBOT_AGENTS.map((agent) => {
          const isSelected = selectedAgentId === agent.id
          const st = agentStates[agent.id] || 'idle'

          return (
            <div
              key={agent.id}
              onClick={() => setSelectedAgentId(agent.id)}
              className={`p-5 rounded-3xl border transition-all cursor-pointer flex flex-col justify-between space-y-4 ${
                isSelected
                  ? 'bg-zinc-900/90 border-white/20 shadow-2xl scale-[1.01]'
                  : 'bg-[#0C0C0E] hover:bg-zinc-900/50 border-white/5'
              }`}
            >
              <div className="space-y-3">
                {/* Robot SVG Avatar + Phase Badge */}
                <div className="flex items-center justify-between">
                  <div
                    className="w-12 h-12 rounded-2xl flex items-center justify-center border shadow-inner"
                    style={{
                      backgroundColor: `${agent.accentColor}15`,
                      borderColor: `${agent.accentColor}40`,
                    }}
                  >
                    <svg viewBox="0 0 100 100" className="w-9 h-9" fill="none">
                      <line x1="50" y1="18" x2="50" y2="28" stroke={agent.accentColor} strokeWidth="3" strokeLinecap="round" />
                      <circle cx="50" cy="15" r="4.5" fill={agent.accentColor} />
                      <rect x="25" y="28" width="50" height="38" rx="8" fill="#18181B" stroke={agent.accentColor} strokeWidth="3" />
                      <rect x="33" y="36" width="34" height="22" rx="4" fill="#09090B" stroke="#27272A" strokeWidth="1.5" />
                      <circle cx="42" cy="46" r="3" fill={agent.accentColor} />
                      <circle cx="58" cy="46" r="3" fill={agent.accentColor} />
                      <path d="M42 53 Q50 56 58 53" stroke={agent.accentColor} strokeWidth="2" strokeLinecap="round" fill="none" />
                      <rect x="35" y="66" width="30" height="18" rx="4" fill="#18181B" stroke={agent.accentColor} strokeWidth="2.5" />
                      <line x1="20" y1="42" x2="25" y2="42" stroke={agent.accentColor} strokeWidth="3" strokeLinecap="round" />
                      <line x1="75" y1="42" x2="80" y2="42" stroke={agent.accentColor} strokeWidth="3" strokeLinecap="round" />
                    </svg>
                  </div>

                  <span
                    className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold border ${agent.badgeBg}`}
                  >
                    Fase {agent.phaseNumber}
                  </span>
                </div>

                <div>
                  <h3 className="text-base font-extrabold text-white flex items-center gap-1.5">
                    <span>{agent.name}</span>
                    <span className="text-xs font-mono font-normal text-zinc-400">
                      (Agente {agent.phaseNumber})
                    </span>
                  </h3>
                  <p className="text-xs text-zinc-300 mt-1 font-medium leading-relaxed">
                    «{agent.diagramRole}»
                  </p>
                </div>
              </div>

              {/* Status and Action */}
              <div className="pt-3 border-t border-white/5 flex items-center justify-between text-xs">
                <span className="font-mono text-[10px] text-zinc-400">
                  {st === 'working' ? (
                    <span className="text-amber-400 flex items-center gap-1">
                      <Loader2 className="w-3 h-3 animate-spin" /> Procesando
                    </span>
                  ) : st === 'done' ? (
                    <span className="text-emerald-400 flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" /> Completado
                    </span>
                  ) : (
                    <span className="text-zinc-500">En espera</span>
                  )}
                </span>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    setSelectedAgentId(agent.id)
                    handleRunAgentOrder(agent)
                  }}
                  disabled={st === 'working'}
                  className="px-3 py-1.5 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-bold transition cursor-pointer flex items-center gap-1"
                >
                  <Play className="w-3 h-3 fill-black" />
                  <span>Probar</span>
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {/* Consola de Órdenes Interactiva para el Agente Seleccionado (KISS) */}
      <div className="p-6 rounded-3xl bg-[#0C0C0E] border border-white/10 space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/5 pb-4">
          <div className="flex items-center gap-3">
            <span
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: selectedAgent.accentColor }}
            />
            <div>
              <h2 className="text-sm font-extrabold text-white">
                Asignar Orden a {selectedAgent.name} ({selectedAgent.phaseTitle})
              </h2>
              <p className="text-xs text-zinc-400">{selectedAgent.specialty}</p>
            </div>
          </div>
          <span className="text-xs font-mono text-zinc-500">{selectedAgent.worktree}</span>
        </div>

        {/* Input + Presets */}
        <div className="space-y-3">
          <div className="flex flex-col sm:flex-row gap-2">
            <input
              type="text"
              value={customOrder}
              onChange={(e) => setCustomOrder(e.target.value)}
              placeholder={`Escribe una instrucción para ${selectedAgent.name}...`}
              className="flex-1 bg-black border border-zinc-800 focus:border-white rounded-2xl px-4 py-2.5 text-xs text-white placeholder-zinc-500 font-mono focus:outline-none"
            />
            <button
              type="button"
              disabled={agentStates[selectedAgent.id] === 'working'}
              onClick={() => handleRunAgentOrder(selectedAgent)}
              className="px-5 py-2.5 rounded-2xl bg-white hover:bg-zinc-200 disabled:opacity-40 text-black text-xs font-extrabold transition cursor-pointer flex items-center justify-center gap-2 shrink-0"
            >
              {agentStates[selectedAgent.id] === 'working' ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-black" />
                  <span>Ejecutando...</span>
                </>
              ) : (
                <>
                  <Send className="w-3.5 h-3.5 text-black" />
                  <span>Enviar Orden</span>
                </>
              )}
            </button>
          </div>

          <div className="space-y-1.5">
            <span className="text-[10px] font-mono uppercase tracking-wider text-zinc-500 block">
              Plantillas Rápidas para {selectedAgent.name}:
            </span>
            <div className="flex flex-wrap gap-1.5">
              {selectedAgent.presets.map((preset, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setCustomOrder(preset)
                    handleRunAgentOrder(selectedAgent, preset)
                  }}
                  className="px-3 py-1 rounded-xl bg-black hover:bg-zinc-800 border border-zinc-800 text-[11px] text-zinc-300 hover:text-white transition cursor-pointer font-mono"
                >
                  {preset}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Action Error / Output */}
        {actionError && (
          <div className="p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-200">
            {actionError}
          </div>
        )}

        {actionResult && (
          <div className="pt-2">
            <StructuredPayloadViewer
              execution={actionResult}
              onRequireHITL={() => {
                if (onNavigateToResolution) onNavigateToResolution()
              }}
              onRetryTask={() => handleRunAgentOrder(selectedAgent)}
            />
          </div>
        )}
      </div>
    </div>
  )
}
