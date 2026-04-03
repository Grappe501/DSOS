import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import DataState from '../components/DataState'
import { useAsync } from '../hooks/useAsync'
import { api } from '../lib/api'
import { useAuth } from '../context/AuthContext'

export default function DashboardPage() {
  const { user } = useAuth()
  const { data, error, loading } = useAsync(() => api.getOperationalSummary(), [user?.role, user?.department])
  const canSeeOperationalControls = user?.role === 'owner' || user?.role === 'admin'
  const departmentBreakdown = Object.entries(data?.department_breakdown || {})

  return (
    <div>
      <PageHeader
        title="Dashboard"
        subtitle="Operational visibility now respects role and department scoping while preserving the existing scheduling slice."
      />

      <div className={`stats-grid ${canSeeOperationalControls ? 'stats-grid-five' : ''}`}>
        <StatCard label="Schedules" value={data?.schedules_total ?? 0} hint="Visible under your current scope" />
        <StatCard label="Scheduled" value={data?.scheduled_count ?? 0} hint="Active scheduled items" />
        <StatCard label="Conflicts" value={data?.conflict_count ?? 0} hint="Items needing review" />
        <StatCard label="Cancelled" value={data?.cancelled_count ?? 0} hint="Historical cancellations" />
        {canSeeOperationalControls ? (
          <StatCard label="Audit Rows" value={data?.audit_count ?? 0} hint="Owner/admin operational audit trail" />
        ) : null}
      </div>

      <DataState loading={loading} error={error}>
        <div className="grid-two">
          <div className="card">
            <h3>Current operator scope</h3>
            <div className="stack">
              <div><strong>Role:</strong> {data?.role || user?.role || 'unknown'}</div>
              <div><strong>Department:</strong> {data?.department || user?.department || 'unscoped'}</div>
              <div><strong>Workflows:</strong> {data?.workflow_count ?? 0}</div>
              <div><strong>Events:</strong> {data?.event_count ?? 0}</div>
              {canSeeOperationalControls ? <div><strong>Messages:</strong> {data?.message_count ?? 0}</div> : null}
            </div>
          </div>
          <div className="card">
            <h3>Department schedule footprint</h3>
            {departmentBreakdown.length ? (
              <div className="stack">
                {departmentBreakdown.map(([department, count]) => (
                  <div key={department} className="row-between subtle-row">
                    <span>{department}</span>
                    <strong>{count}</strong>
                  </div>
                ))}
              </div>
            ) : (
              <div className="info-text">No schedule records are visible under the current scope.</div>
            )}
          </div>
        </div>
      </DataState>
    </div>
  )
}
