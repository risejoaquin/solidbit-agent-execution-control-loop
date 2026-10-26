import React, { useState, useEffect } from 'react'
import {
  Layers,
  Sparkles,
  Play,
  Search,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  Terminal,
  ShieldCheck,
  FolderGit2,
  FileCode,
  RotateCw,
} from 'lucide-react'
import { ToolCallCard, type ToolCallData } from '../ToolCallCard'

export interface SkillItem {
  id: string
  name: string
  description: string
  scope: 'workspace' | 'global' | 'builtin' | 'plugin'
  skill_dir: string
  skill_file: string
  slash_command: string
  parameters: Array<{
    name: string
    label: string
    type: string
    required?: boolean
    placeholder?: string
    default?: any
  }>
  has_scripts?: boolean
  has_references?: boolean
}

export const WorkflowsSection: React.FC = () => {
  const [skills, setSkills] = useState<SkillItem[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [selectedScope, setSelectedScope] = useState<string>('all')

  // Execution Modal state
  const [activeSkill, setActiveSkill] = useState<SkillItem | null>(null)
  const [executing, setExecuting] = useState<boolean>(false)
  const [paramGoal, setParamGoal] = useState<string>('')
  const [strictMode, setStrictMode] = useState<boolean>(true)
  const [executionResult, setExecutionResult] = useState<any | null>(null)

  const loadSkills = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/skills')
      const data = await res.json()
      if (data.skills) {
        setSkills(data.skills)
      }
    } catch (e) {
      console.warn('Error loading skills:', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSkills()
  }, [])

  const filteredSkills = skills.filter((s) => {
    const matchesQuery =
      s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.id.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesScope = selectedScope === 'all' || s.scope === selectedScope
    return matchesQuery && matchesScope
  })

  const handleOpenLaunchModal = (skill: SkillItem) => {
    setActiveSkill(skill)
    setParamGoal('')
    setStrictMode(true)
    setExecutionResult(null)
  }

  const handleExecuteSkill = async () => {
    if (!activeSkill) return
    setExecuting(true)
    setExecutionResult(null)
    try {
      const res = await fetch('/api/skills/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          skill_id: activeSkill.id,
          params: {
            goal: paramGoal || `Ejecutar workflow ${activeSkill.name}`,
            strict_mode: strictMode,
          },
        }),
      })
      const data = await res.json()
      setExecutionResult(data)
    } catch (e: any) {
      alert('Error ejecutando skill: ' + e.message)
    } finally {
      setExecuting(false)
    }
  }

  const getScopeBadge = (scope: string) => {
    switch (scope) {
      case 'workspace':
        return (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full font-bold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            WORKSPACE
          </span>
        )
      case 'global':
        return (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full font-bold bg-blue-500/15 text-blue-400 border border-blue-500/30">
            GLOBAL
          </span>
        )
      case 'plugin':
        return (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full font-bold bg-purple-500/15 text-purple-400 border border-purple-500/30">
            PLUGIN
          </span>
        )
      default:
        return (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full font-bold bg-zinc-800 text-zinc-400 border border-zinc-700">
            BUILTIN
          </span>
        )
    }
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto animate-fade-in">
      {/* 1. Header Banner */}
      <section className="p-5 sm:p-6 rounded-3xl bg-[#0c121a] border border-[#1b2533] shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-purple-500/15 border border-purple-500/30 flex items-center justify-center text-purple-400 shrink-0">
            <Layers className="w-6 h-6" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-base sm:text-xl font-extrabold text-white tracking-tight">
                Hub de Workflows & Skills de Antigravity
              </h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-400 border border-purple-500/30 font-bold">
                {skills.length} DISPONIBLES
              </span>
            </div>
            <p className="text-xs sm:text-sm text-zinc-400 mt-1 max-w-3xl">
              Descubrimiento autónomo de archivos <code className="text-emerald-400 font-mono">SKILL.md</code> y flujos legados con ejecución aislada en Git Worktrees y verificación de invariantes.
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={loadSkills}
          disabled={loading}
          className="px-4 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border border-zinc-700 font-bold text-xs flex items-center justify-center gap-2 transition cursor-pointer self-start md:self-auto shrink-0"
        >
          <RotateCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-purple-400' : ''}`} />
          <span>Sincronizar Skills</span>
        </button>
      </section>

      {/* 2. Filter Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Scope pills */}
        <div className="flex items-center p-1 rounded-2xl bg-[#090e16] border border-[#1b2533] overflow-x-auto text-xs font-mono">
          {['all', 'workspace', 'global', 'plugin', 'builtin'].map((scope) => (
            <button
              key={scope}
              onClick={() => setSelectedScope(scope)}
              className={`px-3 py-1.5 rounded-xl transition cursor-pointer shrink-0 uppercase text-[11px] font-bold ${
                selectedScope === scope
                  ? 'bg-purple-500 text-white shadow-md'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              {scope === 'all' ? 'Todos' : scope}
            </button>
          ))}
        </div>

        {/* Search input */}
        <div className="relative flex-1 max-w-sm">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Buscar workflow por nombre o comando..."
            className="w-full bg-[#090e16] border border-[#1b2533] rounded-2xl pl-10 pr-4 py-2 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-purple-500 transition"
          />
        </div>
      </div>

      {/* 3. Skills Cards Grid */}
      {loading ? (
        <div className="p-12 text-center text-zinc-500 space-y-3 font-mono text-xs">
          <Loader2 className="w-8 h-8 animate-spin text-purple-400 mx-auto" />
          <p>Escaneando árboles de skills en workspace y directorios globales...</p>
        </div>
      ) : filteredSkills.length === 0 ? (
        <div className="p-12 text-center text-zinc-500 rounded-3xl bg-[#0c121a] border border-[#1b2533] font-mono text-xs">
          No se encontraron workflows con el criterio de búsqueda seleccionado.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredSkills.map((skill) => (
            <div
              key={skill.id}
              className="p-5 rounded-3xl bg-[#0c121a] border border-[#1b2533] hover:border-purple-500/40 transition flex flex-col justify-between group shadow-lg"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
                      <Sparkles className="w-4 h-4" />
                    </div>
                    <h3 className="text-sm font-bold text-white group-hover:text-purple-300 transition">
                      {skill.name}
                    </h3>
                  </div>
                  {getScopeBadge(skill.scope)}
                </div>

                <p className="text-xs text-zinc-400 leading-relaxed line-clamp-3">
                  {skill.description}
                </p>

                <div className="flex items-center gap-2 pt-2 border-t border-[#1b2533]/60 text-[10px] font-mono text-zinc-500">
                  <Terminal className="w-3 h-3 text-emerald-400" />
                  <code className="text-emerald-400 font-bold">{skill.slash_command}</code>
                </div>
              </div>

              <div className="pt-4 mt-4 border-t border-[#1b2533] flex items-center justify-between gap-2">
                <span className="text-[10px] text-zinc-500 font-mono">
                  {skill.has_scripts ? 'Scripting activo' : 'Paso único'}
                </span>
                <button
                  type="button"
                  onClick={() => handleOpenLaunchModal(skill)}
                  className="px-3.5 py-1.5 rounded-xl bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 border border-purple-500/40 font-mono font-bold text-xs flex items-center gap-1.5 transition cursor-pointer active:scale-95"
                >
                  <Play className="w-3 h-3 fill-purple-400 text-purple-400" />
                  <span>Lanzar</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 4. Execution Modal */}
      {activeSkill && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in"
        >
          <div className="w-full max-w-2xl bg-[#0c121a] border border-[#1b2533] rounded-3xl p-6 shadow-2xl space-y-5 overflow-hidden">
            <div className="flex items-start justify-between gap-3 border-b border-[#1b2533] pb-4">
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-base font-extrabold text-white">
                    Ejecutar Workflow: {activeSkill.name}
                  </h2>
                  {getScopeBadge(activeSkill.scope)}
                </div>
                <p className="text-xs text-zinc-400 mt-1">{activeSkill.description}</p>
              </div>
              <button
                type="button"
                onClick={() => setActiveSkill(null)}
                className="text-zinc-400 hover:text-white p-1 rounded-lg"
              >
                ✕
              </button>
            </div>

            {/* Inputs */}
            {!executionResult && (
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-mono font-bold text-zinc-300 mb-1.5">
                    Objetivo / Meta del Workflow:
                  </label>
                  <textarea
                    rows={3}
                    value={paramGoal}
                    onChange={(e) => setParamGoal(e.target.value)}
                    placeholder={`Instrucción específica para ${activeSkill.name}...`}
                    className="w-full bg-[#070a0e] border border-[#1b2533] rounded-2xl p-3 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-purple-500 font-mono"
                  />
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="strict-invariants"
                    checked={strictMode}
                    onChange={(e) => setStrictMode(e.target.checked)}
                    className="w-4 h-4 rounded text-purple-600 bg-zinc-900 border-zinc-700 cursor-pointer"
                  />
                  <label htmlFor="strict-invariants" className="text-xs text-zinc-300 cursor-pointer">
                    Verificación estricta de invariantes SolidBit (<code className="text-emerald-400 font-mono">DR-INV-001</code>)
                  </label>
                </div>

                <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#1b2533]">
                  <button
                    type="button"
                    onClick={() => setActiveSkill(null)}
                    className="px-4 py-2 rounded-xl bg-zinc-900 text-zinc-400 text-xs font-bold"
                  >
                    Cancelar
                  </button>
                  <button
                    type="button"
                    onClick={handleExecuteSkill}
                    disabled={executing}
                    className="px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-extrabold text-xs flex items-center gap-2 transition cursor-pointer shadow-lg shadow-purple-600/20 active:scale-95 disabled:opacity-50"
                  >
                    {executing ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Ejecutando en Worktree...</span>
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 fill-white" />
                        <span>Lanzar Workflow</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}

            {/* Execution Result view */}
            {executionResult && (
              <div className="space-y-4 font-mono text-xs animate-fade-in">
                <div className="p-3.5 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-between text-emerald-400 font-bold">
                  <span className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" />
                    Workflow Completado ({executionResult.duration_sec}s)
                  </span>
                  <span>ID: {executionResult.execution_id}</span>
                </div>

                <div className="space-y-2">
                  <div className="text-[11px] text-zinc-400 font-bold">Pasos Ejecutados:</div>
                  <div className="space-y-1.5 max-h-48 overflow-y-auto custom-scroll">
                    {executionResult.steps?.map((step: any) => (
                      <div key={step.step} className="p-2.5 rounded-xl bg-zinc-950 border border-zinc-900 flex items-center justify-between">
                        <div>
                          <div className="text-white font-bold">Paso {step.step}: {step.name}</div>
                          <div className="text-[10px] text-zinc-400">{step.output}</div>
                        </div>
                        <span className="text-[10px] text-emerald-400 font-bold">{step.duration_ms}ms</span>
                      </div>
                    ))}
                  </div>
                </div>

                {executionResult.tool_calls && executionResult.tool_calls.length > 0 && (
                  <div className="space-y-1">
                    <div className="text-[11px] text-zinc-400 font-bold">Llamadas a Herramientas:</div>
                    {executionResult.tool_calls.map((tc: any, i: number) => (
                      <ToolCallCard key={i} toolCall={tc} />
                    ))}
                  </div>
                )}

                <div className="flex justify-end pt-3 border-t border-[#1b2533]">
                  <button
                    type="button"
                    onClick={() => setActiveSkill(null)}
                    className="px-5 py-2 rounded-xl bg-emerald-500 text-black font-extrabold text-xs cursor-pointer"
                  >
                    Aceptar
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
