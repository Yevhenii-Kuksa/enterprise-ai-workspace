import {
  Activity,
  FileSearch,
  Search,
  ShieldCheck,
} from 'lucide-react'
import {
  useMemo,
  useState,
} from 'react'

import DataTable, {
  type DataTableColumn,
} from '../components/ui/DataTable'
import KpiCard from '../components/ui/KpiCard'
import PageHeader from '../components/ui/PageHeader'
import SectionHeader from '../components/ui/SectionHeader'
import StatusBadge from '../components/ui/StatusBadge'
import { demoAuditEvents } from '../data/demoData'

import './AuditPage.css'

type AuditEvent =
  (typeof demoAuditEvents)[number]

function getEventTone(eventType: string) {
  if (
    eventType.includes('EXECUTED') ||
    eventType.includes('GRANTED')
  ) {
    return 'success' as const
  }

  if (
    eventType.includes('FAILED') ||
    eventType.includes('DENIED')
  ) {
    return 'danger' as const
  }

  if (
    eventType.includes('PENDING') ||
    eventType.includes('REQUESTED')
  ) {
    return 'warning' as const
  }

  return 'info' as const
}

function formatEventLabel(eventType: string) {
  const labels: Record<string, string> = {
    AI_INSIGHT_CREATED: 'Utworzono analizę AI',
    ACTION_PROPOSAL_CREATED: 'Utworzono propozycję działania',
    APPROVAL_GRANTED: 'Zatwierdzono działanie',
    APPROVAL_REJECTED: 'Odrzucono działanie',
    ACTION_EXECUTED: 'Wykonano działanie',
    ACTION_EXECUTION_STARTED: 'Rozpoczęto wykonanie działania',
    ACTION_EXECUTION_FAILED: 'Błąd wykonania działania',
  }

  return labels[eventType] ?? 'Zdarzenie systemowe'
}

function AuditPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [eventFilter, setEventFilter] = useState('ALL')
  const [selectedIndex, setSelectedIndex] = useState(0)

  const eventTypes = useMemo(
    () =>
      Array.from(
        new Set(
          demoAuditEvents.map(
            (event) => event.event,
          ),
        ),
      ).sort(),
    [],
  )

  const filteredEvents = useMemo(() => {
    const query = searchQuery
      .trim()
      .toLowerCase()

    return demoAuditEvents.filter((event) => {
      const matchesSearch =
        query.length === 0 ||
        event.event
          .toLowerCase()
          .includes(query) ||
        event.description
          .toLowerCase()
          .includes(query) ||
        event.time
          .toLowerCase()
          .includes(query)

      const matchesType =
        eventFilter === 'ALL' ||
        event.event === eventFilter

      return matchesSearch && matchesType
    })
  }, [eventFilter, searchQuery])

  const selectedEvent =
    filteredEvents[selectedIndex] ??
    filteredEvents[0] ??
    demoAuditEvents[0]

  const columns: DataTableColumn<AuditEvent>[] = [
    {
      key: 'event',
      header: 'Typ zdarzenia',
      width: '230px',
      render: (event) => (
        <button
          className="audit-v2__event-button"
          type="button"
          onClick={() =>
            setSelectedIndex(
              filteredEvents.indexOf(event),
            )
          }
        >
          <div className="audit-v2__event-icon">
            <Activity size={17} />
          </div>

          <div>
            <span className="ui-table__primary">
              {formatEventLabel(event.event)}
            </span>

            <span className="ui-table__secondary">
              {event.event}
            </span>
          </div>
        </button>
      ),
    },
    {
      key: 'description',
      header: 'Opis',
      render: (event) => (
        <span className="audit-v2__description">
          {event.description}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      width: '140px',
      render: (event) => (
        <StatusBadge
          tone={getEventTone(event.event)}
        >
          Zapisano
        </StatusBadge>
      ),
    },
    {
      key: 'time',
      header: 'Czas',
      width: '110px',
      render: (event) => (
        <span className="audit-v2__time">
          {event.time}
        </span>
      ),
    },
  ]

  return (
    <div className="ui-page-stack audit-v2">
      <PageHeader
        eyebrow="Audyt i identyfikowalnoЕ›Д‡"
        title="Audyt"
        description={
          'Chronologiczny zapis kluczowych zdarzeЕ„, decyzji i wykonaЕ„ ' +
          'w Enterprise AI Workspace.'
        }
        actions={
          <div className="audit-v2__integrity">
            <ShieldCheck size={18} />

            <div>
              <span>ЕљcieЕјka audytowa</span>
              <strong>Aktywny</strong>
            </div>
          </div>
        }
      />

      <section className="ui-kpi-grid">
        <KpiCard
          label="Zdarzenia"
          value={demoAuditEvents.length}
          meta="Zdarzenia w scenariuszu demo"
          icon={<Activity size={20} />}
        />

        <KpiCard
          label="Typy zdarzeЕ„"
          value={eventTypes.length}
          meta="Unikalne klasy eventГіw"
          icon={<FileSearch size={20} />}
        />

        <KpiCard
          label="Widoczne"
          value={filteredEvents.length}
          meta="Wyniki po zastosowaniu filtrГіw"
          icon={<Search size={20} />}
        />

        <KpiCard
          label="IdentyfikowalnoЕ›Д‡"
          value="100%"
          meta="Kluczowe dziaЕ‚ania objД™te Е›cieЕјkД… audytowД…"
          icon={<ShieldCheck size={20} />}
        />
      </section>

      <section className="ui-section-stack">
        <SectionHeader
          title="Dziennik audytowy"
          description="Zdarzenia uporzД…dkowane w jednym rejestrze"
          meta={`${filteredEvents.length} wpisГіw`}
        />

        <div className="audit-v2__toolbar">
          <label className="audit-v2__search">
            <Search
              size={18}
              strokeWidth={1.9}
            />

            <input
              type="search"
              value={searchQuery}
              onChange={(event) => {
                setSearchQuery(event.target.value)
                setSelectedIndex(0)
              }}
              placeholder="Szukaj w zdarzeniach audytowych..."
              aria-label="Szukaj w audycie"
            />
          </label>

          <select
            className="audit-v2__select"
            value={eventFilter}
            onChange={(event) => {
              setEventFilter(event.target.value)
              setSelectedIndex(0)
            }}
            aria-label="Filtruj wedЕ‚ug typu zdarzenia"
          >
            <option value="ALL">
              Wszystkie typy zdarzeЕ„
            </option>

            {eventTypes.map((eventType) => (
              <option
                key={eventType}
                value={eventType}
              >
                {formatEventLabel(eventType)}
              </option>
            ))}
          </select>
        </div>

        <div className="audit-v2__workspace">
          <div className="audit-v2__table">
            <DataTable
              columns={columns}
              rows={filteredEvents}
              getRowKey={(event) =>
                `${event.time}-${event.event}-${event.description}`
              }
              emptyState={
                <div className="audit-v2__empty">
                  <FileSearch size={26} />

                  <strong>
                    Brak zdarzeЕ„
                  </strong>

                  <span>
                    ZmieЕ„ wyszukiwanie lub wybrany filtr.
                  </span>
                </div>
              }
            />
          </div>

          {selectedEvent ? (
            <aside className="ui-card audit-v2__detail">
              <header className="audit-v2__detail-header">
                <div>
                  <span className="audit-v2__overline">
                    SzczegГіЕ‚y zdarzenia
                  </span>

                  <h2>
                    {formatEventLabel(
                      selectedEvent.event,
                    )}
                  </h2>

                  <span className="audit-v2__code">
                    {selectedEvent.event}
                  </span>
                </div>

                <StatusBadge
                  tone={getEventTone(
                    selectedEvent.event,
                  )}
                >
                  Zapisano
                </StatusBadge>
              </header>

              <div className="audit-v2__detail-meta">
                <div>
                  <span>Czas</span>
                  <strong>
                    {selectedEvent.time}
                  </strong>
                </div>

                <div>
                  <span>Е№rГіdЕ‚o</span>
                  <strong>
                    Enterprise AI Workspace
                  </strong>
                </div>
              </div>

              <section className="audit-v2__detail-section">
                <div className="audit-v2__detail-icon">
                  <Activity size={19} />
                </div>

                <div>
                  <span>Opis zdarzenia</span>

                  <p>
                    {selectedEvent.description}
                  </p>
                </div>
              </section>

              <footer className="audit-v2__trace">
                <ShieldCheck size={20} />

                <div>
                  <strong>
                    IdentyfikowalnoЕ›Д‡ zachowana
                  </strong>

                  <span>
                    Zdarzenie pozostaje czД™Е›ciД… Е›cieЕјki audytowej Workspace.
                  </span>
                </div>
              </footer>
            </aside>
          ) : null}
        </div>
      </section>
    </div>
  )
}

export default AuditPage