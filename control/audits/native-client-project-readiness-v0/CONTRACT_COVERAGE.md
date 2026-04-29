# Contract Coverage

| Area | Exists | Validation | Enough For Skeleton? | Missing Pieces | Risk |
| --- | --- | --- | --- | --- | --- |
| Native Client Contract | yes | `python scripts/validate_native_client_contract.py` | yes, for strict read-only skeleton scope | explicit human approval and project location | medium |
| Native Client Lanes | yes | `python scripts/validate_native_client_contract.py` | yes, lane inventory names first candidate | build host/toolchain not verified | medium |
| Action / Download / Install Policy | yes | `python scripts/validate_action_policy.py` | yes, because risky actions are disabled | no implementation of handoff, scanner, rights clearance | high if ignored |
| Local Cache / Privacy Policy | yes | `python scripts/validate_local_cache_privacy_policy.py` | yes, because cache/private features remain off | no cache runtime, deletion UI, retention model | high if skipped |
| Snapshot Consumer Contract | yes | `python scripts/validate_snapshot_consumer_contract.py` | yes, for contract-guided skeleton planning | no native snapshot reader runtime | medium |
| Relay Surface Design | yes | `python scripts/validate_relay_surface_design.py` | not needed for initial skeleton | no relay runtime or threat model | medium |
| Live Backend Handoff Contract | yes | `python scripts/validate_live_backend_handoff.py` | optional only; not needed for skeleton | no backend, auth, rate limit, hosting | high if treated as live API |
| Public Data Contract | yes | `python scripts/validate_publication_inventory.py` | yes, enough for static public-data reader planning | no public API stability promise | medium |
| Static Snapshot Format | yes | `python scripts/validate_static_snapshot.py` | yes, for seed snapshot inspection planning | no production signing or real key management | medium |
| Compatibility Surface Strategy | yes | `python scripts/validate_compatibility_surfaces.py` | yes, clarifies old-client degradation | no snapshot/relay/native implementation | medium |
| Rust Parity Status | partial/planning | `python scripts/check_rust_source_registry_parity.py`; `python scripts/validate_rust_local_index_parity_plan.py` | no dependency for skeleton | Cargo unavailable here; Rust remains unwired | medium |
| Public-alpha Limitations | yes | `python scripts/public_alpha_smoke.py` | informs native restrictions | not production, local wrapper only | medium |
| Manual Baseline Status | yes | `python scripts/report_external_baseline_status.py` | not required for skeleton | observations remain human-operated and pending | low for skeleton |

Coverage conclusion: the repo has enough policy and contract coverage to plan a
minimal skeleton after explicit human approval. It is not ready for a native
prototype, live integration, installer/download behavior, local private cache,
or broad platform compatibility claims.

