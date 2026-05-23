# TRACK-B-07 Query Observation Runtime

This audit pack adds the first bounded Query Observation runtime.

Query observation follows Local Foundry State because it needs a local,
reviewable place to prepare learning signals without creating private roots,
public telemetry, or accepted truth.

## Added

- `runtime/local/foundry/query_observation.py`
- `scripts/record_query_observation.py`
- `scripts/validate_query_observation_runtime.py`
- Query observation runtime, privacy, poisoning guard, and output policies
- five compact flat runtime examples under `examples/search/query_observations/`
- query observation runtime reference, architecture, and privacy/poisoning docs
- runtime and script tests
- generated sample report and summary from a committed synthetic example

## Runtime Boundary

The runtime accepts explicit local JSON input only. It can classify local query
outcomes, hash or redact query text, flag poisoning risks, validate boundaries,
and print or explicitly write an audit report.

It cannot observe hosted users, record public traffic, call sources, call
models, alter public search behavior, create private local state, accept
evidence, or mutate the master index.

## Why This Is Not Telemetry

There is no automatic query capture, public traffic hook, hosted user
observation, account identifier, browser-state read, cookie read, or raw public
query logging. Synthetic committed fixture text is the only raw query text
allowed in this milestone.

## Deferred

Search miss ledger runtime, SearchNeed runtime, WorkUnit seed generation, and
review queue behavior remain future tasks.

## Validation

```powershell
python scripts/validate_query_observation_runtime.py
python scripts/record_query_observation.py --input examples/search/query_observations/minimal_query_observation_v0.json --check
python -m unittest discover -s tests -t .
```

## Next Task

TRACK-B-08 - Search miss ledger runtime
