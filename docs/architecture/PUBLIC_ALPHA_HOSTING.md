# Public Alpha Hosting

`PUBLIC-ALPHA-HOSTING-READINESS-00` defines hosting posture for the read-only
public alpha. It is a readiness and planning task only. It does not deploy,
publish, or claim production or public launch readiness.

## Supported Modes

| Mode | Current posture | Required inputs | Output artifacts | Rollback path |
| --- | --- | --- | --- | --- |
| `static_snapshot_site` | Preferred for initial alpha consideration | reviewed snapshot manifest, relay manifest, static route build | static reviewed-index-only pages and data | restore prior static artifact and prior reviewed snapshot manifest |
| `read_only_relay_service` | Preferred alternative | reviewed snapshot manifest, relay manifest, read-only service config | read-only alpha API and web routes | pin previous relay manifest and restart read-only service |
| `local_preview_server` | Allowed for operator preview | local reviewed snapshot and relay fixtures | local-only preview routes | stop preview process and discard preview-only state |
| `future_dynamic_gateway` | Blocked until future reviewed task | future approved gateway plan | none in this task | future task must define rollback before use |

The public alpha path remains snapshot-backed, relay-backed, reviewed-index
only, and read-only. It has no live source fanout, public mutation, downloads,
extraction, account system, or model/provider call path.

## Launch Gate

No hosting mode is launchable from this task. A later launch-candidate task must
show validator pass, snapshot/relay pass, external full discovery pass, explicit
deployment approval, security headers, rate limits, privacy/abuse/takedown docs,
and rollback readiness.
