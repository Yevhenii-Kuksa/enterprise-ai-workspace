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

import './AssistantPage.css'

const suggestedQuestions = [
  'Które zamówienia mają obecnie najwyższe ryzyko opóźnienia?',
  'Jakie dokumenty opisują procedurę reklamacji?',
  'Czy dostawca potwierdził termin dostawy komponentu CMP-204?',
]

const sources = [
  {
    reference: '[S1]',
    title: 'ORD-1048',
    description: 'ERP · Zamówienie',
  },
  {
    reference: '[S2]',
    title: 'Stan magazynowy CMP-204',
    description: 'ERP · Magazyn',
  },
  {
    reference: '[S3]',
    title: 'Supply update',
    description: 'Gmail · Dostawca',
  },
]

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
              Enterprise AI Assistant
            </span>

            <h2>Asystent AI</h2>

            <p>
              Zadawaj pytania dotyczące dokumentów, procesów,
              zamówień i danych operacyjnych Nexalvora Industries.
              Odpowiedzi są generowane na podstawie dostępnych źródeł.
            </p>
          </div>
        </div>

        <div className="assistant-security">
          <ShieldCheck size={18} />

          <div>
            <span>Tryb bezpieczny</span>
            <strong>Źródła wymagane</strong>
          </div>
        </div>
      </section>

      <section className="assistant-layout">
        <article className="panel-card assistant-chat">
          <div className="assistant-chat-header">
            <div>
              <span className="section-kicker">
                Rozmowa
              </span>

              <h3>Nowe zapytanie</h3>
            </div>

            <span className="assistant-model-badge">
              Grounded AI
            </span>
          </div>

          <div className="assistant-conversation">
            <div className="assistant-message user-message">
              <div className="assistant-avatar user-avatar">
                <User size={17} />
              </div>

              <div className="assistant-message-content">
                <span className="assistant-message-author">
                  Ty
                </span>

                <div className="assistant-message-bubble">
                  Które zamówienie wymaga dziś największej uwagi
                  i dlaczego?
                </div>
              </div>
            </div>

            <div className="assistant-message ai-message">
              <div className="assistant-avatar ai-avatar">
                <Sparkles size={17} />
              </div>

              <div className="assistant-message-content">
                <div className="assistant-message-heading">
                  <span className="assistant-message-author">
                    Asystent AI
                  </span>

                  <span className="assistant-grounded">
                    Oparte na źródłach
                  </span>
                </div>

                <div className="assistant-message-bubble">
                  <p>
                    Największej uwagi wymaga obecnie zamówienie
                    <strong> ORD-1048</strong>.
                  </p>

                  <p>
                    Głównym ryzykiem jest niski stan komponentu
                    CMP-204, który może wpłynąć na termin realizacji.
                    Dostawca potwierdził możliwość częściowej dostawy,
                    co zmniejsza ryzyko, ale nie eliminuje go całkowicie.
                  </p>

                  <p>
                    Rekomendowane działanie: monitorować potwierdzony
                    termin dostawy i przygotować decyzję dotyczącą
                    harmonogramu zamówienia.
                  </p>

                  <div className="assistant-inline-sources">
                    <span>[S1] ORD-1048</span>
                    <span>[S2] CMP-204</span>
                    <span>[S3] Supply update</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="assistant-composer">
            <div className="assistant-input-shell">
              <button
                aria-label="Dodaj załącznik"
                className="assistant-icon-button"
                type="button"
              >
                <Paperclip size={18} />
              </button>

              <textarea
                aria-label="Wiadomość do Asystenta AI"
                placeholder="Zapytaj o dokumenty, zamówienia lub procesy..."
                rows={1}
              />

              <button
                aria-label="Wyślij wiadomość"
                className="assistant-send-button"
                type="button"
              >
                <ArrowUp size={18} />
              </button>
            </div>

            <span className="assistant-composer-note">
              AI może odpowiadać wyłącznie na podstawie dostępnych
              i dozwolonych źródeł.
            </span>
          </div>
        </article>

        <aside className="assistant-sidebar">
          <article className="panel-card">
            <div className="panel-header">
              <div>
                <span className="section-kicker">
                  Źródła odpowiedzi
                </span>

                <h3>Wykorzystane dane</h3>
              </div>

              <FileText size={18} />
            </div>

            <div className="assistant-source-list">
              {sources.map((source) => (
                <div
                  className="assistant-source-item"
                  key={source.reference}
                >
                  <div className="assistant-source-reference">
                    {source.reference}
                  </div>

                  <div>
                    <strong>{source.title}</strong>
                    <span>{source.description}</span>
                  </div>
                </div>
              ))}
            </div>
          </article>

          <article className="panel-card">
            <div className="panel-header">
              <div>
                <span className="section-kicker">
                  Podpowiedzi
                </span>

                <h3>Przykładowe pytania</h3>
              </div>

              <Search size={18} />
            </div>

            <div className="assistant-suggestions">
              {suggestedQuestions.map((question) => (
                <button
                  className="assistant-suggestion"
                  key={question}
                  type="button"
                >
                  {question}
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