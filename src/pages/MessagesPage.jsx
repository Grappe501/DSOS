import PageHeader from '../components/PageHeader'
import DataState from '../components/DataState'
import { useAsync } from '../hooks/useAsync'
import { api } from '../lib/api'

export default function MessagesPage() {
  const { data, error, loading } = useAsync(() => api.getMessages(), [])

  return (
    <div>
      <PageHeader title="Messages" subtitle="Queued and processed messages from the runtime." />
      <DataState loading={loading} error={error} empty={!data?.length}>
        <div className="table-wrap card">
          <table>
            <thead>
              <tr>
                <th>Channel</th>
                <th>Recipient</th>
                <th>Content</th>
                <th>Status</th>
                <th>Retries</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row) => (
                <tr key={row.id}>
                  <td>{row.channel}</td>
                  <td>{row.recipient}</td>
                  <td>{row.content}</td>
                  <td>{row.status}</td>
                  <td>{row.retry_count}/{row.max_retries}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </DataState>
    </div>
  )
}
