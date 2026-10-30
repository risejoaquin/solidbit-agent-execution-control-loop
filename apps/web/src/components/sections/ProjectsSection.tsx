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
  Loader2,
  RefreshCw,
  Award,
} from 'lucide-react'
import { StatusBadge } from '../ui/status-badge'

interface ProjectsSectionProps {
  onLaunchAutoSprint?: (planData: any) => void
  onNavigateSection?: (section: string) => void
  activeProject?: any
  projects?: any[]
  onProjectRemoved?: (projId: string) => Promise<void> | void
  onRefreshAll?: () => Promise<void> | void
}

export const ProjectsSection: React.FC<ProjectsSectionProps> = ({
  onLaunchAutoSprint,
  onNavigateSection,
  activeProject,
  projects,
  onProjectRemoved,
  onRefreshAll,
}) => {
  const [projectsList, setProjectsList] = useState<any[]>([])
  const [activeProjId, setActiveProjId] = useState<string>('')
  const [inspection360, setInspection360] = useState<any | null>(null)
  const [loading360, setLoading360] = useState<boolean>(false)
  const [planningAutoSprint, setPlanningAutoSprint] = useState<boolean>(false)
  const [importPath, setImportPath] = useState<string>('')
  const [importing, setImporting] = useState<boolean>(false)
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null)
  const [showAdvanced, setShowAdvanced] = useState<boolean>(false)

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
      console.warn('Error cargando inspección:', e)
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
      if (projects) {
        setProjectsList(projects)
        const active = projects.find((p: any) => p.is_active) || projects[0]
        currentActiveId = active?.id ?? ''
        setActiveProjId(currentActiveId)
      }
    }
    if (currentActiveId) {
      loadInspection360(currentActiveId)
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
      if (res.ok && data.success) {
        setActiveProjId(projId)
        setFeedback({ type: 'success', message: `Proyecto activo cambiado a "${data.active?.name || projId}".` })
        await loadInspection360(projId)
        if (onRefreshAll) await onRefreshAll()
      }
    } catch (e) {
      setFeedback({ type: 'error', message: 'Error al cambiar de proyecto.' })
    }
  }

  const handleRemoveProject = async (projId: string, projName: string) => {
    try {
      const res = await fetch('/api/projects/remove', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projId }),
      })
      const data = await res.json()
      if (res.ok && data.success) {
        setProjectsList((prev) => prev.filter((p) => p.id !== projId))
        setFeedback({ type: 'success', message: `Proyecto "${projName}" quitado con éxito.` })
        if (onProjectRemoved) {
          await onProjectRemoved(projId)
        }
      }
    } catch (e) {
      setFeedback({ type: 'error', message: 'Error al quitar el proyecto.' })
    }
  }

  const handleImportProject = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!importPath.trim() || importPath.trim().length < 3) return

    setImporting(true)
    setFeedback(null)
    try {
      const res = await fetch('/api/projects/import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: importPath.trim(), set_active: true }),
      })
      const data = await res.json()
      if (res.ok && data.success) {
        setFeedback({ type: 'success', message: `¡Proyecto "${data.project?.name}" vinculado con éxito!` })
        setImportPath('')
        await loadData()
        if (onRefreshAll) await onRefreshAll()
      } else {
        setFeedback({ type: 'error', message: data.message || 'No se pudo vincular la carpeta.' })
      }
    } catch (err: any) {
      setFeedback({ type: 'error', message: 'Error de red al importar carpeta.' })
    } finally {
      setImporting(false)
    }
  }

  const handleAuditAndAutoSprint = async (autoExecute: boolean = true) => {
    setPlanningAutoSprint(true)
    setFeedback(null)
    try {
      const res = await fetch('/api/projects/audit-and-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: activeProjId || 'default',
          auto_execute: autoExecute,
        }),
      })
      const data = await res.json()
      if (res.ok && data.success) {
        setFeedback({
          type: 'success',
          message: data.message || 'Sprint diseñado y ejecutado automáticamente con éxito.',
        })
        if (onLaunchAutoSprint) {
          onLaunchAutoSprint(data)
        }
      } else {
        setFeedback({ type: 'error', message: data.message || 'Error al sintetizar el sprint automático.' })
      }
    } catch (e: any) {
      setFeedback({ type: 'error', message: 'Error al procesar la auditoría y síntesis del sprint.' })
    } finally {
      setPlanningAutoSprint(false)
    }
  }

  const activeProj = projectsList.find((p) => p.id === activeProjId || p.is_active) || projectsList[0]

  return (
    <div className="space-y-6 max-w-5xl mx-auto animate-fade-in pb-12 text-left">
      {/* Header Simple y Limpio */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-3xl bg-[#0C0C0E] border border-white/5 shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2.5">
            <h1 className="text-lg font-extrabold text-white tracking-tight">
              Proyectos & Repositorios
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold bg-zinc-900 text-zinc-300 border border-zinc-750">
              {projectsList.length} {projectsList.length === 1 ? 'vinculado' : 'vinculados'}
            </span>
          </div>
          <p className="text-xs text-zinc-400">
            Administra los repositorios que alimentan el flujo de trabajo de los agentes.
          </p>
        </div>

        {/* Botón Primario de Auto-Sprint (Compatible con suite E2E) */}
        <button
          type="button"
          onClick={() => handleAuditAndAutoSprint(true)}
          disabled={planningAutoSprint || loading360}
          className="px-5 py-2.5 rounded-2xl bg-white hover:bg-zinc-200 text-black text-xs font-extrabold flex items-center gap-2 transition cursor-pointer shadow-lg disabled:opacity-50 shrink-0"
        >
          {planningAutoSprint ? (
            <Loader2 className="w-4 h-4 animate-spin text-black" />
          ) : (
            <Sparkles className="w-4 h-4 text-black" />
          )}
          <span>
            {planningAutoSprint
              ? 'Sintetizando y Ejecutando Sprint...'
              : '⚡ Diseñar y Ejecutar Sprint Automático desde Auditoría'}
          </span>
        </button>
      </div>

      {/* Feedback Banner */}
      {feedback && (
        <div
          className={`p-4 rounded-2xl border text-xs flex items-center justify-between gap-3 ${
            feedback.type === 'success'
              ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-200'
              : 'bg-amber-950/40 border-amber-500/40 text-amber-200'
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
            ✕
          </button>
        </div>
      )}

      {/* Tarjeta del Proyecto Activo (KISS) */}
      {activeProj && (
        <div className="p-6 rounded-3xl bg-[#0C0C0E] border border-white/10 space-y-4 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/5 pb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-white text-black flex items-center justify-center font-extrabold text-sm shrink-0">
                <FolderGit2 className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-emerald-400 font-bold">
                  Proyecto en Sesión
                </span>
                <h2 className="text-base font-extrabold text-white">{activeProj.name}</h2>
              </div>
            </div>
            <StatusBadge status="SUCCESS" label="PROYECTO ACTIVO" pulsing />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs font-mono">
            <div className="p-3 rounded-2xl bg-black border border-white/5">
              <span className="text-zinc-500 block text-[10px] uppercase">Ruta en Disco</span>
              <span className="text-zinc-200 truncate block mt-0.5" title={activeProj.path}>
                {activeProj.path}
              </span>
            </div>
            <div className="p-3 rounded-2xl bg-black border border-white/5">
              <span className="text-zinc-500 block text-[10px] uppercase">Rama de Git</span>
              <span className="text-sky-400 font-bold block mt-0.5 flex items-center gap-1.5">
                <GitBranch className="w-3.5 h-3.5" />
                {activeProj.branch || 'main'}
              </span>
            </div>
            <div className="p-3 rounded-2xl bg-black border border-white/5">
              <span className="text-zinc-500 block text-[10px] uppercase">Último Commit</span>
              <span className="text-emerald-400 font-bold block mt-0.5 flex items-center gap-1.5">
                <GitCommit className="w-3.5 h-3.5" />
                {(activeProj.commit_hash || 'HEAD').substring(0, 7)}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Formulario Sencillo: Vincular Carpeta Local (1 línea, KISS) */}
      <div className="p-5 rounded-3xl bg-[#0C0C0E] border border-white/5 space-y-3 shadow-md">
        <span className="text-xs font-bold text-white block">
          Vincular Carpeta o Repositorio Local
        </span>
        <form onSubmit={handleImportProject} className="flex flex-col sm:flex-row gap-2.5">
          <input
            type="text"
            value={importPath}
            onChange={(e) => setImportPath(e.target.value)}
            placeholder="Ej: C:\MisProyectos\MiTiendaOnline o /home/user/app"
            className="flex-1 bg-black border border-zinc-800 focus:border-white rounded-2xl px-4 py-2.5 text-xs text-white placeholder-zinc-500 font-mono focus:outline-none"
          />
          <button
            type="submit"
            disabled={importing || importPath.trim().length < 3}
            className="px-5 py-2.5 rounded-2xl bg-zinc-900 hover:bg-zinc-800 disabled:opacity-40 text-white border border-zinc-750 text-xs font-bold flex items-center justify-center gap-2 transition cursor-pointer shrink-0"
          >
            {importing ? (
              <Loader2 className="w-4 h-4 animate-spin text-white" />
            ) : (
              <Plus className="w-4 h-4 text-emerald-400" />
            )}
            <span>Vincular Carpeta</span>
          </button>
        </form>
      </div>

      {/* Lista de Otros Proyectos Vinculados */}
      {projectsList.length > 1 && (
        <div className="space-y-3">
          <span className="text-xs font-bold text-zinc-400 uppercase tracking-wider block font-mono">
            Otros Repositorios ({projectsList.length - 1})
          </span>
          <div className="space-y-2">
            {projectsList
              .filter((p) => p.id !== activeProj?.id)
              .map((p) => (
                <div
                  key={p.id}
                  className="p-3.5 rounded-2xl bg-[#0C0C0E] border border-white/5 flex items-center justify-between gap-3 text-xs"
                >
                  <div className="min-w-0">
                    <span className="font-bold text-white block truncate">{p.name}</span>
                    <span className="text-[11px] font-mono text-zinc-500 block truncate">{p.path}</span>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      type="button"
                      onClick={() => handleSwitchProject(p.id)}
                      className="px-3 py-1.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-white border border-zinc-750 text-xs font-bold transition cursor-pointer"
                    >
                      Activar
                    </button>
                    <button
                      type="button"
                      onClick={() => handleRemoveProject(p.id, p.name)}
                      className="p-1.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-rose-400 transition cursor-pointer"
                      title="Quitar proyecto"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Auditoría Técnica Avanzada en 5 Dimensiones (Colapsada por defecto para Cero Ruido) */}
      {inspection360 && (
        <details className="group border border-white/5 rounded-3xl bg-[#0C0C0E] overflow-hidden">
          <summary className="p-4 sm:p-5 flex items-center justify-between text-xs font-mono text-zinc-400 hover:text-white cursor-pointer select-none">
            <span className="flex items-center gap-2 font-bold uppercase tracking-wider">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Ver Auditoría Técnica Completa en 5 Dimensiones (Opcional)</span>
            </span>
            <span className="text-[10px] uppercase font-bold text-zinc-500 group-open:rotate-180 transition-transform">
              ▼
            </span>
          </summary>

          <div className="p-5 pt-0 border-t border-white/5 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-3 pt-3">
              {(inspection360.audit_dimensions || []).map((dim: any) => (
                <div key={dim.id} className="p-3.5 rounded-2xl bg-black border border-white/5 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono text-emerald-400 font-bold">{dim.character}</span>
                    <span className="text-xs font-mono font-bold text-white">{dim.score}%</span>
                  </div>
                  <h4 className="text-xs font-bold text-white">{dim.dimension}</h4>
                  <p className="text-[11px] text-zinc-400">{dim.summary}</p>
                </div>
              ))}
            </div>
          </div>
        </details>
      )}
    </div>
  )
}
