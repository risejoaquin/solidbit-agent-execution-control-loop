import React, { useState, useEffect } from 'react'
import {
  CheckSquare,
  Plus,
  RefreshCw,
  Search,
  ShieldCheck,
  AlertCircle,
  CheckCircle2,
  Sparkles,
  ChevronDown,
  X,
  Bookmark,
  Bug,
  Zap,
} from 'lucide-react'

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
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(
    null
  )

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
      setFeedback({ type: 'error', message: 'No se pudo cargar el listado de tareas.' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTickets()
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
        setFeedback({
          type: 'success',
          message: `Estado de ${ticketKey} actualizado a ${newStatus}.`,
        })
      }
    } catch (e: any) {
      setFeedback({ type: 'error', message: 'Error actualizando estado: ' + e.message })
    }
  }

  // Poka-Yoke real-time validation
  const isTitleValid = newTitle.trim().length >= 5

  const handleCreateTicket = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isTitleValid) return

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
        setFeedback({ type: 'success', message: data.message || 'Tarea creada exitosamente.' })
        setShowCreateModal(false)
        setNewKey('')
        setNewTitle('')
        setNewDesc('')
        setNewCriteria('')
        await loadTickets()
      } else {
        setFeedback({ type: 'error', message: data.error || 'Error al crear la tarea.' })
      }
    } catch (e: any) {
      setFeedback({ type: 'error', message: e.message || 'Fallo de red al crear la tarea.' })
    } finally {
      setIsSubmitting(false)
    }
  }

  const filteredTickets = tickets.filter((t) => {
    const q = searchQuery.toLowerCase()
    const matchesSearch =
      !q ||
      t.key.toLowerCase().includes(q) ||
      t.title.toLowerCase().includes(q) ||
      (t.description && t.description.toLowerCase().includes(q))

    const matchesStatus =
      statusFilter === 'ALL' ||
      (statusFilter === 'READY' && t.status === 'READY_FOR_SPRINT') ||
      (statusFilter === 'IN_PROGRESS' && t.status === 'IN_PROGRESS') ||
      (statusFilter === 'COMPLETED' && (t.status === 'COMPLETED' || t.status === 'DEPLOYED'))

    return matchesSearch && matchesStatus
  })

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

  const isJiraConnected = jiraConnection?.authenticated === true

  return (
    <div className="space-y-6 max-w-6xl mx-auto animate-fade-in text-left pb-12">
      {/* 1. Header Claro (1 CTA Primario: + Nueva Tarea) */}
      <div className="p-5 sm:p-6 rounded-2xl bg-zinc-950 border border-zinc-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-start sm:items-center gap-3.5">
          <div className="w-10 h-10 rounded-xl bg-zinc-900 border border-zinc-750 flex items-center justify-center text-white shrink-0">
            <CheckSquare className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold text-white tracking-tight">
                Backlog de Tareas y Jira
              </h2>
              <span
                className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold border ${
                  isJiraConnected
                    ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                    : 'bg-zinc-900 text-zinc-300 border-zinc-800'
                }`}
              >
                {isJiraConnected ? 'CONECTADO A JIRA CLOUD' : 'GUARDADO LOCAL EN SQLITE'}
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              Selecciona cualquier tarea para lanzar un sprint automático o registra un nuevo requerimiento.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5 self-start sm:self-auto">
          <button
            type="button"
            onClick={loadTickets}
            disabled={loading}
            className="px-3.5 py-2 rounded-xl bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-xs text-zinc-300 flex items-center gap-1.5 transition cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Actualizar</span>
          </button>

          <button
            type="button"
            id="btn-create-jira-ticket"
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 rounded-xl bg-white hover:bg-zinc-200 text-black font-bold text-xs flex items-center gap-1.5 transition shadow-sm cursor-pointer"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>+ Nueva Tarea</span>
          </button>
        </div>
      </div>

      {/* Feedback Banner */}
      {feedback && (
        <div
          className={`p-4 rounded-xl border text-xs flex items-center justify-between gap-3 ${
            feedback.type === 'success'
              ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-200'
              : 'bg-red-950/40 border-red-500/40 text-red-200'
          }`}
        >
          <div className="flex items-center gap-2.5">
            {feedback.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            )}
            <span>{feedback.message}</span>
          </div>
          <button
            type="button"
            onClick={() => setFeedback(null)}
            className="text-xs underline cursor-pointer"
          >
            Cerrar
          </button>
        </div>
      )}

      {/* 2. Filtro y Buscador */}
      <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between">
        <div className="flex items-center gap-1.5">
          {[
            { id: 'ALL', label: `Todas (${tickets.length})` },
            {
              id: 'READY',
              label: `Listas (${tickets.filter((t) => t.status === 'READY_FOR_SPRINT').length})`,
            },
            {
              id: 'IN_PROGRESS',
              label: `En Progreso (${tickets.filter((t) => t.status === 'IN_PROGRESS').length})`,
            },
            {
              id: 'COMPLETED',
              label: `Completadas (${
                tickets.filter((t) => t.status === 'COMPLETED' || t.status === 'DEPLOYED').length
              })`,
            },
          ].map((s) => (
            <button
              key={s.id}
              type="button"
              onClick={() => setStatusFilter(s.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer ${
                statusFilter === s.id
                  ? 'bg-white text-black'
                  : 'bg-zinc-900 text-zinc-400 hover:text-white border border-zinc-800'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>

        <div className="relative min-w-[240px]">
          <Search className="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Buscar tarea por código o título..."
            className="w-full pl-9 pr-4 py-1.5 rounded-xl bg-zinc-950 border border-zinc-800 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-white"
          />
        </div>
      </div>

      {/* 3. Lista de Tareas (Progressive Disclosure para descripción y criterios) */}
      <div className="space-y-3">
        {filteredTickets.length === 0 ? (
          <div className="p-8 rounded-2xl bg-zinc-950 border border-zinc-800 text-center space-y-2">
            <CheckSquare className="w-8 h-8 text-zinc-600 mx-auto" />
            <p className="text-xs text-zinc-400">No hay tareas que coincidan con este filtro.</p>
          </div>
        ) : (
          filteredTickets.map((ticket) => {
            const isExpanded = expandedTicketKey === ticket.key
            const isCompleted = ticket.status === 'COMPLETED' || ticket.status === 'DEPLOYED'

            return (
              <div
                key={ticket.key}
                className="p-4 sm:p-5 rounded-2xl bg-zinc-950 border border-zinc-800 hover:border-zinc-700 transition space-y-3"
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
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-zinc-900 text-zinc-400 border border-zinc-850">
                          Prioridad: {ticket.priority || 'MEDIUM'}
                        </span>
                      </div>
                      <h3 className="text-sm font-bold text-white mt-1">{ticket.title}</h3>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
                    <select
                      value={ticket.status}
                      onChange={(e) => handleTransitionStatus(ticket.key, e.target.value)}
                      className={`px-2.5 py-1.5 rounded-xl border text-xs font-mono cursor-pointer focus:outline-none ${
                        isCompleted
                          ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30 font-bold'
                          : 'bg-zinc-900 text-zinc-200 border-zinc-750'
                      }`}
                    >
                      <option value="READY_FOR_SPRINT">Listo para Sprint</option>
                      <option value="IN_PROGRESS">En Progreso</option>
                      <option value="COMPLETED">Completado</option>
                    </select>

                    {onLaunchSprintForTicket && (
                      <button
                        type="button"
                        onClick={() => onLaunchSprintForTicket(ticket)}
                        className="px-3.5 py-1.5 rounded-xl bg-white hover:bg-zinc-200 text-black font-bold text-xs flex items-center gap-1.5 transition shadow-sm cursor-pointer"
                      >
                        <Sparkles className="w-3.5 h-3.5 fill-black" />
                        <span>Lanzar Sprint</span>
                      </button>
                    )}

                    <button
                      type="button"
                      onClick={() => setExpandedTicketKey(isExpanded ? null : ticket.key)}
                      className="p-1.5 rounded-lg bg-zinc-900 text-zinc-400 hover:text-white transition cursor-pointer"
                      title="Ver detalles"
                    >
                      <ChevronDown
                        className={`w-4 h-4 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                      />
                    </button>
                  </div>
                </div>

                {isExpanded && (
                  <div className="pt-3 border-t border-zinc-850 space-y-3 text-xs text-zinc-300 animate-fade-in">
                    {ticket.description && (
                      <p className="text-zinc-300 leading-relaxed">{ticket.description}</p>
                    )}
                    {ticket.contracts && ticket.contracts.length > 0 && (
                      <div className="flex items-center gap-2 font-mono">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="text-zinc-400">Contratos verificados:</span>
                        {ticket.contracts.map((c) => (
                          <span
                            key={c}
                            className="px-2 py-0.5 rounded bg-zinc-900 text-white border border-zinc-700 text-[10px]"
                          >
                            {c}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })
        )}
      </div>

      {/* 4. Modal con Validación Poka-Yoke */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-fade-in text-left">
          <div className="w-full max-w-lg rounded-2xl bg-zinc-950 border border-zinc-800 p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
              <div className="flex items-center gap-2">
                <CheckSquare className="w-4 h-4 text-white" />
                <h3 className="text-sm font-bold text-white">Crear Nueva Tarea</h3>
              </div>
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="w-7 h-7 rounded-lg bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-white flex items-center justify-center transition cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleCreateTicket} className="space-y-4 text-xs">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="font-semibold text-zinc-200">
                    Título de la Tarea *
                  </label>
                  <span
                    className={`text-[11px] flex items-center gap-1 ${
                      isTitleValid ? 'text-emerald-400' : 'text-amber-400'
                    }`}
                  >
                    <CheckCircle2 className="w-3 h-3" />
                    {isTitleValid ? 'Título claro y válido' : 'Escribe al menos 5 caracteres'}
                  </span>
                </div>
                <input
                  type="text"
                  autoFocus
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  required
                  placeholder="Ej: Validar pagos sin cargos duplicados en checkout..."
                  className="w-full px-3.5 py-2.5 rounded-xl bg-black border border-zinc-700 text-white focus:outline-none focus:border-white"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-zinc-300 mb-1">
                    Código (Opcional, se genera solo)
                  </label>
                  <input
                    type="text"
                    value={newKey}
                    onChange={(e) => setNewKey(e.target.value.toUpperCase())}
                    placeholder="SOLID-110"
                    className="w-full px-3 py-2 rounded-xl bg-black border border-zinc-800 text-white font-mono focus:outline-none focus:border-white"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-zinc-300 mb-1">Prioridad</label>
                  <select
                    value={newPriority}
                    onChange={(e) => setNewPriority(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-black border border-zinc-800 text-white focus:outline-none cursor-pointer"
                  >
                    <option value="HIGH">Alta (Recomendada)</option>
                    <option value="CRITICAL">Crítica</option>
                    <option value="MEDIUM">Media</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-semibold text-zinc-300 mb-1">
                  Descripción (Opcional)
                </label>
                <textarea
                  rows={3}
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Explica brevemente qué necesitas lograr..."
                  className="w-full px-3 py-2 rounded-xl bg-black border border-zinc-800 text-white focus:outline-none focus:border-white"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-zinc-850">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-3.5 py-2 rounded-xl bg-zinc-900 text-zinc-300 hover:text-white transition cursor-pointer"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting || !isTitleValid}
                  className="px-4 py-2 rounded-xl bg-white text-black font-bold text-xs hover:bg-zinc-200 transition cursor-pointer disabled:opacity-40"
                >
                  {isSubmitting ? 'Guardando...' : 'Guardar Tarea'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
