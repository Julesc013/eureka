# Reviewed Public Index Rebuild Model

Reviewed public-index rebuild follows candidate promotion dry-run because promotion dry-run only answers whether a candidate can seed a future proposal. This contract defines what a future rebuild would need before touching public-facing records.

The model is intentionally staged:

1. Local candidates, source observations, evidence candidates, and review entries remain local governance records.
2. Candidate promotion dry-run rehearses readiness without accepting anything.
3. Reviewed public record proposals package source, evidence, limitation, conflict, duplicate, rights, and risk posture.
4. A future rebuild runtime may consume reviewed proposals only after separate approval.

This task stops at step 3. There is no public-index rebuild runtime, public search behavior change, site artifact generation, or master-index mutation.

## Boundaries

`control/` stores policies and audit evidence. `contracts/master_index/` stores the governed schemas. `examples/` stores public-safe fixtures. No runtime code is added for B20.

The path policy forbids `site/dist/`, `site/dist/data/public_index/`, runtime output roots, publication inventory roots, production public-index roots, production master-index roots, and local private roots.

## Review Semantics

Ready means ready for a future reviewed rebuild dry-run or proposal review. It does not mean accepted public truth. Conflicts and duplicate uncertainty are preserved, not resolved or merged automatically.
