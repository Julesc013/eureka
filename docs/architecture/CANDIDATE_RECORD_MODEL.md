# Candidate Record Model

`candidate_record.v0` is a normalized source lead. Required fields include the
candidate id, kind, source family, source locator, title, description, matched
query, query/source references, domain id, match reasons, suppressions,
limitations, action posture, review state, timestamps, and the explicit
non-claim fields.

Every candidate record carries:

```text
accepted_truth: false
reviewed_record_ref: null
review_required_for_promotion
```

The model is intentionally separate from reviewed search records. Promotion must
come from a later review workflow.
