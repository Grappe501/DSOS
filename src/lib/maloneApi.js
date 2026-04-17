import { apiUrl } from "./apiOrigin.js";

async function parseResponse(res) {
  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) return res.json();
  return res.text();
}

function buildHeaders() {
  const token = localStorage.getItem("access_token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function request(path, options = {}) {
  const { signal, headers: optHeaders, ...rest } = options;
  const res = await fetch(apiUrl(path), {
    ...rest,
    ...(signal ? { signal } : {}),
    headers: {
      ...buildHeaders(),
      ...(optHeaders || {}),
    },
  });

  const payload = await parseResponse(res);

  if (!res.ok) {
    throw new Error(typeof payload === "string" ? payload : JSON.stringify(payload));
  }

  return payload;
}

export const maloneApi = {
  async me() {
    return request("/api/me");
  },

  /**
   * Same Malone chat spine as typing; optional AbortSignal cancels the HTTP request (Voice Phase 2+).
   */
  async chat(message, options = {}) {
    const { signal } = options;
    return request("/api/malone/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
      ...(signal ? { signal } : {}),
    });
  },

  async getRecentProposals(limit = 12) {
    return request(`/api/malone/proposals?limit=${encodeURIComponent(limit)}`);
  },

  async getTelemetrySchema() {
    return request("/api/malone/inspect/telemetry-schema");
  },

  /** Read-only demo mode flags (MALONE_DEMO_* server env). */
  async getDemoStatus() {
    return request("/api/malone/demo/status");
  },

  async getInspectTraces(limit = 20) {
    return request(`/api/malone/inspect/traces?limit=${encodeURIComponent(limit)}`);
  },

  async getInspectTrace(scenarioMemoryId) {
    return request(`/api/malone/inspect/traces/${encodeURIComponent(scenarioMemoryId)}`);
  },

  /**
   * Owner/admin: submit human review feedback (governance; does not edit source evidence).
   */
  async reviewSubmitFeedback(body) {
    return request("/api/malone/review/feedback", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  /** Owner/admin: company-knowledge candidates (ingestion sources + review heads). */
  async reviewCompanyKnowledgeCandidates(limit = 80) {
    return request(`/api/malone/review/company-knowledge/candidates?limit=${encodeURIComponent(limit)}`);
  },

  /** Owner/admin: website pack lines that have review heads (manifest-backed). */
  async reviewWebsitePackHeads(limit = 60) {
    return request(`/api/malone/review/company-knowledge/website-pack-heads?limit=${encodeURIComponent(limit)}`);
  },

  /** Owner/admin: promote an approved ingestion source version to active/trusted retrieval. */
  async reviewPromoteCompanyIngestionVersion(body) {
    return request("/api/malone/review/company-knowledge/promote-version", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  /** Owner/admin: archive a version and record governance (optional superseded). */
  async reviewArchiveCompanyIngestionVersion(body) {
    return request("/api/malone/review/company-knowledge/archive-version", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  /** Department intake + operations map (same auth as chat). */
  async operationsMapStartIntake(body) {
    return request("/api/malone/operations-map/intake/sessions", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  async operationsMapGetIntakeSession(sessionId) {
    return request(`/api/malone/operations-map/intake/sessions/${encodeURIComponent(sessionId)}`);
  },

  async operationsMapPostAnswer(sessionId, body) {
    return request(`/api/malone/operations-map/intake/sessions/${encodeURIComponent(sessionId)}/answers`, {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  async operationsMapMaterialize(sessionId) {
    return request(`/api/malone/operations-map/intake/sessions/${encodeURIComponent(sessionId)}/materialize`, {
      method: "POST",
    });
  },

  async operationsMapGetDepartmentMap(departmentId) {
    return request(`/api/malone/operations-map/departments/${encodeURIComponent(departmentId)}/map`);
  },

  async voiceStatus() {
    return request("/api/malone/voice/status");
  },

  /**
   * Server-side ElevenLabs TTS; returns audio/mpeg Blob. Optional AbortSignal for cancellation (voice phase 2+).
   */
  async tts(text, options = {}) {
    const { signal } = options;
    const res = await fetch(apiUrl("/api/malone/tts"), {
      method: "POST",
      headers: buildHeaders(),
      body: JSON.stringify({ text }),
      signal,
    });
    if (!res.ok) {
      let detail = res.statusText;
      try {
        const j = await res.json();
        if (j?.detail) {
          detail = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail);
        }
      } catch {
        /* ignore */
      }
      throw new Error(detail);
    }
    return res.blob();
  },
};
