# Tool Summary

Validate-Only Pack Import Tool v0 is implemented by
`scripts/validate_only_pack_import.py`.

It supports:

- `--pack-root <path>` repeatable explicit roots
- `--all-examples`
- `--include-ai-outputs`
- `--output <path>`
- `--json`
- `--strict`
- `--list-examples`

The default behavior validates all known repository example packs when no
explicit root is supplied. This default is deterministic and suitable for local
CI-style checks.

The tool is stdlib-only and delegates pack checks to existing validators
through the aggregate pack validation layer. It does not import, stage, index,
upload, submit, mutate runtime state, mutate public search, or mutate the
master index.
