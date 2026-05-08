# TRACK-B-08 Search Miss Ledger Runtime

This audit pack adds the first bounded Search Miss Ledger runtime.

Search miss ledger follows Query Observation because it turns explicit local
query outcome records into reviewable gap signals without creating public
telemetry, absence proof, accepted truth, or master-index mutations.

## Added

- `runtime/local_foundry/search_miss_ledger.py`
- `scripts/record_search_miss.py`
- `scripts/validate_search_miss_ledger_runtime.py`
- Search miss runtime, failure-mode, output, and review policies
- six compact public-safe examples under `examples/search_misses/`
- search miss reference, architecture, and review docs
- runtime and script tests
- generated sample report and summary from committed synthetic examples

## Runtime Boundary

The runtime accepts explicit local JSON input only. It can classify local gaps,
preserve privacy posture, flag poisoning risks, validate boundaries, and print
or explicitly write an audit report.

It cannot observe hosted users, record public traffic, call sources, call
models, alter public search behavior, create private local state, accept
evidence, prove absence, or mutate the master index.

## Why This Is Not Telemetry

There is no automatic query capture, public traffic hook, hosted user
observation, account identifier, browser-state read, cookie read, or raw public
query logging. Inputs are committed examples or explicit local files.

## Deferred

SearchNeed runtime, WorkUnit seed generation, source-lead preparation, and
review queue behavior remain future tasks.

## Validation

```powershell
python scripts/validate_search_miss_ledger_runtime.py
python scripts/record_search_miss.py --input examples/query_observations/empty_result_query_observation_v0.json --check
python -m unittest discover -s tests -t .
```

## Next Task

TRACK-B-09 - SearchNeed runtime
