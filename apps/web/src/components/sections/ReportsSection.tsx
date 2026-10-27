import React, { useState, useEffect } from 'react'
import {
  Database,
  Lock,
  CheckCircle2,
  RefreshCw,
  AlertCircle,
} from 'lucide-react'

export const ReportsSection: React.FC = () => {
  const [selectedTable, setSelectedTable] = useState<string>('runs')
  const [tableRows, setTableRows] = useState<any[]>([])
  const [dbStats, setDbStats] = useState<any>({ tables: {} })
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(
    null
  )
  const [contractsData, setContractsData] = useState<any>(null)
  const [checkpointing, setCheckpointing] = useState<boolean>(false)

  const loadData = async () => {
    try {
      const sRes = await fetch('/api/db/stats')
      const sData = await sRes.json()
      setDbStats(sData)
    } catch (e) {
      console.warn('Error loading db stats:', e)
    }

    try {
      const cRes = await fetch('/api/contracts')
      const cData = await cRes.json()
      setContractsData(cData)
    } catch (e) {
      console.warn('Error loading contracts:', e)
    }

    fetchTableRows(selectedTable)
  }

  const fetchTableRows = async (tableName: string) => {
    try {
      const res = await fetch(`/api/db/rows?table=${tableName}&limit=20`)
      const data = await res.json()
      if (data && data.rows) {
        setTableRows(data.rows)
      }
    } catch (e) {
      console.warn('Error loading table rows:', e)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  useEffect(() => {
    fetchTableRows(selectedTable)
  }, [selectedTable])

  const handleIntegrityCheck = async () => {
    try {
      const res = await fetch('/api/db/integrity')
      const data = await res.json()
      setFeedback({
        type: 'success',
        message: `Integridad de SQLite verificada: ${data.integrity || 'OK'} (${data.file_size_kb || 0} KB en disco).`,
      })
    } catch (e: any) {
      setFeedback({
        type: 'error',
        message: 'Error al verificar integridad: ' + e.message,
      })
    }
  }

  const handleWalCheckpoint = async () => {
    setCheckpointing(true)
    try {
      const res = await fetch('/api/db/checkpoint')
      const data = await res.json()
      setFeedback({
        type: 'success',
        message: data.message || 'Datos sincronizados a disco correctamente.',
      })
      loadData()
    } catch (e: any) {
      setFeedback({
        type: 'error',
        message: 'Error en sincronización de base de datos: ' + e.message,
      })
    } finally {
      setCheckpointing(false)
    }
  }

  const availableTables = Object.keys(
    dbStats.tables || { runs: 0, jobs: 0, approvals: 0, events: 0 }
  )

  return (
    <div className="space-y-6 max-w-6xl mx-auto text-left pb-12">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 sm:p-6 rounded-2xl bg-zinc-950 border border-zinc-800">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-lg font-bold text-white tracking-tight">
              Base de Datos Local (`sacl_ops.db`) y Reglas de Negocio
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
              {((dbStats.size_bytes || 0) / 1024).toFixed(1)} KB en disco
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Consulta los datos reales guardados en SQLite y las reglas de protección activas.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <button
            onClick={handleIntegrityCheck}
            className="px-3.5 py-2 rounded-xl bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-xs text-zinc-200 font-semibold flex items-center gap-1.5 transition cursor-pointer"
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Verificar Integridad</span>
          </button>

          <button
            onClick={handleWalCheckpoint}
            disabled={checkpointing}
            className="px-3.5 py-2 rounded-xl bg-white hover:bg-zinc-200 text-black font-bold text-xs flex items-center gap-1.5 transition cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${checkpointing ? 'animate-spin' : ''}`} />
            <span>{checkpointing ? 'Sincronizando...' : 'Guardar en Disco'}</span>
          </button>
        </div>
      </div>

      {feedback && (
        <div
          className={`p-4 rounded-xl border text-xs flex items-center justify-between gap-3 ${
            feedback.type === 'success'
              ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-200'
              : 'bg-red-950/40 border-red-500/40 text-red-200'
          }`}
        >
          <div className="flex items-center gap-2">
            {feedback.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            )}
            <span>{feedback.message}</span>
          </div>
          <button onClick={() => setFeedback(null)} className="text-xs underline cursor-pointer">
            Cerrar
          </button>
        </div>
      )}

      {/* Explorer de Tablas Reales */}
      <div className="p-5 sm:p-6 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-850 pb-4">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-zinc-200" />
            <h2 className="text-sm font-bold text-white">Tablas en SQLite (`sacl_ops.db`)</h2>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {availableTables.map((tbl) => (
              <button
                key={tbl}
                onClick={() => setSelectedTable(tbl)}
                className={`px-3 py-1.5 rounded-xl text-xs font-mono transition cursor-pointer ${
                  selectedTable === tbl
                    ? 'bg-white text-black font-bold'
                    : 'bg-zinc-900 text-zinc-400 border border-zinc-800 hover:text-white'
                }`}
              >
                {tbl} ({dbStats.tables?.[tbl] ?? 0})
              </button>
            ))}
          </div>
        </div>

        <div className="overflow-x-auto">
          {tableRows.length === 0 ? (
            <p className="text-xs text-zinc-500 py-6 text-center font-mono">
              La tabla "{selectedTable}" no tiene filas registradas en este momento.
            </p>
          ) : (
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-zinc-800 text-[10px] text-zinc-500 uppercase">
                  {Object.keys(tableRows[0] || {}).map((k) => (
                    <th key={k} className="pb-2.5 pr-4 font-semibold">
                      {k}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-850">
                {tableRows.map((row, i) => (
                  <tr key={i} className="hover:bg-zinc-900/40">
                    {Object.values(row).map((val: any, j) => (
                      <td
                        key={j}
                        className="py-2.5 pr-4 text-[11px] text-zinc-300 truncate max-w-[220px]"
                      >
                        {typeof val === 'object' ? JSON.stringify(val) : String(val ?? '')}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Contratos Protegidos */}
      {contractsData && (
        <div className="p-5 sm:p-6 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-4">
          <div className="flex items-center justify-between border-b border-zinc-850 pb-3">
            <div className="flex items-center gap-2">
              <Lock className="w-4 h-4 text-zinc-200" />
              <h2 className="text-sm font-bold text-white">
                Reglas y Contratos Protegidos en el Proyecto
              </h2>
            </div>
            <span className="text-xs font-mono text-emerald-400">Verificados con Pytest</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {contractsData.contracts?.map((c: any) => (
              <div
                key={c.id}
                className="p-4 rounded-xl bg-black border border-zinc-850 space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-white">{c.id}</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                    {c.status}
                  </span>
                </div>
                <h3 className="text-xs font-bold text-zinc-200">{c.title}</h3>
                <p className="text-[11px] text-zinc-400 leading-relaxed">{c.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
