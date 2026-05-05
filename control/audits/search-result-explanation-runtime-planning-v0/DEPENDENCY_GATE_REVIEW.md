# Dependency Gate Review

Evidence-weighted ranking contract: present, contract-only. Explanation may
refer to ranking factors only after a future ranking runtime emits public-safe
explanation fields.

Compatibility-aware ranking contract: present, contract-only. Explanation may
refer to compatibility caveats from public result cards now and future ranking
relationships only after approval.

Result merge/deduplication contract: present, contract-only. Explanation may
represent grouping/dedup as future relationship metadata, not destructive merge.

Cross-source identity resolution contract: present, contract-only. Explanation
may describe identity uncertainty and grouping only when public-safe identity
relations are in the result envelope.

Object page contract: present. Page runtime is local dry-run only; explanation
runtime must not call page runtime in P106.

Source page contract: present. Page runtime is local dry-run only; explanation
runtime must not call source page runtime in P106.

Comparison page contract: present. Page runtime is local dry-run only; no
comparison route integration is added.

Deep extraction contract: present, but runtime planning is blocked by missing
resource-limit/sandbox operator approval. Explanation must not call extraction.

Source cache: contract and local dry-run runtime present. No authoritative source
cache reads are allowed for P106.

Evidence ledger: contract and local dry-run runtime present. No authoritative
evidence ledger reads are allowed for P106.

Candidate index and promotion policy: present as governed contracts. Explanation
must not promote candidates or mutate candidate/master/public indexes.

Known absence page contract: present under query contracts. Any future absence
explanation must remain scoped and not become a global absence claim.

