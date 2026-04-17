/** Origin for all `/api/*` calls. Empty = same-origin (Vite dev proxy). Set VITE_API_BASE on Netlify to your FastAPI URL. */
export const API_ORIGIN = (import.meta.env.VITE_API_BASE || "").replace(/\/$/, "");

export function apiUrl(path) {
  const p = path.startsWith("/") ? path : `/${path}`;
  return `${API_ORIGIN}${p}`;
}
