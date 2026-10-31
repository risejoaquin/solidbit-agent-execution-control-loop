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
      role: 'Coordinador de Flujos & DAG',
      currentProcess: 'Topological Kahn Scheduler Activo',
      status: 'PASS',
      lastLog: 'DAG topológico verificado sin ciclos de ramas.',
      pid: 14208,
      commitSha: '0bf7b4c',
      lastActive: 'Justo ahora',
    },
    {
      agentName: 'Vega',
      role: 'Arquitecta de Datos & Contratos',
      currentProcess: 'Invariantes DR-INV-001 y DR-PAY-001',
      status: 'PASS',
      lastLog: 'Balance transaccional verificado en SQLite WAL.',
      pid: 14212,
      commitSha: '0bf7b4c',
      lastActive: 'Justo ahora',
    },
    {
      agentName: 'Nova',
      role: 'Inspectora de Calidad & Pytest',
      currentProcess: 'Suite Automatizada de Verificación',
      status: 'PASS',
      lastLog: '37/37 pruebas de UI pasaron exitosamente.',
      pid: 14216,
      commitSha: '0bf7b4c',
      lastActive: 'Justo ahora',
    },
    {
      agentName: 'Centinela',
      role: 'Guardián de Políticas y Hard Deny',
      currentProcess: 'Auditoría Constitucional de Seguridad',
      status: 'PASS',
      lastLog: '9/9 políticas constitucionales validadas.',
      pid: 14220,
      commitSha: '0bf7b4c',
      lastActive: 'Justo ahora',
    },
  ])

  const [inspectedAgent, setInspectedAgent] = useState<AgentCardData | null>(null)
  const [isProfileOpen, setIsProfileOpen] = useState(false)
  const [selectedVoiceIds, setSelectedVoiceIds] = useState<string[]>(['sec-auditor', 'arch-strict', 'data-vega'])
  const [isCampaignModalOpen, setIsCampaignModalOpen] = useState(false)
  const [activeTab, setActiveTab] = useState<'squad' | 'soft_phase'>('squad')

  const toggleVoice = (id: string) => {
    setSelectedVoiceIds((prev) =>
      prev.includes(id) ? (prev.length > 1 ? prev.filter((v) => v !== id) : prev) : [...prev, id]
    )
  }

  // SSE Stream Listener
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
    <div className="flex flex-col h-full w-full bg-[#000000] space-y-4 select-none text-left">
      {/* Header Aeronáutico Técnico de la Casa de Agentes */}
      <div className="border border-white/8 bg-[#0a0a0a] rounded-lg p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75">
              <path d="M12 2a4 4 0 0 0-4 4v1H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-2V6a4 4 0 0 0-4-4Z" />
              <circle cx="9" cy="13" r="1" />
              <circle cx="15" cy="13" r="1" />
              <path d="M10 17h4" />
            </svg>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold text-white tracking-wide uppercase font-sans">
                Casa de Agentes · Control Loop EOP
              </h1>
              <span className="text-[9px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-1.5 py-0.5 rounded">
                PARIDAD 100%
              </span>
            </div>
            <p className="text-[11px] font-mono text-zinc-400 mt-0.5">
              Topología Kahn DAG · Coordinación de Atlas, Vega, Nova y Centinela · Skins & SDLC
            </p>
          </div>
        </div>

        {/* Tab Switcher & Action */}
        <div className="flex items-center gap-2 self-end sm:self-auto">
          <div className="flex bg-[#121212] border border-white/8 rounded p-0.5">
            <button
              type="button"
              onClick={() => setActiveTab('squad')}
              className={`px-3 py-1.5 text-xs font-mono rounded transition ${
                activeTab === 'squad'
                  ? 'bg-white/10 text-white font-semibold'
                  : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              Escuadrón & Procesos
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('soft_phase')}
              className={`px-3 py-1.5 text-xs font-mono rounded transition flex items-center gap-1.5 ${
                activeTab === 'soft_phase'
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-semibold'
                  : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span>Fase Soft ({selectedVoiceIds.length})</span>
            </button>
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
            <span>Lanzar Campaña Visual</span>
          </button>
        </div>
      </div>

      {/* Main Content View */}
      {activeTab === 'squad' ? (
        <div className="flex-1 space-y-4">
          {/* Status Subtitle Banner */}
          <div className="flex items-center justify-between px-2 text-[11px] font-mono text-zinc-500">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>{agents.length} Agentes Autolimpiables en Memoria Activa</span>
            </div>
            <span>Haz clic en "Auditar SDLC" en cualquier tarjeta para desplegar el perfil</span>
          </div>

          {/* Cuadrícula de Alta Densidad (Agent Cards) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
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

          {/* Banner Explicativo de Invariantes */}
          <div className="bg-[#0a0a0a] border border-white/8 rounded-lg p-3.5 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-xs font-mono">
            <div className="flex items-center gap-2.5 text-zinc-300">
              <span className="text-emerald-400 font-bold">✓ Zero-Token Security:</span>
              <span className="text-zinc-400">
                Las llaves maestras jamás tocan el navegador. Toda mutación pasa por compuertas Gate 5.
              </span>
            </div>
            <div className="text-zinc-500 text-[10px]">
              Kahn Topological DAG · SQLite WAL Invariant
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 bg-[#0a0a0a] border border-white/8 rounded-lg p-5 space-y-4">
          <div>
            <h2 className="text-sm font-semibold text-white tracking-wide uppercase font-sans">
              Directorio de Síntesis Estratégica (Fase Soft)
            </h2>
            <p className="text-xs text-zinc-400 mt-1">
              Configura qué voces y directivas de diseño, seguridad y contratos se inyectarán de forma invisible en cada comando CQRS.
            </p>
          </div>

          <SoftPhaseMultiVoice
            selectedVoiceIds={selectedVoiceIds}
            onToggleVoice={toggleVoice}
          />
        </div>
      )}

      {/* Drawer Lateral de Perfil Extendido SDLC (Fase 2) */}
      <AgentProfileExtended
        agent={inspectedAgent}
        isOpen={isProfileOpen}
        onClose={() => setIsProfileOpen(false)}
      />

      {/* Modal Visual Campaign Builder (Fase 3) */}
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
