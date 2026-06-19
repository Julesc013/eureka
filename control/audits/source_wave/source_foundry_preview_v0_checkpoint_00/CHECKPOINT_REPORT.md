# Source Foundry Preview v0 Checkpoint

Task: `SOURCE-FOUNDRY-PREVIEW-V0-CHECKPOINT-00`

Status: `BLOCKED_BY_EXTERNAL_FULL_DISCOVERY_FAILURE`

Generated: `2026-06-18T21:36:09+10:00`

## Repo State

- branch: `dev`
- checkpoint source HEAD: `ad68a79fec18d602024395921b5f5b93e70d8d3f`
- origin/dev: `ad68a79fec18d602024395921b5f5b93e70d8d3f`
- origin/main: `3b770ab9a9f6a99572f66c3ab2b89fb4e6fddf31`
- origin/dev sync before edits: `0 0`
- origin/main...origin/dev: `0 12`
- origin/main is ancestor of origin/dev: true
- worktree before edits: clean

## Milestone

Source Foundry Preview v0 is coherent on `dev`:

```text
IA metadata
-> source observations
-> candidates
-> evidence summaries
-> review batch
-> 8-item operator tranche
```

Counts:

- source observations: 56
- provisional candidates: 56
- evidence summaries: 344
- review items prepared: 56
- pending review items: 56
- tranche 01 items: 8
- tranche 01 promotion eligible: 0
- tranche 01 decisions supplied: false
- tranche 01 decisions recorded: 0

This is not reviewed IA truth. It is a pending-operator-review tooling
checkpoint.

## Human Boundary

Tranche 01 is fixture-derived:

- fixture-derived tranche items: 8
- live-derived tranche items: 0
- promotion blocked items: 8
- blocker: `PROMOTION_BLOCKED_FIXTURE_ONLY_PROVENANCE`
- blocker: `WAITING_FOR_OPERATOR_REVIEW_DECISIONS`

Review decisions, review-ledger writes, reviewed-record creation, reviewed-index
refresh, and accepted-truth claims remain blocked until explicit operator input
and later review/materialization tasks.

## Safety

- no automatic decisions: true
- no automatic promotion: true
- no review-ledger decisions recorded: true
- no reviewed records created: true
- no reviewed/master mutation: true
- no public-index mutation: true
- no candidate-index store mutation: true
- no evidence-ledger store mutation: true
- no snapshot refresh: true
- no network/provider call during checkpoint: true
- no downloads/file fetch: true
- no Wayback replay: true
- public exposure remains paused: true
- license posture unchanged: true

## Validation

Passed:

- `git fetch origin`
- `git status --short --branch`
- `git rev-list --left-right --count origin/dev...HEAD`
- `python scripts/check_git_task_state.py --mode start-task --task-id SOURCE-FOUNDRY-PREVIEW-V0-CHECKPOINT-00`
  - warning only: branch `dev` does not contain the task ID
- `git rev-list --left-right --count origin/main...origin/dev`
- `git merge-base --is-ancestor origin/main origin/dev`
- `python scripts/eureka_ia_candidate_review.py validate-batch --batch .eureka/source-wave/ia-metadata/review-batch/latest/review_batch_manifest.json --strict`
- `python scripts/eureka_ia_candidate_review.py validate-tranche --tranche .eureka/source-wave/ia-metadata/review-batch/tranches/01/tranche_manifest.json --strict`
- `python scripts/eureka_ia_candidate_review.py tranche-status --tranche .eureka/source-wave/ia-metadata/review-batch/tranches/01/tranche_manifest.json`
  - status: `PASS_WITH_WARNINGS` because operator decisions are pending and promotion is blocked
- `python -m unittest tests.operations.test_review_ia_candidates_batch -v`
- `python -m unittest tests.runtime.test_review_ledger -v`
- `python -m unittest tests.runtime.test_review_queue_store -v`
- `python scripts/check_architecture_boundaries.py`
- `python scripts/check_generated_artifact_cleanliness.py --check --json`
- `python scripts/validate_public_alpha_readonly.py`
- `python scripts/validate_snapshot_relay.py`
- `python scripts/eureka_test_select.py --changed --failed-first --json`
- `py -3 .aide/scripts/aide_lite.py doctor`
- `py -3 .aide/scripts/aide_lite.py validate`
- `git diff --check`

Not run:

- `python -m unittest discover -s tests -t .`

External full discovery returned red for run id
`source_foundry_preview_v0_checkpoint_00`:

- latest run head: `f16d828714614c5ac7f84ab3e85aebc06cbf7a5d`
- latest run started: `2026-06-18T22:37:12Z`
- tests run: 5792
- failures: 43
- errors: 7
- failed tests: 50
- failed modules: 40
- failure families: 31

The run id was executed twice. The latest rerun included the first red-result
ingest commit and still failed with the same substantive counts. The compact
result is recorded in `FULL_DISCOVERY_RESULT.md` and
`full_discovery_result.json`.

## Dev To Main

Future `dev -> main` promotion is structurally fast-forwardable because
`origin/main` is an ancestor of `origin/dev`.

Promotion was not performed in this checkpoint because external full discovery
returned red. Promotion remains blocked until a repair or policy update produces
a green compact full-discovery result for the current promotion candidate.

## Next

1. Triage the external full-discovery failure families.
2. Decide whether historical queue-state validators should be repaired,
   reclassified, or excluded from the promotion gate.
3. Rerun external full discovery after the repair/policy lane.
4. If green, prepare or perform fast-forward `dev -> main` promotion with a
   report that states:
   - pending operator review
   - no reviewed IA truth
   - no public exposure
