# Normalized unit taxonomy (v0)

Implemented string slugs (see `unit_types.py`):

| Slug | Typical use |
|------|-------------|
| `definition` | Defined terms |
| `requirement` | Mandatory duties (must/shall) |
| `prohibition` | Must not / unlawful / prohibited |
| `permission` | May / discretionary |
| `exception` | Except / unless carve-outs |
| `escalation_rule` | Escalation / supervisor / compliance contact |
| `workflow_step` | Reserved for SOP (future) |
| `documentation_rule` | Record-keeping duties |
| `reporting_rule` | Reporting / notification duties |
| `contact_reference` | Reserved |
| `decision_log_entry` | Reserved (meeting memory) |
| `policy_rule` | Policy manual generic rule |
| `general_statement` | Fallback when signals are weak |

**Action types** (orthogonal): `obligation`, `prohibition`, `permission`, `recommendation`, `discretion`, `unknown`.

**Requirement levels**: `must`, `should`, `may`, `unknown`.

New types can be added as strings without migration if they fit existing columns; otherwise add `structured_facets_json` keys.
