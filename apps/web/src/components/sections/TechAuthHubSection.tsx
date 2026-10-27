import React, { useState, useEffect } from 'react'
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
  const [testResults, setTestResults] = useState<Record<string, { success: boolean; message: string; timestamp: string }>>({})
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState<string>('')
  
  // Auth Credential Modal state
  const [authModalTool, setAuthModalTool] = useState<TechnologySessionItem | null>(null)
  const [authToken, setAuthToken] = useState<string>('')
  const [authEmail, setAuthEmail] = useState<string>('')
  const [authDomain, setAuthDomain] = useState<string>('')
  const [isSubmittingAuth, setIsSubmittingAuth] = useState<boolean>(false)
  const [authFeedback, setAuthFeedback] = useState<{ success: boolean; message: string } | null>(null)

  // Fetch connections from real backend
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

  // 1-Click Copy CLI Command
  const copyCliCommand = (toolId: string, cmd: string) => {
    navigator.clipboard.writeText(cmd)
    setCopiedId(toolId)
    setTimeout(() => {
      setCopiedId(null)
    }, 2200)
  }

  // Live test connection endpoint call
  const handleTestConnection = async (toolId: string) => {
    setTestingId(toolId)
    try {
      const res = await fetch('/api/connections/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tool_id: toolId }),
      })
      const result = await res.json()
      const isSuccess = result.success || (result.connection && result.connection.status === 'connected')
      const msg = result.connection?.account_info || (isSuccess ? 'Sesión verificada correctamente con el ejecutable local.' : (result.connection?.error_message || 'Sesión no autenticada o binario ausente.'))
      
      setTestResults((prev) => ({
        ...prev,
        [toolId]: {
          success: !!isSuccess,
          message: msg,
          timestamp: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        },
      }))
      // Refresh state
      fetchConnections()
    } catch (err) {
      setTestResults((prev) => ({
        ...prev,
        [toolId]: {
          success: false,
          message: `Error al ejecutar prueba de diagnóstico: ${err}`,
          timestamp: new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        },
      }))
    } finally {
      setTestingId(null)
    }
  }

  // Web Browser / OAuth Auth Trigger
  const handleLaunchBrowserAuth = async (tech: TechnologySessionItem) => {
    try {
      const res = await fetch('/api/connections/browser-auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tool_id: tech.id }),
      })
      const result = await res.json()
      if (result.browser_opened || result.success) {
        alert(`Navegador iniciado para autenticar ${tech.name}. Complete el inicio de sesión y luego pulse "Probar Sesión CLI".`)
      } else if (tech.auth_url) {
        window.open(tech.auth_url, '_blank', 'noopener,noreferrer')
      }
    } catch (e) {
      if (tech.auth_url) {
        window.open(tech.auth_url, '_blank', 'noopener,noreferrer')
      }
    }
  }

  // Submit Credential Form
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
        setAuthFeedback({ success: true, message: data.message || 'Credencial guardada y sesión validada con éxito.' })
        setTimeout(() => {
          setAuthModalTool(null)
          setAuthToken('')
          setAuthEmail('')
          setAuthDomain('')
          setAuthFeedback(null)
          fetchConnections()
        }, 1500)
      } else {
        setAuthFeedback({ success: false, message: data.message || data.error || 'No se pudo validar la credencial ingresada.' })
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
        return category === 'runtime' ? <Terminal className="w-5 h-5 text-zinc-400" /> : <Layers className="w-5 h-5 text-zinc-400" />
    }
  }

  // Filter list
  const filteredConnections = connections.filter((c) => {
    const matchesCategory =
      selectedCategory === 'all' ||
      (selectedCategory === 'ai' && c.category === 'ai') ||
      (selectedCategory === 'vcs' && c.category === 'vcs') ||
      (selectedCategory === 'cloud' && (c.category === 'cloud' || c.category === 'infra')) ||
      (selectedCategory === 'database' && c.category === 'database') ||
      (selectedCategory === 'governance' && (c.category === 'governance' || c.category === 'notifications')) ||
      (selectedCategory === 'runtime' && (c.category === 'runtime' || c.category === 'infra' && c.id === 'docker'))

    const matchesSearch =
      c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.agent_usage && c.agent_usage.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (c.account_info && c.account_info.toLowerCase().includes(searchQuery.toLowerCase()))

    return matchesCategory && matchesSearch
  })

  const connectedCount = connections.filter((c) => c.status === 'connected').length
  const pendingCount = connections.length - connectedCount

  return (
    <div className="space-y-6 pb-12 animate-fade-in max-w-7xl mx-auto">
      {/* 1. Top Section Header */}
      <div className="p-4 sm:p-6 rounded-2xl bg-zinc-950 border border-zinc-800 space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="flex items-start sm:items-center gap-3">
            <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-zinc-900 border border-zinc-700 flex items-center justify-center text-white shrink-0">
              <Key className="w-5 h-5 sm:w-6 sm:h-6" />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="text-base sm:text-lg lg:text-xl font-bold text-white tracking-wide">
                  Sesiones CLI & Autenticación de Tecnologías
                </h1>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-white text-black border border-white">
                  12 Plataformas SACL
                </span>
              </div>
              <p className="text-xs sm:text-sm text-zinc-400 mt-1 max-w-2xl">
                Controle el estado de autenticación, credenciales de entorno y comandos CLI para que los agentes autónomos operen en local sobre cada tecnología de la suite.
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            <button
              type="button"
              id="btn-refresh-all-tech"
              onClick={fetchConnections}
              disabled={isLoading}
              className="px-3.5 py-2 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-bold font-mono flex items-center gap-2 transition cursor-pointer shadow-sm disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 text-black ${isLoading ? 'animate-spin' : ''}`} />
              <span>Verificar Todas en Local</span>
            </button>
          </div>
        </div>

        {/* Live Metrics Row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 pt-3 border-t border-zinc-850 text-xs">
          <div className="p-3 rounded-xl bg-black border border-zinc-800">
            <span className="text-zinc-500 block text-[11px] font-mono uppercase">Total Tecnologías</span>
            <span className="text-base font-bold text-white font-mono mt-0.5 block">{connections.length}</span>
          </div>
          <div className="p-3 rounded-xl bg-black border border-zinc-800">
            <span className="text-zinc-500 block text-[11px] font-mono uppercase">Sesiones Activas</span>
            <span className="text-base font-bold text-white font-mono mt-0.5 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-white animate-pulse" />
              {connectedCount} Verificadas
            </span>
          </div>
          <div className="p-3 rounded-xl bg-black border border-zinc-800">
            <span className="text-zinc-500 block text-[11px] font-mono uppercase">Pendientes / Inactivas</span>
            <span className="text-base font-bold text-zinc-400 font-mono mt-0.5 block">{pendingCount}</span>
          </div>
          <div className="p-3 rounded-xl bg-black border border-zinc-800">
            <span className="text-zinc-500 block text-[11px] font-mono uppercase">Dirty-Root Guard</span>
            <span className="text-base font-bold text-white font-mono mt-0.5 block">100% Hermético</span>
          </div>
        </div>
      </div>

      {/* 2. Filters & Search Toolbar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* Category Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0 custom-scroll text-xs">
          {[
            { id: 'all', label: 'Todas (12)' },
            { id: 'ai', label: 'IA & Inferencia' },
            { id: 'vcs', label: 'VCS & Git' },
            { id: 'cloud', label: 'Cloud & PaaS' },
            { id: 'database', label: 'Bases de Datos' },
            { id: 'governance', label: 'Gobernanza' },
            { id: 'runtime', label: 'Runtimes' },
          ].map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-3 py-1.5 rounded-xl whitespace-nowrap transition cursor-pointer text-xs font-medium ${
                selectedCategory === cat.id
                  ? 'bg-white text-black font-bold shadow-sm'
                  : 'bg-zinc-900 text-zinc-400 hover:text-white border border-zinc-800 hover:border-zinc-700'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div className="relative min-w-[220px]">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
          <input
            type="text"
            placeholder="Buscar tecnología o comando..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 rounded-xl bg-zinc-950 border border-zinc-800 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-white transition"
          />
        </div>
      </div>

      {/* 3. Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {filteredConnections.map((tech) => {
          const isConnected = tech.status === 'connected'
          const isTesting = testingId === tech.id
          const testResult = testResults[tech.id]
          const isCopied = copiedId === tech.id

          return (
            <div
              key={tech.id}
              id={`card-tech-${tech.id}`}
              className="p-4 sm:p-5 rounded-2xl bg-zinc-950 border border-zinc-800 hover:border-zinc-700 transition flex flex-col justify-between space-y-4 shadow-lg group"
            >
              {/* Header: Icon, Name, Badge */}
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-zinc-900 border border-zinc-800 flex items-center justify-center shrink-0 group-hover:border-zinc-600 transition">
                      {getTechIcon(tech.id, tech.category)}
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-white block group-hover:text-zinc-100 transition">
                        {tech.name}
                      </h3>
                      <span className="text-[11px] font-mono text-zinc-400 block mt-0.5 truncate max-w-[190px]">
                        {tech.version || tech.id}
                      </span>
                    </div>
                  </div>

                  {/* Status Badge */}
                  {isConnected ? (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-white text-black border border-white shrink-0">
                      <span className="w-1.5 h-1.5 rounded-full bg-black animate-pulse" />
                      CONECTADO
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-zinc-900 text-zinc-300 border border-zinc-700 shrink-0">
                      <AlertTriangle className="w-3 h-3 text-zinc-400" />
                      SIN AUTENTICAR
                    </span>
                  )}
                </div>

                {/* Account / Session Info */}
                <div className="p-2.5 rounded-xl bg-black border border-zinc-850 text-xs">
                  <span className="text-[10px] font-mono uppercase text-zinc-500 block">Sesión en Host</span>
                  <span className="text-xs text-zinc-200 font-mono block mt-0.5 truncate">
                    {tech.account_info || (isConnected ? 'Sesión local detectada en PATH' : 'No se detecta sesión activa en el entorno')}
                  </span>
                </div>

                {/* Agent Usage description */}
                {tech.agent_usage && (
                  <div className="text-xs text-zinc-400 leading-relaxed bg-zinc-900/50 p-2.5 rounded-xl border border-zinc-850">
                    <span className="text-[10px] font-mono uppercase text-zinc-500 block mb-1">
                      Uso por Agentes Locales:
                    </span>
                    <p className="text-[11px] text-zinc-300">
                      {tech.agent_usage}
                    </p>
                  </div>
                )}
              </div>

              {/* Dedicated CLI Snippet Box */}
              <div className="space-y-3 pt-2 border-t border-zinc-850">
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-[11px] font-mono text-zinc-400">
                    <span className="flex items-center gap-1.5 text-zinc-300">
                      <Terminal className="w-3.5 h-3.5 text-zinc-400" />
                      Comando CLI para Agentes:
                    </span>
                    <button
                      type="button"
                      onClick={() => copyCliCommand(tech.id, tech.cli_command || `${tech.id} --version`)}
                      className="inline-flex items-center gap-1 text-[10px] text-zinc-400 hover:text-white transition cursor-pointer font-bold"
                      title="Copiar comando"
                    >
                      {isCopied ? (
                        <>
                          <Check className="w-3 h-3 text-white" />
                          <span className="text-white">¡Copiado!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          <span>Copiar</span>
                        </>
                      )}
                    </button>
                  </div>

                  {/* Monospace Command Bar */}
                  <div
                    onClick={() => copyCliCommand(tech.id, tech.cli_command || `${tech.id} --version`)}
                    className="p-2.5 rounded-xl bg-black border border-zinc-800 hover:border-zinc-600 font-mono text-[11px] text-white flex items-center justify-between cursor-pointer transition select-all overflow-x-auto custom-scroll"
                  >
                    <code className="whitespace-nowrap">{tech.cli_command || `${tech.id} --version`}</code>
                    <Copy className="w-3.5 h-3.5 text-zinc-500 ml-2 shrink-0 group-hover:text-white transition" />
                  </div>
                </div>

                {/* Inline Test Result if executed */}
                {testResult && (
                  <div
                    className={`p-2.5 rounded-xl text-xs border ${
                      testResult.success
                        ? 'bg-zinc-900 border-zinc-700 text-zinc-200'
                        : 'bg-zinc-900 border-zinc-750 text-zinc-300'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-1 text-[10px] font-mono text-zinc-400">
                      <span className="flex items-center gap-1 font-bold">
                        {testResult.success ? (
                          <CheckCircle2 className="w-3 h-3 text-white" />
                        ) : (
                          <AlertTriangle className="w-3 h-3 text-zinc-400" />
                        )}
                        {testResult.success ? 'DIAGNÓSTICO EXITOSO' : 'DIAGNÓSTICO FALLIDO'}
                      </span>
                      <span>{testResult.timestamp}</span>
                    </div>
                    <p className="text-[11px] mt-1 font-mono truncate">{testResult.message}</p>
                  </div>
                )}

                {/* Action Buttons Toolbar */}
                <div className="grid grid-cols-2 gap-2 pt-1">
                  <button
                    type="button"
                    onClick={() => handleTestConnection(tech.id)}
                    disabled={isTesting}
                    className="px-3 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-750 text-white text-xs font-mono font-medium flex items-center justify-center gap-1.5 transition cursor-pointer disabled:opacity-50"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 text-zinc-300 ${isTesting ? 'animate-spin' : ''}`} />
                    <span>{isTesting ? 'Probando...' : 'Probar Sesión'}</span>
                  </button>

                  {tech.auth_url ? (
                    <button
                      type="button"
                      onClick={() => handleLaunchBrowserAuth(tech)}
                      className="px-3 py-2 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-mono font-bold flex items-center justify-center gap-1.5 transition cursor-pointer"
                    >
                      <ExternalLink className="w-3.5 h-3.5 text-black" />
                      <span>Iniciar Sesión</span>
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={() => {
                        setAuthModalTool(tech)
                        setAuthToken('')
                        setAuthFeedback(null)
                      }}
                      className="px-3 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-750 text-zinc-200 text-xs font-mono font-medium flex items-center justify-center gap-1.5 transition cursor-pointer"
                    >
                      <Lock className="w-3.5 h-3.5 text-zinc-400" />
                      <span>Configurar Token</span>
                    </button>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* 4. Modal for Credential Setup */}
      {authModalTool && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
          <div className="w-full max-w-md bg-zinc-950 border border-zinc-800 rounded-2xl p-5 sm:p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-zinc-900 border border-zinc-700 flex items-center justify-center text-white">
                  <Lock className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">Configurar Credencial</h3>
                  <span className="text-[11px] font-mono text-zinc-400">{authModalTool.name}</span>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setAuthModalTool(null)}
                className="w-8 h-8 rounded-xl bg-zinc-900 hover:bg-zinc-850 text-zinc-400 hover:text-white flex items-center justify-center transition"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSubmitCredential} className="space-y-3.5">
              <p className="text-xs text-zinc-400 leading-relaxed">
                Ingrese el token de API o clave de sesión para {authModalTool.name}. El token quedará activo en la memoria del orquestador para ejecuciones de agentes.
              </p>

              <div className="space-y-1">
                <label className="text-[11px] font-mono text-zinc-300 block">Token / Clave de API</label>
                <input
                  type="password"
                  required
                  placeholder="Ingrese token (ej: re_3G... o ghp_...)"
                  value={authToken}
                  onChange={(e) => setAuthToken(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-black border border-zinc-800 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-white font-mono"
                />
              </div>

              {authModalTool.id === 'jira' && (
                <>
                  <div className="space-y-1">
                    <label className="text-[11px] font-mono text-zinc-300 block">Email de Atlassian</label>
                    <input
                      type="email"
                      placeholder="usuario@empresa.com"
                      value={authEmail}
                      onChange={(e) => setAuthEmail(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl bg-black border border-zinc-800 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-white font-mono"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[11px] font-mono text-zinc-300 block">Dominio Atlassian (opcional)</label>
                    <input
                      type="text"
                      placeholder="mi-empresa.atlassian.net"
                      value={authDomain}
                      onChange={(e) => setAuthDomain(e.target.value)}
                      className="w-full px-3 py-2 rounded-xl bg-black border border-zinc-800 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-white font-mono"
                    />
                  </div>
                </>
              )}

              {authFeedback && (
                <div
                  className={`p-3 rounded-xl text-xs font-mono border ${
                    authFeedback.success
                      ? 'bg-zinc-900 border-zinc-700 text-zinc-200'
                      : 'bg-zinc-900 border-zinc-750 text-zinc-300'
                  }`}
                >
                  {authFeedback.message}
                </div>
              )}

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-zinc-850">
                <button
                  type="button"
                  onClick={() => setAuthModalTool(null)}
                  className="px-3.5 py-2 rounded-xl bg-zinc-900 hover:bg-zinc-850 text-zinc-300 text-xs font-mono transition cursor-pointer"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingAuth || !authToken.trim()}
                  className="px-4 py-2 rounded-xl bg-white hover:bg-zinc-200 text-black text-xs font-mono font-bold transition cursor-pointer disabled:opacity-50"
                >
                  {isSubmittingAuth ? 'Validando...' : 'Guardar y Verificar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
