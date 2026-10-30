import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  MarkerType,
  Position,
  Handle,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import React, { useState, useEffect } from 'react'
import {
  GitBranch,
  Calendar,
  ListFilter,
  Download,
  CheckCircle2,
  Layers,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  Terminal,
  Clock,
  User,
  ArrowRight,
  ShieldAlert,
} from 'lucide-react'
import type { TaskItem } from '../../types/orchestrator'
import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerDescription,
  DrawerFooter,
  DrawerClose,
} from '../ui/drawer'
import { StatusBadge } from '../ui/status-badge'

interface RoadmapSectionProps {
  tasks: TaskItem[]
  onOpenSprintModal?: () => void
}

interface DagNode {
  id: string
  label: string
  agent_role: string
  action: string
  gate_required: boolean
  timeout_sec: number
  dependencies: string
  status?: 'IDLE' | 'RUNNING' | 'COMPLETED' | 'ERROR'
}

const AgentStepNode = ({ data }: { data: any }) => {
  const isGate = data.gate_required
  const status = data.status || 'IDLE'

  let borderStyle = 'border-white/10 hover:border-zinc-500'
  if (status === 'RUNNING') {
    borderStyle = 'border-cyan-400 shadow-[0_0_15px_rgba(34,211,238,0.3)] ring-1 ring-cyan-400/50'
  } else if (status === 'ERROR') {
    borderStyle = 'border-rose-500 shadow-[0_0_15px_rgba(244,63,94,0.3)]'
  } else if (isGate) {
    borderStyle = 'border-amber-500/40 hover:border-amber-400'
  }

  return (
    <div
      onClick={data.onSelect}
      className={`p-3.5 rounded-2xl bg-[#0C0C0E] border ${borderStyle} shadow-2xl min-w-[220px] max-w-[260px] text-left transition select-none cursor-pointer group`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!bg-zinc-400 !w-2.5 !h-2.5 !border-zinc-900"
      />
      <div className="flex items-center justify-between gap-2 mb-1.5">
        <span className="text-[9px] font-mono px-2 py-0.5 rounded-full bg-white/10 text-zinc-300">
          {data.step}
        </span>
        <span
          className={`text-[9px] font-mono px-2 py-0.5 rounded-full ${
            isGate
              ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
              : 'bg-zinc-900 text-zinc-400 border border-zinc-800'
          }`}
        >
          {isGate ? 'Requiere Firma' : 'Automático'}
        </span>
      </div>
      <div className="font-bold text-white text-xs truncate group-hover:text-cyan-300 transition" title={data.label}>
        {data.label}
      </div>
      <div className="text-[10px] font-mono text-zinc-400 mt-0.5 truncate">
        {data.agent_role}
      </div>
      <div className="mt-2 pt-2 border-t border-zinc-800/80 flex items-center justify-between text-[9px] font-mono text-zinc-500">
        <span className="flex items-center gap-1">
          <Clock className="w-2.5 h-2.5 text-zinc-400" />
          {data.timeout_sec}s máx
        </span>
        <span className="text-zinc-300">{data.action}</span>
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-zinc-400 !w-2.5 !h-2.5 !border-zinc-900"
      />
    </div>
  )
}

const nodeTypes = {
  agentStep: AgentStepNode,
}

export const RoadmapSection: React.FC<RoadmapSectionProps> = ({
  tasks: initialTasks,
}) => {
  const [viewMode, setViewMode] = useState<'flow' | 'gantt' | 'list'>('flow')
  const [dagData, setDagData] = useState<any>(null)
  const [dagNodes, setDagNodes] = useState<DagNode[]>([])
  const [backlogTasks, setBacklogTasks] = useState<any[]>([])
  const [validating, setValidating] = useState(false)
  const [validationResult, setValidationResult] = useState<any>(null)
  const [showTechExport, setShowTechExport] = useState(false)

  // Drawer detail state for interactive DAG exploration
  const [selectedNode, setSelectedNode] = useState<DagNode | null>(null)
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)

  const loadDag = async () => {
    try {
      const res = await fetch('/api/campaigns/designer')
      const data = await res.json()
      if (data && data.nodes) {
        setDagData(data)
        setDagNodes(data.nodes)
      }
    } catch (e) {
      console.warn('Error loading workflow sequence:', e)
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

  const handleValidateSequence = async () => {
    setValidating(true)
    try {
      const res = await fetch('/api/campaigns/designer/validate', { method: 'POST' })
      const data = await res.json()
      setValidationResult(data)
    } catch (e: any) {
      setValidationResult({
        valid: false,
        message: 'No se pudo verificar el orden de etapas: ' + e.message,
      })
    } finally {
      setValidating(false)
    }
  }

  const handleOpenNodeDetail = (node: DagNode) => {
    setSelectedNode(node)
    setIsDrawerOpen(true)
  }

  const handleExportJSON = () => {
    const dataStr =
      'data:text/json;charset=utf-8,' +
      encodeURIComponent(JSON.stringify(dagData || { nodes: dagNodes }, null, 2))
    const a = document.createElement('a')
    a.href = dataStr
    a.download = 'mapa_flujo_trabajo.json'
    document.body.appendChild(a)
    a.click()
    a.remove()
  }

  const handleExportCSV = () => {
    const headers = [
      'ID Etapa',
      'Etiqueta',
      'Especialista',
      'Accion',
      'Requiere Aprobacion',
      'Dependencias',
    ]
    const rows = dagNodes.map((n) => [
      n.id,
      `"${n.label.replace(/"/g, '""')}"`,
      n.agent_role,
      n.action,
      n.gate_required ? 'SI' : 'NO',
      `"${n.dependencies || 'Inicio'}"`,
    ])
    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((r) => r.join(','))].join('\n')
    const a = document.createElement('a')
    a.href = encodeURI(csvContent)
    a.download = 'etapas_flujo_trabajo.csv'
    document.body.appendChild(a)
    a.click()
    a.remove()
  }

  const flowNodes = dagNodes.map((n, idx) => {
    const col = idx % 3
    const row = Math.floor(idx / 3)
    return {
      id: n.id,
      type: 'agentStep',
      position: { x: col * 280 + 40, y: row * 160 + 40 },
      data: {
        step: `Etapa ${idx + 1}`,
        label: n.label,
        agent_role: n.agent_role,
        action: n.action,
        gate_required: n.gate_required,
        timeout_sec: n.timeout_sec,
        status: idx === 0 ? 'COMPLETED' : idx === 1 ? 'RUNNING' : 'IDLE',
        onSelect: () => handleOpenNodeDetail(n),
      },
    }
  })

  const flowEdges = dagNodes.flatMap((n) => {
    if (!n.dependencies) return []
    const rawDeps: any = n.dependencies
    const deps: string[] = Array.isArray(rawDeps)
      ? rawDeps
      : typeof rawDeps === 'string'
      ? rawDeps
          .split(',')
          .map((d: string) => d.trim())
          .filter(Boolean)
      : []
    return deps.map((d) => ({
      id: `e-${d}-${n.id}`,
      source: d,
      target: n.id,
      animated: true,
      style: { stroke: '#38bdf8', strokeWidth: 1.5 },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#38bdf8' },
    }))
  })

  // Filter tasks belonging to the currently selected node
  const filteredSubtasks = selectedNode
    ? (backlogTasks.length > 0 ? backlogTasks : initialTasks).filter((t: any) => {
        const titleMatch = t.title?.toLowerCase().includes(selectedNode.label.toLowerCase())
        const phaseMatch = t.phase?.toLowerCase().includes(selectedNode.agent_role.toLowerCase())
        const keyMatch = t.key?.toLowerCase().includes(selectedNode.id.toLowerCase())
        return titleMatch || phaseMatch || keyMatch
      })
    : []

  return (
    <div className="space-y-6 max-w-6xl mx-auto text-left pb-12">
      {/* 1. Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 sm:p-6 rounded-3xl bg-[#0C0C0E] border border-white/5 shadow-xl">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-lg font-extrabold text-white tracking-tight">
              Mapa de Flujo y Secuencia de DAGs
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-zinc-900 text-zinc-200 border border-zinc-750 font-bold">
              {dagNodes.length} Nodos Conectados
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Haz clic sobre cualquier etapa o nodo del grafo para abrir instantáneamente el panel de subtareas asociadas.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {/* View Mode Switcher */}
          <div className="flex items-center p-1 rounded-2xl bg-black border border-zinc-800">
            <button
              type="button"
              onClick={() => setViewMode('flow')}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition flex items-center gap-1.5 cursor-pointer ${
                viewMode === 'flow'
                  ? 'bg-zinc-800 text-white font-bold'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              <GitBranch className="w-3.5 h-3.5" />
              <span>Grafo Interactivo</span>
            </button>
            <button
              type="button"
              onClick={() => setViewMode('gantt')}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition flex items-center gap-1.5 cursor-pointer ${
                viewMode === 'gantt'
                  ? 'bg-zinc-800 text-white font-bold'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              <Calendar className="w-3.5 h-3.5" />
              <span>Cronograma</span>
            </button>
            <button
              type="button"
              onClick={() => setViewMode('list')}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition flex items-center gap-1.5 cursor-pointer ${
                viewMode === 'list'
                  ? 'bg-zinc-800 text-white font-bold'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              <ListFilter className="w-3.5 h-3.5" />
              <span>Tabla</span>
            </button>
          </div>

          <button
            type="button"
            onClick={handleValidateSequence}
            disabled={validating}
            className="px-4 py-2 rounded-2xl bg-white hover:bg-zinc-200 text-black font-extrabold text-xs flex items-center gap-1.5 transition cursor-pointer shadow-sm"
          >
            <ShieldCheck className="w-4 h-4 text-black" />
            <span>{validating ? 'Verificando...' : 'Verificar Orden de Etapas'}</span>
          </button>
        </div>
      </div>

      {/* Validation Result Banner */}
      {validationResult && (
        <div className="p-4 rounded-2xl bg-emerald-950/30 border border-emerald-500/40 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 text-emerald-200 font-bold">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>
              {validationResult.message ||
                'Secuencia de etapas verificada correctamente (sin bloqueos circulares).'}
            </span>
          </div>
          <span className="font-mono text-emerald-300 text-[10px]">
            {dagNodes.length} etapas listas
          </span>
        </div>
      )}

      {/* Interactive Sequence Canvas */}
      {viewMode === 'flow' && (
        <div className="h-[440px] w-full rounded-3xl bg-[#09090B] border border-white/5 overflow-hidden relative shadow-2xl">
          <div className="absolute top-3 left-4 z-10 flex items-center gap-2 px-3 py-1.5 rounded-xl bg-black/80 backdrop-blur-md border border-zinc-800 text-[11px] text-zinc-300">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            <span>Grafo Interactivo: Haz clic en cualquier nodo para ver sus subtareas</span>
          </div>
          <ReactFlow
            nodes={flowNodes}
            edges={flowEdges}
            nodeTypes={nodeTypes}
            onNodeClick={(_, node) => {
              const original = dagNodes.find((n) => n.id === node.id)
              if (original) handleOpenNodeDetail(original)
            }}
            fitView
            className="bg-[#09090b]"
          >
            <Background color="#1f1f23" gap={20} size={1} />
            <Controls className="!bg-zinc-900 !border-zinc-800 !text-white [&>button]:!border-zinc-800 [&>button]:!fill-white" />
            <MiniMap
              nodeColor="#3f3f46"
              maskColor="rgba(0, 0, 0, 0.7)"
              className="!bg-zinc-950 !border !border-zinc-800 !rounded-xl"
            />
          </ReactFlow>
        </div>
      )}

      {/* Stage Cards Grid with Click-to-Open Drawer */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {dagNodes.map((node, index) => (
          <div
            key={node.id}
            onClick={() => handleOpenNodeDetail(node)}
            className="p-4 rounded-2xl bg-[#0C0C0E] border border-white/5 space-y-3 hover:border-cyan-500/50 hover:bg-[#121215] transition cursor-pointer shadow-lg group"
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-zinc-900 text-zinc-300">
                Etapa {index + 1}
              </span>
              <span
                className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${
                  node.gate_required
                    ? 'bg-amber-500/15 text-amber-300 border border-amber-500/30'
                    : 'bg-zinc-900 text-zinc-400 border border-zinc-800'
                }`}
              >
                {node.gate_required ? 'Requiere tu Autorización' : 'Paso Automático'}
              </span>
            </div>

            <div>
              <h3 className="text-xs font-bold text-white group-hover:text-cyan-300 transition">
                {node.label}
              </h3>
              <p className="text-[11px] text-zinc-400 mt-0.5">
                Responsable: <strong className="text-zinc-200">{node.agent_role}</strong>
              </p>
            </div>

            <div className="space-y-1 pt-2 border-t border-zinc-850 text-[11px] text-zinc-400">
              <div className="flex justify-between">
                <span>Tarea:</span>
                <span className="text-zinc-200 font-mono">{node.action}</span>
              </div>
              <div className="flex justify-between">
                <span>Paso previo requerido:</span>
                <span className="text-zinc-200 truncate max-w-[150px]">
                  {node.dependencies || 'Inicio del flujo'}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Gantt / Table View */}
      {(viewMode === 'gantt' || viewMode === 'list') && (
        <div className="p-6 rounded-3xl bg-[#0C0C0E] border border-white/5 space-y-4">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-4">
            <div className="flex items-center gap-2.5">
              <Layers className="w-4 h-4 text-zinc-200" />
              <h2 className="text-sm font-bold text-white">
                {viewMode === 'gantt' ? 'Cronograma de Avance' : 'Detalle de Requerimientos'}
              </h2>
            </div>
            <span className="text-xs text-zinc-400">
              {backlogTasks.length > 0 ? backlogTasks.length : initialTasks.length} elementos
            </span>
          </div>

          {viewMode === 'gantt' ? (
            <div className="space-y-3">
              {(backlogTasks.length > 0 ? backlogTasks : initialTasks).map(
                (t: any, idx: number) => {
                  const progress =
                    t.progress !== undefined ? t.progress : t.status === 'COMPLETED' ? 100 : 50
                  return (
                    <div
                      key={t.key || idx}
                      className="p-3.5 rounded-2xl bg-black border border-zinc-800 space-y-2"
                    >
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-bold text-white">{t.title}</span>
                        <span className="text-zinc-300 font-mono font-bold">{progress}%</span>
                      </div>
                      <div className="h-1.5 w-full bg-zinc-900 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-emerald-400 rounded-full transition-all"
                          style={{ width: `${progress}%` }}
                        />
                      </div>
                    </div>
                  )
                }
              )}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-zinc-800 text-[11px] text-zinc-400">
                    <th className="pb-2.5">Referencia</th>
                    <th className="pb-2.5">Objetivo</th>
                    <th className="pb-2.5">Responsable</th>
                    <th className="pb-2.5 text-right">Estado</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-900">
                  {(backlogTasks.length > 0 ? backlogTasks : initialTasks).map(
                    (t: any, idx: number) => (
                      <tr key={t.key || idx}>
                        <td className="py-2.5 font-mono text-zinc-300 font-bold">{t.key}</td>
                        <td className="py-2.5 text-white font-medium">{t.title}</td>
                        <td className="py-2.5 text-zinc-400">{t.phase || 'Equipo Principal'}</td>
                        <td className="py-2.5 text-right">
                          <span className="px-2 py-0.5 rounded-full text-[10px] bg-zinc-900 text-zinc-300 border border-zinc-800">
                            {t.status}
                          </span>
                        </td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Layer 2 Progressive Disclosure */}
      <div className="rounded-2xl bg-[#0C0C0E] border border-white/5 overflow-hidden">
        <button
          type="button"
          onClick={() => setShowTechExport(!showTechExport)}
          className="w-full p-4 flex items-center justify-between hover:bg-zinc-900/40 transition cursor-pointer text-left"
        >
          <span className="flex items-center gap-2 text-xs font-bold text-zinc-300">
            <Terminal className="w-4 h-4 text-zinc-500" />
            <span>Opciones de Exportación Técnica (JSON / CSV)</span>
          </span>
          {showTechExport ? (
            <ChevronUp className="w-4 h-4 text-zinc-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-zinc-400" />
          )}
        </button>

        {showTechExport && (
          <div className="p-4 pt-0 border-t border-zinc-800/80 flex items-center gap-3 mt-3">
            <button
              type="button"
              onClick={handleExportJSON}
              className="px-3.5 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-xs text-zinc-200 flex items-center gap-1.5 cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Descargar Estructura JSON</span>
            </button>
            <button
              type="button"
              onClick={handleExportCSV}
              className="px-3.5 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-xs text-zinc-200 flex items-center gap-1.5 cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Descargar Tabla CSV</span>
            </button>
          </div>
        )}
      </div>

      {/* Interactive Drawer for Selected Node Details */}
      <Drawer open={isDrawerOpen} onOpenChange={setIsDrawerOpen}>
        <DrawerContent side="right">
          {selectedNode && (
            <div className="space-y-5 flex flex-col h-full text-left">
              <DrawerHeader>
                <div className="flex items-center gap-2 mb-1">
                  <StatusBadge
                    status={selectedNode.gate_required ? 'WAITING' : 'IDLE'}
                    label={selectedNode.gate_required ? 'Requiere Aprobación' : 'Paso Automático'}
                  />
                  <span className="text-[10px] font-mono text-zinc-400">
                    ID: {selectedNode.id}
                  </span>
                </div>
                <DrawerTitle>{selectedNode.label}</DrawerTitle>
                <DrawerDescription>
                  Especialista asignado: {selectedNode.agent_role}
                </DrawerDescription>
              </DrawerHeader>

              <div className="space-y-4 flex-1 overflow-y-auto custom-scroll pr-1">
                {/* Node Parameters */}
                <div className="p-4 rounded-2xl bg-black border border-white/5 space-y-2.5 font-mono text-xs">
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Acción a Ejecutar:</span>
                    <span className="text-zinc-200 font-bold">{selectedNode.action}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Tiempo Máximo (Timeout):</span>
                    <span className="text-sky-400">{selectedNode.timeout_sec}s</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Depende de (Predecesores):</span>
                    <span className="text-emerald-400">{selectedNode.dependencies || 'Ninguna (Inicio)'}</span>
                  </div>
                </div>

                {/* Associated Backlog Subtasks */}
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
                    Subtareas Asignadas a este Nodo ({filteredSubtasks.length}):
                  </h4>

                  {filteredSubtasks.length > 0 ? (
                    <div className="space-y-2">
                      {filteredSubtasks.map((task: any, idx: number) => (
                        <div
                          key={task.key || idx}
                          className="p-3 rounded-xl bg-zinc-900/60 border border-white/5 space-y-1 text-xs"
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-mono text-[11px] font-bold text-sky-400">
                              {task.key || `#${idx + 1}`}
                            </span>
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-zinc-800 text-zinc-300">
                              {task.status || 'En progreso'}
                            </span>
                          </div>
                          <p className="text-white font-medium">{task.title}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-4 rounded-xl bg-zinc-900/30 border border-white/5 text-center text-xs text-zinc-500">
                      No hay tareas individuales filtradas para esta etapa específica en el backlog actual.
                    </div>
                  )}
                </div>
              </div>

              <DrawerFooter>
                <DrawerClose asChild>
                  <button
                    type="button"
                    className="w-full py-2.5 rounded-xl bg-white hover:bg-zinc-200 text-black font-extrabold text-xs cursor-pointer shadow-md transition"
                  >
                    Entendido / Cerrar Panel
                  </button>
                </DrawerClose>
              </DrawerFooter>
            </div>
          )}
        </DrawerContent>
      </Drawer>
    </div>
  )
}
