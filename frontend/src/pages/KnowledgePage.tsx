import {
  FileText,
  Library,
  Search,
} from 'lucide-react'
import {
  useMemo,
  useState,
} from 'react'

import DataTable, {
  type DataTableColumn,
} from '../components/ui/DataTable'
import PageHeader from '../components/ui/PageHeader'
import SectionHeader from '../components/ui/SectionHeader'
import {
  demoKnowledgeDocuments,
} from '../data/demoData'

import './KnowledgePage.css'

type KnowledgeDocument =
  (typeof demoKnowledgeDocuments)[number]

function KnowledgePage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] =
    useState('ALL')

  const categories = useMemo(
    () =>
      Array.from(
        new Set(
          demoKnowledgeDocuments.map(
            (document) => document.category,
          ),
        ),
      ).sort(),
    [],
  )

  const filteredDocuments = useMemo(() => {
    const normalizedSearch = searchQuery
      .trim()
      .toLowerCase()

    return demoKnowledgeDocuments.filter(
      (document) => {
        const matchesSearch =
          normalizedSearch.length === 0 ||
          document.title
            .toLowerCase()
            .includes(normalizedSearch) ||
          document.code
            .toLowerCase()
            .includes(normalizedSearch) ||
          document.category
            .toLowerCase()
            .includes(normalizedSearch)

        const matchesCategory =
          categoryFilter === 'ALL' ||
          document.category === categoryFilter

        return matchesSearch && matchesCategory
      },
    )
  }, [categoryFilter, searchQuery])

  const columns: DataTableColumn<KnowledgeDocument>[] = [
    {
      key: 'document',
      header: 'Dokument',
      render: (document) => (
        <div className="knowledge-v2__document">
          <div className="knowledge-v2__document-icon">
            <FileText size={18} />
          </div>

          <div className="knowledge-v2__document-copy">
            <span className="ui-table__primary">
              {document.title}
            </span>

            <span className="ui-table__secondary">
              {document.code}
            </span>
          </div>
        </div>
      ),
    },
    {
      key: 'category',
      header: 'Kategoria',
      width: '220px',
      render: (document) => (
        <span className="knowledge-v2__category">
          {document.category}
        </span>
      ),
    },
    {
      key: 'version',
      header: 'Wersja',
      width: '140px',
      render: (document) => (
        <span className="knowledge-v2__version">
          v{document.version}
        </span>
      ),
    },
  ]

  return (
    <div className="ui-page-stack knowledge-v2">
      <PageHeader
        eyebrow="Knowledge Hub"
        title="Baza wiedzy"
        description={
          'Centralna biblioteka dokumentów wykorzystywanych przez ' +
          'Enterprise AI Workspace do wyszukiwania, RAG i odpowiedzi AI.'
        }
      />

      <section className="knowledge-v2__overview">
        <div className="ui-card knowledge-v2__overview-item">
          <div className="knowledge-v2__overview-icon">
            <Library size={20} />
          </div>

          <div>
            <span>Dokumenty</span>

            <strong>
              {demoKnowledgeDocuments.length}
            </strong>
          </div>
        </div>

        <div className="ui-card knowledge-v2__overview-item">
          <div className="knowledge-v2__overview-icon">
            <FileText size={20} />
          </div>

          <div>
            <span>Kategorie</span>

            <strong>{categories.length}</strong>
          </div>
        </div>

        <div className="ui-card knowledge-v2__overview-item">
          <div className="knowledge-v2__overview-icon">
            <Search size={20} />
          </div>

          <div>
            <span>Widoczne wyniki</span>

            <strong>
              {filteredDocuments.length}
            </strong>
          </div>
        </div>
      </section>

      <section className="ui-section-stack">
        <SectionHeader
          title="Biblioteka dokumentów"
          description="Dokumenty dostępne w kontekście wiedzy organizacji"
          meta={`${filteredDocuments.length} z ${demoKnowledgeDocuments.length}`}
        />

        <div className="knowledge-v2__toolbar">
          <label className="knowledge-v2__search">
            <Search
              size={18}
              strokeWidth={1.9}
            />

            <input
              type="search"
              value={searchQuery}
              onChange={(event) =>
                setSearchQuery(event.target.value)
              }
              placeholder="Szukaj po nazwie, kodzie lub kategorii..."
              aria-label="Szukaj dokumentów"
            />
          </label>

          <select
            className="knowledge-v2__select"
            value={categoryFilter}
            onChange={(event) =>
              setCategoryFilter(event.target.value)
            }
            aria-label="Filtruj według kategorii"
          >
            <option value="ALL">
              Wszystkie kategorie
            </option>

            {categories.map((category) => (
              <option
                key={category}
                value={category}
              >
                {category}
              </option>
            ))}
          </select>
        </div>

        <DataTable
          columns={columns}
          rows={filteredDocuments}
          getRowKey={(document) => document.code}
          emptyState={
            <div className="knowledge-v2__empty">
              <FileText size={26} />

              <strong>
                Brak pasujących dokumentów
              </strong>

              <span>
                Zmień wyszukiwanie lub wybrany filtr.
              </span>
            </div>
          }
        />
      </section>
    </div>
  )
}

export default KnowledgePage