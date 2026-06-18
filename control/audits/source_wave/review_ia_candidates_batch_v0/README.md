# Review IA Candidates Batch v0

Task: `REVIEW-IA-CANDIDATES-BATCH-00`

Status: `PASS_WITH_WARNINGS`

This audit packet records the prepare-only IA candidate review batch. The batch
materializes deterministic operator review items and a blank decision template.
It records no review decisions and creates no reviewed records or index
mutation.

Generated local artifacts:

```text
.eureka/source-wave/ia-metadata/review-batch/latest/
  review_items.jsonl
  review_batch_manifest.json
  REVIEW_BATCH_REPORT.md
  OPERATOR_REVIEW_PACKET.md
  operator_decision_template.json
  OPERATOR_DECISION_GUIDE.md
```

Tracked files in this audit:

```text
control/audits/source_wave/review_ia_candidates_batch_v0/
  README.md
  REVIEW_BATCH_RESULT.md
  review_batch_report.json
```

Remaining blocker:

```text
WAITING_FOR_OPERATOR_REVIEW_DECISIONS
```
