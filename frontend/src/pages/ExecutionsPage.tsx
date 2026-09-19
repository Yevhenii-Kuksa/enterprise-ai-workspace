import {
  CheckCircle2,
  Clock3,
  Database,
  RotateCcw,
  ShieldCheck,
  Workflow,
  XCircle,
} from 'lucide-react'

import './ExecutionsPage.css'

const executions = [
  {
    status: 'Zakończono',
    statusTone: 'success',
    icon: CheckCircle2,
    title: 'Aktualizacja terminu ORD-1048',
    description:
      'Zatwierdzona zmiana terminu została wykonana w systemie ERP.',
    approvedBy: 'Anna Kowalska',
    executedAt: '19 września 2026 · 10:44',
    system: 'ERP',
    actionId: 'act_9f31b7c2',
    traceId: 'trc_8a42d1f9',
    idempotency: 'Pierwsze wykonanie',
  },
  {
    status: 'Zakończono',
    statusTone: 'success',
    icon: Database,
    title: 'Utworzenie wniosku zakupowego CMP-204',
    description:
      'Po zatwierdzeniu utworzono kontrolowany wniosek zakupowy.',
    approvedBy: 'Anna Kowalska',
    executedAt: '19 września 2026 · 10:12',
    system: 'ERP · Zakupy',
    actionId: 'act_6c04d8e1',
    traceId: 'trc_31e7c5a4',
    idempotency: 'Pierwsze wykonanie',
  },
  {
    status: 'Powtórzone bez zmian',
    statusTone: 'replayed',
    icon: RotateCcw,
    title: 'Synchronizacja statusu ORD-1039',
    description:
      'System wykrył wcześniejsze wykonanie tej samej operacji i nie wykonał jej ponownie.',
    approvedBy: 'Piotr Nowak',
    executedAt: '19 września 2026 · 09:36',
    system: 'ERP · Zamówienia',
    actionId: 'act_42b9f1de',
    traceId: 'trc_b8124e63',
    idempotency: 'Replay zablokowany',
  },
  {
    status: 'Błąd',
    statusTone: 'error',
    icon: XCircle,
    title: 'Aktualizacja danych dostawcy SUP-018',
    description:
      'Wykonanie zostało zatrzymane z powodu chwilowego błędu źródłowego systemu.',
    approvedBy: 'Anna Kowalska',
    executedAt: '18 września 2026 · 16:48',
    system: 'ERP · Dostawcy',
    actionId: 'act_71df23a8',
    traceId: 'trc_5f20c9d7',
    idempotency: 'Można ponowić',
  },
]

function ExecutionsPage() {
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
          <strong>7</strong>
        </article>

        <article className="executions-stat-card">
          <span>Zakończone</span>
          <strong>6</strong>
        </article>

        <article className="executions-stat-card">
          <span>Replay zablokowany</span>
          <strong>1</strong>
        </article>

        <article className="executions-stat-card">
          <span>Błędy</span>
          <strong>1</strong>
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
            Ostatnie 4 zdarzenia
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
                key={execution.actionId}
              >
                <div className="execution-main">
                  <div
                    className={`execution-icon ${execution.statusTone}`}
                  >
                    <Icon size={18} />
                  </div>

                  <div>
                    <strong>{execution.title}</strong>
                    <span>{execution.description}</span>
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
                  {execution.status}
                </span>

                <div className="execution-time">
                  <Clock3 size={14} />
                  <span>{execution.executedAt}</span>
                </div>

                <div className="execution-trace">
                  <div>
                    <span>action_id</span>
                    <strong>{execution.actionId}</strong>
                  </div>

                  <div>
                    <span>trace_id</span>
                    <strong>{execution.traceId}</strong>
                  </div>

                  <div>
                    <span>Idempotency</span>
                    <strong>{execution.idempotency}</strong>
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