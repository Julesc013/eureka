# Command Results

Initial inspection:

- `git status --short --branch`: clean on `main...origin/main`.
- `git rev-parse HEAD`: recorded in report JSON.
- `git rev-parse origin/main`: matched HEAD at start.
- `git log --oneline -n 80`: confirmed P94 as latest local/origin milestone.
- `contracts/extraction/`: missing before P95.
- `control/inventory/extraction/`: missing before P95.

Post-change verification results are recorded after validators and test lanes run.

Post-change verification:

- `python scripts/validate_deep_extraction_request.py --all-examples`: passed, 7 examples.
- `python scripts/validate_deep_extraction_request.py --all-examples --json`: passed.
- `python scripts/validate_extraction_result_summary.py --all-examples`: passed, 7 examples.
- `python scripts/validate_extraction_result_summary.py --all-examples --json`: passed.
- `python scripts/validate_deep_extraction_contract.py`: passed, 49 checked items.
- `python scripts/validate_deep_extraction_contract.py --json`: passed.
- `python scripts/dry_run_deep_extraction_request.py --label "Example archive" --container-kind zip_archive --json`: passed, stdout-only request with hard false guarantees.
- Adjacent pack/page/source-cache/evidence/ranking/identity/public-search validators requested for P95: passed when present.
- `python scripts/run_external_baseline_comparison.py --batch batch_0 --json`: passed; comparison remains not eligible because Manual Observation Batch 0 has no observed records.
- `python scripts/verify_public_hosted_deployment.py --from-repo-config --json`: completed with hosted/static verification still not production-ready; configured static checks reported failure reasons and no deployment claim was made.
- Static site, publication, public search smoke, safety evidence, hosted rehearsal, archive eval, search usefulness audit, generated-artifact drift, Python oracle golden, architecture-boundary, and full Python unittest lanes passed after repairing AIDE audit-backlog JSON drift.
- `cargo --version`: unavailable in this environment; optional cargo check/test skipped.
- `git diff --check`: passed with existing CRLF conversion warnings for generated static artifact files.
