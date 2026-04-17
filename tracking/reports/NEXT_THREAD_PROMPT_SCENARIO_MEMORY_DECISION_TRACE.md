# Next thread prompt — scenario memory & decision trace (follow-on)

## Done in this pass

- `malone_scenario_memories` / `malone_decision_traces` tables, services, Malone wiring, tests, reports.

## Suggested next steps

1. **Admin UI** (allowed app routes only): browse/filter scenario memory, mark `review_audit_status`, export trace JSON.
2. **Governance**: background job to archive old rows; retention policy per tenant.
3. **Similarity**: optional embedding index *only* for candidate priors, still subject to precedence rules.
4. **API**: read-only endpoints returning trace ids already in `truth_packet.packet_meta` for clients.

## Verify

```bash
python -m pytest tests -q
alembic upgrade head
python -m compileall app tools tracking/scripts -q
npm run build
```
