import React, { useState, useEffect } from 'react'
import {
  X,
  GitBranch,
  FileCode,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Plus,
  Minus,
  Layers,
} from 'lucide-react'

interface DiffChunkLine {
  type: 'add' | 'del' | 'ctx'
  text: string
  old_num: number | null
  new_num: number | null
}

interface DiffChunk {
  header: string
  lines: DiffChunkLine[]
}

interface DiffFile {
  path: string
  status: 'modified' | 'added' | 'deleted' | 'untracked' | 'renamed'
  additions: number
  deletions: number
  chunks: DiffChunk[]
}

interface DiffInspectorModalProps {
  isOpen: boolean
  onClose: () => void
  onChangesApplied?: () => void
}

export const DiffInspectorModal: React.FC<DiffInspectorModalProps> = ({
  isOpen,
  onClose,
  onChangesApplied,
}) => {
  const [loading, setLoading] = useState<boolean>(true)
  const [diffData, setDiffData] = useState<{
    branch?: string
    commit?: string
    total_files?: number
    total_additions?: number
    total_deletions?: number
    files: DiffFile[]
  }>({ files: [] })
  const [selectedFileIdx, setSelectedFileIdx] = useState<number>(0)
  const [reverting, setReverting] = useState<boolean>(false)

  const loadDiff = async () => {
    setLoading(true)
    try {
      const [diffRes, statusRes] = await Promise.all([
        fetch('/api/git/diff'),
        fetch('/api/git/status'),
      ])
      const dData = await diffRes.json()
      const sData = await statusRes.json()

      setDiffData({
        branch: sData.branch || 'integration',
        commit: sData.commit || 'HEAD',
        total_files: dData.total_files || 0,
        total_additions: dData.total_additions || 0,
        total_deletions: dData.total_deletions || 0,
        files: dData.files || [],
      })
      if (selectedFileIdx >= (dData.files?.length || 0)) {
        setSelectedFileIdx(0)
      }
    } catch (e) {
      console.warn('Error loading git diff:', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isOpen) {
      loadDiff()
    }
  }, [isOpen])

  if (!isOpen) return null

  const selectedFile = diffData.files[selectedFileIdx] || null

  const handleRevert = async (filePath: string) => {
    if (!confirm(`¿Restaurar archivo '${filePath}' a HEAD? Los cambios locales no confirmados se descartarán.`)) {
      return
    }
    setReverting(true)
    try {
      const res = await fetch('/api/git/revert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_path: filePath }),
      })
      const data = await res.json()
      if (data.success) {
        await loadDiff()
        onChangesApplied?.()
      } else {
        alert('Error al revertir: ' + data.error)
      }
    } catch (e: any) {
      alert('Error de conexión al revertir: ' + e.message)
    } finally {
      setReverting(false)
    }
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/80 backdrop-blur-md animate-fade-in"
    >
      <div className="w-full max-w-6xl h-[88vh] bg-[#0c121a] border border-[#1b2533] rounded-3xl shadow-2xl flex flex-col overflow-hidden">
        {/* Header bar */}
        <div className="px-5 py-4 border-b border-[#1b2533] bg-[#090e16] flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0">
              <GitBranch className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm sm:text-base font-extrabold text-white tracking-wide">
                  Inspector de Diffs Git & Cambios en Worktree
                </h2>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold">
                  {diffData.branch} @ {diffData.commit}
                </span>
              </div>
              <p className="text-xs text-zinc-400 mt-0.5">
                Inspección granular de código antes de autorizar firmas HMAC de compuertas HITL.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={loadDiff}
              disabled={loading}
              className="p-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-300 hover:text-white border border-zinc-800 transition cursor-pointer"
              title="Refrescar diff"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-emerald-400' : ''}`} />
            </button>
            <button
              type="button"
              onClick={onClose}
              className="p-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-300 hover:text-white border border-zinc-800 transition cursor-pointer"
              title="Cerrar modal"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Diff Content Body: 2 Columns on desktop (File List | Diff Code) */}
        <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
          {/* Left Column: File List */}
          <div className="w-full md:w-80 border-b md:border-b-0 md:border-r border-[#1b2533] bg-[#090d14] flex flex-col shrink-0">
            <div className="p-3 border-b border-[#1b2533] flex items-center justify-between text-xs font-mono text-zinc-400">
              <span>ARCHIVOS MODIFICADOS ({diffData.files.length})</span>
              <div className="flex items-center gap-2 text-[10px]">
                <span className="text-emerald-400 font-bold">+{diffData.total_additions}</span>
                <span className="text-red-400 font-bold">-{diffData.total_deletions}</span>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto custom-scroll p-2 space-y-1">
              {diffData.files.length === 0 ? (
                <div className="p-6 text-center text-zinc-500 text-xs font-mono space-y-2">
                  <CheckCircle2 className="w-6 h-6 text-emerald-500 mx-auto" />
                  <p>Árbol de trabajo 100% limpio.</p>
                  <p className="text-[10px] text-zinc-600">No hay cambios sin confirmar en el worktree.</p>
                </div>
              ) : (
                diffData.files.map((file, idx) => {
                  const isSelected = idx === selectedFileIdx
                  return (
                    <div
                      key={file.path}
                      onClick={() => setSelectedFileIdx(idx)}
                      className={`p-2.5 rounded-xl cursor-pointer transition flex items-center justify-between gap-2 text-xs font-mono ${
                        isSelected
                          ? 'bg-emerald-500/15 border border-emerald-500/40 text-white'
                          : 'hover:bg-zinc-900/60 border border-transparent text-zinc-300'
                      }`}
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        <FileCode className={`w-3.5 h-3.5 shrink-0 ${isSelected ? 'text-emerald-400' : 'text-zinc-500'}`} />
                        <span className="truncate text-[11px] font-semibold">{file.path}</span>
                      </div>
                      <div className="flex items-center gap-1.5 shrink-0 text-[10px]">
                        {file.additions > 0 && (
                          <span className="text-emerald-400 font-bold">+{file.additions}</span>
                        )}
                        {file.deletions > 0 && (
                          <span className="text-red-400 font-bold">-{file.deletions}</span>
                        )}
                      </div>
                    </div>
                  )
                })
              )}
            </div>
          </div>

          {/* Right Column: Code Diff View */}
          <div className="flex-1 flex flex-col bg-[#070a0e] overflow-hidden">
            {selectedFile ? (
              <>
                {/* File Action Bar */}
                <div className="px-4 py-2.5 border-b border-[#1b2533] bg-[#0a0f18] flex items-center justify-between shrink-0">
                  <div className="flex items-center gap-2 font-mono text-xs">
                    <span className="text-white font-bold">{selectedFile.path}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-zinc-800 text-zinc-300">
                      {selectedFile.status}
                    </span>
                  </div>

                  <button
                    type="button"
                    onClick={() => handleRevert(selectedFile.path)}
                    disabled={reverting}
                    className="px-3 py-1.5 rounded-xl bg-red-500/15 hover:bg-red-500/25 text-red-300 border border-red-500/30 text-xs font-mono font-bold flex items-center gap-1.5 transition cursor-pointer active:scale-95 disabled:opacity-50"
                  >
                    <RotateCcw className="w-3 h-3 text-red-400" />
                    <span>Revertir Archivo</span>
                  </button>
                </div>

                {/* Chunks Code Viewer */}
                <div className="flex-1 overflow-y-auto custom-scroll p-4 font-mono text-xs leading-relaxed space-y-4">
                  {selectedFile.chunks.length === 0 ? (
                    <div className="p-8 text-center text-zinc-500">
                      Archivo modificado pero sin diff disponible o binario.
                    </div>
                  ) : (
                    selectedFile.chunks.map((chunk, cIdx) => (
                      <div key={cIdx} className="rounded-xl border border-zinc-900 bg-black/70 overflow-hidden">
                        <div className="px-3 py-1 bg-zinc-900/90 text-cyan-400 text-[10px] font-bold border-b border-zinc-800">
                          {chunk.header}
                        </div>
                        <div className="divide-y divide-zinc-900/50">
                          {chunk.lines.map((line, lIdx) => {
                            const isAdd = line.type === 'add'
                            const isDel = line.type === 'del'
                            return (
                              <div
                                key={lIdx}
                                className={`flex items-start text-[11px] ${
                                  isAdd
                                    ? 'bg-emerald-950/40 text-emerald-300'
                                    : isDel
                                    ? 'bg-red-950/40 text-red-300 line-through opacity-85'
                                    : 'text-zinc-400'
                                }`}
                              >
                                <span className="w-10 px-2 py-0.5 select-none text-right text-zinc-600 text-[10px] shrink-0 font-mono">
                                  {line.old_num || ''}
                                </span>
                                <span className="w-10 px-2 py-0.5 select-none text-right text-zinc-600 text-[10px] shrink-0 font-mono border-r border-zinc-800/80">
                                  {line.new_num || ''}
                                </span>
                                <span className="w-6 px-1 py-0.5 select-none text-center font-bold shrink-0">
                                  {isAdd ? '+' : isDel ? '-' : ' '}
                                </span>
                                <span className="px-2 py-0.5 whitespace-pre-wrap break-all flex-1 font-mono">
                                  {line.text}
                                </span>
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-zinc-500 font-mono text-xs">
                Selecciona un archivo modificado de la lista para inspeccionar sus diffs.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
