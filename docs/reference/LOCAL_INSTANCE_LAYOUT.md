# Local Instance Layout

Initialize the default local instance with:

```bash
python scripts/eureka_init_instance.py --instance ./eureka-instance
```

Validate it with:

```bash
python scripts/eureka_validate_instance.py --instance ./eureka-instance
```

Inspect it with:

```bash
python scripts/eureka_instance_status.py --instance ./eureka-instance
```

## Required Tree

```text
eureka-instance/
  config/
    instance.json
  db/
    source_cache.sqlite
    evidence_ledger.sqlite
    review_queue.sqlite
    public_index.sqlite
  logs/
    eureka.log
  run/
    instance.lock
    status.json
  tmp/
    .keep
  exports/
    .keep
  imports/
    .keep
```

## Committed vs Local

Committed:

- bootstrap scripts
- policies
- docs
- validators
- tests
- audit evidence

Not committed:

- `eureka-instance/**`
- SQLite database files created for an instance
- logs
- run locks
- temp files
- imports and exports

The default `eureka-instance/` root is ignored by git. Operators may choose another explicit root, but hidden or product/runtime roots are rejected.
