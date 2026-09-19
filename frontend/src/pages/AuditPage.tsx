import {
  Bot,
  CheckCircle2,
  Database,
  FileText,
  History,
  Search,
  ShieldCheck,
  UserRound,
  Workflow,
  XCircle,
} from 'lucide-react'

import './AuditPage.css'

const auditEvents = [
  {
    icon: CheckCircle2,
    tone: 'success',
    event: 'Zatwierdzono działanie',
    description:
      'Anna Kowalska zatwierdziła zmianę terminu realizacji ORD-1048.',
    actor: 'Anna Kowalska',
    source: 'Approvals',
    status: 'SUCCESS',
    time: '10:42',
    traceId: 'trc_8a42d1f9',
    requestId: 'req_51c7a3e2',
    actionId: 'act_9f31b7c2',
  },
  {
    icon: Workflow,
    tone: 'success',
    event: 'Wykonano działanie',
    description:
      'Zatwierdzona aktualizacja terminu ORD-1048 została wykonana w ERP.',
    actor: 'Enterprise AI Workspace',
    source: 'Governed Execution',
    status: 'SUCCESS',
    time: '10:44',
    traceId: 'trc_8a42d1f9',
    requestId: 'req_51c7a3e2',
    actionId: 'act_9f31b7c2',
  },
  {
    icon: Bot,
    tone: 'info',
    event: 'Wygenerowano odpowiedź AI',
    description:
      'Asystent AI odpowiedział na pytanie dotyczące ryzyka zamówienia ORD-1048.',
    actor: 'Asystent AI',
    source: 'AI Answer',
    status: 'SUCCESS',
    time: '10:18',
    traceId: 'trc_3d71f8a5',
    requestId: 'req_0f62b9c4',
    actionId: '—',
  },
  {
    icon: FileText,
    tone: 'info',
    event: 'Zindeksowano dokument',
    description:
      'Dokument Procedura jakości QMS-04 został dodany do bazy wiedzy.',
    actor: 'Google Drive',
    source: 'Knowledge Hub',
    status: 'SUCCESS',
    time: '09:58',
    traceId: 'trc_7e43c2b1',
    requestId: 'req_6a84d1f3',
    actionId: '—',
  },
  {
    icon: Database,
    tone: 'warning',
    event: 'Ograniczona synchronizacja',
    description:
      'Google Calendar zwrócił częściowy zestaw danych podczas synchronizacji.',
    actor: 'Integration Service',
    source: 'Google Calendar',
    status: 'DEGRADED',
    time: '09:31',
    traceId: 'trc_219d7e46',
    requestId: 'req_93a1f5c8',
    actionId: '—',
  },
  {
    icon: XCircle,
    tone: 'error',
    event: 'Błąd wykonania',
    description:
      'Aktualizacja danych dostawcy SUP-018 została zatrzymana przez błąd systemu źródłowego.',
    actor: 'Governed Execution',
    source: 'ERP',
    status: 'ERROR',
    time: '18 wrz · 16:48',
    traceId: 'trc_5f20c9d7',
    requestId: 'req_2b71e9a4',
    actionId: 'act_71df23a8',
  },
]

function AuditPage() {
  return (
    <div className="audit-page">
      <section className="audit-hero">
        <div className="audit-hero-main">
          <div className="audit-hero-icon">
            <History size={23} />
          </div>

          <div>
            <span className="section-kicker">
              Audit & traceability
            </span>

            <h2>Audyt</h2>

            <p>
              Pełna historia zdarzeń, decyzji, odpowiedzi AI
              i kontrolowanych działań w Enterprise AI Workspace.
            </p>
          </div>
        </div>

        <div className="audit-governance">
          <ShieldCheck size={18} />

          <div>
            <span>Ścieżka audytowa</span>
            <strong>Aktywna</strong>
          </div>
        </div>
      </section>

      <section className="audit-stats">
        <article className="audit-stat-card">
          <span>Zdarzenia dzisiaj</span>
          <strong>142</strong>
        </article>

        <article className="audit-stat-card">
          <span>Operacje AI</span>
          <strong>38</strong>
        </article>

        <article className="audit-stat-card">
          <span>Wykonania</span>
          <strong>7</strong>
        </article>

        <article className="audit-stat-card">
          <span>Błędy</span>
          <strong>1</strong>
        </article>
      </section>

      <section className="panel-card audit-log-card">
        <div className="audit-toolbar">
          <div>
            <span className="section-kicker">
              Audit log
            </span>

            <h3>Historia zdarzeń</h3>
          </div>

          <div className="audit-search">
            <Search size={17} />

            <input
              aria-label="Szukaj w audycie"
              placeholder="Szukaj po trace_id, użytkowniku..."
              type="text"
            />
          </div>
        </div>

        <div className="audit-list">
          {auditEvents.map((item) => {
            const Icon = item.icon

            return (
              <article
                className="audit-event"
                key={`${item.traceId}-${item.time}`}
              >
                <div
                  className={`audit-event-icon ${item.tone}`}
                >
                  <Icon size={18} />
                </div>

                <div className="audit-event-main">
                  <div className="audit-event-heading">
                    <div>
                      <span className="audit-event-source">
                        {item.source}
                      </span>

                      <h4>{item.event}</h4>
                    </div>

                    <span
                      className={`audit-event-status ${item.tone}`}
                    >
                      {item.status}
                    </span>
                  </div>

                  <p>{item.description}</p>

                  <div className="audit-event-meta">
                    <div>
                      <UserRound size={14} />
                      <span>{item.actor}</span>
                    </div>

                    <div>
                      <span>{item.time}</span>
                    </div>
                  </div>

                  <div className="audit-identifiers">
                    <div>
                      <span>trace_id</span>
                      <strong>{item.traceId}</strong>
                    </div>

                    <div>
                      <span>request_id</span>
                      <strong>{item.requestId}</strong>
                    </div>

                    <div>
                      <span>action_id</span>
                      <strong>{item.actionId}</strong>
                    </div>
                  </div>
                </div>
              </article>
            )
          })}
        </div>
      </section>
    </div>
  )
}

export default AuditPage