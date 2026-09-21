import {
  AlertTriangle,
  Boxes,
  CheckCircle2,
  FileText,
  PackageSearch,
  ShoppingCart,
  Sparkles,
  TrendingUp,
} from 'lucide-react'

import DataTable, {
  type DataTableColumn,
} from '../components/ui/DataTable'
import KpiCard from '../components/ui/KpiCard'
import PageHeader from '../components/ui/PageHeader'
import SectionHeader from '../components/ui/SectionHeader'
import StatusBadge from '../components/ui/StatusBadge'
import {
  demoApprovals,
  demoKnowledgeDocuments,
  demoSales,
  mainRisk,
} from '../data/demoData'

import './BriefingPage.css'

const formatPln = (value: number) =>
  new Intl.NumberFormat('pl-PL').format(value)

type PriorityTone =
  | 'warning'
  | 'success'

const priorities: Array<{
  icon: typeof AlertTriangle
  title: string
  description: string
  status: string
  tone: PriorityTone
}> = [
  {
    icon: AlertTriangle,
    title: `Ryzyko terminu ${mainRisk.orderNumber}`,
    description:
      `Brakuje ${mainRisk.shortage} m² materiału ${mainRisk.materialCode}. ` +
      `Pierwsza partia ${mainRisk.firstDeliveryQuantity} m² ma dotrzeć ` +
      `${mainRisk.firstDelivery}, a wysyłka jest planowana na ` +
      `${mainRisk.shipmentDate}.`,
    status: 'Wysoki priorytet',
    tone: 'warning',
  },
  {
    icon: ShoppingCart,
    title: 'Dostawa od BuildCore',
    description:
      `${mainRisk.purchaseOrder}: ${mainRisk.firstDeliveryQuantity} m² ` +
      `${mainRisk.firstDelivery} oraz ${mainRisk.secondDeliveryQuantity} m² ` +
      `${mainRisk.secondDelivery}.`,
    status: 'Monitorować',
    tone: 'warning',
  },
  {
    icon: CheckCircle2,
    title: 'Decyzje operacyjne',
    description:
      `${demoApprovals.filter((item) => item.status === 'APPROVED').length} ` +
      'działania zatwierdzone, ' +
      `${demoApprovals.filter((item) => item.status === 'PENDING').length} ` +
      'oczekuje na decyzję.',
    status: 'Nadzór aktywny',
    tone: 'success',
  },
]

type KnowledgeDocument =
  (typeof demoKnowledgeDocuments)[number]

function BriefingPage() {
  const briefingDocuments = demoKnowledgeDocuments.filter(
    (document) =>
      ['TECH-12', 'PROD-W38', 'PUR-02', 'SUP-01'].includes(
        document.code,
      ),
  )

  const documentColumns: DataTableColumn<KnowledgeDocument>[] = [
    {
      key: 'document',
      header: 'Dokument',
      render: (document) => (
        <div className="briefing-v2__document">
          <div className="briefing-v2__document-icon">
            <FileText size={17} />
          </div>

          <div>
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
      key: 'version',
      header: 'Wersja',
      width: '130px',
      render: (document) => (
        <span>v{document.version}</span>
      ),
    },
    {
      key: 'category',
      header: 'Kategoria',
      width: '180px',
      render: (document) => (
        <span className="briefing-v2__category">
          {document.category}
        </span>
      ),
    },
  ]

  return (
    <div className="ui-page-stack briefing-v2">
      <PageHeader
        eyebrow="Executive intelligence"
        title="Briefing operacyjny"
        description={
          `Najważniejszy obraz sytuacji operacyjnej Nexalvora Industries. ` +
          `Aktualny priorytet to ${mainRisk.orderNumber} i dostępność ` +
          `${mainRisk.materialCode}.`
        }
      />

      <section className="briefing-v2__hero">
        <article className="ui-card briefing-v2__summary">
          <div className="briefing-v2__summary-icon">
            <Sparkles size={22} />
          </div>

          <div className="briefing-v2__summary-content">
            <span className="briefing-v2__overline">
              Podsumowanie AI
            </span>

            <h2>
              {mainRisk.orderNumber} może wymagać korekty
              harmonogramu
            </h2>

            <p>
              Na magazynie znajduje się {mainRisk.onHand} m²
              materiału {mainRisk.materialCode} przy wymaganych{' '}
              {mainRisk.required} m². Pierwsze{' '}
              {mainRisk.firstDeliveryQuantity} m² od{' '}
              {mainRisk.supplier} ma dotrzeć{' '}
              {mainRisk.firstDelivery}. Planowana wysyłka
              pozostaje na {mainRisk.shipmentDate}.
            </p>

            <div className="briefing-v2__sources">
              <span>ERP</span>
              <span>Gmail</span>
              <span>Knowledge Hub</span>
              <span>Calendar</span>
            </div>
          </div>
        </article>

        <aside className="ui-card briefing-v2__risk">
          <span className="briefing-v2__overline">
            Ogólny status
          </span>

          <strong>Wymaga uwagi</strong>

          <StatusBadge tone="warning">
            WYSOKIE RYZYKO
          </StatusBadge>

          <div className="briefing-v2__risk-divider" />

          <div className="briefing-v2__risk-line">
            <span>Dostępne</span>
            <strong>{mainRisk.onHand} m²</strong>
          </div>

          <div className="briefing-v2__risk-line">
            <span>Wymagane</span>
            <strong>{mainRisk.required} m²</strong>
          </div>

          <div className="briefing-v2__risk-line">
            <span>Niedobór</span>
            <strong>{mainRisk.shortage} m²</strong>
          </div>
        </aside>
      </section>

      <section className="ui-section-stack">
        <SectionHeader
          title="Co wymaga uwagi"
          description="Najważniejsze ryzyka i decyzje operacyjne"
          meta={`${priorities.length} pozycje`}
        />

        <div className="ui-alert-list">
          {priorities.map((priority) => {
            const Icon = priority.icon

            return (
              <article
                className="ui-alert-row"
                key={priority.title}
              >
                <div
                  className={[
                    'ui-alert-row__icon',
                    priority.tone === 'success'
                      ? 'ui-alert-row__icon--success'
                      : 'ui-alert-row__icon--warning',
                  ].join(' ')}
                >
                  <Icon size={19} />
                </div>

                <div>
                  <h3 className="ui-alert-row__title">
                    {priority.title}
                  </h3>

                  <p className="ui-alert-row__description">
                    {priority.description}
                  </p>
                </div>

                <StatusBadge tone={priority.tone}>
                  {priority.status}
                </StatusBadge>
              </article>
            )
          })}
        </div>
      </section>

      <section className="ui-section-stack">
        <SectionHeader
          title="Obszary biznesowe"
          description="Najważniejsze wskaźniki operacyjne"
        />

        <div className="ui-kpi-grid">
          <KpiCard
            label="Sprzedaż"
            value={`${formatPln(demoSales.openPipelinePln)} PLN`}
            meta="Aktywny pipeline bez wygranych szans"
            icon={<TrendingUp size={20} />}
          />

          <KpiCard
            label="Produkcja"
            value={mainRisk.orderNumber}
            meta="24 moduły NX-Mod Technical · status AT RISK"
            icon={<Boxes size={20} />}
          />

          <KpiCard
            label="Zakupy"
            value={mainRisk.purchaseOrder}
            meta={`${mainRisk.shortage} m² bieżącego niedoboru MAT-204`}
            icon={<PackageSearch size={20} />}
          />

          <KpiCard
            label="Wygrane"
            value={`${formatPln(demoSales.wonValuePln)} PLN`}
            meta="OPP-2026-041 przekształcone w ORD-1048"
            icon={<ShoppingCart size={20} />}
          />
        </div>
      </section>

      <section className="ui-section-stack">
        <SectionHeader
          title="Dokumenty wykorzystane w briefingu"
          description="Evidence wykorzystane do przygotowania podsumowania AI"
          meta={`${briefingDocuments.length} dokumenty`}
        />

        <DataTable
          columns={documentColumns}
          rows={briefingDocuments}
          getRowKey={(document) => document.code}
        />
      </section>
    </div>
  )
}

export default BriefingPage