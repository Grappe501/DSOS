import { useMemo, useState } from 'react'
import PageHeader from '../components/PageHeader'
import DataState from '../components/DataState'
import StatCard from '../components/StatCard'
import { useAsync } from '../hooks/useAsync'
import { api } from '../lib/api'
import { useAuth } from '../context/AuthContext'
import { formatDateTime } from '../lib/date'

export default function AuditPage() {
  const { user } = useAuth()
  const [filters, setFilters] = useState({
    action: '',
    entity_type: '',
    actor_user_id: '',
    department: '',
    limit: '200',
  })

  const queryFilters = useMemo(() => ({
    ...filters,
    limit: Number(filters.limit || 200),
  }), [filters])

  const { data = [], error, loading } = useAsync(() => api.getAudit(queryFilters), [queryFilters.action, queryFilters.entity_type, queryFilters.actor_user_id, queryFilters.department, queryFilters.limit])

  const actionCounts = data.reduce((acc, row) => {
    acc[row.action] = (acc[row.action] || 0) + 1
    return acc
  }, {})

  const topActions = Object.entries(actionCounts).sort((a, b) => b[1] - a[1]).slice(0, 3)
  const actorCount = new Set(data.map((row) => row.actor_user_id).filter(Boolean)).size

  return (
    <div>
      <PageHeader
        title="Audit Trail"
        subtitle="Owner and admin operators can review who changed what, when, and under which department scope."
      />

      <div className="stats-grid">
        <StatCard label="Rows" value={data.length} hint="Current filtered audit feed" />
        <StatCard label="Actors" value={actorCount} hint="Distinct users captured in results" />
        <StatCard label="Top Action" value={topActions[0]?.[0] || '—'} hint={topActions[0] ? `${topActions[0][1]} rows` : 'No matching audit rows'} />
        <StatCard label="Department" value={filters.department || user?.department || 'all'} hint="Current department filter" />
      </div>

      <div className="card form-card audit-filter-card">
        <h3>Filters</h3>
        <div className="filter-grid">
          <label>
            Action
            <input value={filters.action} onChange={(e) => setFilters({ ...filters, action: e.target.value })} placeholder="schedule.created" />
          </label>
          <label>
            Entity Type
            <input value={filters.entity_type} onChange={(e) => setFilters({ ...filters, entity_type: e.target.value })} placeholder="schedule" />
          </label>
          <label>
            Actor User ID
            <input value={filters.actor_user_id} onChange={(e) => setFilters({ ...filters, actor_user_id: e.target.value })} placeholder="user id" />
          </label>
          <label>
            Department
            <input value={filters.department} onChange={(e) => setFilters({ ...filters, department: e.target.value })} placeholder="operations" />
          </label>
          <label>
            Limit
            <select value={filters.limit} onChange={(e) => setFilters({ ...filters, limit: e.target.value })}>
              <option value="50">50</option>
              <option value="100">100</option>
              <option value="200">200</option>
              <option value="500">500</option>
            </select>
          </label>
        </div>
      </div>

      <DataState loading={loading} error={error} empty={!data.length}>
        <div className="table-wrap card">
          <table>
            <thead>
              <tr>
                <th>When</th>
                <th>Action</th>
                <th>Entity</th>
                <th>Actor</th>
                <th>Department</th>
                <th>Metadata</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row) => (
                <tr key={row.id}>
                  <td>{formatDateTime(row.created_at)}</td>
                  <td>{row.action}</td>
                  <td>{row.entity_type}:{row.entity_id || '—'}</td>
                  <td>
                    <div>{row.actor_email || row.actor_user_id || 'system'}</div>
                    <div className="muted-small">{row.actor_role || 'n/a'}</div>
                  </td>
                  <td>{row.department || row.actor_department || 'unscoped'}</td>
                  <td>
                    <pre className="code-block compact-code">{JSON.stringify(row.metadata, null, 2)}</pre>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </DataState>
    </div>
  )
}
