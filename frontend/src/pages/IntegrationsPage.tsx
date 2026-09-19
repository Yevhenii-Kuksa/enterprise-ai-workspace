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

import { demoIntegrations } from '../data/demoData'

import './IntegrationsPage.css'

const integrationPresentation = {
  gmail: {
    icon: Mail,
    mode: 'Read-only',
    records: '3 wiadomości',
    lastSync: '19 września 2026 · 10:20',
    description:
      'Komunikacja z dostawcami i klientami wykorzystywana w analizie operacyjnej.',
  },
  'google-drive': {
    icon: Cloud,
    mode: 'Read-only',
    records: '5 dokumentów',
    lastSync: '19 września 2026 · 10:15',
    description:
      'Dokumentacja techniczna, zakupowa i handlowa Nexalvora.',
  },
  sharepoint: {
    icon: FileText,
    mode: 'Read-only',
    records: '5 dokumentów',
    lastSync: '19 września 2026 · 10:14',
    description:
      'Kontrolowane procedury jakościowe, bezpieczeństwa i produkcji.',
  },
  'google-calendar': {
    icon: CalendarDays,
    mode: 'Read-only',
    records: '4 wydarzenia',
    lastSync: '19 września 2026 · 10:18',
    description:
      'Spotkania operacyjne, odbiory materiałów i terminy związane z ORD-1048.',
  },
  erp: {
    icon: Database,
    mode: 'Read-only',
    records: '5 zamówień · 6 pozycji magazynowych',
    lastSync: '19 września 2026 · 12:00',
    description:
      'Zamówienia, stany magazynowe i dane operacyjne Nexalvora ERP.',
  },
} as const

const integrations = demoIntegrations.map((integration) => ({
  ...integration,
  ...integrationPresentation[
    integration.key as keyof typeof integrationPresentation
  ],
}))

function IntegrationsPage() {
  const readyCount = integrations.filter(
    (integration) => integration.status === 'READY',
  ).length

  const fileSourceCount = integrations.filter(
    (integration) => integration.capability === 'READ_FILES',
  ).length

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
              Połączone źródła danych Nexalvora wykorzystywane
              przez Enterprise AI Workspace do odczytu wiadomości,
              dokumentów, kalendarza i danych ERP.
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
        <article className="integration-stat-card">
          <span>Integracje</span>
          <strong>{integrations.length}</strong>
        </article>

        <article className="integration-stat-card">
          <span>Gotowe</span>
          <strong>{readyCount}</strong>
        </article>

        <article className="integration-stat-card">
          <span>Źródła plików</span>
          <strong>{fileSourceCount}</strong>
        </article>

        <article className="integration-stat-card">
          <span>Tryb zapisu</span>
          <strong>0</strong>
        </article>
      </section>

      <section className="integrations-grid">
        {integrations.map((integration) => {
          const Icon = integration.icon
          const isReady = integration.status === 'READY'

          return (
            <article
              className="panel-card integration-card"
              key={integration.key}
            >
              <div className="integration-card-header">
                <div className="integration-card-heading">
                  <div className="integration-card-icon">
                    <Icon size={20} />
                  </div>

                  <div>
                    <span className="section-kicker">
                      {integration.provider}
                    </span>

                    <h3>{integration.name}</h3>
                  </div>
                </div>

                <span
                  className={`integration-card-status ${
                    isReady ? 'ready' : 'degraded'
                  }`}
                >
                  <span className="integration-card-status-dot" />
                  {isReady ? 'Gotowe' : 'Degraded'}
                </span>
              </div>

              <p className="integration-card-description">
                {integration.description}
              </p>

              <div className="integration-card-details">
                <div>
                  <span>Tryb</span>
                  <strong>{integration.mode}</strong>
                </div>

                <div>
                  <span>Dane</span>
                  <strong>{integration.records}</strong>
                </div>

                <div>
                  <span>Ostatnia synchronizacja</span>
                  <strong>{integration.lastSync}</strong>
                </div>
              </div>

              <div className="integration-capabilities">
                <span className="integration-capability">
                  {integration.capability}
                </span>
              </div>

              <div className="integration-card-footer">
                <div className="integration-health">
                  {isReady ? (
                    <CheckCircle2 size={16} />
                  ) : (
                    <RefreshCw size={16} />
                  )}

                  <span>
                    {isReady
                      ? 'Połączenie działa prawidłowo'
                      : 'Wymaga ponownej synchronizacji'}
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