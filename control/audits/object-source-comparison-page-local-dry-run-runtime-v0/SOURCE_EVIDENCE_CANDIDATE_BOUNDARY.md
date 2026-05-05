# Source/Evidence/Candidate Boundary

The dry-run may render synthetic source, evidence, and candidate refs already
present in approved examples.

It does not:

- Read source cache.
- Read evidence ledger.
- Write source cache.
- Write evidence ledger.
- Create candidates.
- Promote candidates.
- Accept evidence as truth.
- Mutate candidate, public, local, runtime, or master indexes.

Candidate and provisional status must remain visible in previews.
