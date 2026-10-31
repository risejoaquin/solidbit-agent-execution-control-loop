import React, { useState } from 'react'

export interface WorkspaceContext {
  workspace_id: string
  name: string
  path: string
  branch: string
  is_clean?: boolean
}

interface WorkspaceSelectorProps {
  onWorkspaceMounted: (workspace: WorkspaceContext) => void
  currentPath?: string
}

export const WorkspaceSelector: React.FC<WorkspaceSelectorProps> = ({
  onWorkspaceMounted,
  currentPath = '',
}) => {
  const [workspacePath, setWorkspacePath] = useState(currentPath)
  const [isValidating, setIsValidating] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const handleMount = async (e: React.FormEvent) => {
    e.preventDefault()
    const trimmedPath = workspacePath.trim()
    if (!trimmedPath || isValidating) return

    setIsValidating(true)
    setErrorMessage(null)

    try {
      const res = await fetch('/api/workspace/mount', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: trimmedPath }),
      })

      const data = await res.json()

      if (res.ok && data.success) {
        onWorkspaceMounted({
          workspace_id: data.workspace_id || `ws-${Date.now()}`,
          name: data.name || 'Workspace Local',
          path: data.path || trimmedPath,
          branch: data.branch || 'main',
          is_clean: data.is_clean ?? true,
        })
      } else {
        setErrorMessage(data.error || 'La ruta especificada no cuenta con una estructura válida de repositorio Git.')
      }
    } catch (err: any) {
      setErrorMessage(`Fallo de conexión con el demonio local: ${err.message}`)
    } finally {
      setIsValidating(false)
    }
  }

  return (
    <div id="workspace-context-boundary" className="fixed inset-0 z-[200] bg-black/90 backdrop-blur-sm flex items-center justify-center p-4 select-none">
      <div className="w-full max-w-lg bg-[#0a0a0a] border border-white/8 rounded-lg p-6 shadow-none text-left">
        {/* Header de Seguridad */}
        <div className="flex items-center gap-3 pb-4 border-b border-white/8">
          <div className="w-8 h-8 rounded bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center shrink-0">
            <svg className="w-4 h-4 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
          </div>
          <div>
            <h2 className="text-sm font-semibold text-white tracking-wide uppercase">Context Boundary · EOP</h2>
            <p className="text-[11px] text-zinc-500 font-mono mt-0.5">Inicialización de Workspace Local Obligatoria</p>
          </div>
        </div>

        {/* Descripción */}
        <p className="text-xs text-zinc-400 font-sans mt-4 leading-relaxed">
          Para garantizar el aislamiento de operaciones y la integridad de contratos, define el directorio raíz del repositorio de trabajo. El demonio local validará la estructura y permisos antes de habilitar el Control Plane.
        </p>

        {/* Formulario */}
        <form onSubmit={handleMount} className="mt-5 space-y-4">
          <div>
            <label className="text-[10px] font-mono text-zinc-400 block mb-1.5 uppercase tracking-wider">
              Ruta del Proyecto en Disco
            </label>
            <input
              id="workspace-path-input"
              type="text"
              value={workspacePath}
              onChange={(e) => setWorkspacePath(e.target.value)}
              placeholder="Ej: C:\Proyectos\Mi-Proyecto-EOP o /home/user/workspace"
              className="w-full bg-[#000000] border border-white/8 rounded px-3 py-2 text-xs font-mono text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-white/20 transition"
              disabled={isValidating}
              autoFocus
            />
          </div>

          {errorMessage && (
            <div className="p-3 rounded bg-red-500/10 border border-red-500/20 flex items-start gap-2.5">
              <svg className="w-4 h-4 text-red-400 shrink-0 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" x2="12" y1="8" y2="12" />
                <line x1="12" x2="12.01" y1="16" y2="16" />
              </svg>
              <span className="text-[11px] text-red-400 font-sans">{errorMessage}</span>
            </div>
          )}

          <div className="pt-2 flex items-center justify-between">
            <span className="text-[10px] font-mono text-zinc-500">Handshake: POST /api/workspace/mount</span>
            <button
              id="workspace-mount-btn"
              type="submit"
              disabled={!workspacePath.trim() || isValidating}
              className={`px-4 py-2 rounded text-xs font-medium transition border flex items-center gap-2 ${
                workspacePath.trim() && !isValidating
                  ? 'bg-white text-black border-white hover:bg-zinc-200 cursor-pointer'
                  : 'bg-zinc-900 text-zinc-600 border-white/8 cursor-not-allowed'
              }`}
            >
              {isValidating && (
                <svg className="w-3.5 h-3.5 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 12a9 9 0 1 1-6.219-8.56" />
                </svg>
              )}
              <span>{isValidating ? 'Validando Integridad...' : 'Montar Workspace'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
