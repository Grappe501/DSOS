export const api = {
  async getOperationalSummary() {
    const response = await fetch("/api/operational/summary");
    return response.json();
  },

  async listAudit(params = {}) {
    const query = new URLSearchParams(params).toString();
    const response = await fetch(`/api/audit${query ? `?${query}` : ""}`);
    return response.json();
  },

  async listDepartments() {
    const response = await fetch("/api/departments");
    return response.json();
  },

  async submitSchedule(scheduleId) {
    const response = await fetch(`/api/schedules/${scheduleId}/submit`, { method: "POST" });
    return response.json();
  },

  async approveSchedule(scheduleId) {
    const response = await fetch(`/api/schedules/${scheduleId}/approve`, { method: "POST" });
    return response.json();
  },

  async rejectSchedule(scheduleId) {
    const response = await fetch(`/api/schedules/${scheduleId}/reject`, { method: "POST" });
    return response.json();
  },
};
