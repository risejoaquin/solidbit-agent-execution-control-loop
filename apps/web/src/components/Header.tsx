import React, { useState, useEffect, useRef } from 'react'
import { formatSmartDateTime, formatRelativeTime } from '../utils/dateFormat'
import {
  Bell,
  ShieldAlert,
  CheckCircle2,
  Info,
  Terminal,
  Sparkles,
  User,
  Save,
  X,
  Key,
  Menu,
  GitBranch,
  CheckSquare,
  Search,
  SlidersHorizontal,
} from 'lucide-react'
import type { NotificationItem } from '../types/orchestrator'

interface HeaderProps {
  projectName: string
  onOpenSprintModal: () => void
  onNavigateSection: (section: string) => void
  onToggleMobileMenu?: () => void
  onOpenDiffModal?: () => void
  onOpenCommandPalette?: () => void
}

export const Header: React.FC<HeaderProps> = ({
  projectName,
  onOpenSprintModal,
  onNavigateSection,
  onToggleMobileMenu,
  onOpenDiffModal,
  onOpenCommandPalette,
}) => {
  const [clock, setClock] = useState<string>('')
  const [showNotifications, setShowNotifications] = useState<boolean>(false)
  const [showProfileModal, setShowProfileModal] = useState<boolean>(false)
  const [density, setDensity] = useState<'compact' | 'default' | 'comfortable'>(
    (localStorage.getItem('sacl_ui_density') as any) || 'default'
  )

  const handleDensityChange = (newDensity: 'compact' | 'default' | 'comfortable') => {
    setDensity(newDensity)
    localStorage.setItem('sacl_ui_density', newDensity)
    document.documentElement.setAttribute('data-density', newDensity)
  }

  useEffect(() => {
    document.documentElement.setAttribute('data-density', density)
  }, [density])

  // Sovereign Operator State
  const [operatorName, setOperatorName] = useState<string>(
    localStorage.getItem('sacl_operator_name') || 'Joaquin Vallejo'
  )
  const [operatorRole, setOperatorRole] = useState<string>(
    localStorage.getItem('sacl_operator_role') || 'Owner'
  )
  const [operatorEmail, setOperatorEmail] = useState<string>('risejoaquin@solidbit.io')
  const [savingProfile, setSavingProfile] = useState<boolean>(false)

  const [notifications, setNotifications] = useState<NotificationItem[]>([])
  const [dismissedNotifIds, setDismissedNotifIds] = useState<Set<string>>(() => {
    try {
      const stored = sessionStorage.getItem('sacl_dismissed_notifs')
      return new Set(stored ? JSON.parse(stored) : [])
    } catch {
      return new Set()
    }
  })

  const popoverRef = useRef<HTMLDivElement>(null)
  const profileRef = useRef<HTMLDivElement>(null)

  // Live ticking clock with local time
  useEffect(() => {
    const updateTime = () => {
      const now = new Date()
      const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
      const day = now.getDate()
      const month = months[now.getMonth()]
      const year = now.getFullYear()
      const hours = String(now.getHours()).padStart(2, '0')
      const minutes = String(now.getMinutes()).padStart(2, '0')
      const seconds = String(now.getSeconds()).padStart(2, '0')
      setClock(`${day} ${month} ${year} ${hours}:${minutes}:${seconds}`)
    }
    updateTime()
    const timer = setInterval(updateTime, 1000)
    return () => clearInterval(timer)
  }, [])

  // Load real operator profile and genuine notifications from backend
  const loadNotifications = async () => {
    try {
      const items: NotificationItem[] = []

      // 1. Genuine pending HITL gates from backend
      try {
        const gatesRes = await fetch('/api/gates/pending')
        if (gatesRes.ok) {
          const gatesData = await gatesRes.json()
          const list = gatesData.pending_gates || gatesData.gates || []
          for (const g of list) {
            const notifId = `gate-${g.id || g.request_id}`
            if (!dismissedNotifIds.has(notifId)) {
              items.push({
                id: notifId,
                title: 'Compuerta HITL Pendiente',
                message: `${g.request_id || g.id}: ${g.reason || g.action || 'Firma soberana requerida'}`,
                type: 'gate',
                time: formatRelativeTime(g.created_at || g.timestamp),
                actionUrl: 'executions',
              })
            }
          }
        }
      } catch {}

      // 2. Real SQLite events from local database
      try {
        const evRes = await fetch('/api/db/rows?table=events&limit=6')
        if (evRes.ok) {
          const evData = await evRes.json()
          if (evData.rows && Array.isArray(evData.rows)) {
            for (const ev of evData.rows) {
              const notifId = `ev-${ev.event_id}`
              if (!dismissedNotifIds.has(notifId)) {
                items.push({
                  id: notifId,
                  title: `Evento SQLite: ${ev.event_type}`,
                  message: ev.severity ? `[${ev.severity}] ${ev.run_id || 'Sistema'}` : (ev.run_id || 'Operación duradera'),
                  type: ev.severity === 'FATAL' || ev.severity === 'ERROR' ? 'gate' : 'info',
                  time: formatRelativeTime(ev.created_at),
                  actionUrl: 'database',
                })
              }
            }
          }
        }
      } catch {}

      setNotifications(items)
    } catch (e) {
      console.warn('Error loading real notifications:', e)
    }
  }

  useEffect(() => {
    fetch('/api/settings/profile')
      .then((r) => r.json())
      .then((d) => {
        if (d.profile?.name) {
          setOperatorName(d.profile.name)
          setOperatorRole(d.profile.role?.includes('Owner') ? 'Owner' : d.profile.role)
          if (d.profile.email) setOperatorEmail(d.profile.email)
        }
      })
      .catch(() => {})

    loadNotifications()

    // Subscribe to SSE events for real-time notifications
    try {
      const sse = new EventSource('/api/events/stream')
      sse.addEventListener('gate', (e: MessageEvent) => {
        try {
          const payload = JSON.parse(e.data)
          const newId = `gate-${payload.request_id || payload.id || Date.now()}`
          setNotifications((prev) => [
            {
              id: newId,
              title: 'Nueva Compuerta HITL',
              message: payload.reason || payload.action || 'Firma HMAC requerida.',
              type: 'gate',
              time: 'Ahora',
              actionUrl: 'executions',
            },
            ...prev.filter((p) => p.id !== newId),
          ])
        } catch {
          loadNotifications()
        }
      })
      sse.addEventListener('sprint_executed', () => {
        setNotifications((prev) => [
          {
            id: `exec-${Date.now()}`,
            title: 'Oleadas Ejecutadas',
            message: 'Entregables físicos generados en disco en SQLite WAL.',
            type: 'success',
            time: 'Ahora',
            actionUrl: 'executions',
          },
          ...prev,
        ])
      })
      sse.addEventListener('job', () => loadNotifications())
      return () => sse.close()
    } catch {
      // ignore
    }
  }, [dismissedNotifIds])

  // Close modals on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        setShowNotifications(false)
      }
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) {
        setShowProfileModal(false)
      }
    }
    if (showNotifications || showProfileModal) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [showNotifications, showProfileModal])

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setSavingProfile(true)
    try {
      const res = await fetch('/api/settings/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: operatorName,
          role: operatorRole,
          email: operatorEmail,
        }),
      })
      if (res.ok) {
        localStorage.setItem('sacl_operator_name', operatorName)
        localStorage.setItem('sacl_operator_role', operatorRole)
        setShowProfileModal(false)
      }
    } catch (err: any) {
      alert('Error guardando perfil: ' + err.message)
    } finally {
      setSavingProfile(false)
    }
  }

  const initials = operatorName
    .split(' ')
    .filter(Boolean)
    .map((n) => n[0])
    .slice(0, 2)
    .join('')
    .toUpperCase() || 'JV'

  return (
    <header className="h-16 border-b border-zinc-800 bg-black/95 backdrop-blur-md px-3 sm:px-4 lg:px-6 flex items-center justify-between z-30 shrink-0">
      {/* Left: Hamburger (Mobile/Tablet) + Logo + Title + Project Subtitle */}
      <div className="flex items-center gap-2 sm:gap-3">
        {onToggleMobileMenu && (
          <button
            type="button"
            id="btn-header-hamburger"
            onClick={onToggleMobileMenu}
            className="md:hidden w-9 h-9 rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white hover:bg-zinc-800 flex items-center justify-center transition cursor-pointer shrink-0"
            aria-label="Abrir menú de navegación"
            title="Abrir menú"
          >
            <Menu className="w-4 h-4" />
          </button>
        )}
        <div
          onClick={() => onNavigateSection('dashboard')}
          className="w-9 h-9 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-700 flex items-center justify-center shrink-0 cursor-pointer hover:bg-zinc-800 transition"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none">
            <path
              d="M12 2L2 7L12 12L22 7L12 2Z"
              fill="#ffffff"
              fillOpacity="0.3"
              stroke="#ffffff"
              strokeWidth="1.8"
            />
            <path d="M2 17L12 22L22 17" stroke="#ffffff" strokeWidth="1.8" />
            <path d="M2 12L12 17L22 12" stroke="#ffffff" strokeWidth="1.8" />
          </svg>
        </div>
        <div>
          <div className="text-sm font-bold tracking-tight text-white flex items-center gap-1.5 sm:gap-2">
            <span>SolidBit SACL</span>
            <span className="text-[9px] sm:text-[10px] px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-200 border border-zinc-700 font-mono font-semibold">
              VITE REACT 19
            </span>
          </div>
          <div
            id="header-project-subtitle"
            className="text-[10px] sm:text-[11px] text-zinc-400 font-medium truncate max-w-[130px] sm:max-w-xs"
          >
            {projectName && projectName !== 'integration' ? projectName : 'Stable-Ecommerce'} Orchestrator
          </div>
        </div>
      </div>

      {/* Center: Greeting & Subtitle */}
      <div className="hidden xl:block text-left">
        <h1 className="text-sm font-bold text-white tracking-wide">
          Hola, {operatorName} &bull; Panel de Control
        </h1>
        <p className="text-[11px] text-zinc-400">
          Supervisión de flota multi-agente, contratos congelados y compuertas soberanas
        </p>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3 sm:gap-4">
        {/* Real-time Clock */}
        <div
          id="header-live-clock"
          className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-zinc-950 border border-zinc-800 text-xs font-mono text-zinc-300 shadow-inner"
        >
          <span className="w-2 h-2 rounded-full bg-white animate-pulse" />
          <span>{clock || 'Cargando reloj...'}</span>
        </div>

        {/* Adaptive Information Density Switcher */}
        <div
          id="header-density-control"
          className="hidden xl:flex items-center p-0.5 rounded-xl bg-zinc-900 border border-zinc-800 text-[11px] font-mono"
          title="Densidad Adaptativa de Información"
        >
          <button
            type="button"
            onClick={() => handleDensityChange('compact')}
            className={`px-2 py-1 rounded-lg transition ${
              density === 'compact' ? 'bg-white text-black font-bold shadow-sm' : 'text-zinc-400 hover:text-white'
            }`}
          >
            Compact 28px
          </button>
          <button
            type="button"
            onClick={() => handleDensityChange('default')}
            className={`px-2 py-1 rounded-lg transition ${
              density === 'default' ? 'bg-white text-black font-bold shadow-sm' : 'text-zinc-400 hover:text-white'
            }`}
          >
            Default 38px
          </button>
          <button
            type="button"
            onClick={() => handleDensityChange('comfortable')}
            className={`px-2 py-1 rounded-lg transition ${
              density === 'comfortable' ? 'bg-white text-black font-bold shadow-sm' : 'text-zinc-400 hover:text-white'
            }`}
          >
            Comfort 48px
          </button>
        </div>

        {/* Quick Search / Command Palette Trigger (Cmd+K) */}
        {onOpenCommandPalette && (
          <button
            type="button"
            onClick={onOpenCommandPalette}
            id="btn-header-command-palette"
            className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-xs text-zinc-400 hover:text-white transition cursor-pointer"
            title="Abrir Command Palette (Ctrl+K)"
          >
            <Search className="w-3.5 h-3.5 text-zinc-400" />
            <span>Buscar...</span>
            <kbd className="px-1.5 py-0.2 rounded bg-zinc-800 text-[9px] font-mono border border-zinc-700 text-zinc-300">
              ⌘K
            </kbd>
          </button>
        )}

        {/* Git Diffs Quick Inspector Trigger */}
        {onOpenDiffModal && (
          <button
            type="button"
            id="btn-header-diff-inspector"
            onClick={onOpenDiffModal}
            className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-600 text-xs font-mono text-zinc-300 hover:text-white transition cursor-pointer"
            title="Inspeccionar diffs Git en worktree"
          >
            <GitBranch className="w-3.5 h-3.5 text-white" />
            <span>Diffs</span>
          </button>
        )}

        {/* Notifications Popover */}
        <div className="relative" ref={popoverRef}>
          <button
            type="button"
            id="btn-notifications-bell"
            onClick={() => setShowNotifications(!showNotifications)}
            className="w-9 h-9 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-zinc-300 hover:text-white flex items-center justify-center transition relative cursor-pointer"
            title="Notificaciones"
          >
            <Bell className="w-4 h-4" />
            {notifications.length > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-white text-black text-[9px] font-bold flex items-center justify-center shadow-lg shadow-white/20">
                {notifications.length}
              </span>
            )}
          </button>

          {showNotifications && (
            <div
              id="notifications-popover-content"
              className="fixed inset-x-3 top-16 sm:absolute sm:inset-x-auto sm:right-0 sm:mt-2 sm:w-80 md:w-96 rounded-2xl bg-zinc-950 border border-zinc-800 shadow-2xl p-4 space-y-3 z-50 text-left"
            >
              <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
                <div className="flex items-center gap-2">
                  <Bell className="w-4 h-4 text-white" />
                  <span className="text-xs font-bold text-white">Centro de Notificaciones</span>
                </div>
                <span className="text-[10px] font-mono text-zinc-500">
                  {notifications.length} eventos
                </span>
              </div>

              <div className="space-y-2 max-h-72 overflow-y-auto custom-scroll pr-1">
                {notifications.length === 0 ? (
                  <p className="text-xs text-zinc-500 text-center py-4">No hay notificaciones pendientes</p>
                ) : (
                  notifications.map((n) => (
                    <div
                      key={n.id}
                      onClick={() => {
                        if (n.actionUrl) onNavigateSection(n.actionUrl)
                        setShowNotifications(false)
                      }}
                      className="p-2.5 rounded-xl bg-zinc-900/60 border border-white/5 hover:border-zinc-600 transition cursor-pointer space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-white flex items-center gap-1.5">
                          {n.type === 'gate' ? (
                            <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
                          ) : n.type === 'success' ? (
                            <CheckCircle2 className="w-3.5 h-3.5 text-white" />
                          ) : (
                            <Info className="w-3.5 h-3.5 text-blue-400" />
                          )}
                          {n.title}
                        </span>
                        <span className="text-[10px] font-mono text-zinc-500">{n.time}</span>
                      </div>
                      <p className="text-[11px] text-zinc-400 leading-relaxed">{n.message}</p>
                    </div>
                  ))
                )}
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-zinc-800 text-[11px]">
                <button
                  type="button"
                  onClick={() => {
                    onNavigateSection('executions')
                    setShowNotifications(false)
                  }}
                  className="text-white hover:underline flex items-center gap-1 font-semibold cursor-pointer"
                >
                  <Terminal className="w-3.5 h-3.5" /> Ver compuertas HITL
                </button>
                <button
                  type="button"
                  onClick={() => {
                    const idsToDismiss = new Set(dismissedNotifIds)
                    notifications.forEach((n) => idsToDismiss.add(n.id))
                    setDismissedNotifIds(idsToDismiss)
                    try {
                      sessionStorage.setItem('sacl_dismissed_notifs', JSON.stringify(Array.from(idsToDismiss)))
                    } catch {}
                    setNotifications([])
                  }}
                  className="text-zinc-400 hover:text-white transition cursor-pointer font-medium"
                >
                  Marcar como leídas
                </button>
              </div>
            </div>
          )}
        </div>

        {/* User Profile: Editable on Click */}
        <div className="relative" ref={profileRef}>
          <button
            type="button"
            onClick={() => setShowProfileModal(!showProfileModal)}
            className="flex items-center gap-2.5 pl-1 pr-1 hover:opacity-90 transition cursor-pointer group text-left"
            title="Editar Perfil Soberano"
          >
            <div className="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-white font-bold text-xs flex items-center justify-center shrink-0 group-hover:border-emerald-400">
              {initials}
            </div>
            <div className="hidden sm:block text-left leading-tight">
              <div className="text-xs font-bold text-white group-hover:text-white transition">
                {operatorName}
              </div>
              <div className="text-[10px] text-zinc-400">{operatorRole}</div>
            </div>
          </button>

          {/* Quick Edit Profile Popover */}
          {showProfileModal && (
            <div className="fixed inset-x-3 top-16 sm:absolute sm:inset-x-auto sm:right-0 sm:mt-2 sm:w-80 rounded-2xl bg-zinc-950 border border-zinc-800 shadow-2xl p-4 space-y-3 z-50 text-left">
              <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
                <div className="flex items-center gap-2">
                  <User className="w-4 h-4 text-white" />
                  <span className="text-xs font-bold text-white">Editar Perfil Soberano</span>
                </div>
                <button
                  onClick={() => setShowProfileModal(false)}
                  className="text-zinc-500 hover:text-white"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>

              <form onSubmit={handleSaveProfile} className="space-y-3">
                <div className="space-y-1">
                  <label className="text-[10px] font-mono text-zinc-400">Nombre:</label>
                  <input
                    type="text"
                    value={operatorName}
                    onChange={(e) => setOperatorName(e.target.value)}
                    className="w-full bg-zinc-900/60 border border-zinc-800 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-emerald-500/60"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] font-mono text-zinc-400">Rol:</label>
                  <input
                    type="text"
                    value={operatorRole}
                    onChange={(e) => setOperatorRole(e.target.value)}
                    className="w-full bg-zinc-900/60 border border-zinc-800 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-emerald-500/60"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] font-mono text-zinc-400">Email:</label>
                  <input
                    type="email"
                    value={operatorEmail}
                    onChange={(e) => setOperatorEmail(e.target.value)}
                    className="w-full bg-zinc-900/60 border border-zinc-800 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-emerald-500/60"
                  />
                </div>

                <div className="pt-2 flex items-center justify-between border-t border-zinc-800">
                  <button
                    type="button"
                    onClick={() => {
                      onNavigateSection('settings')
                      setShowProfileModal(false)
                    }}
                    className="text-[11px] text-zinc-400 hover:text-white"
                  >
                    Más opciones &rarr;
                  </button>
                  <button
                    type="submit"
                    disabled={savingProfile}
                    className="px-3.5 py-1.5 rounded-xl bg-white hover:bg-zinc-200 text-black font-semibold shadow-sm text-xs flex items-center gap-1.5 transition cursor-pointer"
                  >
                    <Save className="w-3.5 h-3.5" />
                    <span>{savingProfile ? 'Guardando...' : 'Guardar'}</span>
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>

        {/* Dedicated Jira Backlog Shortcut */}
        <button
          type="button"
          onClick={() => onNavigateSection('jira')}
          id="btn-header-jira-nav"
          className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 sm:py-2 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-xs font-semibold text-zinc-300 hover:text-white transition cursor-pointer shrink-0"
          title="Ver Jira Backlog & Requerimientos"
        >
          <CheckSquare className="w-3.5 h-3.5 text-zinc-300" />
          <span>Jira Backlog</span>
        </button>

        {/* Dedicated Sprint Execution Studio CTA */}
        <button
          type="button"
          onClick={onOpenSprintModal}
          id="btn-design-sprint-cta"
          className="p-2 sm:px-4 sm:py-2 rounded-xl bg-white hover:bg-zinc-200 text-black font-bold text-xs flex items-center gap-1.5 transition shadow-sm cursor-pointer shrink-0"
          title="Abrir Sprint Execution Studio (DAG Kahn)"
        >
          <Sparkles className="w-3.5 h-3.5 fill-black" />
          <span className="hidden sm:inline">Diseñar Sprint</span>
          <span className="sm:hidden">Sprint</span>
        </button>
      </div>
    </header>
  )
}
