import { useMemo, useState } from 'react'
import PageHeader from '../components/PageHeader'
import DataState from '../components/DataState'
import { useAsync } from '../hooks/useAsync'
import { api } from '../lib/api'
import { formatDateTime, toApiDateTime } from '../lib/date'
import { useAuth } from '../context/AuthContext'

const initialForm = {
  title: '',
  assigned_to: '',
  start_time: '',
  end_time: '',
  recurrence_rule: ''
}

export default function SchedulesPage() {
  const { user } = useAuth()
  const canWrite = ['owner', 'admin', 'scheduler'].includes(user?.role)
  const { data, error, loading, reload } = useAsync(() => api.getSchedules(), [])
  const [form, setForm] = useState(initialForm)
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')
  const [success, setSuccess] = useState('')

  const sorted = useMemo(() => {
    return [...(data || [])].sort((a, b) => String(b.start_time).localeCompare(String(a.start_time)))
  }, [data])

  async function onSubmit(e) {
    e.preventDefault()
    if (!canWrite) return

    setSubmitting(true)
    setSubmitError('')
    setSuccess('')

    try {
      const payload = {
        title: form.title,
        assigned_to: form.assigned_to,
        start_time: toApiDateTime(form.start_time),
        end_time: toApiDateTime(form.end_time),
        recurrence_rule: form.recurrence_rule || null
      }

      const result = await api.createSchedule(payload)
      setSuccess(`Created schedule ${result.schedule_id}`)
      setForm(initialForm)
      await reload()
    } catch (err) {
      setSubmitError(String(err.message || err))
    } finally {
      setSubmitting(false)
    }
  }

  async function onCancel(id) {
    if (!canWrite) return
    await api.cancelSchedule(id)
    await reload()
  }

  return (
    <div>
      <PageHeader
        title="Schedules"
        subtitle="Create and manage schedules with role-aware controls."
      />

      <div className="grid-two">
        <form className="card form-card" onSubmit={onSubmit}>
          <h3>Create Schedule</h3>

          {!canWrite ? (
            <div className="info-text">Your role is read-only for schedule actions.</div>
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

          <button type="submit" disabled={submitting || !canWrite} className="primary-button">
            {submitting ? 'Creating…' : 'Create Schedule'}
          </button>

          {submitError ? <div className="error-text">{submitError}</div> : null}
          {success ? <div className="success-text">{success}</div> : null}
        </form>

        <div className="card">
          <h3>Schedule Feed</h3>
          <DataState loading={loading} error={error} empty={!sorted.length}>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Assigned</th>
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