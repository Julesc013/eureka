# Contract Schema Inventory

## Live TSIS Contract Roots

| Root | Current evidence |
|---|---|
| `contracts/semantic/**` | Six live TSIS semantic contracts are validated. |
| `contracts/representation/**` | Six TSIS representation contracts are validated directly, with additional representation contracts present. |
| `contracts/view/**` | Eight TSIS page/view contract stubs are validated directly, with expanded view contracts also present. |
| `contracts/action/**` | `contracts/action/action_registry.v0.json` is part of the TSIS supporting contract set. |
| `contracts/route/**` | `contracts/route/route_model.v0.json` is part of the TSIS supporting contract set. |
| `contracts/policy/**` | `contracts/policy/surface_kernel_policy.v0.json` is part of the TSIS supporting contract set. |
| `contracts/surface/**` | Surface UI contracts are present but are not the failing validator path. |

## Schema Root

No top-level `schema/` directory is present in the current repo. Contract schema
authority is currently checked in under `contracts/**`.

## Runtime Surface Exports

Current `runtime/surface/**` exports include:

- `kernel.py`
- `routes.py`
- `view_models.py`
- `capabilities.py`
- `profiles.py`
- `output_policy.py`
- `cache_key.py`
- `dispatch.py`
- `fallback.py`
- `renderers/**`

These files are from later completed phases and are not TSIS-00 output.

## Focused Validators

- `scripts/validate_temporal_semantic_interface_system.py`
- `tests/scripts/test_validate_temporal_semantic_interface_system.py`

