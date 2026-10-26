import React, { useState, useEffect, useRef } from 'react'
import { Bell, ShieldAlert, CheckCircle2, Info, Terminal, Sparkles } from 'lucide-react'
import type { NotificationItem } from '../types/orchestrator'

interface HeaderProps {
  projectName: string
  onOpenSprintModal: () => void
  onNavigateSection: (section: string) => void
}

export const Header: React.FC<HeaderProps> = ({ projectName, onOpenSprintModal, onNavigateSection }) => {
  const [clock, setClock] = useState<string>('')
  const [showNotifications, setShowNotifications] = useState<boolean>(false)
  const [notifications, setNotifications] = useState<NotificationItem[]>([
    {
      id: 'notif-1',
      title: 'Compuerta Requerida (HITL)',
      message: 'REQ-20261025-E43308B0: Aprobación HMAC requerida para aplicar cambios de Sprint 1.',
      type: 'gate',
      time: 'hace 5 min',
      actionUrl: 'gates',
    },
    {
      id: 'notif-2',
      title: 'Pytest Suite 100% Verde (Exit 0)',
      message: '31 pruebas de UI y contratos completadas con éxito en 92.5s.',
      type: 'success',
      time: 'hace 20 min',
    },
    {
      id: 'notif-3',
      title: 'Jira Cloud Status',
      message: 'Tareas persistidas soberanamente en SQLite WAL (sacl_ops.db).',
      type: 'info',
      time: 'hace 1 hora',
    },
  ])

  const popoverRef = useRef<HTMLDivElement>(null)

  // Live ticking clock
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

  // Close popover on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        setShowNotifications(false)
      }
    }
    if (showNotifications) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [showNotifications])

  return (
    <header className="h-16 border-b border-[#1b2533] bg-[#0c121a]/95 backdrop-blur-md px-4 lg:px-6 flex items-center justify-between z-30 shrink-0">
      {/* Left: Logo + Title + Project Subtitle */}
      <div className="flex items-center gap-3">
        <div
          onClick={() => onNavigateSection('dashboard')}
          className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center shrink-0 cursor-pointer hover:bg-emerald-500/20 transition"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="#10b981" fillOpacity="0.3" stroke="#10b981" strokeWidth="1.8" />
            <path d="M2 17L12 22L22 17" stroke="#10b981" strokeWidth="1.8" />
            <path d="M2 12L12 17L22 12" stroke="#10b981" strokeWidth="1.8" />
          </svg>
        </div>
        <div>
          <div className="text-sm font-bold tracking-tight text-white flex items-center gap-2">
            <span>SolidBit SACL</span>
            <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-400 font-mono font-semibold">
              VITE REACT 19
            </span>
          </div>
          <div id="header-project-subtitle" className="text-[11px] text-zinc-400 font-medium truncate max-w-[180px] sm:max-w-xs">
            {projectName || 'Stable-Ecommerce'} Orchestrator
          </div>
        </div>
      </div>

      {/* Center: Greeting & Subtitle */}
      <div className="hidden xl:block text-left">
        <h1 className="text-base font-bold text-white leading-tight flex items-center gap-1.5">
          Hola, SACL <Sparkles className="w-4 h-4 text-emerald-400" />
        </h1>
        <p className="text-xs text-zinc-400">Orquestador de agentes de IA para desarrollo y entrega de software.</p>
      </div>

      {/* Right: Status Pill, Clock, Notifications, User Profile, CTA */}
      <div className="flex items-center gap-2.5 sm:gap-3">
        {/* Online status pill */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#111e19] border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Sistema en línea</span>
        </div>

        {/* Live Clock pill */}
        <div id="header-datetime-pill" className="hidden md:block px-3 py-1.5 rounded-full bg-[#121922] border border-white/5 text-zinc-300 text-xs font-mono">
          {clock || 'Cargando reloj...'}
        </div>

        {/* Notifications Popover */}
        <div className="relative" ref={popoverRef}>
          <button
            type="button"
            onClick={() => setShowNotifications(!showNotifications)}
            id="btn-notifications"
            className="p-2 rounded-xl text-zinc-400 hover:text-white hover:bg-white/5 relative cursor-pointer transition"
            title="Notificaciones y Alertas"
          >
            <Bell className="w-4 h-4" />
            {notifications.length > 0 && (
              <span id="notif-badge" className="w-2 h-2 rounded-full bg-emerald-400 absolute top-1.5 right-1.5 animate-pulse"></span>
            )}
          </button>

          {showNotifications && (
            <div
              id="notifications-popover"
              className="absolute right-0 mt-2 w-80 sm:w-96 rounded-2xl bg-[#0e141d] border border-[#1b2533] shadow-2xl p-4 z-50 space-y-3.5 backdrop-blur-xl animate-in fade-in zoom-in-95 duration-100"
            >
              <div className="flex items-center justify-between border-b border-[#1b2533] pb-2.5">
                <div className="flex items-center gap-2">
                  <Bell className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs font-bold text-white">Notificaciones del Orquestador</span>
                </div>
                <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-bold text-[10px]">
                  {notifications.length} nuevas
                </span>
              </div>

              <div className="space-y-2 text-xs max-h-72 overflow-y-auto pr-1">
                {notifications.map((n) => (
                  <div
                    key={n.id}
                    className={`p-2.5 rounded-xl border space-y-1 ${
                      n.type === 'gate'
                        ? 'bg-amber-500/10 border-amber-500/20'
                        : n.type === 'success'
                        ? 'bg-emerald-500/10 border-emerald-500/20'
                        : 'bg-blue-500/10 border-blue-500/20'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span
                        className={`font-bold text-xs flex items-center gap-1.5 ${
                          n.type === 'gate' ? 'text-amber-400' : n.type === 'success' ? 'text-emerald-400' : 'text-blue-400'
                        }`}
                      >
                        {n.type === 'gate' && <ShieldAlert className="w-3.5 h-3.5" />}
                        {n.type === 'success' && <CheckCircle2 className="w-3.5 h-3.5" />}
                        {n.type === 'info' && <Info className="w-3.5 h-3.5" />}
                        {n.title}
                      </span>
                      <span className="text-[9px] font-mono text-zinc-500">{n.time}</span>
                    </div>
                    <p className="text-[11px] text-zinc-300">{n.message}</p>
                    {n.actionUrl && (
                      <div className="pt-1">
                        <button
                          onClick={() => {
                            onNavigateSection(n.actionUrl!)
                            setShowNotifications(false)
                          }}
                          className="text-xs text-amber-400 hover:underline font-bold"
                        >
                          Examinar Compuerta &rarr;
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-[#1b2533] text-[11px]">
                <button
                  type="button"
                  onClick={() => {
                    onNavigateSection('gates')
                    setShowNotifications(false)
                  }}
                  className="text-emerald-400 hover:underline flex items-center gap-1 font-semibold"
                >
                  <Terminal className="w-3.5 h-3.5" /> Ver compuertas
                </button>
                <button
                  type="button"
                  onClick={() => setNotifications([])}
                  className="text-zinc-500 hover:text-zinc-300 transition"
                >
                  Marcar como leídas
                </button>
              </div>
            </div>
          )}
        </div>

        {/* User Profile: JV + Joaquin Vallejo + Owner */}
        <div className="flex items-center gap-2.5 pl-1 pr-1">
          <div className="w-8 h-8 rounded-full bg-[#1e293b] border border-zinc-700 text-white font-bold text-xs flex items-center justify-center shrink-0">
            JV
          </div>
          <div className="hidden sm:block text-left leading-tight">
            <div className="text-xs font-bold text-white">Joaquin Vallejo</div>
            <div className="text-[10px] text-zinc-400">Owner</div>
          </div>
        </div>

        {/* Prominent Action CTA: + Diseñar Sprint & Jira */}
        <button
          type="button"
          onClick={onOpenSprintModal}
          id="btn-design-sprint-cta"
          className="px-3.5 sm:px-4 py-2 rounded-xl bg-[#00d084] hover:bg-[#00b875] text-[#0a0e14] font-bold text-xs flex items-center gap-1.5 transition shadow-[0_0_20px_rgba(0,208,132,0.25)] cursor-pointer shrink-0"
        >
          <span className="text-sm font-extrabold leading-none">+</span>
          <span>Diseñar Sprint & Jira</span>
        </button>
      </div>
    </header>
  )
}
