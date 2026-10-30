export type OperationalDomainState =
  | 'UNINITIALIZED'
  | 'PLANNING'
  | 'EXECUTING'
  | 'HALTED_BY_CONFLICT'
  | 'TIMEOUT_STALE'
  | 'POST_CONDITION_FAILED'
  | 'AWAITING_APPROVAL'
  | 'COMPLETED'

export interface DomainStateMeta {
  state: OperationalDomainState
  badgeLabel: string
  badgeVariant: 'zinc' | 'blue' | 'emerald' | 'amber' | 'red'
  title: string
  subtitle: string
  canLaunchNewSprint: boolean
  primaryActionLabel: string
}

export interface DomainStateContext {
  projectsCount: number
  isPlanning: boolean
  isExecuting: boolean
  hasConflict: boolean
  conflictReason?: string | null
  pendingGatesCount: number
  recentlyCompleted?: boolean
  isStaleTimeout?: boolean
  postConditionFailed?: boolean
  postConditionReason?: string | null
}

/**
 * Deterministic Finite State Machine derivation: UI = f(DomainState)
 * Priority order guarantees Invariant 1 (Coherencia de Estado):
 * It is mathematically impossible for the Header or Dashboard to show "Sistema Listo"
 * while a conflict, timeout, failed post-condition, or pending approval gate is active.
 */
export function deriveDomainState(ctx: DomainStateContext): DomainStateMeta {
  if (ctx.projectsCount === 0) {
    return {
      state: 'UNINITIALIZED',
      badgeLabel: 'Paso Inicial: Vincular Proyecto',
      badgeVariant: 'zinc',
      title: 'Ningún proyecto vinculado todavía',
      subtitle: 'Importa la carpeta de tu proyecto para activar el flujo de trabajo.',
      canLaunchNewSprint: false,
      primaryActionLabel: 'Vincular Carpeta de Proyecto',
    }
  }

  // 1. Post-condition assertion check (Design by Contract)
  if (ctx.postConditionFailed) {
    return {
      state: 'POST_CONDITION_FAILED',
      badgeLabel: 'Postcondición No Cumplida (Fallo de Contrato)',
      badgeVariant: 'red',
      title: 'Discrepancia detectada entre el contrato de la tarea y el repositorio',
      subtitle:
        ctx.postConditionReason ||
        'El estado en disco o las verificaciones post-ejecución no coinciden con el hash esperado. Se requiere intervención manual.',
      canLaunchNewSprint: false,
      primaryActionLabel: 'Auditar Estado del Repositorio y Reconciliar',
    }
  }

  // 2. Hardware conflict / git collision
  if (ctx.hasConflict) {
    return {
      state: 'HALTED_BY_CONFLICT',
      badgeLabel: 'Flujo Pausado por Inconsistencia',
      badgeVariant: 'red',
      title: 'Ejecución detenida preventivamente para proteger tus archivos',
      subtitle:
        ctx.conflictReason ||
        'Se detectó una diferencia o fallo en la verificación. Resuélvelo con un clic para reanudar.',
      canLaunchNewSprint: false,
      primaryActionLabel: 'Restaurar Estado Seguro y Continuar',
    }
  }

  // 3. Timeout / Stale State (Exceeded execution threshold without heartbeat)
  if (ctx.isStaleTimeout) {
    return {
      state: 'TIMEOUT_STALE',
      badgeLabel: 'Alerta: Tarea Expirada / Stale State',
      badgeVariant: 'amber',
      title: 'La tarea superó el umbral de tiempo esperado sin latidos de vida',
      subtitle:
        'El subproceso no emitió confirmación dentro del tiempo límite (30s). Revisa el estado del entorno o fuerza su reactivación.',
      canLaunchNewSprint: false,
      primaryActionLabel: 'Forzar Reanudación / Reiniciar Subproceso',
    }
  }

  if (ctx.isExecuting) {
    return {
      state: 'EXECUTING',
      badgeLabel: 'Ejecutando Plan de Trabajo...',
      badgeVariant: 'blue',
      title: 'El equipo de asistentes está ejecutando las pruebas y cambios',
      subtitle: 'Espera unos segundos mientras se completan las verificaciones en tiempo real.',
      canLaunchNewSprint: false,
      primaryActionLabel: 'Ejecución en Curso...',
    }
  }

  if (ctx.pendingGatesCount > 0) {
    return {
      state: 'AWAITING_APPROVAL',
      badgeLabel: `Esperando tu Aprobación (${ctx.pendingGatesCount})`,
      badgeVariant: 'amber',
      title: 'Cambios verificados esperando tu autorización',
      subtitle:
        'El lanzamiento de nuevas tareas está en pausa hasta que autorices o rechaces la entrega pendiente.',
      canLaunchNewSprint: false,
      primaryActionLabel: 'Autorizar e Integrar Entrega',
    }
  }

  if (ctx.isPlanning) {
    return {
      state: 'PLANNING',
      badgeLabel: 'Diseñando Plan de Trabajo',
      badgeVariant: 'blue',
      title: 'Configurando el alcance de la nueva entrega',
      subtitle: 'Define el objetivo de negocio antes de iniciar la ejecución.',
      canLaunchNewSprint: false,
      primaryActionLabel: 'Confirmar y Ejecutar Plan',
    }
  }

  return {
    state: 'COMPLETED',
    badgeLabel: ctx.recentlyCompleted
      ? 'Entrega Integrada · Listo para Planificar'
      : 'Sistema Verificado · Listo para Planificar',
    badgeVariant: 'emerald',
    title: ctx.recentlyCompleted
      ? 'Última entrega autorizada e integrada con éxito'
      : 'Tu proyecto está verificado y al día',
    subtitle:
      'Todas las reglas de negocio están protegidas. Puedes iniciar un nuevo sprint cuando lo necesites.',
    canLaunchNewSprint: true,
    primaryActionLabel: 'Planificar Nuevo Sprint',
  }
}
