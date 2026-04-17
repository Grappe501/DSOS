# Malone Demo Readiness — Report

## 1. DEMO OBJECTIVE

Deliver a **clean, repeatable** owner demo on the **single Malone path**: show grounded operational answers (legal / policy / SOP), operating copilot and decision context, read-only telemetry and traces, and a **starter** department intake flow—without new features, second bots, or weakened citations.

## 2. SELECTED DEMO FLOWS

| Flow | What the owner sees |
|------|---------------------|
| **Operational Q&A** | Chat → delivered answer with optional **presentation** sections (evidence excerpt, next steps, escalation) above the full answer when demo mode is on. |
| **Trace / Inspection** | “Show read-only inspection” → telemetry; optional trace load; in demo mode raw JSON is **collapsed by default** to reduce noise. |
| **Department intake (starter)** | Intake panel → preset department labels in demo mode → answers → materialize map JSON. |

## 3. DEMO MODE CONFIGURATION

| Env | Effect |
|-----|--------|
| `MALONE_DEMO_MODE=1` | Enables `presentation` on responses, demo badge in UI, intake presets, `/api/malone/demo/status`. |
| `MALONE_DEMO_SAFE_RESPONSES=1` | Cosmetic: collapse excessive blank lines; cap extremely long answers with ellipsis. **Does not** rewrite legal text. |
| `MALONE_DEMO_LIMITED_SCOPE=1` | Sets `truth_packet.retrieval_rules.allow_web_search` to **false** for the conversational render branch (reduces variable web-augmented output). |

`GET /api/malone/capabilities` and `GET /api/malone/demo/status` expose read-only flags.

## 4. RESPONSE FORMATTING IMPROVEMENTS

- **Presentation layer** (`presentation` on API response): read-only strings derived from existing `truth_packet` (first evidence excerpt, copilot next steps, escalation lines, delivery mode hint). **No change** to deterministic legal/policy/SOP delivery generators.
- **Safe responses**: whitespace / length hygiene only when `MALONE_DEMO_SAFE_RESPONSES` is set.

## 5. UI SIMPLIFICATIONS

- **Demo badge** when server reports `malone_demo_mode`.
- **ChatPanel**: demo-specific placeholder and short tip when demo is on.
- **ProposalPanel**: structured **What the rules say / What to do next / …** when `presentation` is present.
- **MaloneInspectionPanel**: telemetry / copilot / workflow / trace JSON **collapsed** when `demo.active` on the latest response.
- **DepartmentIntakePanel**: quick preset buttons for department name when demo is on.

## 6. WHAT WAS STABILIZED

- Defensive UI for missing `presentation` / `demo` keys.
- Demo envelope applied in one place (`attach_demo_envelope` after `handle_malone_request`).
- Limited-scope demo **does not** alter handbook/policy/SOP deterministic branches—only the generic render path’s web-search flag.

## 7. WHAT IS INTENTIONALLY HIDDEN OR DEFERRED

- No LLM-only “demo script” inside Malone; prompts live in `tools/demo_prompts.py` for the human operator.
- No fake citations or canned answers.
- No automatic hiding of technical details outside demo mode (defaults unchanged when demo is off).

## 8. DEMO SCRIPT (STEP-BY-STEP)

**Before the meeting**

1. Set server env: `MALONE_DEMO_MODE=1`, optionally `MALONE_DEMO_SAFE_RESPONSES=1`, `MALONE_DEMO_LIMITED_SCOPE=1`, and `MALONE_CORS_ORIGINS` to your static site if needed.
2. Confirm API health: `GET /health`.
3. Log in as a known user (owner/admin for review routes if you show them).

**Flow A — Operational Q&A (2–3 min)**

1. Open Malone; confirm **Demo mode** badge if env is set.
2. Paste a prompt from `tools/demo_prompts.py` (e.g. policy/SOP phrasing with `[policy]` / `[sop]` as appropriate to your corpus).
3. Point at **Malone Output**: presentation blocks (if any), then full answer, then TTS if desired.
4. Expand **Show technical details** only if the owner asks.

**Flow B — Trace / inspection (1–2 min)**

1. After a turn with `malone_telemetry`, click **Show read-only inspection**.
2. Show collapsed summaries; expand one JSON block if needed.
3. Click **Load persisted trace** if `scenario_memory_id` is present.

**Flow C — Department intake (2 min)**

1. Scroll to **Department intake**; use a preset or type “Pharmacy Intake”.
2. **Start intake session** → add a **mission** answer → **Record answer** → **Build operations map** and show JSON.

**Close**

- Reinforce: evidence and citations remain authoritative; intake and copilot are **guidance**, not statute.

## 9. HARD-FAIL COMPLIANCE CHECK

| Rule | Status |
|------|--------|
| No new major product features | Pass (flags + presentation + UI only). |
| Single Malone path | Pass. |
| Citation-first legal behavior preserved | Pass (no edits to deterministic delivery functions). |
| No second chat path | Pass. |
| Tracking outputs produced | Pass (this report + companion JSON/MD). |
