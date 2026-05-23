# R0 Source Cache Store

R0-05 adds the durable local SQLite source cache store.

## Initialize A Store

```bash
python scripts/init_source_cache_store.py --db control/audits/r0-05-durable-source-cache-store-v0/generated/source_cache_demo.sqlite --check --json
```

The command writes only to the explicit `--db` path.

## Run The Demo

```bash
python scripts/demo_source_cache_store.py --json
```

To write the audit sample:

```bash
python scripts/demo_source_cache_store.py --db control/audits/r0-05-durable-source-cache-store-v0/generated/source_cache_demo.sqlite --output control/audits/r0-05-durable-source-cache-store-v0/generated/sample_demo_output.json --json
```

The demo builds the R0-04 source observation flow, stores it in SQLite, reads the cache entry back, lists entries, summarizes the store, and runs SQLite integrity checks.

## Run The Validator

```bash
python scripts/validate_source_cache_store.py
```

The validator checks in-memory and temp-file stores, idempotent init, contracts, leakage, import boundaries, list/get behavior, and the downstream-write boundary.

## Inspect Cache Contents

Use the runtime API:

```python
from runtime.source.cache import SourceCacheStore

with SourceCacheStore.open("path/to/source-cache.sqlite") as store:
    store.init()
    print(store.summarize().to_dict())
    print([entry.to_dict() for entry in store.list_cache_entries()])
```

## Why F0 Remains Blocked

The source cache persists observations only. It does not create an evidence ledger, review queue, or reviewed public index, so F0 remains blocked.

## Next Task

R0-06 should add a durable evidence ledger store that consumes cached observations without accepting evidence automatically.
