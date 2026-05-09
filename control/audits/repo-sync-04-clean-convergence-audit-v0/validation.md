# Validation

## Commands Run

- `git status --short` - PASS, clean before fetch.
- `git rev-parse -q --verify MERGE_HEAD` - PASS, merge state absent.
- `git rev-parse --abbrev-ref HEAD` - PASS, current branch is `sync/preserve-dirty-work-20260509`.
- `git fetch --all --tags` - PASS.
- `git rev-parse HEAD origin/main` - PASS.
- `git rev-list --left-right --count HEAD...origin/main` - PASS, `10 7`.
- `git log --oneline HEAD ^origin/main` - PASS.
- `git log --oneline origin/main ^HEAD` - PASS.
- `git diff --name-status HEAD..origin/main` - PASS.
- `git diff --name-status origin/main..HEAD` - PASS.
- `git diff --stat HEAD..origin/main` - PASS.
- `git diff --stat origin/main..HEAD` - PASS.
- `git merge-tree <base> HEAD origin/main` - WARN, no conflict markers but semantic overlap remains high.

## Final Checks

- `git diff --check` - PASS.
- `python -m json.tool control/audits/repo-sync-04-clean-convergence-audit-v0/branch_inventory.json` - PASS.
- `python -m json.tool control/audits/repo-sync-04-clean-convergence-audit-v0/commit_divergence.json` - PASS.
- `python -m json.tool control/audits/repo-sync-04-clean-convergence-audit-v0/repo_sync_04_report.json` - PASS.
- `python scripts/check_architecture_boundaries.py` - PASS, 493 Python files checked and no architecture-boundary violations found.

## Targeted Validators

- `python scripts/validate_agent_assisted_observation_policy.py` - PASS.
- `python scripts/validate_observation_candidate.py` - PASS.
- `python scripts/validate_observation_candidate_review_queue.py` - PASS.
- `python scripts/validate_eureka_node_manifest.py` - PASS.
- `python scripts/validate_eureka_node_policy.py` - PASS.
- `python scripts/validate_eureka_node_capability.py` - PASS.
- `python scripts/validate_eureka_workunit.py` - PASS.
- `python scripts/validate_eureka_workunit_result.py` - PASS.
- `python scripts/validate_local_foundry_state.py` - PASS.

Remote-only OBS validators requested by this task were not present on the safety branch, which is consistent with the divergence finding:

- `scripts/validate_search_need_seed_candidates.py` - WARN, missing on safety branch.
- `scripts/validate_workunit_seed_candidates.py` - WARN, missing on safety branch.
- `scripts/validate_obs_track_b_synchronization.py` - WARN, missing on safety branch.
- `scripts/validate_obs_human_review_packet.py` - WARN, missing on safety branch.
