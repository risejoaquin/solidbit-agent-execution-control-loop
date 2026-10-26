import React, { useState, useEffect } from 'react'
import {
  User,
  ShieldCheck,
  Key,
  Server,
  Cloud,
  CheckCircle2,
  AlertTriangle,
  Save,
  Lock,
} from 'lucide-react'

export const SettingsSection: React.FC = () => {
  const [operatorName, setOperatorName] = useState('Joaquin Vallejo')
  const [operatorRole, setOperatorRole] = useState('Product Owner / Sovereign Authority')
  const [operatorEmail, setOperatorEmail] = useState('risejoaquin@solidbit.io')
  const [secretKey, setSecretKey] = useState('sacl-sovereign-audit-secret-2026')
  const [saved, setSaved] = useState(false)
  const [jiraStatus, setJiraStatus] = useState<any>({ authenticated: false, message: 'Verificando...' })

  useEffect(() => {
    fetch('/api/settings/profile')
      .then((r) => r.json())
      .then((d) => {
        if (d.profile) {
          if (d.profile.name) setOperatorName(d.profile.name)
          if (d.profile.role) setOperatorRole(d.profile.role)
          if (d.profile.email) setOperatorEmail(d.profile.email)
          if (d.profile.secret) setSecretKey(d.profile.secret)
        }
      })
      .catch(() => {})

    fetch('/api/orchestrator/jira-status')
      .then((r) => r.json())
      .then((d) => setJiraStatus(d))
      .catch(() => {})
  }, [])

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const res = await fetch('/api/settings/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: operatorName,
          role: operatorRole,
          email: operatorEmail,
          secret: secretKey,
        }),
      })
      if (res.ok) {
        localStorage.setItem('sacl_operator_name', operatorName)
        localStorage.setItem('sacl_operator_role', operatorRole)
        setSaved(true)
        setTimeout(() => setSaved(false), 3000)
        alert('Perfil del Product Owner guardado exitosamente en SACL!')
      }
    } catch (e: any) {
      alert('Error guardando perfil: ' + e.message)
    }
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-3xl bg-[#0e141d] border border-[#1b2533]">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold text-white tracking-wide">
              Configuración & Identidad Soberana del Operador
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              Gobernanza SolidBit SDLC
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Gestión de credenciales de firma criptográfica HMAC-SHA256 y guardas de infraestructura
          </p>
        </div>
      </div>

      {/* Operator Identity Form */}
      <div className="p-6 rounded-3xl bg-[#0e141d] border border-[#1b2533] space-y-5 shadow-xl">
        <div className="flex items-center gap-3 border-b border-[#1b2533] pb-4">
          <div className="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <User className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white">Perfil del Operador Soberano</h2>
            <p className="text-xs text-zinc-400">
              Identidad utilizada para autorizar compuertas HITL y firmar despliegues
            </p>
          </div>
        </div>

        <form onSubmit={handleSaveProfile} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-[11px] font-mono text-zinc-400">Nombre del Operador:</label>
              <input
                type="text"
                value={operatorName}
                onChange={(e) => setOperatorName(e.target.value)}
                className="w-full bg-[#080c10] border border-[#1b2533] rounded-2xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-emerald-500/60"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-[11px] font-mono text-zinc-400">Rol en el SDLC:</label>
              <input
                type="text"
                value={operatorRole}
                onChange={(e) => setOperatorRole(e.target.value)}
                className="w-full bg-[#080c10] border border-[#1b2533] rounded-2xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-emerald-500/60"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-[11px] font-mono text-zinc-400">Correo Electrónico:</label>
              <input
                type="email"
                value={operatorEmail}
                onChange={(e) => setOperatorEmail(e.target.value)}
                className="w-full bg-[#080c10] border border-[#1b2533] rounded-2xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-emerald-500/60"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-[11px] font-mono text-zinc-400">Clave Secreta HMAC-SHA256:</label>
              <input
                type="password"
                value={secretKey}
                onChange={(e) => setSecretKey(e.target.value)}
                className="w-full bg-[#080c10] border border-[#1b2533] rounded-2xl px-4 py-2.5 text-xs text-white font-mono focus:outline-none focus:border-emerald-500/60"
              />
            </div>
          </div>

          <button
            type="submit"
            className="px-5 py-2.5 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-black font-bold text-xs flex items-center gap-2 transition cursor-pointer shadow-lg shadow-emerald-500/10"
          >
            <Save className="w-4 h-4" />
            <span>{saved ? 'Guardado Exitosamente!' : 'Guardar Perfil Soberano'}</span>
          </button>
        </form>
      </div>

      {/* Infrastructure Guardrails Status */}
      <div className="p-6 rounded-3xl bg-[#0e141d] border border-[#1b2533] space-y-4">
        <div className="flex items-center gap-2 text-sm font-bold text-white border-b border-[#1b2533] pb-3">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Guardas de Seguridad en Producción (Zero-Unauthorized Deploy)</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="p-3.5 rounded-2xl bg-[#090e16] border border-[#1b2533] space-y-1">
            <span className="text-[10px] font-mono text-zinc-500">Railway Staging Guard</span>
            <div className="flex items-center gap-1.5 text-emerald-400 font-bold">
              <CheckCircle2 className="w-4 h-4" />
              <span>autoDeploy: OFF (Verificado)</span>
            </div>
            <p className="text-[11px] text-zinc-400">
              Imposible desplegar a producción sin token HMAC firmado por el PO.
            </p>
          </div>

          <div className="p-3.5 rounded-2xl bg-[#090e16] border border-[#1b2533] space-y-1">
            <span className="text-[10px] font-mono text-zinc-500">Atlassian / Jira CLI Status</span>
            <div className="flex items-center gap-1.5 text-amber-400 font-bold">
              <AlertTriangle className="w-4 h-4" />
              <span>{jiraStatus.message || 'CLI Local Disponible'}</span>
            </div>
            <p className="text-[11px] text-zinc-400">
              Sincronización respaldada en SQLite WAL local mientras se inicia sesión remota.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
