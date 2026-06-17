# IA Source Observation Cache Delta Authority Decision

Task: `IA-SOURCE-OBSERVATION-CACHE-DELTA-AUTHORITY-00`

Status: PASS_WITH_WARNINGS

## Decision

Advance repo-local authority from
`IA-METADATA-PROVIDER-WIRING-AND-SMOKE-00` to
`IA-SOURCE-OBSERVATION-CACHE-DELTA-00`.

The prior IA smoke task is closed in queue authority. The next task packet is
created so that the cache-delta implementation can proceed later under narrow,
explicit path authority.

## Path Blocker Fixed

The stale generated task packet previously forbade required implementation paths
such as `runtime/**`, `contracts/**`, and general `scripts/**`. The refreshed
packet for `IA-SOURCE-OBSERVATION-CACHE-DELTA-00` authorizes only the narrow
paths needed for the next source-observation cache delta task.

## Safety

- public exposure remains paused
- no runtime/cache implementation is included in this authority task
- no public mutation
- no downloads or file fetches
- no Wayback replay
- no reviewed/master mutation
- no public-index mutation
- license posture unchanged

## Validation

- `git fetch origin`: pass
- `git status --short --branch`: clean and synced before authority edits
- `git rev-list --left-right --count origin/dev...HEAD`: `0 0` before authority edits
- `python scripts/check_git_task_state.py --mode start-task --task-id IA-SOURCE-OBSERVATION-CACHE-DELTA-AUTHORITY-00`: warn only because branch name does not include the task ID
- `py -3 .aide/scripts/aide_lite.py pack --task "IA-SOURCE-OBSERVATION-CACHE-DELTA-00"`: pass, then generated packet was manually narrowed to the task YAML authority
- `py -3 .aide/scripts/aide_lite.py doctor`: pass
- `py -3 .aide/scripts/aide_lite.py validate`: pass
- `python -m unittest tests.operations.test_ia_metadata_smoke_scripts -v`: pass
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

Recommended next task: `IA-SOURCE-OBSERVATION-CACHE-DELTA-00`.
