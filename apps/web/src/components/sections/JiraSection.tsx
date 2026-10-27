import React, { useState, useEffect } from 'react'
import {
  CheckSquare,
  Plus,
  RefreshCw,
  Search,
  Filter,
  ExternalLink,
  ShieldCheck,
  AlertCircle,
  CheckCircle2,
  Clock,
  Layers,
  Sparkles,
  ChevronRight,
  ChevronDown,
  X,
  Tag,
  Bookmark,
  Bug,
  Zap,
  ArrowRight,
} from 'lucide-react'
import { formatSmartDateTime } from '../../utils/dateFormat'

export interface JiraTicket {
  key: string
  title: string
  phase?: string
  contracts?: string[]
  status: string
  description?: string
  priority?: string
  epic?: string
  source?: string
  created_at?: string
  updated_at?: string
  acceptance_criteria?: string[]
  issue_type?: string
}

interface JiraSectionProps {
  onLaunchSprintForTicket?: (ticket: JiraTicket) => void
}

export const JiraSection: React.FC<JiraSectionProps> = ({ onLaunchSprintForTicket }) => {
  const [tickets, setTickets] = useState<JiraTicket[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [jiraConnection, setJiraConnection] = useState<any>(null)
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('ALL')
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL')
  const [expandedTicketKey, setExpandedTicketKey] = useState<string | null>(null)

  // Create ticket modal
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false)
  const [newKey, setNewKey] = useState<string>('')
  const [newTitle, setNewTitle] = useState<string>('')
  const [newDesc, setNewDesc] = useState<string>('')
  const [newPriority, setNewPriority] = useState<string>('HIGH')
  const [newType, setNewType] = useState<string>('Story')
  const [newCriteria, setNewCriteria] = useState<string>('')
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null)

  const loadTickets = async () => {
    try {
      setLoading(true)
      const res = await fetch('/api/jira/tickets')
      if (res.ok) {
        const data = await res.json()
        if (data.tickets) setTickets(data.tickets)
        if (data.connection) setJiraConnection(data.connection)
      }
    } catch (e: any) {
      console.warn('Error cargando tickets Jira:', e)
      setFeedback({ type: 'error', message: 'No se pudo conectar con el servicio Jira' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTickets()

    // Real-time SSE updates
    try {
      const sse = new EventSource('/api/events/stream')
      sse.addEventListener('jira_ticket_created', () => loadTickets())
      sse.addEventListener('jira_ticket_transitioned', () => loadTickets())
      return () => sse.close()
    } catch {}
  }, [])

  const handleTransitionStatus = async (ticketKey: string, newStatus: string) => {
    try {
      const res = await fetch('/api/jira/transition', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticket_key: ticketKey, status: newStatus }),
      })
      if (res.ok) {
        setTickets((prev) =>
          prev.map((t) => (t.key === ticketKey ? { ...t, status: newStatus } : t))
        )
      }
    } catch (e: any) {
      alert('Error transicionando ticket: ' + e.message)
    }
  }

  const handleCreateTicket = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newTitle.trim()) return

    setIsSubmitting(true)
    setFeedback(null)
    try {
      const criteriaList = newCriteria
        .split('\n')
        .map((s) => s.trim())
        .filter(Boolean)

      const payload = {
        key: newKey.trim() || undefined,
        title: newTitle.trim(),
        description: newDesc.trim(),
        priority: newPriority,
        issue_type: newType,
        acceptance_criteria: criteriaList,
        contracts: ['DR-IDEM-001'],
      }

      const res = await fetch('/api/jira/tickets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const data = await res.json()
      if (data.success) {
        setFeedback({ type: 'success', message: data.message || 'Ticket creado exitosamente.' })
        setShowCreateModal(false)
        setNewKey('')
        setNewTitle('')
        setNewDesc('')
        setNewCriteria('')
        await loadTickets()
      } else {
        setFeedback({ type: 'error', message: data.error || 'Error al crear ticket Jira.' })
      }
    } catch (e: any) {
      setFeedback({ type: 'error', message: e.message || 'Fallo de red al crear ticket.' })
    } finally {
      setIsSubmitting(false)
    }
  }

  // Filter logic
  const filteredTickets = tickets.filter((t) => {
    const q = searchQuery.toLowerCase()
    const matchesSearch =
      !q ||
      t.key.toLowerCase().includes(q) ||
      t.title.toLowerCase().includes(q) ||
      (t.description && t.description.toLowerCase().includes(q)) ||
      (t.epic && t.epic.toLowerCase().includes(q))

    const matchesStatus =
      statusFilter === 'ALL' ||
      (statusFilter === 'READY' && t.status === 'READY_FOR_SPRINT') ||
      (statusFilter === 'IN_PROGRESS' && t.status === 'IN_PROGRESS') ||
      (statusFilter === 'COMPLETED' && (t.status === 'COMPLETED' || t.status === 'DEPLOYED')) ||
      (statusFilter === 'BACKLOG' && (t.status === 'BACKLOG' || t.status === 'PLANNED'))

    const matchesPriority =
      priorityFilter === 'ALL' ||
      (priorityFilter === 'HIGH' && (t.priority === 'HIGH' || t.priority === 'CRITICAL')) ||
      (priorityFilter === 'MEDIUM' && t.priority === 'MEDIUM') ||
      (priorityFilter === 'LOW' && t.priority === 'LOW')

    return matchesSearch && matchesStatus && matchesPriority
  })

  // KPIs
  const totalCount = tickets.length
  const readyCount = tickets.filter((t) => t.status === 'READY_FOR_SPRINT').length
  const inProgressCount = tickets.filter((t) => t.status === 'IN_PROGRESS').length
  const completedCount = tickets.filter((t) => t.status === 'COMPLETED' || t.status === 'DEPLOYED').length

  const getTypeIcon = (type?: string) => {
    switch (type?.toLowerCase()) {
      case 'bug':
        return <Bug className="w-3.5 h-3.5 text-zinc-300" />
      case 'epic':
        return <Zap className="w-3.5 h-3.5 text-zinc-300" />
      default:
        return <Bookmark className="w-3.5 h-3.5 text-white" />
    }
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto animate-fade-in text-left">
      {/* Header Banner */}
      <div className="p-6 rounded-3xl bg-zinc-950 border border-zinc-800 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-2xl">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-zinc-900 border border-zinc-750 flex items-center justify-center text-white">
              <CheckSquare className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white tracking-tight">
                  Jira Cloud & Backlog de Requerimientos
                </h2>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-zinc-900 text-zinc-300 border border-zinc-750">
                  ATLASSIAN JIRA SDLC
                </span>
              </div>
              <p className="text-xs text-zinc-400">
                Gestión formal de historias de usuario, bugs y criterios BDD (Given / When / Then) bajo la normativa SolidBit.
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            type="button"
            onClick={loadTickets}
            disabled={loading}
            className="px-3.5 py-2 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-xs text-zinc-300 hover:text-white flex items-center gap-2 transition cursor-pointer"
            title="Sincronizar backlog"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Sincronizar</span>
          </button>

          <button
            type="button"
            id="btn-create-jira-ticket"
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 rounded-xl bg-white hover:bg-zinc-200 text-black font-bold text-xs flex items-center gap-2 transition shadow-sm cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>+ Nuevo Ticket Jira</span>
          </button>
        </div>
      </div>

      {/* Connection Status Card */}
      <div className="p-4 rounded-2xl bg-zinc-950 border border-zinc-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2.5">
          <span className="w-2 h-2 rounded-full bg-white animate-pulse" />
          <span className="font-bold text-white">Estado de Integración Atlassian:</span>
          <span className="text-zinc-400 font-mono">
            {jiraConnection?.message || 'Inspeccionando credenciales locales de Jira...'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-[10px] font-mono text-zinc-300">
            Modo: {jiraConnection?.mode || 'Soberano Local'}
          </span>
          <span className="px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-[10px] font-mono text-zinc-300">
            CLI: {jiraConnection?.cli_installed ? 'Instalado' : 'No detectado'}
          </span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
        <div className="p-4 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-1">
          <div className="text-[11px] font-mono text-zinc-500 uppercase">Total Tickets</div>
          <div className="text-2xl font-bold text-white font-mono">{totalCount}</div>
          <div className="text-[10px] text-zinc-400">Backlog unificado</div>
        </div>
        <div className="p-4 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-1">
          <div className="text-[11px] font-mono text-zinc-500 uppercase">Listos para Sprint</div>
          <div className="text-2xl font-bold text-white font-mono">{readyCount}</div>
          <div className="text-[10px] text-zinc-400">Criterios DoR cumplidos</div>
        </div>
        <div className="p-4 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-1">
          <div className="text-[11px] font-mono text-zinc-500 uppercase">En Progreso</div>
          <div className="text-2xl font-bold text-zinc-200 font-mono">{inProgressCount}</div>
          <div className="text-[10px] text-zinc-400">Asignados a oleadas</div>
        </div>
        <div className="p-4 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-1">
          <div className="text-[11px] font-mono text-zinc-500 uppercase">Completados</div>
          <div className="text-2xl font-bold text-white font-mono">{completedCount}</div>
          <div className="text-[10px] text-zinc-400">Verificados con tests</div>
        </div>
      </div>

      {/* Feedback Banner */}
      {feedback && (
        <div
          className={`p-4 rounded-2xl border text-xs flex items-center justify-between gap-3 ${
            feedback.type === 'success'
              ? 'bg-zinc-900 border-zinc-700 text-white'
              : 'bg-zinc-900 border-zinc-700 text-zinc-300'
          }`}
        >
          <div className="flex items-center gap-2.5">
            {feedback.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-white shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-zinc-400 shrink-0" />
            )}
            <span>{feedback.message}</span>
          </div>
          <button
            type="button"
            onClick={() => setFeedback(null)}
            className="text-zinc-500 hover:text-white font-mono text-xs px-2 py-1"
          >
            Cerrar
          </button>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-2xl bg-zinc-950 border border-zinc-800 flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-zinc-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Buscar por clave (SE-101), título, épica o descripción..."
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-zinc-900 border border-zinc-800 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-zinc-500 font-mono"
          />
        </div>

        <div className="flex items-center gap-2 overflow-x-auto custom-scroll pb-1 md:pb-0">
          <div className="flex items-center gap-1 bg-zinc-900 p-1 rounded-xl border border-zinc-800 text-xs font-mono">
            {['ALL', 'READY', 'IN_PROGRESS', 'COMPLETED'].map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => setStatusFilter(s)}
                className={`px-2.5 py-1 rounded-lg transition cursor-pointer ${
                  statusFilter === s
                    ? 'bg-white text-black font-bold'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                {s === 'ALL' ? 'Todos' : s === 'READY' ? 'Listos' : s === 'IN_PROGRESS' ? 'Progreso' : 'Cerrados'}
              </button>
            ))}
          </div>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-3 py-2 rounded-xl bg-zinc-900 border border-zinc-800 text-xs text-zinc-300 font-mono focus:outline-none focus:border-zinc-500 cursor-pointer"
          >
            <option value="ALL">Prioridad: Todas</option>
            <option value="HIGH">Crítica / Alta</option>
            <option value="MEDIUM">Media</option>
            <option value="LOW">Baja</option>
          </select>
        </div>
      </div>

      {/* Tickets List */}
      <div className="space-y-3">
        {filteredTickets.length === 0 ? (
          <div className="p-8 rounded-3xl bg-zinc-950 border border-zinc-800 text-center space-y-2">
            <CheckSquare className="w-8 h-8 text-zinc-600 mx-auto" />
            <p className="text-xs text-zinc-400">No se encontraron tickets con los filtros aplicados.</p>
            <p className="text-[11px] text-zinc-600">
              Usa el botón "+ Nuevo Ticket Jira" para registrar una historia o sincroniza con Atlassian CLI.
            </p>
          </div>
        ) : (
          filteredTickets.map((ticket) => {
            const isExpanded = expandedTicketKey === ticket.key
            const isCompleted = ticket.status === 'COMPLETED' || ticket.status === 'DEPLOYED'
            const isInProgress = ticket.status === 'IN_PROGRESS'

            return (
              <div
                key={ticket.key}
                className="p-5 rounded-2xl bg-zinc-950 border border-zinc-800 hover:border-zinc-700 transition space-y-3"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-start sm:items-center gap-3">
                    <div className="p-2 rounded-xl bg-zinc-900 border border-zinc-800 shrink-0">
                      {getTypeIcon(ticket.issue_type)}
                    </div>
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-xs font-mono font-bold text-white">
                          {ticket.key}
                        </span>
                        {ticket.epic && (
                          <span className="px-1.5 py-0.2 rounded bg-zinc-900 text-zinc-400 text-[10px] font-mono border border-zinc-850">
                            {ticket.epic}
                          </span>
                        )}
                        <span
                          className={`px-1.5 py-0.2 rounded text-[10px] font-mono font-semibold ${
                            ticket.priority === 'CRITICAL' || ticket.priority === 'HIGH'
                              ? 'bg-zinc-900 text-white border border-zinc-700'
                              : 'bg-zinc-900 text-zinc-400 border border-zinc-850'
                          }`}
                        >
                          {ticket.priority || 'MEDIUM'}
                        </span>
                      </div>
                      <h3 className="text-sm font-bold text-white mt-1">{ticket.title}</h3>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
                    {/* Status Pill */}
                    <span
                      className={`px-2.5 py-1 rounded-xl text-xs font-mono font-bold border ${
                        isCompleted
                          ? 'bg-zinc-900 text-white border-zinc-700'
                          : isInProgress
                          ? 'bg-zinc-900 text-zinc-200 border-zinc-750'
                          : 'bg-zinc-900 text-zinc-400 border-zinc-850'
                      }`}
                    >
                      {ticket.status}
                    </span>

                    {/* Transition Dropdown */}
                    <select
                      value={ticket.status}
                      onChange={(e) => handleTransitionStatus(ticket.key, e.target.value)}
                      className="px-2 py-1 rounded-lg bg-zinc-900 border border-zinc-800 text-[11px] font-mono text-zinc-300 focus:outline-none cursor-pointer"
                      title="Cambiar estado del ticket"
                    >
                      <option value="BACKLOG">Mover: Backlog</option>
                      <option value="READY_FOR_SPRINT">Mover: Listo para Sprint</option>
                      <option value="IN_PROGRESS">Mover: En Progreso</option>
                      <option value="COMPLETED">Mover: Completado</option>
                    </select>

                    {/* Plan Sprint Button */}
                    {onLaunchSprintForTicket && (
                      <button
                        type="button"
                        onClick={() => onLaunchSprintForTicket(ticket)}
                        className="px-3 py-1.5 rounded-xl bg-white hover:bg-zinc-200 text-black font-bold text-xs flex items-center gap-1.5 transition shadow-sm cursor-pointer"
                        title="Abrir Sprint Studio para este ticket"
                      >
                        <Sparkles className="w-3.5 h-3.5 fill-black" />
                        <span className="hidden md:inline">Planificar Sprint</span>
                        <span className="md:hidden">Sprint</span>
                      </button>
                    )}

                    {/* Expand Details Trigger */}
                    <button
                      type="button"
                      onClick={() => setExpandedTicketKey(isExpanded ? null : ticket.key)}
                      className="p-1.5 rounded-lg bg-zinc-900 text-zinc-400 hover:text-white transition cursor-pointer"
                      title="Ver criterios BDD y descripción"
                    >
                      <ChevronDown
                        className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                      />
                    </button>
                  </div>
                </div>

                {/* Expanded Details: BDD Criteria & Description */}
                {isExpanded && (
                  <div className="pt-3 border-t border-zinc-850 space-y-3 text-xs text-zinc-300 animate-fade-in font-mono">
                    {ticket.description && (
                      <div>
                        <span className="text-[11px] text-zinc-500 uppercase block mb-1">
                          Descripción / Especificación:
                        </span>
                        <p className="text-zinc-300 font-sans leading-relaxed">{ticket.description}</p>
                      </div>
                    )}

                    {ticket.contracts && ticket.contracts.length > 0 && (
                      <div className="flex items-center gap-2">
                        <span className="text-[11px] text-zinc-500 uppercase">Contratos Enlazados:</span>
                        <div className="flex items-center gap-1.5">
                          {ticket.contracts.map((c) => (
                            <span
                              key={c}
                              className="px-1.5 py-0.2 rounded bg-zinc-900 text-white border border-zinc-700 text-[10px]"
                            >
                              {c}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Given / When / Then BDD Acceptance Criteria */}
                    <div className="p-3.5 rounded-xl bg-zinc-900/60 border border-zinc-800 space-y-2">
                      <div className="text-[11px] font-bold text-white flex items-center gap-1.5">
                        <ShieldCheck className="w-3.5 h-3.5 text-white" /> Criterios de Aceptación BDD (DoD)
                      </div>
                      {ticket.acceptance_criteria && ticket.acceptance_criteria.length > 0 ? (
                        <ul className="list-disc list-inside space-y-1 text-zinc-300 font-sans text-xs">
                          {ticket.acceptance_criteria.map((cr, idx) => (
                            <li key={idx}>{cr}</li>
                          ))}
                        </ul>
                      ) : (
                        <div className="text-[11px] text-zinc-500 font-sans">
                          <strong>GIVEN:</strong> El estado canónico de SQLite WAL está consistente.<br />
                          <strong>WHEN:</strong> El agente ejecute las pruebas unitarias y de integración.<br />
                          <strong>THEN:</strong> El exit code debe ser 0 y ningún contrato congelado debe ser mutado.
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )
          })
        )}
      </div>

      {/* Modal: Crear Ticket Jira */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in text-left">
          <div className="w-full max-w-lg rounded-3xl bg-zinc-950 border border-zinc-800 p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <div className="flex items-center gap-2">
                <CheckSquare className="w-4 h-4 text-white" />
                <h3 className="text-sm font-bold text-white">Registrar Requerimiento / Ticket Jira</h3>
              </div>
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="w-7 h-7 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-white flex items-center justify-center transition cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateTicket} className="space-y-3.5 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-zinc-300 mb-1">
                    Clave Jira (Opcional)
                  </label>
                  <input
                    type="text"
                    value={newKey}
                    onChange={(e) => setNewKey(e.target.value)}
                    placeholder="SE-105"
                    className="w-full px-3 py-2 rounded-xl bg-zinc-900 border border-zinc-800 text-white font-mono focus:outline-none focus:border-zinc-500"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-zinc-300 mb-1">
                    Tipo de Incidencia
                  </label>
                  <select
                    value={newType}
                    onChange={(e) => setNewType(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-zinc-900 border border-zinc-800 text-white font-mono focus:outline-none focus:border-zinc-500 cursor-pointer"
                  >
                    <option value="Story">Historia de Usuario</option>
                    <option value="Bug">Defecto / Bug</option>
                    <option value="Task">Tarea Técnica</option>
                    <option value="Epic">Épica</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-zinc-300 mb-1">
                  Título del Requerimiento *
                </label>
                <input
                  type="text"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  required
                  placeholder="Implementar sincronización atómica de inventario..."
                  className="w-full px-3 py-2 rounded-xl bg-zinc-900 border border-zinc-800 text-white focus:outline-none focus:border-zinc-500"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-zinc-300 mb-1">
                  Descripción y Contexto de Negocio
                </label>
                <textarea
                  rows={3}
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Detalla el alcance y la necesidad operativa..."
                  className="w-full px-3 py-2 rounded-xl bg-zinc-900 border border-zinc-800 text-white focus:outline-none focus:border-zinc-500 custom-scroll font-sans"
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-zinc-300 mb-1">
                  Criterios de Aceptación BDD (un criterio por línea)
                </label>
                <textarea
                  rows={2}
                  value={newCriteria}
                  onChange={(e) => setNewCriteria(e.target.value)}
                  placeholder="GIVEN un carrito con 2 ítems&#10;WHEN se complete el pago&#10;THEN se decrementa el stock atómicamente"
                  className="w-full px-3 py-2 rounded-xl bg-zinc-900 border border-zinc-800 text-white focus:outline-none focus:border-zinc-500 custom-scroll font-mono text-[11px]"
                />
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-zinc-800">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-3.5 py-1.5 rounded-xl bg-zinc-900 text-zinc-400 hover:text-white transition"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 rounded-xl bg-white text-black font-bold text-xs hover:bg-zinc-200 transition cursor-pointer disabled:opacity-50"
                >
                  {isSubmitting ? 'Registrando...' : 'Registrar en Backlog'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
