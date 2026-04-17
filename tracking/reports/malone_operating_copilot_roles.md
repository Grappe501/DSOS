# Role and ownership guidance

## Source of truth

Role lines are built from the **decision/workflow** block (`build_role_lines` → `collect_roles` / action step role hints). They reflect normalized unit fields and assembled steps, not free-form inference.

## User-facing framing

Formatter labels the section **“Who should act (normalized role hints)”** to avoid implying HR or licensure conclusions beyond the ingested material.

## Gaps

When `partial_workflow` is true or roles are empty, uncertainty notes and the distinction object tell the user to verify owners with policy administrators and primary sources.
