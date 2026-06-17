# IA Candidate Index Refresh Authority Decision

Task: `IA-CANDIDATE-INDEX-REFRESH-AUTHORITY-00`

Status: PASS_WITH_WARNINGS

## Decision

Advance repo-local authority from
`IA-SOURCE-OBSERVATION-CACHE-DELTA-00` to
`IA-CANDIDATE-INDEX-REFRESH-00`.

The prior source-observation cache delta task is closed in queue authority. The
next task packet is created so the candidate-index refresh implementation can
proceed later under narrow, explicit path authority.

## Path Blocker Fixed

The queue previously still recommended
`IA-SOURCE-OBSERVATION-CACHE-DELTA-00`, and no task packet existed for
`IA-CANDIDATE-INDEX-REFRESH-00`. The new packet authorizes only the paths needed
for a future local candidate-index delta or dry-run refresh.

## Safety

- public exposure remains paused
- no candidate-index implementation is included in this authority task
- no public mutation
- no downloads or file fetches
- no Wayback replay
- no reviewed/master mutation
- no public-index mutation
- no evidence-ledger mutation
- license posture unchanged

## Validation

- `git fetch origin`: pass
- `git status --short --branch`: clean and synced before authority edits
- `git rev-list --left-right --count origin/dev...HEAD`: `0 0` before authority edits
- `python scripts/check_git_task_state.py --mode start-task --task-id IA-CANDIDATE-INDEX-REFRESH-00`: warn only because branch name does not include the task ID before edits
- `py -3 .aide/scripts/aide_lite.py pack --task "IA-CANDIDATE-INDEX-REFRESH-00"`: pass, then generated packet was manually narrowed to the task YAML authority
- `py -3 .aide/scripts/aide_lite.py doctor`: pass
- `py -3 .aide/scripts/aide_lite.py validate`: pass
- `python -m unittest tests.operations.test_ia_source_observation_cache_delta -v`: pass
- `python scripts/check_architecture_boundaries.py`: pass
- `python scripts/validate_public_alpha_readonly.py`: pass
- `python scripts/validate_snapshot_relay.py`: pass
- `git diff --check`: pass
- `python scripts/eureka_test_select.py --changed --failed-first --json`: pass, selected static preflight only

Post-commit generated-artifact cleanliness, clean-tree start-task guard, commit
check, and remote sync are recorded in the final task result.

## Remaining Blockers

- External artifact evidence remains waiting.
- User hardware details remain waiting.
- Public launch remains paused pending separate operator decisions.

Recommended next task: `IA-CANDIDATE-INDEX-REFRESH-00`.
