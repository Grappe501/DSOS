import { NavLink, Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./context/AuthContext";

import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import SchedulesPage from "./pages/SchedulesPage";
import CalendarPage from "./pages/CalendarPage";
import WorkflowsPage from "./pages/WorkflowsPage";
import MessagesPage from "./pages/MessagesPage";
import EventsPage from "./pages/EventsPage";
import AuditPage from "./pages/AuditPage";
import ApprovalsPage from "./pages/ApprovalsPage";
import DepartmentsPage from "./pages/DepartmentsPage";
import MalonePage from "./pages/MalonePage";

function ProtectedAppShell() {
  const { user, logout } = useAuth();

  const navItems = [
    { to: "/", label: "Dashboard" },
    { to: "/schedules", label: "Schedules" },
    { to: "/calendar", label: "Calendar" },
    { to: "/workflows", label: "Workflows" },
    { to: "/messages", label: "Messages" },
    { to: "/events", label: "Events" },
    { to: "/malone", label: "Malone" },
  ];

  if (user?.role === "owner" || user?.role === "admin") {
    navItems.push(
      { to: "/audit", label: "Audit" },
      { to: "/approvals", label: "Approvals" },
      { to: "/departments", label: "Departments" },
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-logo-pill">Rx</div>
          <div>
            <div className="brand-title">AllCare Pharmacy</div>
            <div className="brand-subtitle">{user?.role ?? "user"}</div>
          </div>
        </div>

        <nav className="nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) => (isActive ? "active" : "")}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="account-panel">
          <div>{user?.email ?? ""}</div>
          <button className="signout-button" type="button" onClick={logout}>
            Sign out
          </button>
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
          <Route path="/malone" element={<MalonePage />} />

          {(user?.role === "owner" || user?.role === "admin") && (
            <>
              <Route path="/audit" element={<AuditPage />} />
              <Route path="/approvals" element={<ApprovalsPage />} />
              <Route path="/departments" element={<DepartmentsPage />} />
            </>
          )}

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="login-screen">Loading...</div>;
  }

  if (!user) {
    return <LoginPage />;
  }

  return <ProtectedAppShell />;
}