import React, { useState, useEffect } from 'react'
import { formatSmartDateTime } from '../../utils/dateFormat'
import {
  Cpu,
  GitBranch,
  GitFork,
  Database,
  Server,
  Mail,
  ShieldCheck,
  Cloud,
  Terminal,
  Copy,
  Check,
  ExternalLink,
  RefreshCw,
  Key,
  AlertTriangle,
  CheckCircle2,
  Search,
  Layers,
  Lock,
  Box,
  Code2,
  X,
  ChevronDown,
  ChevronUp,
  XCircle,
} from 'lucide-react'

export interface TechnologySessionItem {
  id: string
  name: string
  category: string
  status: 'connected' | 'unauthenticated' | 'disconnected' | 'degraded' | string
  version?: string
  account_info?: string
  last_checked?: string
  error_message?: string
  cli_command?: string
  agent_usage?: string
  auth_url?: string
}

export const TechAuthHubSection: React.FC = () => {
  const [connections, setConnections] = useState<TechnologySessionItem[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [testingId, setTestingId] = useState<string | null>(null)
  const [testResults, setTestResults] = useState<
    Record<string, { success: boolean; message: string; timestamp: string }>
  >({})
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [expandedCliId, setExpandedCliId] = useState<string | null>(null)
  const [bannerFeedback, setBannerFeedback] = useState<{ type: 'success' | 'info'; message: string } | null>(null)

  // Auth Credential Modal state
  const [authModalTool, setAuthModalTool] = useState<TechnologySessionItem | null>(null)
  const [authToken, setAuthToken] = useState<string>('')
  const [authEmail, setAuthEmail] = useState<string>('')
  const [authDomain, setAuthDomain] = useState<string>('')
  const [isSubmittingAuth, setIsSubmittingAuth] = useState<boolean>(false)
  const [authFeedback, setAuthFeedback] = useState<{ success: boolean; message: string } | null>(null)

  const fetchConnections = async () => {
    setIsLoading(true)
    try {
      const res = await fetch('/api/connections')
      const data = await res.json()
      if (data.connections && Array.isArray(data.connections)) {
        setConnections(data.connections)
      }
    } catch (err) {
      console.error('Error fetching technology connections:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchConnections()
  }, [])

  const copyCliCommand = (toolId: string, cmd: string) => {
    navigator.clipboard.writeText(cmd)
    setCopiedId(toolId)
    setTimeout(() => {
      setCopiedId(null)
    }, 2000)
  }

  const handleTestConnection = async (toolId: string) => {
    setTestingId(toolId)
    try {
      const res = await fetch('/api/connections/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tool_id: toolId }),
      })
      const result = await res.json()
      const isSuccess =
        result.success || (result.connection && result.connection.status === 'connected')
      const msg = isSuccess
        ? result.connection?.account_info || 'Sesión activa y verificada en este equipo.'
        : result.connection?.error_message ||
          result.connection?.account_info ||
          'Falta iniciar sesión o configurar credencial.'

      setTestResults((prev) => ({
        ...prev,
        [toolId]: {
          success: !!isSuccess,
          message: msg,
          timestamp: formatSmartDateTime(new Date()),
        },
      }))
      fetchConnections()
    } catch (err) {
      setTestResults((prev) => ({
        ...prev,
        [toolId]: {
          success: false,
          message: `Error al verificar conexión: ${err}`,
          timestamp: formatSmartDateTime(new Date()),
        },
      }))
    } finally {
      setTestingId(null)
    }
  }

  const handleLaunchBrowserAuth = async (tech: TechnologySessionItem) => {
    try {
      const res = await fetch('/api/connections/browser-auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tool_id: tech.id }),
      })
      const result = await res.json()
      setBannerFeedback({
        type: 'info',
        message:
          result.message ||
          `Se abrió el navegador para autenticar ${tech.name}. Al terminar, haz clic en "Verificar".`,
      })
      if (!result.browser_opened && tech.auth_url) {
        window.open(tech.auth_url, '_blank', 'noopener,noreferrer')
      }
    } catch {
      if (tech.auth_url) {
        window.open(tech.auth_url, '_blank', 'noopener,noreferrer')
      }
    }
  }

  // Poka-Yoke real-time token format validation
  const getTokenValidationRules = (toolId: string, tokenVal: string) => {
    const trimmed = tokenVal.trim()
    const hasLength = trimmed.length >= 8
    if (toolId === 'resend') {
      return [
        { label: 'Comienza con el prefijo "re_"', valid: trimmed.startsWith('re_') },
        { label: 'Longitud mínima de clave API (12+ caracteres)', valid: trimmed.length >= 12 },
      ]
    }
    if (toolId === 'gh') {
      return [
        {
          label: 'Prefijo estándar de GitHub (ghp_, github_pat_ o gho_)',
          valid:
            trimmed.startsWith('ghp_') ||
            trimmed.startsWith('github_pat_') ||
            trimmed.startsWith('gho_') ||
            trimmed.length >= 20,
        },
        { label: 'Longitud válida de token', valid: hasLength },
      ]
    }
    return [
      { label: 'Token sin espacios al inicio o final', valid: trimmed.length > 0 && !trimmed.includes(' ') },
      { label: 'Longitud mínima de seguridad (8+ caracteres)', valid: hasLength },
    ]
  }

  const handleSubmitCredential = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!authModalTool) return
    setIsSubmittingAuth(true)
    setAuthFeedback(null)

    try {
      const payload: Record<string, string> = { token: authToken.trim() }
      if (authEmail.trim()) payload.email = authEmail.trim()
      if (authDomain.trim()) payload.domain = authDomain.trim()

      const res = await fetch('/api/connections/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool_id: authModalTool.id,
          credentials: payload,
        }),
      })
      const data = await res.json()
      if (data.success) {
        setAuthFeedback({
          success: true,
          message: data.message || 'Credencial guardada y verificada con éxito.',
        })
        setTimeout(() => {
          setAuthModalTool(null)
          setAuthToken('')
          setAuthEmail('')
          setAuthDomain('')
          setAuthFeedback(null)
          fetchConnections()
        }, 1000)
      } else {
        setAuthFeedback({
          success: false,
          message: data.message || data.error || 'No se pudo validar la credencial ingresada.',
        })
      }
    } catch (err) {
      setAuthFeedback({ success: false, message: `Error al comunicar con el servidor: ${err}` })
    } finally {
      setIsSubmittingAuth(false)
    }
  }

  const getTechIcon = (id: string, category: string) => {
    switch (id) {
      case 'agy':
        return <Cpu className="w-5 h-5 text-white" />
      case 'gh':
        return <GitFork className="w-5 h-5 text-white" />
      case 'git':
        return <GitBranch className="w-5 h-5 text-zinc-200" />
      case 'railway':
        return <Server className="w-5 h-5 text-white" />
      case 'supabase':
        return <Database className="w-5 h-5 text-zinc-200" />
      case 'resend':
        return <Mail className="w-5 h-5 text-zinc-200" />
      case 'jira':
        return <ShieldCheck className="w-5 h-5 text-zinc-200" />
      case 'gcloud':
        return <Cloud className="w-5 h-5 text-zinc-200" />
      case 'python':
        return <Code2 className="w-5 h-5 text-white" />
      case 'node':
        return <Terminal className="w-5 h-5 text-zinc-200" />
      case 'docker':
        return <Box className="w-5 h-5 text-white" />
      case 'aws':
        return <Layers className="w-5 h-5 text-zinc-200" />
      default:
        return category === 'runtime' ? (
          <Terminal className="w-5 h-5 text-zinc-400" />
        ) : (
          <Layers className="w-5 h-5 text-zinc-400" />
        )
    }
  }

  const filteredConnections = connections.filter((c) => {
    const matchesCategory =
      selectedCategory === 'all' ||
      (selectedCategory === 'connected' && c.status === 'connected') ||
      (selectedCategory === 'pending' && c.status !== 'connected')

    const matchesSearch =
      c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.account_info && c.account_info.toLowerCase().includes(searchQuery.toLowerCase()))

    return matchesCategory && matchesSearch
  })

  const connectedCount = connections.filter((c) => c.status === 'connected').length
  const unauthCount = connections.filter(
    (c) => c.status === 'unauthenticated' || c.status === 'degraded'
  ).length
  const missingCount = connections.filter((c) => c.status === 'disconnected').length

  return (
    <div className="space-y-6 pb-12 animate-fade-in max-w-6xl mx-auto text-left">
      {/* 1. Header Simplificado (Hick's Law: 1 CTA primario) */}
      <div className="p-5 sm:p-6 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start sm:items-center gap-3.5">
            <div className="w-11 h-11 rounded-xl bg-zinc-900 border border-zinc-700 flex items-center justify-center text-white shrink-0">
              <Key className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white tracking-tight">
                Conexiones Reales del Sistema
              </h1>
              <p className="text-xs text-zinc-400 mt-0.5">
                Verificación en tiempo real de qué herramientas están instaladas y cuáles tienen sesión iniciada en tu PC.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={fetchConnections}
            disabled={isLoading}
            className="px-4 py-2.5 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-bold flex items-center gap-2 transition cursor-pointer shadow-sm disabled:opacity-50 self-start sm:self-auto"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-black ${isLoading ? 'animate-spin' : ''}`} />
            <span>{isLoading ? 'Verificando...' : 'Volver a Verificar Todo'}</span>
          </button>
        </div>

        {/* Resumen de Estado Claro (Visibilidad continua del sistema) */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-3 border-t border-zinc-850 text-xs">
          <div className="p-3.5 rounded-xl bg-black border border-emerald-500/25 flex items-center justify-between">
            <div>
              <span className="text-zinc-400 block text-[11px]">Conectadas y Autenticadas</span>
              <span className="text-lg font-bold text-emerald-400 font-mono mt-0.5 block">
                {connectedCount} listas para usar
              </span>
            </div>
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          </div>

          <div className="p-3.5 rounded-xl bg-black border border-amber-500/25 flex items-center justify-between">
            <div>
              <span className="text-zinc-400 block text-[11px]">Instaladas (Falta Iniciar Sesión)</span>
              <span className="text-lg font-bold text-amber-400 font-mono mt-0.5 block">
                {unauthCount} por conectar
              </span>
            </div>
            <AlertTriangle className="w-5 h-5 text-amber-400" />
          </div>

          <div className="p-3.5 rounded-xl bg-black border border-zinc-800 flex items-center justify-between">
            <div>
              <span className="text-zinc-500 block text-[11px]">No Instaladas en PC</span>
              <span className="text-lg font-bold text-zinc-400 font-mono mt-0.5 block">
                {missingCount} ausentes
              </span>
            </div>
            <XCircle className="w-5 h-5 text-zinc-500" />
          </div>
        </div>
      </div>

      {bannerFeedback && (
        <div className="p-4 rounded-xl bg-zinc-900 border border-zinc-700 text-xs text-white flex items-center justify-between gap-3">
          <span>{bannerFeedback.message}</span>
          <button
            type="button"
            onClick={() => setBannerFeedback(null)}
            className="text-zinc-400 hover:text-white text-xs font-mono"
          >
            Cerrar
          </button>
        </div>
      )}

      {/* 2. Filtros Simples (Reconocimiento antes que recuerdo) */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          {[
            { id: 'all', label: `Todas (${connections.length})` },
            { id: 'connected', label: `Conectadas (${connectedCount})` },
            { id: 'pending', label: `Requieren Atención (${unauthCount + missingCount})` },
          ].map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setSelectedCategory(tab.id)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer ${
                selectedCategory === tab.id
                  ? 'bg-white text-black'
                  : 'bg-zinc-900 text-zinc-400 hover:text-white border border-zinc-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="relative min-w-[240px]">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
          <input
            type="text"
            placeholder="Filtrar por nombre (GitHub, Resend, Railway...)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 rounded-xl bg-zinc-950 border border-zinc-800 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-white transition"
          />
        </div>
      </div>

      {/* 3. Tarjetas de Conexión (Progressive Disclosure para comandos técnicos) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredConnections.map((tech) => {
          const isConnected = tech.status === 'connected'
          const isDisconnected = tech.status === 'disconnected'
          const isTesting = testingId === tech.id
          const testResult = testResults[tech.id]
          const isCopied = copiedId === tech.id
          const showCli = expandedCliId === tech.id

          return (
            <div
              key={tech.id}
              className={`p-5 rounded-2xl bg-zinc-950 border transition flex flex-col justify-between space-y-4 ${
                isConnected
                  ? 'border-zinc-800 hover:border-zinc-700'
                  : isDisconnected
                  ? 'border-zinc-900 opacity-75'
                  : 'border-amber-500/30 hover:border-amber-500/50'
              }`}
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-zinc-900 border border-zinc-800 flex items-center justify-center shrink-0">
                      {getTechIcon(tech.id, tech.category)}
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-white">{tech.name}</h3>
                      <span className="text-[11px] font-mono text-zinc-500 block mt-0.5 truncate max-w-[180px]">
                        {tech.version || tech.id}
                      </span>
                    </div>
                  </div>

                  {isConnected ? (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 shrink-0">
                      <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                      CONECTADO
                    </span>
                  ) : isDisconnected ? (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-zinc-900 text-zinc-400 border border-zinc-800 shrink-0">
                      <XCircle className="w-3 h-3 text-zinc-500" />
                      NO INSTALADO
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-amber-500/15 text-amber-300 border border-amber-500/30 shrink-0">
                      <AlertTriangle className="w-3 h-3 text-amber-400" />
                      FALTA SESIÓN
                    </span>
                  )}
                </div>

                {/* Estado Real Detectado */}
                <div className="p-3 rounded-xl bg-black border border-zinc-850 text-xs space-y-1">
                  <span className="text-[10px] font-mono uppercase text-zinc-500 block">
                    Estado Real en tu PC:
                  </span>
                  <span className="text-xs text-zinc-200 font-medium block">
                    {tech.account_info || (isConnected ? 'Sesión activa' : 'Sin sesión iniciada')}
                  </span>
                  {!isConnected && tech.error_message && (
                    <span className="text-[11px] text-amber-400/90 block pt-0.5">
                      {tech.error_message}
                    </span>
                  )}
                </div>

                {tech.agent_usage && (
                  <p className="text-xs text-zinc-400 leading-relaxed">{tech.agent_usage}</p>
                )}

                {testResult && (
                  <div
                    className={`p-2.5 rounded-xl text-xs border ${
                      testResult.success
                        ? 'bg-emerald-950/30 border-emerald-500/30 text-emerald-200'
                        : 'bg-amber-950/30 border-amber-500/30 text-amber-200'
                    }`}
                  >
                    <div className="flex items-center justify-between text-[10px] font-mono">
                      <span className="font-bold">
                        {testResult.success ? '✓ VERIFICADO' : '⚠️ REQUIERE ACCIÓN'}
                      </span>
                      <span>{testResult.timestamp}</span>
                    </div>
                    <p className="text-[11px] mt-1">{testResult.message}</p>
                  </div>
                )}
              </div>

              {/* Acciones (Ley de Hick: Acción principal clara + Opciones técnicas ocultas en acordeón) */}
              <div className="space-y-2.5 pt-3 border-t border-zinc-850">
                <div className="flex items-center gap-2">
                  {!isConnected && !isDisconnected ? (
                    <>
                      <button
                        type="button"
                        onClick={() => {
                          setAuthModalTool(tech)
                          setAuthToken('')
                          setAuthFeedback(null)
                        }}
                        className="flex-1 px-3 py-2 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-bold flex items-center justify-center gap-1.5 transition cursor-pointer"
                      >
                        <Key className="w-3.5 h-3.5 text-black" />
                        <span>Conectar con Token</span>
                      </button>
                      {tech.auth_url && (
                        <button
                          type="button"
                          onClick={() => handleLaunchBrowserAuth(tech)}
                          className="px-3 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-750 text-zinc-200 text-xs font-medium flex items-center justify-center gap-1 transition cursor-pointer"
                          title="Abrir web oficial"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </>
                  ) : (
                    <button
                      type="button"
                      onClick={() => handleTestConnection(tech.id)}
                      disabled={isTesting}
                      className="flex-1 px-3 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-750 text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition cursor-pointer disabled:opacity-50"
                    >
                      <RefreshCw className={`w-3.5 h-3.5 ${isTesting ? 'animate-spin' : ''}`} />
                      <span>{isTesting ? 'Verificando...' : 'Probar Conexión'}</span>
                    </button>
                  )}
                </div>

                {/* Divulgación Progresiva: Comando CLI oculto por defecto */}
                <div>
                  <button
                    type="button"
                    onClick={() => setExpandedCliId(showCli ? null : tech.id)}
                    className="w-full flex items-center justify-between text-[11px] text-zinc-500 hover:text-zinc-300 pt-1 transition cursor-pointer"
                  >
                    <span className="flex items-center gap-1">
                      <Terminal className="w-3 h-3" />
                      Ver comando de consola
                    </span>
                    {showCli ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>

                  {showCli && (
                    <div
                      onClick={() => copyCliCommand(tech.id, tech.cli_command || `${tech.id} --version`)}
                      className="mt-2 p-2.5 rounded-xl bg-black border border-zinc-800 hover:border-zinc-600 font-mono text-[11px] text-zinc-200 flex items-center justify-between cursor-pointer transition"
                    >
                      <code className="truncate">{tech.cli_command || `${tech.id} --version`}</code>
                      <span className="text-[10px] text-zinc-400 shrink-0 ml-2 flex items-center gap-1">
                        {isCopied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                        {isCopied ? 'Copiado' : 'Copiar'}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* 4. Modal con Validación en Tiempo Real (Poka-Yoke) */}
      {authModalTool && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
          <div className="w-full max-w-md bg-zinc-950 border border-zinc-800 rounded-2xl p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-zinc-900 border border-zinc-700 flex items-center justify-center text-white">
                  <Lock className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">Conectar {authModalTool.name}</h3>
                  <span className="text-[11px] text-zinc-400">
                    La clave se activará de inmediato en tu sesión local
                  </span>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setAuthModalTool(null)}
                className="w-8 h-8 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-white flex items-center justify-center transition cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSubmitCredential} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-zinc-200 block">
                  Token o API Key de {authModalTool.name}
                </label>
                <input
                  type="password"
                  autoFocus
                  required
                  placeholder={
                    authModalTool.id === 'resend'
                      ? 're_3GoppTX7_...'
                      : authModalTool.id === 'gh'
                      ? 'ghp_...'
                      : 'Pega aquí tu token de acceso...'
                  }
                  value={authToken}
                  onChange={(e) => setAuthToken(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-black border border-zinc-700 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-white font-mono"
                />
              </div>

              {/* Reglas Poka-Yoke en tiempo real que se marcan en verde mientras escribe */}
              <div className="p-3 rounded-xl bg-black border border-zinc-850 space-y-1.5">
                <span className="text-[10px] font-mono uppercase text-zinc-500 block">
                  Verificación de formato en tiempo real:
                </span>
                {getTokenValidationRules(authModalTool.id, authToken).map((rule, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-xs">
                    <CheckCircle2
                      className={`w-3.5 h-3.5 shrink-0 transition ${
                        rule.valid ? 'text-emerald-400' : 'text-zinc-600'
                      }`}
                    />
                    <span className={rule.valid ? 'text-emerald-300 font-medium' : 'text-zinc-500'}>
                      {rule.label}
                    </span>
                  </div>
                ))}
              </div>

              {authModalTool.id === 'jira' && (
                <div className="space-y-3 pt-1">
                  <div className="space-y-1">
                    <label className="text-xs font-semibold text-zinc-300 block">
                      Correo de tu cuenta Atlassian
                    </label>
                    <input
                      type="email"
                      placeholder="tu@correo.com"
                      value={authEmail}
                      onChange={(e) => setAuthEmail(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl bg-black border border-zinc-800 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-white font-mono"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs font-semibold text-zinc-300 block">
                      Dominio Jira (ej: miempresa.atlassian.net)
                    </label>
                    <input
                      type="text"
                      placeholder="miempresa.atlassian.net"
                      value={authDomain}
                      onChange={(e) => setAuthDomain(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl bg-black border border-zinc-800 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-white font-mono"
                    />
                  </div>
                </div>
              )}

              {authFeedback && (
                <div
                  className={`p-3 rounded-xl text-xs border ${
                    authFeedback.success
                      ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-200'
                      : 'bg-red-950/40 border-red-500/40 text-red-200'
                  }`}
                >
                  {authFeedback.message}
                </div>
              )}

              <div className="flex items-center justify-between pt-2 border-t border-zinc-850">
                {authModalTool.auth_url ? (
                  <button
                    type="button"
                    onClick={() => handleLaunchBrowserAuth(authModalTool)}
                    className="text-xs text-zinc-400 hover:text-white flex items-center gap-1 underline cursor-pointer"
                  >
                    <ExternalLink className="w-3 h-3" />
                    Obtener token en la web
                  </button>
                ) : (
                  <span />
                )}

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setAuthModalTool(null)}
                    className="px-3.5 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 text-zinc-300 text-xs transition cursor-pointer"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={
                      isSubmittingAuth ||
                      !getTokenValidationRules(authModalTool.id, authToken).every((r) => r.valid)
                    }
                    className="px-4 py-2 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-bold transition cursor-pointer disabled:opacity-40"
                  >
                    {isSubmittingAuth ? 'Conectando...' : 'Guardar y Conectar'}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
