# Ranking Shadow Model

The ranking shadow model scores explicit fixture/local records with deterministic factor helpers. It can compare candidates, near misses, known absence, and extraction gaps, but it does not publish or persist ranking.

Identity merge and dedup outputs are also shadow-only. They preserve conflicts and require review before any canonicalization, merge, delete, or public search use.
