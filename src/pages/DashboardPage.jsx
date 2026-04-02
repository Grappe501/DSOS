import PageHeader from '../components/PageHeader'
import StatCard from '../components/StatCard'
import DataState from '../components/DataState'
import { useAsync } from '../hooks/useAsync'
import { api } from '../lib/api'

export default function DashboardPage() {
  const schedules = useAsync(() => api.getSchedules(), [])
  const workflows = useAsync(() => api.getWorkflows(), [])
  const messages = useAsync(() => api.getMessages(), [])
  const events = useAsync(() => api.getEvents(), [])

  const counts = {
    schedules: schedules.data?.length ?? 0,
    workflows: workflows.data?.length ?? 0,
    messages: messages.data?.length ?? 0,
    events: events.data?.length ?? 0,
  }

  return (
    <div>
      <PageHeader
        title="Dashboard"
        subtitle="This is the first visible layer on top of your FastAPI runtime. The backend stays JSON-first. The frontend turns it into an application."
      />

      <div className="stats-grid">
        <StatCard label="Schedules" value={counts.schedules} hint="Calendar records in system" />
        <StatCard label="Workflows" value={counts.workflows} hint="Tracked state machines" />
        <StatCard label="Messages" value={counts.messages} hint="Queued and processed messages" />
        <StatCard label="Events" value={counts.events} hint="System event log" />
      </div>

      <DataState
        loading={schedules.loading || workflows.loading || messages.loading || events.loading}
        error={schedules.error || workflows.error || messages.error || events.error}
      >
        <div className="grid-two">
          <div className="card">
            <h3>What exists now</h3>
            <ul className="plain-list">
              <li>FastAPI runtime</li>
              <li>Schedules API</li>
              <li>Workflow state API</li>
              <li>Message queue API</li>
              <li>Event log API</li>
            </ul>
          </div>
          <div className="card">
            <h3>What this frontend adds</h3>
            <ul className="plain-list">
              <li>Navigation shell</li>
              <li>Readable pages</li>
              <li>Forms for schedule creation</li>
              <li>Human-friendly tables</li>
              <li>Separation of API and UI</li>
            </ul>
          </div>
        </div>
      </DataState>
    </div>
  )
}
