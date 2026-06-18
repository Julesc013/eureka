# Review IA Candidates Batch Authority Decision

Task: `REVIEW-IA-CANDIDATES-BATCH-AUTHORITY-00`

Status: `PASS_WITH_WARNINGS`

## Decision

Repo-local authority advances from `IA-EVIDENCE-LEDGER-SUMMARY-00` to
`REVIEW-IA-CANDIDATES-BATCH-00`.

The next task may prepare a deterministic IA candidate review batch from the
source-observation, candidate-index, and evidence-summary deltas. Automation may
assemble items, validate provenance, group or rank items for operator
convenience, and produce blank decision templates.

Automation must not choose substantive review outcomes.

## Review Invariant

Review is the truth boundary. Source observations, provisional candidates, and
evidence summaries are review inputs only.

Review-ledger decision recording and reviewed-record/index materialization are
separate operations. The next task may record review-ledger decisions only when
an explicit operator decision input file is supplied. It must not create
reviewed records, rebuild indexes, publish snapshots, or mutate public indexes.

## Modes

### Prepare

Allowed:

- load existing IA source/candidate/evidence deltas
- construct deterministic review items
- rank or group items for operator convenience
- validate provenance, missing fields, orphan refs, and unsupported claims
- produce a review batch packet
- produce blank decision templates

Forbidden:

- review decisions
- review-ledger decision writes
- promotions
- accepted-truth creation
- reviewed-record materialization
- index rebuilds

### Record Decisions

Allowed only when an explicit operator decision file is supplied.

Requirements:

- named actor
- explicit item-level decisions for every item covered by the file
- evidence refs, source-observation refs, absence refs, fallback refs, or a
  written rationale
- `local_only_confirmed: true` for promotion
- review-ledger decision/event writes only

Forbidden:

- inferred decisions for missing items
- AI/model decisions treated as operator decisions
- implicit promotion from confidence or ranking
- bulk promote-all without item-level decisions
- reviewed-record creation
- reviewed/master/public index mutation

## Supported Decisions

The next task should reuse the existing review ledger decision vocabulary:

- `promote`
- `reject`
- `supersede`
- `mark_near_miss`
- `mark_need`
- `mark_policy_blocked`
- `request_more_evidence`

## Operator Decision Input Shape

```json
{
  "schema_version": "eureka.ia_candidate_review_decisions.v0",
  "batch_id": "...",
  "actor": "operator-name",
  "generated_at": "...",
  "decisions": [
    {
      "review_item_id": "...",
      "candidate_id": "...",
      "decision": "promote|reject|supersede|mark_near_miss|mark_need|mark_policy_blocked|request_more_evidence",
      "reason": "...",
      "evidence_refs": ["..."],
      "source_observation_refs": ["..."],
      "absence_refs": [],
      "fallback_refs": [],
      "supersedes_review_item_id": null,
      "local_only_confirmed": false
    }
  ]
}
```

Authority rules:

- `actor` is mandatory.
- Each recorded item decision must be explicit.
- `reason` is mandatory for `reject`, `supersede`, `mark_policy_blocked`, and
  `request_more_evidence`.
- `supersedes_review_item_id` is mandatory for `supersede`.
- At least one evidence/source/absence/fallback reference or written rationale
  is required.
- `promote` requires `local_only_confirmed: true`.
- Missing decisions remain pending; they must not be inferred.
- A decision file may cover only a subset of the review batch.

## Path Authority

Allowed next-task implementation paths:

- `runtime/local/**`
- `runtime/review/**`
- `scripts/eureka_ia_candidate_review.py`
- optional existing `scripts/eureka_review.py`
- `tools/generators/**`
- `tests/operations/**`
- `tests/runtime/**`
- `docs/operations/**`
- `control/audits/source_wave/**`
- `.eureka/source-wave/ia-metadata/review-batch/**`
- optional `contracts/review/**`
- optional `contracts/evidence/**` only when using existing review/evidence
  shapes

Protected paths:

- reviewed-record materialization paths unless a separate future task
  authorizes them
- reviewed/master-index refresh paths
- public-index paths
- snapshot/public projection paths
- source/provider expansion
- public exposure/launch code
- Workbench runtime unless separately authorized
- `release/**`
- `archive/**`
- license and notice files

## Safety

- public exposure remains paused
- license posture remains unchanged
- reviewed/master mutation remains forbidden
- public-index mutation remains forbidden
- network/provider calls remain forbidden
- downloads, file fetches, and Wayback replay remain forbidden

Recommended next task: `REVIEW-IA-CANDIDATES-BATCH-00`.
