# SearchNeed Runtime

`runtime/local/foundry/search_need.py` implements the first bounded Track B
SearchNeed runtime.

## What It Is

A SearchNeed is a local, reviewable unresolved-search object derived from an
explicit query observation, search miss, manual observation, or agent-assisted
candidate. It preserves the object/action shape of the need and the known local
gap without asserting final identity or truth.

The runtime can build SearchNeed records from search misses or query
observations, classify deterministic intent families, preserve privacy posture,
flag poisoning risks, validate boundaries, summarize the need, and prepare
future review-gated WorkUnit, source-lead, or candidate-review seed candidates.

## What It Is Not

SearchNeed is not telemetry, hosted query capture, public search logging,
browser history collection, external search automation, evidence truth, object
truth, source truth, absence proof, production analytics, or master-index
mutation.

It does not call networks, APIs, models, providers, live sources, browsers, or
connectors. It does not execute WorkUnits, change public search behavior, or
write files unless the CLI is given an explicit allowed output path.

## Intents

Current intent families include finding software, exact versions, compatible
versions, drivers, files inside containers, articles inside scans, manuals,
source releases, package metadata, source comparisons, identity checks,
compatibility checks, absence explanations, source-gap research, policy review,
and not-evaluable records.

Intent classification is deterministic and conservative. It is a planning hint,
not accepted object identity.

## Demand Summary

Demand summaries are local aggregate hints. They preserve the number and source
of committed or reviewed local signals, but do not enable raw public query
retention, account-level tracking, public telemetry, or production analytics.

## Outputs

Allowed outputs are SearchNeed records, summaries, and future review-gated
WorkUnit, source-lead, candidate-review, observation-candidate, or review-item
seeds. Forbidden outputs include absence proof, accepted evidence truth,
accepted public records, master-index mutations, rights clearance, malware
safety, verified installability, exhaustive search proof, and production
readiness claims.

## Validation

Run:

```powershell
python scripts/validate_search_need_runtime.py
python scripts/record_search_need.py --input examples/search/misses/empty_result_search_miss_v0.json --check
```
