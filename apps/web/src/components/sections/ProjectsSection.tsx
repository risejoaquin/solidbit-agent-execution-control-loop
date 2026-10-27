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
} from 'lucide-react'

export const ProjectsSection: React.FC = () => {
  const [projectsList, setProjectsList] = useState<any[]>([])
  const [activeProjId, setActiveProjId] = useState<string>('')
  const [fsTree, setFsTree] = useState<any[]>([])
  const [docContent, setDocContent] = useState<string | null>(null)
  const [selectedDocName, setSelectedDocName] = useState<string>('')
  const [showFileTree, setShowFileTree] = useState<boolean>(false)

  // Manual Import Form State (Poka-Yoke + Inline Validation)
  const [showImportModal, setShowImportModal] = useState<boolean>(false)
  const [importPath, setImportPath] = useState<string>('')
  const [importing, setImporting] = useState<boolean>(false)
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(
    null
  )

  const loadData = async () => {
    try {
      const res = await fetch('/api/projects')
      const data = await res.json()
      if (data && data.projects) {
        setProjectsList(data.projects)
        const active = data.projects.find((p: any) => p.is_active)
        setActiveProjId(active?.id || data.active_project || (data.projects[0]?.id ?? ''))
      }
    } catch (e) {
      console.warn('Error loading projects:', e)
    }

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
        setFeedback({ type: 'success', message: data.message || 'Proyecto activado.' })
        loadData()
      } else {
        setFeedback({ type: 'error', message: data.error || 'No se pudo activar el proyecto.' })
      }
    } catch (e: any) {
      setFeedback({ type: 'error', message: 'Error de red: ' + e.message })
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
        loadData()
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
        loadData()
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

  // Poka-Yoke inline check for Windows/Unix folder path
  const isPathValid = importPath.trim().length >= 3

  return (
    <div className="space-y-6 max-w-5xl mx-auto animate-fade-in">
      {/* 1. Clean Header (Hick's Law: Single Primary CTA "+ Importar Carpeta Manualmente") */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-6 rounded-3xl bg-zinc-950 border border-zinc-800 shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2.5">
            <h1 className="text-lg font-extrabold text-white tracking-tight">
              Mis Proyectos Importados
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold bg-zinc-900 text-zinc-200 border border-zinc-700">
              {projectsList.length} {projectsList.length === 1 ? 'Proyecto' : 'Proyectos'}
            </span>
          </div>
          <p className="text-xs text-zinc-400">
            Solo aparecen las carpetas que tú importas manualmente. No escaneamos carpetas personales de tu computadora.
          </p>
        </div>

        <button
          type="button"
          onClick={() => {
            setShowImportModal(true)
            setFeedback(null)
          }}
          className="px-4 py-2.5 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-extrabold flex items-center gap-2 transition cursor-pointer shadow-sm shrink-0"
        >
          <Plus className="w-4 h-4 text-black" />
          <span>+ Importar Carpeta Manualmente</span>
        </button>
      </div>

      {/* Inline Feedback Banner */}
      {feedback && (
        <div
          className={`p-4 rounded-2xl border text-xs flex items-center justify-between gap-3 ${
            feedback.type === 'success'
              ? 'bg-zinc-900 border-emerald-500/40 text-white'
              : 'bg-zinc-900 border-amber-500/40 text-zinc-200'
          }`}
        >
          <div className="flex items-center gap-2.5">
            {feedback.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
            )}
            <span>{feedback.message}</span>
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

      {/* 2. Imported Projects Cards */}
      {projectsList.length === 0 ? (
        <div className="p-10 rounded-3xl bg-zinc-950 border border-zinc-800 text-center space-y-3">
          <FolderGit2 className="w-8 h-8 text-zinc-500 mx-auto" />
          <h3 className="text-sm font-bold text-white">No has importado ningún proyecto todavía</h3>
          <p className="text-xs text-zinc-400 max-w-md mx-auto">
            Agrega la ruta de la carpeta donde tienes tu código para trabajar sobre ella de forma limpia y ordenada.
          </p>
          <button
            type="button"
            onClick={() => setShowImportModal(true)}
            className="px-4 py-2 rounded-xl bg-white text-black text-xs font-bold cursor-pointer"
          >
            + Importar mi primera carpeta
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {projectsList.map((p) => {
            const isActive = p.id === activeProjId || p.is_active
            return (
              <div
                key={p.id}
                className={`p-5 rounded-3xl transition flex flex-col justify-between space-y-4 border ${
                  isActive
                    ? 'bg-zinc-900 border-white ring-1 ring-white shadow-lg'
                    : 'bg-zinc-950 border-zinc-800 hover:border-zinc-700'
                }`}
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 ${
                          isActive
                            ? 'bg-white text-black'
                            : 'bg-zinc-900 border border-zinc-800 text-zinc-200'
                        }`}
                      >
                        <FolderGit2 className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="text-sm font-bold text-white">{p.name}</h3>
                        <span className="text-[11px] text-zinc-400 block">
                          Rama: <strong className="text-zinc-200 font-mono">{p.branch || 'main'}</strong>
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center gap-1.5">
                      <span
                        className={`text-[10px] font-mono px-2.5 py-0.5 rounded-full font-bold ${
                          isActive
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                            : 'bg-zinc-800 text-zinc-400'
                        }`}
                      >
                        {isActive ? '✓ EN USO' : 'GUARDADO'}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleRemoveProject(p.id, p.name)}
                        className="p-1.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-red-400 transition cursor-pointer"
                        title="Quitar de la lista"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  <div className="p-2.5 rounded-xl bg-black border border-zinc-850 text-[11px] font-mono text-zinc-300 truncate">
                    {p.path}
                  </div>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-zinc-850">
                  <div className="flex flex-wrap gap-1.5">
                    {(p.tech_stack || []).slice(0, 3).map((t: string) => (
                      <span
                        key={t}
                        className="px-2 py-0.5 rounded-md bg-black border border-zinc-800 text-[10px] font-mono text-zinc-300"
                      >
                        {t}
                      </span>
                    ))}
                  </div>

                  {!isActive && (
                    <button
                      type="button"
                      onClick={() => handleSwitchProject(p.id)}
                      className="px-3.5 py-1.5 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-bold transition cursor-pointer"
                    >
                      Trabajar aquí
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* 3. Progressive Disclosure: File Explorer tucked behind a clean toggle */}
      <div className="pt-2">
        <button
          type="button"
          onClick={() => setShowFileTree(!showFileTree)}
          className="w-full p-4 rounded-2xl bg-zinc-950 hover:bg-zinc-900 border border-zinc-850 text-xs text-zinc-300 flex items-center justify-between transition cursor-pointer"
        >
          <span className="flex items-center gap-2 font-bold">
            <FolderOpen className="w-4 h-4 text-zinc-400" />
            <span>
              {showFileTree
                ? 'Ocultar explorador de archivos del proyecto activo'
                : `Explorar archivos dentro del proyecto activo (${fsTree.length} elementos)`}
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
                    if (item.extension === '.md' || item.extension === '.json') {
                      handleViewDoc(item.path, item.name)
                    }
                  }}
                  className="flex items-center justify-between p-2 rounded-xl hover:bg-zinc-900 cursor-pointer text-zinc-300 transition"
                >
                  <div className="flex items-center gap-2 truncate">
                    {item.is_dir ? (
                      <FolderGit2 className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
                    ) : (
                      <FileText className="w-3.5 h-3.5 text-zinc-200 shrink-0" />
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
                  Selecciona un archivo .md o .json de la izquierda para leer su contenido.
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* 4. Manual Folder Import Modal (Poka-Yoke + Smart Suggestions) */}
      {showImportModal && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in"
          onClick={() => setShowImportModal(false)}
        >
          <div
            className="bg-zinc-950 border border-zinc-800 rounded-3xl max-w-lg w-full p-6 space-y-4 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-zinc-850 pb-3">
              <h3 className="text-sm font-bold text-white">
                Importar Carpeta de Proyecto Manualmente
              </h3>
              <button
                type="button"
                onClick={() => setShowImportModal(false)}
                className="text-zinc-400 hover:text-white text-xs font-bold cursor-pointer"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleImportProject} className="space-y-4 text-xs">
              <div className="space-y-1.5">
                <label className="text-zinc-300 font-bold block">
                  Pega la ruta completa de la carpeta en tu computadora:
                </label>
                <input
                  type="text"
                  autoFocus
                  value={importPath}
                  onChange={(e) => setImportPath(e.target.value)}
                  placeholder="Ej: C:\Users\TuUsuario\Documents\Stable-Ecommerce"
                  className="w-full bg-black border border-zinc-750 rounded-xl px-3.5 py-2.5 text-white font-mono focus:outline-none focus:border-white"
                />
                <div className="flex items-center gap-1.5 text-[11px] pt-1">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      isPathValid ? 'bg-emerald-400' : 'bg-zinc-600'
                    }`}
                  />
                  <span className={isPathValid ? 'text-emerald-400' : 'text-zinc-500'}>
                    {isPathValid
                      ? 'Formato de ruta listo para verificar en disco'
                      : 'Escribe o pega la ruta de la carpeta que deseas agregar'}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-zinc-850">
                <button
                  type="button"
                  onClick={() => setShowImportModal(false)}
                  className="px-4 py-2 rounded-xl bg-zinc-900 text-zinc-300 hover:text-white cursor-pointer"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={!isPathValid || importing}
                  className="px-5 py-2 rounded-xl bg-white hover:bg-zinc-200 disabled:opacity-40 text-black font-bold cursor-pointer"
                >
                  {importing ? 'Verificando carpeta...' : 'Importar Carpeta'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
