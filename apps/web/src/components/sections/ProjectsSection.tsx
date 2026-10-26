import React, { useState, useEffect } from 'react'
import {
  FolderGit2,
  GitBranch,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Terminal,
  ShieldCheck,
  ExternalLink,
} from 'lucide-react'
import type { Project } from '../../types/orchestrator'

interface ProjectsSectionProps {
  projects: Project[]
}

export const ProjectsSection: React.FC<ProjectsSectionProps> = ({ projects: initialProjects }) => {
  const [projects, setProjects] = useState<Project[]>(initialProjects)
  const [preflightOutput, setPreflightOutput] = useState<string | null>(null)
  const [runningPreflight, setRunningPreflight] = useState(false)

  const repoList = [
    {
      name: 'Stable-Ecommerce',
      path: 'runs/impl-20261007-203727-e69378/worktrees/integration',
      branch: 'sacl-implementation-impl-20261007-203727-e69378',
      contracts: ['DR-INV-001', 'DR-PAY-001'],
      isClean: true,
      role: 'Principal E-commerce Storefront & Inventory',
    },
    {
      name: 'FULL-METAL-CASH',
      path: 'C:/Users/Lucilfer/Documents/FULL-METAL-CASH',
      branch: 'main',
      contracts: ['DR-PAY-001', 'DR-REC-001'],
      isClean: true,
      role: 'POS & Cash Management Engine',
    },
    {
      name: 'solidbit-agent-execution-control-loop',
      path: 'C:/Users/Lucilfer/Documents/SolidBit-SACL',
      branch: 'main',
      contracts: ['DR-IDEM-001', 'DR-AUTH-001'],
      isClean: true,
      role: 'Host Multi-Agent Orchestrator (SACL Core)',
    },
  ]

  const handleRunPreflight = async () => {
    setRunningPreflight(true)
    try {
      const res = await fetch('/api/orchestrator/context')
      const data = await res.json()
      setPreflightOutput(
        `[PREFLIGHT PASS]\n- Repositorio activo: ${data.active_project?.name}\n- Rama Git: ${data.active_project?.branch}\n- Hash Commit: ${data.active_project?.commit}\n- Estado Worktree: ${data.active_project?.is_clean ? 'LIMPIO (0 archivos sucios)' : 'ARCHIVOS SIN COMMITEAR'}\n- Conexión Jira: ${data.jira_connection?.status}`
      )
    } catch (e: any) {
      setPreflightOutput(`Error de preflight: ${e.message}`)
    } finally {
      setRunningPreflight(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-3xl bg-[#0e141d] border border-[#1b2533]">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold text-white tracking-wide">
              Gestor Multi-Repositorio & Worktrees de Proyecto
            </h1>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              3 Repositorios SolidBit
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Aislamiento estricto de ramas y verificación de invariante Dirty-Root antes de mutación
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleRunPreflight}
            disabled={runningPreflight}
            className="px-4 py-2 rounded-2xl bg-emerald-500 hover:bg-emerald-400 text-black font-bold text-xs flex items-center gap-1.5 transition cursor-pointer shadow-lg shadow-emerald-500/10"
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>{runningPreflight ? 'Verificando...' : 'Ejecutar Preflight'}</span>
          </button>
        </div>
      </div>

      {/* Preflight Terminal Output */}
      {preflightOutput && (
        <div className="p-4 rounded-3xl bg-[#090e16] border border-emerald-500/30 space-y-2">
          <div className="flex items-center gap-2 text-emerald-400 text-xs font-mono font-bold">
            <Terminal className="w-4 h-4" />
            <span>Resultado de Preflight Soberano</span>
          </div>
          <pre className="font-mono text-xs text-zinc-300 whitespace-pre-wrap">
            {preflightOutput}
          </pre>
        </div>
      )}

      {/* Projects Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {repoList.map((repo, idx) => (
          <div
            key={idx}
            className="p-5 rounded-3xl bg-[#0e141d] border border-[#1b2533] space-y-4 hover:border-zinc-700 transition"
          >
            <div className="flex items-start justify-between">
              <div className="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <FolderGit2 className="w-5 h-5" />
              </div>
              <span className="flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <CheckCircle2 className="w-3 h-3" />
                Worktree Limpio
              </span>
            </div>

            <div>
              <h3 className="text-sm font-bold text-white">{repo.name}</h3>
              <p className="text-[11px] text-zinc-400 mt-0.5">{repo.role}</p>
            </div>

            <div className="p-3 rounded-2xl bg-black/40 border border-white/5 space-y-1.5 font-mono text-[11px]">
              <div className="flex items-center justify-between text-zinc-400">
                <span>Rama:</span>
                <span className="text-white truncate max-w-[150px]">{repo.branch}</span>
              </div>
              <div className="flex items-center justify-between text-zinc-400">
                <span>Contratos:</span>
                <span className="text-emerald-400">{repo.contracts.join(', ')}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
