import React, { useState, useEffect, useRef } from 'react'
import { formatRelativeTime } from '../utils/dateFormat'
import {
  Bell,
  ShieldAlert,
  CheckCircle2,
  Info,
  User,
  Save,
  X,
  Menu,
  GitBranch,
  Search,
  AlertTriangle,
  Loader2,
  FolderGit2,
  Globe,
  Lock,
  ChevronDown,
} from 'lucide-react'
import type { NotificationItem, Project } from '../types/orchestrator'
import type { DomainStateMeta } from '../types/domainState'
import { useLanguage } from '../context/LanguageContext'

interface HeaderProps {
  projectName: string
  activeBranch?: string
  projects?: Project[]
  onSelectProject?: (projId: string) => void
  domainState: DomainStateMeta
  onNavigateSection: (section: string) => void
  onToggleMobileMenu?: () => void
  onOpenDiffModal?: () => void
  onOpenCommandPalette?: () => void
}

export const Header: React.FC<HeaderProps> = ({
  projectName,
  activeBranch = 'worktrees/scheduler',
  projects = [],
  onSelectProject,
  domainState,
  onNavigateSection,
  onToggleMobileMenu,
  onOpenDiffModal,
  onOpenCommandPalette,
}) => {
  const { lang, toggleLanguage, t } = useLanguage()
  const [showNotifications, setShowNotifications] = useState<boolean>(false)
  const [showProfileModal, setShowProfileModal] = useState<boolean>(false)
  const [showProjectDropdown, setShowProjectDropdown] = useState<boolean>(false)

  const [operatorName, setOperatorName] = useState<string>(
    localStorage.getItem('sacl_operator_name') || 'Operador Principal'
  )
  const [operatorRole, setOperatorRole] = useState<string>(
    localStorage.getItem('sacl_operator_role') || 'Responsable de Producto'
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
  const projectDropdownRef = useRef<HTMLDivElement>(null)

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
                title: t('Aprobación Pendiente', 'Pending Approval'),
                message: `${g.reason || g.action || t('Hay una entrega verificada esperando tu autorización', 'Verified delivery awaiting your authorization')}`,
                type: 'gate',
                time: formatRelativeTime(g.created_at || g.timestamp),
                actionUrl: 'dashboard',
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
                  title: t('Evento Registrado', 'Audited Event'),
                  message: `${ev.event_type}: ${ev.payload_json ? ev.payload_json.slice(0, 50) + '...' : t('Transacción registrada', 'Audited transaction')}`,
                  type: 'info',
                  time: formatRelativeTime(ev.created_at),
                  actionUrl: 'database',
                })
              }
            }
          }
        }
      } catch {}

      setNotifications(items)
    } catch {}
  }

  useEffect(() => {
    loadNotifications()
    const interval = setInterval(loadNotifications, 12000)
    return () => clearInterval(interval)
  }, [dismissedNotifIds])

  useEffect(() => {
    const handleOutside = (e: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        setShowNotifications(false)
      }
      if (profileRef.current && !profileRef.current.contains(e.target as Node)) {
        setShowProfileModal(false)
      }
      if (projectDropdownRef.current && !projectDropdownRef.current.contains(e.target as Node)) {
        setShowProjectDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleOutside)
    return () => document.removeEventListener('mousedown', handleOutside)
  }, [])

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setSavingProfile(true)
    try {
      localStorage.setItem('sacl_operator_name', operatorName)
      localStorage.setItem('sacl_operator_role', operatorRole)
      await fetch('/api/settings/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: operatorName, role: operatorRole, email: operatorEmail }),
      })
      setShowProfileModal(false)
    } catch (err) {
      console.error('Error guardando perfil:', err)
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
    projectName && projectName !== 'integration'
      ? projectName
      : t('Tienda Online (Stable-Ecommerce)', 'Online Store (Stable-Ecommerce)')

  // Semantic State Signifier
  const renderCoherentStatusSignifier = () => {
    switch (domainState.badgeVariant) {
      case 'red':
        return (
          <button
            type="button"
            onClick={() => onNavigateSection('dashboard')}
            className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-rose-500/15 text-rose-300 border border-rose-500/35 cursor-pointer hover:bg-rose-500/25 transition"
          >
            <AlertTriangle className="w-3 h-3 text-rose-400" />
            <span>{domainState.badgeLabel}</span>
          </button>
        )
      case 'amber':
        return (
          <button
            type="button"
            onClick={() => onNavigateSection('dashboard')}
            className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/35 cursor-pointer hover:bg-amber-500/25 transition"
          >
            <ShieldAlert className="w-3 h-3 text-amber-400" />
            <span>{domainState.badgeLabel}</span>
          </button>
        )
      case 'blue':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-zinc-900 text-white border border-zinc-700">
            <Loader2 className="w-3 h-3 text-white animate-spin" />
            <span>{domainState.badgeLabel}</span>
          </span>
        )
      case 'zinc':
        return (
          <button
            type="button"
            onClick={() => onNavigateSection('projects')}
            className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-zinc-900 text-zinc-300 border border-zinc-750 cursor-pointer hover:text-white transition"
          >
            <FolderGit2 className="w-3 h-3 text-zinc-400" />
            <span>{domainState.badgeLabel}</span>
          </button>
        )
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            <span>{domainState.badgeLabel}</span>
          </span>
        )
    }
  }

  return (
    <header className="h-16 border-b border-white/5 bg-[#0C0C0E] px-4 lg:px-6 flex items-center justify-between z-30 shrink-0">
      {/* Left: Brand, Selector Global de Proyecto y Rama Git */}
      <div className="flex items-center gap-3">
        {onToggleMobileMenu && (
          <button
            type="button"
            id="btn-header-hamburger"
            onClick={onToggleMobileMenu}
            className="md:hidden w-9 h-9 rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white flex items-center justify-center transition cursor-pointer shrink-0"
            aria-label={t('Abrir menú', 'Open menu')}
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

        {/* Global Project & Branch Selector */}
        <div className="relative" ref={projectDropdownRef}>
          <div
            onClick={() => setShowProjectDropdown(!showProjectDropdown)}
            className="flex flex-col cursor-pointer hover:opacity-90 transition select-none"
          >
            <div className="text-sm font-extrabold text-white flex items-center gap-1.5">
              <span>{cleanProjectName}</span>
              <ChevronDown className="w-3.5 h-3.5 text-zinc-400" />
            </div>
            <div className="flex items-center gap-2 text-[11px] text-zinc-400 font-mono mt-0.5">
              <span className="flex items-center gap-1 text-sky-400">
                <GitBranch className="w-3 h-3" />
                <strong>{activeBranch}</strong>
              </span>
              <span>&bull;</span>
              <span className="text-emerald-400 flex items-center gap-0.5">
                <Lock className="w-2.5 h-2.5" />
                {t('Aislado', 'Isolated')}
              </span>
            </div>
          </div>

          {/* Project Switcher Dropdown */}
          {showProjectDropdown && projects.length > 0 && (
            <div className="absolute left-0 top-12 mt-2 w-64 p-2 rounded-2xl bg-[#0C0C0E] border border-white/10 shadow-2xl z-50 space-y-1 animate-fade-in text-xs font-mono">
              <span className="text-[10px] text-zinc-500 uppercase px-2 py-1 block">
                {t('Seleccionar Proyecto Activo:', 'Select Active Project:')}
              </span>
              {projects.map((p) => (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => {
                    onSelectProject?.(p.id)
                    setShowProjectDropdown(false)
                  }}
                  className={`w-full text-left p-2 rounded-xl transition cursor-pointer flex items-center justify-between ${
                    p.name === projectName || p.is_active
                      ? 'bg-zinc-800 text-white font-bold'
                      : 'text-zinc-300 hover:bg-zinc-900'
                  }`}
                >
                  <div className="truncate">
                    <span className="block truncate">{p.name}</span>
                    <span className="text-[10px] text-zinc-500 block truncate">
                      {p.branch || 'main'}
                    </span>
                  </div>
                  {(p.name === projectName || p.is_active) && (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  )}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Global FSM Status Signifier */}
        <div className="hidden sm:block ml-2">{renderCoherentStatusSignifier()}</div>
      </div>

      {/* Right: Herramientas y Perfil */}
      <div className="flex items-center gap-2 sm:gap-2.5">
        {/* Language Switcher */}
        <button
          type="button"
          id="btn-language-toggle"
          onClick={toggleLanguage}
          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-zinc-900 border border-zinc-750 hover:border-zinc-500 text-xs font-bold text-white transition cursor-pointer"
        >
          <Globe className="w-3.5 h-3.5 text-emerald-400" />
          <span>{lang === 'es-MX' ? '🇲🇽 ES-MX' : '🇺🇸 EN'}</span>
        </button>

        {/* Quick Search Ctrl+K */}
        {onOpenCommandPalette && (
          <button
            type="button"
            onClick={onOpenCommandPalette}
            id="btn-header-command-palette"
            className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-xs text-zinc-300 hover:text-white transition cursor-pointer"
          >
            <Search className="w-3.5 h-3.5 text-zinc-400" />
            <span>{t('Comandos...', 'Commands...')}</span>
            <kbd className="px-1.5 py-0.5 rounded bg-zinc-800 text-[10px] font-mono text-zinc-400">
              Ctrl+K
            </kbd>
          </button>
        )}

        {/* Diff Inspector Modal Trigger */}
        {onOpenDiffModal && (
          <button
            type="button"
            onClick={onOpenDiffModal}
            className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-xs text-zinc-300 hover:text-white transition cursor-pointer"
          >
            <GitBranch className="w-3.5 h-3.5 text-zinc-400" />
            <span>{t('Diffs', 'Diffs')}</span>
          </button>
        )}

        {/* Notifications Bell */}
        <div className="relative" ref={popoverRef}>
          <button
            type="button"
            onClick={() => setShowNotifications(!showNotifications)}
            className="w-9 h-9 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-zinc-300 hover:text-white flex items-center justify-center transition relative cursor-pointer"
          >
            <Bell className="w-4 h-4" />
            {notifications.length > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-amber-400 text-black text-[10px] font-mono font-extrabold flex items-center justify-center">
                {notifications.length}
              </span>
            )}
          </button>

          {showNotifications && (
            <div className="absolute right-0 top-12 mt-2 w-80 p-3 rounded-2xl bg-[#0C0C0E] border border-white/10 shadow-2xl z-50 space-y-2 animate-fade-in text-xs">
              <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
                <span className="font-bold text-white">{t('Avisos del Sistema', 'System Alerts')}</span>
                <span className="text-[10px] font-mono text-zinc-500">
                  {notifications.length} {t('nuevos', 'new')}
                </span>
              </div>
              <div className="space-y-1.5 max-h-64 overflow-y-auto custom-scroll">
                {notifications.length === 0 ? (
                  <p className="text-zinc-500 py-3 text-center">{t('Sin avisos pendientes', 'No alerts')}</p>
                ) : (
                  notifications.map((n) => (
                    <div
                      key={n.id}
                      onClick={() => {
                        if (n.actionUrl) onNavigateSection(n.actionUrl)
                        setShowNotifications(false)
                      }}
                      className="p-2.5 rounded-xl bg-black border border-white/5 space-y-1 hover:bg-zinc-900 cursor-pointer transition"
                    >
                      <div className="font-bold text-zinc-200">{n.title}</div>
                      <p className="text-[11px] text-zinc-400 line-clamp-2">{n.message}</p>
                      <span className="text-[9px] text-zinc-500 font-mono block">{n.time}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Profile Avatar */}
        <div className="relative" ref={profileRef}>
          <button
            type="button"
            onClick={() => setShowProfileModal(!showProfileModal)}
            className="w-9 h-9 rounded-xl bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-white flex items-center justify-center font-extrabold text-xs cursor-pointer shadow-sm"
          >
            {initials}
          </button>

          {showProfileModal && (
            <div className="absolute right-0 top-12 mt-2 w-72 p-4 rounded-2xl bg-[#0C0C0E] border border-white/10 shadow-2xl z-50 space-y-3 animate-fade-in text-xs">
              <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
                <span className="font-bold text-white">{t('Perfil del Operador', 'Operator Profile')}</span>
                <button
                  type="button"
                  onClick={() => setShowProfileModal(false)}
                  className="text-zinc-500 hover:text-white"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>

              <form onSubmit={handleSaveProfile} className="space-y-3">
                <div className="space-y-1">
                  <label className="text-[10px] text-zinc-400 uppercase font-mono">{t('Nombre', 'Name')}:</label>
                  <input
                    type="text"
                    value={operatorName}
                    onChange={(e) => setOperatorName(e.target.value)}
                    className="w-full bg-black border border-zinc-800 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] text-zinc-400 uppercase font-mono">{t('Rol', 'Role')}:</label>
                  <input
                    type="text"
                    value={operatorRole}
                    onChange={(e) => setOperatorRole(e.target.value)}
                    className="w-full bg-black border border-zinc-800 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none"
                  />
                </div>
                <button
                  type="submit"
                  disabled={savingProfile}
                  className="w-full py-2 rounded-xl bg-white hover:bg-zinc-200 text-black font-extrabold text-xs transition cursor-pointer shadow-sm"
                >
                  {savingProfile ? t('Guardando...', 'Saving...') : t('Guardar Datos', 'Save Profile')}
                </button>
              </form>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
