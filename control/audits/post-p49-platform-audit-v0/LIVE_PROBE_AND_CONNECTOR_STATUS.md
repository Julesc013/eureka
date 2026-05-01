# Live Probe And Connector Status

| Connector/capability | Evidence | Classification | Notes |
|---|---|---|---|
| Live probe gateway | `validate_live_probe_gateway.py` | `contract_only` | 9 candidate sources disabled. |
| IA metadata connector | placeholder only | `approval_gated` | No live IA calls. |
| Wayback/CDX/Memento connector | recorded fixtures plus placeholder | `approval_gated` | No live CDX/Memento calls. |
| GitHub Releases connector | recorded fixture source | `fixture_only` | No live GitHub acquisition. |
| PyPI connector | no live connector | `deferred` | Package-registry recorded fixtures only. |
| npm connector | no live connector | `deferred` | Package-registry recorded fixtures only. |
| Software Heritage connector | recorded fixtures plus placeholder | `approval_gated` | No live API calls. |
| Wikidata/Open Library connector | absent | `deferred` | Future source-family work. |
| Connector health/quota dashboard | absent | `deferred` | Needs live connector design first. |
| Source cache/evidence ledger | policy only | `contract_only` | No runtime cache/ledger. |

P50 performed no external API calls.
