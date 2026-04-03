import { NavLink, Route, Routes } from 'react-router-dom'
import DashboardPage from './pages/DashboardPage'
import SchedulesPage from './pages/SchedulesPage'
import CalendarPage from './pages/CalendarPage'
import WorkflowsPage from './pages/WorkflowsPage'
import MessagesPage from './pages/MessagesPage'
import EventsPage from './pages/EventsPage'
import AuditPage from './pages/AuditPage'
import LoginPage from './pages/LoginPage'
import ProtectedRoute from './components/ProtectedRoute'
import { useAuth } from './context/AuthContext'

function AppShell() {
  const { user, logout } = useAuth()
  const canSeeOperationalControls = user?.role === 'owner' || user?.role === 'admin'

  const navItems = [
    { to: '/', label: 'Dashboard' },
    { to: '/schedules', label: 'Schedules' },
    { to: '/calendar', label: 'Calendar' },
    { to: '/workflows', label: 'Workflows' },
    { to: '/events', label: 'Events' },
    ...(canSeeOperationalControls ? [
      { to: '/messages', label: 'Messages' },
      { to: '/audit', label: 'Audit' },
    ] : []),
  ]

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand brand-allcare">
          <div className="brand-logo-pill">Rx</div>
          <div>
            <div className="brand-title">AllCare Pharmacy</div>
            <div className="brand-subtitle">{user?.role || 'user'} · {user?.department || 'unscoped'}</div>
          </div>
        </div>

        <nav className="nav">
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.to === '/'}>{item.label}</NavLink>
          ))}
        </nav>

        <div className="account-panel">
          <div>{user?.email}</div>
          <div>{user?.full_name || 'AllCare user'}</div>
          <button onClick={logout} className="signout-button">Sign out</button>
        </div>
      </aside>

      <main className="content">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/schedules" element={<SchedulesPage />} />
          <Route path="/calendar" element={<CalendarPage />} />
          <Route path="/workflows" element={<WorkflowsPage />} />
          <Route path="/messages" element={<MessagesPage />} />
          <Route path="/events" element={<EventsPage />} />
          <Route path="/audit" element={<AuditPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}
