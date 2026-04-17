# Next thread: smart answer patterns — follow-ups

## Done

- Deterministic selector + four patterns + standard fallback wired through `answer_formatter` and `malone_service`.
- Truth packet + `packet_meta` trace fields; audit `meta_json.answer_pattern` on delivery.

## Next

1. Implement **definition**, **escalation**, **comparison**, **operational_summary** patterns with signals and renderers.
2. Feed `answer_pattern` into **LLM** `render_conversational_response` with “do not contradict excerpts” rules.
3. **SOP-specific** selector profile (`source_type` = `sop_workflow`) if SOP corpus diverges from policy phrasing.
4. Optional **frontend** (`src/`) badge showing selected pattern for power users.

## Verify

```bash
python -m pytest tests/test_answer_patterns.py -q
python tools/debug_answer_patterns.py
```
