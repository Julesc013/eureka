# Instance Layout

The explicit local instance root contains:

- `config/instance.json`
- `db/source_cache.sqlite`
- `db/evidence_ledger.sqlite`
- `db/review_queue.sqlite`
- `db/public_index.sqlite`
- `logs/eureka.log`
- `run/instance.lock`
- `run/status.json`
- `tmp/.keep`
- `exports/.keep`
- `imports/.keep`

The default root is `./eureka-instance`, and it is ignored by git.
