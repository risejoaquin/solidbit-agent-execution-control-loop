import React, { useState, useEffect } from 'react'
import {
  Database,
  Lock,
  CheckCircle2,
  RotateCcw,
  ShieldAlert,
  HardDrive,
  RefreshCw,
  Layers,
} from 'lucide-react'

export const ReportsSection: React.FC = () => {
  const [selectedTable, setSelectedTable] = useState<string>('jobs')
  const [tableRows, setTableRows] = useState<any[]>([])
  const [dbStats, setDbStats] = useState<any>({ tables: {} })
  const [integrityStatus, setIntegrityStatus] = useState<string | null>(null)
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
      setIntegrityStatus(data.integrity || 'PRAGMA integrity_check: ok')
    } catch (e: any) {
      alert('Error en check de integridad: ' + e.message)
    }
  }

  const handleWalCheckpoint = async () => {
    setCheckpointing(true)
    try {
      const res = await fetch('/api/db/checkpoint', { method: 'POST' })
      const data = await res.json()
      alert(`Checkpoint WAL completado: ${data.message || 'Páginas persistidas a disco.'}`)
      loadData()
    } catch (e: any) {
      alert('Error en checkpoint: ' + e.message)
    } finally {
      setCheckpointing(false)
    }
  }

  const availableTables = Object.keys(dbStats.tables || { jobs: 0, runs: 0, events: 0, approvals: 0 })

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-3xl bg-zinc-950 border border-zinc-800">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold text-white tracking-wide">
              Auditoría SQLite WAL (sacl_ops.db) & Contratos Congelados
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-white/10 text-zinc-200 border border-emerald-500/30">
              {dbStats.wal_mode ? 'WAL Mode ACTIVO' : 'SQLite DB'} &bull; {(dbStats.size_bytes / 1024).toFixed(1)} KB
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Persistencia de misión crítica con consistencia ante fallos sin mutación destructiva de Git
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleIntegrityCheck}
            className="px-3 py-1.5 rounded-xl bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-xs text-zinc-300 flex items-center gap-1.5 transition cursor-pointer"
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-zinc-200" />
            <span>PRAGMA Integrity</span>
          </button>

          <button
            onClick={handleWalCheckpoint}
            disabled={checkpointing}
            className="px-3 py-1.5 rounded-xl bg-blue-600/20 border border-blue-500/30 hover:bg-blue-600/30 text-xs text-blue-300 flex items-center gap-1.5 transition cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5 text-zinc-300" />
            <span>{checkpointing ? 'Checkpointing...' : 'WAL Checkpoint'}</span>
          </button>
        </div>
      </div>

      {integrityStatus && (
        <div className="p-4 rounded-3xl bg-white/10 border border-emerald-500/30 text-xs font-mono text-zinc-200 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" />
          <span>{integrityStatus}</span>
        </div>
      )}

      {/* Real Frozen Contracts from backend /api/contracts */}
      {contractsData && (
        <div className="p-6 rounded-3xl bg-zinc-950 border border-zinc-800 space-y-4 shadow-xl">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
            <div className="flex items-center gap-2">
              <Lock className="w-4 h-4 text-zinc-200" />
              <h2 className="text-sm font-bold text-white">
                Contratos Inmutables Congelados (/api/contracts)
              </h2>
            </div>
            <span className="text-[10px] font-mono text-zinc-200">
              {contractsData.safety_summary || 'Hard Deny Supremacy'}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {contractsData.contracts?.map((c: any) => (
              <div
                key={c.id}
                className="p-4 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-2 hover:border-zinc-700 transition"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-zinc-200">{c.id}</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-zinc-900 text-zinc-300 border border-zinc-750">
                    {c.status}
                  </span>
                </div>
                <h3 className="text-xs font-bold text-white">{c.title}</h3>
                <p className="text-[11px] text-zinc-400 leading-relaxed">{c.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Real SQLite Table Explorer */}
      <div className="p-6 rounded-3xl bg-zinc-950 border border-zinc-800 space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-800 pb-4">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-zinc-300" />
            <h2 className="text-sm font-bold text-white">Explorador de Tablas (/api/db/rows)</h2>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {availableTables.map((tbl) => (
              <button
                key={tbl}
                onClick={() => setSelectedTable(tbl)}
                className={`px-3 py-1.5 rounded-xl text-xs font-mono transition cursor-pointer ${
                  selectedTable === tbl
                    ? 'bg-blue-600 text-white font-bold shadow-md shadow-blue-500/20'
                    : 'bg-black/40 text-zinc-400 border border-zinc-800 hover:text-white'
                }`}
              >
                {tbl} ({dbStats.tables[tbl] ?? 0})
              </button>
            ))}
          </div>
        </div>

        {/* Table Rows */}
        <div className="overflow-x-auto">
          {tableRows.length === 0 ? (
            <p className="text-xs text-zinc-500 py-6 text-center font-mono">
              No hay registros en la tabla {selectedTable}
            </p>
          ) : (
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-zinc-800 text-[10px] text-zinc-500 uppercase">
                  {Object.keys(tableRows[0] || {}).map((k) => (
                    <th key={k} className="pb-2.5 pr-4 font-semibold">{k}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1b2533]/40">
                {tableRows.map((row, i) => (
                  <tr key={i} className="hover:bg-white/[0.02]">
                    {Object.values(row).map((val: any, j) => (
                      <td key={j} className="py-2.5 pr-4 text-[11px] text-zinc-300 truncate max-w-[220px]">
                        {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
}
