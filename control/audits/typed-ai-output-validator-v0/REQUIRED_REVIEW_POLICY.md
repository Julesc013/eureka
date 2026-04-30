# Required Review Policy

Every typed AI output must set `required_review: true`.

Every structured claim inside a typed AI output must also set
`review_required: true`. Validation success only means the output is shaped as a
candidate that can be inspected later. It does not convert the output into an
evidence record, contribution item, queue entry, accepted public record, or
canonical truth.
