import React, { useState, useEffect } from 'react'
import {
  Database,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Clock,
  GitCommit,
  Bot,
  Search,
} from 'lucide-react'

interface DbEventRow {
  event_id: number
  job_id: string | null
  run_id: string | null
  node_id: string | null
  agent_id: string | null
  event_type: string
  severity: string
  payload_json: string
  created_at: string
}

export const ReportsSection: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'events' | 'runs'>('events')
  const [events, setEvents] = useState<DbEventRow[]>([])
  const [runs, setRuns] = useState<any[]>([])
  const [loading, setLoading] = useState<boolean>(false)
  const [searchTerm, setSearchTerm] = useState<string>('')
  const [dbStats, setDbStats] = useState<any>(null)

  const loadData = async () => {
    setLoading(true)
    try {
      // 1. Cargar eventos de sacl_ops.db
      const evRes = await fetch('/api/events', {
        headers: { Accept: 'application/json' },
      })
      if (evRes.ok) {
        const evData = await evRes.json()
        if (evData && evData.rows) {
          setEvents(evData.rows)
        }
      }

      // 2. Cargar runs de sacl_ops.db
      const rRes = await fetch('/api/runs', {
        headers: { Accept: 'application/json' },
      })
      if (rRes.ok) {
        const rData = await rRes.json()
        if (rData && rData.rows) {
          setRuns(rData.rows)
        }
      }

      // 3. Cargar estadísticas generales
      const stRes = await fetch('/api/db/stats')
      if (stRes.ok) {
        const stData = await stRes.json()
        setDbStats(stData)
      }
    } catch (err) {
      console.warn('Error cargando base de datos:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  // Extraer commit SHA o datos de payload JSON de forma segura
  const parsePayload = (jsonStr: string) => {
    try {
      return JSON.parse(jsonStr)
    } catch {
      return {}
    }
  }

  // Filtrado de búsqueda
  const filteredEvents = events.filter((ev) => {
    if (!searchTerm.trim()) return true
    const term = searchTerm.toLowerCase()
    return (
      String(ev.event_id).includes(term) ||
      (ev.agent_id && ev.agent_id.toLowerCase().includes(term)) ||
      ev.event_type.toLowerCase().includes(term) ||
      ev.severity.toLowerCase().includes(term) ||
      (ev.job_id && ev.job_id.toLowerCase().includes(term))
    )
  })

  return (
    <div className="space-y-6 max-w-6xl mx-auto text-left pb-12 animate-fade-in">
      {/* 1. Header Principal */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 sm:p-6 rounded-3xl bg-[#0C0C0E] border border-white/5 shadow-xl">
        <div className="space-y-1">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-emerald-400">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-extrabold text-white tracking-tight">
                  Auditoría de Base de Datos Real
                </h1>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                  sacl_ops.db (SQLite WAL)
                </span>
              </div>
              <p className="text-xs text-zinc-400">
                Registro criptográfico inmutable de transacciones, ejecuciones y eventos de agentes en disco.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2.5 self-start sm:self-auto">
          <button
            type="button"
            onClick={loadData}
            disabled={loading}
            className="px-4 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-750 text-xs font-semibold text-zinc-200 flex items-center gap-1.5 transition cursor-pointer disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-emerald-400' : 'text-zinc-400'}`} />
            <span>Actualizar</span>
          </button>
        </div>
      </div>

      {/* 2. Selector de Pestañas (Eventos vs Runs) & Buscador */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center p-1 rounded-2xl bg-[#0C0C0E] border border-white/5">
          <button
            type="button"
            onClick={() => setActiveTab('events')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition cursor-pointer flex items-center gap-2 ${
              activeTab === 'events' ? 'bg-zinc-800 text-white shadow-sm' : 'text-zinc-400 hover:text-white'
            }`}
          >
            <span>Eventos Registrados</span>
            <span className="px-1.5 py-0.2 rounded-full text-[10px] font-mono bg-black/60 text-emerald-400">
              {events.length}
            </span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('runs')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition cursor-pointer flex items-center gap-2 ${
              activeTab === 'runs' ? 'bg-zinc-800 text-white shadow-sm' : 'text-zinc-400 hover:text-white'
            }`}
          >
            <span>Corridas (Runs)</span>
            <span className="px-1.5 py-0.2 rounded-full text-[10px] font-mono bg-black/60 text-zinc-400">
              {runs.length}
            </span>
          </button>
        </div>

        {/* Buscador reactivo */}
        {activeTab === 'events' && (
          <div className="relative w-full sm:w-72">
            <Search className="w-3.5 h-3.5 text-zinc-500 absolute left-3.5 top-3" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Buscar por ID, Agente o Evento..."
              className="w-full bg-[#0C0C0E] border border-zinc-800 focus:border-white rounded-xl pl-9 pr-3.5 py-2 text-xs text-white placeholder-zinc-500 font-mono focus:outline-none"
            />
          </div>
        )}
      </div>

      {/* 3. Tabla Reactiva de Datos */}
      <div className="p-5 rounded-3xl bg-[#0C0C0E] border border-white/5 shadow-2xl space-y-4">
        {activeTab === 'events' ? (
          filteredEvents.length === 0 ? (
            <div className="py-12 text-center space-y-2">
              <Database className="w-8 h-8 text-zinc-600 mx-auto" />
              <p className="text-sm font-bold text-zinc-300">0 transacciones en sacl_ops.db</p>
              <p className="text-xs text-zinc-500 max-w-sm mx-auto">
                No se encontraron eventos registrados en la tabla 'events' de la base de datos local SQLite WAL.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-white/5 text-[10px] text-zinc-500 uppercase tracking-wider">
                    <th className="pb-3 pr-4 font-bold">ID</th>
                    <th className="pb-3 pr-4 font-bold">Timestamp</th>
                    <th className="pb-3 pr-4 font-bold">Agente</th>
                    <th className="pb-3 pr-4 font-bold">Tipo de Evento / Fase</th>
                    <th className="pb-3 pr-4 font-bold">Estado</th>
                    <th className="pb-3 pr-4 font-bold">Commit SHA</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {filteredEvents.map((ev) => {
                    const payload = parsePayload(ev.payload_json)
                    const commitSha = payload.commit_sha || payload.commit || '—'
                    const statusStr = (payload.status || ev.severity || 'INFO').toUpperCase()
                    const isPass = statusStr === 'COMPLETED' || statusStr === 'PASS' || statusStr === 'OK' || statusStr === 'INFO'
                    const isBlocked = statusStr === 'BLOCKED' || statusStr === 'WAITING' || statusStr === 'WARNING'
                    const isError = statusStr === 'ERROR' || statusStr === 'FAILED' || statusStr === 'FAIL'

                    return (
                      <tr key={ev.event_id} className="hover:bg-zinc-900/50 transition">
                        {/* ID */}
                        <td className="py-3 pr-4 text-zinc-400 font-bold">#{ev.event_id}</td>

                        {/* Timestamp */}
                        <td className="py-3 pr-4 text-zinc-300">
                          <span className="flex items-center gap-1.5 text-[11px]">
                            <Clock className="w-3 h-3 text-zinc-500 shrink-0" />
                            {ev.created_at ? new Date(ev.created_at).toLocaleTimeString() : '—'}
                          </span>
                        </td>

                        {/* Agente */}
                        <td className="py-3 pr-4 text-white font-bold">
                          <span className="flex items-center gap-1.5">
                            <Bot className="w-3.5 h-3.5 text-sky-400 shrink-0" />
                            {ev.agent_id || 'SYSTEM'}
                          </span>
                        </td>

                        {/* Tipo de Evento / Fase */}
                        <td className="py-3 pr-4 text-zinc-200">
                          <span className="px-2 py-0.5 rounded-md bg-zinc-900 border border-zinc-800 text-[10px] font-mono text-zinc-300">
                            {ev.event_type}
                          </span>
                        </td>

                        {/* Estado (PASS / FAIL / BLOCKED) */}
                        <td className="py-3 pr-4">
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-bold border inline-flex items-center gap-1 ${
                              isPass
                                ? 'bg-emerald-950/40 text-emerald-300 border-emerald-500/30'
                                : isBlocked
                                ? 'bg-amber-950/40 text-amber-300 border-amber-500/30'
                                : isError
                                ? 'bg-rose-950/40 text-rose-300 border-rose-500/30'
                                : 'bg-zinc-900 text-zinc-400 border-zinc-800'
                            }`}
                          >
                            {isPass ? (
                              <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                            ) : isBlocked ? (
                              <AlertTriangle className="w-3 h-3 text-amber-400" />
                            ) : isError ? (
                              <XCircle className="w-3 h-3 text-rose-400" />
                            ) : null}
                            <span>{statusStr}</span>
                          </span>
                        </td>

                        {/* Commit SHA */}
                        <td className="py-3 pr-4">
                          {commitSha !== '—' ? (
                            <span className="px-2 py-0.5 rounded bg-sky-950/40 border border-sky-500/20 text-sky-400 text-[10px] font-bold inline-flex items-center gap-1">
                              <GitCommit className="w-3 h-3 text-sky-400" />
                              {commitSha.substring(0, 7)}
                            </span>
                          ) : (
                            <span className="text-zinc-600">—</span>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )
        ) : (
          /* Pestaña Runs */
          runs.length === 0 ? (
            <div className="py-12 text-center space-y-2">
              <Database className="w-8 h-8 text-zinc-600 mx-auto" />
              <p className="text-sm font-bold text-zinc-300">0 transacciones en sacl_ops.db</p>
              <p className="text-xs text-zinc-500 max-w-sm mx-auto">
                No hay registros de corridas activas en la tabla 'runs' actualmente.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-white/5 text-[10px] text-zinc-500 uppercase tracking-wider">
                    <th className="pb-3 pr-4 font-bold">Run ID</th>
                    <th className="pb-3 pr-4 font-bold">Proyecto</th>
                    <th className="pb-3 pr-4 font-bold">Modo</th>
                    <th className="pb-3 pr-4 font-bold">Estado</th>
                    <th className="pb-3 pr-4 font-bold">Inicio</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {runs.map((r) => (
                    <tr key={r.run_id} className="hover:bg-zinc-900/50 transition">
                      <td className="py-3 pr-4 text-sky-400 font-bold">{r.run_id}</td>
                      <td className="py-3 pr-4 text-white font-medium">{r.project || r.project_id || '—'}</td>
                      <td className="py-3 pr-4 text-zinc-300">{r.mode || 'waves'}</td>
                      <td className="py-3 pr-4">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-zinc-900 border border-zinc-750 text-zinc-200">
                          {r.status || 'READY'}
                        </span>
                      </td>
                      <td className="py-3 pr-4 text-zinc-400">{r.started_at ? new Date(r.started_at).toLocaleTimeString() : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        )}
      </div>
    </div>
  )
}
