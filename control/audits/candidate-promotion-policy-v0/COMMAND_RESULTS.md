# Command Results

Verified locally on 2026-05-02.

## P65 Required

- `python scripts/validate_candidate_promotion_assessment.py --all-examples` - passed
- `python scripts/validate_candidate_promotion_assessment.py --all-examples --json` - passed
- `python scripts/validate_candidate_promotion_policy.py` - passed
- `python scripts/validate_candidate_promotion_policy.py --json` - passed
- `python scripts/dry_run_candidate_promotion_assessment.py --candidate-label "Firefox ESR Windows XP compatibility candidate" --candidate-type compatibility_claim_candidate --json` - passed
- `python -m unittest tests.operations.test_candidate_promotion_policy tests.scripts.test_validate_candidate_promotion_assessment tests.scripts.test_validate_candidate_promotion_policy tests.scripts.test_dry_run_candidate_promotion_assessment` - passed

## Regression Sweep

- Query-intelligence predecessor validators from P59-P64 - passed
- Hosted/public search rehearsal and safety validators/runners - passed
- Public search contract/result card/safety/local runtime smoke checks - passed
- Static site/publication/generated artifact drift checks - passed
- Archive resolution eval runner and JSON mode - passed; status counts: `satisfied=6`
- Search usefulness audit runner and JSON mode - passed; counts: `covered=5`, `partial=40`, `source_gap=10`, `capability_gap=7`, `unknown=2`
- External baseline status - passed; `192` global slots remain pending manual observation and Batch 0 has `39` pending slots
- Unit discovery lanes for `tests/scripts`, `tests/operations`, `tests/hardening`, `tests/parity`, `runtime`, `surfaces`, and `tests` - passed
- `python scripts/check_architecture_boundaries.py` - passed

The consolidated sweep ran 60 commands: 60 passed, 0 failed, 0 skipped as missing.

## Optional

- `cargo --version` - unavailable; Cargo is not installed or not on PATH in this environment.
- `cargo check --workspace --manifest-path crates/Cargo.toml` - not run because Cargo is unavailable.
- `cargo test --workspace --manifest-path crates/Cargo.toml` - not run because Cargo is unavailable.

- `git diff --check` - passed
- `git status --short --branch` - passed; worktree was dirty with P65 changes before commit.
