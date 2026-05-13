# Bootstrap Result

LOCAL-01 adds:

- `scripts/eureka_init_instance.py`
- `scripts/eureka_validate_instance.py`
- `scripts/eureka_instance_status.py`
- `scripts/validate_local_instance_bootstrap.py`

The init command requires `--instance`, rejects forbidden roots, creates the required layout, initializes empty R0 SQLite stores through existing store APIs, and is idempotent.
