import {
  Activity,
  ArrowRight,
  CircleCheckBig,
  Plug,
  Sparkles,
  TrendingUp,
  TriangleAlert,
  Trophy,
  Workflow,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'

import KpiCard from '../components/ui/KpiCard'
import PageHeader from '../components/ui/PageHeader'
import SectionHeader from '../components/ui/SectionHeader'
import StatusBadge from '../components/ui/StatusBadge'
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

function DashboardPage() {
  const pendingApprovals = demoApprovals.filter(
    (approval) => approval.status === 'PENDING',
  )

  const approvedApprovals = demoApprovals.filter(
    (approval) => approval.status === 'APPROVED',
  )

  const readyIntegrations = demoIntegrations.filter(
    (integration) => integration.status === 'READY',
  )

  const recentEvents = demoAuditEvents
    .slice(-4)
    .reverse()

  return (
    <div className="ui-page-stack dashboard-v2">
      <PageHeader
        eyebrow="Panel zarządczy"
        title={`Dzień dobry, ${currentUser.fullName.split(' ')[0]}`}
        description={
          `Najważniejsze informacje operacyjne Nexalvora Industries. ` +
          `Aktualny priorytet: ${mainRisk.orderNumber} i niedobór ` +
          `${mainRisk.materialCode}.`
        }
        actions={
          <NavLink
            className="ui-button ui-button--primary"
            to="/briefing"
          >
            <Sparkles size={17} />
            Otwórz briefing
          </NavLink>
        }
      />

      <section className="ui-kpi-grid">
        <KpiCard
          label="Aktywny pipeline"
          value={`${formatPln(demoSales.openPipelinePln)} PLN`}
          meta="3 aktywne szanse sprzedażowe"
          icon={<TrendingUp size={20} />}
        />

        <KpiCard
          label="Wygrane szanse"
          value={`${formatPln(demoSales.wonValuePln)} PLN`}
          meta="OPP-2026-041 → ORD-1048"
          icon={<Trophy size={20} />}
        />

        <KpiCard
          label="Ryzyka operacyjne"
          value="2"
          meta="1 wysokie · 1 opóźnione"
          icon={<TriangleAlert size={20} />}
        />

        <KpiCard
          label="Decyzje"
          value={demoApprovals.length}
          meta={`${approvedApprovals.length} zatwierdzone · ${pendingApprovals.length} oczekująca`}
          icon={<CircleCheckBig size={20} />}
        />
      </section>

      <section className="dashboard-v2__primary-grid">
        <article className="ui-card dashboard-v2__risk-card">
          <div className="dashboard-v2__risk-top">
            <div>
              <span className="dashboard-v2__overline">
                Priorytet dnia
              </span>

              <h2>{mainRisk.orderNumber}</h2>

              <p>
                Ryzyko terminu produkcji z powodu niedoboru
                materiału {mainRisk.materialCode}.
              </p>
            </div>

            <StatusBadge tone="warning">
              AT RISK
            </StatusBadge>
          </div>

          <div className="dashboard-v2__risk-metrics">
            <div>
              <span>Dostępne</span>
              <strong>{mainRisk.onHand} m²</strong>
            </div>

            <div>
              <span>Wymagane</span>
              <strong>{mainRisk.required} m²</strong>
            </div>

            <div>
              <span>Niedobór</span>
              <strong>{mainRisk.shortage} m²</strong>
            </div>

            <div>
              <span>Wysyłka</span>
              <strong>{mainRisk.shipmentDate}</strong>
            </div>
          </div>

          <div className="dashboard-v2__risk-note">
            <TriangleAlert size={20} />

            <div>
              <strong>
                Dostawa pozostawia ograniczony bufor czasowy
              </strong>

              <p>
                Pierwsze {mainRisk.firstDeliveryQuantity} m² od{' '}
                {mainRisk.supplier} ma dotrzeć{' '}
                {mainRisk.firstDelivery}, tylko dwa dni przed
                planowaną wysyłką.
              </p>
            </div>
          </div>

          <NavLink
            className="dashboard-v2__text-link"
            to="/briefing"
          >
            Zobacz pełną analizę
            <ArrowRight size={16} />
          </NavLink>
        </article>

        <article className="ui-card dashboard-v2__panel">
          <SectionHeader
            title="Zatwierdzenia"
            description="Decyzje wymagające kontroli człowieka"
            meta={
              <NavLink
                className="dashboard-v2__text-link"
                to="/approvals"
              >
                Wszystkie
                <ArrowRight size={15} />
              </NavLink>
            }
          />

          <div className="dashboard-v2__approval-list">
            {demoApprovals.map((approval) => (
              <div
                className="dashboard-v2__approval-row"
                key={approval.code}
              >
                <div className="dashboard-v2__row-icon">
                  <Workflow size={18} />
                </div>

                <div className="dashboard-v2__row-content">
                  <strong>{approval.title}</strong>
                  <span>{approval.code}</span>
                </div>

                <StatusBadge
                  tone={
                    approval.status === 'PENDING'
                      ? 'warning'
                      : 'success'
                  }
                >
                  {approval.status === 'PENDING'
                    ? 'Oczekuje'
                    : 'Zatwierdzone'}
                </StatusBadge>
              </div>
            ))}
          </div>

          <div className="dashboard-v2__panel-footer">
            <span>Wymaga decyzji</span>
            <strong>{pendingApprovals.length}</strong>
          </div>
        </article>
      </section>

      <section className="dashboard-v2__secondary-grid">
        <article className="ui-card dashboard-v2__panel">
          <SectionHeader
            title="Integracje"
            description="Aktywne źródła danych"
            meta={
              <NavLink
                className="dashboard-v2__text-link"
                to="/integrations"
              >
                Zarządzaj
                <ArrowRight size={15} />
              </NavLink>
            }
          />

          <div className="dashboard-v2__integration-list">
            {demoIntegrations.map((integration) => (
              <div
                className="dashboard-v2__integration-row"
                key={integration.key}
              >
                <div className="dashboard-v2__row-icon">
                  <Plug size={18} />
                </div>

                <div className="dashboard-v2__row-content">
                  <strong>{integration.name}</strong>
                  <span>{integration.provider}</span>
                </div>

                <StatusBadge tone="success">
                  Gotowe
                </StatusBadge>
              </div>
            ))}
          </div>

          <div className="dashboard-v2__panel-footer">
            <span>Aktywne źródła</span>

            <strong>
              {readyIntegrations.length}/{demoIntegrations.length}
            </strong>
          </div>
        </article>

        <article className="ui-card dashboard-v2__panel">
          <SectionHeader
            title="Ostatnia aktywność"
            description="Najnowsze zdarzenia w systemie"
            meta={
              <NavLink
                className="dashboard-v2__text-link"
                to="/audit"
              >
                Pełny audyt
                <ArrowRight size={15} />
              </NavLink>
            }
          />

          <div className="dashboard-v2__activity-list">
            {recentEvents.map((event) => (
              <div
                className="dashboard-v2__activity-row"
                key={`${event.time}-${event.event}`}
              >
                <div className="dashboard-v2__activity-marker">
                  <Activity size={17} />
                </div>

                <div className="dashboard-v2__activity-content">
                  <strong>{event.description}</strong>

                  <span>
                    {event.time} · {event.event}
                  </span>
                </div>
              </div>
            ))}
          </div>

          <div className="dashboard-v2__panel-footer">
            <span>Ścieżka audytowa</span>
            <strong>Aktywny</strong>
          </div>
        </article>
      </section>
    </div>
  )
}

export default DashboardPage