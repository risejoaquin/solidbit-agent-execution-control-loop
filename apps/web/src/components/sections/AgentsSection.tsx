import React, { useState } from 'react'
import {
  Cpu,
  Server,
  Database,
  Shield,
  ShoppingBag,
  Layout,
  CheckCircle2,
  Terminal,
  Activity,
  AlertTriangle,
  Play,
  Square,
  RefreshCw,
} from 'lucide-react'
import type { AgentItem } from '../../types/orchestrator'

interface AgentsSectionProps {
  agents: AgentItem[]
}

export const AgentsSection: React.FC<AgentsSectionProps> = ({ agents }) => {
  const [selectedAgent, setSelectedAgent] = useState<AgentItem>(agents[0])
  const [agentLogs, setAgentLogs] = useState<Record<string, string[]>>({
    a1: [
      '[02:00:15] [INIT] architect-agent iniciado en worktree integration (PID: 1432)',
      '[02:00:16] [PREFLIGHT] Git worktree limpio verificado. Hash: 3b2a62d',
      '[02:00:17] [DAG] Sintetizando dependencias acíclicas de Kahn para Sprint SOLID-301',
      '[02:00:18] [AUDIT] 2 contratos inmutables congelados: DR-INV-001, DR-PAY-001',
    ],
    a2: [
      '[02:01:02] [REST] api-agent escuchando en puerto 8765 (PID: 2190)',
      '[02:01:04] [IDEM] Llaves de idempotencia DR-IDEM-001 registradas',
      '[02:01:06] [DISPATCH] Oleada 2 despachada a worktree coder-alpha',
    ],
    a3: [
      '[02:00:45] [SQLITE] db-agent conectado a SQLite WAL sacl_ops.db (PID: 3411)',
      '[02:00:46] [CONSTRAINTS] 22 estados canónicos validados en tabla jobs',
      '[02:00:48] [CHECKPOINT] WAL checkpoint completado. 0 páginas pendientes.',
    ],
    a4: [
      '[02:01:20] [AUTH] auth-agent verificando llaves HMAC-SHA256 (PID: 4892)',
      '[02:01:22] [SECURITY] Hard Deny Supremacy ACTIVO. Cero bypass.',
    ],
  })

  const getAgentIcon = (iconName: string) => {
    switch (iconName) {
      case 'cpu':
        return <Cpu className="w-5 h-5" />
      case 'server':
        return <Server className="w-5 h-5" />
      case 'database':
        return <Database className="w-5 h-5" />
      case 'shield':
        return <Shield className="w-5 h-5" />
      case 'shopping-bag':
        return <ShoppingBag className="w-5 h-5" />
      case 'layout':
        return <Layout className="w-5 h-5" />
      case 'check-circle':
        return <CheckCircle2 className="w-5 h-5" />
      default:
        return <Terminal className="w-5 h-5" />
    }
  }

  const logs = agentLogs[selectedAgent?.id] || [
    `[INFO] Agente ${selectedAgent?.name} listo en espera de asignación de oleada.`,
  ]

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-3xl bg-[#0e141d] border border-[#1b2533]">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold text-white tracking-wide">
              Gestión de Flota de Agentes Autónomos (SACL Fleet)
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              8 Agentes Especializados
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Supervisión concurrente de procesos, aislamiento en ramas Git y defensa contra reciclaje de PID
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-2xl bg-black/40 border border-[#1b2533] text-xs font-mono text-zinc-300">
            <Activity className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
            <span>Heartbeat: 100% Saludable</span>
          </span>
        </div>
      </div>

      {/* Agents Fleet Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {agents.map((agent) => {
          const isSelected = selectedAgent?.id === agent.id
          return (
            <div
              key={agent.id}
              onClick={() => setSelectedAgent(agent)}
              className={`p-4 rounded-3xl cursor-pointer transition-all border ${
                isSelected
                  ? 'bg-[#121a26] border-emerald-500/60 shadow-lg shadow-emerald-500/5'
                  : 'bg-[#0e141d] border-[#1b2533] hover:border-zinc-700'
              }`}
            >
              <div className="flex items-start justify-between">
                <div
                  className={`w-10 h-10 rounded-2xl flex items-center justify-center ${
                    agent.color === 'emerald'
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      : agent.color === 'amber'
                      ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      : 'bg-zinc-800 text-zinc-400 border border-zinc-700'
                  }`}
                >
                  {getAgentIcon(agent.icon)}
                </div>

                <span
                  className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${
                    agent.status === 'Activo'
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                      : agent.status === 'En espera'
                      ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                      : 'bg-zinc-800 text-zinc-500'
                  }`}
                >
                  {agent.status}
                </span>
              </div>

              <div className="mt-3">
                <h3 className="text-xs font-bold text-white font-mono">{agent.name}</h3>
                <p className="text-[11px] text-zinc-400">{agent.role}</p>
              </div>

              <div className="mt-3 pt-3 border-t border-[#1b2533] flex items-center justify-between text-[10px] font-mono text-zinc-500">
                <span>PID: {agent.pid}</span>
                <span className="text-emerald-400">Lock: ACTIVO</span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Selected Agent Live Console Inspector */}
      {selectedAgent && (
        <div className="p-6 rounded-3xl bg-[#0e141d] border border-[#1b2533] space-y-4 shadow-xl">
          <div className="flex items-center justify-between border-b border-[#1b2533] pb-4">
            <div className="flex items-center gap-3">
              <Terminal className="w-4 h-4 text-emerald-400" />
              <div>
                <h2 className="text-sm font-bold text-white font-mono">
                  Consola de Telemetría: {selectedAgent.name} (PID: {selectedAgent.pid})
                </h2>
                <p className="text-[11px] text-zinc-400">
                  Flujo de registros en tiempo real en worktrees/integration
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => alert(`Enviando señal SIGTERM segura a ${selectedAgent.name} (PID: ${selectedAgent.pid})`)}
                className="px-3 py-1.5 rounded-xl bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 text-xs font-mono flex items-center gap-1.5 transition"
              >
                <Square className="w-3 h-3" />
                <span>Detener Proceso</span>
              </button>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-[#070b10] border border-[#1b2533] font-mono text-xs text-zinc-300 space-y-2 max-h-60 overflow-y-auto custom-scroll">
            {logs.map((line, idx) => (
              <div key={idx} className="leading-relaxed">
                <span className="text-emerald-400 select-none">&gt; </span>
                <span>{line}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
