# Public Alpha Reassess Decision

The reassessment decision packet records:

- snapshot refresh reference
- reviewed record count
- candidate count
- known need count
- absence summary count
- route smoke status
- query coverage
- usefulness score
- launch recommendation
- demo-mode recommendation
- blockers
- warnings
- next work

For `PUBLIC-ALPHA-REASSESS-00`, the decision is:

```text
decision: remain_deferred
launch_recommended: false
demo_mode_recommended: true
needs_more_reviewed_records: true
needs_more_seed_batches: true
needs_live_metadata_pilot: true
```

The packet is not a deploy artifact and does not authorize launch.

For `PUBLIC-ALPHA-REASSESS-01`, the decision adds live metadata and public
search view-model evidence:

```text
decision: remain_deferred
launch_recommended: false
demo_mode_recommended: true
internal_review_recommended: true
needs_more_reviewed_records: true
needs_live_candidate_review: true
needs_snapshot_refresh_after_review: true
```

Live metadata candidates improve internal review usefulness, but they remain
review-only until a later review and local apply gate supports promotion.

For `PUBLIC-ALPHA-REASSESS-02`, the decision adds review-preview evidence:

```text
decision: remain_deferred
launch_recommended: false
demo_mode_recommended: true
internal_review_recommended: true
needs_more_reviewed_records: true
needs_local_apply_of_review_previews: true
needs_snapshot_refresh_after_apply: true
needs_public_alpha_reassess_after_apply: true
```

Reviewed metadata/source-lead previews improve readiness, but they are not
applied reviewed records and do not authorize public launch.
