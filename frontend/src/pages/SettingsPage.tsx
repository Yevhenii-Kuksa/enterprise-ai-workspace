import {
  Bell,
  Building2,
  Globe2,
  LockKeyhole,
  Mail,
  Settings,
  ShieldCheck,
  UserRound,
} from 'lucide-react'

import './SettingsPage.css'

function SettingsPage() {
  return (
    <div className="settings-page">
      <section className="settings-hero">
        <div className="settings-hero-main">
          <div className="settings-hero-icon">
            <Settings size={23} />
          </div>

          <div>
            <span className="section-kicker">
              Workspace preferences
            </span>

            <h2>Ustawienia</h2>

            <p>
              Ustawienia profilu, bezpieczeństwa, języka
              i preferencji użytkownika Enterprise AI Workspace.
            </p>
          </div>
        </div>

        <div className="settings-security">
          <ShieldCheck size={18} />

          <div>
            <span>Status konta</span>
            <strong>Bezpieczne</strong>
          </div>
        </div>
      </section>

      <section className="settings-grid">
        <article className="panel-card settings-card">
          <div className="settings-card-header">
            <div className="settings-card-icon">
              <UserRound size={19} />
            </div>

            <div>
              <span className="section-kicker">
                Profil
              </span>

              <h3>Dane użytkownika</h3>
            </div>
          </div>

          <div className="settings-form">
            <div className="settings-field">
              <label htmlFor="settings-name">
                Imię i nazwisko
              </label>

              <input
                id="settings-name"
                readOnly
                type="text"
                value="Anna Kowalska"
              />
            </div>

            <div className="settings-field">
              <label htmlFor="settings-email">
                Adres e-mail
              </label>

              <div className="settings-input-with-icon">
                <Mail size={16} />

                <input
                  id="settings-email"
                  readOnly
                  type="email"
                  value="anna.kowalska@nexalvora.example"
                />
              </div>
            </div>

            <div className="settings-field">
              <label htmlFor="settings-role">
                Rola
              </label>

              <input
                id="settings-role"
                readOnly
                type="text"
                value="Administrator"
              />
            </div>
          </div>
        </article>

        <article className="panel-card settings-card">
          <div className="settings-card-header">
            <div className="settings-card-icon">
              <Building2 size={19} />
            </div>

            <div>
              <span className="section-kicker">
                Workspace
              </span>

              <h3>Organizacja</h3>
            </div>
          </div>

          <div className="settings-info-list">
            <div className="settings-info-row">
              <span>Organizacja</span>
              <strong>Nexalvora Industries Sp. z o.o.</strong>
            </div>

            <div className="settings-info-row">
              <span>Workspace</span>
              <strong>Enterprise AI Workspace</strong>
            </div>

            <div className="settings-info-row">
              <span>Środowisko</span>
              <strong>Production Demo</strong>
            </div>

            <div className="settings-info-row">
              <span>Dostęp</span>
              <strong>Enterprise</strong>
            </div>
          </div>
        </article>

        <article className="panel-card settings-card">
          <div className="settings-card-header">
            <div className="settings-card-icon">
              <Globe2 size={19} />
            </div>

            <div>
              <span className="section-kicker">
                Interfejs
              </span>

              <h3>Język i region</h3>
            </div>
          </div>

          <div className="settings-form">
            <div className="settings-field">
              <label htmlFor="settings-language">
                Język interfejsu
              </label>

              <select
                defaultValue="pl"
                id="settings-language"
              >
                <option value="pl">
                  Polski
                </option>
              </select>
            </div>

            <div className="settings-field">
              <label htmlFor="settings-timezone">
                Strefa czasowa
              </label>

              <select
                defaultValue="europe-warsaw"
                id="settings-timezone"
              >
                <option value="europe-warsaw">
                  Europe/Warsaw
                </option>
              </select>
            </div>

            <div className="settings-field">
              <label htmlFor="settings-date-format">
                Format daty
              </label>

              <select
                defaultValue="pl"
                id="settings-date-format"
              >
                <option value="pl">
                  DD.MM.YYYY
                </option>
              </select>
            </div>
          </div>
        </article>

        <article className="panel-card settings-card">
          <div className="settings-card-header">
            <div className="settings-card-icon">
              <Bell size={19} />
            </div>

            <div>
              <span className="section-kicker">
                Powiadomienia
              </span>

              <h3>Preferencje</h3>
            </div>
          </div>

          <div className="settings-toggle-list">
            <label className="settings-toggle-row">
              <div>
                <strong>Zatwierdzenia</strong>
                <span>
                  Powiadamiaj o nowych decyzjach wymagających akcji.
                </span>
              </div>

              <input
                defaultChecked
                type="checkbox"
              />
            </label>

            <label className="settings-toggle-row">
              <div>
                <strong>Ryzyka operacyjne</strong>
                <span>
                  Powiadamiaj o nowych ryzykach i opóźnieniach.
                </span>
              </div>

              <input
                defaultChecked
                type="checkbox"
              />
            </label>

            <label className="settings-toggle-row">
              <div>
                <strong>Błędy integracji</strong>
                <span>
                  Powiadamiaj o problemach z synchronizacją danych.
                </span>
              </div>

              <input
                defaultChecked
                type="checkbox"
              />
            </label>
          </div>
        </article>

        <article className="panel-card settings-card settings-security-card">
          <div className="settings-card-header">
            <div className="settings-card-icon">
              <LockKeyhole size={19} />
            </div>

            <div>
              <span className="section-kicker">
                Bezpieczeństwo
              </span>

              <h3>Sesja i dostęp</h3>
            </div>
          </div>

          <div className="settings-security-status">
            <div className="settings-security-check">
              <ShieldCheck size={20} />

              <div>
                <strong>Aktywna bezpieczna sesja</strong>
                <span>
                  Dostęp do workspace jest kontrolowany
                  przez system uprawnień.
                </span>
              </div>
            </div>

            <div className="settings-info-list">
              <div className="settings-info-row">
                <span>Rola</span>
                <strong>Administrator</strong>
              </div>

              <div className="settings-info-row">
                <span>Uprawnienia</span>
                <strong>Pełny dostęp demonstracyjny</strong>
              </div>

              <div className="settings-info-row">
                <span>Sesja</span>
                <strong>Aktywna</strong>
              </div>
            </div>
          </div>
        </article>
      </section>
    </div>
  )
}

export default SettingsPage