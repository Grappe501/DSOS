import { useEffect, useState } from 'react'
import { api } from '../lib/api'

export default function DepartmentsPage() {
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    api.getDepartments().then(setRows).catch((err) => setError(err.message || 'Failed to load departments'))
  }, [])

  return (
    <section className="page-shell">
      <h2>Departments</h2>
      <p>Starter admin surface for department registry and membership management.</p>
      {error && <p className="error-text">{error}</p>}
      <div className="table-card">
        <table>
          <thead>
            <tr>
              <th>Code</th>
              <th>Name</th>
              <th>Active</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id}>
                <td>{row.code}</td>
                <td>{row.name}</td>
                <td>{row.is_active ? 'Yes' : 'No'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
