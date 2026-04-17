# Next thread: decision / workflow reasoning — follow-ups

## Completed in prior pass

- `app/services/decision_reasoning/` merge + action plan + truth packet `decision_workflow`.
- Deterministic legal / policy / SOP answers append operational guidance when safe.
- Cross-source opt-in (`MALONE_CROSS_SOURCE_DECISION_ENABLED`) and SOP intent path.
- Tests: `tests/test_decision_reasoning.py`; debug: `python tools/debug_decision_reasoning.py`.

## Suggested next steps

1. **LLM path**: pass `decision_workflow` into `render_conversational_response` with instructions to **not** contradict citations or invent steps outside `source_evidence_map`.
2. **Conflict handling**: deterministic signals when legal vs policy units disagree on obligation strength (flag-only).
3. **Metrics**: log `decision_workflow.fallback_reason` and `partial_workflow` rates on `LegalAnswerTrace` or proposal meta.
4. **Frontend** (`src/`): optional panel showing roles/steps next to citations (additive).

## Verify

```bash
python -m pytest tests/test_decision_reasoning.py tests/test_normalized_retrieval.py -q
python tools/debug_decision_reasoning.py
```
