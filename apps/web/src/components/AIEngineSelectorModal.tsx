import React, { useState, useEffect } from 'react'

export interface ModelInfo {
  id: string
  name: string
  provider: string
  tier: string
  badge: string
  description: string
  context_window: string
  default_temp: number
  is_active?: boolean
}

interface AIEngineSelectorModalProps {
  isOpen: boolean
  onClose: () => void
  onSelectModel?: (modelId: string) => void
}

export const AIEngineSelectorModal: React.FC<AIEngineSelectorModalProps> = ({
  isOpen,
  onClose,
  onSelectModel,
}) => {
  const [models, setModels] = useState<ModelInfo[]>([])
  const [activeModelId, setActiveModelId] = useState<string>('claude-3-7-sonnet')
  const [loading, setLoading] = useState<boolean>(true)
  const [vramUsagePct, setVramUsagePct] = useState<number>(34)
  const [cpuUsagePct, setCpuUsagePct] = useState<number>(18)
  const [switching, setSwitching] = useState<boolean>(false)

  useEffect(() => {
    if (!isOpen) return
    const fetchModels = async () => {
      try {
        setLoading(true)
        const res = await fetch('/api/models/config')
        const data = await res.json()
        if (data.available_models) {
          setModels(data.available_models)
        }
        if (data.active_model?.id) {
          setActiveModelId(data.active_model.id)
        }
      } catch (e) {
        console.error('Error fetching models config:', e)
      } finally {
        setLoading(false)
      }
    }
    fetchModels()
  }, [isOpen])

  if (!isOpen) return null

  const handleSelect = async (modelId: string) => {
    setSwitching(true)
    try {
      await fetch('/api/model/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model_id: modelId }),
      })
      setActiveModelId(modelId)
      if (onSelectModel) onSelectModel(modelId)
    } catch (e) {
      console.error('Error switching AI model:', e)
    } finally {
      setSwitching(false)
    }
  }

  return (
    <div className="fixed inset-0 z-[150] bg-black/90 backdrop-blur-sm flex items-center justify-center p-4 select-none">
      <div className="w-full max-w-3xl bg-[#0a0a0a] border border-white/8 rounded-xl p-6 text-left shadow-2xl flex flex-col max-h-[90vh]">
        {/* Header con métricas de hardware */}
        <div className="flex items-center justify-between border-b border-white/8 pb-4 shrink-0">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <h2 className="text-sm font-bold text-white uppercase tracking-wider font-sans">
                Desglose de Motores IA · antigravity Daemon
              </h2>
            </div>
            <p className="text-[11px] text-zinc-500 font-mono mt-0.5">
              Mapeo de recursos de inferencia, capacidad de contexto y asignación de hardware.
            </p>
          </div>

          <button
            onClick={onClose}
            className="text-zinc-500 hover:text-white font-mono text-sm px-2 py-1 rounded transition cursor-pointer"
          >
            ✕
          </button>
        </div>

        {/* Barra de Telemetría de Recursos Físicos (Boceto: % Disp y Cantidad de Modelos) */}
        <div className="grid grid-cols-3 gap-3 my-4 shrink-0">
          <div className="p-3 bg-[#000000] border border-white/8 rounded-lg space-y-1">
            <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-wider">
              Modelos Registrados
            </span>
            <div className="text-base font-bold font-mono text-white">
              {models.length || 9} Motores
            </div>
          </div>

          <div className="p-3 bg-[#000000] border border-white/8 rounded-lg space-y-1">
            <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-wider">
              % Disp VRAM (Host)
            </span>
            <div className="flex items-center justify-between">
              <span className="text-base font-bold font-mono text-emerald-400">
                {100 - vramUsagePct}%
              </span>
              <span className="text-[9px] font-mono text-zinc-500">Uso: {vramUsagePct}%</span>
            </div>
          </div>

          <div className="p-3 bg-[#000000] border border-white/8 rounded-lg space-y-1">
            <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-wider">
              % Disp CPU (Daemon)
            </span>
            <div className="flex items-center justify-between">
              <span className="text-base font-bold font-mono text-blue-400">
                {100 - cpuUsagePct}%
              </span>
              <span className="text-[9px] font-mono text-zinc-500">Uso: {cpuUsagePct}%</span>
            </div>
          </div>
        </div>

        {/* Lista de Motores de IA */}
        <div className="flex-1 overflow-y-auto space-y-2.5 custom-scroll pr-1">
          {loading ? (
            <div className="py-12 text-center text-xs font-mono text-zinc-500">
              Consultando estado de hardware y modelos...
            </div>
          ) : (
            models.map((m) => {
              const isActive = activeModelId === m.id
              return (
                <div
                  key={m.id}
                  onClick={() => handleSelect(m.id)}
                  className={`p-3.5 rounded-lg border transition cursor-pointer flex items-center justify-between gap-4 ${
                    isActive
                      ? 'bg-emerald-500/5 border-emerald-500/40 text-white'
                      : 'bg-[#000000] border-white/8 hover:border-white/20 text-zinc-300'
                  }`}
                >
                  <div className="space-y-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold font-sans">{m.name}</span>
                      <span
                        className={`text-[9px] font-mono font-bold px-1.5 py-0.2 rounded border uppercase ${
                          isActive
                            ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
                            : 'text-zinc-500 bg-zinc-900 border-zinc-800'
                        }`}
                      >
                        {m.badge || m.provider}
                      </span>
                      {isActive && (
                        <span className="text-[9px] font-mono text-emerald-400 font-semibold">
                          ● Activo
                        </span>
                      )}
                    </div>

                    <p className="text-[11px] text-zinc-400 font-sans line-clamp-1">
                      {m.description}
                    </p>

                    <div className="flex items-center gap-3 text-[9px] font-mono text-zinc-500 pt-0.5">
                      <span>Proveedor: {m.provider}</span>
                      <span>Contexto: {m.context_window}</span>
                      <span>Temp: {m.default_temp}</span>
                    </div>
                  </div>

                  <div className="shrink-0 text-right">
                    <button
                      type="button"
                      disabled={isActive || switching}
                      className={`px-3 py-1.5 rounded text-xs font-mono transition cursor-pointer ${
                        isActive
                          ? 'bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30 cursor-default'
                          : 'bg-[#121212] hover:bg-[#1a1a1a] text-zinc-300 border border-white/10'
                      }`}
                    >
                      {isActive ? 'Seleccionado' : 'Asignar'}
                    </button>
                  </div>
                </div>
              )
            })
          )}
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-white/8 mt-4 flex items-center justify-between text-[10px] font-mono text-zinc-500 shrink-0">
          <span>Inferencia Local & Cloud Desacoplada (antigravity Engine)</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-[#121212] hover:bg-zinc-800 text-zinc-200 border border-white/8 rounded font-mono text-xs transition cursor-pointer"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  )
}
