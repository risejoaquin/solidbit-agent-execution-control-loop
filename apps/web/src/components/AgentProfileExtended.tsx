import React, { useState } from 'react'
import type { AgentCardData } from './AgentCard'

interface AgentProfileExtendedProps {
  agent: AgentCardData | null
  isOpen: boolean
  onClose: () => void
}

export const AgentProfileExtended: React.FC<AgentProfileExtendedProps> = ({
  agent,
  isOpen,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState<'profile' | 'sdlc' | 'skins'>('profile')
  const [selectedSkin, setSelectedSkin] = useState<'strict' | 'fast' | 'debug'>('strict')

  if (!isOpen || !agent) return null

  const getPersonaDetails = () => {
    const name = agent.agentName.toLowerCase()
    if (name.includes('atlas')) {
      return {
        personality: 'Estratega determinista, enfocado en resolución topológica de grafos Kahn.',
        voiceTone: 'Imperativo y estructurado, prioriza el orden de las dependencias.',
        sdlcRole: 'Stage 1-3: Requerimientos, Mapeo de DAG y Particionamiento de Oleadas.',
        ownedPaths: ['src/sacl/scheduler', 'src/sacl/engine', 'campaigns/'],
        avatarBorder: 'border-blue-500/40 text-blue-400 bg-blue-500/10',
      }
    }
    if (name.includes('vega')) {
      return {
        personality: 'Arquitecta de datos implacable, garante de la persistencia ACID en SQLite WAL.',
        voiceTone: 'Analítica y defensiva, previene cualquier corrupción de contratos de datos.',
        sdlcRole: 'Stage 4: Mutación de Modelos, Schemas de Base de Datos y Repositorios.',
        ownedPaths: ['src/sacl/storage', 'migrations/', 'database/postgresql'],
        avatarBorder: 'border-purple-500/40 text-purple-400 bg-purple-500/10',
      }
    }
    if (name.includes('nova')) {
      return {
        personality: 'Certificadora de calidad con tolerancia cero al falso positivo.',
        voiceTone: 'Metódica y rigurosa, no permite avance sin cobertura del 100%.',
        sdlcRole: 'Stage 5-7: Suites de Pruebas Unitarias, Integración y Contratos OpenAPI.',
        ownedPaths: ['tests/', 'tests/unit', 'tests/integration', 'contracts/'],
        avatarBorder: 'border-emerald-500/40 text-emerald-400 bg-emerald-500/10',
      }
    }
    return {
      personality: 'Guardián constitucional, supervisor de las 9 prohibiciones de SolidBit.',
      voiceTone: 'Vigilante e inmutable, custodial absoluto de la compuerta Gate 5.',
      sdlcRole: 'Stage 8-9: Detección de Fugas, Verificación de Políticas y Gate 5 HMAC.',
      ownedPaths: ['src/sacl/security', 'src/sacl/policy', '.github/'],
      avatarBorder: 'border-amber-500/40 text-amber-400 bg-amber-500/10',
    }
  }

  const persona = getPersonaDetails()

  return (
    <div className="fixed inset-0 z-[140] bg-black/60 backdrop-blur-sm flex justify-end select-none">
      <div className="w-full max-w-md bg-[#0a0a0a] border-l border-white/8 h-full flex flex-col justify-between text-left p-6 shadow-2xl animate-in slide-in-from-right duration-200">
        {/* Top Header */}
        <div>
          <div className="flex items-center justify-between border-b border-white/8 pb-4">
            <div className="flex items-center gap-3 min-w-0">
              <div className={`w-10 h-10 rounded-lg border flex items-center justify-center font-bold font-mono text-sm shrink-0 ${persona.avatarBorder}`}>
                {agent.agentName.slice(0, 2).toUpperCase()}
              </div>
              <div className="min-w-0">
                <h2 className="text-sm font-bold text-white uppercase tracking-wider font-sans truncate">
                  {agent.agentName}
                </h2>
                <p className="text-[10px] text-zinc-500 font-mono truncate">{agent.role}</p>
              </div>
            </div>

            <button
              onClick={onClose}
              className="text-zinc-500 hover:text-white font-mono text-sm px-2 py-1 rounded transition cursor-pointer"
            >
              ✕
            </button>
          </div>

          {/* Tabs Selector */}
          <div className="flex rounded-lg border border-white/8 bg-[#000000] p-1 my-4 text-[10px] font-mono">
            {(['profile', 'sdlc', 'skins'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 py-1 rounded transition cursor-pointer uppercase font-semibold ${
                  activeTab === tab ? 'bg-[#1a1a1a] text-white' : 'text-zinc-500 hover:text-zinc-300'
                }`}
              >
                {tab === 'profile' ? 'Identidad' : tab === 'sdlc' ? 'Ciclo SDLC' : 'Skins / Perfil'}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="space-y-4 text-xs font-sans">
            {activeTab === 'profile' && (
              <div className="space-y-3.5">
                <div className="p-3 bg-[#000000] border border-white/8 rounded-lg space-y-1">
                  <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-wider">
                    Personalidad Operativa
                  </span>
                  <p className="text-xs text-zinc-300 font-sans leading-relaxed">
                    {persona.personality}
                  </p>
                </div>

                <div className="p-3 bg-[#000000] border border-white/8 rounded-lg space-y-1">
                  <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-wider">
                    Tono y Registro de Voz
                  </span>
                  <p className="text-xs text-zinc-300 font-sans leading-relaxed">
                    {persona.voiceTone}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
                  <div className="p-2.5 bg-[#000000] border border-white/8 rounded">
                    <span className="text-zinc-500 block">Proceso Actual</span>
                    <span className="text-emerald-400 font-bold truncate block">
                      {agent.currentProcess || 'En espera de despacho'}
                    </span>
                  </div>
                  <div className="p-2.5 bg-[#000000] border border-white/8 rounded">
                    <span className="text-zinc-500 block">PID / Daemon</span>
                    <span className="text-zinc-300 font-bold">
                      {agent.pid || '8765-DAEMON'}
                    </span>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'sdlc' && (
              <div className="space-y-3.5">
                <div className="p-3 bg-[#000000] border border-white/8 rounded-lg space-y-1">
                  <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-wider">
                    Asignación en Pipeline SDLC (9 Fases)
                  </span>
                  <p className="text-xs text-zinc-200 font-sans font-medium">
                    {persona.sdlcRole}
                  </p>
                </div>

                <div className="p-3 bg-[#000000] border border-white/8 rounded-lg space-y-2">
                  <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-wider block">
                    Rutas Propiedad del Agente (owned_paths)
                  </span>
                  <div className="space-y-1 font-mono text-[10px]">
                    {persona.ownedPaths.map((path) => (
                      <div key={path} className="flex items-center gap-1.5 text-zinc-400">
                        <span className="text-emerald-400">📁</span>
                        <span>{path}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="p-3 bg-[#000000] border border-white/8 rounded-lg space-y-1 text-[10px] font-mono">
                  <span className="text-zinc-500 block">Último Commit de Mutación</span>
                  <span className="text-zinc-300 font-bold">
                    {agent.commitSha ? `git:${agent.commitSha}` : 'Sincronizado con base'}
                  </span>
                </div>
              </div>
            )}

            {activeTab === 'skins' && (
              <div className="space-y-3">
                <span className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider block">
                  Perfil de Ejecución del Agente (Skin)
                </span>

                {(['strict', 'fast', 'debug'] as const).map((skin) => (
                  <div
                    key={skin}
                    onClick={() => setSelectedSkin(skin)}
                    className={`p-3 rounded-lg border transition cursor-pointer ${
                      selectedSkin === skin
                        ? 'bg-emerald-500/10 border-emerald-500/40 text-white'
                        : 'bg-[#000000] border-white/8 hover:border-white/20 text-zinc-400'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-xs uppercase font-mono">{skin} Mode</span>
                      {selectedSkin === skin && (
                        <span className="text-[9px] font-mono text-emerald-400">Activo</span>
                      )}
                    </div>
                    <p className="text-[11px] text-zinc-400 mt-1 font-sans">
                      {skin === 'strict'
                        ? 'Auditoría formal de contratos, cero tolerancias a regresiones.'
                        : skin === 'fast'
                        ? 'Pase ágil optimizado para refactorizaciones cosméticas de UI.'
                        : 'Registro exhaustivo con trazas completas de SQLite y eventos FSM.'}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-white/8 flex items-center justify-between text-[10px] font-mono text-zinc-500 shrink-0">
          <span>Identidad Gobernada por SolidBit EOP</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-[#121212] hover:bg-zinc-800 text-zinc-200 border border-white/8 rounded transition cursor-pointer"
          >
            Cerrar Panel
          </button>
        </div>
      </div>
    </div>
  )
}
