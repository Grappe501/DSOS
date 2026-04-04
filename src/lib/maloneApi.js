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
  const res = await fetch(path, {
    ...options,
    headers: {
      ...buildHeaders(),
      ...(options.headers || {}),
    },
  });

  const payload = await parseResponse(res);

  if (!res.ok) {
    throw new Error(typeof payload === "string" ? payload : JSON.stringify(payload));
  }

  return payload;
}

export const maloneApi = {
  async chat(message) {
    return request("/api/malone/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    });
  },

  async getRecentProposals(limit = 12) {
    return request(`/api/malone/proposals?limit=${encodeURIComponent(limit)}`);
  },
};
