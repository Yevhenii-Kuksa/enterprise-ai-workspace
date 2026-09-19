import {
  BookOpen,
  CheckCircle2,
  FileSpreadsheet,
  FileText,
  Filter,
  FolderOpen,
  Search,
  Share2,
} from 'lucide-react'

import './KnowledgePage.css'

const documents = [
  {
    icon: FileText,
    title: 'Procedura jakości QMS-04',
    type: 'PDF',
    source: 'Google Drive',
    updated: '19 września 2026',
    status: 'Zindeksowany',
    pages: '18 stron',
  },
  {
    icon: FileSpreadsheet,
    title: 'Plan produkcji — tydzień 38',
    type: 'XLSX',
    source: 'SharePoint',
    updated: '18 września 2026',
    status: 'Zindeksowany',
    pages: '6 arkuszy',
  },
  {
    icon: FileText,
    title: 'Instrukcja obsługi reklamacji',
    type: 'DOCX',
    source: 'SharePoint',
    updated: '17 września 2026',
    status: 'Zindeksowany',
    pages: '12 stron',
  },
  {
    icon: FileText,
    title: 'Polityka zakupowa 2026',
    type: 'PDF',
    source: 'Google Drive',
    updated: '15 września 2026',
    status: 'Zindeksowany',
    pages: '24 strony',
  },
  {
    icon: FileSpreadsheet,
    title: 'Lista dostawców strategicznych',
    type: 'XLSX',
    source: 'Google Drive',
    updated: '14 września 2026',
    status: 'Zindeksowany',
    pages: '4 arkusze',
  },
]

const stats = [
  {
    label: 'Dokumenty',
    value: '128',
  },
  {
    label: 'Zindeksowane',
    value: '124',
  },
  {
    label: 'Źródła danych',
    value: '3',
  },
  {
    label: 'Aktualizacja dziś',
    value: '6',
  },
]

function KnowledgePage() {
  return (
    <div className="knowledge-page">
      <section className="knowledge-hero">
        <div className="knowledge-hero-main">
          <div className="knowledge-hero-icon">
            <BookOpen size={23} />
          </div>

          <div>
            <span className="section-kicker">
              Knowledge Hub
            </span>

            <h2>Baza wiedzy</h2>

            <p>
              Dokumenty, procedury i materiały firmowe wykorzystywane
              przez Enterprise AI Workspace do wyszukiwania wiedzy
              i generowania odpowiedzi opartych na źródłach.
            </p>
          </div>
        </div>

        <div className="knowledge-health">
          <div className="knowledge-health-icon">
            <CheckCircle2 size={18} />
          </div>

          <div>
            <span>Status bazy</span>
            <strong>Gotowa do użycia</strong>
          </div>
        </div>
      </section>

      <section className="knowledge-stats">
        {stats.map((stat) => (
          <article
            className="knowledge-stat-card"
            key={stat.label}
          >
            <span>{stat.label}</span>
            <strong>{stat.value}</strong>
          </article>
        ))}
      </section>

      <section className="panel-card knowledge-library">
        <div className="knowledge-toolbar">
          <div>
            <span className="section-kicker">
              Biblioteka
            </span>

            <h3>Dokumenty firmowe</h3>
          </div>

          <div className="knowledge-toolbar-actions">
            <div className="knowledge-search">
              <Search size={17} />

              <input
                aria-label="Szukaj dokumentów"
                placeholder="Szukaj dokumentu..."
                type="text"
              />
            </div>

            <button
              className="knowledge-filter-button"
              type="button"
            >
              <Filter size={16} />
              Filtry
            </button>
          </div>
        </div>

        <div className="knowledge-table">
          <div className="knowledge-table-head">
            <span>Dokument</span>
            <span>Źródło</span>
            <span>Aktualizacja</span>
            <span>Status</span>
            <span />
          </div>

          {documents.map((document) => {
            const Icon = document.icon

            return (
              <div
                className="knowledge-table-row"
                key={document.title}
              >
                <div className="knowledge-document">
                  <div className="knowledge-document-icon">
                    <Icon size={18} />
                  </div>

                  <div>
                    <strong>{document.title}</strong>

                    <span>
                      {document.type} · {document.pages}
                    </span>
                  </div>
                </div>

                <div className="knowledge-source">
                  <Share2 size={15} />
                  <span>{document.source}</span>
                </div>

                <span className="knowledge-updated">
                  {document.updated}
                </span>

                <div className="knowledge-status">
                  <span className="knowledge-status-dot" />
                  {document.status}
                </div>

                <button
                  aria-label={`Otwórz ${document.title}`}
                  className="knowledge-open-button"
                  type="button"
                >
                  <FolderOpen size={17} />
                </button>
              </div>
            )
          })}
        </div>
      </section>

      <section className="knowledge-footer-grid">
        <article className="panel-card knowledge-source-card">
          <div className="panel-header">
            <div>
              <span className="section-kicker">
                Źródła danych
              </span>

              <h3>Połączone biblioteki</h3>
            </div>
          </div>

          <div className="knowledge-source-list">
            <div className="knowledge-source-row">
              <div>
                <span className="knowledge-provider-dot" />
                <strong>Google Drive</strong>
              </div>

              <span>72 dokumenty</span>
            </div>

            <div className="knowledge-source-row">
              <div>
                <span className="knowledge-provider-dot" />
                <strong>SharePoint</strong>
              </div>

              <span>52 dokumenty</span>
            </div>

            <div className="knowledge-source-row">
              <div>
                <span className="knowledge-provider-dot" />
                <strong>Upload lokalny</strong>
              </div>

              <span>4 dokumenty</span>
            </div>
          </div>
        </article>

        <article className="panel-card knowledge-rag-card">
          <div className="panel-header">
            <div>
              <span className="section-kicker">
                RAG
              </span>

              <h3>Gotowość AI</h3>
            </div>
          </div>

          <div className="knowledge-rag-content">
            <div className="knowledge-rag-score">
              97%
            </div>

            <div>
              <strong>
                Wysoka gotowość bazy wiedzy
              </strong>

              <p>
                Większość dokumentów została poprawnie
                przetworzona i może być używana jako
                źródło odpowiedzi AI.
              </p>
            </div>
          </div>
        </article>
      </section>
    </div>
  )
}

export default KnowledgePage