import React, { useState, useEffect } from 'react'
import {
  User,
  GitBranch,
  RefreshCw,
  CheckCircle2,
  Save,
  AlertCircle,
} from 'lucide-react'

export const SettingsSection: React.FC = () => {
  const [operatorName, setOperatorName] = useState('')
  const [operatorRole, setOperatorRole] = useState('Product Owner / Autoridad Principal')
  const [operatorEmail, setOperatorEmail] = useState('')
  const [secretKey, setSecretKey] = useState('sacl-local-audit-secret-2026')
  const [ghStatus, setGhStatus] = useState<any>(null)
  const [prs, setPrs] = useState<any[]>([])
  const [saving, setSaving] = useState(false)
  const [syncing, setSyncing] = useState(false)
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(
    null
  )

  const loadData = async () => {
    try {
      const pRes = await fetch('/api/settings/profile')
      const pData = await pRes.json()
      if (pData.profile) {
        if (pData.profile.name) setOperatorName(pData.profile.name)
        if (pData.profile.role) {
          setOperatorRole(
            pData.profile.role.replace(/sovereign/gi, 'Principal').replace(/local/gi, 'Local')
          )
        }
        if (pData.profile.email) setOperatorEmail(pData.profile.email)
        if (pData.profile.secret) {
          setSecretKey(pData.profile.secret.replace(/sovereign/gi, 'local'))
        }
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

  // Poka-Yoke real-time checks
  const isNameValid = operatorName.trim().length >= 2
  const isEmailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(operatorEmail.trim())
  const isSecretValid = secretKey.trim().length >= 8

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isNameValid || !isEmailValid || !isSecretValid) return
    setSaving(true)
    setFeedback(null)
    try {
      const res = await fetch('/api/settings/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: operatorName.trim(),
          role: operatorRole.trim(),
          email: operatorEmail.trim(),
          secret: secretKey.trim(),
        }),
      })
      if (res.ok) {
        localStorage.setItem('sacl_operator_name', operatorName.trim())
        localStorage.setItem('sacl_operator_role', operatorRole.trim())
        setFeedback({
          type: 'success',
          message: 'Tu perfil y credenciales han sido guardados correctamente.',
        })
      } else {
        setFeedback({ type: 'error', message: 'No se pudo guardar el perfil.' })
      }
    } catch (e: any) {
      setFeedback({ type: 'error', message: 'Error guardando perfil: ' + e.message })
    } finally {
      setSaving(false)
    }
  }

  const handleSyncGit = async () => {
    setSyncing(true)
    setFeedback(null)
    try {
      const res = await fetch('/api/github/sync', { method: 'POST' })
      const data = await res.json()
      setFeedback({
        type: 'success',
        message: `Sincronización Git completada: ${data.message || 'Rama al día con origin'}`,
      })
      loadData()
    } catch (e: any) {
      setFeedback({ type: 'error', message: 'Error sincronizando Git: ' + e.message })
    } finally {
      setSyncing(false)
    }
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto text-left pb-12">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 sm:p-6 rounded-2xl bg-zinc-950 border border-zinc-800">
        <div>
          <h1 className="text-lg font-bold text-white tracking-tight">
            Mi Perfil y Estado de GitHub
          </h1>
          <p className="text-xs text-zinc-400 mt-1">
            Configura tu identidad de operador para firmar aprobaciones y consulta el estado de tu repositorio.
          </p>
        </div>

        <button
          onClick={handleSyncGit}
          disabled={syncing}
          className="px-4 py-2 rounded-xl bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 text-xs text-zinc-200 font-semibold flex items-center gap-2 transition cursor-pointer self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin' : ''}`} />
          <span>{syncing ? 'Sincronizando...' : 'Sincronizar Git'}</span>
        </button>
      </div>

      {feedback && (
        <div
          className={`p-4 rounded-xl border text-xs flex items-center justify-between gap-3 ${
            feedback.type === 'success'
              ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-200'
              : 'bg-red-950/40 border-red-500/40 text-red-200'
          }`}
        >
          <div className="flex items-center gap-2">
            {feedback.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
            )}
            <span>{feedback.message}</span>
          </div>
          <button onClick={() => setFeedback(null)} className="text-xs underline cursor-pointer">
            Cerrar
          </button>
        </div>
      )}

      {/* GitHub Repository Live Status */}
      {ghStatus && (
        <div className="p-5 sm:p-6 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-4">
          <div className="flex items-center justify-between border-b border-zinc-850 pb-3">
            <div className="flex items-center gap-2">
              <GitBranch className="w-4 h-4 text-zinc-200" />
              <h2 className="text-sm font-bold text-white">Estado Actual del Repositorio</h2>
            </div>
            <span
              className={`text-[10px] font-mono px-2.5 py-0.5 rounded-full border ${
                !ghStatus.dirty
                  ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                  : 'bg-amber-500/15 text-amber-300 border-amber-500/30'
              }`}
            >
              {!ghStatus.dirty ? 'SIN CAMBIOS PENDIENTES' : 'HAY CAMBIOS LOCALES'}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-xs">
            <div className="p-3.5 rounded-xl bg-black border border-zinc-850 space-y-1">
              <span className="text-[10px] text-zinc-500">Rama Activa:</span>
              <div className="text-white font-bold truncate">{ghStatus.branch || 'main'}</div>
            </div>

            <div className="p-3.5 rounded-xl bg-black border border-zinc-850 space-y-1">
              <span className="text-[10px] text-zinc-500">Último Commit:</span>
              <div className="text-zinc-200 font-bold">{ghStatus.last_commit || 'HEAD'}</div>
            </div>

            <div className="p-3.5 rounded-xl bg-black border border-zinc-850 space-y-1">
              <span className="text-[10px] text-zinc-500">Pull Requests Abiertos:</span>
              <div className="text-zinc-300 font-bold">{prs.length} en GitHub</div>
            </div>
          </div>
        </div>
      )}

      {/* Operator Identity Form with Poka-Yoke Real-Time Green Indicators */}
      <div className="p-5 sm:p-6 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-5">
        <div className="flex items-center gap-3 border-b border-zinc-850 pb-4">
          <div className="w-10 h-10 rounded-xl bg-zinc-900 border border-zinc-750 flex items-center justify-center text-zinc-200">
            <User className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white">Datos del Operador y Clave de Firma</h2>
            <p className="text-xs text-zinc-400">
              Se utilizan para atribuir tus aprobaciones y enviar notificaciones a tu correo.
            </p>
          </div>
        </div>

        <form onSubmit={handleSaveProfile} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-zinc-300">Nombre Completo</label>
                <span className={`text-[11px] flex items-center gap-1 ${isNameValid ? 'text-emerald-400' : 'text-zinc-500'}`}>
                  <CheckCircle2 className="w-3 h-3" />
                  {isNameValid ? 'Válido' : 'Requerido'}
                </span>
              </div>
              <input
                type="text"
                value={operatorName}
                onChange={(e) => setOperatorName(e.target.value)}
                className="w-full bg-black border border-zinc-800 rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-white"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-zinc-300 block">Rol en el Equipo</label>
              <input
                type="text"
                value={operatorRole}
                onChange={(e) => setOperatorRole(e.target.value)}
                className="w-full bg-black border border-zinc-800 rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-white"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-zinc-300">Correo Electrónico</label>
                <span className={`text-[11px] flex items-center gap-1 ${isEmailValid ? 'text-emerald-400' : 'text-amber-400'}`}>
                  <CheckCircle2 className="w-3 h-3" />
                  {isEmailValid ? 'Formato de correo válido' : 'Ingresa un correo válido'}
                </span>
              </div>
              <input
                type="email"
                value={operatorEmail}
                onChange={(e) => setOperatorEmail(e.target.value)}
                className="w-full bg-black border border-zinc-800 rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-white font-mono"
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-zinc-300">Clave Privada de Autorización</label>
                <span className={`text-[11px] flex items-center gap-1 ${isSecretValid ? 'text-emerald-400' : 'text-amber-400'}`}>
                  <CheckCircle2 className="w-3 h-3" />
                  {isSecretValid ? 'Longitud segura (8+ caracteres)' : 'Mínimo 8 caracteres'}
                </span>
              </div>
              <input
                type="password"
                value={secretKey}
                onChange={(e) => setSecretKey(e.target.value)}
                className="w-full bg-black border border-zinc-800 rounded-xl px-3.5 py-2.5 text-xs text-white font-mono focus:outline-none focus:border-white"
              />
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={saving || !isNameValid || !isEmailValid || !isSecretValid}
              className="px-5 py-2.5 rounded-xl bg-white hover:bg-zinc-200 disabled:opacity-40 text-black font-bold text-xs flex items-center gap-2 transition cursor-pointer shadow-sm"
            >
              <Save className="w-4 h-4" />
              <span>{saving ? 'Guardando...' : 'Guardar Mi Perfil'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
