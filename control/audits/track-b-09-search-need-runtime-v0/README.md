# TRACK-B-09 SearchNeed Runtime

This audit pack adds the first bounded SearchNeed runtime.

SearchNeed follows Search Miss Ledger because it turns explicit local gap
signals into reviewable unresolved-search objects without creating public
telemetry, absence proof, accepted truth, or master-index mutations.

## Added

- `runtime/local/foundry/search_need.py`
- `scripts/record_search_need.py`
- `scripts/validate_search_need_runtime.py`
- SearchNeed runtime, status, intent, output, and review policies
- six compact public-safe examples under `examples/search/needs/`
- SearchNeed reference, architecture, and review docs
- runtime and script tests
- generated sample report and summary from committed synthetic examples

## Runtime Boundary

The runtime accepts explicit local JSON input only. It can build SearchNeed
records, classify local intent, preserve privacy posture, flag poisoning risks,
validate boundaries, and print or explicitly write an audit report.

It cannot observe hosted users, record public traffic, call sources, call
models, execute WorkUnits, alter public search behavior, create private local
state, accept evidence, prove absence, or mutate the master index.

## Why This Is Not Telemetry

There is no automatic query capture, public traffic hook, hosted user
observation, account identifier, browser-state read, cookie read, or raw public
query logging. Inputs are committed examples or explicit local files.

## Deferred

WorkUnit dry-run runner, source-lead preparation, candidate-review runtime, and
review queue behavior remain future tasks.

## Validation

```powershell
python scripts/validate_search_need_runtime.py
python scripts/record_search_need.py --input examples/search/misses/empty_result_search_miss_v0.json --check
python -m unittest discover -s tests -t .
```

## Next Task

TRACK-B-10 - WorkUnit dry-run runner
