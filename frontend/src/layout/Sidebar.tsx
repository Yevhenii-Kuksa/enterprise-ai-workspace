import {
    Bot,
    CircleCheckBig,
    Database,
    FileText,
    LayoutDashboard,
    Library,
    PlayCircle,
    Plug,
    Settings,
    ShieldCheck,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'

const navigation = [
    {
        label: 'Panel główny',
        to: '/dashboard',
        icon: LayoutDashboard,
    },
    {
        label: 'Briefing',
        to: '/briefing',
        icon: FileText,
    },
    {
        label: 'Baza wiedzy',
        to: '/knowledge',
        icon: Library,
    },
    {
        label: 'Asystent AI',
        to: '/assistant',
        icon: Bot,
    },
    {
        label: 'Zatwierdzenia',
        to: '/approvals',
        icon: CircleCheckBig,
    },
    {
        label: 'Wykonania',
        to: '/executions',
        icon: PlayCircle,
    },
    {
        label: 'ERP',
        to: '/erp',
        icon: Database,
    },
    {
        label: 'Integracje',
        to: '/integrations',
        icon: Plug,
    },
    {
        label: 'Audyt',
        to: '/audit',
        icon: ShieldCheck,
    },
    {
        label: 'Ustawienia',
        to: '/settings',
        icon: Settings,
    },
]

function Sidebar() {
    return (
        <aside className="app-sidebar">
            <div className="app-sidebar__brand">
                <div className="app-sidebar__brand-mark">
                    N
                </div>

                <div className="app-sidebar__brand-copy">
                    <strong>Nexalvora</strong>
                    <span>Enterprise AI Workspace</span>
                </div>
            </div>

            <div className="app-sidebar__section-label">
                Środowisko
            </div>

            <nav
                className="app-sidebar__navigation"
                aria-label="Główna nawigacja"
            >
                {navigation.map((item) => {
                    const Icon = item.icon

                    return (
                        <NavLink
                            key={item.to}
                            to={item.to}
                            end={item.to === '/dashboard'}
                            className={({ isActive }) =>
                                [
                                    'app-sidebar__link',
                                    isActive
                                        ? 'app-sidebar__link--active'
                                        : '',
                                ]
                                    .filter(Boolean)
                                    .join(' ')
                            }
                        >
                            <Icon
                                className="app-sidebar__link-icon"
                                size={19}
                                strokeWidth={1.9}
                            />

                            <span>{item.label}</span>
                        </NavLink>
                    )
                })}
            </nav>

            <div className="app-sidebar__footer">
                <div className="app-sidebar__user">
                    <div className="app-sidebar__avatar">
                        AK
                    </div>

                    <div className="app-sidebar__user-copy">
                        <strong>Anna Kowalska</strong>
                        <span>Operations Director</span>
                    </div>
                </div>
            </div>
        </aside>
    )
}

export default Sidebar