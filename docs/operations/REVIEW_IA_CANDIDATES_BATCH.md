# Review IA Candidates Batch

This runbook covers `REVIEW-IA-CANDIDATES-BATCH-00`.

## Purpose

The review batch consumes the governed IA source-observation, candidate-index,
and evidence-summary deltas, then prepares deterministic operator review
material.

The batch is review input only. It does not choose outcomes, promote
candidates, create reviewed records, rebuild indexes, publish snapshots, expose
Workbench, or mutate public indexes.

## Modes

Prepare mode is autonomous and safe:

- loads existing IA deltas
- validates provenance and refs
- creates one pending review item per candidate
- groups and ranks items for operator convenience only
- writes an operator review packet
- writes a blank decision template
- records no review-ledger decisions

Record-decisions mode is available only with an explicit operator decision file
and explicit local review store path. It records review-ledger decisions/events
only. Reviewed-record creation and index rebuilds remain separate future tasks.

## Prepare Commands

```powershell
python scripts/eureka_ia_candidate_review.py prepare `
  --source ia_metadata `
  --source-observation-delta .eureka/source-wave/ia-metadata/source-observation-cache/latest/source_observation_delta_manifest.json `
  --candidate-index-delta .eureka/source-wave/ia-metadata/candidate-index/latest/candidate_index_delta_manifest.json `
  --evidence-summary-delta .eureka/source-wave/ia-metadata/evidence-ledger/latest/evidence_summary_delta_manifest.json `
  --out .eureka/source-wave/ia-metadata/review-batch/latest
```

```powershell
python scripts/eureka_ia_candidate_review.py validate-batch `
  --batch .eureka/source-wave/ia-metadata/review-batch/latest/review_batch_manifest.json `
  --strict
```

```powershell
python scripts/eureka_ia_candidate_review.py status `
  --batch .eureka/source-wave/ia-metadata/review-batch/latest/review_batch_manifest.json
```

## Generated Outputs

Generated local artifacts live under:

```text
.eureka/source-wave/ia-metadata/review-batch/latest/
  review_items.jsonl
  review_batch_manifest.json
  REVIEW_BATCH_REPORT.md
  OPERATOR_REVIEW_PACKET.md
  operator_decision_template.json
  OPERATOR_DECISION_GUIDE.md
```

The `.eureka/` tree is local generated state and is ignored by git.

Tracked audit material lives under:

```text
control/audits/source_wave/review_ia_candidates_batch_v0/
```

## Inspecting The Packet

Start with:

```text
.eureka/source-wave/ia-metadata/review-batch/latest/OPERATOR_REVIEW_PACKET.md
```

Each item includes candidate refs, source-observation refs, evidence-summary
refs, query refs, group, attention band, missing fields, and the explicit
statement that no outcome was inferred.

## Tranche 01

Use a small tranche when the full batch is too large for one operator pass.
Tranche 01 selects eight evidence-rich pending items with deterministic
query-balanced ordering.

```powershell
python scripts/eureka_ia_candidate_review.py prepare-tranche `
  --batch .eureka/source-wave/ia-metadata/review-batch/latest/review_batch_manifest.json `
  --group evidence_rich_pending_review `
  --limit 8 `
  --selection-policy balanced_evidence_rich_v0 `
  --tranche-id tranche-01 `
  --out .eureka/source-wave/ia-metadata/review-batch/tranches/01
```

```powershell
python scripts/eureka_ia_candidate_review.py validate-tranche `
  --tranche .eureka/source-wave/ia-metadata/review-batch/tranches/01/tranche_manifest.json `
  --strict
```

```powershell
python scripts/eureka_ia_candidate_review.py tranche-status `
  --tranche .eureka/source-wave/ia-metadata/review-batch/tranches/01/tranche_manifest.json
```

Generated tranche artifacts live under:

```text
.eureka/source-wave/ia-metadata/review-batch/tranches/01/
  tranche_review_items.jsonl
  tranche_manifest.json
  OPERATOR_REVIEW_TRANCHE.md
  operator_decision_template.json
  OPERATOR_DECISION_GUIDE.md
```

Because the current Tranche 01 items are fixture-derived, every selected item is
promotion-ineligible and includes:

```text
fixture_only_provenance
independent_external_evidence_missing
```

Allowed Tranche 01 decisions:

- `reject`
- `supersede`
- `mark_near_miss`
- `mark_need`
- `mark_policy_blocked`
- `request_more_evidence`

`promote` is not allowed for Tranche 01.

Validate a filled tranche decision file before any ledger write:

```powershell
python scripts/eureka_ia_candidate_review.py validate-tranche-decisions `
  --tranche .eureka/source-wave/ia-metadata/review-batch/tranches/01/tranche_manifest.json `
  --decisions <explicit-operator-decision-file> `
  --strict
```

## Filling Decisions

Copy the generated template shape into an operator-authored decision file and
fill only the items reviewed. Omitted items remain pending.

Supported decisions:

- `promote`
- `reject`
- `supersede`
- `mark_near_miss`
- `mark_need`
- `mark_policy_blocked`
- `request_more_evidence`

Rules:

- `actor` is required and must identify the local operator.
- Every included item needs an explicit decision.
- Evidence refs, source-observation refs, absence refs, fallback refs, or a
  written rationale are required.
- `reject`, `supersede`, `mark_policy_blocked`, and `request_more_evidence`
  require a reason.
- `supersede` requires `supersedes_review_item_id`.
- `promote` requires `local_only_confirmed: true`.
- AI/model output is not an operator decision.

Validate before recording:

```powershell
python scripts/eureka_ia_candidate_review.py validate-decisions `
  --batch .eureka/source-wave/ia-metadata/review-batch/latest/review_batch_manifest.json `
  --decisions <explicit-operator-decision-file> `
  --strict
```

Record only to an explicit local review store:

```powershell
python scripts/eureka_ia_candidate_review.py record-decisions `
  --batch .eureka/source-wave/ia-metadata/review-batch/latest/review_batch_manifest.json `
  --decisions <explicit-operator-decision-file> `
  --review-store <explicit-local-review-store-path> `
  --strict
```

## Safety Invariants

- no network or provider calls
- no downloads or file fetches
- no Wayback replay
- no automatic decisions
- no automatic promotion
- no reviewed records
- no reviewed/master mutation
- no public-index mutation
- no candidate-index store mutation
- no evidence-ledger store mutation
- no reviewed-index rebuild
- no snapshot refresh
- public exposure remains paused
- license posture remains restricted source-available
