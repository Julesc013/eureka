# Command Results

Initial P94 prerequisite commands:

- `git status --short --branch`: clean `main` tracking `origin/main`.
- `git rev-parse HEAD`: recorded in report JSON.
- `git rev-parse origin/main`: matched local HEAD at inspection time.
- `git log --oneline -n 80`: P93/P92/P91/P90/P89 and earlier governance history present.
- `python scripts/validate_source_pack.py --all-examples`: passed, 1/1.
- `python scripts/validate_evidence_pack.py --all-examples`: passed, 1/1.
- `python scripts/validate_index_pack.py --all-examples`: passed, 1/1.
- `python scripts/validate_contribution_pack.py --all-examples`: passed, 1/1.
- `python scripts/validate_pack_set.py`: passed, 5/5.
- `python scripts/validate_pack_import_report.py --all-examples`: passed, 3/3.
- `python scripts/validate_only_pack_import.py --known-examples`: validate_only_passed, 5/5.
- `python scripts/validate_local_quarantine_staging_model.py`: valid.
- `python scripts/validate_staging_report_path_contract.py`: valid.
- `python scripts/validate_local_staging_manifest.py --all-examples`: passed, 1/1.
- `python scripts/inspect_staged_pack.py --all-examples`: passed, 1/1.

P94 validator and focused tests:

- `python scripts/validate_pack_import_runtime_plan.py`: valid.
- `python scripts/validate_pack_import_runtime_plan.py --json`: valid JSON, readiness `ready_for_local_dry_run_runtime_after_operator_approval`.
- `python -m unittest tests.operations.test_pack_import_runtime_plan tests.scripts.test_validate_pack_import_runtime_plan`: 8 tests passed.

Related runtime planning and contracts:

- Page runtime planning, Software Heritage, npm, PyPI, GitHub Releases, Wayback/CDX/Memento, Internet Archive metadata connector runtime plans: valid.
- Public query observation runtime plan, compatibility-aware ranking, evidence-weighted ranking, result merge/deduplication, and cross-source identity contracts: valid.

Public search, static, hosted, and baseline checks:

- Public search contract, result-card contract, safety, local runtime, smoke, safety evidence, hosted local rehearsal, static build/validate, publication inventory, public static site, Pages static artifact, and generated-artifact drift checks passed.
- Hosted deployment remains operator-gated: hosted backend not configured and configured static route verification failed.
- External baseline comparison remains not eligible: Manual Observation Batch 0 has 0 observed / 39 pending; global baseline slots remain 192 pending.

Eval and full test checks:

- Archive resolution evals: 6/6 satisfied.
- Search usefulness audit: 64 queries; capability_gap=7, covered=5, partial=40, source_gap=10, unknown=2.
- Python oracle golden check: passed.
- `python -m unittest discover -s tests/scripts -t .`: 613 tests passed.
- `python -m unittest discover -s tests/operations -t .`: 589 tests passed.
- `python -m unittest discover -s tests/hardening -t .`: 53 tests passed.
- `python -m unittest discover -s tests/parity -t .`: 25 tests passed.
- `python -m unittest discover -s runtime -t .`: 320 tests passed.
- `python -m unittest discover -s surfaces -t .`: 168 tests passed.
- `python -m unittest discover -s tests -t .`: 1371 tests passed.
- `python scripts/check_architecture_boundaries.py`: passed for 446 Python files.
- `git diff --check`: exited 0 with line-ending warnings only.

Optional:

- `gh`: unavailable.
- `cargo`: unavailable.

No verification command imported packs into runtime state, staged real packs, executed pack contents, followed pack URLs, created uploads/admin endpoints, wrote source cache/evidence ledger/candidate/public/local/master indexes, created promotion decisions, created accepted records, deployed anything, added credentials, added telemetry/accounts, or called model/source APIs.
