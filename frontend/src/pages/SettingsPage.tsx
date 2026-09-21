import {
  Bot,
  Building2,
  Database,
  LockKeyhole,
  ServerCog,
  ShieldCheck,
  SlidersHorizontal,
  UserRound,
} from 'lucide-react'

import PageHeader from '../components/ui/PageHeader'
import SectionHeader from '../components/ui/SectionHeader'
import StatusBadge from '../components/ui/StatusBadge'
import { currentUser } from '../data/demoData'

import './SettingsPage.css'

function SettingsPage() {
  return (
    <div className="ui-page-stack settings-v2">
      <PageHeader
        eyebrow="Workspace configuration"
        title="Ustawienia"
        description={
          'Konfiguracja środowiska Enterprise AI Workspace, zasad AI, ' +
          'bezpieczeństwa oraz dostępu użytkowników.'
        }
        actions={
          <div className="settings-v2__status">
            <ShieldCheck size={18} />

            <div>
              <span>Stan konfiguracji</span>
              <strong>Production-ready</strong>
            </div>
          </div>
        }
      />

      <section className="ui-section-stack">
        <SectionHeader
          title="Workspace"
          description="Podstawowe informacje o środowisku Nexalvora"
        />

        <article className="ui-card settings-v2__section">
          <div className="settings-v2__section-heading">
            <div className="settings-v2__section-icon">
              <Building2 size={21} />
            </div>

            <div>
              <h2>Organizacja i produkt</h2>

              <p>
                Informacje identyfikujące środowisko demonstracyjne.
              </p>
            </div>
          </div>

          <div className="settings-v2__rows">
            <div className="settings-v2__row">
              <div>
                <span>Organizacja</span>
                <small>Tenant organizacyjny</small>
              </div>

              <strong>Nexalvora Industries Sp. z o.o.</strong>
            </div>

            <div className="settings-v2__row">
              <div>
                <span>Produkt</span>
                <small>Aktywny workspace</small>
              </div>

              <strong>Enterprise AI Workspace</strong>
            </div>

            <div className="settings-v2__row">
              <div>
                <span>Użytkownik</span>
                <small>Aktualny kontekst użytkownika</small>
              </div>

              <div className="settings-v2__user">
                <UserRound size={17} />
                <strong>{currentUser.fullName}</strong>
              </div>
            </div>
          </div>
        </article>
      </section>

      <section className="ui-section-stack">
        <SectionHeader
          title="AI i reliability"
          description="Konfiguracja modelu oraz bramek jakości odpowiedzi"
        />

        <div className="settings-v2__two-column">
          <article className="ui-card settings-v2__section">
            <div className="settings-v2__section-heading">
              <div className="settings-v2__section-icon">
                <Bot size={21} />
              </div>

              <div>
                <h2>AI runtime</h2>

                <p>
                  Parametry wykorzystywane przez provider odpowiedzi.
                </p>
              </div>
            </div>

            <div className="settings-v2__rows">
              <div className="settings-v2__row">
                <div>
                  <span>Provider</span>
                  <small>Źródło generowania odpowiedzi</small>
                </div>

                <strong>OpenAI</strong>
              </div>

              <div className="settings-v2__row">
                <div>
                  <span>Model</span>
                  <small>Model odpowiedzi AI</small>
                </div>

                <strong>gpt-5.6-luna</strong>
              </div>

              <div className="settings-v2__row">
                <div>
                  <span>Timeout</span>
                  <small>Maksymalny czas pojedynczego requestu</small>
                </div>

                <strong>30 s</strong>
              </div>

              <div className="settings-v2__row">
                <div>
                  <span>Retries</span>
                  <small>Maksymalna liczba ponowień</small>
                </div>

                <strong>2</strong>
              </div>
            </div>
          </article>

          <article className="ui-card settings-v2__section">
            <div className="settings-v2__section-heading">
              <div className="settings-v2__section-icon">
                <SlidersHorizontal size={21} />
              </div>

              <div>
                <h2>Reliability gates</h2>

                <p>
                  Ograniczenia chroniące przed słabo ugruntowaną odpowiedzią.
                </p>
              </div>
            </div>

            <div className="settings-v2__rows">
              <div className="settings-v2__row">
                <div>
                  <span>Max evidence distance</span>
                  <small>Próg jakości evidence</small>
                </div>

                <strong>0.35</strong>
              </div>

              <div className="settings-v2__row">
                <div>
                  <span>Max source age</span>
                  <small>Maksymalny wiek źródła</small>
                </div>

                <strong>30 dni</strong>
              </div>

              <div className="settings-v2__row">
                <div>
                  <span>Citation validation</span>
                  <small>Walidacja odwołań [S1], [S2]...</small>
                </div>

                <StatusBadge tone="success">
                  Aktywna
                </StatusBadge>
              </div>

              <div className="settings-v2__row">
                <div>
                  <span>Grounded answers</span>
                  <small>Odpowiedzi wyłącznie na podstawie evidence</small>
                </div>

                <StatusBadge tone="success">
                  Wymagane
                </StatusBadge>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section className="ui-section-stack">
        <SectionHeader
          title="Bezpieczeństwo i dostęp"
          description="Kontrola tenantów, uprawnień i działań krytycznych"
        />

        <div className="settings-v2__two-column">
          <article className="ui-card settings-v2__section">
            <div className="settings-v2__section-heading">
              <div className="settings-v2__section-icon">
                <LockKeyhole size={21} />
              </div>

              <div>
                <h2>Access control</h2>

                <p>
                  Zasady dostępu do danych organizacji.
                </p>
              </div>
            </div>

            <div className="settings-v2__checks">
              <div className="settings-v2__check">
                <ShieldCheck size={19} />

                <div>
                  <strong>Tenant isolation</strong>
                  <span>
                    Dane innych organizacji są niedostępne.
                  </span>
                </div>

                <StatusBadge tone="success">
                  Aktywne
                </StatusBadge>
              </div>

              <div className="settings-v2__check">
                <ShieldCheck size={19} />

                <div>
                  <strong>RBAC</strong>
                  <span>
                    Dostęp zależny od uprawnień użytkownika.
                  </span>
                </div>

                <StatusBadge tone="success">
                  Aktywne
                </StatusBadge>
              </div>

              <div className="settings-v2__check">
                <ShieldCheck size={19} />

                <div>
                  <strong>Human approval</strong>
                  <span>
                    Krytyczne działania wymagają decyzji człowieka.
                  </span>
                </div>

                <StatusBadge tone="success">
                  Wymagane
                </StatusBadge>
              </div>
            </div>
          </article>

          <article className="ui-card settings-v2__section">
            <div className="settings-v2__section-heading">
              <div className="settings-v2__section-icon">
                <Database size={21} />
              </div>

              <div>
                <h2>Dostęp do systemów</h2>

                <p>
                  Polityka integracji z systemami źródłowymi.
                </p>
              </div>
            </div>

            <div className="settings-v2__rows">
              <div className="settings-v2__row">
                <div>
                  <span>ERP</span>
                  <small>Dane operacyjne</small>
                </div>

                <StatusBadge tone="info">
                  Read-only
                </StatusBadge>
              </div>

              <div className="settings-v2__row">
                <div>
                  <span>Gmail / Drive / SharePoint</span>
                  <small>Źródła wiedzy i komunikacji</small>
                </div>

                <StatusBadge tone="info">
                  Read-only
                </StatusBadge>
              </div>

              <div className="settings-v2__row">
                <div>
                  <span>Calendar</span>
                  <small>Kontekst terminów i zdarzeń</small>
                </div>

                <StatusBadge tone="info">
                  Read-only
                </StatusBadge>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section className="ui-section-stack">
        <SectionHeader
          title="Runtime"
          description="Stan środowiska i zabezpieczeń produkcyjnych"
        />

        <article className="ui-card settings-v2__runtime">
          <div className="settings-v2__runtime-icon">
            <ServerCog size={22} />
          </div>

          <div className="settings-v2__runtime-content">
            <div className="settings-v2__runtime-heading">
              <div>
                <span className="settings-v2__overline">
                  Production readiness
                </span>

                <h2>
                  Środowisko przygotowane do bezpiecznego uruchomienia
                </h2>
              </div>

              <StatusBadge tone="success">
                READY
              </StatusBadge>
            </div>

            <div className="settings-v2__runtime-grid">
              <div>
                <span>Health</span>
                <strong>/health</strong>
              </div>

              <div>
                <span>Readiness</span>
                <strong>/ready</strong>
              </div>

              <div>
                <span>Database</span>
                <strong>PostgreSQL + pgvector</strong>
              </div>

              <div>
                <span>Container user</span>
                <strong>Non-root</strong>
              </div>

              <div>
                <span>Filesystem</span>
                <strong>Read-only</strong>
              </div>

              <div>
                <span>Privileges</span>
                <strong>no-new-privileges</strong>
              </div>
            </div>
          </div>
        </article>
      </section>
    </div>
  )
}

export default SettingsPage