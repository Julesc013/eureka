# Query Observation Runtime

`runtime/local/foundry/query_observation.py` implements the first bounded
Track B Query Observation runtime.

## What It Is

A query observation is a local, privacy-filtered learning signal about an
explicit query attempt and its local outcome. It can record that a synthetic or
reviewed input had empty, weak, useful, blocked, or not-evaluable local results.

The runtime can classify query outcomes, hash or redact query text, flag
poisoning risks, validate boundaries, and summarize review-gated downstream
signals.

## What It Is Not

Query observation is not telemetry, hosted query capture, public search
logging, browser history collection, external search automation, evidence
truth, object truth, source truth, global absence proof, or master-index
mutation.

It does not call networks, APIs, models, providers, live sources, browsers, or
connectors. It does not change public search behavior and does not write files
unless the CLI is given an explicit allowed output path.

## Inputs

Current inputs are explicit local JSON records from committed fixtures, local
evals, manual observation candidates, public-search rehearsal fixtures, static
demo fixtures, or agent-assisted candidates. Future public-search or node
WorkUnit inputs remain policy-gated and disabled in this milestone.

## Outputs

Allowed outputs are query observation records, summaries, and future
review-gated miss-ledger, SearchNeed, WorkUnit, observation-candidate, or review
item seeds. Forbidden outputs include external baseline truth, accepted
evidence truth, accepted public records, master-index mutations, rights
clearance, malware safety, verified installability, exhaustive search proof,
and production readiness claims.

## Validation

Run:

```powershell
python scripts/validate_query_observation_runtime.py
python scripts/record_query_observation.py --input examples/search/query_observations/minimal_query_observation_v0.json --check
```
