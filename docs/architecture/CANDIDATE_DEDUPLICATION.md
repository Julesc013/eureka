# Candidate Deduplication

Candidate deduplication uses a deterministic fingerprint over normalized title,
source family, source locator, domain id, object hint, version hint, platform
hint, and checksum hint.

Deduplication does not merge truth, accept candidates, or mutate the reviewed
index. It marks duplicate candidate memory so review can avoid repeated work.
Collision notes remain review-owned.
