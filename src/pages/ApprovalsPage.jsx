import { useEffect, useState } from 'react'
import { api } from '../lib/api'

export default function ApprovalsPage() {
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')

  const load = () => api.getPendingApprovals().then(setRows).catch((err) => setError(err.message || 'Failed to load approvals'))

  useEffect(() => {
    load()
  }, [])

  async function approve(id) {
    await api.approveSchedule(id)
    load()
  }

  async function reject(id) {
    const reason = window.prompt('Rejection reason') || ''
    if (!reason.trim()) return
    await api.rejectSchedule(id, { reason })
    load()
  }

  return (
    <section className="page-shell">
      <h2>Pending Approvals</h2>
      {error && <p className="error-text">{error}</p>}
      <div className="table-card">
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Department</th>
              <th>Status</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id}>
                <td>{row.title}</td>
                <td>{row.department || '—'}</td>
                <td>{row.status}</td>
                <td className="actions-cell">
                  <button onClick={() => approve(row.id)}>Approve</button>
                  <button onClick={() => reject(row.id)}>Reject</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
