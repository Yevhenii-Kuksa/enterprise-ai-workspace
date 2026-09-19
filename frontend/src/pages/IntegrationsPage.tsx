import {
  CalendarDays,
  CheckCircle2,
  Cloud,
  Database,
  FileText,
  Mail,
  PlugZap,
  RefreshCw,
  ShieldCheck,
} from 'lucide-react'

import './IntegrationsPage.css'

const integrations = [
  {
    icon: Mail,
    name: 'Gmail',
    kind: 'Email',
    status: 'READY',
    statusTone: 'ready',
    mode: 'Read-only',
    records: '18 wiadomości',
    lastSync: '10:44',
    capabilities: ['READ_MESSAGES'],
  },
  {
    icon: Cloud,
    name: 'Google Drive',
    kind: 'File storage',
    status: 'READY',
    statusTone: 'ready',
    mode: 'Read-only',
    records: '72 dokumenty',
    lastSync: '10:41',
    capabilities: ['READ_FILES'],
  },
  {
    icon: FileText,
    name: 'SharePoint',
    kind: 'File storage',
    status: 'READY',
    statusTone: 'ready',
    mode: 'Read-only',
    records: '52 dokumenty',
    lastSync: '10:39',
    capabilities: ['READ_FILES'],
  },
  {
    icon: CalendarDays,
    name: 'Google Calendar',
    kind: 'Calendar',
    status: 'DEGRADED',
    statusTone: 'degraded',
    mode: 'Read-only',
    records: '11 wydarzeń',
    lastSync: '10:31',
    capabilities: ['READ_CALENDAR_EVENTS'],
  },
  {
    icon: Database,
    name: 'ERP',
    kind: 'ERP',
    status: 'READY',
    statusTone: 'ready',
    mode: 'Read-only',
    records: '24 zamówienia',
    lastSync: '10:46',
    capabilities: ['READ_ERP_DATA'],
  },
]

function IntegrationsPage() {
  return (
    <div className="integrations-page">
      <section className="integrations-hero">
        <div className="integrations-hero-main">
          <div className="integrations-hero-icon">
            <PlugZap size={23} />
          </div>

          <div>
            <span className="section-kicker">
              Enterprise integrations
            </span>

            <h2>Integracje</h2>

            <p>
              Centralny podgląd źródeł danych połączonych
              z Enterprise AI Workspace oraz ich aktualnego
              stanu operacyjnego.
            </p>
          </div>
        </div>

        <div className="integrations-security">
          <ShieldCheck size={18} />

          <div>
            <span>Tryb dostępu</span>
            <strong>Read-only</strong>
          </div>
        </div>
      </section>

      <section className="integrations-stats">
        <article className="integrations-stat-card">
          <span>Wszystkie integracje</span>
          <strong>5</strong>
        </article>

        <article className="integrations-stat-card">
          <span>Gotowe</span>
          <strong>4</strong>
        </article>

        <article className="integrations-stat-card">
          <span>Ograniczone</span>
          <strong>1</strong>
        </article>

        <article className="integrations-stat-card">
          <span>Błędy</span>
          <strong>0</strong>
        </article>
      </section>

      <section className="integrations-grid">
        {integrations.map((integration) => {
          const Icon = integration.icon

          return (
            <article
              className="panel-card integration-card"
              key={integration.name}
            >
              <div className="integration-card-header">
                <div className="integration-card-title">
                  <div className="integration-card-icon">
                    <Icon size={20} />
                  </div>

                  <div>
                    <span>{integration.kind}</span>
                    <h3>{integration.name}</h3>
                  </div>
                </div>

                <span
                  className={`integration-card-status ${integration.statusTone}`}
                >
                  {integration.status}
                </span>
              </div>

              <div className="integration-card-details">
                <div className="integration-detail">
                  <span>Tryb</span>
                  <strong>{integration.mode}</strong>
                </div>

                <div className="integration-detail">
                  <span>Dane</span>
                  <strong>{integration.records}</strong>
                </div>

                <div className="integration-detail">
                  <span>Ostatnia synchronizacja</span>
                  <strong>{integration.lastSync}</strong>
                </div>
              </div>

              <div className="integration-capabilities">
                <span className="integration-capabilities-label">
                  Capabilities
                </span>

                <div className="integration-capability-list">
                  {integration.capabilities.map((capability) => (
                    <span
                      className="integration-capability"
                      key={capability}
                    >
                      {capability}
                    </span>
                  ))}
                </div>
              </div>

              <div className="integration-card-footer">
                <div className="integration-health">
                  {integration.status === 'READY' ? (
                    <CheckCircle2 size={16} />
                  ) : (
                    <RefreshCw size={16} />
                  )}

                  <span>
                    {integration.status === 'READY'
                      ? 'Połączenie działa prawidłowo'
                      : 'Dane dostępne z ograniczeniem'}
                  </span>
                </div>

                <button
                  className="integration-details-button"
                  type="button"
                >
                  Szczegóły
                </button>
              </div>
            </article>
          )
        })}
      </section>
    </div>
  )
}

export default IntegrationsPage