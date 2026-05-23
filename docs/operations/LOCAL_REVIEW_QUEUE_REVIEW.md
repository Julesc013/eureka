# Local Review Queue Review

Review queue entries are local governance records. They help a human or future reviewed workflow decide what should be rejected, deferred, blocked, marked duplicate, sent back for more evidence, or allowed into a later promotion dry-run.

## Checklist

- Confirm the input is an explicit committed fixture or repo-local record.
- Confirm the entry does not accept evidence or candidate truth.
- Confirm public index and master-index mutation remain false.
- Confirm duplicate entries do not merge or delete records automatically.
- Confirm conflict entries preserve conflicts.
- Confirm request-more-evidence entries list missing evidence.
- Confirm promotion dry-run approval is scoped only to a later dry-run task.

## Forbidden Outcomes

Review queue output must not create public truth, evidence truth, source truth, hosted moderation state, rights clearance, malware safety, installability verification, production-readiness claims, public index mutation, or master-index mutation.

## Validation

```bash
python scripts/validate_local_review_queue_runtime.py
python scripts/record_review_queue.py --input examples/review/queue_entries/candidate_needs_review_v0.json --check
python scripts/summarize_review_queue.py --input examples/review/queue_entries --check
python -m unittest tests.runtime.test_local_review_queue_runtime tests.operations.test_local_review_queue_runtime_scripts
```
