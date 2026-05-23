# Search Miss Ledger Review

Search miss review decides whether a local gap signal is useful enough to
prepare a future SearchNeed, WorkUnit, source lead, observation candidate, or
review item.

## Review Required

Review is required before:

- SearchNeed seed use
- WorkUnit seed use
- source lead preparation
- public surface use
- master-index review

Approval in this workflow means a future seed may be prepared. It does not mean
the miss is public truth or accepted evidence.

## Privacy And Poisoning

Search miss records inherit privacy filtering and poisoning flags from Query
Observation. They also validate local path, credential-like, URL, live-probe,
scraping, upload/account, source manipulation, and result-rank manipulation
risks before downstream use.

## Not Telemetry

The runtime has no public traffic hook, hosted user observation, account
identifier, cookie read, browser-state read, or raw public query logging. It
processes explicit JSON input only.

## Not Absence Proof

A search miss records that local explicit input did not produce a useful
reviewable result. It does not establish that the requested object is absent
outside that local scope.

## Validation

Run:

```powershell
python scripts/validate_search_miss_ledger_runtime.py
python scripts/record_search_miss.py --input examples/search/query_observations/empty_result_query_observation_v0.json --check
python -m unittest tests.runtime.test_search_miss_ledger_runtime tests.operations.test_search_miss_ledger_runtime_scripts
```
