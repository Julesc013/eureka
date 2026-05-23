# SearchNeed Review

SearchNeed review decides whether a local unresolved-search object is shaped
well enough to prepare a future WorkUnit seed, source lead, candidate-review
seed, observation candidate, or review item.

## Review Required

Review is required before:

- WorkUnit seed use
- source lead preparation
- candidate review seed use
- public surface use
- master-index review

Approval in this workflow means a future seed may be prepared. It does not mean
the SearchNeed is public truth or accepted evidence.

## Privacy And Poisoning

SearchNeed records inherit privacy filtering and poisoning flags from Query
Observation and Search Miss Ledger. They also validate local path,
credential-like, URL, live-probe, scraping, upload/account, source
manipulation, and result-rank manipulation risks before downstream use.

## Not Telemetry

The runtime has no public traffic hook, hosted user observation, account
identifier, cookie read, browser-state read, or raw public query logging. It
processes explicit JSON input only.

## Not Absence Proof

A SearchNeed records that local explicit input suggests unresolved search work.
It does not establish that the requested object is absent outside that local
scope.

## Validation

Run:

```powershell
python scripts/validate_search_need_runtime.py
python scripts/record_search_need.py --input examples/search/misses/empty_result_search_miss_v0.json --check
python -m unittest tests.runtime.test_search_need_runtime tests.operations.test_search_need_runtime_scripts
```
