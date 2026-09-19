import {
  Bot,
  Boxes,
  CalendarDays,
  CheckSquare2,
  Database,
  FileText,
  Gauge,
  History,
  PlugZap,
  Search,
  Settings,
  Sparkles,
  Workflow,
} from 'lucide-react'
import {
  NavLink,
  Navigate,
  Route,
  Routes,
} from 'react-router-dom'

import { currentUser, demoCompany } from './data/demoData'
import ApprovalsPage from './pages/ApprovalsPage'
import AssistantPage from './pages/AssistantPage'
import AuditPage from './pages/AuditPage'
import BriefingPage from './pages/BriefingPage'
import DashboardPage from './pages/DashboardPage'
import ErpPage from './pages/ErpPage'
import ExecutionsPage from './pages/ExecutionsPage'
import IntegrationsPage from './pages/IntegrationsPage'
import KnowledgePage from './pages/KnowledgePage'
import SettingsPage from './pages/SettingsPage'

import './App.css'

const navigation = [
  {
    label: 'Panel główny',
    icon: Gauge,
    path: '/dashboard',
  },
  {
    label: 'Briefing',
    icon: Sparkles,
    path: '/briefing',
  },
  {
    label: 'Baza wiedzy',
    icon: FileText,
    path: '/knowledge',
  },
  {
    label: 'Asystent AI',
    icon: Bot,
    path: '/assistant',
  },
  {
    label: 'Zatwierdzenia',
    icon: CheckSquare2,
    path: '/approvals',
    badge: '3',
  },
  {
    label: 'Wykonania',
    icon: Workflow,
    path: '/executions',
  },
  {
    label: 'ERP',
    icon: Database,
    path: '/erp',
  },
  {
    label: 'Integracje',
    icon: PlugZap,
    path: '/integrations',
  },
  {
    label: 'Audyt',
    icon: History,
    path: '/audit',
  },
]

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">
          <Boxes size={20} strokeWidth={2.2} />
        </div>

        <div>
          <strong>Nexalvora</strong>
          <span>Enterprise AI Workspace</span>
        </div>
      </div>

      <nav className="navigation">
        <span className="navigation-label">
          Workspace
        </span>

        {navigation.map((item) => {
          const Icon = item.icon

          return (
            <NavLink
              className={({ isActive }) =>
                `nav-item ${isActive ? 'active' : ''}`
              }
              key={item.path}
              style={{
                textDecoration: 'none',
              }}
              to={item.path}
            >
              <Icon size={18} strokeWidth={1.9} />

              <span>{item.label}</span>

              {item.badge && (
                <span className="nav-badge">
                  {item.badge}
                </span>
              )}
            </NavLink>
          )
        })}
      </nav>

      <div className="sidebar-footer">
        <NavLink
          className={({ isActive }) =>
            `nav-item ${isActive ? 'active' : ''}`
          }
          style={{
            textDecoration: 'none',
          }}
          to="/settings"
        >
          <Settings
            size={18}
            strokeWidth={1.9}
          />

          <span>Ustawienia</span>
        </NavLink>

        <div className="user-card">
          <div className="avatar">AK</div>

          <div className="user-details">
            <strong>{currentUser.fullName}</strong>
            <span>{currentUser.jobTitle}</span>
          </div>

          <span className="status-dot" />
        </div>
      </div>
    </aside>
  )
}

function PageHeader({
  title,
}: {
  title: string
}) {
  return (
    <header className="topbar">
      <div>
        <span className="eyebrow">
          {demoCompany.shortName}
        </span>

        <h1>{title}</h1>
      </div>

      <div className="topbar-actions">
        <div className="search-box">
          <Search size={17} />

          <input
            aria-label="Szukaj"
            placeholder="Szukaj w workspace..."
            type="text"
          />
        </div>

        <button
          className="date-button"
          type="button"
        >
          <CalendarDays size={17} />
          {demoCompany.dateLabel}
        </button>
      </div>
    </header>
  )
}

function App() {
  return (
    <div className="app-shell">
      <Sidebar />

      <main className="main-content">
        <Routes>
          <Route
            element={
              <Navigate
                replace
                to="/dashboard"
              />
            }
            path="/"
          />

          <Route
            element={
              <>
                <PageHeader title="Panel główny" />
                <DashboardPage />
              </>
            }
            path="/dashboard"
          />

          <Route
            element={
              <>
                <PageHeader title="Briefing" />
                <BriefingPage />
              </>
            }
            path="/briefing"
          />

          <Route
            element={
              <>
                <PageHeader title="Baza wiedzy" />
                <KnowledgePage />
              </>
            }
            path="/knowledge"
          />

          <Route
            element={
              <>
                <PageHeader title="Asystent AI" />
                <AssistantPage />
              </>
            }
            path="/assistant"
          />

          <Route
            element={
              <>
                <PageHeader title="Zatwierdzenia" />
                <ApprovalsPage />
              </>
            }
            path="/approvals"
          />

          <Route
            element={
              <>
                <PageHeader title="Wykonania" />
                <ExecutionsPage />
              </>
            }
            path="/executions"
          />

          <Route
            element={
              <>
                <PageHeader title="ERP" />
                <ErpPage />
              </>
            }
            path="/erp"
          />

          <Route
            element={
              <>
                <PageHeader title="Integracje" />
                <IntegrationsPage />
              </>
            }
            path="/integrations"
          />

          <Route
            element={
              <>
                <PageHeader title="Audyt" />
                <AuditPage />
              </>
            }
            path="/audit"
          />

          <Route
            element={
              <>
                <PageHeader title="Ustawienia" />
                <SettingsPage />
              </>
            }
            path="/settings"
          />

          <Route
            element={
              <Navigate
                replace
                to="/dashboard"
              />
            }
            path="*"
          />
        </Routes>
      </main>
    </div>
  )
}

export default App