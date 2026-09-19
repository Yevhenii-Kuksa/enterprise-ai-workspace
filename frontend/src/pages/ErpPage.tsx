import {
  AlertTriangle,
  Boxes,
  CalendarDays,
  CheckCircle2,
  CircleDollarSign,
  Clock3,
  Database,
  PackageCheck,
  Search,
  Truck,
} from 'lucide-react'

import {
  demoOrders,
  demoSales,
  mainRisk,
} from '../data/demoData'

import './ErpPage.css'

const formatPln = (value: number) =>
  new Intl.NumberFormat('pl-PL').format(value)

const orderPresentation: Record<
  string,
  {
    value: string
    availability: string
    availabilityTone: string
  }
> = {
  'ORD-1048': {
    value: `${formatPln(686_400)} PLN`,
    availability: `Brak ${mainRisk.shortage} m² ${mainRisk.materialCode}`,
    availabilityTone: 'warning',
  },
  'ORD-1047': {
    value: `${formatPln(420_000)} PLN`,
    availability: 'Dostępne',
    availabilityTone: 'success',
  },
  'ORD-1046': {
    value: `${formatPln(315_000)} PLN`,
    availability: 'Dostępne',
    availabilityTone: 'success',
  },
  'ORD-1045': {
    value: `${formatPln(185_000)} PLN`,
    availability: 'Monitoruj dostępność',
    availabilityTone: 'error',
  },
  'ORD-1044': {
    value: '—',
    availability: 'Rezerwacja',
    availabilityTone: 'neutral',
  },
}

const orders = demoOrders.map((order) => ({
  ...order,
  ...orderPresentation[order.number],
}))

const stockAlerts = [
  {
    code: mainRisk.materialCode,
    name: mainRisk.materialName,
    current: `${mainRisk.onHand} m²`,
    minimum: `${mainRisk.safetyStock} m²`,
    status: `Niedobór ${mainRisk.shortage} m²`,
    tone: 'warning',
  },
  {
    code: 'MAT-118',
    name: 'Galvanized Steel Profile 120',
    current: '920 mb',
    minimum: '300 mb',
    status: 'Dostępne',
    tone: 'success',
  },
  {
    code: 'MAT-331',
    name: 'Fire-rated Gypsum Board',
    current: '640 m²',
    minimum: '200 m²',
    status: 'Dostępne',
    tone: 'success',
  },
]

function ErpPage() {
  const activeOrders = orders.filter(
    (order) => order.lifecycle !== 'DRAFT',
  )

  const atRiskOrders = orders.filter(
    (order) => order.delayState === 'AT_RISK',
  ).length

  const delayedOrders = orders.filter(
    (order) => order.delayState === 'DELAYED',
  ).length

  return (
    <div className="erp-page">
      <section className="erp-hero">
        <div className="erp-hero-main">
          <div className="erp-hero-icon">
            <Database size={23} />
          </div>

          <div>
            <span className="section-kicker">
              ERP intelligence
            </span>

            <h2>ERP</h2>

            <p>
              Podgląd zamówień, stanów magazynowych i danych
              operacyjnych z systemu ERP w trybie read-only.
            </p>
          </div>
        </div>

        <div className="erp-readonly">
          <PackageCheck size={18} />

          <div>
            <span>Tryb dostępu</span>
            <strong>Read-only</strong>
          </div>
        </div>
      </section>

      <section className="erp-stats">
        <article className="erp-stat-card">
          <div className="erp-stat-icon">
            <Boxes size={19} />
          </div>

          <div>
            <span>Aktywne zamówienia</span>
            <strong>{activeOrders.length}</strong>
            <small>
              {orders.length} zamówień w demo dataset
            </small>
          </div>
        </article>

        <article className="erp-stat-card">
          <div className="erp-stat-icon warning">
            <AlertTriangle size={19} />
          </div>

          <div>
            <span>Ryzyko opóźnienia</span>
            <strong>{atRiskOrders + delayedOrders}</strong>
            <small>
              {atRiskOrders} AT RISK · {delayedOrders} DELAYED
            </small>
          </div>
        </article>

        <article className="erp-stat-card">
          <div className="erp-stat-icon">
            <CircleDollarSign size={19} />
          </div>

          <div>
            <span>Wygrana wartość sprzedaży</span>
            <strong>
              {formatPln(demoSales.wonValuePln)} PLN
            </strong>
            <small>
              OPP-2026-041 → ORD-1048
            </small>
          </div>
        </article>

        <article className="erp-stat-card">
          <div className="erp-stat-icon">
            <Truck size={19} />
          </div>

          <div>
            <span>Dostawa krytyczna</span>
            <strong>
              {mainRisk.firstDeliveryQuantity} m²
            </strong>
            <small>
              {mainRisk.materialCode} · {mainRisk.firstDelivery}
            </small>
          </div>
        </article>
      </section>

      <section className="panel-card erp-orders-card">
        <div className="erp-toolbar">
          <div>
            <span className="section-kicker">
              Zamówienia
            </span>

            <h3>Aktywne zamówienia</h3>
          </div>

          <div className="erp-search">
            <Search size={17} />

            <input
              aria-label="Szukaj zamówienia"
              placeholder="Szukaj zamówienia..."
              type="text"
            />
          </div>
        </div>

        <div className="erp-table">
          <div className="erp-table-head">
            <span>Zamówienie</span>
            <span>Klient</span>
            <span>Status</span>
            <span>Ryzyko</span>
            <span>Wartość</span>
            <span>Termin</span>
            <span>Dostępność</span>
          </div>

          {orders.map((order) => (
            <div
              className="erp-table-row"
              key={order.number}
            >
              <strong className="erp-order-id">
                {order.number}
              </strong>

              <span className="erp-customer">
                {order.customer}
              </span>

              <span className="erp-lifecycle">
                {order.lifecycle}
              </span>

              <span
                className={`erp-delay-state ${order.delayState.toLowerCase()}`}
              >
                {order.delayState}
              </span>

              <strong className="erp-value">
                {order.value}
              </strong>

              <div className="erp-due-date">
                <CalendarDays size={14} />

                <span>
                  {order.deliveryDate ?? 'Nie ustalono'}
                </span>
              </div>

              <span
                className={`erp-availability ${order.availabilityTone}`}
              >
                {order.availability}
              </span>
            </div>
          ))}
        </div>
      </section>

      <section className="erp-bottom-grid">
        <article className="panel-card">
          <div className="panel-header">
            <div>
              <span className="section-kicker">
                Magazyn
              </span>

              <h3>Alerty stanów magazynowych</h3>
            </div>

            <AlertTriangle size={18} />
          </div>

          <div className="erp-stock-list">
            {stockAlerts.map((item) => (
              <div
                className="erp-stock-item"
                key={item.code}
              >
                <div className="erp-stock-main">
                  <span
                    className={`erp-stock-indicator ${item.tone}`}
                  />

                  <div>
                    <strong>
                      {item.code} · {item.name}
                    </strong>

                    <span>
                      Stan: {item.current} · Minimum: {item.minimum}
                    </span>
                  </div>
                </div>

                <span
                  className={`erp-stock-status ${item.tone}`}
                >
                  {item.status}
                </span>
              </div>
            ))}
          </div>
        </article>

        <article className="panel-card erp-sync-card">
          <div className="panel-header">
            <div>
              <span className="section-kicker">
                Synchronizacja
              </span>

              <h3>Status danych</h3>
            </div>

            <CheckCircle2 size={18} />
          </div>

          <div className="erp-sync-main">
            <div className="erp-sync-status">
              <CheckCircle2 size={21} />

              <div>
                <strong>Dane aktualne</strong>
                <span>
                  Połączenie z Nexalvora ERP działa prawidłowo
                </span>
              </div>
            </div>

            <div className="erp-sync-details">
              <div>
                <span>Ostatnia synchronizacja</span>
                <strong>12:00</strong>
              </div>

              <div>
                <span>Tryb</span>
                <strong>Read-only</strong>
              </div>

              <div>
                <span>Źródło</span>
                <strong>demo_erp</strong>
              </div>
            </div>

            <div className="erp-sync-footer">
              <Clock3 size={14} />
              Dane zsynchronizowane z canonical demo dataset
            </div>
          </div>
        </article>
      </section>
    </div>
  )
}

export default ErpPage