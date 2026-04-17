# Demo Flows (Stabilized)

## Flow 1 — Operational Q&A

**Goal:** Grounded answer with optional structured presentation.

**Steps:** Chat → review Malone Output (presentation + answer) → optional technical details.

**Reliability:** Use prompts from `tools/demo_prompts.py`; match `[policy]` / `[sop]` / handbook intent to your enabled corpora.

## Flow 2 — Trace / Inspection

**Goal:** Show telemetry and optional persisted trace without overwhelming JSON.

**Steps:** Run a chat turn → open inspection → in demo mode expand raw JSON only as needed → load trace if id exists.

## Flow 3 — Department Intake (Starter)

**Goal:** Show org mapping machinery without claiming completeness.

**Steps:** Intake panel → preset or typed department → start session → answer mission/workflows → materialize map.
