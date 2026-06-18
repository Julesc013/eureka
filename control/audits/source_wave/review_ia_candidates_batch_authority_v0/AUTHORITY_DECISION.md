# Review IA Candidates Batch Authority Decision

Task: `REVIEW-IA-CANDIDATES-BATCH-AUTHORITY-00`

Status: `PASS_WITH_WARNINGS`

## Repo State At Authority Update

- branch: `dev`
- HEAD before edits: `c9d9a1f77b2cd8f805f75612612555f2009bf600`
- origin/dev before edits: `c9d9a1f77b2cd8f805f75612612555f2009bf600`
- origin/dev sync before edits: `0 0`
- worktree before edits: clean

## Queue Change

- previous recommended task: `IA-EVIDENCE-LEDGER-SUMMARY-00`
- new recommended task: `REVIEW-IA-CANDIDATES-BATCH-00`
- evidence-summary task closed: true
- review task packet created:
  `.aide/queue/REVIEW-IA-CANDIDATES-BATCH-00/task.yaml`

## Reason

`IA-EVIDENCE-LEDGER-SUMMARY-00` completed at
`c9d9a1f77b2cd8f805f75612612555f2009bf600` with 56 source observations, 56
provisional candidates, and 344 evidence summaries. The automated preparation
pipeline has reached the human review boundary, so repo authority must advance
to a task that prepares review material while preventing automated decisions.

## Review-Stage Invariant

Automation may prepare review material, validate provenance, rank or group
items for operator convenience, and produce blank decision templates.

Automation must not choose promote, reject, supersede, near-miss, need,
policy-blocked, or request-more-evidence outcomes. Operator decisions must be
explicit and attributable.

Review-ledger events record decisions only. Reviewed-record creation and index
rebuilding remain separate future tasks.

## Modes

- prepare mode: allowed, autonomous, no decisions
- record-decisions mode: allowed only with explicit operator decision input

## Operator-Only Decisions

Supported decision kinds:

- `promote`
- `reject`
- `supersede`
- `mark_near_miss`
- `mark_need`
- `mark_policy_blocked`
- `request_more_evidence`

Promotion requires `local_only_confirmed: true`.

Missing decisions remain pending and must not be inferred.

## Safety Boundary

- review implementation performed in this authority task: false
- automatic decisions: false
- automatic promotion: false
- reviewed record creation: false
- reviewed/master mutation: false
- public-index mutation: false
- network/provider calls: false
- public exposure: paused
- license posture: unchanged

Recommended next task: `REVIEW-IA-CANDIDATES-BATCH-00`.
