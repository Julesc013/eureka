# LOCAL-12 LAN Read-Only Smoke

LOCAL-12 adds same-machine explicit LAN-bind smoke for the Local Appliance.

The proof starts the local service with `--bind-lan`, verifies read-only route
availability, verifies LAN-scope mutation blocking, verifies shutdown cleanup,
and records that no external second-client smoke was performed.

This audit is not deployment evidence, public hosting evidence, production
readiness evidence, or public launch readiness evidence.
