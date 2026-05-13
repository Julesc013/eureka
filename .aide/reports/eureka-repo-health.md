# Eureka Repo Health

## Current Queue

- Completed item: LOCAL-01 - Local instance layout and bootstrap.
- Current item: LOCAL-02 - Instance configuration, schema, and migration guard.
- F0 status: deferred until LOCAL-14.

## Local Appliance State

LOCAL-00 inserted the Local Appliance track before F0. LOCAL-01 adds explicit local instance bootstrap, validation, and status commands:

```bash
python scripts/eureka_init_instance.py --instance ./eureka-instance
python scripts/eureka_validate_instance.py --instance ./eureka-instance
python scripts/eureka_instance_status.py --instance ./eureka-instance
```

The default local instance root is ignored by git and must not be committed.

## Boundaries

- HTTP server: not implemented.
- HTML workbench: not implemented.
- WorkUnit runtime: not implemented.
- LAN: disabled.
- Deployment: not performed.
- Production readiness: not claimed.
- Public launch readiness: not claimed.

## Warnings

Full unittest discovery remains blocked by the pre-existing runtime leakage gate. LOCAL-01 records the leakage baseline and does not increase it.
