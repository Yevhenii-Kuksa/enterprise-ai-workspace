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

import {
  demoApprovals,
  mainRisk,
} from '../data/demoData'

import './ApprovalsPage.css'

const approvalPresentation = {
  'ACT-PROP-001': {
    icon: Database,
    priority: 'Wysoki',
    priorityTone: 'high',
    actionType: 'ERP · Zakupy',
    requestedBy: 'Enterprise AI Workspace',
    createdAt: '19 września 2026 · 10:35',
    risk: (
      `Brak ${mainRisk.shortage} m² ${mainRisk.materialCode} ` +
      `może wpłynąć na termin wysyłki ${mainRisk.orderNumber}.`
    ),
  },
  'ACT-PROP-002': {
    icon: Workflow,
    priority: 'Wysoki',
    priorityTone: 'high',
    actionType: 'Produkcja · Harmonogram',
    requestedBy: 'Enterprise AI Workspace',
    createdAt: '19 września 2026 · 10:40',
    risk: (
      `Zmiana harmonogramu wpływa na realizację ` +
      `${mainRisk.orderNumber} i termin ${mainRisk.shipmentDate}.`
    ),
  },
  'ACT-PROP-003': {
    icon: AlertTriangle,
    priority: 'Normalny',
    priorityTone: 'normal',
    actionType: 'Klient · Komunikacja',
    requestedBy: 'Enterprise AI Workspace',
    createdAt: '19 września 2026 · 10:45',
    risk: (
      'Komunikat do klienta wymaga zatwierdzenia człowieka ' +
      'przed wysłaniem.'
    ),
  },
} as const

const approvals = demoApprovals.map((approval) => ({
  ...approval,
  ...approvalPresentation[
    approval.code as keyof typeof approvalPresentation
  ],
}))

function ApprovalsPage() {
  const pendingCount = approvals.filter(
    (approval) => approval.status === 'PENDING',
  ).length

  const approvedCount = approvals.filter(
    (approval) => approval.status === 'APPROVED',
  ).length

  const highPriorityCount = approvals.filter(
    (approval) => approval.priorityTone === 'high',
  ).length

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
              decyzji człowieka przed wykonaniem lub zostały już
              zatwierdzone w ramach procesu governance.
            </p>
          </div>
        </div>

        <div className="approvals-summary">
          <div className="approvals-summary-icon">
            <ShieldCheck size={18} />
          </div>

          <div>
            <span>Oczekuje na decyzję</span>
            <strong>
              {pendingCount}{' '}
              {pendingCount === 1 ? 'działanie' : 'działania'}
            </strong>
          </div>
        </div>
      </section>

      <section className="approvals-stats">
        <article className="approvals-stat-card">
          <span>Wszystkie propozycje</span>
          <strong>{approvals.length}</strong>
        </article>

        <article className="approvals-stat-card">
          <span>Zatwierdzone</span>
          <strong>{approvedCount}</strong>
        </article>

        <article className="approvals-stat-card">
          <span>Wysoki priorytet</span>
          <strong>{highPriorityCount}</strong>
        </article>

        <article className="approvals-stat-card">
          <span>Oczekujące</span>
          <strong>{pendingCount}</strong>
        </article>
      </section>

      <section className="approvals-list">
        {approvals.map((approval) => {
          const Icon = approval.icon
          const isPending = approval.status === 'PENDING'

          return (
            <article
              className="panel-card approval-card"
              key={approval.code}
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
                    {approval.code} · {approval.actionType}
                  </p>

                  <div className="approval-meta-grid">
                    <div className="approval-meta-item">
                      <span>Status</span>
                      <strong>
                        {isPending ? 'Oczekuje' : 'Zatwierdzone'}
                      </strong>
                    </div>

                    <div className="approval-meta-item">
                      <span>Zatwierdzający</span>
                      <strong>
                        {approval.approver ?? 'Nie przypisano'}
                      </strong>
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

                {isPending ? (
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
                ) : (
                  <div className="approval-decision-actions">
                    <button
                      className="approval-approve-button"
                      disabled
                      type="button"
                    >
                      <CheckCircle2 size={17} />
                      Zatwierdzone
                    </button>
                  </div>
                )}
              </div>
            </article>
          )
        })}
      </section>
    </div>
  )
}

export default ApprovalsPage