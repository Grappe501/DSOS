# Intake / discovery strategy

## Root

Default: `tracking/data/internal_company_knowledge/`.

## Walk policy

- Recursive `os.walk`, POSIX-style relative paths for stable sorting.
- Skip dotfiles and **`README.md`** (documentation, not knowledge rows).
- First path segment = **category** for classification (e.g. `policy_manual/file.md` → `policy_manual`).

## File eligibility

- **Preferred:** `.md`, `.txt`, `.markdown` — read as UTF-8 for preview + ingest.
- **Blocked for generic ingest:** `.pdf`, `.docx` — `active_candidate=false` with conversion note (existing generic pipeline is text-only).

## Stable keys

`internal_company__{folder_slug}__{filename_slug}__{sha8(path)}` ensures deterministic registry keys without collisions from folder + name.
