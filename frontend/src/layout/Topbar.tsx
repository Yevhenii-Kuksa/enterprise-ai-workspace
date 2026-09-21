import {
  Bell,
  Search,
} from 'lucide-react'

function Topbar() {
  return (
    <header className="app-topbar">
      <label className="app-topbar__search">
        <Search
          size={18}
          strokeWidth={1.9}
        />

        <input
          type="search"
          placeholder="Szukaj w workspace, dokumentach, zamówieniach..."
          aria-label="Szukaj"
        />
      </label>

      <div className="app-topbar__actions">
        <button
          className="app-topbar__icon-button"
          type="button"
          aria-label="Powiadomienia"
        >
          <Bell
            size={19}
            strokeWidth={1.9}
          />

          <span className="app-topbar__notification-dot" />
        </button>

        <div className="app-topbar__profile">
          <div className="app-topbar__avatar">
            AK
          </div>

          <div className="app-topbar__profile-copy">
            <strong>Anna Kowalska</strong>
            <span>Nexalvora Industries</span>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Topbar