import {
  ArrowUp,
  Bot,
  FileText,
  Paperclip,
  Search,
  ShieldCheck,
  Sparkles,
  User,
} from 'lucide-react'

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
    <div className="assistant-page">
      <section className="assistant-hero">
        <div className="assistant-hero-main">
          <div className="assistant-hero-icon">
            <Bot size={23} />
          </div>

          <div>
            <span className="section-kicker">
              Grounded AI
            </span>

            <h2>Asystent AI</h2>

            <p>
              Zadawaj pytania o dane operacyjne, dokumenty,
              integracje i procesy Nexalvora. Odpowiedzi są
              przygotowywane na podstawie dostępnych źródeł.
            </p>
          </div>
        </div>

        <div className="assistant-hero-status">
          <ShieldCheck size={18} />

          <div>
            <span>Status</span>
            <strong>Grounded & governed</strong>
          </div>
        </div>
      </section>

      <section className="assistant-layout">
        <article className="panel-card assistant-chat">
          <div className="panel-header">
            <div>
              <span className="section-kicker">
                Rozmowa
              </span>

              <h3>Analiza ORD-1048</h3>
            </div>

            <div className="assistant-chat-status">
              <span className="status-dot" />
              AI online
            </div>
          </div>

          <div className="assistant-conversation">
            <div className="assistant-message user-message">
              <div className="assistant-message-avatar">
                <User size={18} />
              </div>

              <div className="assistant-message-content">
                <span>Anna Kowalska</span>

                <div className="assistant-message-bubble">
                  Dlaczego ORD-1048 ma status AT RISK i czy
                  możemy utrzymać termin wysyłki 23.09.2026?
                </div>
              </div>
            </div>

            <div className="assistant-message ai-message">
              <div className="assistant-message-avatar">
                <Sparkles size={18} />
              </div>

              <div className="assistant-message-content">
                <span>Enterprise AI Workspace</span>

                <div className="assistant-message-bubble">
                  <p>
                    ORD-1048 ma podwyższone ryzyko terminowe z powodu
                    dostępności materiału {mainRisk.materialCode}.
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
                    Pierwsza dostawa ilościowo pokrywa niedobór,
                    ale pozostawia tylko krótki bufor na przyjęcie
                    materiału, dalszą produkcję oraz kontrolę jakości.
                    Dlatego termin jest nadal możliwy, lecz wymaga
                    ścisłego monitorowania i zatwierdzonych działań
                    operacyjnych.
                  </p>

                  <div className="assistant-inline-sources">
                    <span>[S1] TECH-12</span>
                    <span>[S2] PROD-W38</span>
                    <span>[S3] PUR-02</span>
                    <span>[S4] SUP-01</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="assistant-composer">
            <div className="assistant-input-shell">
              <textarea
                aria-label="Wiadomość do Asystenta AI"
                placeholder="Zapytaj o zamówienie, materiał, dokument lub proces..."
                rows={3}
              />

              <div className="assistant-composer-actions">
                <button
                  aria-label="Dodaj załącznik"
                  type="button"
                >
                  <Paperclip size={18} />
                </button>

                <button
                  aria-label="Wyślij wiadomość"
                  className="assistant-send-button"
                  type="button"
                >
                  <ArrowUp size={18} />
                </button>
              </div>
            </div>

            <div className="assistant-composer-note">
              <ShieldCheck size={14} />
              Odpowiedzi mogą zawierać wyłącznie informacje
              dostępne w zatwierdzonych źródłach Workspace.
            </div>
          </div>
        </article>

        <aside className="assistant-sidebar">
          <article className="panel-card assistant-source-card">
            <div className="panel-header">
              <div>
                <span className="section-kicker">
                  Evidence
                </span>

                <h3>Źródła odpowiedzi</h3>
              </div>

              <Search size={18} />
            </div>

            <div className="assistant-source-list">
              {sources.map((source, index) => (
                <div
                  className="assistant-source-item"
                  key={source.code}
                >
                  <div className="assistant-source-icon">
                    <FileText size={17} />
                  </div>

                  <div>
                    <strong>
                      [S{index + 1}] {source.code}
                    </strong>

                    <span>{source.title}</span>
                  </div>
                </div>
              ))}
            </div>
          </article>

          <article className="panel-card assistant-suggestions">
            <div className="panel-header">
              <div>
                <span className="section-kicker">
                  Sugestie
                </span>

                <h3>Zapytaj dalej</h3>
              </div>
            </div>

            <div className="assistant-suggestion-list">
              {suggestedQuestions.map((question) => (
                <button
                  className="assistant-suggestion"
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