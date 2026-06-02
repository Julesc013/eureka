# Review Batch Apply Next Runbook

Run from a clean `dev` branch after `PUBLIC-ALPHA-REASSESS-05`.

Smoke commands:

```bash
python scripts/eureka_review_batch_apply_validate.py --from-examples --json
python scripts/eureka_review_batch_apply_next.py --from-examples --use-temp-instance --json
python scripts/eureka_review_batch_apply_report.py --from-examples --json
```

Validation:

```bash
python scripts/validate_review_batch_apply_next.py
```

The default target is a temporary explicit instance. Operator instance apply is
forbidden in this task and requires a separate approval task if it is ever
enabled.

After apply proof, run `SNAPSHOT-REFRESH-06`.
