import { useState, useEffect } from 'react'
import { Header } from './components/Header'
import { LeftSidebar } from './components/LeftSidebar'
import { CenterDashboard } from './components/CenterDashboard'
import { RightSidebar } from './components/RightSidebar'
import { SprintDesignerModal } from './components/SprintDesignerModal'
import { ChatSection } from './components/sections/ChatSection'
import { RoadmapSection } from './components/sections/RoadmapSection'
import { AgentsSection } from './components/sections/AgentsSection'
import { ExecutionsSection } from './components/sections/ExecutionsSection'
import { ProjectsSection } from './components/sections/ProjectsSection'
import { ReportsSection } from './components/sections/ReportsSection'
import { SettingsSection } from './components/sections/SettingsSection'
import type { TaskItem, AgentItem, CommitItem, Project, ActivityEvent } from './types/orchestrator'

export default function App() {
  const [currentSection, setCurrentSection] = useState<string>('dashboard')
  const [isSprintModalOpen, setIsSprintModalOpen] = useState<boolean>(false)
  const [projectName, setProjectName] = useState<string>('Stable-Ecommerce')

  // Canonical Tasks State
  const [tasks] = useState<TaskItem[]>([
    { id: '1', title: 'Autenticación JWT y roles', key: 'SEC-101', agent: 'auth-agent', start: '24 Oct', end: '27 Oct', progress: 100, status: 'Completada' },
    { id: '2', title: 'Catálogo de productos y stock', key: 'CAT-202', agent: 'db-agent', start: '25 Oct', end: '29 Oct', progress: 80, status: 'En progreso' },
    { id: '3', title: 'API REST Checkout & Pagos', key: 'PAY-303', agent: 'api-agent', start: '26 Oct', end: '01 Nov', progress: 45, status: 'En progreso' },
    { id: '4', title: 'UI Carrito y Checkout', key: 'UI-404', agent: 'frontend-agent', start: '28 Oct', end: '03 Nov', progress: 15, status: 'Pendiente' },
    { id: '5', title: 'Tests E2E & Cobertura', key: 'QA-505', agent: 'qa-agent', start: '02 Nov', end: '06 Nov', progress: 0, status: 'Pendiente' },
    { id: '6', title: 'Despliegue y CI/CD Railway', key: 'OPS-606', agent: 'devops-agent', start: '05 Nov', end: '07 Nov', progress: 0, status: 'Pendiente' },
  ])

  // Canonical Fleet Agents State
  const [agents] = useState<AgentItem[]>([
    { id: 'a1', name: 'architect-agent', role: 'Líder técnico', status: 'Activo', color: 'emerald', icon: 'cpu', pid: 1432 },
    { id: 'a2', name: 'api-agent', role: 'Backend REST', status: 'Activo', color: 'emerald', icon: 'server', pid: 2190 },
    { id: 'a3', name: 'db-agent', role: 'PostgreSQL / SQLite', status: 'Activo', color: 'emerald', icon: 'database', pid: 3411 },
    { id: 'a4', name: 'auth-agent', role: 'Seguridad y JWT', status: 'Activo', color: 'emerald', icon: 'shield', pid: 4892 },
    { id: 'a5', name: 'checkout-agent', role: 'Flujo de compra', status: 'En espera', color: 'amber', icon: 'shopping-bag', pid: 5670 },
    { id: 'a6', name: 'frontend-agent', role: 'UI / Tailwind', status: 'Activo', color: 'emerald', icon: 'layout', pid: 6112 },
    { id: 'a7', name: 'qa-agent', role: 'Tests unitarios y e2e', status: 'Activo', color: 'emerald', icon: 'check-circle', pid: 7289 },
    { id: 'a8', name: 'devops-agent', role: 'CI/CD y Docker', status: 'Activo', color: 'emerald', icon: 'terminal', pid: 8940 },
  ])

  const [commits, setCommits] = useState<CommitItem[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [events, setEvents] = useState<ActivityEvent[]>([])
  const [dbStats, setDbStats] = useState<any>({ jobs: 2, runs: 26, events: 26 })

  // Initial data loading from live backend endpoints
  const loadData = async () => {
    try {
      // 1. Context
      const ctxRes = await fetch('/api/orchestrator/context')
      const ctxData = await ctxRes.json()
      if (ctxData.active_project?.name) {
        setProjectName(ctxData.active_project.name)
      }

      // 2. Commits
      const comRes = await fetch('/api/github/commits?limit=4')
      const comData = await comRes.json()
      if (comData.commits) setCommits(comData.commits)

      // 3. Projects
      const projRes = await fetch('/api/projects')
      const projData = await projRes.json()
      if (projData.projects) setProjects(projData.projects)

      // 4. Events
      const evRes = await fetch('/api/db/rows?table=events&limit=8')
      const evData = await evRes.json()
      if (evData.rows) setEvents(evData.rows)

      // 5. DB Stats
      const dbRes = await fetch('/api/db/stats')
      const dbData = await dbRes.json()
      if (dbData.tables) {
        setDbStats({
          jobs: dbData.tables.jobs || 2,
          runs: dbData.tables.runs || 26,
          events: dbData.tables.events || 26,
        })
      }
    } catch (e) {
      console.warn('Backend loading in offline fallback mode:', e)
    }
  }

  useEffect(() => {
    loadData()

    // Real-time SSE stream
    try {
      const sse = new EventSource('/api/events/stream')
      sse.addEventListener('snapshot', () => loadData())
      sse.addEventListener('gate', () => loadData())
      sse.addEventListener('job', () => loadData())
      sse.addEventListener('sprint_executed', () => loadData())
      return () => sse.close()
    } catch (e) {
      console.warn('SSE not supported or connection closed')
    }
  }, [])

  return (
    <div className="flex flex-col h-screen w-screen bg-[#080c10] text-zinc-100 font-sans overflow-hidden">
      {/* Top Header */}
      <Header
        projectName={projectName}
        onOpenSprintModal={() => setIsSprintModalOpen(true)}
        onNavigateSection={(sec) => setCurrentSection(sec)}
      />

      {/* Main 3-Column Layout */}
      <div className="flex flex-1 overflow-hidden bg-[#080c10]">
        {/* Left Sidebar */}
        <LeftSidebar
          currentSection={currentSection}
          onSelectSection={(sec) => setCurrentSection(sec)}
          onOpenSprintModal={() => setIsSprintModalOpen(true)}
          dbStats={dbStats}
        />

        {/* Center Main Viewport */}
        <main className="flex-1 overflow-y-auto custom-scroll p-4 lg:p-6 space-y-6">
          {currentSection === 'dashboard' && (
            <CenterDashboard
              tasks={tasks}
              agents={agents}
              commits={commits}
              projects={projects}
              events={events}
              onOpenSprintModal={() => setIsSprintModalOpen(true)}
              onNavigateSection={(sec) => setCurrentSection(sec)}
            />
          )}

          {currentSection === 'chat' && (
            <ChatSection />
          )}

          {(currentSection === 'designer' || currentSection === 'roadmap') && (
            <RoadmapSection
              tasks={tasks}
              onOpenSprintModal={() => setIsSprintModalOpen(true)}
            />
          )}

          {currentSection === 'agents' && (
            <AgentsSection agents={agents} />
          )}

          {(currentSection === 'gates' || currentSection === 'executions') && (
            <ExecutionsSection />
          )}

          {currentSection === 'projects' && (
            <ProjectsSection projects={projects} />
          )}

          {(currentSection === 'database' || currentSection === 'reports') && (
            <ReportsSection />
          )}

          {(currentSection === 'github' || currentSection === 'settings') && (
            <SettingsSection />
          )}
        </main>

        {/* Right Sidebar */}
        <RightSidebar
          agents={agents}
          events={events}
          onSelectAgent={(agent) => alert(`Agente seleccionado: ${agent.name} (${agent.role})`)}
          onSelectEvent={(ev) => alert(`Evento: ${ev.event_type} - ${ev.payload_json}`)}
          onNavigateSection={(sec) => setCurrentSection(sec)}
        />
      </div>

      {/* Sprint Designer Modal */}
      <SprintDesignerModal
        isOpen={isSprintModalOpen}
        onClose={() => setIsSprintModalOpen(false)}
        onSprintExecuted={() => loadData()}
      />
    </div>
  )
}
