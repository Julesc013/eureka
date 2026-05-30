# Candidate Record

`candidate_record.v0` fields:

```text
candidate_id
candidate_kind
source_family
source_locator
title
description
matched_query
query_plan_ref
source_action_ref
source_observation_ref
evidence_candidate_refs
domain_id
confidence_label
match_reasons
suppressions
limitations
action_posture
review_state
accepted_truth
reviewed_record_ref
created_at
updated_at
```

`accepted_truth` must remain `false` and `reviewed_record_ref` must remain
`null` until a separate review/promotion workflow exists and is approved.
