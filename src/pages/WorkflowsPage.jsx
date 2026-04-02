import PageHeader from '../components/PageHeader'
import DataState from '../components/DataState'
import { useAsync } from '../hooks/useAsync'
import { api } from '../lib/api'

export default function WorkflowsPage() {
  const { data, error, loading } = useAsync(() => api.getWorkflows(), [])

  return (
    <div>
      <PageHeader title="Workflows" subtitle="Workflow states coming from the runtime." />
      <DataState loading={loading} error={error} empty={!data?.length}>
        <div className="table-wrap card">
          <table>
            <thead>
              <tr>
                <th>Workflow</th>
                <th>Entity Type</th>
                <th>Entity ID</th>
                <th>State</th>
                <th>Status</th>
                <th>Updated</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row) => (
                <tr key={row.id}>
                  <td>{row.workflow_name}</td>
                  <td>{row.entity_type}</td>
                  <td>{row.entity_id}</td>
                  <td>{row.state}</td>
                  <td>{row.status}</td>
                  <td>{row.updated_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </DataState>
    </div>
  )
}
