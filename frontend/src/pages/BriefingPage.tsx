import {
  AlertTriangle,
  ArrowUpRight,
  Boxes,
  CheckCircle2,
  FileText,
  PackageSearch,
  ShoppingCart,
  Sparkles,
  TrendingUp,
} from 'lucide-react'

import {
  demoApprovals,
  demoKnowledgeDocuments,
  demoSales,
  mainRisk,
} from '../data/demoData'

import './BriefingPage.css'

const formatPln = (value: number) =>
  new Intl.NumberFormat('pl-PL').format(value)

const priorities = [
  {
    icon: AlertTriangle,
    title: `Ryzyko terminu ${mainRisk.orderNumber}`,
    description: (
      `Brakuje ${mainRisk.shortage} m² materiału ${mainRisk.materialCode}. ` +
      `Pierwsza partia ${mainRisk.firstDeliveryQuantity} m² ma dotrzeć ` +
      `${mainRisk.firstDelivery}, a wysyłka jest planowana na ` +
      `${mainRisk.shipmentDate}.`
    ),
    status: 'Wysoki priorytet',
    tone: 'warning',
  },
  {
    icon: ShoppingCart,
    title: 'Dostawa od BuildCore',
    description: (
      `${mainRisk.purchaseOrder}: ${mainRisk.firstDeliveryQuantity} m² ` +
      `${mainRisk.firstDelivery} oraz ${mainRisk.secondDeliveryQuantity} m² ` +
      `${mainRisk.secondDelivery}.`
    ),
    status: 'Monitorować',
    tone: 'warning',
  },
  {
    icon: CheckCircle2,
    title: 'Decyzje operacyjne',
    description: (
      `${demoApprovals.filter((item) => item.status === 'APPROVED').length} ` +
      'działania zatwierdzone, ' +
      `${demoApprovals.filter((item) => item.status === 'PENDING').length} ` +
      'oczekuje na decyzję.'
    ),
    status: 'Governance aktywny',
    tone: 'success',
  },
]

const businessAreas = [
  {
    icon: TrendingUp,
    label: 'Sprzedaż',
    value: `${formatPln(demoSales.openPipelinePln)} PLN`,
    description: 'Aktywny pipeline bez wygranych szans.',
  },
  {
    icon: Boxes,
    label: 'Produkcja',
    value: mainRisk.orderNumber,
    description: '24 moduły NX-Mod Technical · status AT RISK.',
  },
  {
    icon: PackageSearch,
    label: 'Zakupy',
    value: mainRisk.purchaseOrder,
    description: `${mainRisk.shortage} m² bieżącego niedoboru MAT-204.`,
  },
  {
    icon: ShoppingCart,
    label: 'Wygrane',
    value: `${formatPln(demoSales.wonValuePln)} PLN`,
    description: 'OPP-2026-041 przekształcone w ORD-1048.',
  },
]

function BriefingPage() {
  const briefingDocuments = demoKnowledgeDocuments.filter((document) =>
    ['TECH-12', 'PROD-W38', 'PUR-02', 'SUP-01'].includes(document.code),
  )

  return (
    <div className="briefing-page">
      <section className="briefing-hero">
        <div className="briefing-hero-main">
          <div className="briefing-hero-icon">
            <Sparkles size={24} />
          </div>

          <div>
            <span className="section-kicker">
              Executive intelligence
            </span>

            <h2>Briefing operacyjny</h2>

            <p>
              Najważniejszym tematem jest dziś {mainRisk.orderNumber}.
              Dostępność {mainRisk.materialCode} pozostaje poniżej
              zapotrzebowania produkcyjnego, a opóźniona dostawa
              pozostawia ograniczony bufor przed wysyłką do klienta.
            </p>
          </div>
        </div>

        <div className="briefing-health">
          <span>Ogólny status</span>

          <strong>Wymaga uwagi</strong>

          <div className="briefing-health-status">
            <span className="status-dot warning" />
            HIGH RISK
          </div>
        </div>
      </section>

      <section className="briefing-summary-card">
        <div className="briefing-summary-icon">
          <Sparkles size={21} />
        </div>

        <div className="briefing-summary-content">
          <span className="section-kicker">
            Podsumowanie AI
          </span>

          <h3>
            {mainRisk.orderNumber} może wymagać korekty harmonogramu
          </h3>

          <p>
            Na magazynie znajduje się {mainRisk.onHand} m² materiału{' '}
            {mainRisk.materialCode} przy wymaganych {mainRisk.required} m².
            Pierwsze {mainRisk.firstDeliveryQuantity} m² od{' '}
            {mainRisk.supplier} ma dotrzeć {mainRisk.firstDelivery}.
            Planowana wysyłka zamówienia pozostaje na{' '}
            {mainRisk.shipmentDate}.
          </p>

          <div className="briefing-source-row">
            <span>ERP</span>
            <span>Gmail</span>
            <span>Knowledge Hub</span>
            <span>Calendar</span>
          </div>
        </div>
      </section>

      <section className="briefing-section">
        <div className="panel-header">
          <div>
            <span className="section-kicker">
              Priorytety
            </span>

            <h3>Co wymaga uwagi</h3>
          </div>

          <span className="briefing-section-count">
            {priorities.length} pozycje
          </span>
        </div>

        <div className="briefing-priority-grid">
          {priorities.map((priority) => {
            const Icon = priority.icon

            return (
              <article
                className="briefing-priority-card"
                key={priority.title}
              >
                <div className={`briefing-priority-icon ${priority.tone}`}>
                  <Icon size={19} />
                </div>

                <div>
                  <div className="briefing-priority-heading">
                    <strong>{priority.title}</strong>

                    <span className={`briefing-status ${priority.tone}`}>
                      {priority.status}
                    </span>
                  </div>

                  <p>{priority.description}</p>
                </div>
              </article>
            )
          })}
        </div>
      </section>

      <section className="briefing-section">
        <div className="panel-header">
          <div>
            <span className="section-kicker">
              Business overview
            </span>

            <h3>Obszary biznesowe</h3>
          </div>
        </div>

        <div className="briefing-business-grid">
          {businessAreas.map((area) => {
            const Icon = area.icon

            return (
              <article
                className="briefing-business-card"
                key={area.label}
              >
                <div className="briefing-business-top">
                  <div className="briefing-business-icon">
                    <Icon size={19} />
                  </div>

                  <ArrowUpRight size={17} />
                </div>

                <span>{area.label}</span>
                <strong>{area.value}</strong>
                <p>{area.description}</p>
              </article>
            )
          })}
        </div>
      </section>

      <section className="panel-card briefing-documents">
        <div className="panel-header">
          <div>
            <span className="section-kicker">
              Evidence
            </span>

            <h3>Dokumenty wykorzystane w briefingu</h3>
          </div>

          <FileText size={19} />
        </div>

        <div className="briefing-document-list">
          {briefingDocuments.map((document) => (
            <div
              className="briefing-document-row"
              key={document.code}
            >
              <div className="briefing-document-icon">
                <FileText size={17} />
              </div>

              <div>
                <strong>{document.title}</strong>
                <span>
                  {document.code} · v{document.version}
                </span>
              </div>

              <span className="briefing-document-category">
                {document.category}
              </span>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

export default BriefingPage