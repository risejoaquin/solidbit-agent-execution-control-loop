import React from 'react'

export interface VoicePersona {
  id: string
  name: string
  role: string
  badge: string
  systemPromptDirective: string
  color: string
}

export const AVAILABLE_VOICES: VoicePersona[] = [
  {
    id: 'sec-auditor',
    name: 'Centinela Security',
    role: 'Auditor Constitucional',
    badge: 'Hard Deny',
    systemPromptDirective: 'Aplica análisis estricto de las 9 prohibiciones constitucionales. Bloquea cualquier token expuesto o mutación directa a main.',
    color: 'border-amber-500/40 text-amber-400 bg-amber-500/10',
  },
  {
    id: 'arch-strict',
    name: 'Atlas Orchestrator',
    role: 'Arquitecto Kahn DAG',
    badge: 'Topológico',
    systemPromptDirective: 'Prioriza el ordenamiento topológico determinista, la idempotencia de comandos y la resolución de dependencias sin ciclos.',
    color: 'border-blue-500/40 text-blue-400 bg-blue-500/10',
  },
  {
    id: 'data-vega',
    name: 'Vega Data Architect',
    role: 'Especialista SQLite WAL & PG',
    badge: 'ACID Strict',
    systemPromptDirective: 'Fuerza el patrón Outbox, atomicidad en transacciones SQLite y congruencia de esquemas relacionales sin pérdida de eventos.',
    color: 'border-purple-500/40 text-purple-400 bg-purple-500/10',
  },
  {
    id: 'qa-nova',
    name: 'Nova QA Certifier',
    role: 'Inspectora de Calidad 100%',
    badge: 'Zero-Tolerance',
    systemPromptDirective: 'Exige suites de pruebas deterministas (Pytest / xUnit), validación de contratos OpenAPI y cobertura total antes de compuertas.',
    color: 'border-emerald-500/40 text-emerald-400 bg-emerald-500/10',
  },
  {
    id: 'front-minimal',
    name: 'Frontend Architect (SolidBit)',
    role: 'UX / Zero-Blocking UI',
    badge: 'O(1) Render',
    systemPromptDirective: 'Preserva la jerarquía de diseño negro puro (bg-[#000000]), superficies bg-[#0a0a0a], border-white/8 y react-memo O(1).',
    color: 'border-cyan-500/40 text-cyan-400 bg-cyan-500/10',
  },
]

interface SoftPhaseMultiVoiceProps {
  selectedVoiceIds: string[]
  onToggleVoice: (id: string) => void
}

export const SoftPhaseMultiVoice: React.FC<SoftPhaseMultiVoiceProps> = ({
  selectedVoiceIds,
  onToggleVoice,
}) => {
  return (
    <div className="bg-[#0a0a0a] border border-white/8 rounded-lg p-3 space-y-2.5 select-none text-left">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-mono font-bold text-white uppercase tracking-wider">
            Fase Soft · Multivoces Activas
          </span>
        </div>
        <span className="text-[10px] font-mono text-zinc-500">
          {selectedVoiceIds.length} voz(ces) inyectada(s)
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
        {AVAILABLE_VOICES.map((voice) => {
          const isSelected = selectedVoiceIds.includes(voice.id)
          return (
            <button
              key={voice.id}
              type="button"
              onClick={() => onToggleVoice(voice.id)}
              className={`p-2.5 rounded-lg border text-left transition cursor-pointer flex flex-col justify-between ${
                isSelected
                  ? `${voice.color} shadow-sm`
                  : 'bg-[#000000] border-white/8 hover:border-white/20 text-zinc-400'
              }`}
            >
              <div>
                <div className="flex items-center justify-between gap-1 mb-1">
                  <span className="text-xs font-bold font-sans truncate">{voice.name}</span>
                  <span className="text-[8px] font-mono uppercase px-1 rounded border border-current shrink-0">
                    {voice.badge}
                  </span>
                </div>
                <div className="text-[10px] font-mono text-zinc-500 truncate">{voice.role}</div>
              </div>

              <div className="text-[9px] font-sans text-zinc-400 line-clamp-2 mt-1.5">
                {voice.systemPromptDirective}
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
