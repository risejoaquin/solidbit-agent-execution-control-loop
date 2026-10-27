import React, { useState, useEffect, useRef } from 'react'
import { formatRelativeTime } from '../utils/dateFormat'
import {
  Bell,
  ShieldAlert,
  CheckCircle2,
  Info,
  Sparkles,
  User,
  Save,
  X,
  Menu,
  GitBranch,
  Search,
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
  const [showNotifications, setShowNotifications] = useState<boolean>(false)
  const [showProfileModal, setShowProfileModal] = useState<boolean>(false)

  // Sovereign Operator State
  const [operatorName, setOperatorName] = useState<string>(
    localStorage.getItem('sacl_operator_name') || 'Operador'
  )
  const [operatorRole, setOperatorRole] = useState<string>(
    localStorage.getItem('sacl_operator_role') || 'Propietario'
  )
  const [operatorEmail, setOperatorEmail] = useState<string>('')
  const [savingProfile, setSavingProfile] = useState<boolean>(false)

  const [notifications, setNotifications] = useState<NotificationItem[]>([])
  const [dismissedNotifIds] = useState<Set<string>>(() => {
    try {
      const stored = sessionStorage.getItem('sacl_dismissed_notifs')
      return new Set(stored ? JSON.parse(stored) : [])
    } catch {
      return new Set()
    }
  })

  const popoverRef = useRef<HTMLDivElement>(null)
  const profileRef = useRef<HTMLDivElement>(null)

  const loadNotifications = async () => {
    try {
      const items: NotificationItem[] = []

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
                title: 'Aprobación Pendiente',
                message: `${g.reason || g.action || 'Hay un cambio listo esperando tu visto bueno'}`,
                type: 'gate',
                time: formatRelativeTime(g.created_at || g.timestamp),
                actionUrl: 'executions',
              })
            }
          }
        }
      } catch {}

      try {
        const evRes = await fetch('/api/db/rows?table=events&limit=4')
        if (evRes.ok) {
          const evData = await evRes.json()
          if (evData.rows && Array.isArray(evData.rows)) {
            for (const ev of evData.rows) {
              const notifId = `ev-${ev.event_id}`
              if (!dismissedNotifIds.has(notifId)) {
                items.push({
                  id: notifId,
                  title: `Actividad: ${ev.event_type}`,
                  message: ev.run_id ? `Registro ${ev.run_id}` : 'Guardado en memoria local',
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
      console.warn('Error loading notifications:', e)
    }
  }

  useEffect(() => {
    fetch('/api/settings/profile')
      .then((r) => r.json())
      .then((d) => {
        if (d.profile?.name) {
          setOperatorName(d.profile.name)
          setOperatorRole(d.profile.role?.includes('Owner') ? 'Propietario' : d.profile.role)
          if (d.profile.email) setOperatorEmail(d.profile.email)
        }
      })
      .catch(() => {})

    loadNotifications()
  }, [])

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        setShowNotifications(false)
      }
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) {
        setShowProfileModal(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

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

  const initials =
    operatorName
      .split(' ')
      .filter(Boolean)
      .map((n) => n[0])
      .slice(0, 2)
      .join('')
      .toUpperCase() || 'OP'

  const cleanProjectName =
    projectName && projectName !== 'integration' ? projectName : 'Tienda Online (Stable-Ecommerce)'

  return (
    <header className="h-16 border-b border-zinc-800 bg-black/95 backdrop-blur-md px-4 lg:px-6 flex items-center justify-between z-30 shrink-0">
      {/* Left: Brand & Active Project */}
      <div className="flex items-center gap-3">
        {onToggleMobileMenu && (
          <button
            type="button"
            id="btn-header-hamburger"
            onClick={onToggleMobileMenu}
            className="md:hidden w-9 h-9 rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white flex items-center justify-center transition cursor-pointer shrink-0"
            aria-label="Abrir menú"
          >
            <Menu className="w-4 h-4" />
          </button>
        )}

        <div
          onClick={() => onNavigateSection('dashboard')}
          className="w-9 h-9 rounded-xl bg-white text-black flex items-center justify-center shrink-0 cursor-pointer font-extrabold text-sm shadow-sm"
        >
          SB
        </div>

        <div>
          <div className="text-sm font-bold text-white flex items-center gap-2">
            <span>Asistente de Proyectos SolidBit</span>
            <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              Conectado en tu PC
            </span>
          </div>
          <div className="text-xs text-zinc-400 truncate max-w-[200px] sm:max-w-md">
            Proyecto actual: <strong className="text-zinc-200">{cleanProjectName}</strong>
          </div>
        </div>
      </div>

      {/* Right: Simple Actions */}
      <div className="flex items-center gap-2.5 sm:gap-3">
        {/* Quick Search */}
        {onOpenCommandPalette && (
          <button
            type="button"
            onClick={onOpenCommandPalette}
            id="btn-header-command-palette"
            className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-xs text-zinc-300 hover:text-white transition cursor-pointer"
          >
            <Search className="w-3.5 h-3.5 text-zinc-400" />
            <span>Buscar acción...</span>
            <kbd className="px-1.5 py-0.5 rounded bg-zinc-800 text-[10px] font-mono text-zinc-400">
              Ctrl+K
            </kbd>
          </button>
        )}

        {/* Primary Action: New Task */}
        <button
          type="button"
          onClick={onOpenSprintModal}
          className="px-3.5 py-2 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-extrabold flex items-center gap-1.5 transition cursor-pointer shadow-sm"
        >
          <Sparkles className="w-3.5 h-3.5 text-black" />
          <span className="hidden sm:inline">Nueva Tarea</span>
          <span className="sm:hidden">+ Tarea</span>
        </button>

        {/* View Code Changes (Optional for reviewing files) */}
        {onOpenDiffModal && (
          <button
            type="button"
            id="btn-header-diff-inspector"
            onClick={onOpenDiffModal}
            className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-xs text-zinc-300 hover:text-white transition cursor-pointer"
            title="Ver archivos modificados"
          >
            <GitBranch className="w-3.5 h-3.5 text-zinc-400" />
            <span>Cambios</span>
          </button>
        )}

        {/* Notifications Bell */}
        <div className="relative" ref={popoverRef}>
          <button
            type="button"
            id="btn-notifications-bell"
            onClick={() => setShowNotifications(!showNotifications)}
            className="w-9 h-9 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-zinc-300 hover:text-white flex items-center justify-center transition relative cursor-pointer"
            title="Avisos"
          >
            <Bell className="w-4 h-4" />
            {notifications.length > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-white text-black text-[9px] font-bold flex items-center justify-center">
                {notifications.length}
              </span>
            )}
          </button>

          {showNotifications && (
            <div
              id="notifications-popover-content"
              className="fixed inset-x-3 top-16 sm:absolute sm:inset-x-auto sm:right-0 sm:mt-2 sm:w-80 rounded-2xl bg-zinc-950 border border-zinc-800 shadow-2xl p-4 space-y-3 z-50 text-left"
            >
              <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
                <span className="text-xs font-bold text-white">Avisos Recientes</span>
                <span className="text-[10px] text-zinc-400">{notifications.length}</span>
              </div>

              <div className="space-y-2 max-h-72 overflow-y-auto custom-scroll pr-1">
                {notifications.length === 0 ? (
                  <p className="text-xs text-zinc-500 text-center py-4">Todo está al día</p>
                ) : (
                  notifications.map((n) => (
                    <div
                      key={n.id}
                      onClick={() => {
                        if (n.actionUrl) onNavigateSection(n.actionUrl)
                        setShowNotifications(false)
                      }}
                      className="p-2.5 rounded-xl bg-zinc-900/70 border border-zinc-800 hover:border-zinc-600 transition cursor-pointer space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-white flex items-center gap-1.5">
                          {n.type === 'gate' ? (
                            <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
                          ) : n.type === 'success' ? (
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                          ) : (
                            <Info className="w-3.5 h-3.5 text-zinc-400" />
                          )}
                          {n.title}
                        </span>
                        <span className="text-[10px] text-zinc-500">{n.time}</span>
                      </div>
                      <p className="text-[11px] text-zinc-300">{n.message}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* User Profile Pill */}
        <div className="relative" ref={profileRef}>
          <button
            type="button"
            id="btn-operator-profile"
            onClick={() => setShowProfileModal(!showProfileModal)}
            className="flex items-center gap-2 pl-1.5 pr-2.5 py-1 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-700 transition cursor-pointer"
            title="Tu Perfil"
          >
            <div className="w-7 h-7 rounded-lg bg-white text-black font-bold text-xs flex items-center justify-center">
              {initials}
            </div>
            <div className="hidden md:block text-left">
              <div className="text-xs font-bold text-white leading-none">{operatorName}</div>
              <div className="text-[10px] text-zinc-400 mt-0.5">{operatorRole}</div>
            </div>
          </button>

          {showProfileModal && (
            <div className="fixed inset-x-3 top-16 sm:absolute sm:inset-x-auto sm:right-0 sm:mt-2 sm:w-80 rounded-2xl bg-zinc-950 border border-zinc-800 shadow-2xl p-4 space-y-3 z-50 text-left">
              <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
                <div className="flex items-center gap-2">
                  <User className="w-4 h-4 text-white" />
                  <span className="text-xs font-bold text-white">Tus Datos de Operador</span>
                </div>
                <button
                  type="button"
                  onClick={() => setShowProfileModal(false)}
                  className="text-zinc-400 hover:text-white cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <form onSubmit={handleSaveProfile} className="space-y-3 text-xs">
                <div>
                  <label className="text-[11px] text-zinc-400 block mb-1">Tu Nombre:</label>
                  <input
                    type="text"
                    value={operatorName}
                    onChange={(e) => setOperatorName(e.target.value)}
                    className="w-full bg-black border border-zinc-800 rounded-xl px-3 py-1.5 text-white"
                  />
                </div>
                <div>
                  <label className="text-[11px] text-zinc-400 block mb-1">Tu Rol:</label>
                  <input
                    type="text"
                    value={operatorRole}
                    onChange={(e) => setOperatorRole(e.target.value)}
                    className="w-full bg-black border border-zinc-800 rounded-xl px-3 py-1.5 text-white"
                  />
                </div>
                <div>
                  <label className="text-[11px] text-zinc-400 block mb-1">Correo para recibir avisos:</label>
                  <input
                    type="email"
                    value={operatorEmail}
                    onChange={(e) => setOperatorEmail(e.target.value)}
                    placeholder="tucorreo@ejemplo.com"
                    className="w-full bg-black border border-zinc-800 rounded-xl px-3 py-1.5 text-white"
                  />
                </div>
                <button
                  type="submit"
                  disabled={savingProfile}
                  className="w-full py-2 rounded-xl bg-white hover:bg-zinc-200 text-black font-bold flex items-center justify-center gap-1.5 cursor-pointer"
                >
                  <Save className="w-3.5 h-3.5" />
                  <span>{savingProfile ? 'Guardando...' : 'Guardar mis datos'}</span>
                </button>
              </form>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
