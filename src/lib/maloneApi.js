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
  const res = await fetch(path, {
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

  async voiceStatus() {
    return request("/api/malone/voice/status");
  },

  /**
   * Server-side ElevenLabs TTS; returns audio/mpeg Blob. Optional AbortSignal for cancellation (voice phase 2+).
   */
  async tts(text, options = {}) {
    const { signal } = options;
    const res = await fetch("/api/malone/tts", {
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
