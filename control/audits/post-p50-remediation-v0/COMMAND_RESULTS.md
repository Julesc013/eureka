# Command Results

| Command | Status | Notes |
|---|---|---|
| `git status --short --branch` | pass | Initial P51 status was clean on `main...origin/main`. |
| `git rev-parse HEAD` | pass | Initial head: `d26d093897e5c7b09cf233c5a2771186009e8bfb`. |
| `git rev-parse origin/main` | pass | Initial origin/main matched `d26d093897e5c7b09cf233c5a2771186009e8bfb`. |
| `git log --oneline -n 20` | pass | P50 commits present. |
| `python scripts/validate_post_p49_platform_audit.py` | pass | P50 audit pack valid. |
| `python scripts/validate_post_p49_platform_audit.py --json` | pass | JSON result parsed. |
| `python scripts/check_architecture_boundaries.py` | pass | 445 Python files checked, no violations. |
| `python scripts/run_archive_resolution_evals.py` | pass | 6 tasks, 6 satisfied. |
| `python scripts/run_search_usefulness_audit.py` | pass | 64 queries: covered 5, partial 40, source_gap 10, capability_gap 7, unknown 2. |
| `python scripts/report_external_baseline_status.py --json` | pass | 192 pending, 0 observed; batch_0 39 pending, 0 observed. |
| `cargo --version` | unavailable | Cargo not installed in current environment. |
| `python scripts/validate_source_pack.py --all-examples --json` | pass | 1/1 source pack example valid. |
| `python scripts/validate_evidence_pack.py --all-examples --json` | pass | 1/1 evidence pack example valid. |
| `python scripts/validate_index_pack.py --all-examples --json` | pass | 1/1 index pack example valid. |
| `python scripts/validate_contribution_pack.py --all-examples --json` | pass | 1/1 contribution pack example valid. |
| `python scripts/validate_master_index_review_queue.py --all-examples --json` | pass | 1/1 review queue example valid. |
| `python scripts/validate_pack_set.py --known-examples --json` | pass | 5/5 known examples passed. |
| `python scripts/validate_only_pack_import.py --known-examples --json` | pass | 5/5 validate-only examples passed; no mutation flags false. |
| `python -m unittest tests.scripts.test_validate_source_pack ... test_validate_only_pack_import` | pass | 54 focused pack validator tests passed. |
| `git diff --check` | pass | No whitespace errors; line-ending warnings only. |

Final verification commands are recorded after the P51 validator/test metadata
is added.
