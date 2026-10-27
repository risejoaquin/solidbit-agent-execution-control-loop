import React, { useState, useEffect } from 'react'
import {
  Cpu,
  Server,
  Database,
  Shield,
  ShoppingBag,
  Layout,
  CheckCircle2,
  Terminal,
  Activity,
  AlertTriangle,
  Play,
  RotateCcw,
  Sparkles,
} from 'lucide-react'

interface ConnectionItem {
  id: string
  name: string
  category: string
  status: string
  version?: string
  account_info?: string
  last_checked?: string
  error_message?: string
}

export const AgentsSection: React.FC = () => {
  const [connections, setConnections] = useState<ConnectionItem[]>([])
  const [selectedConn, setSelectedConn] = useState<ConnectionItem | null>(null)
  const [actionHistory, setActionHistory] = useState<any[]>([])
  const [testingId, setTestingId] = useState<string | null>(null)

  const loadData = async () => {
    try {
      const res = await fetch('/api/connections')
      const data = await res.json()
      if (data && data.connections) {
        setConnections(data.connections)
        if (!selectedConn && data.connections.length > 0) {
          setSelectedConn(data.connections[0])
        }
      }
    } catch (e) {
      console.warn('Error loading connections:', e)
    }

    try {
      const actRes = await fetch('/api/actions/history')
      const actData = await actRes.json()
      if (actData && actData.history) {
        setActionHistory(actData.history)
      }
    } catch (e) {
      console.warn('Error loading action history:', e)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleTestConnection = async (connId: string) => {
    setTestingId(connId)
    try {
      const res = await fetch('/api/connections/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ connection_id: connId }),
      })
      const data = await res.json()
      alert(`Resultado prueba ${connId}: ${data.status} - ${data.message || data.error || 'OK'}`)
      loadData()
    } catch (e: any) {
      alert('Error probando conexión: ' + e.message)
    } finally {
      setTestingId(null)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-3xl bg-zinc-950 border border-zinc-800">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold text-white tracking-wide">
              Agentes, Runtimes & Conexiones de Infraestructura
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-white/10 text-zinc-200 border border-emerald-500/30">
              {connections.length} Herramientas Conectadas
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Supervisión directa de CLIs locales (AGY, Git, GitHub, Railway, Supabase, Atlassian, Resend)
          </p>
        </div>

        <button
          onClick={loadData}
          className="px-3 py-1.5 rounded-xl bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-xs text-zinc-300 flex items-center gap-1.5 transition cursor-pointer"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Actualizar Estado</span>
        </button>
      </div>

      {/* Real Connections Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {connections.map((conn) => {
          const isSelected = selectedConn?.id === conn.id
          const isOk = conn.status === 'connected'
          return (
            <div
              key={conn.id}
              onClick={() => setSelectedConn(conn)}
              className={`p-4 rounded-3xl cursor-pointer transition-all border ${
                isSelected
                  ? 'bg-[#121a26] border-emerald-500/60 shadow-lg shadow-emerald-500/5'
                  : 'bg-zinc-950 border-zinc-800 hover:border-zinc-700'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="w-10 h-10 rounded-2xl flex items-center justify-center bg-zinc-900 text-zinc-300 border border-zinc-750">
                  {conn.id === 'agy' ? (
                    <Sparkles className="w-5 h-5 text-zinc-200" />
                  ) : conn.category === 'vcs' ? (
                    <Terminal className="w-5 h-5 text-zinc-300" />
                  ) : conn.category === 'cloud' ? (
                    <Server className="w-5 h-5 text-purple-400" />
                  ) : (
                    <Database className="w-5 h-5 text-zinc-200" />
                  )}
                </div>

                <span
                  className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${
                    isOk
                      ? 'bg-white/10 text-zinc-200 border border-emerald-500/30'
                      : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                  }`}
                >
                  {isOk ? 'CONECTADO' : 'PENDIENTE'}
                </span>
              </div>

              <div className="mt-3">
                <h3 className="text-xs font-bold text-white font-mono">{conn.name}</h3>
                <p className="text-[11px] text-zinc-400 truncate mt-0.5">
                  {conn.account_info || `Versión: ${conn.version || 'Local'}`}
                </p>
              </div>

              <div className="mt-3 pt-3 border-t border-zinc-800 flex items-center justify-between text-[10px] font-mono text-zinc-500">
                <span>Categoría: {conn.category}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleTestConnection(conn.id)
                  }}
                  disabled={testingId === conn.id}
                  className="text-zinc-200 hover:underline cursor-pointer"
                >
                  {testingId === conn.id ? 'Probando...' : 'Test CLI'}
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {/* Real Actions Executed Table */}
      <div className="p-6 rounded-3xl bg-zinc-950 border border-zinc-800 space-y-4 shadow-xl">
        <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-zinc-200" />
            <h2 className="text-sm font-bold text-white">Historial de Acciones de Agentes (/api/actions/history)</h2>
          </div>
          <span className="text-xs text-zinc-400 font-mono">{actionHistory.length} ejecuciones</span>
        </div>

        <div className="overflow-x-auto">
          {actionHistory.length === 0 ? (
            <p className="text-xs text-zinc-500 py-3 font-mono">No hay ejecuciones de acciones registradas aún.</p>
          ) : (
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-zinc-800 text-[10px] text-zinc-500">
                  <th className="pb-2">Execution ID</th>
                  <th className="pb-2">Acción</th>
                  <th className="pb-2">Duración</th>
                  <th className="pb-2">Exit Code</th>
                  <th className="pb-2 pr-2">Estado</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1b2533]/40">
                {actionHistory.map((act, i) => (
                  <tr key={act.execution_id || i} className="hover:bg-white/[0.02]">
                    <td className="py-2.5 font-bold text-zinc-300">{act.execution_id}</td>
                    <td className="py-2.5 text-white">{act.title || act.action_type}</td>
                    <td className="py-2.5 text-zinc-400">{act.duration_sec}s</td>
                    <td className="py-2.5 text-zinc-200">{act.exit_code}</td>
                    <td className="py-2.5 pr-2">
                      <span className="px-2 py-0.5 rounded-full text-[10px] bg-zinc-900 text-zinc-300 border border-zinc-750">
                        {act.status}
                      </span>
                    </td>
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
