# Command Results

Initial implementation commands:

- `git status --short --branch`: clean at start.
- `git rev-parse HEAD`: `472220b37312304c05969be9df8a0254a4e97d41`.
- `git rev-parse origin/main`: `472220b37312304c05969be9df8a0254a4e97d41`.
- `git log --oneline -n 100`: P103, P102, P101, P100, P99, P98, P97, P96,
  P95, P94, P93, and pack planning/validate-only/staging packs present in
  recent history.

P104 runtime and report commands:

- `python scripts/run_pack_import_dry_run.py --all-examples --json`: passed;
  9 packs seen, 9 valid, 0 invalid.
- `python scripts/run_pack_import_dry_run.py --all-examples --no-validator-commands --json`: passed;
  9 packs seen, 9 valid, 0 invalid.
- `python scripts/validate_pack_import_dry_run_report.py`: passed.
- `python scripts/validate_pack_import_dry_run_report.py --json`: passed.

Adjacent P98-P103/local planning validations:

- Page dry-run command and report validator: passed.
- Manual Observation Batch 0 follow-up validator: passed; Batch 0 remains
  pending with 0 observed and 39 pending records.
- Connector approval/runtime planning audit validator: passed.
- Public search runtime integration audit validator: passed.
- Evidence ledger dry-run command and report validator: passed.
- Source cache dry-run command and report validator: passed.
- Public search ranking runtime plan validator: passed.
- Search result explanation contract validator: passed.
- Deep extraction contract validator: passed.
- Pack import runtime plan validator: passed.
- Page runtime plan validator: passed.

Pack contract, validate-only import, and staging/quarantine validators:

- `python scripts/validate_source_pack.py --all-examples`: passed.
- `python scripts/validate_evidence_pack.py --all-examples`: passed.
- `python scripts/validate_index_pack.py --all-examples`: passed.
- `python scripts/validate_contribution_pack.py --all-examples`: passed.
- `python scripts/validate_pack_set.py`: passed.
- `python scripts/validate_pack_import_report.py --all-examples`: passed.
- `python scripts/validate_only_pack_import.py --known-examples`: passed.
- `python scripts/validate_local_quarantine_staging_model.py`: passed.
- `python scripts/validate_staging_report_path_contract.py`: passed.
- `python scripts/validate_local_staging_manifest.py --all-examples`: passed.
- `python scripts/inspect_staged_pack.py --all-examples`: passed.

Public search, baseline, and eval checks:

- `python scripts/run_external_baseline_comparison.py --batch batch_0 --json`: passed;
  comparison remains not eligible because no manual observations are present.
- `python scripts/validate_external_baseline_comparison_report.py`: passed.
- `python scripts/validate_public_search_contract.py`: passed.
- `python scripts/validate_public_search_result_card_contract.py`: passed.
- `python scripts/validate_public_search_safety.py`: passed.
- `python scripts/validate_local_public_search_runtime.py`: passed.
- `python scripts/public_search_smoke.py`: passed.
- `python scripts/public_search_smoke.py --json`: passed.
- `python scripts/run_archive_resolution_evals.py`: passed; 6/6 local archive
  resolution tasks satisfied.
- `python scripts/run_archive_resolution_evals.py --json`: passed.
- `python scripts/run_search_usefulness_audit.py`: passed; local usefulness
  observations remain partial and do not claim external superiority.
- `python scripts/run_search_usefulness_audit.py --json`: passed.

Unit and architecture checks:

- `python -m unittest discover -s tests/runtime -t .`: passed, 27 tests.
- `python -m unittest discover -s tests/scripts -t .`: initially exposed
  test-registry metadata drift, then passed after repair, 685 tests.
- `python -m unittest discover -s tests/operations -t .`: passed, 629 tests.
- `python -m unittest discover -s tests/hardening -t .`: initially exposed
  test-registry metadata drift, then passed after repair, 53 tests.
- `python -m unittest discover -s tests/parity -t .`: passed, 25 tests.
- `python -m unittest discover -s runtime -t .`: passed, 320 tests.
- `python -m unittest discover -s surfaces -t .`: passed, 168 tests.
- `python -m unittest discover -s tests -t .`: initially exposed the same
  metadata drift, then passed after repair, 1510 tests.
- `python scripts/check_architecture_boundaries.py`: passed; no architecture
  boundary violations found.
- `git diff --check`: passed; Git emitted existing CRLF normalization warnings
  for site/dist files.

Optional local command availability:

- `gh`: not available in PATH; GitHub Actions status was not checked.
- `cargo`: not available in PATH; optional cargo checks were not run.
