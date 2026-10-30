import { useState, useEffect, useCallback } from 'react'
import { Header } from './components/Header'
import { LeftSidebar } from './components/LeftSidebar'
import { CenterDashboard } from './components/CenterDashboard'
import { PersistentTelemetryDrawer } from './components/PersistentTelemetryDrawer'
import { InteractivePipelineStepper } from './components/InteractivePipelineStepper'
import { MobileDrawer } from './components/MobileDrawer'
import { MobileBottomNav } from './components/MobileBottomNav'
import { SprintDesignerModal } from './components/SprintDesignerModal'
import { Breadcrumbs } from './components/Breadcrumbs'
import { NetworkStatusBanner } from './components/NetworkStatusBanner'
import { ChatSection } from './components/sections/ChatSection'
import { RoadmapSection } from './components/sections/RoadmapSection'
import { AgentsSection } from './components/sections/AgentsSection'
import { ExecutionsSection } from './components/sections/ExecutionsSection'
import { ProjectsSection } from './components/sections/ProjectsSection'
import { ReportsSection } from './components/sections/ReportsSection'
import { SettingsSection } from './components/sections/SettingsSection'
import { WorkflowsSection } from './components/sections/WorkflowsSection'
import { TechAuthHubSection } from './components/sections/TechAuthHubSection'
import { EmailGatewaySection } from './components/sections/EmailGatewaySection'
import { JiraSection } from './components/sections/JiraSection'
import { DiffInspectorModal } from './components/DiffInspectorModal'
import { CommandPaletteModal } from './components/CommandPaletteModal'
import { deriveDomainState } from './types/domainState'
import type { TaskItem, AgentItem, CommitItem, Project, ActivityEvent } from './types/orchestrator'
import type { TechnologyItem } from './components/ConnectedTechnologiesMatrix'

export default function App() {
  const [currentSection, setCurrentSection] = useState<string>(() => {
    const hash = window.location.hash.replace('#', '')
    const valid = [
      'dashboard',
      'chat',
      'sprint',
      'jira',
      'connections',
      'workflows',
      'designer',
      'roadmap',
      'agents',
      'gates',
      'executions',
      'projects',
      'email',
      'database',
      'reports',
      'github',
      'settings',
    ]
    return valid.includes(hash) ? hash : 'dashboard'
  })

  const [isSprintModalOpen, setIsSprintModalOpen] = useState<boolean>(false)
  const [isMobileDrawerOpen, setIsMobileDrawerOpen] = useState<boolean>(false)
  const [isDiffModalOpen, setIsDiffModalOpen] = useState<boolean>(false)
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState<boolean>(false)
  const [projectName, setProjectName] = useState<string>('Tienda Online (Stable-Ecommerce)')
  const [activeBranch, setActiveBranch] = useState<string>('worktrees/scheduler')
  const [selectedJiraTicketForSprint, setSelectedJiraTicketForSprint] = useState<any | null>(null)

  // Dynamic state loaded strictly from backend APIs
  const [tasks, setTasks] = useState<TaskItem[]>([])
  const [agents, setAgents] = useState<AgentItem[]>([])
  const [connections, setConnections] = useState<TechnologyItem[]>([])
  const [commits, setCommits] = useState<CommitItem[]>([])
  const [projects, setProjects] = useState<Project[]>([
    {
      id: 'stable-ecommerce',
      name: 'Tienda Online (Stable-Ecommerce)',
      is_active: true,
      branch: 'worktrees/scheduler',
    } as any,
  ])
  const [events, setEvents] = useState<ActivityEvent[]>([])
  const [pendingGatesCount, setPendingGatesCount] = useState<number>(0)

  // Explicit Finite State Machine (FSM) Flags
  const [hasConflict, setHasConflict] = useState<boolean>(false)
  const [conflictReason, setConflictReason] = useState<string | null>(null)
  const [isExecuting, setIsExecuting] = useState<boolean>(false)
  const [recentlyCompleted, setRecentlyCompleted] = useState<boolean>(false)

  const loadData = async () => {
    try {
      const ctxRes = await fetch('/api/orchestrator/context')
      const ctxData = await ctxRes.json()
      if (ctxData.active_project?.name) {
        setProjectName(ctxData.active_project.name)
      }
      if (ctxData.active_project?.branch) {
        setActiveBranch(ctxData.active_project.branch)
      } else {
        setActiveBranch('worktrees/scheduler')
      }

      if (ctxData.jira_backlog && ctxData.jira_backlog.length > 0) {
        const now = new Date()
        const sprintStart = now.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
        const sprintEnd = new Date(now.getTime() + 14 * 86400000).toLocaleDateString('es-ES', {
          day: 'numeric',
          month: 'short',
        })
        const dynamicTasks: TaskItem[] = ctxData.jira_backlog.map((t: any, i: number) => ({
          id: String(i + 1),
          title: t.title,
          key: t.key,
          agent: t.phase || 'Equipo Principal',
          start: t.start_date || sprintStart,
          end: t.due_date || sprintEnd,
          progress: t.status === 'COMPLETED' ? 100 : t.status === 'IN_PROGRESS' ? 65 : 20,
          status:
            t.status === 'COMPLETED'
              ? 'Completada'
              : t.status === 'En progreso'
              ? 'En progreso'
              : 'Pendiente',
        }))
        setTasks(dynamicTasks)
      }

      const connRes = await fetch('/api/connections')
      const connData = await connRes.json()
      if (connData.connections && connData.connections.length > 0) {
        setConnections(connData.connections)
      }

      try {
        const fleetRes = await fetch('/api/agents/fleet')
        const fleetData = await fleetRes.json()
        if (fleetData && fleetData.active_agents && Array.isArray(fleetData.active_agents)) {
          setAgents(fleetData.active_agents)
        } else {
          setAgents([])
        }
      } catch {
        setAgents([])
      }

      const comRes = await fetch('/api/github/commits?limit=5')
      const comData = await comRes.json()
      if (comData.commits) setCommits(comData.commits)

      const projRes = await fetch('/api/projects')
      const projData = await projRes.json()
      if (projData.projects) {
        setProjects(projData.projects)
        const act = projData.projects.find((p: any) => p.is_active)
        if (act?.branch) setActiveBranch(act.branch)
      }

      const evRes = await fetch('/api/db/rows?table=events&limit=25')
      const evData = await evRes.json()
      if (evData.rows) setEvents(evData.rows)

      try {
        const gatesRes = await fetch('/api/gates/pending')
        const gatesData = await gatesRes.json()
        setPendingGatesCount(Number(gatesData.count ?? (gatesData.gates?.length || 0)))
      } catch {
        setPendingGatesCount(0)
      }
    } catch (e) {
      console.warn('Backend loading warning:', e)
    }
  }

  useEffect(() => {
    if (window.location.hash.replace('#', '') !== currentSection) {
      window.location.hash = currentSection
    }
  }, [currentSection])

  useEffect(() => {
    const handleHash = () => {
      const h = window.location.hash.replace('#', '')
      if (h && h !== currentSection) setCurrentSection(h)
    }
    window.addEventListener('hashchange', handleHash)
    return () => window.removeEventListener('hashchange', handleHash)
  }, [currentSection])

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        setIsCommandPaletteOpen((prev) => !prev)
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [])

  // Event Sourcing: Ingest incoming FSM and Telemetry events immutably (UI = f(State))
  const handleFSMEvent = useCallback((rawPayload: any) => {
    if (!rawPayload) return
    const payload =
      typeof rawPayload === 'string'
        ? (() => {
            try {
              return JSON.parse(rawPayload)
            } catch {
              return { message: rawPayload }
            }
          })()
        : rawPayload

    // 1. Immutable Agent state transition (e.g. Agent: Vega, Status: PASS, Commit: b9a448f9)
    if (payload.agent || payload.agent_id || payload.agent_name) {
      const agentName = payload.agent || payload.agent_id || payload.agent_name
      const agentStatus = payload.status || 'PASS'

      setAgents((prev) => {
        const idx = prev.findIndex(
          (a) =>
            a.name.toLowerCase() === String(agentName).toLowerCase() ||
            a.id.toLowerCase() === String(agentName).toLowerCase()
        )
        const updated: AgentItem = {
          id: idx >= 0 ? prev[idx].id : String(agentName).toLowerCase(),
          name: agentName,
          role: idx >= 0 ? prev[idx].role : 'Autonomous Verification Specialist',
          status: agentStatus,
          status_type: agentStatus,
          color:
            agentStatus === 'PASS' || agentStatus === 'Completado'
              ? 'emerald'
              : agentStatus === 'ERROR'
              ? 'red'
              : 'amber',
          commit_sha:
            payload.commit || payload.commit_sha || (idx >= 0 ? prev[idx].commit_sha : undefined),
          current_task: payload.task || payload.message || 'Verificación FSM completada',
          last_active: 'Justo ahora',
        }
        if (idx >= 0) {
          const next = [...prev]
          next[idx] = { ...next[idx], ...updated }
          return next
        }
        return [updated, ...prev]
      })
    }

    // 2. Immutable Commit state transition
    if (payload.commit || payload.commit_sha) {
      const sha = payload.commit || payload.commit_sha
      setCommits((prev) => {
        if (prev.some((c) => c.sha === sha)) return prev
        const newCommit: CommitItem = {
          sha,
          message: payload.message || `Automated verify from ${payload.agent || 'Agent'}`,
          author: payload.agent || 'SACL Operator',
          time: new Date().toLocaleTimeString('es-ES'),
        }
        return [newCommit, ...prev]
      })
    }

    // 3. Immutable Activity Event ingestion for FSM Console
    const newActivityEvent: ActivityEvent = {
      event_id: Date.now(),
      event_type: payload.status || payload.event_type || 'FSM_EVENT',
      severity:
        payload.status === 'ERROR'
          ? 'ERROR'
          : payload.status === 'BLOCKED'
          ? 'WARN'
          : 'INFO',
      payload_json: typeof payload === 'string' ? payload : JSON.stringify(payload),
      created_at: new Date().toISOString(),
    }
    setEvents((prev) => [newActivityEvent, ...prev.slice(0, 49)])
  }, [])

  const handleAtomicProjectTeardown = useCallback(
    async (removedProjId: string) => {
      // 1. Audit active project vs removed project
      const currentActive =
        projects.find((p) => (p.id === removedProjId || p.path === removedProjId) && p.is_active) ||
        (projects.length > 0 && (projects[0].id === removedProjId || projects[0].path === removedProjId))

      const remainingProjects = projects.filter(
        (p) => p.id !== removedProjId && p.path !== removedProjId
      )

      if (currentActive) {
        // 2. ATOMIC CASCADING TEARDOWN:
        // Reset all derived and state variables in a single synchronous commit
        // No dangling tasks, no stale activeBranch, no ghost commits or agent states
        const nextActive = remainingProjects[0] || null

        setProjects(remainingProjects)
        setProjectName(nextActive?.name || 'Orquestador SACL')
        setActiveBranch(nextActive?.branch || 'worktrees/scheduler')
        setTasks([])
        setAgents([])
        setCommits([])
        setEvents([])
        setHasConflict(false)
        setConflictReason(null)
        setIsExecuting(false)
        setPendingGatesCount(0)

        // 3. Side-Effect Cleanup Phase: Call Daemon to prune isolated git worktrees
        try {
          await fetch('/api/actions/execute', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'x-git-branch': nextActive?.branch || 'main',
              'x-worktree-path': nextActive?.path || '.',
              'x-commit-sha': 'HEAD',
            },
            body: JSON.stringify({
              action: 'release_worktree',
              action_type: 'release_worktree',
              params: {
                clean_worktrees: true,
                worktree_path: nextActive?.path || '.',
                git_branch: nextActive?.branch || 'main',
              },
              context: {
                git_branch: nextActive?.branch || 'main',
                worktree_path: nextActive?.path || '.',
              },
            }),
          })
        } catch (err) {
          console.warn('Worktree cleanup notice:', err)
        }
      } else {
        setProjects(remainingProjects)
      }

      await loadData()
    },
    [projects]
  )


  useEffect(() => {
    loadData()

    // Expose test hooks for E2E automation (Playwright / integration tests)
    ;(window as any).__INJECT_FSM_EVENT__ = (data: any) => handleFSMEvent(data)
    const onCustomEvent = (e: any) => handleFSMEvent(e.detail)
    window.addEventListener('fsm-event', onCustomEvent)

    let sse: EventSource | null = null
    try {
      sse = new EventSource('/api/events/stream')
      sse.addEventListener('snapshot', () => loadData())
      sse.addEventListener('gate', () => loadData())
      sse.addEventListener('gate_decided', () => loadData())
      sse.addEventListener('gate_requested', () => loadData())
      sse.addEventListener('job', () => loadData())
      sse.addEventListener('sprint_executed', () => loadData())
      sse.addEventListener('changes_applied', () => loadData())
      sse.addEventListener('project_removed', (e) => {
        try {
          const d = JSON.parse(e.data)
          if (d?.removed_id) {
            handleAtomicProjectTeardown(d.removed_id)
          } else {
            loadData()
          }
        } catch {
          loadData()
        }
      })
      sse.addEventListener('agent_event', (e) => {
        try {
          handleFSMEvent(JSON.parse(e.data))
        } catch {}
      })
      sse.addEventListener('action_executed', (e) => {
        try {
          const d = JSON.parse(e.data)
          handleFSMEvent(d)
        } catch {}
        loadData()
      })
      sse.addEventListener('terminal_log', (e) => {
        try {
          const d = JSON.parse(e.data)
          handleFSMEvent(d)
        } catch {}
      })
      sse.onmessage = (e) => {
        try {
          handleFSMEvent(JSON.parse(e.data))
        } catch {}
      }
    } catch {
      console.warn('SSE not supported or connection closed')
    }

    return () => {
      window.removeEventListener('fsm-event', onCustomEvent)
      if (sse) sse.close()
    }
  }, [handleFSMEvent, handleAtomicProjectTeardown])

  const handleSelectProject = async (projId: string) => {
    try {
      const res = await fetch('/api/projects/switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projId }),
      })
      const data = await res.json()
      if (data.success) {
        await loadData()
      }
    } catch (e) {
      console.warn('Error switching project from header:', e)
    }
  }

  // Derive deterministic DomainState (UI = f(DomainState))
  const domainState = deriveDomainState({
    projectsCount: projects.length,
    isPlanning: isSprintModalOpen,
    isExecuting: isExecuting || agents.length > 0,
    hasConflict,
    conflictReason,
    pendingGatesCount,
    recentlyCompleted,
  })

  const getBreadcrumbs = () => {
    switch (currentSection) {
      case 'jira':
        return [{ label: 'Backlog & Requerimientos', sectionId: 'jira' }]
      case 'email':
        return [{ label: 'Notificaciones por Correo', sectionId: 'email' }]
      case 'chat':
        return [{ label: 'Terminal de Consulta', sectionId: 'chat' }]
      case 'connections':
        return [{ label: 'Conexiones de Infraestructura', sectionId: 'connections' }]
      case 'workflows':
        return [{ label: 'Contratos SolidBit', sectionId: 'workflows' }]
      case 'designer':
      case 'roadmap':
        return [{ label: 'Mapa de Flujo DAG', sectionId: 'roadmap' }]
      case 'agents':
        return [{ label: 'Escuadrón de Agentes', sectionId: 'agents' }]
      case 'gates':
      case 'executions':
        return [{ label: 'Aprobaciones & Auditoría', sectionId: 'executions' }]
      case 'projects':
        return [{ label: 'Proyectos & Repositorios', sectionId: 'projects' }]
      case 'database':
      case 'reports':
        return [{ label: 'Auditoría SQLite WAL', sectionId: 'database' }]
      case 'github':
      case 'settings':
        return [{ label: 'Configuración & Sync', sectionId: 'github' }]
      default:
        return [{ label: 'Sprint Activo', sectionId: 'dashboard' }]
    }
  }

  const activeProject = projects.find((p) => p.is_active) || projects[0]

  return (
    <div className="flex flex-col h-screen min-h-[100dvh] w-screen bg-[#09090B] text-zinc-100 font-sans overflow-hidden">
      {/* Header Global de Proyecto con Rama Anclada y Dropdown */}
      <Header
        projectName={projectName}
        activeBranch={activeBranch}
        projects={projects}
        onSelectProject={handleSelectProject}
        domainState={domainState}
        onNavigateSection={(sec) => setCurrentSection(sec)}
        onToggleMobileMenu={() => setIsMobileDrawerOpen(!isMobileDrawerOpen)}
        onOpenDiffModal={() => setIsDiffModalOpen(true)}
        onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
      />

      {/* Network Offline / Reconnection Banner */}
      <NetworkStatusBanner onRetry={loadData} />

      {/* Layout Maestro de 3 Capas Continuas (Sidebar ~18%, Workbench ~52%, Telemetría ~30%) */}
      <div className="flex flex-1 overflow-hidden bg-[#09090B] relative">
        {/* Capa 1: Sidebar de Navegación OOUX (Izquierda) */}
        <LeftSidebar
          currentSection={currentSection}
          onSelectSection={(sec) => setCurrentSection(sec)}
          pendingGatesCount={pendingGatesCount}
          projectsCount={projects.length}
        />

        {/* Capa 2: Workbench Central Dinámico (~65% del área operativa) */}
        <main className="flex-1 overflow-y-auto custom-scroll p-3.5 sm:p-5 lg:p-6 pb-24 md:pb-6 space-y-4 sm:space-y-6">
          {/* Breadcrumbs y Stepper Interactivo (Solo en vistas secundarias; en dashboard el RobotFlowDiagram es el stepper primario) */}
          {currentSection !== 'dashboard' && (
            <div className="space-y-3 border-b border-white/5 pb-3">
              <Breadcrumbs items={getBreadcrumbs()} onNavigate={(sec) => setCurrentSection(sec)} />
              <InteractivePipelineStepper
                currentSection={currentSection}
                currentState={domainState.state}
                onSelectStep={(sec) => setCurrentSection(sec)}
                hasConflict={hasConflict}
                isExecuting={isExecuting || agents.length > 0}
                pendingGatesCount={pendingGatesCount}
              />
            </div>
          )}

          {/* Renderizado Reactivo del Workbench Activo */}
          {currentSection === 'dashboard' && (
            <CenterDashboard
              domainState={domainState}
              tasks={tasks}
              agents={agents}
              connections={connections}
              onRefreshConnections={loadData}
              commits={commits}
              projects={projects}
              events={events}
              onOpenSprintModal={() => setIsSprintModalOpen(true)}
              onNavigateSection={(sec) => setCurrentSection(sec)}
              pendingGatesCount={pendingGatesCount}
              onConflictStateChange={(conflict, reason) => {
                setHasConflict(conflict)
                setConflictReason(reason || null)
              }}
              onExecutingStateChange={(exec) => setIsExecuting(exec)}
              onGateResolved={() => {
                setRecentlyCompleted(true)
                loadData()
              }}
            />
          )}

          {currentSection === 'jira' && (
            <JiraSection
              onLaunchSprintForTicket={(ticket) => {
                setSelectedJiraTicketForSprint(ticket)
                setIsSprintModalOpen(true)
              }}
            />
          )}

          {currentSection === 'email' && <EmailGatewaySection />}

          {currentSection === 'chat' && <ChatSection />}

          {currentSection === 'connections' && <TechAuthHubSection />}

          {currentSection === 'workflows' && <WorkflowsSection />}

          {(currentSection === 'designer' || currentSection === 'roadmap') && (
            <RoadmapSection
              tasks={tasks}
              onOpenSprintModal={() => setIsSprintModalOpen(true)}
            />
          )}

          {currentSection === 'agents' && (
            <AgentsSection
              onAgentLaunched={() => loadData()}
              domainState={domainState}
              onNavigateToResolution={() => setCurrentSection('executions')}
            />
          )}

          {(currentSection === 'gates' || currentSection === 'executions') && (
            <ExecutionsSection />
          )}

          {currentSection === 'projects' && (
            <ProjectsSection
              activeProject={activeProject}
              projects={projects}
              onProjectRemoved={handleAtomicProjectTeardown}
              onRefreshAll={loadData}
              onNavigateSection={(sec) => setCurrentSection(sec)}
              onLaunchAutoSprint={(data) => {
                if (data?.ticket) setSelectedJiraTicketForSprint(data.ticket)
                loadData()
                if (data?.executed) {
                  if (data?.execution?.pending_gates > 0) {
                    setCurrentSection('executions')
                  } else {
                    setCurrentSection('dashboard')
                  }
                } else if (data?.plan) {
                  setIsSprintModalOpen(true)
                }
              }}
            />
          )}

          {(currentSection === 'database' || currentSection === 'reports') && <ReportsSection />}

          {(currentSection === 'github' || currentSection === 'settings') && <SettingsSection />}
        </main>

        {/* Capa 3: Drawer Persistente de Telemetría, Logs FSM y Daemon (Derecha) */}
        <div className="hidden lg:block h-full">
          <PersistentTelemetryDrawer
            daemonPort={8765}
            activeProject={activeProject}
            activeBranch={activeBranch}
            agents={agents}
            commits={commits}
            events={events}
            onNavigateSection={(sec) => setCurrentSection(sec)}
            onRefreshTelemetry={loadData}
            onSimulateConflict={() => {
              const next = !hasConflict
              setHasConflict(next)
              setConflictReason(next ? 'Incidencia simulada para verificar contención.' : null)
            }}
            hasConflict={hasConflict}
          />
        </div>
      </div>

      {/* Mobile Slide-Over Navigation Drawer */}
      <MobileDrawer
        isOpen={isMobileDrawerOpen}
        onClose={() => setIsMobileDrawerOpen(false)}
        currentSection={currentSection}
        onSelectSection={(sec) => setCurrentSection(sec)}
        projectName={projectName}
      />

      {/* Mobile Bottom Navigation Bar */}
      <MobileBottomNav
        currentSection={currentSection}
        onSelectSection={(sec) => setCurrentSection(sec)}
        onOpenDrawer={() => setIsMobileDrawerOpen(true)}
        hasPendingGate={pendingGatesCount > 0}
      />

      {/* Sprint Designer Modal */}
      <SprintDesignerModal
        isOpen={isSprintModalOpen}
        onClose={() => {
          setIsSprintModalOpen(false)
          setSelectedJiraTicketForSprint(null)
        }}
        onSprintExecuted={() => {
          setRecentlyCompleted(true)
          loadData()
        }}
        initialTicket={selectedJiraTicketForSprint}
      />

      {/* Global Diff Inspector Modal */}
      <DiffInspectorModal
        isOpen={isDiffModalOpen}
        onClose={() => setIsDiffModalOpen(false)}
        onChangesApplied={() => loadData()}
      />

      {/* Global Command Palette Spotlight (Ctrl+K) */}
      <CommandPaletteModal
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
        onNavigate={(sec) => setCurrentSection(sec)}
        onOpenSprintModal={() => setIsSprintModalOpen(true)}
        onOpenDiffModal={() => setIsDiffModalOpen(true)}
      />
    </div>
  )
}
