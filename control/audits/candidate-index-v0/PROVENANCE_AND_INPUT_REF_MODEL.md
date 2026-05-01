# Provenance And Input Ref Model

Candidate records may reference earlier query-intelligence artifacts:

- query observations
- shared query/result cache entries
- search miss ledger entries
- search need records
- probe queue items

They may also reference future manual observations, source packs, evidence
packs, contribution packs, typed AI output candidates, source-cache records, or
probe results. In P64 these are references only; no pack import, probe
execution, AI runtime, or source-cache write is added.
