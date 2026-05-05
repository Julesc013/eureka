# Command Results

Initial inspection:

- `git status --short --branch`: clean on `main...origin/main`.
- `git rev-parse HEAD`: `42063f8440f4820b9ab79d17f2764b26a6668054`.
- `git rev-parse origin/main`: `42063f8440f4820b9ab79d17f2764b26a6668054`.
- `git log --oneline -n 100`: P99 evidence-ledger dry-run runtime commits are at
  the tip.

Evidence inspected:

- Public search local runtime code in `runtime/gateway/public_api/public_search.py`.
- Public route inventory in `control/inventory/publication/public_search_routes.json`.
- Public search safety inventory in `control/inventory/publication/public_search_safety.json`.
- Static handoff and config inventories under `control/inventory/publication/`.
- Public index stats in `data/public_index/index_stats.json`.
- P98 and P99 dry-run runtime inventories.
- Query observation, page runtime, ranking runtime, pack import, deep extraction,
  and explanation inventories.

Final verification:

- `python scripts/validate_public_search_runtime_integration_audit.py`: passed.
- `python scripts/validate_public_search_runtime_integration_audit.py --json`: passed.
- `python scripts/report_public_search_runtime_integration_status.py --json`: passed.
- `python scripts/run_evidence_ledger_dry_run.py --all-examples --json`: passed,
  7 valid synthetic candidates, 0 invalid, no mutation hard booleans set.
- `python scripts/validate_evidence_ledger_dry_run_report.py`: passed.
- `python scripts/run_source_cache_dry_run.py --all-examples --json`: passed,
  5 valid synthetic candidates, 0 invalid, no mutation hard booleans set.
- `python scripts/validate_source_cache_dry_run_report.py`: passed.
- `python scripts/validate_public_search_ranking_runtime_plan.py`: passed.
- `python scripts/validate_search_result_explanation_contract.py`: passed.
- `python scripts/validate_deep_extraction_contract.py`: passed.
- `python scripts/validate_pack_import_runtime_plan.py`: passed.
- `python scripts/validate_page_runtime_plan.py`: passed.
- Connector runtime planning validators for Internet Archive metadata,
  Wayback/CDX/Memento, GitHub releases, PyPI metadata, npm metadata, and
  Software Heritage: passed.
- Query observation, compatibility-aware ranking, evidence-weighted ranking,
  result merge/deduplication, identity resolution, comparison page, source page,
  and object page validators: passed.
- `python scripts/run_external_baseline_comparison.py --batch batch_0 --json`:
  passed with 0 observed manual baseline records, 39 pending batch slots, and no
  eligible comparison.
- `python scripts/validate_external_baseline_comparison_report.py`: passed.
- `python scripts/verify_public_hosted_deployment.py --from-repo-config --json`:
  passed as evidence collection, with hosted backend not configured and hosted
  route/safe-query/blocked-request evidence operator-gated.
- `python scripts/validate_public_hosted_deployment_evidence.py`: passed.
- Public search contract, result-card contract, safety, local runtime, smoke,
  safety evidence, hosted rehearsal, and hosted rehearsal validator commands:
  passed.
- Static site, publication inventory, public static site, GitHub Pages static
  artifact, generated artifact drift, archive eval, search usefulness audit,
  external baseline status, and Python oracle golden checks: passed.
- `python -m unittest discover -s tests/runtime -t .`: passed, 14 tests.
- `python -m unittest discover -s tests/scripts -t .`: passed, 658 tests.
- `python -m unittest discover -s tests/operations -t .`: passed, 613 tests.
- `python -m unittest discover -s tests/hardening -t .`: passed, 53 tests.
- `python -m unittest discover -s tests/parity -t .`: passed, 25 tests.
- `python -m unittest discover -s runtime -t .`: passed, 320 tests.
- `python -m unittest discover -s surfaces -t .`: passed, 168 tests.
- `python -m unittest discover -s tests -t .`: passed, 1454 tests.
- `python scripts/check_architecture_boundaries.py`: passed, 458 Python files
  checked.
- `git diff --check`: passed.

Optional local tools:

- `gh --version`: unavailable; `gh` is not installed in this shell.
- `gh auth status`: unavailable; `gh` is not installed in this shell.
- `cargo --version`: unavailable; `cargo` is not installed in this shell.
- Cargo workspace check/test: unavailable because `cargo` is not installed.
