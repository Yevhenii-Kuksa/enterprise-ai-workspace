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

import './ErpPage.css'

const orders = [
  {
    orderId: 'ORD-1048',
    customer: 'Baltic Retail Group',
    lifecycle: 'IN_PROGRESS',
    delayState: 'AT_RISK',
    value: '186 400 PLN',
    dueDate: '23 września 2026',
    availability: 'Częściowy brak',
    availabilityTone: 'warning',
  },
  {
    orderId: 'ORD-1047',
    customer: 'Nordline Systems',
    lifecycle: 'IN_PROGRESS',
    delayState: 'ON_TIME',
    value: '142 800 PLN',
    dueDate: '24 września 2026',
    availability: 'Dostępne',
    availabilityTone: 'success',
  },
  {
    orderId: 'ORD-1046',
    customer: 'Vistula Components',
    lifecycle: 'READY',
    delayState: 'ON_TIME',
    value: '98 250 PLN',
    dueDate: '22 września 2026',
    availability: 'Dostępne',
    availabilityTone: 'success',
  },
  {
    orderId: 'ORD-1045',
    customer: 'Asteron Distribution',
    lifecycle: 'IN_PROGRESS',
    delayState: 'DELAYED',
    value: '221 900 PLN',
    dueDate: '18 września 2026',
    availability: 'Brak CMP-118',
    availabilityTone: 'error',
  },
  {
    orderId: 'ORD-1044',
    customer: 'Polaris Industrial',
    lifecycle: 'DRAFT',
    delayState: 'ON_TIME',
    value: '74 600 PLN',
    dueDate: '30 września 2026',
    availability: 'Rezerwacja',
    availabilityTone: 'neutral',
  },
]

const stockAlerts = [
  {
    code: 'CMP-204',
    name: 'Moduł sterujący',
    current: '18 szt.',
    minimum: '40 szt.',
    status: 'Niski stan',
    tone: 'warning',
  },
  {
    code: 'CMP-118',
    name: 'Zespół zasilający',
    current: '0 szt.',
    minimum: '12 szt.',
    status: 'Brak',
    tone: 'error',
  },
  {
    code: 'CMP-331',
    name: 'Obudowa przemysłowa',
    current: '54 szt.',
    minimum: '50 szt.',
    status: 'Monitoruj',
    tone: 'neutral',
  },
]

function ErpPage() {
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
            <strong>24</strong>
            <small>7 w realizacji dzisiaj</small>
          </div>
        </article>

        <article className="erp-stat-card">
          <div className="erp-stat-icon warning">
            <AlertTriangle size={19} />
          </div>

          <div>
            <span>Ryzyko opóźnienia</span>
            <strong>4</strong>
            <small>1 zamówienie opóźnione</small>
          </div>
        </article>

        <article className="erp-stat-card">
          <div className="erp-stat-icon">
            <CircleDollarSign size={19} />
          </div>

          <div>
            <span>Wartość aktywnych</span>
            <strong>1,28 mln PLN</strong>
            <small>+8,4% tydzień do tygodnia</small>
          </div>
        </article>

        <article className="erp-stat-card">
          <div className="erp-stat-icon">
            <Truck size={19} />
          </div>

          <div>
            <span>Dostawy dziś</span>
            <strong>6</strong>
            <small>5 potwierdzonych</small>
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
              key={order.orderId}
            >
              <strong className="erp-order-id">
                {order.orderId}
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
                <span>{order.dueDate}</span>
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
                <span>Połączenie z ERP działa prawidłowo</span>
              </div>
            </div>

            <div className="erp-sync-details">
              <div>
                <span>Ostatnia synchronizacja</span>
                <strong>10:46</strong>
              </div>

              <div>
                <span>Tryb</span>
                <strong>Read-only</strong>
              </div>

              <div>
                <span>Opóźnienie danych</span>
                <strong>&lt; 2 min</strong>
              </div>
            </div>

            <div className="erp-sync-footer">
              <Clock3 size={14} />
              Automatyczna synchronizacja aktywna
            </div>
          </div>
        </article>
      </section>
    </div>
  )
}

export default ErpPage