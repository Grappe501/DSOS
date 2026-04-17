# Role / ownership

## Priority

1. Normalized `applies_to_role` on the unit (unchanged authority).
2. Else first **text extraction** role hint (`role_owner_extractor`).
3. Else `ownership_resolved`: null and `ownership_source`: `unknown`.

## Role keys

`pharmacist`, `pharmacy_technician`, `pic`, `nurse`, `compliance` — matched from explicit vocabulary only.

## No guessing

If the source does not mention a role, extraction does not invent one.
