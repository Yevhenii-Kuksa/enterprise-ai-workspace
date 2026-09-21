import {
  CalendarDays,
  Database,
  Mail,
  Plug,
  RefreshCw,
  ShieldCheck,
} from 'lucide-react'

import KpiCard from '../components/ui/KpiCard'
import PageHeader from '../components/ui/PageHeader'
import SectionHeader from '../components/ui/SectionHeader'
import StatusBadge from '../components/ui/StatusBadge'
import { demoIntegrations } from '../data/demoData'

import './IntegrationsPage.css'

function getIntegrationIcon(name: string) {
  const normalized = name.toLowerCase()

  if (normalized.includes('gmail')) {
    return Mail
  }

  if (normalized.includes('calendar')) {
    return CalendarDays
  }

  if (
    normalized.includes('erp') ||
    normalized.includes('database')
  ) {
    return Database
  }

  return Plug
}

function IntegrationsPage() {
  const readyCount = demoIntegrations.filter(
    (integration) => integration.status === 'READY',
  ).length

  return (
    <div className="ui-page-stack integrations-v2">
      <PageHeader
        eyebrow="Enterprise integrations"
        title="Integracje"
        description={
          'Źródła danych podłączone do Enterprise AI Workspace. ' +
          'Integracje w scenariuszu demo działają w bezpiecznym trybie odczytu.'
        }
        actions={
          <div className="integrations-v2__security">
            <ShieldCheck size={18} />

            <div>
              <span>Data access</span>
              <strong>Controlled</strong>
            </div>
          </div>
        }
      />

      <section className="ui-kpi-grid">
        <KpiCard
          label="Integracje"
          value={demoIntegrations.length}
          meta="Źródła danych w Workspace"
          icon={<Plug size={20} />}
        />

        <KpiCard
          label="Gotowe"
          value={readyCount}
          meta="Integracje dostępne w scenariuszu demo"
          icon={<ShieldCheck size={20} />}
        />

        <KpiCard
          label="Read-only"
          value={demoIntegrations.length}
          meta="Brak niekontrolowanych zapisów do systemów źródłowych"
          icon={<Database size={20} />}
        />

        <KpiCard
          label="Problemy"
          value="0"
          meta="Brak niedostępnych źródeł w scenariuszu demo"
          icon={<RefreshCw size={20} />}
        />
      </section>

      <section className="ui-section-stack">
        <SectionHeader
          title="Źródła danych"
          description="Systemy dostępne dla Enterprise AI Workspace"
          meta={`${demoIntegrations.length} integracji`}
        />

        <div className="integrations-v2__grid">
          {demoIntegrations.map((integration) => {
            const Icon = getIntegrationIcon(
              integration.name,
            )

            return (
              <article
                className="ui-card integrations-v2__card"
                key={integration.key}
              >
                <header className="integrations-v2__card-header">
                  <div className="integrations-v2__identity">
                    <div className="integrations-v2__icon">
                      <Icon size={21} />
                    </div>

                    <div>
                      <h2>{integration.name}</h2>

                      <span>
                        {integration.provider}
                      </span>
                    </div>
                  </div>

                  <StatusBadge tone="success">
                    Gotowe
                  </StatusBadge>
                </header>

                <div className="integrations-v2__meta-grid">
                  <div>
                    <span>Tryb</span>
                    <strong>Read-only</strong>
                  </div>

                  <div>
                    <span>Status</span>
                    <strong>{integration.status}</strong>
                  </div>
                </div>

                <section className="integrations-v2__capabilities">
                  <span className="integrations-v2__label">
                    Dostęp
                  </span>

                  <div className="integrations-v2__chips">
                    <span className="integrations-v2__chip">
                      Read-only
                    </span>

                    <span className="integrations-v2__chip">
                      Dane źródłowe
                    </span>

                    <span className="integrations-v2__chip">
                      Bezpieczny dostęp
                    </span>
                  </div>
                </section>

                <footer className="integrations-v2__footer">
                  <div className="integrations-v2__health">
                    <span className="integrations-v2__health-dot" />

                    <span>
                      Połączenie dostępne
                    </span>
                  </div>

                  <span>
                    Demo connector
                  </span>
                </footer>
              </article>
            )
          })}
        </div>
      </section>

      <section className="ui-card integrations-v2__policy">
        <div className="integrations-v2__policy-icon">
          <ShieldCheck size={22} />
        </div>

        <div>
          <span className="integrations-v2__overline">
            Integration governance
          </span>

          <h2>
            Systemy źródłowe pozostają pod kontrolą
          </h2>

          <p>
            Enterprise AI Workspace wykorzystuje integracje jako
            kontrolowane źródła danych. Operacje modyfikujące dane
            wymagają osobnego mechanizmu governance i nie są wykonywane
            przez read-only connectors.
          </p>
        </div>
      </section>
    </div>
  )
}

export default IntegrationsPage