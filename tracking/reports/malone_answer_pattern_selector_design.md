# Answer pattern selector design

## Inputs

- `message` (user text)
- `source_type` (`legal_handbook` | `policy_manual` for scoring)
- Flat list of normalized unit dicts from the active bundle

## Scoring

1. `score_question_signals`: additive integer weights per pattern from phrases and citation-like short queries.
2. `score_normalized_signals`: additive weights from `normalized_unit_type` buckets and presence of condition/exception/escalation text.
3. `combined_signal_scores`: sum per pattern (plus a weak default on `standard` from question scoring only — **not** used as the competitive winner).

## Winner rule

- `max_score = max(scores[p] for p in {source_locator, requirement, workflow, exception})`
- If `max_score == 0` → **`standard`**
- Else pick the **first** pattern in fixed priority order whose score equals `max_score`

## Confidence

- `high` if `max_score >= 12`
- `medium` if `>= 6` or weak-signal branch
- `low` if zero

## Legal special case

Downgrade obligation-style winners when there are **no** normalized units and the winning text score is **&lt; 12**, to avoid hollow structured obligation sections.
