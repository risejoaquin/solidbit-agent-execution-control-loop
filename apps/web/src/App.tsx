import { useState, useEffect } from 'react'
import { Header } from './components/Header'
import { LeftSidebar } from './components/LeftSidebar'
import { CenterDashboard } from './components/CenterDashboard'
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
  const [projectName, setProjectName] = useState<string>('Stable-Ecommerce')
  const [selectedJiraTicketForSprint, setSelectedJiraTicketForSprint] = useState<any | null>(null)

  // Dynamic state loaded strictly from backend APIs
  const [tasks, setTasks] = useState<TaskItem[]>([])
  const [agents, setAgents] = useState<AgentItem[]>([])
  const [connections, setConnections] = useState<TechnologyItem[]>([])
  const [commits, setCommits] = useState<CommitItem[]>([])
  const [projects, setProjects] = useState<Project[]>([
    { id: 'stable-ecommerce', name: 'Tienda Online (Stable-Ecommerce)', is_active: true } as any,
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

      const comRes = await fetch('/api/github/commits?limit=4')
      const comData = await comRes.json()
      if (comData.commits) setCommits(comData.commits)

      const projRes = await fetch('/api/projects')
      const projData = await projRes.json()
      if (projData.projects) setProjects(projData.projects)

      const evRes = await fetch('/api/db/rows?table=events&limit=8')
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

  useEffect(() => {
    loadData()

    try {
      const sse = new EventSource('/api/events/stream')
      sse.addEventListener('snapshot', () => loadData())
      sse.addEventListener('gate', () => loadData())
      sse.addEventListener('job', () => loadData())
      sse.addEventListener('sprint_executed', () => loadData())
      sse.addEventListener('changes_applied', () => loadData())
      return () => sse.close()
    } catch {
      console.warn('SSE not supported or connection closed')
    }
  }, [])

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
        return [{ label: 'Requerimientos y Lista de Tareas', sectionId: 'jira' }]
      case 'email':
        return [{ label: 'Notificaciones por Correo', sectionId: 'email' }]
      case 'chat':
        return [{ label: 'Asistente de Consulta', sectionId: 'chat' }]
      case 'connections':
        return [{ label: 'Conexiones del Sistema', sectionId: 'connections' }]
      case 'workflows':
        return [{ label: 'Catálogo de Flujos', sectionId: 'workflows' }]
      case 'designer':
      case 'roadmap':
        return [{ label: '3. Mapa de Flujo', sectionId: 'roadmap' }]
      case 'agents':
        return [{ label: '4. Equipo de Asistentes', sectionId: 'agents' }]
      case 'gates':
      case 'executions':
        return [{ label: '5. Aprobaciones e Historial', sectionId: 'executions' }]
      case 'projects':
        return [{ label: '2. Proyectos Vinculados', sectionId: 'projects' }]
      case 'database':
      case 'reports':
        return [{ label: 'Registro de Actividad y Reglas de Negocio', sectionId: 'database' }]
      case 'github':
      case 'settings':
        return [{ label: 'Perfil y Sincronización', sectionId: 'github' }]
      default:
        return [{ label: '1. Sprint Actual' }]
    }
  }

  return (
    <div className="flex flex-col h-screen min-h-[100dvh] w-screen bg-black text-zinc-100 font-sans overflow-hidden">
      {/* Top Header (Driven by the single DomainState FSM — Invariant 1 & 2) */}
      <Header
        projectName={projectName}
        domainState={domainState}
        onNavigateSection={(sec) => setCurrentSection(sec)}
        onToggleMobileMenu={() => setIsMobileDrawerOpen(!isMobileDrawerOpen)}
        onOpenDiffModal={() => setIsDiffModalOpen(true)}
        onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
      />

      {/* Network Offline / Reconnection Banner */}
      <NetworkStatusBanner onRetry={loadData} />

      {/* Main Layout */}
      <div className="flex flex-1 overflow-hidden bg-black relative">
        {/* Left Sidebar (5 MECE OOUX Domain Entities — Invariant 2) */}
        <LeftSidebar
          currentSection={currentSection}
          onSelectSection={(sec) => setCurrentSection(sec)}
          pendingGatesCount={pendingGatesCount}
          projectsCount={projects.length}
        />

        {/* Center Main Viewport */}
        <main className="flex-1 overflow-y-auto custom-scroll p-3.5 sm:p-5 lg:p-6 pb-24 md:pb-6 space-y-4 sm:space-y-6">
          <div className="border-b border-zinc-850 pb-2">
            <Breadcrumbs items={getBreadcrumbs()} onNavigate={(sec) => setCurrentSection(sec)} />
          </div>

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

          {currentSection === 'agents' && <AgentsSection />}

          {(currentSection === 'gates' || currentSection === 'executions') && (
            <ExecutionsSection />
          )}

          {currentSection === 'projects' && <ProjectsSection />}

          {(currentSection === 'database' || currentSection === 'reports') && <ReportsSection />}

          {(currentSection === 'github' || currentSection === 'settings') && <SettingsSection />}
        </main>
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
