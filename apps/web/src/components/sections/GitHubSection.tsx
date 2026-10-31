import React, { useState, useEffect } from 'react'

interface GitHubStatus {
  connected: boolean
  repo: string
  branch: string
  remote_url: string
  user: string
  is_clean: boolean
  ahead: number
  behind: number
  status_label: string
}

interface PullRequestItem {
  id: number
  number: number
  title: string
  state: string
  head: string
  base: string
  author: string
}

export const GitHubSection: React.FC = () => {
  const [status, setStatus] = useState<GitHubStatus | null>(null)
  const [prs, setPrs] = useState<PullRequestItem[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [syncing, setSyncing] = useState<boolean>(false)
  const [message, setMessage] = useState<string | null>(null)

  const fetchGitHubData = async () => {
    try {
      setLoading(true)
      const [resStatus, resPrs] = await Promise.all([
        fetch('/api/github/status'),
        fetch('/api/github/prs')
      ])

      const dataStatus = await resStatus.json()
      const dataPrs = await resPrs.json()

      setStatus(dataStatus)
      if (dataPrs && dataPrs.prs) {
        setPrs(dataPrs.prs)
      }
    } catch (err: any) {
      setMessage(`Error de consulta con el demonio: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchGitHubData()
  }, [])

  const handleSyncOrigin = async () => {
    try {
      setSyncing(true)
      setMessage(null)
      const res = await fetch('/api/github/sync', { method: 'POST' })
      const data = await res.json()
      if (res.ok) {
        setMessage('Sincronización remota completada exitosamente.')
        await fetchGitHubData()
      } else {
        setMessage(`Error al sincronizar: ${data.error || 'Respuesta fallida'}`)
      }
    } catch (err: any) {
      setMessage(`Fallo de red: ${err.message}`)
    } finally {
      setSyncing(false)
    }
  }

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6 text-left">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white uppercase tracking-wider font-sans">
            Panel de Gobernanza GitHub · Read-Only
          </h1>
          <p className="text-xs text-zinc-500 font-mono mt-1">
            Monitoreo soberano de ramas, estado de sincronización y pull requests sin almacenamiento de tokens.
          </p>
        </div>

        <button
          onClick={handleSyncOrigin}
          disabled={syncing || loading}
          className="px-3 py-1.5 bg-[#121212] border border-white/8 hover:border-white/20 rounded text-xs font-mono text-zinc-300 transition cursor-pointer flex items-center gap-2"
        >
          {syncing ? (
            <div className="w-3 h-3 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
          ) : (
            <span>⟳ Fetch Remoto</span>
          )}
        </button>
      </div>

      {message && (
        <div className="p-3 rounded bg-zinc-900 border border-white/10 text-xs font-mono text-zinc-300">
          ℹ {message}
        </div>
      )}

      {/* Grid de Estado */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Repo Card */}
        <div className="bg-[#0a0a0a] border border-white/8 rounded-lg p-4 space-y-2">
          <span className="text-[10px] font-mono uppercase text-zinc-500 tracking-wider">Repositorio Activo</span>
          <p className="text-sm font-semibold text-white truncate font-mono">
            {status?.repo || 'Cargando...'}
          </p>
          <div className="text-[10px] font-mono text-zinc-400 truncate">
            {status?.remote_url || 'URL Remota Segura'}
          </div>
        </div>

        {/* Branch Card */}
        <div className="bg-[#0a0a0a] border border-white/8 rounded-lg p-4 space-y-2">
          <span className="text-[10px] font-mono uppercase text-zinc-500 tracking-wider">Rama Base / Estado</span>
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-white font-mono">{status?.branch || 'main'}</span>
            <span className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border uppercase ${
              status?.is_clean ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' : 'text-amber-400 bg-amber-500/10 border-amber-500/20'
            }`}>
              {status?.is_clean ? 'Clean' : 'Porcelain Dirty'}
            </span>
          </div>
          <div className="text-[10px] font-mono text-zinc-500">
            Ahead: {status?.ahead ?? 0} | Behind: {status?.behind ?? 0}
          </div>
        </div>

        {/* Identity Card */}
        <div className="bg-[#0a0a0a] border border-white/8 rounded-lg p-4 space-y-2">
          <span className="text-[10px] font-mono uppercase text-zinc-500 tracking-wider">Autoridad Git (SSH/Host)</span>
          <p className="text-sm font-semibold text-white font-mono truncate">
            {status?.user || 'risejoaquin'}
          </p>
          <div className="text-[10px] font-mono text-emerald-400">
            ✓ Credenciales administradas por SO
          </div>
        </div>
      </div>

      {/* Pull Requests List */}
      <div className="bg-[#0a0a0a] border border-white/8 rounded-lg p-4 space-y-4">
        <div className="flex items-center justify-between border-b border-white/8 pb-3">
          <span className="text-xs font-mono uppercase text-zinc-400 font-semibold tracking-wider">
            Pull Requests Registrados ({prs.length})
          </span>
          <span className="text-[10px] font-mono text-zinc-600">Gate 5 Human Approval Required</span>
        </div>

        {prs.length === 0 ? (
          <div className="py-8 text-center text-xs font-mono text-zinc-600">
            No hay Pull Requests pendientes en la rama actual.
          </div>
        ) : (
          <div className="space-y-2">
            {prs.map((pr) => (
              <div
                key={pr.id || pr.number}
                className="p-3 bg-[#000000] border border-white/8 rounded flex items-center justify-between hover:border-white/20 transition"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-zinc-400 font-semibold">#{pr.number}</span>
                    <span className="text-xs text-white font-sans">{pr.title}</span>
                  </div>
                  <div className="text-[10px] font-mono text-zinc-500 mt-0.5">
                    {pr.head} ➔ {pr.base} · por {pr.author}
                  </div>
                </div>

                <span className="text-[9px] font-mono font-bold px-2 py-0.5 rounded border border-emerald-500/20 text-emerald-400 bg-emerald-500/10 uppercase">
                  {pr.state}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
