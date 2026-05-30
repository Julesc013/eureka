# Candidate State Model

Candidate states:

```text
new
seen
useful_lead
needs_review
review_item_created
rejected_wrong_object
rejected_wrong_version
rejected_wrong_platform
rejected_low_quality
duplicate
blocked
accepted_local_reviewed
```

Automatic transitions are limited to:

```text
new -> seen
seen -> duplicate
seen -> needs_review
needs_review -> review_item_created
```

Operator transitions require an operator context and explicit approval. Public
candidate mutation is disabled.
