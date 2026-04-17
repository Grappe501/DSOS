# Answer pattern fallbacks

| Condition | Result |
|-----------|--------|
| `MALONE_SMART_ANSWER_PATTERNS_ENABLED` off | `format_*_lookup_answer_standard` body + decision appendix only |
| Selector returns `standard` or all scores zero | Standard body |
| `should_fallback_to_standard_pattern` true | Standard body |
| Low confidence on obligation-style pattern without strong normalized support | Standard body |

Trace fields:

- `rendered_pattern`: what layout was actually used (`standard` or pattern id)  
- `fallback_to_standard`: bool when explicit downgrade path used  
- `pattern_id`: selector’s first pick (may differ from rendered after fallback)
