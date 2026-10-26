import React, { useState, useEffect } from 'react'
import {
  Database,
  FileCheck2,
  Table,
  ShieldAlert,
  CheckCircle2,
  Lock,
  Layers,
  Search,
} from 'lucide-react'

export const ReportsSection: React.FC = () => {
  const [selectedTable, setSelectedTable] = useState<string>('jobs')
  const [tableRows, setTableRows] = useState<any[]>([])
  const [stats, setStats] = useState<any>({ jobs: 2, runs: 26, events: 26, approvals: 1 })

  useEffect(() => {
    fetch('/api/db/stats')
      .then((r) => r.json())
      .then((d) => {
        if (d.tables) setStats(d.tables)
      })
      .catch(() => {})

    fetchTableRows(selectedTable)
  }, [selectedTable])

  const fetchTableRows = async (tableName: string) => {
    try {
      const res = await fetch(`/api/db/rows?table=${tableName}&limit=8`)
      const data = await res.json()
      if (data.rows) setTableRows(data.rows)
    } catch {
      // ignore
    }
  }

  const contracts = [
    {
      code: 'DR-INV-001',
      title: 'Inventario Atómico & Cero Sobreventa',
      status: 'VERIFICADO',
      enforcedBy: 'spec-enforcer',
      details: 'SellableUnit lock con verificación de colisiones en concurrencia masiva.',
    },
    {
      code: 'DR-PAY-001',
      title: 'Ledger Transaccional de Doble Partida',
      status: 'VERIFICADO',
      enforcedBy: 'worktree-coder-alpha',
      details: 'Partidas cuadradas, balance neutro, trazabilidad bancaria inmutable.',
    },
    {
      code: 'DR-IDEM-001',
      title: 'Llaves de Idempotencia en Endpoints HTTP',
      status: 'VERIFICADO',
      enforcedBy: 'worktree-coder-beta',
      details: 'Prevención de duplicidad de cobros y retries seguros.',
    },
    {
      code: 'DR-AUTH-001',
      title: 'Aislamiento Tenant & Tokens HMAC-SHA256',
      status: 'VERIFICADO',
      enforcedBy: 'hitl-sentinel',
      details: 'Firmas soberanas requeridas en compuertas de despliegue a producción.',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-3xl bg-[#0e141d] border border-[#1b2533]">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold text-white tracking-wide">
              Reportes de Auditoría & SQLite WAL Explorer (sacl_ops.db)
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              Modo WAL Lectura Consistente
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Inspección formal de contratos inmutables, tablas de estado y trazabilidad criptográfica
          </p>
        </div>
      </div>

      {/* Frozen Contracts Conformance Matrix */}
      <div className="p-6 rounded-3xl bg-[#0e141d] border border-[#1b2533] space-y-4 shadow-xl">
        <div className="flex items-center gap-2 text-sm font-bold text-white">
          <Lock className="w-4 h-4 text-emerald-400" />
          <span>Matriz de Cumplimiento de Contratos Inmutables (SolidBit SDLC)</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
          {contracts.map((c) => (
            <div
              key={c.code}
              className="p-4 rounded-2xl bg-[#090e16] border border-[#1b2533] space-y-2 hover:border-zinc-700 transition"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-emerald-400">{c.code}</span>
                <span className="flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <CheckCircle2 className="w-3 h-3" />
                  {c.status}
                </span>
              </div>
              <h3 className="text-xs font-bold text-white">{c.title}</h3>
              <p className="text-[11px] text-zinc-400">{c.details}</p>
              <div className="text-[10px] font-mono text-zinc-500 pt-1 border-t border-white/5">
                Auditado por: <span className="text-zinc-300">{c.enforcedBy}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* SQLite WAL Tables Explorer */}
      <div className="p-6 rounded-3xl bg-[#0e141d] border border-[#1b2533] space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1b2533] pb-4">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-blue-400" />
            <h2 className="text-sm font-bold text-white">
              Explorador de Tablas SQLite WAL (sacl_ops.db)
            </h2>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {['jobs', 'runs', 'events', 'approvals'].map((tbl) => (
              <button
                key={tbl}
                onClick={() => setSelectedTable(tbl)}
                className={`px-3 py-1.5 rounded-xl text-xs font-mono transition ${
                  selectedTable === tbl
                    ? 'bg-blue-600 text-white font-bold'
                    : 'bg-black/40 text-zinc-400 border border-[#1b2533] hover:text-white'
                }`}
              >
                {tbl} ({stats[tbl] || 0})
              </button>
            ))}
          </div>
        </div>

        {/* Table rows preview */}
        <div className="overflow-x-auto">
          {tableRows.length === 0 ? (
            <p className="text-xs text-zinc-500 py-4 font-mono">No hay registros disponibles en {selectedTable}</p>
          ) : (
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-[#1b2533] text-[10px] text-zinc-500">
                  {Object.keys(tableRows[0] || {}).map((k) => (
                    <th key={k} className="pb-2 pr-3 font-semibold uppercase">{k}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1b2533]/40">
                {tableRows.map((row, i) => (
                  <tr key={i} className="hover:bg-white/[0.02]">
                    {Object.values(row).map((val: any, j) => (
                      <td key={j} className="py-2.5 pr-3 text-[11px] text-zinc-300 truncate max-w-[200px]">
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
