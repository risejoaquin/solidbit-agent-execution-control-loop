import React, { useState, useEffect } from 'react'
import {
  Layers,
  Sparkles,
  Play,
  Search,
  CheckCircle2,
  Loader2,
  Terminal,
  RotateCw,
  ChevronDown,
  ChevronUp,
} from 'lucide-react'
import { ToolCallCard } from '../ToolCallCard'

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
  const [showTechCalls, setShowTechCalls] = useState<boolean>(false)

  const loadSkills = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/skills')
      const data = await res.json()
      if (data.skills) {
        setSkills(data.skills)
      }
    } catch (e) {
      console.warn('Error loading workflows:', e)
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
    setShowTechCalls(false)
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
            goal: paramGoal || `Ejecutar flujo ${activeSkill.name}`,
            strict_mode: strictMode,
          },
        }),
      })
      const data = await res.json()
      setExecutionResult(data)
    } catch (e: any) {
      console.error('Error ejecutando flujo:', e)
    } finally {
      setExecuting(false)
    }
  }

  const getScopeBadge = (scope: string) => {
    switch (scope) {
      case 'workspace':
        return (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full font-bold bg-zinc-900 text-zinc-200 border border-zinc-750">
            PROYECTO
          </span>
        )
      case 'global':
        return (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full font-bold bg-zinc-900 text-zinc-300 border border-zinc-800">
            SISTEMA
          </span>
        )
      case 'plugin':
        return (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full font-bold bg-zinc-900 text-zinc-300 border border-zinc-800">
            EXTENSIÓN
          </span>
        )
      default:
        return (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full font-bold bg-zinc-900 text-zinc-400 border border-zinc-850">
            INTEGRADO
          </span>
        )
    }
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto animate-fade-in text-left pb-12">
      {/* 1. Header Banner (Zero implementation file leaks in Layer 1 & Single Primary CTA) */}
      <section className="p-5 sm:p-6 rounded-3xl bg-zinc-950 border border-zinc-850 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-11 h-11 rounded-2xl bg-zinc-900 border border-zinc-750 flex items-center justify-center text-white shrink-0">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-lg font-bold text-white tracking-tight">
                Catálogo de Flujos Automatizados
              </h1>
              <span className="text-[10px] font-mono px-2.5 py-0.5 rounded-full bg-zinc-900 text-zinc-200 border border-zinc-750 font-bold">
                {skills.length} DISPONIBLES
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-1 max-w-2xl">
              Rutinas listas para ejecutar tareas especializadas de revisión, diagnóstico o configuración.
            </p>
          </div>
        </div>

        {/* SINGLE Primary Action Token in WorkflowsSection */}
        <button
          type="button"
          onClick={loadSkills}
          disabled={loading}
          className="px-4 py-2.5 rounded-xl bg-white hover:bg-zinc-200 text-black font-extrabold text-xs flex items-center justify-center gap-2 transition cursor-pointer self-start md:self-auto shrink-0 shadow-sm"
        >
          <RotateCw className={`w-3.5 h-3.5 text-black ${loading ? 'animate-spin' : ''}`} />
          <span>Actualizar Catálogo</span>
        </button>
      </section>

      {/* 2. Filter Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="flex items-center p-1 rounded-2xl bg-zinc-950 border border-zinc-850 overflow-x-auto text-xs">
          {[
            { id: 'all', label: 'Todos' },
            { id: 'workspace', label: 'Proyecto' },
            { id: 'global', label: 'Sistema' },
            { id: 'plugin', label: 'Extensiones' },
          ].map((scope) => (
            <button
              key={scope.id}
              type="button"
              onClick={() => setSelectedScope(scope.id)}
              className={`px-3 py-1.5 rounded-xl transition cursor-pointer shrink-0 text-xs font-semibold ${
                selectedScope === scope.id
                  ? 'bg-zinc-800 text-white font-bold'
                  : 'text-zinc-400 hover:text-white'
              }`}
            >
              {scope.label}
            </button>
          ))}
        </div>

        <div className="relative flex-1 max-w-sm">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Buscar flujo por nombre o función..."
            className="w-full bg-zinc-950 border border-zinc-850 rounded-2xl pl-10 pr-4 py-2 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-white transition"
          />
        </div>
      </div>

      {/* 3. Workflows Grid */}
      {loading ? (
        <div className="p-12 text-center text-zinc-400 space-y-3 text-xs">
          <Loader2 className="w-6 h-6 animate-spin text-white mx-auto" />
          <p>Cargando flujos disponibles...</p>
        </div>
      ) : filteredSkills.length === 0 ? (
        <div className="p-10 text-center text-zinc-400 rounded-3xl bg-zinc-950 border border-zinc-850 space-y-3 text-xs">
          <p>No se encontraron flujos con ese filtro.</p>
          <button
            type="button"
            onClick={() => {
              setSearchQuery('')
              setSelectedScope('all')
            }}
            className="px-4 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-white font-semibold cursor-pointer"
          >
            Mostrar todos los flujos
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredSkills.map((skill) => (
            <div
              key={skill.id}
              className="p-5 rounded-3xl bg-zinc-950 border border-zinc-850 hover:border-zinc-700 transition flex flex-col justify-between space-y-4"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-200">
                      <Sparkles className="w-4 h-4" />
                    </div>
                    <h3 className="text-sm font-bold text-white">{skill.name}</h3>
                  </div>
                  {getScopeBadge(skill.scope)}
                </div>

                <p className="text-xs text-zinc-400 leading-relaxed line-clamp-3">
                  {skill.description}
                </p>
              </div>

              <div className="pt-3 border-t border-zinc-900 flex items-center justify-between gap-2">
                <code className="text-[11px] font-mono text-zinc-400">{skill.slash_command}</code>
                <button
                  type="button"
                  onClick={() => handleOpenLaunchModal(skill)}
                  className="px-3.5 py-1.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-white border border-zinc-750 font-semibold text-xs flex items-center gap-1.5 transition cursor-pointer"
                >
                  <Play className="w-3 h-3 text-emerald-400" />
                  <span>Abrir Flujo</span>
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
          <div className="w-full max-w-2xl bg-zinc-950 border border-zinc-800 rounded-3xl p-6 shadow-2xl space-y-5 overflow-hidden">
            <div className="flex items-start justify-between gap-3 border-b border-zinc-850 pb-4">
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-base font-extrabold text-white">
                    Ejecutar Flujo: {activeSkill.name}
                  </h2>
                  {getScopeBadge(activeSkill.scope)}
                </div>
                <p className="text-xs text-zinc-400 mt-1">{activeSkill.description}</p>
              </div>
              <button
                type="button"
                onClick={() => setActiveSkill(null)}
                className="text-zinc-400 hover:text-white p-1 rounded-lg cursor-pointer"
              >
                ✕
              </button>
            </div>

            {!executionResult && (
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-zinc-200 mb-1.5">
                    Objetivo específico para esta ejecución:
                  </label>
                  <textarea
                    rows={3}
                    value={paramGoal}
                    onChange={(e) => setParamGoal(e.target.value)}
                    placeholder={`Describe qué deseas revisar o ejecutar con ${activeSkill.name}...`}
                    className="w-full bg-black border border-zinc-800 rounded-2xl p-3 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-white"
                  />
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="strict-invariants"
                    checked={strictMode}
                    onChange={(e) => setStrictMode(e.target.checked)}
                    className="w-4 h-4 rounded bg-zinc-900 border-zinc-700 cursor-pointer"
                  />
                  <label htmlFor="strict-invariants" className="text-xs text-zinc-300 cursor-pointer">
                    Verificar reglas de protección del negocio antes de finalizar
                  </label>
                </div>

                <div className="flex items-center justify-end gap-3 pt-3 border-t border-zinc-850">
                  <button
                    type="button"
                    onClick={() => setActiveSkill(null)}
                    className="px-4 py-2 rounded-xl bg-zinc-900 text-zinc-300 text-xs font-semibold cursor-pointer"
                  >
                    Cancelar
                  </button>
                  <button
                    type="button"
                    onClick={handleExecuteSkill}
                    disabled={executing}
                    className="px-5 py-2.5 rounded-xl bg-white hover:bg-zinc-200 text-black font-extrabold text-xs flex items-center gap-2 transition cursor-pointer shadow-sm disabled:opacity-50"
                  >
                    {executing ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin text-black" />
                        <span>Ejecutando Flujo...</span>
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 fill-black text-black" />
                        <span>Iniciar Ejecución</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}

            {executionResult && (
              <div className="space-y-4 text-xs animate-fade-in">
                <div className="p-3.5 rounded-2xl bg-emerald-950/30 border border-emerald-500/40 flex items-center justify-between text-emerald-200 font-bold">
                  <span className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    Flujo Completado ({executionResult.duration_sec}s)
                  </span>
                  <span className="font-mono">Registro: {executionResult.execution_id}</span>
                </div>

                <div className="space-y-2">
                  <div className="text-[11px] text-zinc-400 font-bold">Etapas Completadas:</div>
                  <div className="space-y-1.5 max-h-48 overflow-y-auto custom-scroll">
                    {executionResult.steps?.map((step: any) => (
                      <div
                        key={step.step}
                        className="p-2.5 rounded-xl bg-black border border-zinc-850 flex items-center justify-between"
                      >
                        <div>
                          <div className="text-white font-bold">
                            Paso {step.step}: {step.name}
                          </div>
                          <div className="text-[11px] text-zinc-400">{step.output}</div>
                        </div>
                        <span className="text-[10px] font-mono text-zinc-300 font-bold">
                          {step.duration_ms}ms
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Layer 2 Collapsible Tool Calls */}
                {executionResult.tool_calls && executionResult.tool_calls.length > 0 && (
                  <div className="pt-2 border-t border-zinc-850">
                    <button
                      type="button"
                      onClick={() => setShowTechCalls(!showTechCalls)}
                      className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-white cursor-pointer"
                    >
                      <Terminal className="w-3.5 h-3.5" />
                      <span>
                        {showTechCalls
                          ? 'Ocultar inspección de comandos internos'
                          : `Inspección Técnica: Ver comandos ejecutados (${executionResult.tool_calls.length})`}
                      </span>
                      {showTechCalls ? (
                        <ChevronUp className="w-3.5 h-3.5" />
                      ) : (
                        <ChevronDown className="w-3.5 h-3.5" />
                      )}
                    </button>

                    {showTechCalls && (
                      <div className="mt-2 space-y-1">
                        {executionResult.tool_calls.map((tc: any, i: number) => (
                          <ToolCallCard key={i} toolCall={tc} />
                        ))}
                      </div>
                    )}
                  </div>
                )}

                <div className="flex justify-end pt-3 border-t border-zinc-850">
                  <button
                    type="button"
                    onClick={() => setActiveSkill(null)}
                    className="px-5 py-2 rounded-xl bg-white text-black font-extrabold text-xs cursor-pointer"
                  >
                    Finalizar y Cerrar
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
