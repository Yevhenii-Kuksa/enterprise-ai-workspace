import {
  CheckCircle2,
  Database,
  FileCheck2,
  PlayCircle,
  ShieldCheck,
  UserRound,
} from 'lucide-react'
import { useMemo, useState } from 'react'

import DataTable, {
  type DataTableColumn,
} from '../components/ui/DataTable'
import KpiCard from '../components/ui/KpiCard'
import PageHeader from '../components/ui/PageHeader'
import SectionHeader from '../components/ui/SectionHeader'
import StatusBadge from '../components/ui/StatusBadge'

import './ExecutionsPage.css'

type ExecutionStatus = 'SUCCEEDED'

type ExecutionRecord = {
  id: string
  proposalCode: string
  action: string
  system: string
  actor: string
  status: ExecutionStatus
  executedAt: string
  result: string
  governance: string
}

const executions: ExecutionRecord[] = [
  {
    id: 'Wykonanie 01',
    proposalCode: 'ACT-PROP-001',
    action: 'Utworzyć pilne zamówienie materiału MAT-204',
    system: 'ERP',
    actor: 'Piotr Nowak',
    status: 'SUCCEEDED',
    executedAt: '19.09.2026',
    result:
      'Zatwierdzone działanie zakupowe zostało wykonane zgodnie z decyzją użytkownika.',
    governance:
      'Wykonanie było możliwe dopiero po zatwierdzeniu ACT-PROP-001.',
  },
  {
    id: 'Wykonanie 02',
    proposalCode: 'ACT-PROP-002',
    action: 'Zaktualizować harmonogram produkcji ORD-1048',
    system: 'ERP',
    actor: 'Anna Kowalska',
    status: 'SUCCEEDED',
    executedAt: '19.09.2026',
    result:
      'Harmonogram produkcji ORD-1048 został zaktualizowany po zatwierdzeniu działania.',
    governance:
      'Wykonanie było możliwe dopiero po zatwierdzeniu ACT-PROP-002.',
  },
]

function ExecutionsPage() {
  const [selectedId, setSelectedId] = useState(
    executions[0]?.id ?? '',
  )

  const selectedExecution = useMemo(
    () =>
      executions.find(
        (execution) => execution.id === selectedId,
      ) ?? executions[0],
    [selectedId],
  )

  const columns: DataTableColumn<ExecutionRecord>[] = [
    {
      key: 'action',
      header: 'Działanie',
      render: (execution) => (
        <button
          className="executions-v2__row-button"
          type="button"
          onClick={() => setSelectedId(execution.id)}
        >
          <div className="executions-v2__action-icon">
            <PlayCircle size={18} />
          </div>

          <div>
            <span className="ui-table__primary">
              {execution.action}
            </span>

            <span className="ui-table__secondary">
              {execution.proposalCode}
            </span>
          </div>
        </button>
      ),
    },
    {
      key: 'system',
      header: 'System',
      width: '150px',
      render: (execution) => (
        <div className="executions-v2__system">
          <Database size={16} />
          <span>{execution.system}</span>
        </div>
      ),
    },
    {
      key: 'actor',
      header: 'Zatwierdził',
      width: '210px',
      render: (execution) => (
        <div className="executions-v2__actor">
          <UserRound size={16} />
          <span>{execution.actor}</span>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      width: '150px',
      render: () => (
        <StatusBadge tone="success">
          ZAKOŃCZONE
        </StatusBadge>
      ),
    },
    {
      key: 'date',
      header: 'Data',
      width: '150px',
      render: (execution) => execution.executedAt,
    },
  ]

  return (
    <div className="ui-page-stack executions-v2">
      <PageHeader
        eyebrow="Kontrolowane wykonanie"
        title="Wykonania"
        description={
          'Historia działań wykonanych po zatwierdzeniu przez uprawnionych ' +
          'użytkowników. Krytyczne operacje nie są wykonywane automatycznie.'
        }
        actions={
          <div className="executions-v2__governance">
            <ShieldCheck size={18} />

            <div>
              <span>Zasady wykonania</span>
              <strong>Wymagane zatwierdzenie przez człowieka</strong>
            </div>
          </div>
        }
      />

      <section className="ui-kpi-grid">
        <KpiCard
          label="Wykonania"
          value={executions.length}
          meta="Zarejestrowane kontrolowane wykonania"
          icon={<PlayCircle size={20} />}
        />

        <KpiCard
          label="Zakończone sukcesem"
          value={executions.length}
          meta="Wszystkie wykonane działania zakończone poprawnie"
          icon={<CheckCircle2 size={20} />}
        />

        <KpiCard
          label="Nieudane"
          value="0"
          meta="Brak błędów wykonania w scenariuszu demo"
          icon={<FileCheck2 size={20} />}
        />

        <KpiCard
          label="Automatyczne wykonanie"
          value="0"
          meta="Brak krytycznych działań wykonanych bez zatwierdzenia"
          icon={<ShieldCheck size={20} />}
        />
      </section>

      <section className="executions-v2__workspace">
        <div className="executions-v2__history">
          <SectionHeader
            title="Historia wykonań"
            description="Zatwierdzone działania i ich wynik"
            meta={`${executions.length} wykonania`}
          />

          <DataTable
            columns={columns}
            rows={executions}
            getRowKey={(execution) => execution.id}
          />
        </div>

        {selectedExecution ? (
          <aside className="ui-card executions-v2__detail">
            <header className="executions-v2__detail-header">
              <div>
                <span className="executions-v2__overline">
                  Szczegóły wykonania
                </span>

                <h2>{selectedExecution.action}</h2>

                <span className="executions-v2__code">
                  {selectedExecution.proposalCode}
                </span>
              </div>

              <StatusBadge tone="success">
                ZAKOŃCZONE
              </StatusBadge>
            </header>

            <div className="executions-v2__detail-grid">
              <div>
                <span>System</span>
                <strong>{selectedExecution.system}</strong>
              </div>

              <div>
                <span>Zatwierdził</span>
                <strong>{selectedExecution.actor}</strong>
              </div>

              <div>
                <span>Data wykonania</span>
                <strong>
                  {selectedExecution.executedAt}
                </strong>
              </div>

              <div>
                <span>Tryb</span>
                <strong>Kontrolowane wykonanie</strong>
              </div>
            </div>

            <section className="executions-v2__detail-section">
              <div className="executions-v2__section-icon">
                <CheckCircle2 size={19} />
              </div>

              <div>
                <span>Wynik wykonania</span>
                <p>{selectedExecution.result}</p>
              </div>
            </section>

            <section className="executions-v2__detail-section">
              <div className="executions-v2__section-icon executions-v2__section-icon--governance">
                <ShieldCheck size={19} />
              </div>

              <div>
                <span>Kontrola wykonania</span>
                <p>{selectedExecution.governance}</p>
              </div>
            </section>

            <footer className="executions-v2__trace">
              <ShieldCheck size={20} />

              <div>
                <strong>
                  Pełna ścieżka audytowa dostępna
                </strong>

                <span>
                  Zatwierdzenie → Wykonanie → Ścieżka audytowa
                </span>
              </div>
            </footer>
          </aside>
        ) : null}
      </section>
    </div>
  )
}

export default ExecutionsPage