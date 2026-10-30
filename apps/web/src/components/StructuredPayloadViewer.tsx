import React, { useState } from 'react'
import {
  FileCode,
  Terminal,
  FolderGit2,
  Clock,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Cpu,
  GitBranch,
  GitCommit,
  Hash,
  Layers,
  ExternalLink,
} from 'lucide-react'
import type { VerifiableExecutionResult } from '../types/cqrsContract'
import { StatusBadge } from './ui/status-badge'

interface StructuredPayloadViewerProps {
  execution: VerifiableExecutionResult
  onRequireHITL?: () => void
  onRetryTask?: () => void
}

export const StructuredPayloadViewer: React.FC<StructuredPayloadViewerProps> = ({
  execution,
  onRequireHITL,
  onRetryTask,
}) => {
  const [activeTab, setActiveTab] = useState<'cqrs' | 'sandbox' | 'timing' | 'post_condition'>('cqrs')
  const [showRawJson, setShowRawJson] = useState(false)

  const evt = execution.execution_event
  const sbx = execution.sandbox_context
  const timing = execution.fsm_timing
  const post = execution.post_condition

  const isStale = timing?.is_stale || (timing?.latency_ms ? timing.latency_ms > (timing.timeout_sec || 30) * 1000 : false)
  const isPostConditionFailed = post?.status === 'POST_CONDITION_FAILED' || (post && !post.contract_verified)
  const isSandboxDesynced = sbx ? (!sbx.verified || !sbx.commit_sha || !sbx.worktree_path) : false

  return (
    <div className="rounded-2xl bg-[#09090B] border border-white/10 overflow-hidden shadow-2xl text-left font-sans animate-fade-in">
      {/* Top Banner: Verification Status & 4 Questions Tab Bar */}
      <div className="p-4 sm:p-5 border-b border-white/5 bg-[#0C0C0E] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-zinc-400">
              Protocolo de Verificación Observable
            </span>
            <span className="text-zinc-600">&bull;</span>
            <code className="text-[11px] font-mono text-cyan-400 font-semibold">
              {execution.execution_id || 'EXEC-SACL'}
            </code>

            {/* Invariant & Contract Status Badges */}
            {isPostConditionFailed ? (
              <StatusBadge status="ERROR" label="POSTCONDICIÓN FALLIDA" />
            ) : isSandboxDesynced ? (
              <StatusBadge status="WARNING" label="SANDBOX DESINCRONIZADO" pulsing />
            ) : isStale ? (
              <StatusBadge status="WARNING" label="TIMEOUT / STALE STATE" pulsing />
            ) : (
              <StatusBadge status="SUCCESS" label="ESTADO VERIFICADO" />
            )}
          </div>
          <h3 className="text-sm font-extrabold text-white">
            {execution.title || 'Ejecución Atómica de Asistente'}
          </h3>
        </div>

        {/* 4 Pillars Navigation Tabs */}
        <div className="flex items-center gap-1 p-1 rounded-xl bg-black border border-white/5 overflow-x-auto">
          <button
            type="button"
            onClick={() => setActiveTab('cqrs')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition cursor-pointer flex items-center gap-1.5 shrink-0 ${
              activeTab === 'cqrs' ? 'bg-zinc-800 text-white' : 'text-zinc-400 hover:text-white'
            }`}
          >
            <FileCode className="w-3.5 h-3.5 text-cyan-400" />
            <span>1. ¿Qué? (CQRS)</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('sandbox')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition cursor-pointer flex items-center gap-1.5 shrink-0 ${
              activeTab === 'sandbox' ? 'bg-zinc-800 text-white' : 'text-zinc-400 hover:text-white'
            }`}
          >
            <FolderGit2 className="w-3.5 h-3.5 text-sky-400" />
            <span>2. ¿Dónde? (Worktree)</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('timing')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition cursor-pointer flex items-center gap-1.5 shrink-0 ${
              activeTab === 'timing' ? 'bg-zinc-800 text-white' : 'text-zinc-400 hover:text-white'
            }`}
          >
            <Clock className="w-3.5 h-3.5 text-amber-400" />
            <span>3. ¿Cuándo? (FSM)</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('post_condition')}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition cursor-pointer flex items-center gap-1.5 shrink-0 ${
              activeTab === 'post_condition' ? 'bg-zinc-800 text-white' : 'text-zinc-400 hover:text-white'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>4. ¿Hecho? (Contrato)</span>
          </button>
        </div>
      </div>

      {/* Critical Warnings based on Contract Discrepancies */}
      {isPostConditionFailed && (
        <div className="p-4 bg-rose-950/30 border-b border-rose-500/40 text-xs text-rose-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <ShieldAlert className="w-5 h-5 text-rose-400 shrink-0" />
            <div>
              <strong className="block font-bold">Postcondición No Cumplida (Falso Positivo Bloqueado)</strong>
              <span>El resultado de salida o el estado git --porcelain no coincide con el contrato de la tarea.</span>
            </div>
          </div>
          {onRequireHITL && (
            <button
              type="button"
              onClick={onRequireHITL}
              className="px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs cursor-pointer shrink-0"
            >
              Intervención Manual (HITL)
            </button>
          )}
        </div>
      )}

      {isSandboxDesynced && (
        <div className="p-4 bg-amber-950/30 border-b border-amber-500/40 text-xs text-amber-200 flex items-center gap-2.5">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />
          <div>
            <strong className="block font-bold">Sandbox Desincronizado / Sin Aislamiento Físico Verificado</strong>
            <span>La respuesta del agente no incluye el hash del worktree activo o su ruta física es inconsistente.</span>
          </div>
        </div>
      )}

      {isStale && (
        <div className="p-4 bg-amber-950/30 border-b border-amber-500/40 text-xs text-amber-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <Clock className="w-5 h-5 text-amber-400 shrink-0" />
            <div>
              <strong className="block font-bold">Alerta de Inactividad (Stale State)</strong>
              <span>La tarea superó el umbral de {timing?.timeout_sec || 30}s (Latencia: {timing?.latency_ms}ms).</span>
            </div>
          </div>
          {onRetryTask && (
            <button
              type="button"
              onClick={onRetryTask}
              className="px-3 py-1.5 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-white font-bold text-xs cursor-pointer shrink-0"
            >
              Reiniciar Subproceso
            </button>
          )}
        </div>
      )}

      {/* Tab Contents */}
      <div className="p-5 space-y-4">
        {/* ===================================================================
            1. ¿QUÉ SE ESTÁ PROCESANDO? (CQRS / PAYLOAD OBSERVABLE)
           =================================================================== */}
        {activeTab === 'cqrs' && (
          <div className="space-y-4 animate-fade-in text-xs">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Input Payload & Business Intent */}
              <div className="p-4 rounded-xl bg-black border border-white/5 space-y-2.5">
                <span className="text-[10px] font-mono uppercase text-zinc-400 font-bold block">
                  A. Payload de Entrada e Intención de Negocio
                </span>
                <div className="space-y-1.5 font-mono text-[11px]">
                  <div>
                    <span className="text-zinc-500">Objetivo declarado:</span>
                    <p className="text-white font-medium mt-0.5">
                      {evt?.input_payload?.intent || execution.summary || 'Verificación declarada'}
                    </p>
                  </div>
                  <div>
                    <span className="text-zinc-500">Acción Solicitada:</span>
                    <span className="text-cyan-400 font-bold block">{execution.action_type}</span>
                  </div>
                  {evt?.input_payload?.params && Object.keys(evt.input_payload.params).length > 0 && (
                    <div className="pt-1 border-t border-zinc-800/80">
                      <span className="text-zinc-500 block mb-1">Parámetros:</span>
                      <pre className="p-2 rounded bg-zinc-950 text-[10px] text-zinc-300 overflow-x-auto">
                        {JSON.stringify(evt.input_payload.params, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </div>

              {/* Executed Atomic Command */}
              <div className="p-4 rounded-xl bg-black border border-white/5 space-y-2.5">
                <span className="text-[10px] font-mono uppercase text-zinc-400 font-bold block">
                  B. Comando Atómico Ejecutado en Subproceso
                </span>
                <div className="space-y-2 font-mono text-[11px]">
                  <div className="flex items-center gap-2 p-2 rounded bg-zinc-950 border border-white/5">
                    <Terminal className="w-4 h-4 text-emerald-400 shrink-0" />
                    <code className="text-emerald-300 truncate">
                      {evt?.executed_command?.binary || 'python'} {evt?.executed_command?.args?.join(' ') || execution.action_type}
                    </code>
                  </div>

                  <div>
                    <span className="text-zinc-500">Directorio de Ejecución (CWD):</span>
                    <span className="text-zinc-300 block truncate" title={evt?.executed_command?.cwd || sbx?.worktree_path}>
                      {evt?.executed_command?.cwd || sbx?.worktree_path || 'Entorno local'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between pt-1 border-t border-zinc-800/80">
                    <span className="text-zinc-500">Código de Salida:</span>
                    <span className={`font-bold ${execution.exit_code === 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {execution.exit_code} ({execution.exit_code === 0 ? 'EXIT_SUCCESS' : 'EXIT_FAILURE'})
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Mutated Files & Structured Output */}
            <div className="p-4 rounded-xl bg-black border border-white/5 space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono uppercase text-zinc-400 font-bold block">
                  C. Resultado Parcial y Archivos Mutados en Disco
                </span>
                <span className="text-[10px] font-mono text-zinc-500">
                  {evt?.partial_result?.mutated_files?.length || 0} archivos registrados
                </span>
              </div>

              {evt?.partial_result?.mutated_files && evt.partial_result.mutated_files.length > 0 ? (
                <div className="space-y-1 font-mono text-xs max-h-40 overflow-y-auto custom-scroll">
                  {evt.partial_result.mutated_files.map((f, i) => (
                    <div key={i} className="flex items-center justify-between p-2 rounded bg-zinc-950 border border-white/5">
                      <span className="text-zinc-200 truncate">{f.path}</span>
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                        f.status === 'M' ? 'bg-amber-950/40 text-amber-300' :
                        f.status === 'A' ? 'bg-emerald-950/40 text-emerald-300' : 'bg-zinc-800 text-zinc-400'
                      }`}>
                        {f.status}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-[11px] text-zinc-500 italic py-2">
                  No hubo mutaciones en disco durante esta lectura o verificación preventiva.
                </p>
              )}
            </div>
          </div>
        )}

        {/* ===================================================================
            2. ¿DÓNDE SE ESTÁ PROCESANDO? (AISLAMIENTO DE WORKTREE)
           =================================================================== */}
        {activeTab === 'sandbox' && (
          <div className="space-y-4 animate-fade-in text-xs font-mono">
            <div className="p-4 rounded-xl bg-black border border-white/5 space-y-3">
              <span className="text-[10px] uppercase text-zinc-400 font-bold block">
                Metadatos de Entorno Inyectados (Execution Context Injection)
              </span>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-zinc-950 border border-white/5 space-y-1">
                  <span className="text-zinc-500 text-[10px] uppercase">ID de Sandbox</span>
                  <span className="text-white font-bold block flex items-center gap-1.5">
                    <Cpu className="w-3.5 h-3.5 text-sky-400" />
                    {sbx?.sandbox_id || 'sbx-local-worktree'}
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-zinc-950 border border-white/5 space-y-1">
                  <span className="text-zinc-500 text-[10px] uppercase">Rama Git Activa</span>
                  <span className="text-sky-300 font-bold block flex items-center gap-1.5">
                    <GitBranch className="w-3.5 h-3.5" />
                    {sbx?.git_branch || 'main'}
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-zinc-950 border border-white/5 space-y-1">
                  <span className="text-zinc-500 text-[10px] uppercase">Commit SHA Criptográfico</span>
                  <span className="text-emerald-400 font-bold block flex items-center gap-1.5">
                    <GitCommit className="w-3.5 h-3.5" />
                    {sbx?.commit_sha || 'HEAD'}
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-zinc-950 border border-white/5 space-y-1">
                  <span className="text-zinc-500 text-[10px] uppercase">Estado de Higiene</span>
                  <span className={`font-bold block flex items-center gap-1.5 ${
                    sbx?.worktree_clean ? 'text-emerald-400' : 'text-amber-300'
                  }`}>
                    <ShieldCheck className="w-3.5 h-3.5" />
                    {sbx?.worktree_clean ? 'Worktree Limpio' : 'Con cambios sin confirmar'}
                  </span>
                </div>
              </div>

              <div className="pt-2 border-t border-zinc-800/80">
                <span className="text-zinc-500 text-[10px] uppercase block mb-1">
                  Ruta Física del Repositorio en Disco:
                </span>
                <code className="text-zinc-300 text-[11px] block p-2 rounded bg-zinc-950 border border-white/5 truncate" title={sbx?.worktree_path}>
                  {sbx?.worktree_path || 'worktrees/integration'}
                </code>
              </div>
            </div>
          </div>
        )}

        {/* ===================================================================
            3. ¿CUÁNDO SE ESTÁ PROCESANDO? (FSM DETERMINISTA & TIMING)
           =================================================================== */}
        {activeTab === 'timing' && (
          <div className="space-y-4 animate-fade-in text-xs font-mono">
            <div className="p-4 rounded-xl bg-black border border-white/5 space-y-3">
              <span className="text-[10px] uppercase text-zinc-400 font-bold block">
                Trazabilidad Temporal Determinista (FSM Timestamps)
              </span>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-3 rounded-xl bg-zinc-950 border border-white/5 space-y-1">
                  <span className="text-zinc-500 text-[10px] uppercase">Inicio (Started At)</span>
                  <span className="text-zinc-200 block text-[11px] truncate">
                    {timing?.started_at ? timing.started_at.replace('T', ' ').slice(0, 19) : execution.timestamp}
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-zinc-950 border border-white/5 space-y-1">
                  <span className="text-zinc-500 text-[10px] uppercase">Cierre (Completed At)</span>
                  <span className="text-zinc-200 block text-[11px] truncate">
                    {timing?.completed_at ? timing.completed_at.replace('T', ' ').slice(0, 19) : execution.timestamp}
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-zinc-950 border border-white/5 space-y-1">
                  <span className="text-zinc-500 text-[10px] uppercase">Latencia Medida</span>
                  <span className="text-emerald-400 font-bold block text-sm">
                    {timing?.latency_ms ? `${timing.latency_ms} ms` : `${execution.duration_sec * 1000} ms`}
                  </span>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-zinc-950 border border-white/5 flex items-center justify-between">
                <div>
                  <span className="text-zinc-400 text-[11px] font-bold block">
                    Umbral de Timeout Máximo:
                  </span>
                  <span className="text-zinc-500 text-[10px]">
                    Si la tarea supera este umbral sin latidos, la FSM transiciona a STALE.
                  </span>
                </div>
                <span className="px-2.5 py-1 rounded-lg bg-zinc-900 border border-zinc-800 text-amber-300 font-bold text-xs">
                  {timing?.timeout_sec || 30} segundos
                </span>
              </div>
            </div>
          </div>
        )}

        {/* ===================================================================
            4. ¿EN REALIDAD SE HIZO? (DISEÑO POR CONTRATO & POSTCONDICIÓN)
           =================================================================== */}
        {activeTab === 'post_condition' && (
          <div className="space-y-4 animate-fade-in text-xs font-mono">
            <div className="p-4 rounded-xl bg-black border border-white/5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase text-zinc-400 font-bold block">
                  Aserción de Post-Condición Inmutable
                </span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                  post?.contract_verified ? 'bg-emerald-950/40 text-emerald-400 border border-emerald-500/30' :
                  'bg-rose-950/40 text-rose-400 border border-rose-500/30'
                }`}>
                  {post?.contract_verified ? '✓ CONTRATO VERIFICADO' : '✗ DISCREPANCIA DETECTADA'}
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-zinc-950 border border-white/5 space-y-1">
                  <span className="text-zinc-500 text-[10px] uppercase">Hash SHA-256 de Post-Condición</span>
                  <span className="text-cyan-400 font-bold block flex items-center gap-1.5 truncate">
                    <Hash className="w-3.5 h-3.5" />
                    {post?.post_condition_hash || 'SHA-UNVERIFIED'}
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-zinc-950 border border-white/5 space-y-1">
                  <span className="text-zinc-500 text-[10px] uppercase">Revisión Humana Obligatoria (HITL)</span>
                  <span className={`font-bold block ${post?.hitl_required ? 'text-amber-300' : 'text-zinc-400'}`}>
                    {post?.hitl_required ? 'SÍ (Intervención Requerida)' : 'NO (Automático)'}
                  </span>
                </div>
              </div>

              {/* Raw Porcelain Snapshot */}
              <div>
                <span className="text-zinc-500 text-[10px] uppercase block mb-1">
                  Captura de git status --porcelain:
                </span>
                <pre className="p-3 rounded-xl bg-zinc-950 border border-white/5 text-[11px] text-zinc-300 overflow-x-auto max-h-32">
                  {post?.porcelain_status || '(Worktree completamente limpio - sin cambios pendientes)'}
                </pre>
              </div>
            </div>
          </div>
        )}

        {/* Toggle Raw JSON Inspector */}
        <div className="pt-2 border-t border-white/5 flex items-center justify-between text-xs font-mono">
          <button
            type="button"
            onClick={() => setShowRawJson(!showRawJson)}
            className="text-zinc-400 hover:text-white flex items-center gap-1.5 transition cursor-pointer"
          >
            <Layers className="w-3.5 h-3.5" />
            <span>{showRawJson ? 'Ocultar JSON Estructurado Completo' : 'Inspeccionar JSON Estructurado Completo'}</span>
            {showRawJson ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>

        {showRawJson && (
          <pre className="p-4 rounded-xl bg-black border border-white/5 text-[10px] font-mono text-zinc-400 overflow-x-auto max-h-64 animate-fade-in">
            {JSON.stringify(execution, null, 2)}
          </pre>
        )}
      </div>
    </div>
  )
}
