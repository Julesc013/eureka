# Contract Summary

P61 adds `contracts/query/search_miss_ledger_entry.v0.json` and
`contracts/query/search_miss_classification.v0.json`.

The contract allows future privacy-filtered miss records for no-hit, weak-hit,
near-miss, blocked, ambiguous, and incomplete public searches. It requires raw
query retention default `none`, checked/not-checked scope, miss causes,
near-miss and weak-hit summary models, scoped absence, privacy flags, and hard
no-mutation guarantees.

Current status: `contract_only`. No public search runtime route writes miss
ledger entries in this milestone.

