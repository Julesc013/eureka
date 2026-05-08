# Search Miss Ledger Runtime

`runtime/local_foundry/search_miss_ledger.py` implements the first bounded
Track B Search Miss Ledger runtime.

## What It Is

A search miss ledger record is a local, privacy-filtered gap signal derived
from an explicit query observation or a committed search-miss fixture. It can
record that local results were empty, weak, noisy, near matches only, blocked
by policy, or not evaluable.

The runtime can classify miss kinds, preserve the privacy and poisoning posture
from Query Observation records, validate no-truth boundaries, and summarize
future review-gated SearchNeed, WorkUnit, and source-lead seed candidates.

## What It Is Not

A search miss is not telemetry, hosted query capture, browser history
collection, external search automation, evidence truth, object truth, public
truth, source truth, absence proof, or master-index mutation.

It does not call networks, APIs, models, providers, live sources, browsers, or
connectors. It does not change public search behavior and does not write files
unless the CLI is given an explicit allowed output path.

## Inputs

Current inputs are explicit query observation records, committed fixtures,
local eval outputs, manual observation candidates, public-search rehearsal
fixtures, static demo fixtures, and agent-assisted candidates. Future public
search and node WorkUnit inputs remain policy-gated and disabled in this
milestone.

## Outputs

Allowed outputs are search miss records, search miss summaries, and future
review-gated SearchNeed, WorkUnit, source-lead, observation-candidate, or
review-item seeds. Forbidden outputs include absence proof, accepted evidence
truth, accepted public records, master-index mutations, rights clearance,
malware safety, verified installability, exhaustive search proof, and
production readiness claims.

## Review Gates

Search miss records require review before SearchNeed seeds, WorkUnit seeds,
source leads, public surfaces, or master-index review. A search miss can
prepare future seeds, but it cannot promote them.

## Validation

Run:

```powershell
python scripts/validate_search_miss_ledger_runtime.py
python scripts/record_search_miss.py --input examples/query_observations/empty_result_query_observation_v0.json --check
```
