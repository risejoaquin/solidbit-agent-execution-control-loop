import React, { useState, useEffect } from 'react'
import { AgentCard, type AgentCardData } from '../AgentCard'
import { AgentProfileExtended } from '../AgentProfileExtended'
import { SoftPhaseMultiVoice, AVAILABLE_VOICES } from '../SoftPhaseMultiVoice'
import { CampaignVisualBuilder } from '../CampaignVisualBuilder'

interface AgentsHouseSectionProps {
  onAgentLaunched?: (data: any) => void
}

export const AgentsHouseSection: React.FC<AgentsHouseSectionProps> = ({ onAgentLaunched }) => {
  const [agents, setAgents] = useState<AgentCardData[]>([
    {
      agentName: 'Atlas',
      role: 'Coordinador Kahn DAG & Scheduler',
      currentProcess: 'Topological Kahn Scheduler Activo',
      status: 'PASS',
      lastLog: 'DAG topológico verificado sin ciclos de ramas.',
      pid: 14208,
      commitSha: 'c6370d7',
      lastActive: 'Justo ahora',
      skin: 'bomberman_idle',
    },
    {
      agentName: 'Vega',
      role: 'Arquitecta de Datos & Contratos',
      currentProcess: 'Invariantes DR-INV-001 y DR-PAY-001',
      status: 'PASS',
      lastLog: 'Balance transaccional verificado en SQLite WAL.',
      pid: 14212,
      commitSha: 'c6370d7',
      lastActive: 'Justo ahora',
      skin: 'bomberman_idle',
    },
    {
      agentName: 'Nova',
      role: 'Inspectora de Calidad & Pytest',
      currentProcess: 'Suite Automatizada de Verificación',
      status: 'PASS',
      lastLog: '37/37 pruebas de UI pasaron exitosamente.',
      pid: 14216,
      commitSha: 'c6370d7',
      lastActive: 'Justo ahora',
      skin: 'bomberman_idle',
    },
    {
      agentName: 'Centinela',
      role: 'Guardián Constitucional & Hard Deny',
      currentProcess: 'Auditoría de Políticas Gate 5 HMAC',
      status: 'PASS',
      lastLog: '9/9 políticas constitucionales validadas.',
      pid: 14220,
      commitSha: 'c6370d7',
      lastActive: 'Justo ahora',
      skin: 'bomberman_idle',
    },
    {
      agentName: 'Frontend Architect',
      role: 'Maquetador OOUX & Fidelidad Visual',
      currentProcess: 'Paridad 100% de Bocetos Físicos',
      status: 'PASS',
      lastLog: 'Sincronización reactiva con sprites 16-bit completada.',
      pid: 14224,
      commitSha: 'c6370d7',
      lastActive: 'Justo ahora',
      skin: 'bomberman_idle',
    },
    {
      agentName: 'Julian (External EOP)',
      role: 'Operador Soberano Independiente',
      currentProcess: 'Context Boundary Aislado',
      status: 'PASS',
      lastLog: 'Operación en espacio soberano propio.',
      pid: 14228,
      commitSha: 'c6370d7',
      lastActive: 'Justo ahora',
      skin: 'bomberman_idle',
    },
  ])

  // Menú lateral interno exacto de tu boceto físico
  const [activeSideMenu, setActiveSideMenu] = useState<'skills' | 'skins' | 'procesos' | 'builder'>('skins')
  const [inspectedAgent, setInspectedAgent] = useState<AgentCardData | null>(null)
  const [isProfileOpen, setIsProfileOpen] = useState(false)
  const [selectedVoiceIds, setSelectedVoiceIds] = useState<string[]>(['sec-auditor', 'arch-strict', 'data-vega'])
  const [isCampaignModalOpen, setIsCampaignModalOpen] = useState(false)

  const toggleVoice = (id: string) => {
    setSelectedVoiceIds((prev) =>
      prev.includes(id) ? (prev.length > 1 ? prev.filter((v) => v !== id) : prev) : [...prev, id]
    )
  }

  // SSE Telemetry listener
  useEffect(() => {
    let sse: EventSource | null = null
    try {
      sse = new EventSource('/api/events/stream')
      const handleTelemetry = (e: MessageEvent) => {
        try {
          const payload = JSON.parse(e.data)
          const agentName = payload.agent || payload.agent_id || payload.agent_name || payload.component
          if (!agentName) return

          const status = payload.status || 'RUNNING'
          const task = payload.task || payload.current_task || payload.message || payload.goal || 'Proceso en curso'
          const log = payload.reason || payload.last_log || payload.message

          setAgents((prev) => {
            const idx = prev.findIndex((a) => a.agentName.toLowerCase() === String(agentName).toLowerCase())
            const updated: AgentCardData = {
              agentName,
              role: idx >= 0 ? prev[idx].role : 'EOP Execution Agent',
              currentProcess: task,
              status,
              lastLog: log,
              pid: payload.pid || (idx >= 0 ? prev[idx].pid : undefined),
              commitSha: payload.commit || payload.commit_sha || (idx >= 0 ? prev[idx].commitSha : undefined),
              lastActive: 'Justo ahora',
            }
            if (idx >= 0) {
              const next = [...prev]
              next[idx] = { ...next[idx], ...updated }
              return next
            }
            return [updated, ...prev]
          })
        } catch {}
      }

      sse.addEventListener('task_running', handleTelemetry)
      sse.addEventListener('agent_spawned', handleTelemetry)
      sse.addEventListener('heartbeat_recorded', handleTelemetry)
      sse.addEventListener('agent_event', handleTelemetry)
    } catch {}

    return () => {
      if (sse) sse.close()
    }
  }, [])

  return (
    <div className="flex flex-col h-full w-full bg-[#000000] space-y-3 select-none text-left">
      {/* Header Aeronáutico Técnico */}
      <div className="border border-white/8 bg-[#0a0a0a] rounded-lg p-3.5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shrink-0">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xs font-bold text-white tracking-wider uppercase font-sans">
              Casa de Agentes Tiempo Real
            </h1>
            <span className="text-[9px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-1.5 py-0.5 rounded">
              BOCETO FÍSICO PARIDAD 100%
            </span>
          </div>
          <p className="text-[10px] font-mono text-zinc-500 mt-0.5">
            Los agentes se ven en tiempo real con un diseño completo importando assets, personalidad y sprint SDLC.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setIsCampaignModalOpen(true)}
          className="px-3 py-1.5 rounded text-xs font-mono bg-emerald-500 text-black font-semibold hover:bg-emerald-400 transition cursor-pointer flex items-center gap-1.5"
        >
          <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <path d="M3 9h18" />
            <path d="M9 21V9" />
          </svg>
          <span>Diseñar Wave / Campaña (Ventana Emergente)</span>
        </button>
      </div>

      {/* Layout Split de Dos Columnas: Exacto como en tu Boceto Físico */}
      <div className="flex-1 flex flex-col md:flex-row gap-3 min-h-0 overflow-hidden">
        {/* Columna Izquierda: Menú Lateral de la Casa de Agentes (Skills, Skins, Procesos, Diseñar) */}
        <div className="w-full md:w-56 bg-[#0a0a0a] border border-white/8 rounded-lg p-3 flex flex-col justify-between shrink-0">
          <div className="space-y-1.5">
            <div className="text-[9px] font-mono text-zinc-500 uppercase tracking-wider px-2 py-1">
              Parámetros de Agentes
            </div>

            {/* 1. Skills */}
            <button
              type="button"
              onClick={() => setActiveSideMenu('skills')}
              className={`w-full text-left px-3 py-2 rounded text-xs font-mono transition flex items-center justify-between ${
                activeSideMenu === 'skills'
                  ? 'bg-white/10 text-white font-semibold border border-white/10'
                  : 'text-zinc-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <span>Skills</span>
              <span className="text-[9px] text-zinc-600">.md</span>
            </button>

            {/* 2. Skins (Activa y conectada a Bomberman) */}
            <button
              type="button"
              onClick={() => setActiveSideMenu('skins')}
              className={`w-full text-left px-3 py-2 rounded text-xs font-mono transition flex items-center justify-between ${
                activeSideMenu === 'skins'
                  ? 'bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/30'
                  : 'text-zinc-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                <span>Skins</span>
              </div>
              <span className="text-[9px] text-emerald-500 font-mono">16-bit SNES</span>
            </button>

            {/* 3. Procesos */}
            <button
              type="button"
              onClick={() => setActiveSideMenu('procesos')}
              className={`w-full text-left px-3 py-2 rounded text-xs font-mono transition flex items-center justify-between ${
                activeSideMenu === 'procesos'
                  ? 'bg-white/10 text-white font-semibold border border-white/10'
                  : 'text-zinc-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <span>Procesos</span>
              <span className="text-[9px] text-zinc-600">Kahn DAG</span>
            </button>

            {/* 4. Diseñar wave/campaña / ventana emergente */}
            <button
              type="button"
              onClick={() => setIsCampaignModalOpen(true)}
              className="w-full text-left px-3 py-2 rounded text-xs font-mono transition border border-dashed border-white/20 text-zinc-300 hover:text-emerald-400 hover:border-emerald-500/40 mt-3"
            >
              <div className="font-semibold">+ Diseñar Wave/Campaña</div>
              <div className="text-[9px] text-zinc-500">Ventana emergente</div>
            </button>
          </div>

          <div className="p-2.5 bg-[#000000] border border-white/8 rounded text-[9px] font-mono text-zinc-500 space-y-1">
            <div className="text-zinc-400 font-bold">SOLIDBIT AGENTS</div>
            <div>• {agents.length} avatares activos</div>
            <div>• Zero-Token aislado</div>
            <div>• Super Bomberman 1</div>
          </div>
        </div>

        {/* Columna Derecha: Recuadro Grande con la Cuadrícula de Avatares (Exacto al Boceto Físico) */}
        <div className="flex-1 bg-[#0a0a0a] border border-white/8 rounded-lg p-4 overflow-y-auto custom-scroll flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3 border-b border-white/8 pb-2">
              <div className="text-xs font-mono text-zinc-400">
                Vista de Campo: <span className="text-white font-semibold">{activeSideMenu.toUpperCase()}</span>
              </div>
              <div className="text-[10px] font-mono text-emerald-400">
                Haz clic en cualquier avatar para auditar SDLC y alternar skins
              </div>
            </div>

            {/* Cuadrícula de Siluetas/Avatares: 6 personajes tal como el boceto (2 filas de 3) */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {agents.map((agent) => (
                <AgentCard
                  key={agent.agentName}
                  agent={agent}
                  onInspect={() => {
                    setInspectedAgent(agent)
                    setIsProfileOpen(true)
                  }}
                />
              ))}
            </div>
          </div>

          {/* Mini-Panel inferior contextual según menú seleccionado */}
          {activeSideMenu === 'skins' && (
            <div className="mt-4 p-3 bg-[#000000] border border-white/8 rounded flex items-center justify-between text-xs font-mono">
              <div className="flex items-center gap-2">
                <span className="text-emerald-400 font-bold">Sprites SNES Activos:</span>
                <span className="text-zinc-400">
                  White (Atlas), Blue (Vega), Red (Nova), Black (Centinela).
                </span>
              </div>
              <span className="text-zinc-500 text-[10px]">Render Pixel-Perfect O(1)</span>
            </div>
          )}

          {activeSideMenu === 'skills' && (
            <div className="mt-4 p-3 bg-[#000000] border border-white/8 rounded text-xs font-mono space-y-1">
              <div className="text-white font-bold">Skills Vinculados a los Agentes:</div>
              <div className="text-zinc-400 text-[11px]">
                Atlas (sacl-orchestrator) · Vega (solidbit-engineer) · Nova (pytest-runner) · Centinela (solidbit-sdlc).
              </div>
            </div>
          )}

          {activeSideMenu === 'procesos' && (
            <div className="mt-4 p-3 bg-[#000000] border border-white/8 rounded text-xs font-mono space-y-1">
              <div className="text-white font-bold">Control Loop Kahn DAG en Ejecución:</div>
              <div className="text-zinc-400 text-[11px]">
                Particionado de oleadas por worktrees efímeros sin colisiones en SQLite WAL.
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Drawer Lateral de Perfil Extendido SDLC (Fase 2) */}
      <AgentProfileExtended
        agent={inspectedAgent}
        isOpen={isProfileOpen}
        onClose={() => setIsProfileOpen(false)}
        onSkinChange={(agentName, skinKey) => {
          setAgents((prev) =>
            prev.map((a) => (a.agentName.toLowerCase() === agentName.toLowerCase() ? { ...a, skin: skinKey } : a))
          )
        }}
      />

      {/* Modal Visual Campaign Builder (Fase 3 - Ventana Emergente) */}
      <CampaignVisualBuilder
        isOpen={isCampaignModalOpen}
        onClose={() => setIsCampaignModalOpen(false)}
        onDispatched={(jobId) => {
          if (onAgentLaunched) onAgentLaunched({ job_id: jobId })
        }}
      />
    </div>
  )
}
