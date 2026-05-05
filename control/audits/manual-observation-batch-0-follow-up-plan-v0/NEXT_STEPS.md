# Next Steps

If Batch 0 remains pending:

1. Human: execute Manual Observation Batch 0.
2. Human or Codex locally: run `python scripts/validate_external_baseline_observations.py`.
3. Human or Codex locally: run `python scripts/run_external_baseline_comparison.py --batch batch_0 --json`.
4. P103: Object/Source/Comparison Page Local Dry-Run Runtime v0 only after approval.
5. Continue P104-P111 only within their explicit gates.

If Batch 0 becomes complete:

1. Run an External Baseline Comparison Refresh.
2. Preserve uncertainty and non-claims.
3. Use the comparison to inform future ranking/page/source-cache priorities.

Human/operator parallel work:

- Execute Manual Observation Batch 0.
- Validate observation records.
- Rerun external baseline comparison.
- Deploy hosted wrapper.
- Configure backend URL.
- Configure edge/rate limits.
- Verify static site.

