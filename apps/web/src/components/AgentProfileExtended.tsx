import React, { useState } from 'react'
import type { AgentCardData } from './AgentCard'

interface AgentProfileExtendedProps {
  agent: AgentCardData | null
  isOpen: boolean
  onClose: () => void
  onSkinChange?: (agentName: string, skinKey: string) => void
}

export const AgentProfileExtended: React.FC<AgentProfileExtendedProps> = ({
  agent,
  isOpen,
  onClose,
  onSkinChange,
}) => {
  const [activeTab, setActiveTab] = useState<'profile' | 'sdlc' | 'skins'>('profile')
  const [selectedSkin, setSelectedSkin] = useState<'bomberman_idle' | 'bomberman_cheering' | 'minimal_strict' | 'minimal_fast'>('bomberman_idle')

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
        spriteIdle: '/assets/sprites/bomberman/atlas_white_idle.png',
        spriteCheering: '/assets/sprites/bomberman/atlas_white_cheering.png',
        skinName: 'White Bomberman (P1)',
      }
    }
    if (name.includes('vega')) {
      return {
        personality: 'Arquitecta de datos implacable, garante de la persistencia ACID en SQLite WAL.',
        voiceTone: 'Analítica y defensiva, previene cualquier corrupción de contratos de datos.',
        sdlcRole: 'Stage 4: Mutación de Modelos, Schemas de Base de Datos y Repositorios.',
        ownedPaths: ['src/sacl/storage', 'migrations/', 'database/postgresql'],
        avatarBorder: 'border-purple-500/40 text-purple-400 bg-purple-500/10',
        spriteIdle: '/assets/sprites/bomberman/vega_blue_idle.png',
        spriteCheering: '/assets/sprites/bomberman/vega_blue_cheering.png',
        skinName: 'Blue Bomberman (P3)',
      }
    }
    if (name.includes('nova')) {
      return {
        personality: 'Certificadora de calidad con tolerancia cero al falso positivo.',
        voiceTone: 'Metódica y rigurosa, no permite avance sin cobertura del 100%.',
        sdlcRole: 'Stage 5-7: Suites de Pruebas Unitarias, Integración y Contratos OpenAPI.',
        ownedPaths: ['tests/', 'tests/unit', 'tests/integration', 'contracts/'],
        avatarBorder: 'border-emerald-500/40 text-emerald-400 bg-emerald-500/10',
        spriteIdle: '/assets/sprites/bomberman/nova_red_idle.png',
        spriteCheering: '/assets/sprites/bomberman/nova_red_cheering.png',
        skinName: 'Red/Green Bomberman (P4)',
      }
    }
    return {
      personality: 'Guardián constitucional, supervisor de las 9 prohibiciones de SolidBit.',
      voiceTone: 'Vigilante e inmutable, custodial absoluto de la compuerta Gate 5.',
      sdlcRole: 'Stage 8-9: Detección de Fugas, Verificación de Políticas y Gate 5 HMAC.',
      ownedPaths: ['src/sacl/security', 'src/sacl/policy', '.github/'],
      avatarBorder: 'border-amber-500/40 text-amber-400 bg-amber-500/10',
      spriteIdle: '/assets/sprites/bomberman/centinela_black_idle.png',
      spriteCheering: '/assets/sprites/bomberman/centinela_black_cheering.png',
      skinName: 'Black Bomberman (P2)',
    }
  }

  const persona = getPersonaDetails()

  const currentAvatarSrc =
    selectedSkin === 'bomberman_cheering'
      ? persona.spriteCheering
      : persona.spriteIdle

  const handleSelectSkin = (skin: 'bomberman_idle' | 'bomberman_cheering' | 'minimal_strict' | 'minimal_fast') => {
    setSelectedSkin(skin)
    if (onSkinChange) {
      onSkinChange(agent.agentName, skin)
    }
  }

  return (
    <div className="fixed inset-0 z-[140] bg-black/60 backdrop-blur-sm flex justify-end select-none animate-in fade-in duration-200">
      <div className="w-full max-w-md bg-[#0a0a0a] border-l border-white/8 h-full flex flex-col justify-between text-left p-6 shadow-2xl animate-in slide-in-from-right duration-200">
        {/* Top Header */}
        <div>
          <div className="flex items-center justify-between border-b border-white/8 pb-4">
            <div className="flex items-center gap-3 min-w-0">
              <div className={`w-12 h-12 rounded-lg border flex items-center justify-center p-1 shrink-0 bg-[#000000] ${persona.avatarBorder}`}>
                <img
                  src={currentAvatarSrc}
                  alt={agent.agentName}
                  className="w-8 h-8 object-contain [image-rendering:pixelated]"
                />
              </div>
              <div className="min-w-0">
                <div className="flex items-center gap-1.5">
                  <h2 className="text-sm font-bold text-white uppercase tracking-wider font-sans truncate">
                    {agent.agentName}
                  </h2>
                  <span className="text-[9px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-1 py-0.2 rounded">
                    SKIN ACTIVA
                  </span>
                </div>
                <p className="text-[10px] text-zinc-400 font-mono truncate">{agent.role}</p>
                <p className="text-[9px] text-zinc-500 font-mono truncate">{persona.skinName}</p>
              </div>
            </div>

            <button
              type="button"
              onClick={onClose}
              className="text-zinc-500 hover:text-white font-mono text-sm px-2 py-1 rounded transition cursor-pointer"
            >
              ✕
            </button>
          </div>

          {/* Navigation Tabs */}
          <div className="flex border-b border-white/8 mt-4 gap-4 text-xs font-mono">
            <button
              type="button"
              onClick={() => setActiveTab('profile')}
              className={`pb-2 border-b-2 transition cursor-pointer ${
                activeTab === 'profile'
                  ? 'border-white text-white font-bold'
                  : 'border-transparent text-zinc-500 hover:text-zinc-300'
              }`}
            >
              Identidad
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('sdlc')}
              className={`pb-2 border-b-2 transition cursor-pointer ${
                activeTab === 'sdlc'
                  ? 'border-white text-white font-bold'
                  : 'border-transparent text-zinc-500 hover:text-zinc-300'
              }`}
            >
              Ciclo SDLC
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('skins')}
              className={`pb-2 border-b-2 transition cursor-pointer flex items-center gap-1 ${
                activeTab === 'skins'
                  ? 'border-emerald-400 text-emerald-400 font-bold'
                  : 'border-transparent text-zinc-500 hover:text-zinc-300'
              }`}
            >
              <span>🎮 Skins & Sprites</span>
            </button>
          </div>

          {/* Tab Content */}
          <div className="mt-4 space-y-4 overflow-y-auto max-h-[60vh] custom-scroll pr-1">
            {activeTab === 'profile' && (
              <div className="space-y-3.5">
                <div className="p-3 bg-[#000000] border border-white/8 rounded-lg space-y-1">
                  <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-wider">
                    Personalidad Arquitectónica
                  </span>
                  <p className="text-xs text-zinc-200 font-sans leading-relaxed">
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
                  Catálogo de Skins Super Bomberman (16-bit SNES)
                </span>

                {/* Skin 1: Bomberman Idle */}
                <div
                  onClick={() => handleSelectSkin('bomberman_idle')}
                  className={`p-3 rounded-lg border transition cursor-pointer flex items-center justify-between gap-3 ${
                    selectedSkin === 'bomberman_idle'
                      ? 'bg-emerald-500/10 border-emerald-500/40 text-white'
                      : 'bg-[#000000] border-white/8 hover:border-white/20 text-zinc-400'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded bg-[#121212] border border-white/10 flex items-center justify-center p-1">
                      <img
                        src={persona.spriteIdle}
                        alt="Idle"
                        className="w-7 h-7 object-contain [image-rendering:pixelated]"
                      />
                    </div>
                    <div>
                      <div className="font-bold text-xs font-mono text-white">
                        {persona.skinName} · Walk / Idle
                      </div>
                      <div className="text-[10px] text-zinc-500">Sprite frontal clásico reactivo</div>
                    </div>
                  </div>
                  {selectedSkin === 'bomberman_idle' && (
                    <span className="text-[9px] font-mono text-emerald-400 bg-emerald-500/20 px-1.5 py-0.5 rounded">
                      ACTIVA
                    </span>
                  )}
                </div>

                {/* Skin 2: Bomberman Cheering (Victoria) */}
                <div
                  onClick={() => handleSelectSkin('bomberman_cheering')}
                  className={`p-3 rounded-lg border transition cursor-pointer flex items-center justify-between gap-3 ${
                    selectedSkin === 'bomberman_cheering'
                      ? 'bg-emerald-500/10 border-emerald-500/40 text-white'
                      : 'bg-[#000000] border-white/8 hover:border-white/20 text-zinc-400'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded bg-[#121212] border border-white/10 flex items-center justify-center p-1">
                      <img
                        src={persona.spriteCheering}
                        alt="Cheering"
                        className="w-7 h-7 object-contain [image-rendering:pixelated]"
                      />
                    </div>
                    <div>
                      <div className="font-bold text-xs font-mono text-white">
                        {persona.skinName} · Cheering (Victoria Gate 5)
                      </div>
                      <div className="text-[10px] text-zinc-500">Celebración post-aprobación HMAC</div>
                    </div>
                  </div>
                  {selectedSkin === 'bomberman_cheering' && (
                    <span className="text-[9px] font-mono text-emerald-400 bg-emerald-500/20 px-1.5 py-0.5 rounded">
                      ACTIVA
                    </span>
                  )}
                </div>

                {/* Modos Minimalistas */}
                <div className="pt-2 border-t border-white/8 space-y-2">
                  <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-wider block">
                    Modos de Ejecución SDLC
                  </span>
                  <div className="grid grid-cols-2 gap-2">
                    <div
                      onClick={() => handleSelectSkin('minimal_strict')}
                      className={`p-2.5 rounded border text-xs font-mono transition cursor-pointer ${
                        selectedSkin === 'minimal_strict'
                          ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-300'
                          : 'bg-[#000000] border-white/8 text-zinc-500'
                      }`}
                    >
                      <div className="font-bold">Strict Mode</div>
                      <div className="text-[9px] text-zinc-600 mt-0.5">Auditoría Formal</div>
                    </div>
                    <div
                      onClick={() => handleSelectSkin('minimal_fast')}
                      className={`p-2.5 rounded border text-xs font-mono transition cursor-pointer ${
                        selectedSkin === 'minimal_fast'
                          ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-300'
                          : 'bg-[#000000] border-white/8 text-zinc-500'
                      }`}
                    >
                      <div className="font-bold">Fast Mode</div>
                      <div className="text-[9px] text-zinc-600 mt-0.5">Pase Rápido UI</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-white/8 flex items-center justify-between text-[10px] font-mono text-zinc-500 shrink-0">
          <span>Identidad Gobernada por SolidBit EOP</span>
          <button
            type="button"
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
