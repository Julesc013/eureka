# LAN Smoke Summary

LOCAL-12 adds `scripts/eureka_lan_smoke.py`.

The script:

- requires `--bind-lan` for `0.0.0.0` and `::`
- requires `--read-only`
- starts the local service through the existing server CLI
- probes read-only routes
- checks LAN-scope mutation blocking
- shuts the service down
- validates the instance after shutdown

The automated run is same-machine LAN-bind proof only. External second-client
smoke was not performed.
