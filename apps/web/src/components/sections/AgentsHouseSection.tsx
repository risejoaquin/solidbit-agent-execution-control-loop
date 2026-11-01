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
  ])

  // Menú lateral interno exacto de tu boceto físico
  const [activeSideMenu, setActiveSideMenu] = useState<'skills' | 'skins' | 'procesos' | 'builder'>('skins')
  // Filtro superior por estado (Tarea B)
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'ACTIVE' | 'WAITING_GATE'>('ALL')
  const [inspectedAgent, setInspectedAgent] = useState<AgentCardData | null>(null)
  const [isProfileOpen, setIsProfileOpen] = useState(false)
  const [selectedVoiceIds, setSelectedVoiceIds] = useState<string[]>(['sec-auditor', 'arch-strict', 'data-vega'])
  const [isCampaignModalOpen, setIsCampaignModalOpen] = useState(false)

  // Estado para el modal de orden rápida
  const [quickOrderAgent, setQuickOrderAgent] = useState<AgentCardData | null>(null)
  const [quickOrderText, setQuickOrderText] = useState('')
  const [quickOrderLoading, setQuickOrderLoading] = useState(false)

  const toggleVoice = (id: string) => {
    setSelectedVoiceIds((prev) =>
      prev.includes(id) ? (prev.length > 1 ? prev.filter((v) => v !== id) : prev) : [...prev, id]
    )
  }

  // Filtrado reactivo de agentes
  const filteredAgents = agents.filter((agent) => {
    if (statusFilter === 'ACTIVE') {
      return ['RUNNING', 'COMPLETED', 'PASS', 'Activo'].includes(agent.status)
    }
    if (statusFilter === 'WAITING_GATE') {
      return ['WAITING_APPROVAL', 'BLOCKED', 'HUMAN_IN_THE_LOOP', 'En espera'].includes(agent.status)
    }
    return true
  })

  // Lanzar orden rápida
  const handleLaunchQuickOrder = async () => {
    if (!quickOrderAgent || !quickOrderText.trim()) return
    setQuickOrderLoading(true)
    try {
      const payload = {
        command: 'EXECUTE_WAVE',
        job_id: `quick-${Date.now()}`,
        project_id: 'stable-ecommerce',
        manifest: {
          id: `pkg-${Date.now()}`,
          agent: quickOrderAgent.agentName,
          tasks: [quickOrderText.trim()],
          priority: 0,
        },
      }
      const res = await fetch('/api/orchestrator/enqueue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (res.ok) {
        if (onAgentLaunched) onAgentLaunched({ agent: quickOrderAgent.agentName, task: quickOrderText })
        setQuickOrderAgent(null)
        setQuickOrderText('')
      }
    } catch (e) {
      console.warn('Error launching quick order:', e)
    } finally {
      setQuickOrderLoading(false)
    }
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
    <div className="flex flex-col w-full bg-[#000000] space-y-3 select-none text-left min-h-full pb-16 md:pb-6">
      {/* Header Aeronáutico Técnico con scroll horizontal en móvil si se requiere */}
      <div className="border border-white/8 bg-[#0a0a0a] rounded-lg p-3 sm:p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shrink-0">
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-xs sm:text-sm font-bold text-white tracking-wider uppercase font-sans truncate">
              Casa de Agentes Tiempo Real
            </h1>
            <span className="text-[9px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-1.5 py-0.5 rounded shrink-0">
              PARIDAD 100%
            </span>
          </div>
          <p className="text-[10px] font-mono text-zinc-500 mt-0.5 leading-snug">
            Los agentes se ven en tiempo real con diseño completo, assets Bomberman y pipeline SDLC.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setIsCampaignModalOpen(true)}
          className="w-full sm:w-auto px-3 py-2 rounded text-xs font-mono bg-emerald-500 text-black font-semibold hover:bg-emerald-400 transition cursor-pointer flex items-center justify-center gap-1.5 shrink-0"
        >
          <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <path d="M3 9h18" />
            <path d="M9 21V9" />
          </svg>
          <span>Diseñar Wave / Campaña (Emergente)</span>
        </button>
      </div>

      {/* Menú de Boceto Físico: En móvil horizontal deslizable, en escritorio vertical (w-56) */}
      <div className="flex flex-col md:flex-row gap-3">
        {/* Menú Lateral / Barra de Pestañas Móvil */}
        <div className="w-full md:w-56 bg-[#0a0a0a] border border-white/8 rounded-lg p-2.5 sm:p-3 flex md:flex-col justify-between shrink-0 overflow-x-auto custom-scroll">
          <div className="flex md:flex-col gap-1.5 w-full">
            <div className="hidden md:block text-[9px] font-mono text-zinc-500 uppercase tracking-wider px-2 py-1">
              Parámetros de Agentes
            </div>

            {/* 1. Skills */}
            <button
              type="button"
              onClick={() => setActiveSideMenu('skills')}
              className={`px-3 py-1.5 sm:py-2 rounded text-xs font-mono transition flex items-center justify-between whitespace-nowrap shrink-0 md:shrink md:w-full ${
                activeSideMenu === 'skills'
                  ? 'bg-white/10 text-white font-semibold border border-white/10'
                  : 'text-zinc-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <span>Skills</span>
              <span className="hidden md:inline text-[9px] text-zinc-600">.md</span>
            </button>

            {/* 2. Skins (Activa y conectada a Bomberman) */}
            <button
              type="button"
              onClick={() => setActiveSideMenu('skins')}
              className={`px-3 py-1.5 sm:py-2 rounded text-xs font-mono transition flex items-center justify-between whitespace-nowrap shrink-0 md:shrink md:w-full ${
                activeSideMenu === 'skins'
                  ? 'bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/30'
                  : 'text-zinc-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                <span>Skins</span>
              </div>
              <span className="hidden md:inline text-[9px] text-emerald-500 font-mono">16-bit SNES</span>
            </button>

            {/* 3. Procesos */}
            <button
              type="button"
              onClick={() => setActiveSideMenu('procesos')}
              className={`px-3 py-1.5 sm:py-2 rounded text-xs font-mono transition flex items-center justify-between whitespace-nowrap shrink-0 md:shrink md:w-full ${
                activeSideMenu === 'procesos'
                  ? 'bg-white/10 text-white font-semibold border border-white/10'
                  : 'text-zinc-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <span>Procesos</span>
              <span className="hidden md:inline text-[9px] text-zinc-600">Kahn DAG</span>
            </button>

            {/* 4. Diseñar wave/campaña */}
            <button
              type="button"
              onClick={() => setIsCampaignModalOpen(true)}
              className="px-3 py-1.5 sm:py-2 rounded text-xs font-mono transition border border-dashed border-white/20 text-zinc-300 hover:text-emerald-400 hover:border-emerald-500/40 whitespace-nowrap shrink-0 md:shrink md:w-full md:mt-3"
            >
              <div className="font-semibold">+ Diseñar Wave</div>
            </button>
          </div>

          <div className="hidden md:block p-2.5 bg-[#000000] border border-white/8 rounded text-[9px] font-mono text-zinc-500 space-y-1 mt-4">
            <div className="text-zinc-400 font-bold">SOLIDBIT AGENTS</div>
            <div>• {agents.length} avatares activos</div>
            <div>• Zero-Token aislado</div>
            <div>• Super Bomberman 1</div>
          </div>
        </div>

        {/* Columna Derecha / Principal: Cuadrícula Adaptativa con Filtros Rápidos */}
        <div className="flex-1 bg-[#0a0a0a] border border-white/8 rounded-lg p-3 sm:p-4 flex flex-col justify-between">
          <div>
            {/* Barra Superior con Chips de Filtrado Rápido (Tarea B) */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 mb-3 border-b border-white/8 pb-2.5">
              <div className="flex items-center gap-1.5 bg-[#121212] border border-white/8 rounded-lg p-1 w-full sm:w-auto">
                <button
                  type="button"
                  onClick={() => setStatusFilter('ALL')}
                  className={`flex-1 sm:flex-none px-2.5 py-1 text-[10px] font-mono rounded transition ${
                    statusFilter === 'ALL'
                      ? 'bg-white/10 text-white font-semibold'
                      : 'text-zinc-400 hover:text-zinc-200'
                  }`}
                >
                  Todos ({agents.length})
                </button>
                <button
                  type="button"
                  onClick={() => setStatusFilter('ACTIVE')}
                  className={`flex-1 sm:flex-none px-2.5 py-1 text-[10px] font-mono rounded transition flex items-center justify-center gap-1 ${
                    statusFilter === 'ACTIVE'
                      ? 'bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/30'
                      : 'text-zinc-400 hover:text-zinc-200'
                  }`}
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                  <span>Activos ({agents.filter((a) => ['RUNNING', 'COMPLETED', 'PASS', 'Activo'].includes(a.status)).length})</span>
                </button>
                <button
                  type="button"
                  onClick={() => setStatusFilter('WAITING_GATE')}
                  className={`flex-1 sm:flex-none px-2.5 py-1 text-[10px] font-mono rounded transition flex items-center justify-center gap-1 ${
                    statusFilter === 'WAITING_GATE'
                      ? 'bg-amber-500/10 text-amber-400 font-semibold border border-amber-500/30'
                      : 'text-zinc-400 hover:text-zinc-200'
                  }`}
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                  <span>Esperando Gate 5 ({agents.filter((a) => ['WAITING_APPROVAL', 'BLOCKED', 'HUMAN_IN_THE_LOOP', 'En espera'].includes(a.status)).length})</span>
                </button>
              </div>

              <div className="text-[10px] font-mono text-zinc-500 hidden sm:block">
                ⚡ Clic en "Orden" para despacho de 1 toque
              </div>
            </div>

            {/* Cuadrícula Adaptativa: 1 columna en móvil (iPhone 13 Pro), 2 en tablet, 3 en desktop */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 sm:gap-3">
              {filteredAgents.map((agent) => (
                <AgentCard
                  key={agent.agentName}
                  agent={agent}
                  onInspect={() => {
                    setInspectedAgent(agent)
                    setIsProfileOpen(true)
                  }}
                  onQuickOrder={(a) => {
                    setQuickOrderAgent(a)
                    setQuickOrderText(
                      a.agentName === 'Atlas'
                        ? 'Verificar consistencia del grafo Kahn DAG sin ciclos de ramas'
                        : a.agentName === 'Vega'
                        ? 'Auditar balance transaccional estricto en SQLite WAL bajo invariante DR-INV-001'
                        : a.agentName === 'Nova'
                        ? 'Ejecutar suite completa de pruebas unitarias Pytest'
                        : 'Auditar 9 políticas constitucionales y compuertas Gate 5'
                    )
                  }}
                />
              ))}
            </div>
          </div>

          {/* Banner inferior contextual */}
          {activeSideMenu === 'skins' && (
            <div className="mt-3 p-2.5 sm:p-3 bg-[#000000] border border-white/8 rounded flex flex-col sm:flex-row items-start sm:items-center justify-between gap-1 text-[11px] font-mono">
              <div className="flex items-center gap-2">
                <span className="text-emerald-400 font-bold">Sprites SNES:</span>
                <span className="text-zinc-400">
                  White (Atlas), Blue (Vega), Red (Nova), Black (Centinela).
                </span>
              </div>
              <span className="text-zinc-500 text-[10px]">Render Pixel-Perfect O(1)</span>
            </div>
          )}

          {activeSideMenu === 'skills' && (
            <div className="mt-3 p-2.5 sm:p-3 bg-[#000000] border border-white/8 rounded text-[11px] font-mono space-y-1">
              <div className="text-white font-bold">Skills Vinculados a los Agentes:</div>
              <div className="text-zinc-400">
                Atlas (sacl-orchestrator) · Vega (solidbit-engineer) · Nova (pytest-runner) · Centinela (solidbit-sdlc).
              </div>
            </div>
          )}

          {activeSideMenu === 'procesos' && (
            <div className="mt-3 p-2.5 sm:p-3 bg-[#000000] border border-white/8 rounded text-[11px] font-mono space-y-1">
              <div className="text-white font-bold">Control Loop Kahn DAG en Ejecución:</div>
              <div className="text-zinc-400">
                Particionado de oleadas por worktrees efímeros sin colisiones en SQLite WAL.
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Mini-Modal de Orden Rápida (1 Toque) */}
      {quickOrderAgent && (
        <div className="fixed inset-0 z-[150] bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#0a0a0a] border border-white/10 rounded-xl p-4 sm:p-5 w-full max-w-md shadow-2xl text-left space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-emerald-400 font-bold text-sm">⚡ Orden Rápida:</span>
                <span className="text-white font-bold text-sm font-sans">{quickOrderAgent.agentName}</span>
              </div>
              <button
                type="button"
                onClick={() => setQuickOrderAgent(null)}
                className="text-zinc-500 hover:text-white font-mono text-sm p-1"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-zinc-400 font-sans">
              Despacha una directiva puntual sin abrir el maquetador completo de campañas.
            </p>

            <textarea
              value={quickOrderText}
              onChange={(e) => setQuickOrderText(e.target.value)}
              rows={3}
              className="w-full bg-[#000000] border border-white/10 rounded p-2.5 text-xs text-white font-mono focus:border-emerald-500/50 outline-none"
              placeholder="Ingresa la orden directa para este agente..."
            />

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-white/8">
              <button
                type="button"
                onClick={() => setQuickOrderAgent(null)}
                className="px-3 py-1.5 rounded text-xs font-mono text-zinc-400 hover:text-white"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={handleLaunchQuickOrder}
                disabled={quickOrderLoading || !quickOrderText.trim()}
                className="px-4 py-1.5 rounded text-xs font-mono bg-emerald-500 text-black font-semibold hover:bg-emerald-400 transition cursor-pointer disabled:opacity-50 flex items-center gap-1.5"
              >
                {quickOrderLoading ? 'Enviando...' : 'Despachar Ahora'}
              </button>
            </div>
          </div>
        </div>
      )}

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
