# Local Appliance Integration

`scripts/eureka_init_instance.py` initializes `db/search_hunt.sqlite`. `runtime/local_appliance` opens it through the store manifest as `runtime.search_hunt`, includes it in integrity checks, and reports it in runtime status.

The store path is not ad hoc and hidden state roots remain forbidden.
