import React, { useState } from 'react'
import {
  GitBranch,
  Calendar,
  ListFilter,
  Download,
  Plus,
  CheckCircle2,
  Clock,
  Shield,
  Layers,
  ArrowRight,
} from 'lucide-react'
import type { TaskItem } from '../../types/orchestrator'

interface RoadmapSectionProps {
  tasks: TaskItem[]
  onOpenSprintModal: () => void
}

export const RoadmapSection: React.FC<RoadmapSectionProps> = ({
  tasks,
  onOpenSprintModal,
}) => {
  const [viewMode, setViewMode] = useState<'gantt' | 'list'>('gantt')
  const [filterAgent, setFilterAgent] = useState<string>('all')

  // Real Export to JSON
  const handleExportJSON = () => {
    const dataStr =
      'data:text/json;charset=utf-8,' +
      encodeURIComponent(
        JSON.stringify(
          {
            sprint: 'SACL-SPRINT-2026',
            generated_at: new Date().toISOString(),
            algorithm: 'Kahn DAG Topological Sorter',
            contracts_enforced: ['DR-INV-001', 'DR-PAY-001', 'DR-IDEM-001'],
            waves: [
              { wave: 1, name: 'Arquitectura & Preflight', agents: ['spec-enforcer'] },
              { wave: 2, name: 'Síntesis en Paralelo', agents: ['worktree-coder-alpha', 'worktree-coder-beta'] },
              { wave: 3, name: 'Aseguramiento de Calidad', agents: ['zero-bypass-qa'] },
              { wave: 4, name: 'Gobernanza & Release', agents: ['hitl-sentinel'] },
            ],
            tasks,
          },
          null,
          2
        )
      )
    const downloadAnchor = document.createElement('a')
    downloadAnchor.setAttribute('href', dataStr)
    downloadAnchor.setAttribute('download', 'sacl_roadmap.json')
    document.body.appendChild(downloadAnchor)
    downloadAnchor.click()
    downloadAnchor.remove()
  }

  // Real Export to CSV
  const handleExportCSV = () => {
    const headers = ['Clave', 'Titulo', 'Agente', 'Inicio', 'Fin', 'Progreso', 'Estado']
    const rows = tasks.map((t) => [
      t.key,
      `"${t.title.replace(/"/g, '""')}"`,
      t.agent,
      t.start,
      t.end,
      `${t.progress}%`,
      t.status,
    ])
    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers.join(','), ...rows.map((r) => r.join(','))].join('\n')
    const downloadAnchor = document.createElement('a')
    downloadAnchor.setAttribute('href', encodeURI(csvContent))
    downloadAnchor.setAttribute('download', 'sacl_roadmap.csv')
    document.body.appendChild(downloadAnchor)
    downloadAnchor.click()
    downloadAnchor.remove()
  }

  const wavesData = [
    {
      wave: 1,
      title: 'Oleada 1: Contratos & Preflight',
      agent: 'spec-enforcer',
      tasks: ['Congelar DR-INV-001 & DR-PAY-001', 'Preflight Git Status'],
      status: 'COMPLETADO',
      color: 'emerald',
    },
    {
      wave: 2,
      title: 'Oleada 2: Síntesis en Paralelo',
      agent: 'coder-alpha & coder-beta',
      tasks: ['Lógica de Doble Partida', 'Adaptadores de Idempotencia'],
      status: 'EN PROGRESO',
      color: 'blue',
    },
    {
      wave: 3,
      title: 'Oleada 3: Verificación Zero-Bypass',
      agent: 'zero-bypass-qa',
      tasks: ['Pytest 31/31 Exit 0', 'Simulación de Colisión Concurrente'],
      status: 'PENDIENTE',
      color: 'amber',
    },
    {
      wave: 4,
      title: 'Oleada 4: Gobernanza & Despliegue',
      agent: 'hitl-sentinel',
      tasks: ['Compuerta HMAC-SHA256', 'Deploy Railway (autoDeploy: OFF)'],
      status: 'PENDIENTE',
      color: 'purple',
    },
  ]

  const filteredTasks =
    filterAgent === 'all' ? tasks : tasks.filter((t) => t.agent === filterAgent)

  return (
    <div className="space-y-6">
      {/* Header bar with controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-3xl bg-[#0e141d] border border-[#1b2533]">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold text-white tracking-wide">
              Roadmap Técnico & Topología de Kahn
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              DAG Acíclico (4 Oleadas)
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Planificación estricta de dependencias y paralelismo para la flota de agentes autónomos
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* View mode toggle */}
          <div className="flex items-center p-1 rounded-2xl bg-black/40 border border-[#1b2533]">
            <button
              onClick={() => setViewMode('gantt')}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition flex items-center gap-1.5 ${
                viewMode === 'gantt'
                  ? 'bg-emerald-500 text-black font-bold shadow-md'
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
                  ? 'bg-emerald-500 text-black font-bold shadow-md'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              <ListFilter className="w-3.5 h-3.5" />
              <span>Lista</span>
            </button>
          </div>

          {/* Export buttons */}
          <button
            onClick={handleExportJSON}
            className="px-3 py-2 rounded-2xl bg-[#0a0f16] border border-[#1b2533] hover:border-zinc-700 text-xs text-zinc-300 flex items-center gap-1.5 transition"
            title="Descargar sacl_roadmap.json"
          >
            <Download className="w-3.5 h-3.5 text-blue-400" />
            <span>JSON</span>
          </button>

          <button
            onClick={handleExportCSV}
            className="px-3 py-2 rounded-2xl bg-[#0a0f16] border border-[#1b2533] hover:border-zinc-700 text-xs text-zinc-300 flex items-center gap-1.5 transition"
            title="Descargar sacl_roadmap.csv"
          >
            <Download className="w-3.5 h-3.5 text-emerald-400" />
            <span>CSV</span>
          </button>

          {/* New Sprint Button */}
          <button
            onClick={onOpenSprintModal}
            className="px-4 py-2 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-black font-bold text-xs flex items-center gap-1.5 transition shadow-lg shadow-emerald-500/10 cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Diseñar Sprint</span>
          </button>
        </div>
      </div>

      {/* Visual Kahn DAG Waves Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {wavesData.map((wave) => (
          <div
            key={wave.wave}
            className="p-4 rounded-3xl bg-[#0e141d] border border-[#1b2533] space-y-3 relative overflow-hidden"
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded-full bg-white/5 text-zinc-400">
                Oleada {wave.wave}
              </span>
              <span
                className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${
                  wave.status === 'COMPLETADO'
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : wave.status === 'EN PROGRESO'
                    ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20 animate-pulse'
                    : 'bg-zinc-800 text-zinc-400'
                }`}
              >
                {wave.status}
              </span>
            </div>

            <h3 className="text-xs font-bold text-white">{wave.title}</h3>

            <div className="text-[11px] font-mono text-zinc-400 flex items-center gap-1">
              <GitBranch className="w-3 h-3 text-emerald-400" />
              <span>{wave.agent}</span>
            </div>

            <div className="space-y-1.5 pt-2 border-t border-[#1b2533]">
              {wave.tasks.map((taskName, idx) => (
                <div
                  key={idx}
                  className="p-2 rounded-xl bg-black/40 border border-white/5 text-[11px] text-zinc-300 flex items-center gap-2"
                >
                  <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" />
                  <span className="truncate">{taskName}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Toggle View: Gantt vs List */}
      <div className="p-6 rounded-3xl bg-[#0e141d] border border-[#1b2533] space-y-4 shadow-xl">
        <div className="flex items-center justify-between border-b border-[#1b2533] pb-4">
          <div className="flex items-center gap-3">
            <Layers className="w-4 h-4 text-emerald-400" />
            <h2 className="text-sm font-bold text-white">
              {viewMode === 'gantt' ? 'Línea de Tiempo (Diagrama de Gantt)' : 'Lista de Tareas Operacionales'}
            </h2>
          </div>
          <span className="text-xs text-zinc-400">
            {filteredTasks.length} tareas planificadas
          </span>
        </div>

        {/* Mode: Gantt View */}
        {viewMode === 'gantt' && (
          <div className="space-y-3 pt-2">
            {filteredTasks.map((task) => (
              <div
                key={task.id}
                className="p-3.5 rounded-2xl bg-[#090e16] border border-[#1b2533] space-y-2 hover:border-zinc-700 transition"
              >
                <div className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-emerald-400 text-[11px] font-bold">
                      {task.key}
                    </span>
                    <span className="font-bold text-white">{task.title}</span>
                  </div>
                  <div className="flex items-center gap-3 text-[11px] font-mono text-zinc-400">
                    <span>{task.agent}</span>
                    <span>
                      {task.start} &rarr; {task.end}
                    </span>
                    <span className="text-emerald-400 font-bold">{task.progress}%</span>
                  </div>
                </div>

                {/* Visual Gantt Bar */}
                <div className="h-2 w-full bg-zinc-900 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      task.progress === 100
                        ? 'bg-emerald-500'
                        : task.progress > 0
                        ? 'bg-blue-500'
                        : 'bg-zinc-700'
                    }`}
                    style={{ width: `${task.progress}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Mode: List View */}
        {viewMode === 'list' && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#1b2533] text-[11px] font-mono text-zinc-400">
                  <th className="pb-3 pl-2">Clave</th>
                  <th className="pb-3">Título</th>
                  <th className="pb-3">Agente Responsable</th>
                  <th className="pb-3">Plazo</th>
                  <th className="pb-3">Progreso</th>
                  <th className="pb-3 pr-2">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1b2533]/50">
                {filteredTasks.map((task) => (
                  <tr key={task.id} className="hover:bg-white/[0.02] transition">
                    <td className="py-3 pl-2 font-mono text-emerald-400 font-bold">{task.key}</td>
                    <td className="py-3 font-medium text-white">{task.title}</td>
                    <td className="py-3 text-zinc-400 font-mono">{task.agent}</td>
                    <td className="py-3 text-zinc-500 text-[11px]">
                      {task.start} - {task.end}
                    </td>
                    <td className="py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-emerald-500 rounded-full"
                            style={{ width: `${task.progress}%` }}
                          />
                        </div>
                        <span className="font-mono text-[10px] text-zinc-400">{task.progress}%</span>
                      </div>
                    </td>
                    <td className="py-3 pr-2">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-mono ${
                          task.status === 'Completada'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : task.status === 'En progreso'
                            ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                            : 'bg-zinc-800 text-zinc-400'
                        }`}
                      >
                        {task.status}
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
