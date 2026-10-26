import React, { useState } from 'react'
import {
  Zap,
  Cpu,
  CheckCircle2,
  AlertTriangle,
  Play,
  GitMerge,
  Download,
  Database,
  ArrowRight,
  Sparkles,
  Layers,
} from 'lucide-react'
import type { TaskItem, AgentItem, CommitItem, Project, ActivityEvent } from '../types/orchestrator'
import { LogTerminal } from './LogTerminal'

interface CenterDashboardProps {
  tasks: TaskItem[]
  agents: AgentItem[]
  commits: CommitItem[]
  projects: Project[]
  events: ActivityEvent[]
  activeSprintTitle?: string
  activeSprintDesc?: string
  onOpenSprintModal: () => void
  onNavigateSection: (section: string) => void
}

export const CenterDashboard: React.FC<CenterDashboardProps> = ({
  tasks,
  agents,
  commits,
  projects,
  events,
  activeSprintTitle = 'Sprint 1 — MVP E-commerce (DR-INV-001 & DR-PAY-001)',
  activeSprintDesc = 'Flujo de venta atómica, contratos congelados SellableUnit y ledger de doble partida sin sobreventa.',
  onOpenSprintModal,
  onNavigateSection,
}) => {
  const [viewMode, setViewMode] = useState<'gantt' | 'lista'>('gantt')

  const completedCount = tasks.filter((t) => t.status === 'Completada').length
  const runningCount = tasks.filter((t) => t.status === 'En progreso').length
  const activeAgentsCount = agents.filter((a) => a.status === 'Activo').length

  // Real Export Handler
  const handleExportRoadmap = () => {
    const dataStr =
      'data:text/json;charset=utf-8,' +
      encodeURIComponent(
        JSON.stringify(
          {
            sprint: activeSprintTitle,
            exported_at: new Date().toISOString(),
            methodology: 'SolidBit SDLC (WF-02 / WF-03)',
            contracts: ['DR-INV-001', 'DR-PAY-001', 'DR-IDEM-001'],
            tasks,
          },
          null,
          2
        )
      )
    const dl = document.createElement('a')
    dl.setAttribute('href', dataStr)
    dl.setAttribute('download', 'sacl_sprint_roadmap.json')
    document.body.appendChild(dl)
    dl.click()
    dl.remove()
  }

  return (
    <div id="sec-dashboard" className="space-y-6 max-w-7xl mx-auto">
      {/* 1. SPRINT HERO BANNER (CLEAN & MINIMALIST) */}
      <div className="p-5 sm:p-6 rounded-2xl sm:rounded-3xl bg-[#0c121a] border border-[#1b2533] space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1.5 flex-1">
            <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
              <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold">
                SPRINT ACTIVO
              </span>
              <span className="text-zinc-500">&bull;</span>
              <span className="text-zinc-400">24 Oct &rarr; 07 Nov 2026</span>
              <span className="text-zinc-500">&bull;</span>
              <span className="text-zinc-400 font-semibold">SolidBit SDLC Metodología</span>
            </div>

            <h1 className="text-base sm:text-xl font-extrabold text-white tracking-tight">
              {activeSprintTitle}
            </h1>
            <p className="text-xs sm:text-sm text-zinc-400 max-w-3xl leading-relaxed">
              {activeSprintDesc}
            </p>
          </div>

          <div className="flex items-center gap-2.5 shrink-0">
            <button
              onClick={onOpenSprintModal}
              className="w-full sm:w-auto px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-bold text-xs flex items-center justify-center gap-2 transition cursor-pointer shadow-lg shadow-emerald-500/20"
            >
              <Play className="w-3.5 h-3.5 fill-black" />
              <span>Ejecutar Oleadas</span>
            </button>
          </div>
        </div>

        {/* Global Progress Line */}
        <div className="space-y-1.5 pt-1 border-t border-[#1b2533]/60">
          <div className="flex items-center justify-between text-xs">
            <span className="text-zinc-400 font-medium text-[11px]">Progreso general del Sprint</span>
            <span className="text-emerald-400 font-bold font-mono">
              {Math.round((completedCount / (tasks.length || 1)) * 100)}%
            </span>
          </div>
          <div className="h-1.5 w-full bg-[#070a0e] rounded-full overflow-hidden">
            <div
              className="h-full bg-emerald-500 rounded-full transition-all duration-500 shadow-sm"
              style={{ width: `${(completedCount / (tasks.length || 1)) * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* 2. CORE METRICS (4 CLEAN HIGH-CONTRAST CARDS) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        {/* Metric 1: Flota de Agentes */}
        <div
          onClick={() => onNavigateSection('agents')}
          className="p-4 rounded-2xl bg-[#0c121a] border border-[#1b2533] space-y-2.5 cursor-pointer hover:border-emerald-500/40 transition group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-zinc-400 group-hover:text-zinc-200 transition">
              Flota de Agentes
            </span>
            <div className="w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <Zap className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-lg sm:text-xl font-extrabold text-white font-mono">
              {activeAgentsCount} / {agents.length}
            </span>
            <span className="text-[10px] font-mono text-emerald-400">Activos</span>
          </div>
          <div className="w-full bg-[#1b2533] h-1 rounded-full overflow-hidden">
            <div
              className="bg-emerald-500 h-full rounded-full transition-all"
              style={{ width: `${(activeAgentsCount / (agents.length || 1)) * 100}%` }}
            />
          </div>
        </div>

        {/* Metric 2: Tareas en Ejecución */}
        <div
          onClick={() => onNavigateSection('roadmap')}
          className="p-4 rounded-2xl bg-[#0c121a] border border-[#1b2533] space-y-2.5 cursor-pointer hover:border-blue-500/40 transition group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-zinc-400 group-hover:text-zinc-200 transition">
              En Ejecución
            </span>
            <div className="w-7 h-7 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
              <Cpu className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-lg sm:text-xl font-extrabold text-white font-mono">
              {runningCount}
            </span>
            <span className="text-[10px] font-mono text-blue-400">Oleadas Kahn</span>
          </div>
          <div className="w-full bg-[#1b2533] h-1 rounded-full overflow-hidden">
            <div
              className="bg-blue-500 h-full rounded-full transition-all"
              style={{ width: `${runningCount > 0 ? 60 : 0}%` }}
            />
          </div>
        </div>

        {/* Metric 3: Tareas Completadas */}
        <div
          onClick={() => onNavigateSection('roadmap')}
          className="p-4 rounded-2xl bg-[#0c121a] border border-[#1b2533] space-y-2.5 cursor-pointer hover:border-emerald-500/40 transition group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-zinc-400 group-hover:text-zinc-200 transition">
              Completadas
            </span>
            <div className="w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <CheckCircle2 className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-lg sm:text-xl font-extrabold text-white font-mono">
              {completedCount} / {tasks.length}
            </span>
            <span className="text-[10px] font-mono text-zinc-500">
              {Math.round((completedCount / (tasks.length || 1)) * 100)}%
            </span>
          </div>
          <div className="w-full bg-[#1b2533] h-1 rounded-full overflow-hidden">
            <div
              className="bg-emerald-500 h-full rounded-full transition-all"
              style={{ width: `${(completedCount / (tasks.length || 1)) * 100}%` }}
            />
          </div>
        </div>

        {/* Metric 4: Compuertas HITL Soberanas */}
        <div
          onClick={() => onNavigateSection('executions')}
          className="p-4 rounded-2xl bg-[#0c121a] border border-[#1b2533] space-y-2.5 cursor-pointer hover:border-amber-500/40 transition group"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-zinc-400 group-hover:text-zinc-200 transition">
              Compuertas HITL
            </span>
            <div className="w-7 h-7 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <AlertTriangle className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-lg sm:text-xl font-extrabold text-white font-mono">
              1 Pendiente
            </span>
            <span className="text-[10px] font-mono text-amber-400">HMAC-SHA256</span>
          </div>
          <div className="w-full bg-[#1b2533] h-1 rounded-full overflow-hidden">
            <div className="bg-amber-500 h-full rounded-full transition-all" style={{ width: '100%' }} />
          </div>
        </div>
      </div>

      {/* 3. ROADMAP & GANTT EXECUTION CARD */}
      <div className="p-5 sm:p-6 rounded-2xl sm:rounded-3xl bg-[#0c121a] border border-[#1b2533] space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1b2533] pb-4">
          <div>
            <div className="flex items-center gap-2">
              <GitMerge className="w-4 h-4 text-emerald-400" />
              <h2 className="text-sm sm:text-base font-bold text-white">
                Plan de Trabajo del Sprint (Topología de Kahn)
              </h2>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              Particionado acíclico de tareas sincronizado con SQLite WAL y contratos congelados.
            </p>
          </div>

          <div className="flex items-center gap-2.5 shrink-0">
            {/* View Mode Toggle */}
            <div className="flex items-center p-0.5 rounded-xl bg-black/60 border border-zinc-800">
              <button
                type="button"
                onClick={() => setViewMode('gantt')}
                className={`px-3 py-1 rounded-lg text-xs font-mono transition cursor-pointer ${
                  viewMode === 'gantt'
                    ? 'bg-emerald-500 text-black font-bold'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                Gantt
              </button>
              <button
                type="button"
                onClick={() => setViewMode('lista')}
                className={`px-3 py-1 rounded-lg text-xs font-mono transition cursor-pointer ${
                  viewMode === 'lista'
                    ? 'bg-emerald-500 text-black font-bold'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                Lista
              </button>
            </div>

            {/* Export Roadmap */}
            <button
              type="button"
              onClick={handleExportRoadmap}
              className="px-3 py-1.5 rounded-xl border border-zinc-800 hover:border-zinc-700 bg-black/40 text-xs font-medium text-zinc-300 hover:text-white flex items-center gap-1.5 cursor-pointer transition"
              title="Descargar JSON del Roadmap"
            >
              <Download className="w-3.5 h-3.5 text-emerald-400" />
              <span>Exportar</span>
            </button>
          </div>
        </div>

        {/* View Mode: Gantt */}
        {viewMode === 'gantt' && (
          <div className="space-y-2.5 pt-1">
            {tasks.map((task) => (
              <div
                key={task.id}
                className="p-3 sm:p-3.5 rounded-xl sm:rounded-2xl bg-[#070b10] border border-[#1b2533] space-y-2 hover:border-zinc-700 transition"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-emerald-400 text-[11px] font-bold shrink-0">
                      {task.key}
                    </span>
                    <span className="font-bold text-white">{task.title}</span>
                  </div>
                  <div className="flex flex-wrap items-center gap-2 text-[10px] sm:text-[11px] font-mono text-zinc-400">
                    <span className="px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-300">
                      {task.agent}
                    </span>
                    <span>
                      {task.start} &rarr; {task.end}
                    </span>
                    <span className="text-emerald-400 font-bold">{task.progress}%</span>
                  </div>
                </div>

                <div className="h-1.5 w-full bg-zinc-900 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
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

        {/* View Mode: List */}
        {viewMode === 'lista' && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#1b2533] text-zinc-400 text-[11px] font-semibold">
                  <th className="pb-3 pl-1">Tarea / Identificador</th>
                  <th className="pb-3">Responsable</th>
                  <th className="pb-3">Plazo</th>
                  <th className="pb-3 min-w-[120px]">Progreso</th>
                  <th className="pb-3 text-right pr-2">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1b2533]/60">
                {tasks.map((t) => (
                  <tr key={t.id} className="hover:bg-white/[0.02] transition">
                    <td className="py-3 pl-1">
                      <div className="font-semibold text-white">{t.title}</div>
                      <div className="text-[10px] font-mono text-emerald-400">{t.key}</div>
                    </td>
                    <td className="py-3">
                      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-[#16231d] border border-emerald-500/30 text-emerald-400 text-[11px] font-medium">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                        {t.agent}
                      </span>
                    </td>
                    <td className="py-3 text-zinc-400 font-mono text-[11px]">
                      {t.start} - {t.end}
                    </td>
                    <td className="py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-20 bg-[#1b2533] h-1.5 rounded-full overflow-hidden">
                          <div
                            className="bg-emerald-500 h-full rounded-full transition-all"
                            style={{ width: `${t.progress}%` }}
                          />
                        </div>
                        <span className="text-[11px] font-mono text-zinc-400">{t.progress}%</span>
                      </div>
                    </td>
                    <td className="py-3 text-right pr-2">
                      <span
                        className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold ${
                          t.status === 'Completada'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                            : t.status === 'En progreso'
                            ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30'
                            : 'bg-zinc-800 text-zinc-400 border border-zinc-700'
                        }`}
                      >
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

      {/* 4. HIGH-DENSITY STRUCTURED LOG TERMINAL (INCORPORATED NATIVELY) */}
      <LogTerminal
        initialEvents={events}
        onOpenGate={() => onNavigateSection('executions')}
      />
    </div>
  )
}
