import {
  ArrowUp,
  FileText,
  Paperclip,
  Search,
  ShieldCheck,
  Sparkles,
  User,
} from 'lucide-react'

import PageHeader from '../components/ui/PageHeader'
import StatusBadge from '../components/ui/StatusBadge'
import {
  demoKnowledgeDocuments,
  mainRisk,
} from '../data/demoData'

import './AssistantPage.css'

const suggestedQuestions = [
  'Dlaczego ORD-1048 ma status AT RISK?',
  'Kiedy dotrze brakujący MAT-204?',
  'Jakie dokumenty wspierają ocenę ryzyka ORD-1048?',
  'Jakie działanie wymaga zatwierdzenia człowieka?',
]

const sourceCodes = [
  'TECH-12',
  'PROD-W38',
  'PUR-02',
  'SUP-01',
]

const sources = demoKnowledgeDocuments.filter((document) =>
  sourceCodes.includes(document.code),
)

function AssistantPage() {
  return (
    <div className="ui-page-stack assistant-v2">
      <PageHeader
        eyebrow="Grounded AI"
        title="Asystent AI"
        description={
          'Zadawaj pytania o dane operacyjne, dokumenty i procesy Nexalvora. ' +
          'Odpowiedzi są oparte na zatwierdzonych źródłach i zawierają evidence.'
        }
        actions={
          <div className="assistant-v2__governance">
            <ShieldCheck size={18} />

            <div>
              <span>Status AI</span>
              <strong>Grounded & governed</strong>
            </div>
          </div>
        }
      />

      <section className="assistant-v2__layout">
        <article className="ui-card assistant-v2__workspace">
          <header className="assistant-v2__workspace-header">
            <div>
              <span className="assistant-v2__overline">
                Rozmowa
              </span>

              <h2>Analiza ORD-1048</h2>
            </div>

            <StatusBadge tone="success">
              AI online
            </StatusBadge>
          </header>

          <div className="assistant-v2__conversation">
            <div className="assistant-v2__message assistant-v2__message--user">
              <div className="assistant-v2__avatar assistant-v2__avatar--user">
                <User size={18} />
              </div>

              <div className="assistant-v2__message-content">
                <span className="assistant-v2__author">
                  Anna Kowalska
                </span>

                <div className="assistant-v2__bubble assistant-v2__bubble--user">
                  Dlaczego ORD-1048 ma status AT RISK i czy możemy
                  utrzymać termin wysyłki 23.09.2026?
                </div>
              </div>
            </div>

            <div className="assistant-v2__message assistant-v2__message--ai">
              <div className="assistant-v2__avatar assistant-v2__avatar--ai">
                <Sparkles size={18} />
              </div>

              <div className="assistant-v2__message-content">
                <div className="assistant-v2__ai-heading">
                  <span className="assistant-v2__author">
                    Enterprise AI Workspace
                  </span>

                  <StatusBadge tone="success">
                    Grounded
                  </StatusBadge>
                </div>

                <div className="assistant-v2__bubble assistant-v2__bubble--ai">
                  <p>
                    ORD-1048 ma podwyższone ryzyko terminowe z powodu
                    dostępności materiału{' '}
                    <strong>{mainRisk.materialCode}</strong>.
                  </p>

                  <p>
                    Aktualnie na magazynie znajduje się{' '}
                    <strong>{mainRisk.onHand} m²</strong>, podczas gdy
                    zapotrzebowanie dla zamówienia wynosi{' '}
                    <strong>{mainRisk.required} m²</strong>. Oznacza to
                    bieżący niedobór{' '}
                    <strong>{mainRisk.shortage} m²</strong>.
                  </p>

                  <p>
                    Dostawca {mainRisk.supplier} potwierdził pierwszą
                    partię {mainRisk.firstDeliveryQuantity} m² na{' '}
                    <strong>{mainRisk.firstDelivery}</strong>.
                    Planowana wysyłka ORD-1048 pozostaje na{' '}
                    <strong>{mainRisk.shipmentDate}</strong>.
                  </p>

                  <p>
                    Pierwsza dostawa ilościowo pokrywa niedobór, ale
                    pozostawia tylko krótki bufor na przyjęcie materiału,
                    dalszą produkcję oraz kontrolę jakości. Termin jest
                    nadal możliwy, lecz wymaga ścisłego monitorowania i
                    zatwierdzonych działań operacyjnych.
                  </p>

                  <div className="assistant-v2__citations">
                    <span>[S1] TECH-12</span>
                    <span>[S2] PROD-W38</span>
                    <span>[S3] PUR-02</span>
                    <span>[S4] SUP-01</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <footer className="assistant-v2__composer">
            <div className="assistant-v2__input-shell">
              <textarea
                aria-label="Wiadomość do Asystenta AI"
                placeholder="Zapytaj o zamówienie, materiał, dokument lub proces..."
                rows={3}
              />

              <div className="assistant-v2__composer-actions">
                <button
                  className="assistant-v2__icon-button"
                  aria-label="Dodaj załącznik"
                  type="button"
                >
                  <Paperclip size={18} />
                </button>

                <button
                  className="assistant-v2__send-button"
                  aria-label="Wyślij wiadomość"
                  type="button"
                >
                  <ArrowUp size={18} />
                </button>
              </div>
            </div>

            <div className="assistant-v2__composer-note">
              <ShieldCheck size={15} />

              <span>
                Odpowiedzi mogą zawierać wyłącznie informacje dostępne
                w zatwierdzonych źródłach Workspace.
              </span>
            </div>
          </footer>
        </article>

        <aside className="assistant-v2__sidebar">
          <article className="ui-card assistant-v2__source-panel">
            <header className="assistant-v2__panel-header">
              <div>
                <span className="assistant-v2__overline">
                  Evidence
                </span>

                <h3>Źródła odpowiedzi</h3>
              </div>

              <Search size={18} />
            </header>

            <div className="assistant-v2__source-list">
              {sources.map((source, index) => (
                <div
                  className="assistant-v2__source-row"
                  key={source.code}
                >
                  <div className="assistant-v2__source-icon">
                    <FileText size={17} />
                  </div>

                  <div className="assistant-v2__source-copy">
                    <strong>
                      [S{index + 1}] {source.code}
                    </strong>

                    <span>{source.title}</span>

                    <small>
                      {source.category} · v{source.version}
                    </small>
                  </div>
                </div>
              ))}
            </div>
          </article>

          <article className="ui-card assistant-v2__suggestions">
            <header className="assistant-v2__panel-header">
              <div>
                <span className="assistant-v2__overline">
                  Sugestie
                </span>

                <h3>Zapytaj dalej</h3>
              </div>
            </header>

            <div className="assistant-v2__suggestion-list">
              {suggestedQuestions.map((question) => (
                <button
                  className="assistant-v2__suggestion"
                  key={question}
                  type="button"
                >
                  <Sparkles size={16} />

                  <span>{question}</span>
                </button>
              ))}
            </div>
          </article>
        </aside>
      </section>
    </div>
  )
}

export default AssistantPage