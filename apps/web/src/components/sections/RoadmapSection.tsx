import React, { useState, useEffect } from 'react'
import {
  GitBranch,
  Calendar,
  ListFilter,
  Download,
  Plus,
  CheckCircle2,
  Layers,
  ShieldCheck,
  Play,
  RotateCcw,
} from 'lucide-react'
import type { TaskItem } from '../../types/orchestrator'

interface RoadmapSectionProps {
  tasks: TaskItem[]
  onOpenSprintModal: () => void
}

interface DagNode {
  id: string
  label: string
  agent_role: string
  action: string
  gate_required: boolean
  timeout_sec: number
  dependencies: string
}

export const RoadmapSection: React.FC<RoadmapSectionProps> = ({
  tasks: initialTasks,
  onOpenSprintModal,
}) => {
  const [viewMode, setViewMode] = useState<'gantt' | 'list'>('gantt')
  const [dagData, setDagData] = useState<any>(null)
  const [dagNodes, setDagNodes] = useState<DagNode[]>([])
  const [backlogTasks, setBacklogTasks] = useState<any[]>([])
  const [validating, setValidating] = useState(false)
  const [validationResult, setValidationResult] = useState<any>(null)

  // Load real DAG from Campaign Designer backend & backlog from context
  const loadDag = async () => {
    try {
      const res = await fetch('/api/campaigns/designer')
      const data = await res.json()
      if (data && data.nodes) {
        setDagData(data)
        setDagNodes(data.nodes)
      }
    } catch (e) {
      console.warn('Error loading DAG from backend:', e)
    }

    try {
      const ctxRes = await fetch('/api/orchestrator/context')
      const ctx = await ctxRes.json()
      if (ctx && ctx.jira_backlog) {
        setBacklogTasks(ctx.jira_backlog)
      }
    } catch (e) {
      console.warn('Error loading context backlog:', e)
    }
  }

  useEffect(() => {
    loadDag()
  }, [])

  // Real backend topological validation
  const handleValidateDAG = async () => {
    setValidating(true)
    try {
      const res = await fetch('/api/campaigns/designer/validate', { method: 'POST' })
      const data = await res.json()
      setValidationResult(data)
    } catch (e: any) {
      alert('Error validando DAG: ' + e.message)
    } finally {
      setValidating(false)
    }
  }

  // Real export to JSON
  const handleExportJSON = () => {
    const payload = {
      campaign: dagData || { name: 'SACL Autonomous Sprint DAG' },
      nodes: dagNodes,
      backlog: backlogTasks,
      exported_at: new Date().toISOString(),
    }
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(payload, null, 2))
    const a = document.createElement('a')
    a.href = dataStr
    a.download = 'sacl_topological_dag.json'
    document.body.appendChild(a)
    a.click()
    a.remove()
  }

  // Real export to CSV
  const handleExportCSV = () => {
    const headers = ['ID Nodo', 'Etiqueta', 'Rol de Agente', 'Accion', 'Compuerta Requerida', 'Dependencias']
    const rows = dagNodes.map((n) => [
      n.id,
      `"${n.label.replace(/"/g, '""')}"`,
      n.agent_role,
      n.action,
      n.gate_required ? 'SI (HITL)' : 'NO',
      `"${n.dependencies || 'Raíz'}"`,
    ])
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((r) => r.join(','))].join('\n')
    const a = document.createElement('a')
    a.href = encodeURI(csvContent)
    a.download = 'sacl_dag_nodes.csv'
    document.body.appendChild(a)
    a.click()
    a.remove()
  }

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-3xl bg-zinc-950 border border-zinc-800">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold text-white tracking-wide">
              {dagData?.name || 'Roadmap & DAG Topológico de Kahn'}
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-white/10 text-zinc-200 border border-zinc-700">
              {dagNodes.length} Nodos &bull; {dagData?.campaign_id || 'DAG Activo'}
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Topología acíclica de ejecución para agentes autónomos obtenida directamente de CampaignDesignerModule
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* View toggle */}
          <div className="flex items-center p-1 rounded-2xl bg-black/40 border border-zinc-800">
            <button
              onClick={() => setViewMode('gantt')}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition flex items-center gap-1.5 ${
                viewMode === 'gantt'
                  ? 'bg-white text-black font-bold shadow-md'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              <Calendar className="w-3.5 h-3.5" />
              <span>Gantt</span>
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition flex items-center gap-1.5 ${
                viewMode === 'list'
                  ? 'bg-white text-black font-bold shadow-md'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              <ListFilter className="w-3.5 h-3.5" />
              <span>Lista</span>
            </button>
          </div>

          <button
            onClick={handleValidateDAG}
            disabled={validating}
            className="px-3 py-2 rounded-2xl bg-black border border-zinc-800 hover:border-zinc-700 text-xs text-zinc-300 flex items-center gap-1.5 transition cursor-pointer"
            title="Validar aciclicidad con backend"
          >
            <ShieldCheck className="w-3.5 h-3.5 text-zinc-300" />
            <span>{validating ? 'Validando...' : 'Validar DAG'}</span>
          </button>

          <button
            onClick={handleExportJSON}
            className="px-3 py-2 rounded-2xl bg-black border border-zinc-800 hover:border-zinc-700 text-xs text-zinc-300 flex items-center gap-1.5 transition cursor-pointer"
            title="Descargar sacl_topological_dag.json"
          >
            <Download className="w-3.5 h-3.5 text-zinc-200" />
            <span>JSON</span>
          </button>

          <button
            onClick={handleExportCSV}
            className="px-3 py-2 rounded-2xl bg-black border border-zinc-800 hover:border-zinc-700 text-xs text-zinc-300 flex items-center gap-1.5 transition cursor-pointer"
            title="Descargar sacl_dag_nodes.csv"
          >
            <Download className="w-3.5 h-3.5 text-zinc-200" />
            <span>CSV</span>
          </button>

          <button
            id="btn-open-sprint-designer" onClick={onOpenSprintModal}
            className="px-4 py-2 rounded-2xl bg-white hover:bg-zinc-200 text-black font-semibold font-bold text-xs flex items-center gap-1.5 transition shadow-lg shadow-sm cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Diseñar Sprint</span>
          </button>
        </div>
      </div>

      {/* Validation Result Banner */}
      {validationResult && (
        <div className="p-4 rounded-3xl bg-white/10 border border-zinc-700 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 text-zinc-200 font-bold">
            <CheckCircle2 className="w-4 h-4" />
            <span>{validationResult.message || 'Validación de DAG Acíclico Exitosa (Cero Ciclos)'}</span>
          </div>
          <span className="font-mono text-zinc-400 text-[10px]">
            {dagNodes.length} nodos verificados
          </span>
        </div>
      )}

      {/* Real DAG Nodes Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {dagNodes.map((node, index) => (
          <div
            key={node.id}
            className="p-4 rounded-3xl bg-zinc-950 border border-zinc-800 space-y-3 relative hover:border-zinc-700 transition"
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/5 text-zinc-400">
                Paso {index + 1}
              </span>
              <span
                className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${
                  node.gate_required
                    ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    : 'bg-zinc-900 text-zinc-300 border border-zinc-750'
                }`}
              >
                {node.gate_required ? 'Requiere HITL' : 'Automático'}
              </span>
            </div>

            <div>
              <h3 className="text-xs font-bold text-white">{node.label}</h3>
              <p className="text-[11px] font-mono text-zinc-200 mt-0.5">{node.agent_role}</p>
            </div>

            <div className="space-y-1 pt-2 border-t border-zinc-800 font-mono text-[10px] text-zinc-400">
              <div className="flex justify-between">
                <span>Acción:</span>
                <span className="text-zinc-200">{node.action}</span>
              </div>
              <div className="flex justify-between">
                <span>Depende de:</span>
                <span className="text-zinc-200 truncate max-w-[150px]">
                  {node.dependencies || 'Raíz (Sin dependencia)'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Timeout:</span>
                <span className="text-zinc-200">{node.timeout_sec}s</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Real Backlog Tasks Table / Gantt */}
      <div className="p-6 rounded-3xl bg-zinc-950 border border-zinc-800 space-y-4 shadow-xl">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-4">
          <div className="flex items-center gap-3">
            <Layers className="w-4 h-4 text-zinc-200" />
            <h2 className="text-sm font-bold text-white">
              {viewMode === 'gantt' ? 'Cronograma de Trabajo (Gantt)' : 'Lista de Tareas del Backlog'}
            </h2>
          </div>
          <span className="text-xs text-zinc-400">
            {backlogTasks.length > 0 ? backlogTasks.length : initialTasks.length} tareas sincronizadas
          </span>
        </div>

        {viewMode === 'gantt' && (
          <div className="space-y-3 pt-2">
            {(backlogTasks.length > 0 ? backlogTasks : initialTasks).map((t: any, idx: number) => {
              const progress = t.progress !== undefined ? t.progress : (t.status === 'COMPLETED' ? 100 : 50)
              return (
                <div
                  key={t.key || idx}
                  className="p-3.5 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-2 hover:border-zinc-700 transition"
                >
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-zinc-200 text-[11px] font-bold">
                        {t.key}
                      </span>
                      <span className="font-bold text-white">{t.title}</span>
                    </div>
                    <div className="flex items-center gap-3 text-[11px] font-mono text-zinc-400">
                      <span>{t.phase || t.agent || 'Orquestador'}</span>
                      <span className="text-zinc-200 font-bold">{progress}%</span>
                    </div>
                  </div>

                  <div className="h-1.5 w-full bg-zinc-900 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-white rounded-full transition-all"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {viewMode === 'list' && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-zinc-800 text-[11px] font-mono text-zinc-400">
                  <th className="pb-3 pl-2">Clave</th>
                  <th className="pb-3">Título</th>
                  <th className="pb-3">Fase / Agente</th>
                  <th className="pb-3">Contratos</th>
                  <th className="pb-3 pr-2">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1b2533]/50">
                {(backlogTasks.length > 0 ? backlogTasks : initialTasks).map((t: any, idx: number) => (
                  <tr key={t.key || idx} className="hover:bg-white/[0.02] transition">
                    <td className="py-3 pl-2 font-mono text-zinc-200 font-bold">{t.key}</td>
                    <td className="py-3 font-medium text-white">{t.title}</td>
                    <td className="py-3 text-zinc-400 font-mono text-[11px]">{t.phase || t.agent || 'SACL Core'}</td>
                    <td className="py-3 text-zinc-400 font-mono text-[11px]">
                      {t.contracts ? t.contracts.join(', ') : 'DR-INV-001'}
                    </td>
                    <td className="py-3 pr-2">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-zinc-900 text-zinc-300 border border-zinc-750">
                        {t.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
