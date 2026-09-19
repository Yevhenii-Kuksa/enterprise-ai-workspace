import {
  CheckCircle2,
  Clock3,
  Database,
  ShieldCheck,
  Workflow,
} from 'lucide-react'

import { demoExecutions } from '../data/demoData'

import './ExecutionsPage.css'

const executions = demoExecutions.map((execution) => {
  if (execution.code === 'EXECUTION-001') {
    return {
      ...execution,
      icon: Database,
      statusLabel: 'Zakończono',
      statusTone: 'success',
      title: 'Pilne zamówienie materiału MAT-204',
      description:
        'Po zatwierdzeniu działanie zostało przekazane do kontrolowanej obsługi zakupowej.',
      approvedBy: 'Piotr Nowak',
      executedAt: '19 września 2026 · 10:52',
      system: 'ERP · Zakupy',
      actionId: 'act_mat204_urgent_order',
      traceId: 'trc_ord1048_mat204_001',
      idempotency: 'Pierwsze wykonanie',
    }
  }

  return {
    ...execution,
    icon: Workflow,
    statusLabel: 'Zakończono',
    statusTone: 'success',
    title: 'Aktualizacja harmonogramu ORD-1048',
    description:
      'Po zatwierdzeniu harmonogram zamówienia został oznaczony do aktualizacji po przyjęciu MAT-204.',
    approvedBy: 'Anna Kowalska',
    executedAt: '19 września 2026 · 10:57',
    system: 'Produkcja · Harmonogram',
    actionId: 'act_ord1048_schedule_update',
    traceId: 'trc_ord1048_schedule_002',
    idempotency: 'Pierwsze wykonanie',
  }
})

function ExecutionsPage() {
  const succeededCount = executions.filter(
    (execution) => execution.status === 'SUCCEEDED',
  ).length

  return (
    <div className="executions-page">
      <section className="executions-hero">
        <div className="executions-hero-main">
          <div className="executions-hero-icon">
            <Workflow size={23} />
          </div>

          <div>
            <span className="section-kicker">
              Governed execution
            </span>

            <h2>Wykonania</h2>

            <p>
              Historia działań wykonanych po zatwierdzeniu,
              z pełną informacją o statusie, identyfikatorach
              i ścieżce audytowej.
            </p>
          </div>
        </div>

        <div className="executions-summary">
          <div className="executions-summary-icon">
            <ShieldCheck size={18} />
          </div>

          <div>
            <span>Kontrola wykonania</span>
            <strong>Governance aktywne</strong>
          </div>
        </div>
      </section>

      <section className="executions-stats">
        <article className="executions-stat-card">
          <span>Wykonane dzisiaj</span>
          <strong>{executions.length}</strong>
        </article>

        <article className="executions-stat-card">
          <span>Zakończone</span>
          <strong>{succeededCount}</strong>
        </article>

        <article className="executions-stat-card">
          <span>Replay zablokowany</span>
          <strong>0</strong>
        </article>

        <article className="executions-stat-card">
          <span>Błędy</span>
          <strong>0</strong>
        </article>
      </section>

      <section className="panel-card executions-table-card">
        <div className="executions-table-header">
          <div>
            <span className="section-kicker">
              Historia
            </span>

            <h3>Kontrolowane wykonania</h3>
          </div>

          <span className="executions-count">
            Ostatnie {executions.length} zdarzenia
          </span>
        </div>

        <div className="executions-table">
          <div className="executions-table-head">
            <span>Działanie</span>
            <span>System</span>
            <span>Zatwierdził</span>
            <span>Status</span>
            <span>Czas</span>
          </div>

          {executions.map((execution) => {
            const Icon = execution.icon

            return (
              <div
                className="executions-table-row"
                key={execution.code}
              >
                <div className="execution-main">
                  <div
                    className={`execution-icon ${execution.statusTone}`}
                  >
                    <Icon size={18} />
                  </div>

                  <div>
                    <strong>{execution.title}</strong>

                    <span>
                      {execution.description}
                    </span>
                  </div>
                </div>

                <div className="execution-system">
                  <Database size={15} />

                  <span>{execution.system}</span>
                </div>

                <span className="execution-approved-by">
                  {execution.approvedBy}
                </span>

                <span
                  className={`execution-status ${execution.statusTone}`}
                >
                  <CheckCircle2 size={14} />
                  {execution.statusLabel}
                </span>

                <div className="execution-time">
                  <Clock3 size={14} />

                  <span>{execution.executedAt}</span>
                </div>

                <div className="execution-trace">
                  <div>
                    <span>proposal</span>
                    <strong>
                      {execution.proposalCode}
                    </strong>
                  </div>

                  <div>
                    <span>action_id</span>
                    <strong>
                      {execution.actionId}
                    </strong>
                  </div>

                  <div>
                    <span>trace_id</span>
                    <strong>
                      {execution.traceId}
                    </strong>
                  </div>

                  <div>
                    <span>Idempotency</span>
                    <strong>
                      {execution.idempotency}
                    </strong>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </section>
    </div>
  )
}

export default ExecutionsPage