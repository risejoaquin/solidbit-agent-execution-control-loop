import React, { useState, useEffect, useRef } from 'react'
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
} from 'lucide-react'
import type { NotificationItem } from '../types/orchestrator'

interface HeaderProps {
  projectName: string
  onOpenSprintModal: () => void
  onNavigateSection: (section: string) => void
  onToggleMobileMenu?: () => void
}

export const Header: React.FC<HeaderProps> = ({
  projectName,
  onOpenSprintModal,
  onNavigateSection,
  onToggleMobileMenu,
}) => {
  const [clock, setClock] = useState<string>('')
  const [showNotifications, setShowNotifications] = useState<boolean>(false)
  const [showProfileModal, setShowProfileModal] = useState<boolean>(false)

  // Sovereign Operator State
  const [operatorName, setOperatorName] = useState<string>(
    localStorage.getItem('sacl_operator_name') || 'Joaquin Vallejo'
  )
  const [operatorRole, setOperatorRole] = useState<string>(
    localStorage.getItem('sacl_operator_role') || 'Owner'
  )
  const [operatorEmail, setOperatorEmail] = useState<string>('risejoaquin@solidbit.io')
  const [savingProfile, setSavingProfile] = useState<boolean>(false)

  const [notifications, setNotifications] = useState<NotificationItem[]>([
    {
      id: 'notif-1',
      title: 'Compuerta Requerida (HITL)',
      message: 'REQ-20261026-743941E4: Aprobación HMAC requerida para aplicar cambios.',
      type: 'gate',
      time: 'Reciente',
      actionUrl: 'executions',
    },
    {
      id: 'notif-2',
      title: 'Pytest Suite Verde (Exit 0)',
      message: '31 pruebas de UI y contratos completadas con éxito.',
      type: 'success',
      time: 'hace 5 min',
    },
    {
      id: 'notif-3',
      title: 'DAG de Kahn Generado',
      message: '4 Oleadas concurrentes sincronizadas con SQLite WAL.',
      type: 'info',
      time: 'hace 10 min',
    },
  ])

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

  // Load operator profile from backend
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

    // Subscribe to SSE events for notifications
    try {
      const sse = new EventSource('/api/events/stream')
      sse.addEventListener('gate', (e: MessageEvent) => {
        setNotifications((prev) => [
          {
            id: `gate-${Date.now()}`,
            title: 'Nueva Compuerta HITL',
            message: 'Compuerta de decisión requiere firma soberana.',
            type: 'gate',
            time: 'Ahora',
            actionUrl: 'executions',
          },
          ...prev,
        ])
      })
      sse.addEventListener('sprint_executed', () => {
        setNotifications((prev) => [
          {
            id: `exec-${Date.now()}`,
            title: 'Oleadas Ejecutadas',
            message: 'Entregables físicos generados en disco.',
            type: 'success',
            time: 'Ahora',
            actionUrl: 'executions',
          },
          ...prev,
        ])
      })
      return () => sse.close()
    } catch {
      // ignore
    }
  }, [])

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
    <header className="h-16 border-b border-[#1b2533] bg-[#0c121a]/95 backdrop-blur-md px-3 sm:px-4 lg:px-6 flex items-center justify-between z-30 shrink-0">
      {/* Left: Mobile Toggle + Logo + Title + Project Subtitle */}
      <div className="flex items-center gap-2.5 sm:gap-3">
        {onToggleMobileMenu && (
          <button
            type="button"
            id="btn-mobile-menu-toggle"
            onClick={onToggleMobileMenu}
            className="md:hidden w-9 h-9 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-zinc-300 hover:text-white flex items-center justify-center transition shrink-0 cursor-pointer"
            title="Abrir menú de navegación"
          >
            <Menu className="w-4 h-4" />
          </button>
        )}
        <div
          onClick={() => onNavigateSection('dashboard')}
          className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center shrink-0 cursor-pointer hover:bg-emerald-500/20 transition"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none">
            <path
              d="M12 2L2 7L12 12L22 7L12 2Z"
              fill="#10b981"
              fillOpacity="0.3"
              stroke="#10b981"
              strokeWidth="1.8"
            />
            <path d="M2 17L12 22L22 17" stroke="#10b981" strokeWidth="1.8" />
            <path d="M2 12L12 17L22 12" stroke="#10b981" strokeWidth="1.8" />
          </svg>
        </div>
        <div>
          <div className="text-sm font-bold tracking-tight text-white flex items-center gap-1.5 sm:gap-2">
            <span>SolidBit SACL</span>
            <span className="text-[9px] sm:text-[10px] px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-400 font-mono font-semibold">
              VITE REACT 19
            </span>
          </div>
          <div
            id="header-project-subtitle"
            className="text-[10px] sm:text-[11px] text-zinc-400 font-medium truncate max-w-[130px] sm:max-w-xs"
          >
            {projectName || 'Stable-Ecommerce'} Orchestrator
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
          className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#090e16] border border-[#1b2533] text-xs font-mono text-zinc-300 shadow-inner"
        >
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>{clock || 'Cargando reloj...'}</span>
        </div>

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
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-emerald-500 text-black text-[9px] font-bold flex items-center justify-center shadow-lg shadow-emerald-500/50">
                {notifications.length}
              </span>
            )}
          </button>

          {showNotifications && (
            <div
              id="notifications-popover-content"
              className="fixed inset-x-3 top-16 sm:absolute sm:inset-x-auto sm:right-0 sm:mt-2 sm:w-80 md:w-96 rounded-2xl bg-[#0e141d] border border-[#1b2533] shadow-2xl p-4 space-y-3 z-50 text-left"
            >
              <div className="flex items-center justify-between border-b border-[#1b2533] pb-2">
                <div className="flex items-center gap-2">
                  <Bell className="w-4 h-4 text-emerald-400" />
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
                      className="p-2.5 rounded-xl bg-[#080c10] border border-white/5 hover:border-emerald-500/30 transition cursor-pointer space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-white flex items-center gap-1.5">
                          {n.type === 'gate' ? (
                            <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
                          ) : n.type === 'success' ? (
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
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

              <div className="flex items-center justify-between pt-2 border-t border-[#1b2533] text-[11px]">
                <button
                  type="button"
                  onClick={() => {
                    onNavigateSection('executions')
                    setShowNotifications(false)
                  }}
                  className="text-emerald-400 hover:underline flex items-center gap-1 font-semibold cursor-pointer"
                >
                  <Terminal className="w-3.5 h-3.5" /> Ver compuertas HITL
                </button>
                <button
                  type="button"
                  onClick={() => setNotifications([])}
                  className="text-zinc-500 hover:text-zinc-300 transition cursor-pointer"
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
            <div className="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 font-bold text-xs flex items-center justify-center shrink-0 group-hover:border-emerald-400">
              {initials}
            </div>
            <div className="hidden sm:block text-left leading-tight">
              <div className="text-xs font-bold text-white group-hover:text-emerald-400 transition">
                {operatorName}
              </div>
              <div className="text-[10px] text-zinc-400">{operatorRole}</div>
            </div>
          </button>

          {/* Quick Edit Profile Popover */}
          {showProfileModal && (
            <div className="fixed inset-x-3 top-16 sm:absolute sm:inset-x-auto sm:right-0 sm:mt-2 sm:w-80 rounded-2xl bg-[#0e141d] border border-[#1b2533] shadow-2xl p-4 space-y-3 z-50 text-left">
              <div className="flex items-center justify-between border-b border-[#1b2533] pb-2">
                <div className="flex items-center gap-2">
                  <User className="w-4 h-4 text-emerald-400" />
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
                    className="w-full bg-[#080c10] border border-[#1b2533] rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-emerald-500/60"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] font-mono text-zinc-400">Rol:</label>
                  <input
                    type="text"
                    value={operatorRole}
                    onChange={(e) => setOperatorRole(e.target.value)}
                    className="w-full bg-[#080c10] border border-[#1b2533] rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-emerald-500/60"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] font-mono text-zinc-400">Email:</label>
                  <input
                    type="email"
                    value={operatorEmail}
                    onChange={(e) => setOperatorEmail(e.target.value)}
                    className="w-full bg-[#080c10] border border-[#1b2533] rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-emerald-500/60"
                  />
                </div>

                <div className="pt-2 flex items-center justify-between border-t border-[#1b2533]">
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
                    className="px-3.5 py-1.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-bold text-xs flex items-center gap-1.5 transition cursor-pointer"
                  >
                    <Save className="w-3.5 h-3.5" />
                    <span>{savingProfile ? 'Guardando...' : 'Guardar'}</span>
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>

        {/* Prominent Action CTA: + Diseñar Sprint & Jira (Icon on mobile, Full on sm+) */}
        <button
          type="button"
          onClick={onOpenSprintModal}
          id="btn-design-sprint-cta"
          className="p-2 sm:px-4 sm:py-2 rounded-xl bg-[#00d084] hover:bg-[#00b875] text-[#0a0e14] font-bold text-xs flex items-center gap-1.5 transition shadow-[0_0_20px_rgba(0,208,132,0.25)] cursor-pointer shrink-0"
          title="Diseñar Sprint & Jira"
        >
          <span className="text-sm font-extrabold leading-none">+</span>
          <span className="hidden sm:inline">Diseñar Sprint & Jira</span>
        </button>
      </div>
    </header>
  )
}
