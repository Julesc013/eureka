# Example Miss Entry Review

Committed examples:

- `examples/search_miss_ledger/minimal_no_hits_miss_v0/`
- `examples/search_miss_ledger/minimal_weak_hits_miss_v0/`

`minimal_no_hits_miss_v0` uses the synthetic query
`no-such-local-index-hit` and records a scoped no-hit miss against the public
index.

`minimal_weak_hits_miss_v0` uses the synthetic query `windows 7 apps` and
records weak-hit posture with public-safe summary references.

Both examples retain no raw query, use non-reversible fingerprints, keep all
mutation flags false, and include checksums.

