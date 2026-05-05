# Command Results

All required P96 verification commands passed on 2026-05-06 local time.

P96 contract checks:

- `python scripts/validate_search_result_explanation.py --all-examples`
- `python scripts/validate_search_result_explanation.py --all-examples --json`
- `python scripts/validate_search_result_explanation_contract.py`
- `python scripts/validate_search_result_explanation_contract.py --json`
- `python scripts/dry_run_search_result_explanation.py --title "Example result" --match-kind lexical_match --json`

Adjacent checks requested by P96 passed when present, including deep extraction, pack/page/runtime planning, connector-runtime planning, identity/merge/ranking/page contracts, external baseline report checks, hosted deployment evidence validation, public search contract/card/safety/local runtime/smoke, safety evidence, hosted rehearsal, site build/validation, publication/static artifact checks, generated artifact drift, archive evals, search usefulness audit, external baseline status, Python oracle check, test discovery lanes, and architecture boundaries.

Eval/status snapshot:

- Archive resolution evals: `{"satisfied": 6}`.
- Search usefulness audit: `{"covered": 5, "partial": 40, "source_gap": 10, "capability_gap": 7, "unknown": 2}`.
- External baseline Batch 0: 0 observed / 39 pending.
- Hosted deployment evidence: verifier passed as evidence, but static site status remains `verified_failed`, hosted backend is `not_configured`, and safety/search handoff remain operator-gated.

Optional:

- Cargo is unavailable on `PATH`; optional `cargo check` and `cargo test` were skipped.
