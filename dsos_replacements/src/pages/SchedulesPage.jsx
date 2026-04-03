import { useEffect, useMemo, useState } from 'react'
import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import DataState from '../components/DataState'
import { api } from '../lib/api'
import { useAuth } from '../context/AuthContext'
import { formatDateTime } from '../lib/date'

const initialForm = {
  title: '',
  assigned_to: '',
  start_time: '',
  end_time: '',
  recurrence_rule: '',
  department: ''
}

export default function SchedulesPage() {
  const { user } = useAuth()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ ...initialForm, department: user?.department || '' })
  const [submitError, setSubmitError] = useState('')
  const [success, setSuccess] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [departmentFilter, setDepartmentFilter] = useState('')

  const canWrite = ['owner', 'admin', 'scheduler'].includes(user?.role)
  const canChooseDepartment = ['owner', 'admin'].includes(user?.role)

  async function load() {
    try {
      setLoading(true)
      setError('')
      const data = await api.getSchedules(canChooseDepartment ? { department: departmentFilter } : {})
      setItems(data)
    } catch (err) {
      setError(String(err.message || err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [user?.role, departmentFilter])

  useEffect(() => {
    setForm((current) => ({
      ...current,
      department: canChooseDepartment ? current.department : (user?.department || '')
    }))
  }, [canChooseDepartment, user?.department])

  const sorted = useMemo(() => {
    return [...items].sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
  }, [items])

  async function onSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    setSubmitError('')
    setSuccess('')

    try {
      await api.createSchedule({
        ...form,
        recurrence_rule: form.recurrence_rule || null,
        department: canChooseDepartment ? (form.department || null) : null
      })
      setForm({ ...initialForm, department: canChooseDepartment ? form.department : (user?.department || '') })
      setSuccess('Schedule created successfully.')
      await load()
    } catch (err) {
      setSubmitError(String(err.message || err))
    } finally {
      setSubmitting(false)
    }
  }

  async function onCancel(scheduleId) {
    try {
      await api.cancelSchedule(scheduleId)
      await load()
    } catch (err) {
      setError(String(err.message || err))
    }
  }

  const totals = {
    total: items.length,
    scheduled: items.filter((item) => item.status === 'scheduled').length,
    conflicts: items.filter((item) => item.status === 'conflict').length,
    cancelled: items.filter((item) => item.status === 'cancelled').length,
  }

  return (
    <div>
      <PageHeader
        title="Schedules"
        subtitle="Create and monitor schedule records with department-aware visibility and preserved role controls."
      />

      <div className="stats-grid">
        <StatCard label="Visible schedules" value={totals.total} hint="Based on your role and department scope" />
        <StatCard label="Scheduled" value={totals.scheduled} hint="Ready to execute" />
        <StatCard label="Conflicts" value={totals.conflicts} hint="Needs resolution" />
        <StatCard label="Cancelled" value={totals.cancelled} hint="Historical records" />
      </div>

      <div className="grid-two">
        <form className="card form-card" onSubmit={onSubmit}>
          <h3>Create Schedule</h3>
          {!canWrite ? (
            <div className="info-text">Your role is read-only. You can review schedules but cannot create or cancel them.</div>
          ) : null}

          <label>
            Title
            <input
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              disabled={!canWrite}
              required
            />
          </label>

          <label>
            Assigned To
            <input
              value={form.assigned_to}
              onChange={(e) => setForm({ ...form, assigned_to: e.target.value })}
              disabled={!canWrite}
              required
            />
          </label>

          <label>
            Start Time
            <input
              type="datetime-local"
              value={form.start_time}
              onChange={(e) => setForm({ ...form, start_time: e.target.value })}
              disabled={!canWrite}
              required
            />
          </label>

          <label>
            End Time
            <input
              type="datetime-local"
              value={form.end_time}
              onChange={(e) => setForm({ ...form, end_time: e.target.value })}
              disabled={!canWrite}
              required
            />
          </label>

          <label>
            Recurrence Rule
            <select
              value={form.recurrence_rule}
              onChange={(e) => setForm({ ...form, recurrence_rule: e.target.value })}
              disabled={!canWrite}
            >
              <option value="">None</option>
              <option value="daily">Daily</option>
            </select>
          </label>

          <label>
            Department
            <input
              value={canChooseDepartment ? form.department : (user?.department || 'unscoped')}
              onChange={(e) => setForm({ ...form, department: e.target.value })}
              disabled={!canWrite || !canChooseDepartment}
              placeholder={canChooseDepartment ? 'e.g. operations' : 'Your department scope'}
            />
          </label>

          <button type="submit" disabled={submitting || !canWrite} className="primary-button">
            {submitting ? 'Creating…' : 'Create Schedule'}
          </button>

          {submitError ? <div className="error-text">{submitError}</div> : null}
          {success ? <div className="success-text">{success}</div> : null}
        </form>

        <div className="card">
          <div className="row-between wrap-gap">
            <div>
              <h3>Schedule Feed</h3>
              <div className="muted-small">Role: {user?.role || 'unknown'} · Department: {user?.department || 'unscoped'}</div>
            </div>
            {canChooseDepartment ? (
              <label className="inline-filter">
                Department Filter
                <input
                  value={departmentFilter}
                  onChange={(e) => setDepartmentFilter(e.target.value)}
                  placeholder="all departments"
                />
              </label>
            ) : null}
          </div>

          <DataState loading={loading} error={error} empty={!sorted.length}>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Assigned</th>
                    <th>Department</th>
                    <th>Start</th>
                    <th>End</th>
                    <th>Status</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {sorted.map((item) => (
                    <tr key={item.id}>
                      <td>{item.title}</td>
                      <td>{item.assigned_to}</td>
                      <td>{item.department || 'unscoped'}</td>
                      <td>{formatDateTime(item.start_time)}</td>
                      <td>{formatDateTime(item.end_time)}</td>
                      <td><span className={`pill ${item.status}`}>{item.status}</span></td>
                      <td>
                        {canWrite ? (
                          <button className="secondary-button" type="button" onClick={() => onCancel(item.id)}>
                            Cancel
                          </button>
                        ) : null}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </DataState>
        </div>
      </div>
    </div>
  )
}
