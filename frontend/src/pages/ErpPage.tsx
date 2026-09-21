import {
  Boxes,
  Database,
  PackageSearch,
  ShieldCheck,
  ShoppingCart,
  TriangleAlert,
} from 'lucide-react'

import DataTable, {
  type DataTableColumn,
} from '../components/ui/DataTable'
import KpiCard from '../components/ui/KpiCard'
import PageHeader from '../components/ui/PageHeader'
import SectionHeader from '../components/ui/SectionHeader'
import StatusBadge from '../components/ui/StatusBadge'
import { mainRisk } from '../data/demoData'

import './ErpPage.css'

type OrderLifecycle =
  | 'DRAFT'
  | 'IN_PROGRESS'
  | 'READY'

type DelayState =
  | 'ON_TIME'
  | 'AT_RISK'
  | 'DELAYED'

type OrderRecord = {
  orderNumber: string
  customer: string
  product: string
  lifecycle: OrderLifecycle
  delayState: DelayState
  shipmentDate: string | null
}

const orders: OrderRecord[] = [
  {
    orderNumber: 'ORD-1048',
    customer: 'Baltic Construction Group',
    product: '24 × NX-Mod Technical',
    lifecycle: 'IN_PROGRESS',
    delayState: 'AT_RISK',
    shipmentDate: '23.09.2026',
  },
  {
    orderNumber: 'ORD-1047',
    customer: 'NordBuild Development',
    product: 'NX-Mod Office',
    lifecycle: 'IN_PROGRESS',
    delayState: 'ON_TIME',
    shipmentDate: '28.09.2026',
  },
  {
    orderNumber: 'ORD-1046',
    customer: 'Mazovia Logistics Parks',
    product: 'NX-Wall Pro',
    lifecycle: 'READY',
    delayState: 'ON_TIME',
    shipmentDate: '20.09.2026',
  },
  {
    orderNumber: 'ORD-1045',
    customer: 'Vistula Property Group',
    product: 'NX-Facade',
    lifecycle: 'IN_PROGRESS',
    delayState: 'DELAYED',
    shipmentDate: '18.09.2026',
  },
  {
    orderNumber: 'ORD-1044',
    customer: 'Polaris Industrial Development',
    product: 'NX-Mod Technical',
    lifecycle: 'DRAFT',
    delayState: 'ON_TIME',
    shipmentDate: null,
  },
]

function getLifecycleTone(
  lifecycle: OrderLifecycle,
) {
  if (lifecycle === 'READY') {
    return 'success' as const
  }

  if (lifecycle === 'IN_PROGRESS') {
    return 'info' as const
  }

  return 'neutral' as const
}

function getDelayTone(
  delayState: DelayState,
) {
  if (delayState === 'DELAYED') {
    return 'danger' as const
  }

  if (delayState === 'AT_RISK') {
    return 'warning' as const
  }

  return 'success' as const
}

function ErpPage() {
  const delayedOrders = orders.filter(
    (order) => order.delayState === 'DELAYED',
  ).length

  const atRiskOrders = orders.filter(
    (order) => order.delayState === 'AT_RISK',
  ).length

  const orderColumns: DataTableColumn<OrderRecord>[] = [
    {
      key: 'order',
      header: 'Zamówienie',
      render: (order) => (
        <div className="erp-v2__order-cell">
          <div className="erp-v2__order-icon">
            <Boxes size={18} />
          </div>

          <div>
            <span className="ui-table__primary">
              {order.orderNumber}
            </span>

            <span className="ui-table__secondary">
              {order.customer}
            </span>
          </div>
        </div>
      ),
    },
    {
      key: 'product',
      header: 'Produkt',
      width: '250px',
      render: (order) => order.product,
    },
    {
      key: 'lifecycle',
      header: 'Lifecycle',
      width: '170px',
      render: (order) => (
        <StatusBadge
          tone={getLifecycleTone(order.lifecycle)}
        >
          {order.lifecycle}
        </StatusBadge>
      ),
    },
    {
      key: 'delay',
      header: 'Delay state',
      width: '160px',
      render: (order) => (
        <StatusBadge
          tone={getDelayTone(order.delayState)}
        >
          {order.delayState}
        </StatusBadge>
      ),
    },
    {
      key: 'shipment',
      header: 'Wysyłka',
      width: '150px',
      render: (order) =>
        order.shipmentDate ?? 'Nie ustalono',
    },
  ]

  return (
    <div className="ui-page-stack erp-v2">
      <PageHeader
        eyebrow="ERP intelligence"
        title="ERP"
        description={
          'Operacyjny podgląd zamówień, stanów materiałowych i dostaw. ' +
          'Integracja ERP działa w trybie tylko do odczytu.'
        }
        actions={
          <div className="erp-v2__readonly">
            <ShieldCheck size={18} />

            <div>
              <span>Tryb integracji</span>
              <strong>Read-only</strong>
            </div>
          </div>
        }
      />

      <section className="ui-kpi-grid">
        <KpiCard
          label="Zamówienia"
          value={orders.length}
          meta="Aktywne rekordy w scenariuszu demo"
          icon={<Database size={20} />}
        />

        <KpiCard
          label="AT RISK"
          value={atRiskOrders}
          meta={`${mainRisk.orderNumber} wymaga monitorowania`}
          icon={<TriangleAlert size={20} />}
        />

        <KpiCard
          label="Opóźnione"
          value={delayedOrders}
          meta="Zamówienia z delay_state DELAYED"
          icon={<Boxes size={20} />}
        />

        <KpiCard
          label={`Niedobór ${mainRisk.materialCode}`}
          value={`${mainRisk.shortage} m²`}
          meta={`${mainRisk.onHand} m² dostępne przy ${mainRisk.required} m² wymaganych`}
          icon={<PackageSearch size={20} />}
        />
      </section>

      <section className="ui-section-stack">
        <SectionHeader
          title="Zamówienia"
          description={
            'Lifecycle oraz delay state są prezentowane jako dwa niezależne stany.'
          }
          meta={`${orders.length} zamówień`}
        />

        <DataTable
          columns={orderColumns}
          rows={orders}
          getRowKey={(order) => order.orderNumber}
        />
      </section>

      <section className="erp-v2__operations-grid">
        <article className="ui-card erp-v2__material">
          <header className="erp-v2__card-header">
            <div>
              <span className="erp-v2__overline">
                Inventory exception
              </span>

              <h2>
                {mainRisk.materialCode}
              </h2>

              <p>
                Structural Insulated Panel 120 mm
              </p>
            </div>

            <StatusBadge tone="warning">
              Niedobór
            </StatusBadge>
          </header>

          <div className="erp-v2__material-metrics">
            <div>
              <span>Na magazynie</span>
              <strong>{mainRisk.onHand} m²</strong>
            </div>

            <div>
              <span>Zapotrzebowanie</span>
              <strong>{mainRisk.required} m²</strong>
            </div>

            <div>
              <span>Niedobór</span>
              <strong>{mainRisk.shortage} m²</strong>
            </div>

            <div>
              <span>Powiązane zamówienie</span>
              <strong>{mainRisk.orderNumber}</strong>
            </div>
          </div>

          <div className="erp-v2__risk-note">
            <TriangleAlert size={20} />

            <div>
              <strong>
                Dostępność materiału wpływa na termin ORD-1048
              </strong>

              <p>
                Pierwsza dostawa pokrywa bieżący niedobór,
                ale pozostawia ograniczony bufor przed planowaną
                wysyłką {mainRisk.shipmentDate}.
              </p>
            </div>
          </div>
        </article>

        <article className="ui-card erp-v2__purchase-order">
          <header className="erp-v2__card-header">
            <div>
              <span className="erp-v2__overline">
                Purchase order
              </span>

              <h2>{mainRisk.purchaseOrder}</h2>

              <p>{mainRisk.supplier}</p>
            </div>

            <StatusBadge tone="warning">
              Dostawa opóźniona
            </StatusBadge>
          </header>

          <div className="erp-v2__po-summary">
            <div>
              <span>Materiał</span>
              <strong>{mainRisk.materialCode}</strong>
            </div>

            <div>
              <span>Łącznie</span>
              <strong>
                {mainRisk.firstDeliveryQuantity +
                  mainRisk.secondDeliveryQuantity}{' '}
                m²
              </strong>
            </div>
          </div>

          <div className="erp-v2__delivery-list">
            <div className="erp-v2__delivery-row">
              <div className="erp-v2__delivery-icon">
                <ShoppingCart size={18} />
              </div>

              <div>
                <strong>
                  Pierwsza partia
                </strong>

                <span>
                  {mainRisk.firstDeliveryQuantity} m²
                </span>
              </div>

              <div className="erp-v2__delivery-date">
                <span>Plan</span>
                <strong>{mainRisk.firstDelivery}</strong>
              </div>
            </div>

            <div className="erp-v2__delivery-row">
              <div className="erp-v2__delivery-icon">
                <ShoppingCart size={18} />
              </div>

              <div>
                <strong>
                  Druga partia
                </strong>

                <span>
                  {mainRisk.secondDeliveryQuantity} m²
                </span>
              </div>

              <div className="erp-v2__delivery-date">
                <span>Plan</span>
                <strong>{mainRisk.secondDelivery}</strong>
              </div>
            </div>
          </div>

          <footer className="erp-v2__source-note">
            <Database size={18} />

            <div>
              <strong>Źródło systemowe</strong>
              <span>
                ERP · dane tylko do odczytu
              </span>
            </div>
          </footer>
        </article>
      </section>
    </div>
  )
}

export default ErpPage