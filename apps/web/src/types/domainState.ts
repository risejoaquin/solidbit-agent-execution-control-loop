export type OperationalDomainState =
  | 'UNINITIALIZED'
  | 'PLANNING'
  | 'EXECUTING'
  | 'HALTED_BY_CONFLICT'
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
}

/**
 * Deterministic Finite State Machine derivation: UI = f(DomainState)
 * Priority order guarantees Invariant 1 (Coherencia de Estado):
 * It is mathematically impossible for the Header or Dashboard to show "Sistema Listo"
 * while a conflict or pending approval gate is active.
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
