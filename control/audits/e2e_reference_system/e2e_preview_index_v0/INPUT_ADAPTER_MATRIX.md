# Input Adapter Matrix

- Reviewed records produce `reviewed` records with `reviewed_record` authority
  only when accepted truth and review refs are already present in the input.
- Candidate deltas produce `candidate` records with `candidate_only` authority.
- Evidence summaries produce `mention_only`, `near_miss`, `need`, `absence`, or
  `unavailable` records according to evidence type and support posture.
- Source observations produce `mention_only` or `unavailable` records.
- ResolutionRun bundles produce projection records. Synthetic runs use
  `synthetic_test` authority and are excluded from search by default.
