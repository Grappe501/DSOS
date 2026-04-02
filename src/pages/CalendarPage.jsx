import { useMemo } from 'react'
import PageHeader from '../components/PageHeader'
import DataState from '../components/DataState'
import { useAsync } from '../hooks/useAsync'
import { api } from '../lib/api'
import { addDays, formatDateTime, sameDay, startOfWeek } from '../lib/date'

export default function CalendarPage() {
  const { data, error, loading } = useAsync(() => api.getSchedules(), [])
  const weekStart = startOfWeek(new Date())
  const days = useMemo(() => Array.from({ length: 7 }, (_, i) => addDays(weekStart, i)), [weekStart])

  return (
    <div>
      <PageHeader
        title="Calendar"
        subtitle="Simple weekly operational view built on top of schedule records."
      />

      <DataState loading={loading} error={error} empty={!data?.length}>
        <div className="calendar-grid">
          {days.map((day) => {
            const items = (data || []).filter((row) => sameDay(row.start_time, day))
            return (
              <div className="card calendar-day" key={day.toISOString()}>
                <div className="calendar-date">
                  <strong>{day.toLocaleDateString(undefined, { weekday: 'long' })}</strong>
                  <span>{day.toLocaleDateString()}</span>
                </div>

                <div className="calendar-items">
                  {items.length ? items.map((item) => (
                    <div className="calendar-item" key={item.id}>
                      <div className="calendar-item-title">{item.title}</div>
                      <div className="calendar-item-sub">{item.assigned_to}</div>
                      <div className="calendar-item-time">{formatDateTime(item.start_time)}</div>
                    </div>
                  )) : <div className="calendar-empty">No schedules</div>}
                </div>
              </div>
            )
          })}
        </div>
      </DataState>
    </div>
  )
}
