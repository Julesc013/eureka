# State Matrix

Automatic transitions are limited to `new -> seen`, `seen -> duplicate`,
`seen -> needs_review`, and `needs_review -> review_item_created`.

Operator review-only transitions require explicit operator approval. Public
state mutation is disabled.
