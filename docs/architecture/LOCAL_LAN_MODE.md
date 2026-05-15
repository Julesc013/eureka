# Local LAN Mode

LOCAL-11 defines the Local Appliance LAN binding safety gate.

LAN mode is not public hosting. It is an explicitly enabled, read-only local
network inspection mode over the existing local service and workbench routes.

## Defaults

- default host: `127.0.0.1`
- `lan_enabled`: `false`
- `bind_lan`: `false`
- read-only posture: `true`

The server refuses `0.0.0.0` and `::` unless the operator passes `--bind-lan`.

## Explicit LAN Bind

Allowed bind hosts with `--bind-lan`:

- `0.0.0.0`
- `::`

When explicit LAN binding is used, the service emits operator and firewall
warnings. LAN clients are classified separately from loopback clients, and LAN
route access is constrained to read-only routes.

## Boundary

LAN clients may inspect the local reviewed index and status/workbench pages.
They may not record review decisions, rebuild the reviewed index, execute
WorkUnits, run source probes, run extraction, run agents, mutate config, upload
files, download/install/execute anything, mutate master index state, write
`site/dist`, or deploy.

## LOCAL-12 Smoke Result

LOCAL-12 adds same-machine LAN-bind smoke. The service is started with
`--bind-lan` on `0.0.0.0`, probed through a local client URL, and then shut
down. LAN mutation blocking is checked through the same client-scope route gate
used by the service.

External second-client smoke is preferred but was not performed by the
automated LOCAL-12 run. That limitation is recorded explicitly and must not be
described as cross-device proof.

## LOCAL-13 Relationship

LOCAL-13 does not broaden LAN mode. It proves clean-machine localhost
bootstrap and may reference LOCAL-12 for LAN smoke coverage. Any actual
second-machine proof remains optional and must not be claimed unless performed.
