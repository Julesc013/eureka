# Query Observation Privacy And Poisoning

Query observation records are privacy-filtered before they can be used as local
learning signals.

## Privacy Rules

- Public telemetry is disabled.
- Raw public query logging is disabled.
- Hosted user capture is disabled.
- Account identity, location, browser state, cookies, and history are not
  collected.
- Synthetic committed query text is allowed only as fixture input.
- Credential-like content, private paths, private URLs, and contact-like data
  are redacted or blocked for public-safe use.

## Poisoning Guard

The runtime flags repeated spam queries, suspiciously long input, URL injection,
local path injection, credential-like content, private data content,
download/install intent, unsupported live-probe requests, unsupported scraping,
account/upload requests, source manipulation, result-rank manipulation, and
future bulk automation patterns.

Risk flags are review signals only. They do not change ranking, public search,
evidence acceptance, source truth, or the master index.

## Output Review

Miss-ledger seeds, SearchNeed seeds, WorkUnit seeds, observation candidates, and
review items remain future outputs requiring review. Automatic public use,
automatic evidence acceptance, and automatic master-index mutation are
forbidden.

## Validation

Run:

```powershell
python scripts/validate_query_observation_runtime.py
python -m unittest tests.runtime.test_query_observation_runtime tests.operations.test_query_observation_runtime_scripts
```
