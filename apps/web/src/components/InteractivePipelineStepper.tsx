import React from 'react'
import {
  FolderGit2,
  Calendar,
  GitBranch,
  Bot,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  ShieldAlert,
} from 'lucide-react'
import type { OperationalDomainState } from '../types/domainState'
import { useLanguage } from '../context/LanguageContext'

export interface PipelineStep {
  id: string
  labelEs: string
  labelEn: string
  sectionId: string
  associatedState: OperationalDomainState
}

export const PIPELINE_STEPS: PipelineStep[] = [
  {
    id: 'link',
    labelEs: '1. Vincular',
    labelEn: '1. Link',
    sectionId: 'projects',
    associatedState: 'UNINITIALIZED',
  },
  {
    id: 'plan',
    labelEs: '2. Planificar',
    labelEn: '2. Plan',
    sectionId: 'dashboard',
    associatedState: 'PLANNING',
  },
  {
    id: 'map',
    labelEs: '3. Mapear DAG',
    labelEn: '3. Map DAG',
    sectionId: 'roadmap',
    associatedState: 'EXECUTING',
  },
  {
    id: 'squad',
    labelEs: '4. Escuadrón',
    labelEn: '4. Squad',
    sectionId: 'agents',
    associatedState: 'EXECUTING',
  },
  {
    id: 'authorize',
    labelEs: '5. Autorizar',
    labelEn: '5. Authorize',
    sectionId: 'executions',
    associatedState: 'AWAITING_APPROVAL',
  },
]

interface InteractivePipelineStepperProps {
  currentSection: string
  currentState: OperationalDomainState
  onSelectStep: (sectionId: string) => void
  hasConflict?: boolean
  isExecuting?: boolean
  pendingGatesCount?: number
}

export const InteractivePipelineStepper: React.FC<InteractivePipelineStepperProps> = ({
  currentSection,
  currentState,
  onSelectStep,
  hasConflict = false,
  isExecuting = false,
  pendingGatesCount = 0,
}) => {
  const { t } = useLanguage()

  return (
    <div className="w-full bg-[#0C0C0E] border border-white/5 rounded-2xl p-2.5 flex items-center justify-between gap-2 overflow-x-auto select-none shadow-md">
      <div className="flex items-center gap-1.5 sm:gap-2 min-w-max">
        {PIPELINE_STEPS.map((step, idx) => {
          const isSectionActive =
            currentSection === step.sectionId ||
            (step.sectionId === 'dashboard' && currentSection === 'dashboard')

          const isFSMActive =
            (step.associatedState === 'UNINITIALIZED' && currentState === 'UNINITIALIZED') ||
            (step.associatedState === 'PLANNING' && currentState === 'PLANNING') ||
            (step.associatedState === 'AWAITING_APPROVAL' && currentState === 'AWAITING_APPROVAL') ||
            (step.associatedState === 'EXECUTING' && (currentState === 'EXECUTING' || isExecuting))

          const isTerminalDone =
            currentState === 'COMPLETED' && (idx < 4 || (idx === 4 && pendingGatesCount === 0))

          return (
            <button
              key={step.id}
              type="button"
              onClick={() => onSelectStep(step.sectionId)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-mono font-semibold transition-all cursor-pointer ${
                isSectionActive
                  ? 'bg-white text-black font-extrabold shadow-sm ring-1 ring-white/50 scale-[1.02]'
                  : isFSMActive
                  ? 'bg-cyan-950/40 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-900/40'
                  : isTerminalDone
                  ? 'bg-zinc-900/80 text-zinc-300 hover:text-white hover:bg-zinc-800'
                  : 'bg-black/60 text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900/40'
              }`}
            >
              {isFSMActive && isExecuting ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin text-cyan-400" />
              ) : isFSMActive && currentState === 'AWAITING_APPROVAL' ? (
                <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
              ) : isTerminalDone ? (
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              ) : (
                <span
                  className={`w-2 h-2 rounded-full ${
                    isSectionActive ? 'bg-black' : isFSMActive ? 'bg-cyan-400' : 'bg-zinc-600'
                  }`}
                />
              )}
              <span>{t(step.labelEs, step.labelEn)}</span>
            </button>
          )
        })}
      </div>

      {/* Indicador de Incidencia / Alerta Preventiva */}
      {hasConflict && (
        <button
          type="button"
          onClick={() => onSelectStep('dashboard')}
          className="flex items-center gap-1.5 px-3 py-1 rounded-xl bg-rose-500/20 text-rose-300 border border-rose-500/40 text-xs font-mono font-bold animate-pulse cursor-pointer shrink-0 ml-2"
        >
          <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
          <span>{t('Incidencia Preventiva', 'Preventive Issue')}</span>
        </button>
      )}
    </div>
  )
}
