/**
 * Strict Typed Contracts for SolidBit Orchestrator (CQRS & Event-Driven State)
 * Implements 4 foundational dimensions:
 * 1. ¿Qué se procesa? (Contrato CQRS / Payload Observable)
 * 2. ¿Dónde se procesa? (Aislamiento de Entorno / Sandbox Context Injection)
 * 3. ¿Cuándo se procesa? (FSM Determinista / Timing & Latency Deltas)
 * 4. ¿En realidad se hizo? (Verificación Inmutable / Post-Condition Hash & Porcelain Check)
 */

export interface MutatedFileItem {
  status: string // e.g. "M", "A", "D", "??"
  path: string
  diff_stat?: string
}

export interface TaskExecutionEvent {
  event_id: string
  action_type: string
  input_payload: {
    action_type: string
    params: Record<string, any>
    intent: string
    target_files?: string[]
  }
  executed_command: {
    binary: string
    args: string[]
    cwd: string
    env_signature?: string
  }
  partial_result: {
    exit_code: number
    status: 'COMPLETED' | 'FAILED' | 'PENDING' | 'EXECUTING' | 'TIMEOUT_STALE' | string
    mutated_files: MutatedFileItem[]
    summary: string
    stdout_snippet?: string
    stderr_snippet?: string
  }
  timestamp: string
}

export interface SandboxContext {
  sandbox_id: string
  git_branch: string
  worktree_path: string
  commit_sha: string
  worktree_clean: boolean
  is_isolated: boolean
  verified: boolean
  mismatch_warning?: string | null
}

export interface FSMTiming {
  started_at: string
  completed_at?: string
  latency_ms: number
  timeout_sec: number
  is_stale: boolean
  heartbeat_at?: string
}

export interface PostConditionVerification {
  evaluated: boolean
  status: 'PASS' | 'POST_CONDITION_FAILED' | string
  porcelain_status: string
  post_condition_hash: string
  contract_verified: boolean
  hitl_required: boolean
  mismatch_reason?: string
}

export interface VerifiableExecutionResult {
  success: boolean
  execution_id: string
  action_type: string
  title: string
  status: string
  exit_code: number
  duration_sec: number
  timestamp: string
  summary: string
  steps?: Array<{
    name: string
    status: string
    duration: string
    command?: string
  }>
  logs?: string[]
  sandbox_context?: SandboxContext
  fsm_timing?: FSMTiming
  execution_event?: TaskExecutionEvent
  post_condition?: PostConditionVerification
  raw_output?: string
}
