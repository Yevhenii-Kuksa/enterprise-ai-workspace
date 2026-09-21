import type { PropsWithChildren } from 'react'

import Sidebar from './Sidebar'
import Topbar from './Topbar'

type AppShellProps = PropsWithChildren<{
  title?: string
}>

function AppShell({
  children,
}: AppShellProps) {
  return (
    <div className="app-shell">
      <Sidebar />

      <div className="app-shell__main">
        <Topbar />

        <main className="app-shell__content">
          <div className="ui-page">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}

export default AppShell