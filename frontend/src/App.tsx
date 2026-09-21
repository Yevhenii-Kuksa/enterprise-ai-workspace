import {
  Navigate,
  Route,
  Routes,
} from 'react-router-dom'

import AppShell from './layout/AppShell'
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

function App() {
  return (
    <AppShell>
      <Routes>
        <Route
          path="/"
          element={
            <Navigate
              to="/dashboard"
              replace
            />
          }
        />

        <Route
          path="/dashboard"
          element={<DashboardPage />}
        />

        <Route
          path="/briefing"
          element={<BriefingPage />}
        />

        <Route
          path="/knowledge"
          element={<KnowledgePage />}
        />

        <Route
          path="/assistant"
          element={<AssistantPage />}
        />

        <Route
          path="/approvals"
          element={<ApprovalsPage />}
        />

        <Route
          path="/executions"
          element={<ExecutionsPage />}
        />

        <Route
          path="/erp"
          element={<ErpPage />}
        />

        <Route
          path="/integrations"
          element={<IntegrationsPage />}
        />

        <Route
          path="/audit"
          element={<AuditPage />}
        />

        <Route
          path="/settings"
          element={<SettingsPage />}
        />

        <Route
          path="*"
          element={
            <Navigate
              to="/dashboard"
              replace
            />
          }
        />
      </Routes>
    </AppShell>
  )
}

export default App