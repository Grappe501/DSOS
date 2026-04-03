const API_BASE = "/api";
const AUTH_BASE = "/api/auth";

function getToken() {
  return localStorage.getItem("access_token");
}

function setToken(token) {
  if (token) {
    localStorage.setItem("access_token", token);
  }
}

function clearToken() {
  localStorage.removeItem("access_token");
}

function buildHeaders(customHeaders = {}, includeJson = true) {
  const headers = {
    ...(includeJson ? { "Content-Type": "application/json" } : {}),
    ...customHeaders,
  };

  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
}

async function parseResponse(res) {
  const contentType = res.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    return res.json();
  }

  const text = await res.text();
  return text || null;
}

function buildErrorMessage(payload, fallback = "Request failed") {
  if (!payload) return fallback;
  if (typeof payload === "string") return payload;
  if (typeof payload.detail === "string") return payload.detail;
  if (Array.isArray(payload.detail)) return JSON.stringify(payload.detail);
  return JSON.stringify(payload);
}

async function request(url, options = {}) {
  const headers = buildHeaders(options.headers, options.includeJson !== false);

  const res = await fetch(url, {
    ...options,
    headers,
  });

  const payload = await parseResponse(res);

  if (!res.ok) {
    const error = new Error(buildErrorMessage(payload));
    error.status = res.status;
    error.payload = payload;

    if (res.status === 401) {
      clearToken();
    }

    throw error;
  }

  return payload;
}

function normalizeLoginArgs(emailOrPayload, password) {
  if (
    emailOrPayload &&
    typeof emailOrPayload === "object" &&
    !Array.isArray(emailOrPayload)
  ) {
    return {
      email: String(emailOrPayload.email ?? "").trim(),
      password: String(emailOrPayload.password ?? ""),
    };
  }

  return {
    email: String(emailOrPayload ?? "").trim(),
    password: String(password ?? ""),
  };
}

function toQueryString(params = {}) {
  const query = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") return;
    query.append(key, String(value));
  });

  const qs = query.toString();
  return qs ? `?${qs}` : "";
}

export const api = {
  async login(emailOrPayload, password) {
    const payload = normalizeLoginArgs(emailOrPayload, password);

    const data = await request(`${AUTH_BASE}/login`, {
      method: "POST",
      body: JSON.stringify(payload),
    });

    if (data?.access_token) {
      setToken(data.access_token);
    }

    return data;
  },

  async logout() {
    clearToken();
    return { ok: true };
  },

  async me() {
    return request(`${AUTH_BASE}/me`, {
      method: "GET",
    });
  },

  async getSchedules(params = {}) {
    return request(`${API_BASE}/schedules${toQueryString(params)}`, {
      method: "GET",
    });
  },

  async createSchedule(payload) {
    return request(`${API_BASE}/schedules/create`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async cancelSchedule(id) {
    return request(`${API_BASE}/schedules/${id}/cancel`, {
      method: "POST",
    });
  },

  async getAudit(params = {}) {
    return request(`${API_BASE}/audit${toQueryString(params)}`, {
      method: "GET",
    });
  },

  async getOperationalSummary() {
    return request(`${API_BASE}/operational/summary`, {
      method: "GET",
    });
  },

  async getWorkflows(params = {}) {
    return request(`${API_BASE}/workflows${toQueryString(params)}`, {
      method: "GET",
    });
  },

  async getMessages(params = {}) {
    return request(`${API_BASE}/messages${toQueryString(params)}`, {
      method: "GET",
    });
  },

  async getEvents(params = {}) {
    return request(`${API_BASE}/events${toQueryString(params)}`, {
      method: "GET",
    });
  },
};

export { API_BASE, AUTH_BASE, getToken, setToken, clearToken };