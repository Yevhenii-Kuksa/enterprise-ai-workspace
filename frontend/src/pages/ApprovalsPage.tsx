import {
  CheckCircle2,
  Clock3,
  FileCheck2,
  ShieldCheck,
  TriangleAlert,
  UserRoundCheck,
} from 'lucide-react'
import { useMemo, useState } from 'react'

import KpiCard from '../components/ui/KpiCard'
import PageHeader from '../components/ui/PageHeader'
import SectionHeader from '../components/ui/SectionHeader'
import StatusBadge from '../components/ui/StatusBadge'
import { demoApprovals } from '../data/demoData'

import './ApprovalsPage.css'


type ApprovalMeta = {
  owner: string
  area: string
  risk: 'Wysokie' | 'Średnie'
  createdAt: string
  rationale: string
  impact: string
  reviewer?: string
}

const approvalMeta: Record<string, ApprovalMeta> = {
  'ACT-PROP-001': {
    owner: 'Enterprise AI Workspace',
    area: 'Zakupy',
    risk: 'Wysokie',
    createdAt: '19.09.2026 · 10:45',
    rationale:
      'Niedobór MAT-204 może wpłynąć na termin realizacji ORD-1048.',
    impact:
      'Przyspieszenie zakupu materiału ogranicza ryzyko zatrzymania produkcji.',
    reviewer: 'Piotr Nowak',
  },
  'ACT-PROP-002': {
    owner: 'Enterprise AI Workspace',
    area: 'Produkcja',
    risk: 'Średnie',
    createdAt: '19.09.2026 · 10:48',
    rationale:
      'Aktualny harmonogram produkcji wymaga dostosowania do opóźnionej dostawy MAT-204.',
    impact:
      'Korekta harmonogramu utrzymuje kontrolę nad terminem wysyłki ORD-1048.',
    reviewer: 'Anna Kowalska',
  },
  'ACT-PROP-003': {
    owner: 'Enterprise AI Workspace',
    area: 'Obsługa klienta',
    risk: 'Średnie',
    createdAt: '19.09.2026 · 10:50',
    rationale:
      'Ryzyko terminu powinno zostać zakomunikowane klientowi w kontrolowany sposób.',
    impact:
      'Komunikacja pozwala przygotować klienta na możliwe przesunięcie bez automatycznej wysyłki.',
  },
}

const fallbackMeta: ApprovalMeta = {
  owner: 'Enterprise AI Workspace',
  area: 'Operacje',
  risk: 'Średnie',
  createdAt: '19.09.2026',
  rationale: 'Działanie wymaga kontroli człowieka przed wykonaniem.',
  impact: 'Decyzja wpływa na dalszy przebieg procesu operacyjnego.',
}

function getStatusTone(status: string) {
  if (status === 'APPROVED') {
    return 'success' as const
  }

  if (status === 'PENDING') {
    return 'warning' as const
  }

  return 'neutral' as const
}

function getStatusLabel(status: string) {
  if (status === 'APPROVED') {
    return 'Zatwierdzone'
  }

  if (status === 'PENDING') {
    return 'Oczekuje'
  }

  return status
}

function ApprovalsPage() {
  const [selectedCode, setSelectedCode] = useState(
    demoApprovals.find((approval) => approval.status === 'PENDING')?.code ??
      demoApprovals[0]?.code ??
      '',
  )

  const pendingCount = demoApprovals.filter(
    (approval) => approval.status === 'PENDING',
  ).length

  const approvedCount = demoApprovals.filter(
    (approval) => approval.status === 'APPROVED',
  ).length

  const selectedApproval = useMemo(
    () =>
      demoApprovals.find(
        (approval) => approval.code === selectedCode,
      ) ?? demoApprovals[0],
    [selectedCode],
  )

  const selectedMeta = selectedApproval
    ? approvalMeta[selectedApproval.code] ?? fallbackMeta
    : fallbackMeta

  return (
    <div className="ui-page-stack approvals-v2">
      <PageHeader
        eyebrow="Human-in-the-loop governance"
        title="Zatwierdzenia"
        description={
          'Krytyczne działania proponowane przez AI wymagają kontroli ' +
          'i decyzji człowieka przed wykonaniem.'
        }
        actions={
          <div className="approvals-v2__governance">
            <ShieldCheck size={18} />

            <div>
              <span>Action governance</span>
              <strong>Aktywne</strong>
            </div>
          </div>
        }
      />

      <section className="ui-kpi-grid">
        <KpiCard
          label="Wszystkie decyzje"
          value={demoApprovals.length}
          meta="Aktualna kolejka governance"
          icon={<FileCheck2 size={20} />}
        />

        <KpiCard
          label="Oczekujące"
          value={pendingCount}
          meta="Wymagają decyzji człowieka"
          icon={<Clock3 size={20} />}
        />

        <KpiCard
          label="Zatwierdzone"
          value={approvedCount}
          meta="Gotowe do governed execution"
          icon={<CheckCircle2 size={20} />}
        />

        <KpiCard
          label="Auto-execution"
          value="0"
          meta="Krytyczne akcje nie wykonują się automatycznie"
          icon={<ShieldCheck size={20} />}
        />
      </section>

      <section className="approvals-v2__workspace">
        <div className="approvals-v2__queue">
          <SectionHeader
            title="Kolejka decyzji"
            description="Wybierz pozycję, aby zobaczyć pełny kontekst"
            meta={`${demoApprovals.length} pozycje`}
          />

          <div className="ui-card approvals-v2__queue-list">
            {demoApprovals.map((approval) => {
              const meta =
                approvalMeta[approval.code] ?? fallbackMeta

              const isSelected =
                approval.code === selectedApproval?.code

              return (
                <button
                  className={[
                    'approvals-v2__queue-row',
                    isSelected
                      ? 'approvals-v2__queue-row--selected'
                      : '',
                  ]
                    .filter(Boolean)
                    .join(' ')}
                  key={approval.code}
                  onClick={() => setSelectedCode(approval.code)}
                  type="button"
                >
                  <div className="approvals-v2__queue-icon">
                    {approval.status === 'PENDING' ? (
                      <Clock3 size={19} />
                    ) : (
                      <CheckCircle2 size={19} />
                    )}
                  </div>

                  <div className="approvals-v2__queue-copy">
                    <div className="approvals-v2__queue-title">
                      <strong>{approval.title}</strong>

                      <StatusBadge
                        tone={getStatusTone(approval.status)}
                      >
                        {getStatusLabel(approval.status)}
                      </StatusBadge>
                    </div>

                    <span>
                      {approval.code} · {meta.area}
                    </span>

                    <small>{meta.createdAt}</small>
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        {selectedApproval ? (
          <aside className="ui-card approvals-v2__detail">
            <header className="approvals-v2__detail-header">
              <div>
                <span className="approvals-v2__overline">
                  Szczegóły decyzji
                </span>

                <h2>{selectedApproval.title}</h2>

                <span className="approvals-v2__code">
                  {selectedApproval.code}
                </span>
              </div>

              <StatusBadge
                tone={getStatusTone(selectedApproval.status)}
              >
                {getStatusLabel(selectedApproval.status)}
              </StatusBadge>
            </header>

            <div className="approvals-v2__detail-grid">
              <div>
                <span>Obszar</span>
                <strong>{selectedMeta.area}</strong>
              </div>

              <div>
                <span>Poziom ryzyka</span>
                <strong>{selectedMeta.risk}</strong>
              </div>

              <div>
                <span>Proponujący</span>
                <strong>{selectedMeta.owner}</strong>
              </div>

              <div>
                <span>Utworzono</span>
                <strong>{selectedMeta.createdAt}</strong>
              </div>
            </div>

            <section className="approvals-v2__detail-section">
              <div className="approvals-v2__section-icon approvals-v2__section-icon--warning">
                <TriangleAlert size={19} />
              </div>

              <div>
                <span>Uzasadnienie</span>

                <p>{selectedMeta.rationale}</p>
              </div>
            </section>

            <section className="approvals-v2__detail-section">
              <div className="approvals-v2__section-icon">
                <ShieldCheck size={19} />
              </div>

              <div>
                <span>Wpływ biznesowy</span>

                <p>{selectedMeta.impact}</p>
              </div>
            </section>

            <div className="approvals-v2__decision">
              <span className="approvals-v2__overline">
                Human decision
              </span>

              {selectedApproval.status === 'APPROVED' ? (
                <div className="approvals-v2__approved">
                  <UserRoundCheck size={22} />

                  <div>
                    <strong>
                      Działanie zatwierdzone
                    </strong>

                    <span>
                      {selectedMeta.reviewer ??
                        'Autoryzowany użytkownik'}
                    </span>
                  </div>
                </div>
              ) : (
                <div className="approvals-v2__pending">
                  <Clock3 size={22} />

                  <div>
                    <strong>
                      Oczekuje na decyzję
                    </strong>

                    <span>
                      Wykonanie pozostaje zablokowane do momentu
                      zatwierdzenia przez uprawnioną osobę.
                    </span>
                  </div>
                </div>
              )}
            </div>
          </aside>
        ) : null}
      </section>
    </div>
  )
}

export default ApprovalsPage