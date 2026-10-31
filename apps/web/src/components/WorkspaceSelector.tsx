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
  const [isBrowsing, setIsBrowsing] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const handleBrowseNative = async () => {
    setIsBrowsing(true)
    setErrorMessage(null)
    try {
      const res = await fetch('/api/workspace/browse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
      const data = await res.json()
      if (res.ok && data.success && data.path) {
        setWorkspacePath(data.path)
      }
    } catch (err: any) {
      setErrorMessage(`No se pudo abrir el explorador nativo: ${err.message}`)
    } finally {
      setIsBrowsing(false)
    }
  }

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
            <h2 className="text-sm font-semibold text-white tracking-wide uppercase font-sans">Context Boundary · EOP</h2>
            <p className="text-[11px] text-zinc-500 font-mono mt-0.5">Inicialización de Workspace Local Obligatoria</p>
          </div>
        </div>

        {/* Descripción */}
        <p className="text-xs text-zinc-400 font-sans mt-4 leading-relaxed">
          Para garantizar el aislamiento de operaciones y la integridad de contratos, define el directorio raíz del repositorio de trabajo. El demonio local validará la estructura y permisos antes de habilitar el Control Plane.
        </p>

        {/* Formulario con Explorador Nativo IPC */}
        <form onSubmit={handleMount} className="mt-5 space-y-4">
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider">
                Ruta del Proyecto en Disco
              </label>
              <button
                type="button"
                onClick={handleBrowseNative}
                disabled={isBrowsing || isValidating}
                className="text-[10px] font-mono text-emerald-400 hover:text-emerald-300 transition flex items-center gap-1 cursor-pointer disabled:opacity-50"
              >
                <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z" />
                </svg>
                {isBrowsing ? 'Abriendo explorador...' : '📁 Explorar Sistema (Nativo)'}
              </button>
            </div>
            <div className="flex gap-2">
              <input
                id="workspace-path-input"
                type="text"
                value={workspacePath}
                onChange={(e) => setWorkspacePath(e.target.value)}
                placeholder="Ej: C:\Proyectos\Mi-Proyecto-EOP o selecciona Explorar"
                className="flex-1 bg-[#000000] border border-white/8 rounded px-3 py-2 text-xs font-mono text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-white/20 transition"
                disabled={isValidating || isBrowsing}
                autoFocus
              />
              <button
                type="button"
                onClick={handleBrowseNative}
                disabled={isBrowsing || isValidating}
                className="px-3 py-2 bg-[#121212] border border-white/8 rounded text-xs font-mono text-zinc-300 hover:border-white/20 transition cursor-pointer"
                title="Abrir explorador de carpetas del sistema operativo"
              >
                Buscar
              </button>
            </div>
          </div>

          {errorMessage && (
            <div className="p-3 rounded bg-red-500/10 border border-red-500/20 flex items-start gap-2.5">
              <span className="text-red-400 text-xs font-mono">✕</span>
              <p className="text-xs font-mono text-red-400 leading-normal">{errorMessage}</p>
            </div>
          )}

          <div className="pt-2 flex items-center justify-between">
            <span className="text-[10px] font-mono text-zinc-600">Handshake SQLite WAL & Git Branch</span>
            <button
              id="workspace-mount-btn"
              type="submit"
              disabled={isValidating || isBrowsing || !workspacePath.trim()}
              className="px-4 py-2 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20 transition text-xs font-mono font-medium flex items-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            >
              {isValidating ? (
                <>
                  <div className="w-3 h-3 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
                  <span>Validando Entorno...</span>
                </>
              ) : (
                <span>Vincular Workspace ➔</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
