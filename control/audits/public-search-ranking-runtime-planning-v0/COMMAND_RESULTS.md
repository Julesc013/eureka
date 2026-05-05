# Command Results

All required P97 verification commands passed.

P97 checks:

- `python scripts/validate_public_search_ranking_runtime_plan.py`
- `python scripts/validate_public_search_ranking_runtime_plan.py --json`
- `python -m unittest tests.operations.test_public_search_ranking_runtime_plan tests.scripts.test_validate_public_search_ranking_runtime_plan`

Adjacent checks requested by P97 passed when present, including search result explanation, deep extraction, pack/page/source-runtime planning, connector-runtime planning, public query observation planning, ranking/merge/identity/page contracts, external baseline comparison report, hosted deployment evidence validation, public search contract/card/safety/local runtime/smoke, safety evidence, hosted rehearsal, site build/validation, publication/static artifact checks, generated artifact drift, archive evals, search usefulness audit, external baseline status, Python oracle check, test discovery lanes, and architecture boundaries.

Eval/status snapshot:

- Archive resolution evals: `{"satisfied": 6}`.
- Search usefulness audit: `{"covered": 5, "partial": 40, "source_gap": 10, "capability_gap": 7, "unknown": 2}`.
- External baseline Batch 0: 0 observed / 39 pending.
- Hosted deployment evidence: verifier passed as evidence, but static site status remains `verified_failed`, hosted backend is `not_configured`, hosted routes are `not_configured`, and safety/search handoff remain operator-gated.

Optional:

- Cargo is unavailable on `PATH`; optional `cargo check` and `cargo test` were skipped.
