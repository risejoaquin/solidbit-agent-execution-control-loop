import React, { useState, useEffect } from 'react'
import {
  FolderGit2,
  CheckCircle2,
  Plus,
  Trash2,
  FileText,
  ChevronDown,
  ChevronUp,
  FolderOpen,
  AlertCircle,
  Sparkles,
  ShieldCheck,
  GitBranch,
  GitCommit,
  Play,
  Loader2,
  RefreshCw,
  Award,
  Copy,
} from 'lucide-react'
import { StatusBadge } from '../ui/status-badge'
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from '../ui/tooltip'

interface ProjectsSectionProps {
  onLaunchAutoSprint?: (planData: any) => void
  onNavigateSection?: (section: string) => void
}

export const ProjectsSection: React.FC<ProjectsSectionProps> = ({
  onLaunchAutoSprint,
  onNavigateSection,
}) => {
  const [projectsList, setProjectsList] = useState<any[]>([])
  const [activeProjId, setActiveProjId] = useState<string>('')
  const [fsTree, setFsTree] = useState<any[]>([])
  const [docContent, setDocContent] = useState<string | null>(null)
  const [selectedDocName, setSelectedDocName] = useState<string>('')
  const [showFileTree, setShowFileTree] = useState<boolean>(false)

  // 360° Project Dossier & Live Audit State
  const [inspection360, setInspection360] = useState<any | null>(null)
  const [loading360, setLoading360] = useState<boolean>(false)
  const [planningAutoSprint, setPlanningAutoSprint] = useState<boolean>(false)
  const [autoSprintResult, setAutoSprintResult] = useState<any | null>(null)

  // Manual Import Form State (Poka-Yoke + Inline Validation)
  const [showImportModal, setShowImportModal] = useState<boolean>(false)
  const [importPath, setImportPath] = useState<string>('')
  const [importing, setImporting] = useState<boolean>(false)
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(
    null
  )

  const loadInspection360 = async (projId?: string) => {
    setLoading360(true)
    try {
      const q = projId ? `?project_id=${encodeURIComponent(projId)}` : ''
      const res = await fetch(`/api/projects/inspect-360${q}`)
      const data = await res.json()
      if (data && data.success) {
        setInspection360(data)
      }
    } catch (e) {
      console.warn('Error loading 360 inspection:', e)
    } finally {
      setLoading360(false)
    }
  }

  const loadData = async () => {
    let currentActiveId = ''
    try {
      const res = await fetch('/api/projects')
      const data = await res.json()
      if (data && data.projects) {
        setProjectsList(data.projects)
        const active = data.projects.find((p: any) => p.is_active)
        currentActiveId = active?.id || data.active?.id || (data.projects[0]?.id ?? '')
        setActiveProjId(currentActiveId)
      }
    } catch (e) {
      console.warn('Error loading projects:', e)
    }

    await loadInspection360(currentActiveId)

    try {
      const treeRes = await fetch('/api/fs/tree')
      const treeData = await treeRes.json()
      if (treeData && treeData.tree) {
        setFsTree(treeData.tree)
      }
    } catch (e) {
      console.warn('Error loading fs tree:', e)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleSwitchProject = async (projId: string) => {
    try {
      const res = await fetch('/api/projects/switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projId }),
      })
      const data = await res.json()
      if (data.success) {
        setActiveProjId(projId)
        setAutoSprintResult(null)
        setFeedback({ type: 'success', message: data.message || 'Proyecto activado y auditado.' })
        await loadData()
      } else {
        setFeedback({ type: 'error', message: data.error || 'No se pudo activar el proyecto.' })
      }
    } catch (e: any) {
      setFeedback({ type: 'error', message: 'Error de red: ' + e.message })
    }
  }

  const handleAuditAndAutoSprint = async (executeImmediately: boolean) => {
    setPlanningAutoSprint(true)
    setFeedback(null)
    try {
      const res = await fetch('/api/projects/audit-and-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: activeProjId,
          execute_immediately: executeImmediately,
        }),
      })
      const data = await res.json()
      if (res.ok && data.success) {
        setAutoSprintResult(data)
        if (data.inspection) {
          setInspection360(data.inspection)
        }
        setFeedback({
          type: 'success',
          message: data.message,
        })
        if (onLaunchAutoSprint && data.plan && !executeImmediately) {
          onLaunchAutoSprint(data)
        }
      } else {
        setFeedback({
          type: 'error',
          message: data.error || 'No se pudo sintetizar el sprint automático.',
        })
      }
    } catch (e: any) {
      setFeedback({ type: 'error', message: 'Error de conexión: ' + e.message })
    } finally {
      setPlanningAutoSprint(false)
    }
  }

  const handleImportProject = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!importPath.trim()) return
    setImporting(true)
    setFeedback(null)
    try {
      const res = await fetch('/api/projects/import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: importPath.trim() }),
      })
      const data = await res.json()
      if (data.success) {
        setFeedback({ type: 'success', message: data.message })
        setImportPath('')
        setShowImportModal(false)
        await loadData()
      } else {
        setFeedback({
          type: 'error',
          message: data.error || 'Verifica que la ruta de la carpeta exista en tu equipo.',
        })
      }
    } catch (e: any) {
      setFeedback({ type: 'error', message: 'Error al importar: ' + e.message })
    } finally {
      setImporting(false)
    }
  }

  const handleRemoveProject = async (projId: string, projName: string) => {
    if (!confirm(`¿Quitar "${projName}" de esta lista? (Tus archivos en disco NO se borrarán)`)) {
      return
    }
    try {
      const res = await fetch('/api/projects/remove', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projId }),
      })
      const data = await res.json()
      if (data.success) {
        setFeedback({ type: 'success', message: data.message })
        await loadData()
      }
    } catch (e: any) {
      setFeedback({ type: 'error', message: 'Error quitando proyecto: ' + e.message })
    }
  }

  const handleViewDoc = async (docPath: string, docName: string) => {
    try {
      setSelectedDocName(docName)
      const res = await fetch(`/api/projects/doc?doc_path=${encodeURIComponent(docPath)}`)
      const data = await res.json()
      if (data && data.content) {
        setDocContent(data.content)
      }
    } catch (e: any) {
      console.warn('Error leyendo documento:', e)
    }
  }

  const isPathValid = importPath.trim().length >= 3

  return (
    <div className="space-y-6 max-w-6xl mx-auto animate-fade-in pb-12 text-left">
      {/* 1. Header con CTA para Importar Proyecto */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-3xl bg-zinc-950 border border-zinc-800 shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2.5">
            <h1 className="text-lg font-extrabold text-white tracking-tight">
              Proyectos Vinculados y Expediente 360° SolidBit
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold bg-zinc-900 text-zinc-200 border border-zinc-700">
              {projectsList.length} {projectsList.length === 1 ? 'Proyecto' : 'Proyectos'}
            </span>
          </div>
          <p className="text-xs text-zinc-400">
            Abre cualquier proyecto para ver todo su estado en vivo, auditar sus 5 dimensiones SolidBit y diseñar el Sprint automáticamente con los hallazgos.
          </p>
        </div>

        <button
          type="button"
          onClick={() => {
            setShowImportModal(true)
            setFeedback(null)
          }}
          className="px-4 py-2.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-white border border-zinc-700 text-xs font-bold flex items-center gap-2 transition cursor-pointer shrink-0"
        >
          <Plus className="w-4 h-4 text-emerald-400" />
          <span>+ Importar Carpeta Manualmente</span>
        </button>
      </div>

      {/* Inline Feedback Banner */}
      {feedback && (
        <div
          className={`p-4 rounded-2xl border text-xs flex items-center justify-between gap-3 ${
            feedback.type === 'success'
              ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-200'
              : 'bg-amber-950/30 border-amber-500/40 text-amber-200'
          }`}
        >
          <div className="flex items-center gap-2.5">
            {feedback.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
            )}
            <span className="font-medium">{feedback.message}</span>
          </div>
          <button
            type="button"
            onClick={() => setFeedback(null)}
            className="text-zinc-400 hover:text-white text-xs font-bold cursor-pointer"
          >
            Cerrar
          </button>
        </div>
      )}

      {/* 2. Selector de Proyectos Importados */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {projectsList.map((p) => {
          const isActive = p.id === activeProjId || p.is_active
          const isClean = p.worktree_clean !== false
          const shortSha = (p.commit_hash || 'HEAD').substring(0, 7)

          return (
            <div
              key={p.id}
              className={`p-5 rounded-3xl transition flex flex-col justify-between space-y-4 border ${
                isActive
                  ? 'bg-[#18181B] border-emerald-500/50 shadow-[0_0_20px_rgba(16,185,129,0.12)]'
                  : 'bg-[#121215] border-white/5 hover:border-zinc-700 hover:bg-zinc-900/40'
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-11 h-11 rounded-2xl flex items-center justify-center shrink-0 ${
                        isActive
                          ? 'bg-emerald-500 text-black font-extrabold shadow-md'
                          : 'bg-zinc-900 border border-white/5 text-zinc-300'
                      }`}
                    >
                      <FolderGit2 className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-sm font-extrabold text-white">{p.name}</h3>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="inline-flex items-center gap-1 text-[11px] font-mono text-zinc-300">
                          <GitBranch className="w-3 h-3 text-sky-400" />
                          <strong className="text-zinc-200">{p.branch || 'main'}</strong>
                        </span>
                        <span className="text-zinc-600">&bull;</span>
                        <span className="inline-flex items-center gap-1 text-[10px] font-mono px-1.5 py-0.5 rounded bg-black/60 border border-zinc-800 text-emerald-400">
                          <GitCommit className="w-3 h-3" />
                          {shortSha}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5">
                    <StatusBadge
                      status={isActive ? 'SUCCESS' : 'IDLE'}
                      label={isActive ? 'PROYECTO ACTIVO' : 'DISPONIBLE'}
                      pulsing={isActive}
                    />
                    <button
                      type="button"
                      onClick={() => handleRemoveProject(p.id, p.name)}
                      className="p-1.5 rounded-xl bg-zinc-900/80 hover:bg-zinc-800 text-zinc-400 hover:text-rose-400 transition cursor-pointer border border-white/5"
                      title="Quitar de la lista"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                {/* Path and Worktree Hygiene Badge */}
                <div className="p-2.5 rounded-xl bg-black border border-white/5 text-[11px] font-mono text-zinc-300 flex items-center justify-between">
                  <span className="truncate max-w-[280px]">{p.path}</span>
                  <div className="flex items-center gap-2 shrink-0 ml-2">
                    <span className="text-[10px] text-zinc-500">
                      {p.docs_count || 0} docs
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${
                        isClean
                          ? 'bg-emerald-950/40 text-emerald-400 border border-emerald-500/30'
                          : 'bg-amber-950/40 text-amber-300 border border-amber-500/30'
                      }`}
                    >
                      {isClean ? '✓ Worktree Limpio' : '• Cambios sin confirmar'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-white/5">
                <div className="flex flex-wrap gap-1.5">
                  {(p.tech_stack || []).slice(0, 4).map((t: string) => (
                    <span
                      key={t}
                      className="px-2 py-0.5 rounded-md bg-black border border-zinc-800 text-[10px] font-mono text-zinc-300"
                    >
                      {t}
                    </span>
                  ))}
                </div>

                <button
                  type="button"
                  onClick={() => handleSwitchProject(p.id)}
                  className={`px-4 py-2 rounded-xl text-xs font-extrabold transition cursor-pointer shadow-sm ${
                    isActive
                      ? 'bg-zinc-800 text-emerald-300 border border-emerald-500/30'
                      : 'bg-white hover:bg-zinc-200 text-black'
                  }`}
                >
                  {isActive ? 'Expediente 360° Activo' : 'Abrir y Auditar'}
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {/* 3. EXPEDIENTE 360° DEL PROYECTO Y AUDITORÍA SOLIDBIT EN VIVO */}
      {inspection360 && (
        <div className="p-6 rounded-3xl bg-zinc-950 border border-zinc-800 space-y-6 shadow-2xl">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-zinc-850 pb-5">
            <div className="space-y-1">
              <div className="flex flex-wrap items-center gap-2.5">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  EXPEDIENTE 360° EN VIVO
                </span>
                <h2 className="text-base sm:text-lg font-extrabold text-white">
                  {inspection360.project?.name} ({inspection360.project?.path})
                </h2>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-zinc-900 text-emerald-400 border border-zinc-750">
                  Salud SolidBit: {inspection360.audit_summary?.overall_score}%
                </span>
              </div>
              <p className="text-xs text-zinc-400">
                Rama <code className="text-zinc-200">{inspection360.project?.branch}</code> @ commit{' '}
                <code className="text-emerald-400">{inspection360.project?.commit}</code> ·{' '}
                {inspection360.project?.py_tests_count || 0} archivos de prueba Pytest ·{' '}
                {inspection360.project?.docs_count || 0} documentos de arquitectura · Auditado en{' '}
                {inspection360.audit_summary?.duration_ms} ms
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2.5">
              <button
                type="button"
                onClick={() => loadInspection360(activeProjId)}
                disabled={loading360}
                className="px-3.5 py-2.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-200 border border-zinc-750 text-xs font-semibold flex items-center gap-1.5 transition cursor-pointer"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading360 ? 'animate-spin' : ''}`} />
                <span>Re-Auditar Proyecto</span>
              </button>

              {/* SINGLE Primary Action Token in 360 Dossier (Hick's Law) */}
              <button
                type="button"
                onClick={() => handleAuditAndAutoSprint(true)}
                disabled={planningAutoSprint}
                className="px-5 py-2.5 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-extrabold flex items-center gap-2 transition cursor-pointer shadow-lg disabled:opacity-50"
              >
                {planningAutoSprint ? (
                  <Loader2 className="w-4 h-4 animate-spin text-black" />
                ) : (
                  <Sparkles className="w-4 h-4 text-black" />
                )}
                <span>
                  ⚡ Diseñar y Ejecutar Sprint Automático desde Auditoría
                </span>
              </button>
            </div>
          </div>

          {/* 3A. Matriz de las 5 Dimensiones de Auditoría SolidBit (con los 6 Personajes) */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-300 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Diagnóstico en 5 Dimensiones del Escuadrón SolidBit</span>
              </h3>
              <span className="text-[11px] font-mono text-zinc-400">
                5/5 Dimensiones Evaluadas en Disco
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
              {(inspection360.audit_dimensions || []).map((dim: any) => (
                <div
                  key={dim.id}
                  className="p-4 rounded-2xl bg-black border border-zinc-850 flex flex-col justify-between space-y-3"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between gap-1">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-zinc-900 text-emerald-400 border border-zinc-800 font-bold">
                        {dim.character}
                      </span>
                      <span className="text-xs font-mono font-extrabold text-emerald-400">
                        {dim.score}%
                      </span>
                    </div>
                    <h4 className="text-xs font-bold text-white leading-snug">{dim.dimension}</h4>
                    <p className="text-[11px] text-zinc-400 leading-relaxed">{dim.summary}</p>
                  </div>
                  <div className="pt-2 border-t border-zinc-900 flex items-center justify-between text-[10px] font-mono text-zinc-500">
                    <span>{dim.workorder}</span>
                    <span className="text-emerald-400 font-bold">✓ {dim.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 3B. Hallazgos de Auditoría y Propuesta Automática de Sprint */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div className="lg:col-span-2 p-5 rounded-2xl bg-black border border-zinc-850 space-y-3">
              <div className="flex items-center justify-between border-b border-zinc-900 pb-2.5">
                <h3 className="text-xs font-bold text-white flex items-center gap-2">
                  <Award className="w-4 h-4 text-amber-400" />
                  <span>Hallazgos Accionables Detectados para el Sprint Automático</span>
                </h3>
                <span className="text-[10px] font-mono text-zinc-400">
                  {(inspection360.findings || []).length} tareas sintetizadas
                </span>
              </div>

              <div className="space-y-2.5">
                {(inspection360.findings || []).map((f: any) => (
                  <div
                    key={f.id}
                    className="p-3.5 rounded-xl bg-zinc-950 border border-zinc-850 space-y-1.5"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-zinc-900 text-amber-300 border border-zinc-800">
                          {f.id} · {f.contract}
                        </span>
                        <span className="text-xs font-bold text-white">{f.title}</span>
                      </div>
                      <span className="text-[10px] font-mono text-emerald-400 font-bold">
                        Agentes: {f.agent}
                      </span>
                    </div>
                    <p className="text-[11px] text-zinc-400">{f.detail}</p>
                    <div className="text-[11px] font-mono text-zinc-300 pt-1">
                      ↳ Tarea automática: <strong className="text-white">{f.suggested_task}</strong>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 3C. Commits Recientes y Contratos Vigentes del Proyecto */}
            <div className="p-5 rounded-2xl bg-black border border-zinc-850 space-y-4 flex flex-col justify-between">
              <div className="space-y-3">
                <h3 className="text-xs font-bold text-white flex items-center gap-2 border-b border-zinc-900 pb-2.5">
                  <GitBranch className="w-4 h-4 text-emerald-400" />
                  <span>Historial Git Reciente y Contratos</span>
                </h3>

                <div className="space-y-2 max-h-48 overflow-y-auto custom-scroll pr-1">
                  {(inspection360.git_telemetry?.recent_commits || []).map((c: any) => (
                    <div
                      key={c.hash}
                      className="p-2.5 rounded-xl bg-zinc-950 border border-zinc-900 text-[11px] space-y-0.5"
                    >
                      <div className="flex items-center justify-between font-mono text-[10px]">
                        <span className="text-emerald-400 font-bold flex items-center gap-1">
                          <GitCommit className="w-3 h-3" />
                          {c.hash}
                        </span>
                        <span className="text-zinc-500">{c.when}</span>
                      </div>
                      <p className="text-zinc-200 font-medium truncate">{c.subject}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-2 pt-3 border-t border-zinc-900">
                <span className="text-[10px] font-mono uppercase text-zinc-400 block">
                  Contratos Congelados Aplicados:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {(inspection360.contracts_catalog || []).map((c: any) => (
                    <span
                      key={c.id}
                      title={c.name}
                      className="px-2 py-0.5 rounded-md bg-zinc-900 border border-emerald-500/30 text-[10px] font-mono text-emerald-300 font-bold"
                    >
                      ✓ {c.id}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* 3D. Resultado en Vivo del Sprint Automático (Mesa de Decisión Directa) */}
          {autoSprintResult && autoSprintResult.plan && (
            <div className="p-5 rounded-2xl bg-emerald-950/20 border border-emerald-500/40 space-y-4 animate-fade-in">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-emerald-500/20 pb-3">
                <div>
                  <span className="text-[10px] font-mono uppercase text-emerald-300 font-bold block">
                    ✓ SPRINT SINTETIZADO Y EJECUTADO DESDE LA AUDITORÍA DEL PROYECTO
                  </span>
                  <h3 className="text-sm sm:text-base font-bold text-white">
                    {autoSprintResult.plan.sprint_id} · {autoSprintResult.plan.title}
                  </h3>
                </div>

                <div className="flex items-center gap-2">
                  {onNavigateSection && (
                    <button
                      type="button"
                      onClick={() => onNavigateSection('executions')}
                      className="px-4 py-2 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-extrabold flex items-center gap-1.5 cursor-pointer shadow-sm"
                    >
                      <Play className="w-3.5 h-3.5 text-black" />
                      <span>Ir a la Mesa de Decisiones y Firmar Gate 5</span>
                    </button>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
                {(autoSprintResult.plan.waves || []).map((w: any) => (
                  <div
                    key={w.wave_number}
                    className="p-3 rounded-xl bg-black/90 border border-zinc-800 space-y-1"
                  >
                    <div className="flex items-center justify-between font-mono text-[10px]">
                      <span className="text-emerald-400 font-bold">OLEADA {w.wave_number}</span>
                      <span className="text-zinc-400">{w.expected_duration}</span>
                    </div>
                    <p className="font-bold text-white text-xs">{w.name}</p>
                    <p className="text-[11px] text-zinc-400 font-mono">
                      Agentes: {(w.parallel_agents || []).join(', ')}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 4. Divulgación Progresiva: Explorador de Archivos y Lector de Documentación */}
      <div className="pt-1">
        <button
          type="button"
          onClick={() => setShowFileTree(!showFileTree)}
          className="w-full p-4 rounded-2xl bg-zinc-950 hover:bg-zinc-900 border border-zinc-850 text-xs text-zinc-300 flex items-center justify-between transition cursor-pointer"
        >
          <span className="flex items-center gap-2 font-bold">
            <FolderOpen className="w-4 h-4 text-zinc-400" />
            <span>
              {showFileTree
                ? 'Ocultar explorador de archivos y documentos del proyecto activo'
                : `Inspeccionar archivos y documentos técnicos del proyecto (${fsTree.length} elementos en raíz)`}
            </span>
          </span>
          {showFileTree ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {showFileTree && (
          <div className="mt-3 p-5 rounded-3xl bg-zinc-950 border border-zinc-800 grid grid-cols-1 md:grid-cols-2 gap-4 animate-fade-in">
            <div className="p-3 rounded-2xl bg-black border border-zinc-850 max-h-80 overflow-y-auto custom-scroll space-y-1 font-mono text-xs">
              {fsTree.map((item) => (
                <div
                  key={item.path}
                  onClick={() => {
                    if (!item.is_dir) {
                      handleViewDoc(item.path, item.name)
                    }
                  }}
                  className="flex items-center justify-between p-2 rounded-xl hover:bg-zinc-900 cursor-pointer text-zinc-300 transition"
                >
                  <div className="flex items-center gap-2 truncate">
                    {item.is_dir ? (
                      <FolderGit2 className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
                    ) : (
                      <FileText className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    )}
                    <span className="truncate">{item.name}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="p-4 rounded-2xl bg-black border border-zinc-850 max-h-80 overflow-y-auto custom-scroll">
              {docContent ? (
                <div className="space-y-2">
                  <span className="text-xs font-mono font-bold text-white block border-b border-zinc-800 pb-1">
                    {selectedDocName}
                  </span>
                  <pre className="font-mono text-xs text-zinc-300 whitespace-pre-wrap">
                    {docContent}
                  </pre>
                </div>
              ) : (
                <p className="text-xs text-zinc-500 py-8 text-center">
                  Selecciona un archivo de la izquierda (.md, .json, .py, .ts) para inspeccionar su contenido real en disco.
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* 5. Modal de Importación Manual (Poka-Yoke + Autocomplete) */}
      {showImportModal && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in"
          onClick={() => setShowImportModal(false)}
        >
          <div
            className="bg-[#0C0C0E] border border-white/10 rounded-3xl max-w-lg w-full p-6 space-y-4 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <div>
                <h3 className="text-sm font-bold text-white">
                  Importar Carpeta de Proyecto Manualmente
                </h3>
                <p className="text-[11px] text-zinc-400 mt-0.5">
                  Vincula un repositorio local para auditar sus archivos y gestionar su ciclo de vida.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setShowImportModal(false)}
                className="text-zinc-400 hover:text-white text-xs font-bold cursor-pointer p-1 rounded-lg hover:bg-zinc-800"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleImportProject} className="space-y-4 text-xs">
              <div className="space-y-2">
                <label className="text-zinc-300 font-bold block">
                  Ruta del repositorio o proyecto local:
                </label>
                <input
                  type="text"
                  autoFocus
                  value={importPath}
                  onChange={(e) => setImportPath(e.target.value)}
                  placeholder="Ej: ~/Proyectos/Stable-Ecommerce"
                  className="w-full bg-black border border-zinc-750 focus:border-white rounded-xl px-3.5 py-2.5 text-white font-mono focus:outline-none"
                />

                {/* Micro-interaction: Autocomplete Quick Picks */}
                <div className="space-y-1 pt-1">
                  <span className="text-[10px] font-mono text-zinc-500 uppercase">
                    Rutas rápidas sugeridas:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {[
                      '~/Proyectos/Stable-Ecommerce',
                      './worktrees/integration',
                      '../Stable-Ecommerce',
                    ].map((sug) => (
                      <button
                        key={sug}
                        type="button"
                        onClick={() => setImportPath(sug)}
                        className="px-2 py-1 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-[10px] font-mono text-zinc-300 transition cursor-pointer"
                      >
                        {sug}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="flex items-center gap-2 text-[11px] pt-1">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      isPathValid ? 'bg-emerald-400 animate-pulse' : 'bg-zinc-600'
                    }`}
                  />
                  <span className={isPathValid ? 'text-emerald-400 font-medium' : 'text-zinc-500'}>
                    {isPathValid
                      ? 'Ruta válida &bull; Listo para verificar y cargar en disco'
                      : 'Escribe o selecciona la ruta de la carpeta que deseas agregar'}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-zinc-800">
                <button
                  type="button"
                  onClick={() => setShowImportModal(false)}
                  className="px-4 py-2.5 rounded-xl bg-zinc-900 text-zinc-300 hover:text-white cursor-pointer font-medium"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={!isPathValid || importing}
                  className="px-5 py-2.5 rounded-xl bg-white hover:bg-zinc-200 disabled:opacity-40 text-black font-extrabold cursor-pointer shadow-md flex items-center gap-2"
                >
                  {importing ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin text-black" />
                      <span>Verificando carpeta...</span>
                    </>
                  ) : (
                    <span>Confirmar e Importar</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
