# Review Batch Runbook

Build a local example batch:

```bash
python scripts/eureka_review_batch.py --from-candidate-examples --json
```

Preview a batch decision:

```bash
python scripts/eureka_review_batch_preview.py --from-candidate-examples --decision mark_useful_lead --json
```

Validate an operator dry-run promotion preview:

```bash
python scripts/eureka_review_batch_decision.py --from-candidate-examples --decision accept_local_reviewed_preview --operator-token local-dev-token --dry-run --json
```

Create handoff previews:

```bash
python scripts/eureka_review_batch_handoff.py --from-candidate-examples --json
```

These commands use local examples only. They do not mutate indexes, execute local apply, refresh snapshots, download, extract, call models, deploy, or publish.
