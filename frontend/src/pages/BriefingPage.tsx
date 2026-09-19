import {
  AlertTriangle,
  ArrowUpRight,
  Boxes,
  CheckCircle2,
  FileText,
  PackageSearch,
  ShoppingCart,
  Sparkles,
  TrendingUp,
} from 'lucide-react'

import './BriefingPage.css'

const priorities = [
  {
    icon: AlertTriangle,
    tone: 'warning',
    label: 'Wysoki priorytet',
    title: 'Ryzyko opóźnienia ORD-1048',
    description:
      'Brakuje kluczowego komponentu do produkcji. ' +
      'Aktualny zapas może nie wystarczyć do realizacji ' +
      'zamówienia w planowanym terminie.',
    source: '[S1] ERP · ORD-1048',
  },
  {
    icon: PackageSearch,
    tone: 'info',
    label: 'Operacje',
    title: 'Niski stan komponentu CMP-204',
    description:
      'Stan magazynowy spadł poniżej poziomu bezpieczeństwa. ' +
      'Rekomendowane jest sprawdzenie najbliższej dostawy.',
    source: '[S2] ERP · Magazyn',
  },
  {
    icon: ShoppingCart,
    tone: 'neutral',
    label: 'Dostawcy',
    title: 'Nowa wiadomość od dostawcy',
    description:
      'Dostawca potwierdził możliwość częściowej dostawy ' +
      'komponentów przed końcem tygodnia.',
    source: '[S3] Gmail · Supply Operations',
  },
]

const businessAreas = [
  {
    icon: TrendingUp,
    title: 'Sprzedaż',
    value: '+8,4%',
    description:
      'Wartość aktywnych zamówień wzrosła względem poprzedniego tygodnia.',
  },
  {
    icon: Boxes,
    title: 'Operacje',
    value: '4 ryzyka',
    description:
      'Cztery zamówienia wymagają monitorowania pod kątem terminowości.',
  },
  {
    icon: CheckCircle2,
    title: 'Decyzje',
    value: '3 oczekują',
    description:
      'Trzy działania wymagają zatwierdzenia przed wykonaniem.',
  },
]

function BriefingPage() {
  return (
    <div className="briefing-page">
      <section className="briefing-hero">
        <div className="briefing-hero-main">
          <div className="briefing-icon">
            <Sparkles size={23} />
          </div>

          <div>
            <span className="section-kicker">
              Executive intelligence
            </span>

            <h2>Briefing zarządczy</h2>

            <p>
              Najważniejsze informacje, ryzyka i działania
              wymagające uwagi na podstawie aktualnych danych
              Nexalvora Industries.
            </p>
          </div>
        </div>

        <div className="briefing-meta">
          <span>Wygenerowano</span>
          <strong>19 września 2026 · 10:42</strong>
          <small>
            Dane: ERP, Gmail, Google Drive, Calendar
          </small>
        </div>
      </section>

      <section className="briefing-summary-card">
        <div className="briefing-summary-heading">
          <div>
            <span className="section-kicker">
              Podsumowanie AI
            </span>

            <h3>Najważniejsze na dziś</h3>
          </div>

          <span className="grounded-badge">
            Oparte na źródłach
          </span>
        </div>

        <p className="briefing-summary-text">
          Największym ryzykiem operacyjnym pozostaje zamówienie
          <strong> ORD-1048</strong>. Aktualny poziom zapasu
          komponentu CMP-204 może wpłynąć na termin realizacji.
          Jednocześnie dostawca potwierdził możliwość częściowej
          dostawy, co może ograniczyć ryzyko opóźnienia.
        </p>

        <div className="briefing-source-row">
          <span>[S1] ERP · ORD-1048</span>
          <span>[S2] ERP · Magazyn</span>
          <span>[S3] Gmail · Dostawca</span>
        </div>
      </section>

      <section className="briefing-layout">
        <article className="panel-card briefing-priorities">
          <div className="panel-header">
            <div>
              <span className="section-kicker">
                Priorytety
              </span>

              <h3>Wymagają uwagi</h3>
            </div>

            <span className="items-count">
              3 pozycje
            </span>
          </div>

          <div className="priority-list">
            {priorities.map((item) => {
              const Icon = item.icon

              return (
                <div
                  className="briefing-priority-item"
                  key={item.title}
                >
                  <div
                    className={`briefing-priority-icon ${item.tone}`}
                  >
                    <Icon size={18} />
                  </div>

                  <div className="briefing-priority-content">
                    <span className="priority-category">
                      {item.label}
                    </span>

                    <strong>{item.title}</strong>

                    <p>{item.description}</p>

                    <span className="source-reference">
                      {item.source}
                    </span>
                  </div>

                  <button
                    aria-label={`Otwórz ${item.title}`}
                    className="briefing-open-button"
                    type="button"
                  >
                    <ArrowUpRight size={17} />
                  </button>
                </div>
              )
            })}
          </div>
        </article>

        <aside className="briefing-side-column">
          <article className="panel-card">
            <div className="panel-header">
              <div>
                <span className="section-kicker">
                  Stan biznesu
                </span>

                <h3>Obszary</h3>
              </div>
            </div>

            <div className="business-area-list">
              {businessAreas.map((area) => {
                const Icon = area.icon

                return (
                  <div
                    className="business-area"
                    key={area.title}
                  >
                    <div className="business-area-icon">
                      <Icon size={17} />
                    </div>

                    <div className="business-area-content">
                      <span>{area.title}</span>
                      <strong>{area.value}</strong>
                      <p>{area.description}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </article>

          <article className="panel-card briefing-documents">
            <div className="panel-header">
              <div>
                <span className="section-kicker">
                  Źródła
                </span>

                <h3>Materiały briefingowe</h3>
              </div>

              <FileText size={18} />
            </div>

            <div className="briefing-document-list">
              <div className="briefing-document">
                <strong>ORD-1048</strong>
                <span>ERP · Zamówienie</span>
              </div>

              <div className="briefing-document">
                <strong>
                  Stan magazynowy CMP-204
                </strong>
                <span>ERP · Magazyn</span>
              </div>

              <div className="briefing-document">
                <strong>Supply update</strong>
                <span>Gmail · Dostawca</span>
              </div>
            </div>
          </article>
        </aside>
      </section>
    </div>
  )
}

export default BriefingPage