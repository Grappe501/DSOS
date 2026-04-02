import PageHeader from '../components/PageHeader'
import DataState from '../components/DataState'
import { useAsync } from '../hooks/useAsync'
import { api } from '../lib/api'

export default function EventsPage() {
  const { data, error, loading } = useAsync(() => api.getEvents(), [])

  return (
    <div>
      <PageHeader title="Events" subtitle="System event stream exposed as a readable page." />
      <DataState loading={loading} error={error} empty={!data?.length}>
        <div className="stack">
          {data.map((row) => (
            <div className="card" key={row.id}>
              <div className="event-top">
                <strong>{row.event_type}</strong>
                <span>{row.created_at}</span>
              </div>
              <pre className="code-block">{row.payload}</pre>
            </div>
          ))}
        </div>
      </DataState>
    </div>
  )
}
