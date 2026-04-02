const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000/api'

function getToken() {
  return localStorage.getItem('auth_token')
}

async function request(path, options = {}) {
  const token = getToken()
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {})
    },
    ...options
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `Request failed: ${response.status}`)
  }

  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('application/json')) return response.json()
  return response.text()
}

export const api = {
  health: () => request('/health'),
  login: (payload) =>
    request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload)
    }),
  me: () => request('/auth/me'),
  getSchedules: () => request('/schedules'),
  getWorkflows: () => request('/workflows'),
  getMessages: () => request('/messages'),
  getEvents: () => request('/events'),
  getReminders: () => request('/reminders'),
  createSchedule: (payload) =>
    request('/schedules/create', {
      method: 'POST',
      body: JSON.stringify(payload)
    }),
  cancelSchedule: (scheduleId) =>
    request(`/schedules/${scheduleId}/cancel`, {
      method: 'POST'
    }),
}
