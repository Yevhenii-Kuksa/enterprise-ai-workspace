import {
  Activity,
  Bot,
  CheckCircle2,
  Database,
  FileText,
  Mail,
  PlugZap,
  Sparkles,
  Workflow,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'

import './DashboardPage.css'

const metrics = [
  {
    label: 'Zamówienia zagrożone',
    value: '4',
    hint: '2 wymagają uwagi',
  },
  {
    label: 'Do zatwierdzenia',
    value: '3',
    hint: '1 wysoki priorytet',
  },
  {
    label: 'Dokumenty w bazie',
    value: '128',
    hint: '+6 w tym tygodniu',
  },
  {
    label: 'Aktywne integracje',
    value: '5',
    hint: 'Wszystkie monitorowane',
  },
]

const activities = [
  {
    icon: CheckCircle2,
    title: 'Zatwierdzono zmianę ORD-1048',
    description: 'Anna Kowalska · Zatwierdzenia',
    time: '10:42',
  },
  {
    icon: FileText,
    title: 'Dodano nowy dokument',
    description: 'Procedura jakości QMS-04',
    time: '09:58',
  },
  {
    icon: Mail,
    title: 'Odebrano wiadomość od dostawcy',
    description: 'Gmail · Supply Operations',
    time: '09:21',
  },
]

function DashboardPage() {
  return (
    <>
      <section className="hero-card">
        <div className="hero-content">
          <div className="hero-icon">
            <Sparkles size={22} />
          </div>

          <div>
            <span className="section-kicker">
              Briefing zarządczy
            </span>

            <h2>Dzień dobry, Anna</h2>

            <p>
              Wykryto 3 zdarzenia wymagające uwagi.
              Najważniejsze dotyczy ryzyka opóźnienia
              zamówienia ORD-1048.
            </p>

            <NavLink
              className="primary-button"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                textDecoration: 'none',
              }}
              to="/briefing"
            >
              Otwórz briefing
            </NavLink>
          </div>
        </div>

        <div className="hero-summary">
          <span>Priorytet dnia</span>
          <strong>ORD-1048</strong>
          <p>Ryzyko opóźnienia dostawy komponentów</p>
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
            <p>{metric.hint}</p>
          </article>
        ))}
      </section>

      <section className="dashboard-grid">
        <article className="panel-card approvals-panel">
          <div className="panel-header">
            <div>
              <span className="section-kicker">
                Workflow
              </span>

              <h3>Oczekujące zatwierdzenia</h3>
            </div>

            <NavLink
              className="text-button"
              style={{
                textDecoration: 'none',
              }}
              to="/approvals"
            >
              Zobacz wszystkie
            </NavLink>
          </div>

          <div className="approval-list">
            <div className="approval-item">
              <div className="approval-icon warning">
                <Activity size={18} />
              </div>

              <div className="approval-content">
                <strong>
                  Zmiana terminu ORD-1048
                </strong>
                <span>Aktualizacja zamówienia</span>
              </div>

              <span className="priority high">
                Wysoki
              </span>
            </div>

            <div className="approval-item">
              <div className="approval-icon">
                <Database size={18} />
              </div>

              <div className="approval-content">
                <strong>Zakup materiałów</strong>
                <span>ERP · Wniosek zakupowy</span>
              </div>

              <span className="priority">
                Normalny
              </span>
            </div>

            <div className="approval-item">
              <div className="approval-icon">
                <Workflow size={18} />
              </div>

              <div className="approval-content">
                <strong>
                  Zmiana statusu zamówienia
                </strong>
                <span>
                  Automatyzacja operacyjna
                </span>
              </div>

              <span className="priority">
                Normalny
              </span>
            </div>
          </div>
        </article>

        <article className="panel-card integrations-panel">
          <div className="panel-header">
            <div>
              <span className="section-kicker">
                System
              </span>

              <h3>Integracje</h3>
            </div>

            <PlugZap size={19} />
          </div>

          <div className="integration-list">
            {[
              'Gmail',
              'Google Drive',
              'SharePoint',
              'Google Calendar',
              'ERP',
            ].map((name) => (
              <div
                className="integration-row"
                key={name}
              >
                <div>
                  <span className="integration-dot" />
                  <strong>{name}</strong>
                </div>

                <span className="integration-status">
                  Gotowa
                </span>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="dashboard-secondary-grid">
        <article className="panel-card">
          <div className="panel-header">
            <div>
              <span className="section-kicker">
                Aktywność
              </span>

              <h3>Ostatnia aktywność</h3>
            </div>
          </div>

          <div className="activity-list">
            {activities.map((activity) => {
              const Icon = activity.icon

              return (
                <div
                  className="activity-item"
                  key={activity.title}
                >
                  <div className="activity-icon">
                    <Icon size={17} />
                  </div>

                  <div className="activity-content">
                    <strong>{activity.title}</strong>
                    <span>
                      {activity.description}
                    </span>
                  </div>

                  <span className="activity-time">
                    {activity.time}
                  </span>
                </div>
              )
            })}
          </div>
        </article>

        <article className="panel-card ai-status-card">
          <div>
            <div className="panel-header">
              <div>
                <span className="section-kicker">
                  AI
                </span>

                <h3>Status systemu</h3>
              </div>
            </div>

            <div className="ai-status-main">
              <div className="ai-status-icon">
                <Bot size={20} />
              </div>

              <strong>
                Enterprise AI działa prawidłowo
              </strong>

              <p>
                Usługi AI, wyszukiwanie wiedzy i
                integracje są dostępne.
              </p>
            </div>
          </div>

          <div className="ai-status-footer">
            <span>Ostatnia kontrola: 10:45</span>

            <div className="ai-status-ready">
              Operacyjny
            </div>
          </div>
        </article>
      </section>
    </>
  )
}

export default DashboardPage