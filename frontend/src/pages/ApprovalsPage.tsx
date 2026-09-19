import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  Database,
  FileText,
  ShieldCheck,
  UserRoundCheck,
  Workflow,
  XCircle,
} from 'lucide-react'

import './ApprovalsPage.css'

const approvals = [
  {
    icon: AlertTriangle,
    priority: 'Wysoki',
    priorityTone: 'high',
    title: 'Zmiana terminu realizacji ORD-1048',
    description:
      'Proponowana zmiana terminu realizacji zamówienia z powodu ryzyka opóźnienia dostawy komponentu CMP-204.',
    actionType: 'Aktualizacja zamówienia',
    requestedBy: 'Enterprise AI Workspace',
    createdAt: '19 września 2026 · 10:32',
    risk: 'Zmiana wpływa na termin dostawy do klienta.',
  },
  {
    icon: Database,
    priority: 'Normalny',
    priorityTone: 'normal',
    title: 'Utworzenie wniosku zakupowego',
    description:
      'System przygotował wniosek zakupowy dla komponentu CMP-204 na podstawie aktualnego stanu magazynowego.',
    actionType: 'ERP · Zakupy',
    requestedBy: 'Workflow operacyjny',
    createdAt: '19 września 2026 · 09:48',
    risk: 'Wymagane potwierdzenie przed przekazaniem do ERP.',
  },
  {
    icon: Workflow,
    priority: 'Normalny',
    priorityTone: 'normal',
    title: 'Zmiana statusu zamówienia ORD-1042',
    description:
      'Proponowana zmiana statusu po potwierdzeniu kompletności dokumentacji i dostępności towaru.',
    actionType: 'Workflow · Zamówienia',
    requestedBy: 'Automatyzacja',
    createdAt: '19 września 2026 · 09:14',
    risk: 'Operacja zostanie wykonana dopiero po zatwierdzeniu.',
  },
]

function ApprovalsPage() {
  return (
    <div className="approvals-page">
      <section className="approvals-hero">
        <div className="approvals-hero-main">
          <div className="approvals-hero-icon">
            <UserRoundCheck size={23} />
          </div>

          <div>
            <span className="section-kicker">
              Human-in-the-loop governance
            </span>

            <h2>Zatwierdzenia</h2>

            <p>
              Działania przygotowane przez system, które wymagają
              decyzji człowieka przed wykonaniem.
            </p>
          </div>
        </div>

        <div className="approvals-summary">
          <div className="approvals-summary-icon">
            <ShieldCheck size={18} />
          </div>

          <div>
            <span>Oczekuje na decyzję</span>
            <strong>3 działania</strong>
          </div>
        </div>
      </section>

      <section className="approvals-stats">
        <article className="approvals-stat-card">
          <span>Wszystkie oczekujące</span>
          <strong>3</strong>
        </article>

        <article className="approvals-stat-card">
          <span>Wysoki priorytet</span>
          <strong>1</strong>
        </article>

        <article className="approvals-stat-card">
          <span>Dzisiaj</span>
          <strong>3</strong>
        </article>

        <article className="approvals-stat-card">
          <span>Po terminie</span>
          <strong>0</strong>
        </article>
      </section>

      <section className="approvals-list">
        {approvals.map((approval) => {
          const Icon = approval.icon

          return (
            <article
              className="panel-card approval-card"
              key={approval.title}
            >
              <div className="approval-card-main">
                <div
                  className={`approval-card-icon ${approval.priorityTone}`}
                >
                  <Icon size={20} />
                </div>

                <div className="approval-card-content">
                  <div className="approval-card-topline">
                    <span
                      className={`approval-priority ${approval.priorityTone}`}
                    >
                      {approval.priority}
                    </span>

                    <span className="approval-created">
                      <Clock3 size={14} />
                      {approval.createdAt}
                    </span>
                  </div>

                  <h3>{approval.title}</h3>

                  <p className="approval-description">
                    {approval.description}
                  </p>

                  <div className="approval-meta-grid">
                    <div className="approval-meta-item">
                      <span>Typ działania</span>
                      <strong>{approval.actionType}</strong>
                    </div>

                    <div className="approval-meta-item">
                      <span>Inicjator</span>
                      <strong>{approval.requestedBy}</strong>
                    </div>
                  </div>

                  <div className="approval-risk">
                    <AlertTriangle size={16} />

                    <div>
                      <span>Kontrola ryzyka</span>
                      <strong>{approval.risk}</strong>
                    </div>
                  </div>
                </div>
              </div>

              <div className="approval-card-actions">
                <button
                  className="approval-secondary-button"
                  type="button"
                >
                  <FileText size={16} />
                  Szczegóły
                </button>

                <div className="approval-decision-actions">
                  <button
                    className="approval-reject-button"
                    type="button"
                  >
                    <XCircle size={17} />
                    Odrzuć
                  </button>

                  <button
                    className="approval-approve-button"
                    type="button"
                  >
                    <CheckCircle2 size={17} />
                    Zatwierdź
                  </button>
                </div>
              </div>
            </article>
          )
        })}
      </section>
    </div>
  )
}

export default ApprovalsPage