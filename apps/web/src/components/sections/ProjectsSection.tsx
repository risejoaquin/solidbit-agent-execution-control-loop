import React, { useState, useEffect } from 'react'
import {
  FolderGit2,
  GitBranch,
  CheckCircle2,
  RotateCcw,
  Terminal,
  FileCode,
  FileText,
  ChevronRight,
  ExternalLink,
} from 'lucide-react'

export const ProjectsSection: React.FC = () => {
  const [projectsList, setProjectsList] = useState<any[]>([])
  const [activeProjId, setActiveProjId] = useState<string>('')
  const [fsTree, setFsTree] = useState<any[]>([])
  const [docContent, setDocContent] = useState<string | null>(null)
  const [selectedDocName, setSelectedDocName] = useState<string>('')

  const loadData = async () => {
    try {
      const res = await fetch('/api/projects')
      const data = await res.json()
      if (data && data.projects) {
        setProjectsList(data.projects)
        setActiveProjId(data.active_project || (data.projects[0]?.id ?? ''))
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
        loadData()
      } else {
        alert('Error cambiando proyecto: ' + (data.error || 'No permitido'))
      }
    } catch (e: any) {
      alert('Error de red: ' + e.message)
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
      alert('Error leyendo documento: ' + e.message)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-3xl bg-zinc-950 border border-zinc-800">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold text-white tracking-wide">
              Gestor de Espacios de Trabajo & Repositorios (/api/projects)
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-white/10 text-zinc-200 border border-emerald-500/30">
              {projectsList.length} Proyectos Descubiertos
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Gestión física del árbol de trabajo, navegación de archivos y ejecución de scripts locales
          </p>
        </div>

        <button
          onClick={loadData}
          className="px-3 py-1.5 rounded-xl bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-xs text-zinc-300 flex items-center gap-1.5 transition cursor-pointer"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Escanear Proyectos</span>
        </button>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {projectsList.map((p) => {
          const isActive = p.id === activeProjId || p.is_active
          return (
            <div
              key={p.id}
              className={`p-5 rounded-3xl transition space-y-4 border ${
                isActive
                  ? 'bg-[#121a26] border-emerald-500/50 shadow-lg shadow-emerald-500/5'
                  : 'bg-zinc-950 border-zinc-800 hover:border-zinc-700'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="w-10 h-10 rounded-2xl bg-white/10 border border-emerald-500/20 flex items-center justify-center text-zinc-200">
                  <FolderGit2 className="w-5 h-5" />
                </div>
                <span
                  className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${
                    isActive
                      ? 'bg-white/10 text-zinc-200 border border-emerald-500/30 font-bold'
                      : 'bg-zinc-800 text-zinc-400'
                  }`}
                >
                  {isActive ? 'PROYECTO ACTIVO' : 'DISPONIBLE'}
                </span>
              </div>

              <div>
                <h3 className="text-sm font-bold text-white">{p.name}</h3>
                <p className="text-[11px] font-mono text-zinc-400 truncate mt-0.5" title={p.path}>
                  {p.path}
                </p>
              </div>

              {/* Detected scripts from package.json/Makefile */}
              {p.detected_scripts && p.detected_scripts.length > 0 && (
                <div className="space-y-1.5 pt-2 border-t border-zinc-800">
                  <span className="text-[10px] font-mono text-zinc-500 uppercase">Scripts Detectados:</span>
                  <div className="flex flex-wrap gap-1">
                    {p.detected_scripts.slice(0, 3).map((sc: string) => (
                      <span key={sc} className="px-2 py-0.5 rounded-md bg-black/40 border border-white/5 text-[10px] font-mono text-zinc-300">
                        {sc}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {!isActive && (
                <button
                  onClick={() => handleSwitchProject(p.id)}
                  className="w-full py-2 rounded-xl bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-xs text-white font-medium transition cursor-pointer"
                >
                  Activar este Proyecto
                </button>
              )}
            </div>
          )
        })}
      </div>

      {/* Workspace Files Tree */}
      <div className="p-6 rounded-3xl bg-zinc-950 border border-zinc-800 space-y-4 shadow-xl">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-zinc-200" />
            <h2 className="text-sm font-bold text-white">Árbol Físico de Archivos (/api/fs/tree)</h2>
          </div>
          <span className="text-xs text-zinc-400 font-mono">{fsTree.length} elementos raíz</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* File list */}
          <div className="p-3 rounded-2xl bg-[#070b10] border border-zinc-800 max-h-80 overflow-y-auto custom-scroll space-y-1 font-mono text-xs">
            {fsTree.map((item) => (
              <div
                key={item.path}
                onClick={() => {
                  if (item.extension === '.md' || item.extension === '.json') {
                    handleViewDoc(item.path, item.name)
                  }
                }}
                className="flex items-center justify-between p-2 rounded-xl hover:bg-white/5 cursor-pointer text-zinc-300 transition"
              >
                <div className="flex items-center gap-2 truncate">
                  {item.is_dir ? (
                    <FolderGit2 className="w-3.5 h-3.5 text-zinc-300 shrink-0" />
                  ) : (
                    <FileText className="w-3.5 h-3.5 text-zinc-200 shrink-0" />
                  )}
                  <span className="truncate">{item.name}</span>
                </div>
                {!item.is_dir && (
                  <span className="text-[10px] text-zinc-500 shrink-0">{item.size_bytes} B</span>
                )}
              </div>
            ))}
          </div>

          {/* Document Preview */}
          <div className="p-4 rounded-2xl bg-[#070b10] border border-zinc-800 max-h-80 overflow-y-auto custom-scroll">
            {docContent ? (
              <div className="space-y-2">
                <span className="text-xs font-mono font-bold text-zinc-200 block border-b border-white/5 pb-1">
                  {selectedDocName}
                </span>
                <pre className="font-mono text-xs text-zinc-300 whitespace-pre-wrap">{docContent}</pre>
              </div>
            ) : (
              <p className="text-xs text-zinc-500 font-mono py-8 text-center">
                Haz clic en cualquier archivo .md o .json del árbol para previsualizar su contenido.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
