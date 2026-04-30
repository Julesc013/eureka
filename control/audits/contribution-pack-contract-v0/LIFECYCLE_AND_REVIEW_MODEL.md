# Lifecycle And Review Model

Lifecycle states are `draft`, `local_private`, `validated_local`,
`shareable_candidate`, `submitted`, `quarantined`, `review_required`,
`accepted_public`, `rejected`, and `superseded`.

The status field alone does not grant authority. `accepted_public` requires a
future governed master-index review queue, reviewer evidence, conflict handling,
redaction checks, and publication gates. P37 does not implement that queue.
