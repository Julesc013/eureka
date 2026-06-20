# Deduplication Model

The Preview Index deduplicates exact deterministic-content matches during build.
Merged records retain source and evidence refs from duplicate records.

This is intentionally conservative. It does not claim identity equivalence
between similar candidates, and it does not supersede review decisions.
