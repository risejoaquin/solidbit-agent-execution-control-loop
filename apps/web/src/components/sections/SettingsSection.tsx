import React, { useState, useEffect } from 'react'
import {
  User,
  ShieldCheck,
  Key,
  GitBranch,
  RefreshCw,
  GitPullRequest,
  CheckCircle2,
  AlertTriangle,
  Save,
  Server,
  Cloud,
} from 'lucide-react'

export const SettingsSection: React.FC = () => {
  const [operatorName, setOperatorName] = useState('Joaquin Vallejo')
  const [operatorRole, setOperatorRole] = useState('Product Owner / Sovereign Authority')
  const [operatorEmail, setOperatorEmail] = useState('risejoaquin@solidbit.io')
  const [secretKey, setSecretKey] = useState('sacl-sovereign-audit-secret-2026')
  const [ghStatus, setGhStatus] = useState<any>(null)
  const [prs, setPrs] = useState<any[]>([])
  const [saved, setSaved] = useState(false)
  const [syncing, setSyncing] = useState(false)

  const loadData = async () => {
    try {
      const pRes = await fetch('/api/settings/profile')
      const pData = await pRes.json()
      if (pData.profile) {
        if (pData.profile.name) setOperatorName(pData.profile.name)
        if (pData.profile.role) setOperatorRole(pData.profile.role)
        if (pData.profile.email) setOperatorEmail(pData.profile.email)
        if (pData.profile.secret) setSecretKey(pData.profile.secret)
      }
    } catch {}

    try {
      const ghRes = await fetch('/api/github/status')
      const ghData = await ghRes.json()
      setGhStatus(ghData)
    } catch {}

    try {
      const prRes = await fetch('/api/github/prs')
      const prData = await prRes.json()
      if (prData.prs) setPrs(prData.prs)
    } catch {}
  }

  useEffect(() => {
    loadData()
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
        alert('Perfil guardado exitosamente en backend SACL!')
      }
    } catch (e: any) {
      alert('Error guardando perfil: ' + e.message)
    }
  }

  const handleSyncGit = async () => {
    setSyncing(true)
    try {
      const res = await fetch('/api/github/sync', { method: 'POST' })
      const data = await res.json()
      alert(`Sincronización Git: ${data.message || 'Rama al día con origin'}`)
      loadData()
    } catch (e: any) {
      alert('Error sincronizando Git: ' + e.message)
    } finally {
      setSyncing(false)
    }
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-3xl bg-zinc-950 border border-zinc-800">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold text-white tracking-wide">
              Configuración de Gobernanza & Conexión GitHub
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-white/10 text-zinc-200 border border-emerald-500/30">
              SolidBit SDLC Standards
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Gestión de identidad soberana, credenciales HMAC y estado del repositorio remoto
          </p>
        </div>

        <button
          onClick={handleSyncGit}
          disabled={syncing}
          className="px-4 py-2 rounded-2xl bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-xs text-zinc-300 flex items-center gap-1.5 transition cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-zinc-300 ${syncing ? 'animate-spin' : ''}`} />
          <span>{syncing ? 'Sincronizando...' : 'Sync Git Remoto'}</span>
        </button>
      </div>

      {/* GitHub Repository Live Status from /api/github/status */}
      {ghStatus && (
        <div className="p-6 rounded-3xl bg-zinc-950 border border-zinc-800 space-y-4 shadow-xl">
          <div className="flex items-center justify-between border-b border-zinc-800 pb-3">
            <div className="flex items-center gap-2">
              <GitBranch className="w-4 h-4 text-zinc-200" />
              <h2 className="text-sm font-bold text-white">Estado del Repositorio Git (/api/github/status)</h2>
            </div>
            <span
              className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${
                !ghStatus.dirty
                  ? 'bg-zinc-900 text-zinc-300 border border-zinc-750'
                  : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
              }`}
            >
              {!ghStatus.dirty ? 'WORKTREE LIMPIO' : 'CAMBIOS SIN COMMITEAR'}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-xs">
            <div className="p-3 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-1">
              <span className="text-[10px] text-zinc-500">Rama Activa:</span>
              <div className="text-white font-bold truncate">{ghStatus.branch || 'main'}</div>
            </div>

            <div className="p-3 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-1">
              <span className="text-[10px] text-zinc-500">Último Commit SHA:</span>
              <div className="text-zinc-200 font-bold">{ghStatus.last_commit || 'HEAD'}</div>
            </div>

            <div className="p-3 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-1">
              <span className="text-[10px] text-zinc-500">Pull Requests Activos:</span>
              <div className="text-zinc-300 font-bold">{prs.length} detectados</div>
            </div>
          </div>
        </div>
      )}

      {/* Operator Identity Form */}
      <div className="p-6 rounded-3xl bg-zinc-950 border border-zinc-800 space-y-5 shadow-xl">
        <div className="flex items-center gap-3 border-b border-zinc-800 pb-4">
          <div className="w-10 h-10 rounded-2xl bg-white/10 border border-emerald-500/20 flex items-center justify-center text-zinc-200">
            <User className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white">Perfil Soberano & Credenciales HMAC (/api/settings/profile)</h2>
            <p className="text-xs text-zinc-400">
              Configuración persistida en el servidor SACL para validación de decisiones humanas
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
                className="w-full bg-black border border-zinc-800 rounded-2xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-emerald-500/60"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-[11px] font-mono text-zinc-400">Rol en el SDLC:</label>
              <input
                type="text"
                value={operatorRole}
                onChange={(e) => setOperatorRole(e.target.value)}
                className="w-full bg-black border border-zinc-800 rounded-2xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-emerald-500/60"
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
                className="w-full bg-black border border-zinc-800 rounded-2xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-emerald-500/60"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-[11px] font-mono text-zinc-400">Clave Secreta HMAC-SHA256:</label>
              <input
                type="password"
                value={secretKey}
                onChange={(e) => setSecretKey(e.target.value)}
                className="w-full bg-black border border-zinc-800 rounded-2xl px-4 py-2.5 text-xs text-white font-mono focus:outline-none focus:border-emerald-500/60"
              />
            </div>
          </div>

          <button
            type="submit"
            className="px-5 py-2.5 rounded-2xl bg-white hover:bg-zinc-200 text-black font-semibold font-bold text-xs flex items-center gap-2 transition cursor-pointer shadow-lg shadow-emerald-500/10"
          >
            <Save className="w-4 h-4" />
            <span>{saved ? 'Guardado en Backend!' : 'Guardar Perfil'}</span>
          </button>
        </form>
      </div>
    </div>
  )
}
