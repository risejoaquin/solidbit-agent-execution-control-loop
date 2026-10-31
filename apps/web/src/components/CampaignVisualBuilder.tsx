import React, { useState } from 'react'
import { AVAILABLE_VOICES } from './SoftPhaseMultiVoice'

export interface CampaignVisualBuilderProps {
  isOpen: boolean
  onClose: () => void
  onDispatched?: (jobId: string) => void
}

interface CampaignTaskItem {
  id: string
  title: string
  assignedAgent: string
  phase: number
  description: string
  files: string
}

export const CampaignVisualBuilder: React.FC<CampaignVisualBuilderProps> = ({
  isOpen,
  onClose,
  onDispatched,
}) => {
  const [projectId, setProjectId] = useState<'stable-ecommerce' | 'SolidPos' | 'custom'>('SolidPos')
  const [customProject, setCustomProject] = useState('')
  const [campaignName, setCampaignName] = useState('DARK_KITCHEN_ORDER_BUILDER_v1')
  const [worktreePrefix, setWorktreePrefix] = useState('agent/wave-order-builder')
  const [priority, setPriority] = useState<number>(0)
  const [selectedVoices, setSelectedVoices] = useState<string[]>(['sec-auditor', 'arch-strict', 'data-vega'])
  const [activeTab, setActiveTab] = useState<'form' | 'preview'>('form')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)

  const [tasks, setTasks] = useState<CampaignTaskItem[]>([
    {
      id: 'task-1',
      title: 'Validación de Esquema Outbox & Moneda MXN',
      assignedAgent: 'Vega',
      phase: 1,
      description: 'Garantizar balance transaccional estricto en SQLite WAL bajo invariante DR-INV-001.',
      files: 'src/PosCore/SolidPOS.PosCore.Application/Sync/OutboxTelemetry.cs',
    },
    {
      id: 'task-2',
      title: 'Enrutamiento Dark Kitchen & UI Hermosillo/Guaymas/Empalme',
      assignedAgent: 'Atlas',
      phase: 2,
      description: 'Montaje de vista OrderBuilderView.tsx con particionamiento de sucursales.',
      files: 'src/PosDashboard/SolidPOS.PosDashboard.Admin/src/components/pos/OrderBuilderView.tsx',
    },
  ])

  if (!isOpen) return null

  const handleAddTask = () => {
    const nextId = `task-${tasks.length + 1}`
    setTasks((prev) => [
      ...prev,
      {
        id: nextId,
        title: `Nueva Tarea Operativa ${prev.length + 1}`,
        assignedAgent: 'Atlas',
        phase: 1,
        description: 'Directiva técnica para ejecución desatendida.',
        files: '',
      },
    ])
  }

  const handleRemoveTask = (id: string) => {
    if (tasks.length <= 1) return
    setTasks((prev) => prev.filter((t) => t.id !== id))
  }

  const handleUpdateTask = (id: string, field: keyof CampaignTaskItem, value: any) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, [field]: value } : t))
    )
  }

  const toggleVoice = (voiceId: string) => {
    setSelectedVoices((prev) =>
      prev.includes(voiceId)
        ? prev.length > 1
          ? prev.filter((v) => v !== voiceId)
          : prev
        : [...prev, voiceId]
    )
  }

  const targetProject = projectId === 'custom' ? (customProject || 'custom-repo') : projectId

  const activeDirectives = AVAILABLE_VOICES.filter((v) => selectedVoices.includes(v.id)).map(
    (v) => `[${v.name} (${v.role})]: ${v.systemPromptDirective}`
  )

  const generatedPayload = {
    command: 'EXECUTE_WAVE',
    job_id: `job-${Date.now().toString(16)}`,
    project_id: targetProject,
    worktree_prefix: worktreePrefix,
    manifest: {
      id: `pkg-${Date.now().toString(16)}`,
      name: campaignName,
      priority,
      tasks: tasks.map((t) => ({
        id: t.id,
        title: t.title,
        agent: t.assignedAgent,
        phase: t.phase,
        directive: t.description,
        owned_paths: t.files ? t.files.split(',').map((f) => f.trim()).filter(Boolean) : [],
      })),
      multivoice_directives: activeDirectives,
      governance_gate: 'GATE_5_HMAC_REQUIRED',
    },
    priority,
  }

  const handleDispatch = async () => {
    setIsSubmitting(true)
    setErrorMsg(null)
    setSuccessMsg(null)

    try {
      const res = await fetch('/api/orchestrator/enqueue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(generatedPayload),
      })

      const data = await res.json()
      if (res.ok) {
        setSuccessMsg(`Campaña despachada exitosamente. ID: ${data.job_id || generatedPayload.job_id}`)
        if (onDispatched) onDispatched(data.job_id || generatedPayload.job_id)
        setTimeout(() => {
          onClose()
        }, 1200)
      } else {
        setErrorMsg(data.detail || data.error || 'Error al despachar campaña en el orquestador.')
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Error de comunicación con el Local Gateway.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-[150] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-[#0a0a0a] border border-white/8 rounded-lg w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden shadow-2xl">
        {/* Header Modal */}
        <div className="h-12 border-b border-white/8 px-4 flex items-center justify-between shrink-0 bg-[#000000]">
          <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <path d="M3 9h18" />
              <path d="M9 21V9" />
            </svg>
            <span className="text-xs font-semibold text-white tracking-wide uppercase font-sans">
              Campaign Visual Builder
            </span>
            <span className="text-[10px] font-mono text-zinc-500">· Fase 3 EOP · Cero Payloads JSON Manuales</span>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex bg-[#121212] border border-white/8 rounded p-0.5">
              <button
                type="button"
                onClick={() => setActiveTab('form')}
                className={`px-2.5 py-1 text-[10px] font-mono rounded transition ${
                  activeTab === 'form' ? 'bg-white/10 text-white font-semibold' : 'text-zinc-500 hover:text-zinc-300'
                }`}
              >
                Diseño Visual
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('preview')}
                className={`px-2.5 py-1 text-[10px] font-mono rounded transition ${
                  activeTab === 'preview' ? 'bg-white/10 text-white font-semibold' : 'text-zinc-500 hover:text-zinc-300'
                }`}
              >
                JSON Preview CQRS
              </button>
            </div>

            <button
              type="button"
              onClick={onClose}
              className="text-zinc-500 hover:text-white p-1 rounded hover:bg-white/5 transition"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
        </div>

        {/* Status Messages */}
        {errorMsg && (
          <div className="bg-red-500/10 border-b border-red-500/20 px-4 py-2 text-xs text-red-400 font-mono">
            ⚠ {errorMsg}
          </div>
        )}
        {successMsg && (
          <div className="bg-emerald-500/10 border-b border-emerald-500/20 px-4 py-2 text-xs text-emerald-400 font-mono">
            ✓ {successMsg}
          </div>
        )}

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-4 custom-scroll">
          {activeTab === 'form' ? (
            <div className="space-y-4">
              {/* Target Project & Campaign Metadata */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="bg-[#121212] border border-white/8 rounded p-3">
                  <label className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider block mb-1.5">
                    Repositorio Destino
                  </label>
                  <select
                    value={projectId}
                    onChange={(e) => setProjectId(e.target.value as any)}
                    className="w-full bg-[#0a0a0a] border border-white/10 rounded px-2.5 py-1.5 text-xs text-white font-mono focus:border-emerald-500/50 outline-none"
                  >
                    <option value="SolidPos">SolidPos (Dark Kitchen / C# POS)</option>
                    <option value="stable-ecommerce">stable-ecommerce (EOP Core)</option>
                    <option value="custom">Otro Repositorio...</option>
                  </select>
                  {projectId === 'custom' && (
                    <input
                      type="text"
                      placeholder="nombre-del-repo"
                      value={customProject}
                      onChange={(e) => setCustomProject(e.target.value)}
                      className="mt-2 w-full bg-[#0a0a0a] border border-white/10 rounded px-2.5 py-1 text-xs text-white font-mono outline-none"
                    />
                  )}
                </div>

                <div className="bg-[#121212] border border-white/8 rounded p-3">
                  <label className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider block mb-1.5">
                    Identificador de Campaña
                  </label>
                  <input
                    type="text"
                    value={campaignName}
                    onChange={(e) => setCampaignName(e.target.value)}
                    className="w-full bg-[#0a0a0a] border border-white/10 rounded px-2.5 py-1.5 text-xs text-white font-mono focus:border-emerald-500/50 outline-none"
                  />
                </div>

                <div className="bg-[#121212] border border-white/8 rounded p-3">
                  <label className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider block mb-1.5">
                    Prefijo Worktree Efímero
                  </label>
                  <input
                    type="text"
                    value={worktreePrefix}
                    onChange={(e) => setWorktreePrefix(e.target.value)}
                    className="w-full bg-[#0a0a0a] border border-white/10 rounded px-2.5 py-1.5 text-xs text-white font-mono focus:border-emerald-500/50 outline-none"
                  />
                </div>
              </div>

              {/* Multi-Voice Directives Injection */}
              <div className="bg-[#121212] border border-white/8 rounded p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider">
                    Inyección de Directivas Multi-Voice (Fase Soft)
                  </span>
                  <span className="text-[10px] font-mono text-emerald-400">
                    {selectedVoices.length} activas
                  </span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
                  {AVAILABLE_VOICES.map((v) => {
                    const isSelected = selectedVoices.includes(v.id)
                    return (
                      <button
                        key={v.id}
                        type="button"
                        onClick={() => toggleVoice(v.id)}
                        className={`p-2 rounded text-left border transition text-xs font-mono flex flex-col justify-between ${
                          isSelected
                            ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-400'
                            : 'bg-[#0a0a0a] border-white/8 text-zinc-500 hover:text-zinc-300'
                        }`}
                      >
                        <div className="font-semibold">{v.name}</div>
                        <div className="text-[9px] text-zinc-500 truncate">{v.role}</div>
                      </button>
                    )
                  })}
                </div>
              </div>

              {/* Tasks Builder (DAG Wave Blocks) */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider">
                    Bloques de Tareas Topológicas (Kahn DAG)
                  </span>
                  <button
                    type="button"
                    onClick={handleAddTask}
                    className="px-2 py-1 rounded bg-white/5 hover:bg-white/10 border border-white/10 text-emerald-400 text-xs font-mono transition flex items-center gap-1"
                  >
                    <span>+ Agregar Tarea</span>
                  </button>
                </div>

                <div className="space-y-2.5">
                  {tasks.map((task, idx) => (
                    <div
                      key={task.id}
                      className="bg-[#121212] border border-white/8 rounded p-3 space-y-2 relative group"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="w-5 h-5 rounded bg-white/5 border border-white/10 text-[10px] font-mono flex items-center justify-center text-zinc-400">
                            {idx + 1}
                          </span>
                          <input
                            type="text"
                            value={task.title}
                            onChange={(e) => handleUpdateTask(task.id, 'title', e.target.value)}
                            placeholder="Título de la tarea"
                            className="bg-transparent border-b border-transparent hover:border-white/20 focus:border-emerald-500/50 text-xs font-semibold text-white px-1 py-0.5 outline-none font-sans"
                          />
                        </div>

                        <div className="flex items-center gap-2">
                          <select
                            value={task.assignedAgent}
                            onChange={(e) => handleUpdateTask(task.id, 'assignedAgent', e.target.value)}
                            className="bg-[#0a0a0a] border border-white/10 rounded px-2 py-1 text-[10px] font-mono text-zinc-300 outline-none"
                          >
                            <option value="Atlas">Atlas (Coordinador)</option>
                            <option value="Vega">Vega (Datos/Contratos)</option>
                            <option value="Nova">Nova (Inspectora QA)</option>
                            <option value="Centinela">Centinela (Hard Deny)</option>
                            <option value="Frontend Architect">Frontend Architect</option>
                          </select>

                          <button
                            type="button"
                            onClick={() => handleRemoveTask(task.id)}
                            disabled={tasks.length <= 1}
                            className="text-zinc-600 hover:text-red-400 p-1 disabled:opacity-30 transition"
                          >
                            <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <line x1="18" y1="6" x2="6" y2="18" />
                              <line x1="6" y1="6" x2="18" y2="18" />
                            </svg>
                          </button>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
                        <div>
                          <label className="text-[9px] font-mono text-zinc-500 block mb-1">
                            Directiva de Ejecución (Prompt del Agente)
                          </label>
                          <textarea
                            value={task.description}
                            onChange={(e) => handleUpdateTask(task.id, 'description', e.target.value)}
                            rows={2}
                            className="w-full bg-[#0a0a0a] border border-white/10 rounded p-2 text-xs text-zinc-300 font-sans outline-none focus:border-emerald-500/50"
                          />
                        </div>
                        <div>
                          <label className="text-[9px] font-mono text-zinc-500 block mb-1">
                            Owned Paths (Archivos Restringidos Separados por Comas)
                          </label>
                          <textarea
                            value={task.files}
                            onChange={(e) => handleUpdateTask(task.id, 'files', e.target.value)}
                            rows={2}
                            placeholder="ruta/archivo1.ts, ruta/archivo2.tsx"
                            className="w-full bg-[#0a0a0a] border border-white/10 rounded p-2 text-xs text-zinc-300 font-mono outline-none focus:border-emerald-500/50"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-[#000000] border border-white/8 rounded p-4">
              <pre className="text-xs font-mono text-emerald-400 whitespace-pre-wrap leading-relaxed">
                {JSON.stringify(generatedPayload, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="h-14 border-t border-white/8 px-4 flex items-center justify-between shrink-0 bg-[#000000]">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-[11px] font-mono text-zinc-400">
              {tasks.length} tareas · {selectedVoices.length} directivas · Protocolo Gate 5
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 rounded text-xs font-mono border border-white/10 text-zinc-400 hover:text-white transition"
            >
              Cancelar
            </button>
            <button
              type="button"
              onClick={handleDispatch}
              disabled={isSubmitting}
              className="px-4 py-1.5 rounded text-xs font-mono bg-emerald-500 text-black font-semibold hover:bg-emerald-400 transition cursor-pointer flex items-center gap-2 disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <span className="w-3 h-3 border-2 border-black border-t-transparent rounded-full animate-spin" />
                  <span>Despachando...</span>
                </>
              ) : (
                <>
                  <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <polygon points="5 3 19 12 5 21 5 3" />
                  </svg>
                  <span>Despachar Campaña</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
