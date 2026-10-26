export interface Project {
  id: string
  name: string
  path: string
  description?: string
  tech_stack?: string[]
  status?: string
  readiness?: number
  is_active?: boolean
}

export interface TaskItem {
  id: string
  title: string
  key: string
  agent: string
  role?: string
  start: string
  end: string
  progress: number
  status: 'Completada' | 'En progreso' | 'Pendiente' | 'Bloqueada'
  contracts?: string[]
}

export interface AgentItem {
  id: string
  name: string
  role: string
  status: 'Activo' | 'En espera' | 'Inactivo'
  color: 'emerald' | 'blue' | 'amber' | 'zinc'
  icon: string
  pid?: number
}

export interface CommitItem {
  sha: string
  author: string
  time: string
  message: string
}

export interface ActivityEvent {
  event_id: number
  event_type: string
  severity: 'INFO' | 'WARN' | 'FATAL' | 'ERROR'
  created_at: string
  payload_json?: string
  run_id?: string
}

export interface NotificationItem {
  id: string
  title: string
  message: string
  type: 'gate' | 'success' | 'info' | 'warning'
  time: string
  actionUrl?: string
}

export interface OrchestratorContext {
  active_project?: {
    name: string
    path: string
    branch: string
    commit: string
    is_clean: boolean
    status: string
  }
  available_projects?: Project[]
  jira_backlog?: any[]
  active_plan?: any
  jira_connection?: {
    authenticated: boolean
    cli_installed: boolean
    status: string
    message: string
  }
}
