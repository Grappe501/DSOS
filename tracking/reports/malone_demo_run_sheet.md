# Malone — Live demo run sheet (keep beside you)

## One-line story

Malone is the start of a **digital operating partner**: ingest knowledge, reason over it, say what to do next, and begin mapping how the business runs. Next phase: every department → full operations map → automation where it fits.

## Before you walk in (5 min)

| Step | Action |
|------|--------|
| 1 | API env: `MALONE_DEMO_MODE=1` `MALONE_DEMO_SAFE_RESPONSES=1` `MALONE_DEMO_LIMITED_SCOPE=1` |
| 2 | UI: `VITE_API_BASE` points at this API if not using Vite proxy |
| 3 | Browser: log in as your demo user |
| 4 | Confirm **Demo mode** badge on Malone page |

**Launcher (PowerShell):** `.\tools\run_dev_demo.ps1` from repo root (starts API with demo flags).

---

## Flow 1 — Operational Q&A (~3 min)

**Do not freestyle.** Use **only** these (copy-paste):

1. `[policy] How do we handle PHI when coordinating with a prescriber?`  
   *or strongest policy line you verified this morning*
2. `[sop] Walk me through the intake process for new patients.`  
   *or strongest SOP line you verified*
3. `Who handles prior authorization and when do we escalate?`

**Say while it runs:** “Answer is grounded on what we ingested; sections above the text summarize rules vs next steps.”

**Show:** Malone Output → presentation blocks → full answer → **technical details** only if they ask.

---

## Flow 2 — Trace / inspection (~2 min)

1. After Flow 1, click **Show read-only inspection**.
2. Say: “This is read-only telemetry—we’re not changing the answer.”
3. Optionally **Load persisted trace** if the button is enabled.
4. Expand **one** raw JSON block only if they want depth.

---

## Flow 3 — Department intake (~2 min)

1. Scroll to **Department intake**.
2. Click preset **Pharmacy — intake desk** (or type your label).
3. **Start intake session** → answer **mission** (one sentence) → **Record answer** → **Build operations map**.
4. Say: “This is how we start the org map—not the whole company on day one.”

---

## If something breaks

- **No badge:** API not restarted with `MALONE_DEMO_MODE=1`.
- **401 / CORS:** Set `MALONE_CORS_ORIGINS` to your exact UI origin.
- **Weak legal/policy answer:** Use only prompts you **verified this morning** on live data; do not improvise.

---

## Close (~30 sec)

“Real foundation: intelligence, structure, traceability, and a path to map every department. Not ‘everything’s done’—‘this is real and it scales.’”
