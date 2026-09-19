import {
  Activity,
  Database,
  PlugZap,
  Sparkles,
  Workflow,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'

import {
  currentUser,
  demoApprovals,
  demoAuditEvents,
  demoIntegrations,
  demoSales,
  mainRisk,
} from '../data/demoData'

import './DashboardPage.css'

const formatPln = (value: number) =>
  new Intl.NumberFormat('pl-PL').format(value)

const metrics = [
  {
    label: 'Aktywny pipeline',
    value: `${formatPln(demoSales.openPipelinePln)} PLN`,
    detail: '3 aktywne szanse sprzedażowe',
  },
  {
    label: 'Wygrane szanse',
    value: `${formatPln(demoSales.wonValuePln)} PLN`,
    detail: 'OPP-2026-041 → ORD-1048',
  },
  {
    label: 'Ryzyka operacyjne',
    value: '2',
    detail: '1 wysokie · 1 opóźnione',
  },
  {
    label: 'Decyzje',
    value: '3',
    detail: '2 zatwierdzone · 1 oczekująca',
  },
]

function DashboardPage() {
  const pendingApprovals = demoApprovals.filter(
    (approval) => approval.status === 'PENDING',
  ).length

  const readyIntegrations = demoIntegrations.filter(
    (integration) => integration.status === 'READY',
  ).length

  return (
    <div className="dashboard-page">
      <section className="hero-card">
        <div className="hero-content">
          <div className="hero-icon">
            <Sparkles size={23} />
          </div>

          <div>
            <span className="section-kicker">
              Executive briefing
            </span>

            <h2>
              Dzień dobry, {currentUser.fullName.split(' ')[0]}
            </h2>

            <p>
              Najważniejszym ryzykiem operacyjnym jest dziś
              zamówienie {mainRisk.orderNumber}. Dostępne jest{' '}
              {mainRisk.onHand} m² materiału {mainRisk.materialCode}
              {' '}przy zapotrzebowaniu {mainRisk.required} m².
              Pierwsza dostawa od {mainRisk.supplier} jest planowana
              na {mainRisk.firstDelivery}, a wysyłka do klienta
              na {mainRisk.shipmentDate}.
            </p>

            <NavLink
              className="primary-button"
              to="/briefing"
            >
              Otwórz pełny briefing
            </NavLink>
          </div>
        </div>

        <div className="hero-summary">
          <span>Priorytet dnia</span>

          <strong>{mainRisk.orderNumber}</strong>

          <p>
            Ryzyko terminu z powodu niedoboru{' '}
            {mainRisk.materialCode}.
          </p>

          <div className="hero-summary-status">
            <span className="status-dot warning" />
            AT RISK
          </div>
        </div>
      </section>

      <section className="metrics-grid">
        {metrics.map((metric) => (
          <article
            className="metric-card"
            key={metric.label}
          >
            <span>{metric.label}</span>
            <strong>{metric.value}</strong>
            <p>{metric.detail}</p>
          </article>
        ))}
      </section>

      <section className="dashboard-grid">
        <article className="panel-card approvals-panel">
          <div className="panel-header">
            <div>
              <span className="section-kicker">
                Governance
              </span>

              <h3>Zatwierdzenia</h3>
            </div>

            <NavLink
              className="text-button"
              to="/approvals"
            >
              Zobacz wszystkie
            </NavLink>
          </div>

          <div className="approval-list">
            {demoApprovals.map((approval) => (
              <div
                className="approval-item"
                key={approval.code}
              >
                <div className="approval-icon">
                  <Workflow size={18} />
                </div>

                <div className="approval-content">
                  <div>
                    <strong>{approval.title}</strong>
                    <span>{approval.code}</span>
                  </div>

                  <span
                    className={
                      approval.status === 'PENDING'
                        ? 'priority warning'
                        : 'priority success'
                    }
                  >
                    {approval.status === 'PENDING'
                      ? 'Oczekuje'
                      : 'Zatwierdzone'}
                  </span>
                </div>
              </div>
            ))}
          </div>

          <div className="panel-summary">
            <span>Wymaga uwagi</span>
            <strong>{pendingApprovals}</strong>
          </div>
        </article>

        <article className="panel-card integrations-panel">
          <div className="panel-header">
            <div>
              <span className="section-kicker">
                Data sources
              </span>

              <h3>Integracje</h3>
            </div>

            <NavLink
              className="text-button"
              to="/integrations"
            >
              Zarządzaj
            </NavLink>
          </div>

          <div className="integration-list">
            {demoIntegrations.map((integration) => (
              <div
                className="integration-row"
                key={integration.key}
              >
                <div>
                  <span className="integration-dot" />

                  <div>
                    <strong>{integration.name}</strong>
                    <span>{integration.provider}</span>
                  </div>
                </div>

                <span className="integration-status">
                  Gotowe
                </span>
              </div>
            ))}
          </div>

          <div className="panel-summary">
            <span>Aktywne źródła</span>
            <strong>
              {readyIntegrations}/{demoIntegrations.length}
            </strong>
          </div>
        </article>
      </section>

      <section className="dashboard-grid">
        <article className="panel-card activity-panel">
          <div className="panel-header">
            <div>
              <span className="section-kicker">
                Audit trail
              </span>

              <h3>Ostatnia aktywność</h3>
            </div>

            <NavLink
              className="text-button"
              to="/audit"
            >
              Pełny audyt
            </NavLink>
          </div>

          <div className="activity-list">
            {demoAuditEvents.slice(-4).reverse().map((event) => (
              <div
                className="activity-item"
                key={`${event.time}-${event.event}`}
              >
                <div className="activity-icon">
                  <Activity size={17} />
                </div>

                <div>
                  <strong>{event.description}</strong>
                  <span>
                    {event.time} · {event.event}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="panel-card ai-status-panel">
          <div className="panel-header">
            <div>
              <span className="section-kicker">
                AI intelligence
              </span>

              <h3>Status analizy</h3>
            </div>

            <Database size={19} />
          </div>

          <div className="ai-status-content">
            <div className="ai-status-main">
              <div className="ai-status-icon">
                <Sparkles size={22} />
              </div>

              <div>
                <strong>
                  Wykryto ryzyko dla {mainRisk.orderNumber}
                </strong>

                <p>
                  Niedobór {mainRisk.shortage} m² materiału{' '}
                  {mainRisk.materialCode}. Dostawa 200 m²
                  zaplanowana na {mainRisk.firstDelivery}
                  pozostawia ograniczony bufor przed wysyłką.
                </p>
              </div>
            </div>

            <div className="ai-status-meta">
              <span>
                <PlugZap size={15} />
                ERP + Gmail + Knowledge Hub
              </span>

              <span>
                Poziom ryzyka: {mainRisk.riskLevel}
              </span>
            </div>

            <NavLink
              className="text-button"
              to="/assistant"
            >
              Otwórz Asystenta AI
            </NavLink>
          </div>
        </article>
      </section>
    </div>
  )
}

export default DashboardPage