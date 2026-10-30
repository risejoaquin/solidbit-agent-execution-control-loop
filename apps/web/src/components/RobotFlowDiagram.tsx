import React from 'react'
import {
  CheckCircle2,
  ArrowRight,
  ShieldCheck,
  UserCheck,
  Sparkles,
  Code2,
  GitCommit,
  Bot,
  Layers,
} from 'lucide-react'

interface RobotFlowDiagramProps {
  currentPhase: 1 | 2 | 3
  onSelectPhase?: (phase: 1 | 2 | 3) => void
  hasValidatedContracts?: boolean
  isDeploySuccess?: boolean
}

// Retro Robot Illustration SVG matching user's drawing
const RetroRobotIcon: React.FC<{
  phase: 1 | 2 | 3
  isActive: boolean
  isCompleted: boolean
}> = ({ phase, isActive, isCompleted }) => {
  const getColors = () => {
    if (isCompleted) {
      return {
        body: '#064e3b', // emerald-950
        border: '#10b981', // emerald-500
        screen: '#059669', // emerald-600
        glow: 'rgba(16, 185, 129, 0.4)',
        eyes: '#a7f3d0',
      }
    }
    if (isActive) {
      return {
        body: '#18181b', // zinc-900
        border: '#ffffff', // white
        screen: phase === 1 ? '#3b82f6' : phase === 2 ? '#f59e0b' : '#10b981',
        glow: 'rgba(255, 255, 255, 0.3)',
        eyes: '#ffffff',
      }
    }
    return {
      body: '#09090b',
      border: '#27272a',
      screen: '#18181b',
      glow: 'none',
      eyes: '#52525b',
    }
  }

  const c = getColors()

  return (
    <div
      className="relative flex flex-col items-center justify-center transition-all duration-300"
      style={{ filter: isActive ? `drop-shadow(0 0 12px ${c.glow})` : 'none' }}
    >
      <svg
        width="64"
        height="64"
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="transform transition-transform duration-300 hover:scale-105"
      >
        {/* Antena */}
        <circle cx="32" cy="6" r="3" fill={c.border} />
        <line x1="32" y1="9" x2="32" y2="15" stroke={c.border} strokeWidth="2.5" />

        {/* Orejas / Pernos */}
        <rect x="10" y="22" width="4" height="8" rx="1.5" fill={c.border} />
        <rect x="50" y="22" width="4" height="8" rx="1.5" fill={c.border} />

        {/* Cabeza del Robot */}
        <rect
          x="14"
          y="15"
          width="36"
          height="24"
          rx="5"
          fill={c.body}
          stroke={c.border}
          strokeWidth="2.5"
        />

        {/* Pantalla Facial */}
        <rect
          x="19"
          y="19"
          width="26"
          height="14"
          rx="3"
          fill={c.screen}
          opacity={isActive || isCompleted ? 1 : 0.4}
        />

        {/* Ojos */}
        <circle cx="26" cy="26" r="2.5" fill={c.eyes} />
        <circle cx="38" cy="26" r="2.5" fill={c.eyes} />

        {/* Cuello */}
        <rect x="28" y="39" width="8" height="4" fill={c.border} />

        {/* Cuerpo */}
        <rect
          x="16"
          y="43"
          width="32"
          height="17"
          rx="4"
          fill={c.body}
          stroke={c.border}
          strokeWidth="2.5"
        />

        {/* Indicadores en el pecho */}
        <circle cx="24" cy="51" r="2" fill={isActive ? '#ffffff' : '#71717a'} />
        <circle cx="32" cy="51" r="2" fill={isActive ? '#38bdf8' : '#71717a'} />
        <circle cx="40" cy="51" r="2" fill={isActive ? '#4ade80' : '#71717a'} />
      </svg>

      {/* Número de Fase manuscrito / estilizado */}
      <span
        className={`mt-1 font-mono font-black text-sm transition ${
          isActive ? 'text-white scale-110' : isCompleted ? 'text-emerald-400' : 'text-zinc-600'
        }`}
      >
        {phase}
      </span>
    </div>
  )
}

export const RobotFlowDiagram: React.FC<RobotFlowDiagramProps> = ({
  currentPhase,
  onSelectPhase,
  hasValidatedContracts = true,
  isDeploySuccess = false,
}) => {
  return (
    <div className="w-full p-4 sm:p-6 rounded-3xl bg-black/60 border border-zinc-800/80 backdrop-blur-md shadow-2xl">
      <div className="flex flex-col lg:flex-row items-center justify-between gap-4 lg:gap-2">
        {/* ===================================================================
            NODO 1: AGENTE FASE 1
           =================================================================== */}
        <div
          onClick={() => onSelectPhase?.(1)}
          className={`flex-1 flex flex-col items-center text-center p-3 sm:p-4 rounded-2xl transition cursor-pointer border ${
            currentPhase === 1
              ? 'bg-zinc-900/90 border-white/60 shadow-lg'
              : currentPhase > 1
              ? 'bg-emerald-950/20 border-emerald-500/30'
              : 'bg-zinc-950/40 border-zinc-850 hover:border-zinc-700'
          }`}
        >
          <RetroRobotIcon
            phase={1}
            isActive={currentPhase === 1}
            isCompleted={currentPhase > 1}
          />
          <h3 className="mt-2 text-xs sm:text-sm font-black uppercase tracking-wider text-white">
            AGENTE FASE 1
          </h3>
          <p className="text-[11px] text-zinc-400 max-w-[200px] mt-1 leading-snug">
            Diseñar sprint con chat o métodos ya establecidos
          </p>
        </div>

        {/* ===================================================================
            FLECHA Y COMPUERTA 1 -> 2: APROBACIÓN HUMANA
           =================================================================== */}
        <div className="flex flex-col items-center justify-center px-2 py-1 text-center shrink-0">
          <div className="flex items-center gap-1.5 text-zinc-500">
            <span className="w-6 sm:w-10 h-0.5 bg-zinc-700 rounded-full" />
            <ArrowRight className="w-4 h-4 text-zinc-400" />
          </div>
          <div
            className={`mt-1 px-2.5 py-1 rounded-full text-[10px] font-mono font-bold flex items-center gap-1 border ${
              currentPhase > 1
                ? 'bg-emerald-950/40 text-emerald-300 border-emerald-500/40'
                : 'bg-zinc-900 text-zinc-300 border-zinc-750'
            }`}
          >
            {hasValidatedContracts ? (
              <>
                <ShieldCheck className="w-3 h-3 text-emerald-400" />
                <span>aprobación humana / contrato</span>
              </>
            ) : (
              <>
                <UserCheck className="w-3 h-3 text-amber-400" />
                <span>aprobación humana.</span>
              </>
            )}
          </div>
        </div>

        {/* ===================================================================
            NODO 2: AGENTE FASE 2
           =================================================================== */}
        <div
          onClick={() => onSelectPhase?.(2)}
          className={`flex-1 flex flex-col items-center text-center p-3 sm:p-4 rounded-2xl transition cursor-pointer border ${
            currentPhase === 2
              ? 'bg-zinc-900/90 border-white/60 shadow-lg'
              : currentPhase > 2
              ? 'bg-emerald-950/20 border-emerald-500/30'
              : 'bg-zinc-950/40 border-zinc-850 hover:border-zinc-700'
          }`}
        >
          <RetroRobotIcon
            phase={2}
            isActive={currentPhase === 2}
            isCompleted={currentPhase > 2}
          />
          <h3 className="mt-2 text-xs sm:text-sm font-black uppercase tracking-wider text-white">
            AGENTE FASE 2
          </h3>
          <p className="text-[11px] text-zinc-400 max-w-[200px] mt-1 leading-snug">
            Implementa lo decidido y muestra resultados
          </p>
        </div>

        {/* ===================================================================
            FLECHA Y COMPUERTA 2 -> 3: HUMANO APRUEBA
           =================================================================== */}
        <div className="flex flex-col items-center justify-center px-2 py-1 text-center shrink-0">
          <div className="flex items-center gap-1.5 text-zinc-500">
            <span className="w-6 sm:w-10 h-0.5 bg-zinc-700 rounded-full" />
            <ArrowRight className="w-4 h-4 text-zinc-400" />
          </div>
          <div
            className={`mt-1 px-2.5 py-1 rounded-full text-[10px] font-mono font-bold flex items-center gap-1 border ${
              isDeploySuccess || currentPhase === 3
                ? 'bg-emerald-950/40 text-emerald-300 border-emerald-500/40'
                : 'bg-zinc-900 text-zinc-300 border-zinc-750'
            }`}
          >
            <UserCheck className="w-3 h-3 text-emerald-400" />
            <span>humano aprueba si lo implementado es correcto</span>
          </div>
        </div>

        {/* ===================================================================
            NODO 3: AGENTE FASE 3
           =================================================================== */}
        <div
          onClick={() => onSelectPhase?.(3)}
          className={`flex-1 flex flex-col items-center text-center p-3 sm:p-4 rounded-2xl transition cursor-pointer border ${
            currentPhase === 3
              ? 'bg-zinc-900/90 border-white/60 shadow-lg'
              : isDeploySuccess
              ? 'bg-emerald-950/20 border-emerald-500/30'
              : 'bg-zinc-950/40 border-zinc-850 hover:border-zinc-700'
          }`}
        >
          <RetroRobotIcon
            phase={3}
            isActive={currentPhase === 3}
            isCompleted={isDeploySuccess}
          />
          <h3 className="mt-2 text-xs sm:text-sm font-black uppercase tracking-wider text-white">
            AGENTE FASE 3
          </h3>
          <p className="text-[11px] text-zinc-400 max-w-[200px] mt-1 leading-snug">
            Sube y fusiona los cambios a la rama
          </p>
        </div>
      </div>
    </div>
  )
}
