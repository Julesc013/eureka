# LAN Smoke Prerequisites

LOCAL-12 should run a read-only LAN smoke with explicit `--bind-lan`.

Prerequisites:

- show the operator/firewall warning before binding all interfaces
- keep LAN route access read-only
- verify mutating routes are blocked
- use another client device when available
- record a loopback-simulated report only if no second device is available
- document shutdown and cleanup
- make no deployment or public hosting claim
