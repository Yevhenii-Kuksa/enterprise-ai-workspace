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
} from 'lucide-react'

import { demoAuditEvents } from '../data/demoData'

import './AuditPage.css'

const eventPresentation = {
  AI_INSIGHT_CREATED: {
    icon: Bot,
    tone: 'success',
    actor: 'Enterprise AI Workspace',
    source: 'AI Intelligence',
    status: 'Zarejestrowano',
  },
  ACTION_PROPOSAL_CREATED: {
    icon: FileText,
    tone: 'success',
    actor: 'Anna Kowalska',
    source: 'Governance Engine',
    status: 'Utworzono',
  },
  APPROVAL_GRANTED: {
    icon: UserRound,
    tone: 'success',
    actor: 'Human Approval',
    source: 'Approval Engine',
    status: 'Zatwierdzono',
  },
  ACTION_EXECUTED: {
    icon: Workflow,
    tone: 'success',
    actor: 'Governed Execution',
    source: 'Execution Engine',
    status: 'Wykonano',
  },
} as const

const auditEvents = demoAuditEvents.map((event, index) => {
  const presentation =
    eventPresentation[
      event.event as keyof typeof eventPresentation
    ]

  const sequence = String(index + 1).padStart(3, '0')

  let actionId = '—'

  if (event.event === 'ACTION_PROPOSAL_CREATED') {
    actionId = `ACT-PROP-${sequence}`
  }

  if (event.event === 'APPROVAL_GRANTED') {
    actionId = `APPROVAL-${sequence}`
  }

  if (event.event === 'ACTION_EXECUTED') {
    actionId = `EXECUTION-${sequence}`
  }

  return {
    ...event,
    ...presentation,
    traceId: `trc_ord1048_${sequence}`,
    requestId: `req_ord1048_${sequence}`,
    actionId,
  }
})

function AuditPage() {
  const aiEventCount = auditEvents.filter(
    (event) => event.event === 'AI_INSIGHT_CREATED',
  ).length

  const approvalCount = auditEvents.filter(
    (event) => event.event === 'APPROVAL_GRANTED',
  ).length

  const executionCount = auditEvents.filter(
    (event) => event.event === 'ACTION_EXECUTED',
  ).length

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
              Pełna historia zdarzeń systemowych,
              decyzji człowieka i kontrolowanych
              wykonań z zachowaniem identyfikatorów
              śledzenia Enterprise AI Workspace.
            </p>
          </div>
        </div>

        <div className="audit-governance">
          <div className="audit-governance-icon">
            <ShieldCheck size={18} />
          </div>

          <div>
            <span>Governance</span>
            <strong>Aktywne</strong>
          </div>
        </div>
      </section>

      <section className="audit-stats">
        <article className="audit-stat-card">
          <span>Zdarzenia dzisiaj</span>
          <strong>{auditEvents.length}</strong>
        </article>

        <article className="audit-stat-card">
          <span>AI insights</span>
          <strong>{aiEventCount}</strong>
        </article>

        <article className="audit-stat-card">
          <span>Zatwierdzenia</span>
          <strong>{approvalCount}</strong>
        </article>

        <article className="audit-stat-card">
          <span>Wykonania</span>
          <strong>{executionCount}</strong>
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
              placeholder="Szukaj zdarzenia..."
              type="text"
            />
          </div>
        </div>

        <div className="audit-list">
          {auditEvents.map((event) => {
            const Icon = event.icon

            return (
              <article
                className="audit-event"
                key={`${event.time}-${event.event}-${event.description}`}
              >
                <div
                  className={`audit-event-icon ${event.tone}`}
                >
                  <Icon size={18} />
                </div>

                <div className="audit-event-main">
                  <div className="audit-event-header">
                    <div>
                      <span className="audit-event-type">
                        {event.event}
                      </span>

                      <h4>{event.description}</h4>
                    </div>

                    <span
                      className={`audit-event-status ${event.tone}`}
                    >
                      <CheckCircle2 size={14} />
                      {event.status}
                    </span>
                  </div>

                  <div className="audit-event-context">
                    <div className="audit-context-item">
                      <UserRound size={15} />

                      <div>
                        <span>Aktor</span>
                        <strong>{event.actor}</strong>
                      </div>
                    </div>

                    <div className="audit-context-item">
                      <Database size={15} />

                      <div>
                        <span>Źródło</span>
                        <strong>{event.source}</strong>
                      </div>
                    </div>

                    <div className="audit-context-item">
                      <History size={15} />

                      <div>
                        <span>Czas</span>
                        <strong>
                          19 września 2026 · {event.time}
                        </strong>
                      </div>
                    </div>
                  </div>

                  <div className="audit-identifiers">
                    <div>
                      <span>trace_id</span>
                      <strong>{event.traceId}</strong>
                    </div>

                    <div>
                      <span>request_id</span>
                      <strong>{event.requestId}</strong>
                    </div>

                    <div>
                      <span>action_id</span>
                      <strong>{event.actionId}</strong>
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