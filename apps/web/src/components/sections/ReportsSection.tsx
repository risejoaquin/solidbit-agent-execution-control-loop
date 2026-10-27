import React, { useState, useEffect } from 'react'
import {
  Database,
  Lock,
  CheckCircle2,
  RefreshCw,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Terminal,
} from 'lucide-react'

const FRIENDLY_TABLE_LABELS: Record<string, string> = {
  runs: 'Sprints Ejecutados',
  jobs: 'Tareas Registradas',
  approvals: 'Autorizaciones Firmadas',
  events: 'Eventos del Sistema',
}

export const ReportsSection: React.FC = () => {
  const [selectedTable, setSelectedTable] = useState<string>('runs')
  const [tableRows, setTableRows] = useState<any[]>([])
  const [dbStats, setDbStats] = useState<any>({ tables: {} })
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(
    null
  )
  const [contractsData, setContractsData] = useState<any>(null)
  const [checkpointing, setCheckpointing] = useState<boolean>(false)
  const [showRawDbInspector, setShowRawDbInspector] = useState<boolean>(false)

  const loadData = async () => {
    try {
      const sRes = await fetch('/api/db/stats')
      const sData = await sRes.json()
      setDbStats(sData)
    } catch (e) {
      console.warn('Error loading activity stats:', e)
    }

    try {
      const cRes = await fetch('/api/contracts')
      const cData = await cRes.json()
      setContractsData(cData)
    } catch (e) {
      console.warn('Error loading business rules:', e)
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
        message: `Integridad del registro verificada correctamente (${data.file_size_kb || 0} KB respaldados).`,
      })
    } catch (e: any) {
      setFeedback({
        type: 'error',
        message: 'No se pudo verificar el registro: ' + e.message,
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
        message: data.message || 'Respaldo local sincronizado en disco correctamente.',
      })
      loadData()
    } catch (e: any) {
      setFeedback({
        type: 'error',
        message: 'Error al respaldar en disco: ' + e.message,
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
      {/* 1. Header Bar (Capa 1: Lenguaje de negocio claro + 1 Acción Primaria) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 sm:p-6 rounded-3xl bg-zinc-950 border border-zinc-850">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-lg font-bold text-white tracking-tight">
              Registro de Actividad y Reglas de Protección
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
              Respaldo Activo ({((dbStats.size_bytes || 0) / 1024).toFixed(1)} KB)
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Consulta las garantías de negocio protegidas en tu proyecto y el historial de operaciones guardadas.
          </p>
        </div>

        <div className="flex items-center gap-2.5 self-start sm:self-auto">
          <button
            type="button"
            onClick={handleIntegrityCheck}
            className="px-3.5 py-2 rounded-xl bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-xs text-zinc-200 font-semibold flex items-center gap-1.5 transition cursor-pointer"
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Comprobar Integridad</span>
          </button>

          {/* SINGLE Primary Action Token in ReportsSection (Hick's Law) */}
          <button
            type="button"
            onClick={handleWalCheckpoint}
            disabled={checkpointing}
            className="px-4 py-2 rounded-xl bg-white hover:bg-zinc-200 text-black font-extrabold text-xs flex items-center gap-1.5 transition cursor-pointer shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-black ${checkpointing ? 'animate-spin' : ''}`} />
            <span>{checkpointing ? 'Respaldando...' : 'Respaldar Registro Ahora'}</span>
          </button>
        </div>
      </div>

      {feedback && (
        <div
          className={`p-4 rounded-2xl border text-xs flex items-center justify-between gap-3 ${
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
          <button
            type="button"
            onClick={() => setFeedback(null)}
            className="text-xs underline cursor-pointer"
          >
            Cerrar
          </button>
        </div>
      )}

      {/* 2. Capa 1: Reglas de Negocio Protegidas */}
      {contractsData && (
        <div className="p-5 sm:p-6 rounded-3xl bg-zinc-950 border border-zinc-850 space-y-4">
          <div className="flex items-center justify-between border-b border-zinc-850 pb-3">
            <div className="flex items-center gap-2">
              <Lock className="w-4 h-4 text-zinc-200" />
              <h2 className="text-sm font-bold text-white">
                Garantías y Reglas de Negocio Protegidas
              </h2>
            </div>
            <span className="text-xs text-emerald-400 font-semibold">
              Verificadas Automáticamente
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
            {contractsData.contracts?.map((c: any) => (
              <div
                key={c.id}
                className="p-4 rounded-2xl bg-black border border-zinc-850 space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white">{c.title}</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                    PROTEGIDO
                  </span>
                </div>
                <p className="text-xs text-zinc-400 leading-relaxed">{c.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 3. Resumen de Actividad en Capa 1 */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {availableTables.map((tbl) => (
          <div
            key={tbl}
            className="p-4 rounded-2xl bg-zinc-950 border border-zinc-850 space-y-1"
          >
            <span className="text-xs text-zinc-400 block">
              {FRIENDLY_TABLE_LABELS[tbl] || tbl}
            </span>
            <span className="text-xl font-extrabold text-white font-mono">
              {dbStats.tables?.[tbl] ?? 0}
            </span>
          </div>
        ))}
      </div>

      {/* 4. Capa 2 (Divulgación Progresiva): Inspector Técnico de Tablas */}
      <div className="rounded-3xl bg-zinc-950 border border-zinc-850 overflow-hidden">
        <button
          type="button"
          onClick={() => setShowRawDbInspector(!showRawDbInspector)}
          className="w-full p-5 flex items-center justify-between hover:bg-zinc-900/40 transition cursor-pointer text-left"
        >
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-300">
              <Terminal className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-xs font-bold text-white">
                Inspección Técnica: Explorador de Registros Internos
              </h3>
              <p className="text-[11px] text-zinc-400 mt-0.5">
                Consulta las tablas detalladas almacenadas en el motor de persistencia local.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1.5 text-xs font-mono text-zinc-400">
            <span>{showRawDbInspector ? 'Ocultar' : 'Desplegar'}</span>
            {showRawDbInspector ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </div>
        </button>

        {showRawDbInspector && (
          <div className="p-5 pt-0 border-t border-zinc-900 space-y-4 mt-4 animate-fade-in">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-zinc-300" />
                <span className="text-xs font-bold text-zinc-200">Seleccionar colección:</span>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                {availableTables.map((tbl) => (
                  <button
                    key={tbl}
                    type="button"
                    onClick={() => setSelectedTable(tbl)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer ${
                      selectedTable === tbl
                        ? 'bg-zinc-800 text-white border border-zinc-600'
                        : 'bg-zinc-900 text-zinc-400 border border-zinc-850 hover:text-white'
                    }`}
                  >
                    {FRIENDLY_TABLE_LABELS[tbl] || tbl} ({dbStats.tables?.[tbl] ?? 0})
                  </button>
                ))}
              </div>
            </div>

            <div className="overflow-x-auto">
              {tableRows.length === 0 ? (
                <p className="text-xs text-zinc-500 py-6 text-center">
                  Esta colección no tiene registros en este momento.
                </p>
              ) : (
                <table className="w-full text-left text-xs font-mono">
                  <thead>
                    <tr className="border-b border-zinc-850 text-[10px] text-zinc-500 uppercase">
                      {Object.keys(tableRows[0] || {}).map((k) => (
                        <th key={k} className="pb-2.5 pr-4 font-semibold">
                          {k}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-900">
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
        )}
      </div>
    </div>
  )
}
