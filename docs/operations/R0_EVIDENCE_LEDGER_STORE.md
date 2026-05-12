# R0 Evidence Ledger Store

R0-06 adds a durable SQLite evidence ledger without creating review queue persistence or public index behavior.

## Initialize

```bash
python scripts/init_evidence_ledger_store.py --db control/audits/r0-06-durable-evidence-ledger-store-v0/generated/evidence_ledger_demo.sqlite --check --json
```

The DB path must be explicit. Hidden local roots and product directories are refused.

## Demo

```bash
python scripts/demo_evidence_ledger_store.py --source-cache-db control/audits/r0-06-durable-evidence-ledger-store-v0/generated/source_cache_demo.sqlite --evidence-db control/audits/r0-06-durable-evidence-ledger-store-v0/generated/evidence_ledger_demo.sqlite --output control/audits/r0-06-durable-evidence-ledger-store-v0/generated/sample_demo_output.json --json
```

The demo creates synthetic source-observation data, writes it through source cache, persists an evidence candidate, links that candidate to the cache entry, appends events, records a conflict candidate, and reads the ledger back.

## Validate

```bash
python scripts/validate_evidence_ledger_store.py
```

The validator checks contracts, migrations, in-memory behavior, explicit file-backed behavior, append-only event behavior, source-cache linking, conflict recording, and boundary rules.

## Inspect

Use `EvidenceLedgerStore.open(path)` and `summarize()`, `list_evidence_candidates()`, `list_events()`, or `list_conflicts()`.

## Boundaries

- F0 remains blocked.
- Dev-to-main promotion remains blocked.
- R0-07 is next and should build the review queue product seam.
