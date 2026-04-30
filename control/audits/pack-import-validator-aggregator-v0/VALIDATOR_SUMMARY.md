# Validator Summary

Pack Import Validator Aggregator v0 adds `scripts/validate_pack_set.py`.

The command is stdlib-only and offline. It validates all known repo example
packs by reading `control/inventory/packs/example_packs.json`, detecting pack
type by root manifest, and delegating to the existing individual validators.

Supported pack types:

- `source_pack`
- `evidence_pack`
- `index_pack`
- `contribution_pack`
- `master_index_review_queue`

Supported modes:

- `--list-examples`
- `--all-examples`
- `--pack-root <path>`
- `--pack-type <type|auto>`
- `--strict`
- `--json`

The aggregator reports `passed`, `failed`, `unavailable`, and `unknown_type`
without converting validation into import or acceptance.

